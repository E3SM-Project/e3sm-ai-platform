"""Optional Argo generator integration with deterministic fallback.

Argo is the Argonne National Laboratory LLM gateway. It is reachable only from
the ANL network and differs from the OpenAI-compatible LivAI path in two ways
that this adapter exists to absorb:

- Authentication is an ANL username in the ``user`` body field, not a bearer
  token. There is no secret to place in a header, and network position is part
  of the access control.
- The reply is ``{"response": "..."}`` rather than an OpenAI ``choices`` array,
  so the PydanticAI OpenAI provider cannot be pointed at it. Upstream faults
  can arrive with ``response`` holding a nested error object instead of text.

Status codes were verified against the live gateway on 2026-10-07: invalid
model, missing ``user``, and a conflicting top-level ``system`` field all
return 400, and an unavailable upstream model returns 500. The status check
is therefore the primary error path. :func:`_detect_provider_error` is a
secondary guard for the case where the gateway returns 200 while the body
carries a diagnostic rather than an answer; it is cheap and keeps gateway
prose from reaching users as a cited E3SM answer if that behavior changes.

Everything else follows the LivAI adapter so both providers behave identically
from the service's perspective.
"""

from __future__ import annotations

from typing import Any, Protocol
from urllib.parse import urlparse

import httpx
from opentelemetry import trace

from e3sm_ai_platform.application.generation import generate_response
from e3sm_ai_platform.domain.models import Evidence, GenerationMode, QueryResponse, RouteName
from e3sm_ai_platform.infrastructure.settings import Settings
from e3sm_ai_platform.integrations.livai import (
    SYSTEM_PROMPT,
    ChatClient,
    build_livai_messages,
)

DEFAULT_TIMEOUT_SECONDS = 120.0

# Observed gateway diagnostics. These normally arrive with a 4xx and are caught
# by the status check first; the signatures only matter if a diagnostic is ever
# returned with a 200. The gateway exposes no machine-readable error field on
# this path, so matching leading body text is the only option available.
_ERROR_SIGNATURES: tuple[tuple[str, str], ...] = (
    ("which is an invalid model", "invalid_model"),
    ("invalid json body", "invalid_request_body"),
    ("please only pass messages", "invalid_request_body"),
    ("consult the documentation for details", "provider_rejected_request"),
)


