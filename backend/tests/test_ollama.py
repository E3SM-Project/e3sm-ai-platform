import asyncio
import json

import httpx
import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from e3sm_ai_platform.application.generation import generate_response
from e3sm_ai_platform.application.service import CompassService, build_provider_generator
from e3sm_ai_platform.domain.models import Evidence, GenerationMode, QueryRequest, RouteName
from e3sm_ai_platform.infrastructure.settings import Settings, load_settings
from e3sm_ai_platform.integrations.ollama import (
    _GENERATION_LOCK,
    _TEMPLATE_TOKEN_RESERVE,
    OllamaEvidenceGenerator,
    _build_prompt,
    _loopback_base_url,
    build_generator,
)
from e3sm_ai_platform.integrations.prompting import SYSTEM_PROMPT


@pytest.fixture
def evidence() -> list[Evidence]:
    response = CompassService(settings=Settings()).query(
        QueryRequest(question="How do I choose an E3SM compset?")
    )
    assert response.evidence
    return response.evidence[:1]


def _reply(
    content: object = "Compsets define component configurations.", finish_reason: str = "stop"
) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "id": "local-test",
            "object": "chat.completion",
            "created": 0,
            "model": "compass-gemma3:4b",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": finish_reason,
                }
            ],
        },
    )


def test_selection_and_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INFERENCE_BACKEND", "ollama")
    monkeypatch.delenv("OPENAI_COMPATIBLE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_COMPATIBLE_BASE_URL", raising=False)
    monkeypatch.delenv("ARGO_USER", raising=False)
    monkeypatch.setenv("OLLAMA_MODEL", "local-approved-model")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1/")
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "10")
    monkeypatch.setenv("OLLAMA_CONTEXT_TOKENS", "2048")
    monkeypatch.setenv("OLLAMA_MAX_OUTPUT_TOKENS", "256")
    settings = load_settings(load_dotenv_file=False)

    assert settings.ollama_model == "local-approved-model"
    assert settings.ollama_timeout_seconds == 10
    assert settings.ollama_context_tokens == 2048
    assert settings.ollama_max_output_tokens == 256
    assert settings.provider_misconfiguration() is None
    assert isinstance(build_provider_generator(settings), OllamaEvidenceGenerator)
    assert build_generator(Settings()) is None
    assert build_provider_generator(Settings()) is None


@pytest.mark.parametrize(
    "changes",
    [
        {"ollama_timeout_seconds": 0},
        {"ollama_timeout_seconds": 301},
        {"ollama_timeout_seconds": float("nan")},
        {"ollama_timeout_seconds": float("inf")},
        {"ollama_context_tokens": 100},
        {"ollama_context_tokens": 32769},
        {"ollama_max_output_tokens": 0},
        {"ollama_max_output_tokens": 4000},
        {"ollama_model": " "},
    ],
)
def test_invalid_settings(changes: dict) -> None:
    with pytest.raises(ValueError):
        Settings(**changes)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://localhost:11434", "http://127.0.0.1:11434/v1/"),
        ("http://127.0.0.1:11434/v1/", "http://127.0.0.1:11434/v1/"),
        ("http://[::1]:11434/v1", "http://[::1]:11434/v1/"),
        ("https://127.0.0.1/", "https://127.0.0.1/v1/"),
    ],
)
def test_endpoint_normalization(url: str, expected: str) -> None:
    assert _loopback_base_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "http://remote.example/v1/",
        "http://192.168.1.2:11434/v1/",
        "http://0.0.0.0:11434",
        "http://localhost.evil/v1/",
        "http://user:secret@localhost:11434/v1/",
        "http://localhost/v1/?token=secret",
        "http://localhost/v1/#secret",
        "http://localhost:bad/v1/",
        "http://[broken",
        "file:///v1/",
        "http://localhost/other",
        "http://[::ffff:192.168.1.2]:11434",
    ],
)
def test_invalid_endpoint_never_sends(url: str, evidence: list[Evidence]) -> None:
    def forbidden(request: httpx.Request) -> httpx.Response:
        pytest.fail("invalid endpoint made an HTTP request")

    generator = OllamaEvidenceGenerator(
        Settings(ollama_base_url=url), httpx.MockTransport(forbidden)
    )
    response = generator("compsets", RouteName.CURATED_RAG, evidence, True, "test")

    assert response.debug["ollama_error_code"] == "invalid_loopback_base_url"
    assert response.generation_mode is GenerationMode.DETERMINISTIC_FALLBACK
    assert response.citations


