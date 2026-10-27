"""Generic provider for any OpenAI-compatible chat completions endpoint.

This replaces the LivAI-specific module. LivAI (LLNL), GitHub Copilot, GitHub
Models, Azure OpenAI, vLLM, Ollama, and similar gateways all speak the same
``POST {base_url}/chat/completions`` contract with a bearer token, and nothing
in the previous LivAI client was specific to LLNL beyond its default URL.

Two things were fixed on the way to making it generic, both found by testing
against the GitHub Copilot endpoint:

- The old client appended ``/v1`` to every base URL. Copilot serves
  ``/chat/completions`` at the root and returns 404 under ``/v1``. The base
  URL is now used verbatim, so the operator supplies ``.../v1`` for gateways
  that need it (LivAI does) and omits it for those that do not.
- The old client ran through PydanticAI, whose response model requires the
  OpenAI ``object: "chat.completion"`` field. Copilot omits it. The raw
  ``openai`` SDK is lenient here and is already an installed dependency, so
  this module uses it directly and PydanticAI is no longer on the request path.
"""

from __future__ import annotations

import re
from typing import Any, Protocol
from urllib.parse import urlparse

from openai import APIStatusError, OpenAI
from opentelemetry import trace

from e3sm_ai_platform.application.generation import generate_response
from e3sm_ai_platform.domain.models import (
    Evidence,
    GenerationMode,
    QueryResponse,
    RouteName,
    UnsupportedTemperatureError,
)
from e3sm_ai_platform.infrastructure.settings import Settings
from e3sm_ai_platform.integrations.prompting import SYSTEM_PROMPT, ChatClient, build_messages

PROVIDER_NAME = "openai_compatible"
DEFAULT_TIMEOUT_SECONDS = 120.0


class OpenAICompatibleProviderError(RuntimeError):
    """Sanitized provider error for public debug metadata and fallback control."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class CreateCompletion(Protocol):
    """The one call into the ``openai`` SDK this module depends on.

    Tests inject a plain callable with this shape so no network is touched and
    the SDK internals stay out of the test surface.
    """

    def __call__(self, **kwargs: Any) -> Any:
        """Issue a chat completion request and return the SDK response."""


def _sdk_create_completion(api_key: str, base_url: str, timeout: float) -> CreateCompletion:
    """Return a ``CreateCompletion`` backed by the real ``openai`` SDK.

    The SDK's ``create`` is a three-way overload with required keyword-only
    parameters, so it cannot satisfy a ``**kwargs`` Protocol structurally. This
    thin wrapper gives the type checker an honest signature and keeps the SDK
    construction in one place. The client only stores the key; nothing is sent
    until the returned callable runs.
    """
    sdk = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def create(**kwargs: Any) -> Any:
        return sdk.chat.completions.create(**kwargs)

    return create


class OpenAICompatibleChatClient:
    """Chat client for any gateway speaking the OpenAI chat completions API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        create_completion: CreateCompletion | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        temperature: float | None = 0.0,
    ) -> None:
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        # The base URL is validated in complete(), not here. Raising during
        # construction would surface inside the lazily built CompassService
        # and turn every request including /health into a 500 with no
        # fallback. See _sdk_create_completion for why no request leaves here.
        self._create_completion: CreateCompletion = (
            create_completion
            if create_completion is not None
            else _sdk_create_completion(api_key, base_url, timeout)
        )

    def complete(self, messages: list[dict[str, str]]) -> str:
        """Return validated assistant text for the supplied chat messages."""
        with trace.get_tracer(__name__).start_as_current_span("generation.provider") as span:
            span.set_attribute("generation.provider", PROVIDER_NAME)
            span.set_attribute("generation.model", self.model)
            self._validate_https_base_url(span)
            request: dict[str, Any] = {"model": self.model, "messages": messages}
            if self.temperature is not None:
                request["temperature"] = self.temperature
            try:
                response = self._create_completion(**request)
            except Exception as exc:
                if self.temperature is not None and _is_temperature_rejection(exc):
                    raise self._fail(span, "unsupported_temperature") from exc
                raise self._fail(span, "request_error") from exc

            content = _first_choice_content(response)
            if content is None:
                raise self._fail(span, "malformed_response")
            if not content.strip():
                raise self._fail(span, "empty_content")

            span.set_attribute("generation.fallback", False)
            return content.strip()

    def _validate_https_base_url(self, span: trace.Span) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise self._fail(span, "invalid_https_base_url")

    @staticmethod
    def _fail(span: trace.Span, code: str) -> OpenAICompatibleProviderError:
        span.set_attribute("generation.provider_error", code)
        span.set_attribute("generation.fallback", code != "unsupported_temperature")

        return OpenAICompatibleProviderError(code)