class ArgoProviderError(RuntimeError):
    """Sanitized provider error for public debug metadata and fallback control."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class HTTPTransport(Protocol):
    """Injectable HTTP boundary so tests never need the ANL network."""

    def post(self, url: str, json: dict[str, Any], timeout: float) -> httpx.Response:
        """POST a JSON body and return the raw response."""


class ArgoChatClient:
    """Chat client for the Argo gateway's non-OpenAI JSON contract."""

    def __init__(
        self,
        user: str,
        model: str,
        base_url: str,
        transport: HTTPTransport | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        temperature: float | None = None,
    ) -> None:
        self.base_url = base_url
        self.user = user
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self._validate_https_base_url()
        self._transport = transport

    @property
    def chat_url(self) -> str:
        """Return the fully qualified Argo chat endpoint."""
        return f"{self.base_url.rstrip('/')}/api/v1/resource/chat/"

    def complete(self, messages: list[dict[str, str]]) -> str:
        """Return validated Argo output for the supplied chat messages."""
        with trace.get_tracer(__name__).start_as_current_span("generation.provider") as span:
            span.set_attribute("generation.provider", "argo")
            span.set_attribute("generation.model", self.model)
            self._validate_https_base_url()
            payload: dict[str, Any] = {
                "user": self.user,
                "model": self.model,
                # Argo rejects a top-level system field when messages are sent,
                # so the system prompt stays inside the message list.
                "messages": messages,
            }
            # Omitted unless configured. Claude Sonnet 5 on Argo returns 400
            # "`temperature` is deprecated for this model" when it is present,
            # verified live 2026-10-07; older models accept it but do not need it.
            if self.temperature is not None:
                payload["temperature"] = self.temperature
            try:
                response = self._post(payload)
            except Exception as exc:
                raise self._fail(span, "transport_error") from exc

            if response.status_code != 200:
                raise self._fail(span, f"http_{response.status_code}")

            try:
                body = response.json()
            except Exception as exc:
                raise self._fail(span, "invalid_json_response") from exc

            text = body.get("response") if isinstance(body, dict) else None
            # A dict here is Argo relaying an upstream provider fault.
            if not isinstance(text, str):
                raise self._fail(span, "upstream_provider_error")
            if not text.strip():
                raise self._fail(span, "empty_content")

            error_code = _detect_provider_error(text)
            if error_code is not None:
                raise self._fail(span, error_code)

            span.set_attribute("generation.fallback", False)
            return text.strip()

    def _post(self, payload: dict[str, Any]) -> httpx.Response:
        if self._transport is not None:
            return self._transport.post(self.chat_url, json=payload, timeout=self.timeout)
        return httpx.post(self.chat_url, json=payload, timeout=self.timeout)

    @staticmethod
    def _fail(span: trace.Span, code: str) -> ArgoProviderError:
        span.set_attribute("generation.provider_error", code)
        span.set_attribute("generation.fallback", True)
        return ArgoProviderError(code)

    def _validate_https_base_url(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ArgoProviderError("invalid_https_base_url")


class ArgoEvidenceGenerator:
    """Curated-route Argo generator preserving server citations/evidence."""

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
        """Generate a curated response with Argo or the deterministic fallback."""
        if route is not RouteName.CURATED_RAG or not evidence:
            return generate_response(question, route, evidence, include_evidence, reason)

        fallback = generate_response(question, route, evidence, include_evidence, reason)
        try:
            answer = self.client.complete(build_argo_messages(question, evidence))
        except Exception as exc:
            fallback.generation_mode = GenerationMode.DETERMINISTIC_FALLBACK
            fallback.debug["argo_fallback"] = True
            fallback.debug["argo_error"] = "provider_error"
            if isinstance(exc, ArgoProviderError):
                fallback.debug["argo_error_code"] = exc.code
            return fallback

        fallback.answer = answer + "\n\nI have not added claims beyond the cited E3SM sources."
        fallback.generation_mode = GenerationMode.LLM
        fallback.debug["argo_used"] = True
        return fallback


def build_argo_messages(question: str, evidence: list[Evidence]) -> list[dict[str, str]]:
    """Build a source-constrained prompt for Argo.

    Argo accepts the same system/user message shape as the LivAI path, so the
    prompt is shared rather than duplicated. Keeping one builder means the
    evidence-first wording and the deterministic context bound cannot drift
    between the two providers.
    """
    return build_livai_messages(question, evidence)


def build_generator(settings: Settings) -> ArgoEvidenceGenerator | None:
    """Return Argo generator only when explicitly enabled and configured."""
    if not settings.argo_enabled:
        return None
    assert settings.argo_user is not None
    client = ArgoChatClient(
        user=settings.argo_user,
        model=settings.argo_model,
        base_url=settings.argo_base_url,
        temperature=settings.argo_temperature,
    )
    return ArgoEvidenceGenerator(client)


def _detect_provider_error(text: str) -> str | None:
    """Classify a 200 body that carries a gateway diagnostic instead of an answer.

    Only the opening of the reply is examined. Argo's diagnostics appear at the
    start, whereas a legitimate answer could use this wording later on while
    discussing the gateway itself.
    """
    probe = text.strip().lower()[:200]
    for signature, code in _ERROR_SIGNATURES:
        if signature in probe:
            return code
    return None


__all__ = [
    "SYSTEM_PROMPT",
    "ArgoChatClient",
    "ArgoEvidenceGenerator",
    "ArgoProviderError",
    "build_argo_messages",
    "build_generator",
]