@pytest.mark.parametrize("include_evidence", [True, False])
def test_success_preserves_contract_and_request(
    evidence: list[Evidence], include_evidence: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    requests: list[httpx.Request] = []

    def complete(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return _reply()

    # Ambient proxy settings must not route local evidence to a proxy.
    monkeypatch.setenv("HTTP_PROXY", "http://unapproved.invalid:9999")
    settings = Settings(assistant_generator="ollama", ollama_model="approved-local")
    generator = OllamaEvidenceGenerator(settings, httpx.MockTransport(complete))
    response = generator("compsets", RouteName.CURATED_RAG, evidence, include_evidence, "test")
    baseline = generate_response(
        "compsets", RouteName.CURATED_RAG, evidence, include_evidence, "test"
    )

    assert response.generation_mode is GenerationMode.LLM
    assert response.debug["ollama_used"] is True
    assert response.citations == baseline.citations
    assert response.evidence == baseline.evidence
    assert response.retrieved_evidence == baseline.retrieved_evidence
    assert len(requests) == 1
    assert str(requests[0].url) == "http://127.0.0.1:11434/v1/chat/completions"
    body = json.loads(requests[0].content)
    assert body["model"] == "approved-local"
    assert body["max_tokens"] == settings.ollama_max_output_tokens
    assert body["messages"][0]["content"] == SYSTEM_PROMPT
    assert evidence[0].text in body["messages"][1]["content"]


@pytest.mark.parametrize("route", list(RouteName))
def test_bypass_routes(route: RouteName, evidence: list[Evidence]) -> None:
    def forbidden(request: httpx.Request) -> httpx.Response:
        pytest.fail("bypass invoked the provider")

    generator = OllamaEvidenceGenerator(Settings(), httpx.MockTransport(forbidden))
    accepted = [] if route is RouteName.CURATED_RAG else evidence
    response = generator("question", route, accepted, True, "test")

    assert response.generation_mode is GenerationMode.DETERMINISTIC
    assert not any(key.startswith("ollama_") for key in response.debug)


@pytest.mark.parametrize(
    "failure",
    ["missing_model", "server_error", "unavailable", "malformed", "empty", "redirect", "truncated"],
)
def test_sanitized_fallback_without_retries(failure: str, evidence: list[Evidence]) -> None:
    requests: list[httpx.Request] = []

    def fail(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if failure == "unavailable":
            raise httpx.ConnectError("secret-provider-payload", request=request)
        if failure == "malformed":
            return httpx.Response(200, json={"private": "secret-provider-payload"})
        if failure == "empty":
            return _reply(" ")
        if failure == "truncated":
            return _reply("Incomplete claim", finish_reason="length")
        if failure == "redirect":
            return httpx.Response(307, headers={"location": "https://unapproved.invalid/"})
        return httpx.Response(
            404 if failure == "missing_model" else 500, json={"error": "secret-provider-payload"}
        )

    generator = OllamaEvidenceGenerator(Settings(), httpx.MockTransport(fail))
    response = generator("compsets", RouteName.CURATED_RAG, evidence, True, "test")

    assert len(requests) == 1
    assert response.generation_mode is GenerationMode.DETERMINISTIC_FALLBACK
    assert response.debug["ollama_fallback"] is True
    expected_codes = {"empty": "empty_content", "truncated": "output_truncated"}
    assert response.debug["ollama_error_code"] == expected_codes.get(failure, "provider_error")
    assert "secret-provider-payload" not in response.model_dump_json()
    assert "unapproved.invalid" not in response.model_dump_json()
    assert response.citations


def test_timeout_cancels_and_releases_capacity(
    evidence: list[Evidence], monkeypatch: pytest.MonkeyPatch
) -> None:
    cancelled = False
    calls = 0
    original_timeout = asyncio.timeout
    deadlines: list[asyncio.Timeout] = []

    def controlled_timeout(delay: float) -> asyncio.Timeout:
        assert delay == 120
        deadline = original_timeout(None)
        deadlines.append(deadline)
        return deadline

    monkeypatch.setattr(asyncio, "timeout", controlled_timeout)

    async def stall(request: httpx.Request) -> httpx.Response:
        nonlocal cancelled, calls
        calls += 1
        # Expire the real asyncio timeout only after the transport starts.
        # No sleeps or machine-speed-dependent thresholds are needed.
        deadlines[0].reschedule(asyncio.get_running_loop().time())
        try:
            await asyncio.Event().wait()
        finally:
            cancelled = True
        return _reply()

    generator = OllamaEvidenceGenerator(Settings(), httpx.MockTransport(stall))
    response = generator("compsets", RouteName.CURATED_RAG, evidence, True, "test")

    assert response.debug["ollama_error_code"] == "timeout"
    assert cancelled
    assert calls == 1
    assert not _GENERATION_LOCK.locked()


def test_busy_falls_back_without_queue_or_network(evidence: list[Evidence]) -> None:
    def forbidden(request: httpx.Request) -> httpx.Response:
        pytest.fail("busy provider made a request")

    generator = OllamaEvidenceGenerator(Settings(), httpx.MockTransport(forbidden))
    with _GENERATION_LOCK:
        response = generator("compsets", RouteName.CURATED_RAG, evidence, True, "test")
        assert _GENERATION_LOCK.locked()

    assert response.debug["ollama_error_code"] == "busy"


def test_context_budget_includes_unicode_instructions_and_output(evidence: list[Evidence]) -> None:
    settings = Settings()
    prompt = _build_prompt("é" * 100, evidence * 100, settings)
    total = len((SYSTEM_PROMPT + prompt).encode("utf-8"))

    assert (
        total + settings.ollama_max_output_tokens + _TEMPLATE_TOKEN_RESERVE
        <= settings.ollama_context_tokens
    )
    assert evidence[0].text in prompt
    assert "Source 100:" not in prompt


def test_exact_context_boundary(evidence: list[Evidence]) -> None:
    settings = Settings()
    evidence[0].text = "x"
    prompt = _build_prompt("compsets", evidence, settings)
    available = (
        settings.ollama_context_tokens
        - settings.ollama_max_output_tokens
        - _TEMPLATE_TOKEN_RESERVE
        - len((SYSTEM_PROMPT + prompt).encode("utf-8"))
    )
    evidence[0].text += "x" * available
    assert _build_prompt("compsets", evidence, settings).endswith(evidence[0].text)
    evidence[0].text += "x"

    with pytest.raises(RuntimeError, match="context_budget_exceeded"):
        _build_prompt("compsets", evidence, settings)


@pytest.mark.parametrize("oversized_question", [True, False])
def test_context_overflow_falls_back_without_network(
    oversized_question: bool, evidence: list[Evidence]
) -> None:
    def forbidden(request: httpx.Request) -> httpx.Response:
        pytest.fail("oversized prompt made a request")

    question = "é" * 4096 if oversized_question else "compsets"
    if not oversized_question:
        evidence[0].text = "é" * 4096
    generator = OllamaEvidenceGenerator(Settings(), httpx.MockTransport(forbidden))
    response = generator(question, RouteName.CURATED_RAG, evidence, True, "test")

    assert response.debug["ollama_error_code"] == "context_budget_exceeded"


@pytest.mark.parametrize("success", [True, False])
def test_service_and_provider_spans_are_sanitized(
    success: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    monkeypatch.setattr(trace, "get_tracer", provider.get_tracer)

    def fail(request: httpx.Request) -> httpx.Response:
        if success:
            return _reply()
        raise httpx.ConnectError("secret-provider-payload")

    generator = OllamaEvidenceGenerator(Settings(), httpx.MockTransport(fail))
    service = CompassService(settings=Settings(), generator=generator)
    response = service.query(QueryRequest(question="How do I choose an E3SM compset?"))
    spans = {span.name: span for span in exporter.get_finished_spans()}

    assert response.debug["ollama_used" if success else "ollama_fallback"]
    assert spans["generation.generate"].attributes is not None
    assert spans["generation.provider"].attributes is not None
    assert spans["generation.generate"].attributes["generation.provider_fallback"] is not success
    assert spans["generation.generate"].attributes["generation.provider_used"] is success
    assert spans["generation.provider"].attributes["generation.provider"] == "ollama"
    assert not spans["generation.provider"].events
    assert "secret-provider-payload" not in str(exporter.get_finished_spans())
    provider.shutdown()