class OpenAICompatibleEvidenceGenerator:
    """Curated-route generator that preserves server citations and evidence."""

    def __init__(self, client: ChatClient) -> None:
        self.client = client

    def __call__(
        self,
        question: str,
        route: RouteName,
        evidence: list[Evidence],
        include_evidence: bool,
        reason: str,
    ) -> QueryResponse:
        """Generate an answer, raising on unsupported temperature instead of falling back.

        Raises
        ------
        UnsupportedTemperatureError
            If the provider explicitly rejects the configured temperature.
        """
        if route is not RouteName.CURATED_RAG or not evidence:
            return generate_response(question, route, evidence, include_evidence, reason)

        fallback = generate_response(question, route, evidence, include_evidence, reason)
        fallback.debug["provider"] = PROVIDER_NAME
        try:
            answer = self.client.complete(build_messages(question, evidence))
        except Exception as exc:
            if (
                isinstance(exc, OpenAICompatibleProviderError)
                and exc.code == "unsupported_temperature"
            ):
                raise UnsupportedTemperatureError() from None

            fallback.generation_mode = GenerationMode.DETERMINISTIC_FALLBACK
            fallback.debug["provider_fallback"] = True
            fallback.debug["provider_error"] = "provider_error"

            if isinstance(exc, OpenAICompatibleProviderError):
                fallback.debug["provider_error_code"] = exc.code

            return fallback

        fallback.answer = answer + "\n\nI have not added claims beyond the cited E3SM sources."
        fallback.generation_mode = GenerationMode.LLM
        fallback.debug["provider_used"] = True

        return fallback


def build_generator(settings: Settings) -> OpenAICompatibleEvidenceGenerator | None:
    """Return the generator only when explicitly enabled and configured."""
    if not settings.openai_compatible_enabled:
        return None
    assert settings.openai_compatible_api_key is not None
    assert settings.openai_compatible_base_url is not None
    client = OpenAICompatibleChatClient(
        api_key=settings.openai_compatible_api_key,
        model=settings.openai_compatible_model,
        base_url=settings.openai_compatible_base_url,
        temperature=settings.openai_compatible_temperature,
    )
    return OpenAICompatibleEvidenceGenerator(client)


def _is_temperature_rejection(exc: Exception) -> bool:
    """Recognize explicit temperature rejections without exposing provider details."""
    if not isinstance(exc, APIStatusError) or exc.status_code not in {400, 422}:
        return False

    body = exc.body
    if not isinstance(body, dict):
        return False

    error = body.get("error", body)
    if not isinstance(error, dict):
        return False

    param = error.get("param", exc.param)
    code = error.get("code", exc.code)
    if param is not None and param != "temperature":
        return False
    if param == "temperature" and code in ("unsupported_parameter", "unsupported_value"):
        return True

    message = error.get("message")
    if not isinstance(message, str):
        return False

    return (
        re.search(
            r"unsupported (?:parameter|value):?\s*['\"]?temperature\b"
            r"|\btemperature['\"]?\s+(?:is\s+)?(?:not supported|unsupported)"
            r"(?=\s*(?:[.!]|$|(?:for|with|by)\s+(?:this|the)\s+model\b))"
            r"|\bdoes not support\s+(?:the\s+)?['\"]?temperature['\"]?(?=\s*(?:[.!]|$))",
            message,
            re.IGNORECASE,
        )
        is not None
    )


def _first_choice_content(response: object) -> str | None:
    """Pull ``choices[0].message.content`` without trusting the response type.

    Gateways differ in how faithfully they follow the OpenAI schema (Copilot
    omits ``object`` and ``created``), so this reads only the fields it needs
    and treats anything missing as a malformed response rather than crashing.
    """
    choices = getattr(response, "choices", None)
    if not choices:
        return None
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None)
    return content if isinstance(content, str) else None


__all__ = [
    "PROVIDER_NAME",
    "SYSTEM_PROMPT",
    "OpenAICompatibleChatClient",
    "OpenAICompatibleEvidenceGenerator",
    "OpenAICompatibleProviderError",
    "build_generator",
    "build_messages",
]
