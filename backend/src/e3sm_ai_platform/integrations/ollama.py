"""Opt-in loopback Ollama inference with bounded, evidence-first fallback."""

from __future__ import annotations

import asyncio
from ipaddress import ip_address
from threading import Lock
from urllib.parse import urlsplit

import httpx
from opentelemetry import trace
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.providers.openai import OpenAIProvider

from e3sm_ai_platform.application.generation import generate_response
from e3sm_ai_platform.domain.models import Evidence, GenerationMode, QueryResponse, RouteName
from e3sm_ai_platform.infrastructure.settings import Settings
from e3sm_ai_platform.integrations.prompting import SYSTEM_PROMPT

# One in-flight generation across service instances in this backend process.
_GENERATION_LOCK = Lock()
_TEMPLATE_TOKEN_RESERVE = 512


class OllamaProviderError(RuntimeError):
    """Carry an internal error code without provider payloads."""


class OllamaEvidenceGenerator:
    """Generate curated answers through Ollama while retaining server evidence.

    Parameters
    ----------
    settings
        Local inference configuration, including the total generation deadline.
    transport
        Optional asynchronous HTTP transport for offline tests.
    """

    def __init__(
        self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self.settings = settings
        self._transport = transport

    def __call__(
        self,
        question: str,
        route: RouteName,
        evidence: list[Evidence],
        include_evidence: bool,
        reason: str,
    ) -> QueryResponse:
        """Return generated text or a sanitized, cited deterministic fallback.

        Parameters
        ----------
        question
            User question.
        route
            Server-selected route.
        evidence
            Accepted evidence for curated routes.
        include_evidence
            Whether to return full evidence records.
        reason
            Server-owned routing explanation.

        Returns
        -------
        QueryResponse
            Response retaining deterministic citations and evidence metadata.
        """
        response = generate_response(question, route, evidence, include_evidence, reason)
        if route is not RouteName.CURATED_RAG or not evidence:
            return response

        with trace.get_tracer(__name__).start_as_current_span("generation.provider") as span:
            span.set_attribute("generation.provider", "ollama")
            acquired = _GENERATION_LOCK.acquire(blocking=False)
            try:
                if not acquired:
                    raise OllamaProviderError("busy")
                base_url = _loopback_base_url(self.settings.ollama_base_url)
                prompt = _build_prompt(question, evidence, self.settings)
                answer = asyncio.run(self._complete(base_url, prompt))
            except Exception as exc:
                code = str(exc) if isinstance(exc, OllamaProviderError) else "provider_error"
                response.generation_mode = GenerationMode.DETERMINISTIC_FALLBACK
                response.debug.update(ollama_fallback=True, ollama_error_code=code)
                span.set_attribute("generation.fallback", True)
                span.set_attribute("generation.provider_error", code)
            else:
                response.answer = answer
                response.generation_mode = GenerationMode.LLM
                response.debug["ollama_used"] = True
                span.set_attribute("generation.fallback", False)
            finally:
                if acquired:
                    _GENERATION_LOCK.release()

        return response

    async def _complete(self, base_url: str, prompt: str) -> str:
        try:
            # This deadline covers connection, model loading, inference and response
            # parsing. SDK and agent retries are disabled; capacity never queues.
            async with asyncio.timeout(self.settings.ollama_timeout_seconds):
                async with httpx.AsyncClient(
                    transport=self._transport,
                    trust_env=False,
                    follow_redirects=False,
                    timeout=self.settings.ollama_timeout_seconds,
                ) as http_client:
                    provider = OpenAIProvider(
                        base_url=base_url,
                        api_key="ollama",
                        http_client=http_client,
                    )
                    provider.client.max_retries = 0
                    model = OpenAIChatModel(
                        self.settings.ollama_model,
                        provider=provider,
                        profile=OpenAIModelProfile(
                            openai_chat_supports_max_completion_tokens=False
                        ),
                    )
                    agent = Agent(
                        model,
                        system_prompt=SYSTEM_PROMPT,
                        output_type=str,
                        retries=0,
                        model_settings={
                            "temperature": 0,
                            "max_tokens": self.settings.ollama_max_output_tokens,
                        },
                    )
                    result = await agent.run(prompt)
                    if result.response.finish_reason == "length":
                        raise OllamaProviderError("output_truncated")
                    output = result.output
                    if not isinstance(output, str) or not output.strip():
                        raise OllamaProviderError("empty_content")

                    return output.strip()
        except (TimeoutError, httpx.TimeoutException) as exc:
            raise OllamaProviderError("timeout") from exc


def build_generator(settings: Settings) -> OllamaEvidenceGenerator | None:
    """Build a local generator only on explicit selection.

    Parameters
    ----------
    settings
        Backend configuration; no remote-provider credentials are required.

    Returns
    -------
    OllamaEvidenceGenerator or None
        Ollama generator when selected, otherwise no override.
    """
    if settings.assistant_generator.lower() == "ollama":
        return OllamaEvidenceGenerator(settings)
    return None


def _loopback_base_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        if (
            parsed.scheme not in {"http", "https"}
            or not host
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/", "/v1", "/v1/"}
        ):
            raise ValueError
        # Avoid DNS/proxy routing for localhost. Other hostnames are not allowed.
        address = ip_address("127.0.0.1" if host == "localhost" else host)
        if not address.is_loopback:
            raise ValueError
        port = parsed.port
    except ValueError as exc:
        raise OllamaProviderError("invalid_loopback_base_url") from exc
    authority = f"[{address}]" if address.version == 6 else str(address)
    if port is not None:
        authority += f":{port}"

    return f"{parsed.scheme}://{authority}/v1/"


def _build_prompt(question: str, evidence: list[Evidence], settings: Settings) -> str:
    # UTF-8 bytes conservatively bound text tokens for the baseline byte-fallback
    # Gemma/Llama tokenizers. Reserve additional tokens for their chat templates.
    # Custom models/templates need operator validation against this assumption.
    budget = (
        settings.ollama_context_tokens
        - settings.ollama_max_output_tokens
        - _TEMPLATE_TOKEN_RESERVE
        - len(SYSTEM_PROMPT.encode("utf-8"))
    )
    prompt = f"Question: {question}\n\nAccepted E3SM evidence:"
    included = False
    for index, item in enumerate(evidence, start=1):
        block = (
            f"\n\nSource {index}: {item.source.source_id}\n"
            f"Title: {item.source.title}\nSection: {item.source.section}\n"
            f"Provenance: {item.source.provenance}\nText: {item.text}"
        )
        if len((prompt + block).encode("utf-8")) > budget:
            break
        prompt += block
        included = True
    if not included:
        raise OllamaProviderError("context_budget_exceeded")

    return prompt
