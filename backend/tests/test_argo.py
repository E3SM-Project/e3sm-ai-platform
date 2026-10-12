"""Tests for the Argo (ANL) generator integration.

Every test runs offline. The ANL gateway is reachable only from the lab
network, so the HTTP boundary is injected and no test may depend on it.
"""

from collections.abc import Iterator
from typing import Any

import httpx
import pytest

from e3sm_ai_platform.application.service import CompassService, build_provider_generator
from e3sm_ai_platform.domain.models import (
    Evidence,
    GenerationMode,
    QueryRequest,
    RouteName,
    SourceMetadata,
)
from e3sm_ai_platform.infrastructure.settings import (
    DEFAULT_ARGO_BASE_URL,
    DEFAULT_ARGO_MODEL,
    Settings,
    load_settings,
)
from e3sm_ai_platform.integrations.argo import (
    SYSTEM_PROMPT,
    ArgoChatClient,
    ArgoEvidenceGenerator,
    ArgoProviderError,
    build_argo_messages,
    build_generator,
)

ARGO_ENV_KEYS = [
    "INFERENCE_BACKEND",
    "ARGO_USER",
    "ARGO_API_KEY",
    "ARGO_MODEL",
    "ARGO_BASE_URL",
    "ARGO_TEMPERATURE",
    "LIVAI_API_KEY",
    "CORS_ALLOW_ORIGINS",
]


class FakeTransport:
    """Record the outgoing request and return a scripted response."""

    def __init__(
        self,
        payload: Any = None,
        status_code: int = 200,
        raise_exc: Exception | None = None,
        body_text: str | None = None,
    ) -> None:
        self.payload = {"response": "Argo answer from cited evidence."}
        if payload is not None:
            self.payload = payload
        self.status_code = status_code
        self.raise_exc = raise_exc
        self.body_text = body_text
        self.url: str | None = None
        self.json_body: dict[str, Any] | None = None
        self.timeout: float | None = None
        self.calls = 0

    def post(self, url: str, json: dict[str, Any], timeout: float) -> httpx.Response:
        self.calls += 1
        self.url = url
        self.json_body = json
        self.timeout = timeout
        if self.raise_exc is not None:
            raise self.raise_exc
        if self.body_text is not None:
            return httpx.Response(self.status_code, text=self.body_text)
        return httpx.Response(self.status_code, json=self.payload)


class FakeChatClient:
    def __init__(self, response: str = "Argo answer.", fail: bool = False) -> None:
        self.response = response
        self.fail = fail
        self.messages: list[dict[str, str]] | None = None

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.messages = messages
        if self.fail:
            raise ArgoProviderError("invalid_model")
        return self.response


@pytest.fixture
def clear_argo_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    for key in ARGO_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    yield


def _evidence() -> list[Evidence]:
    source = SourceMetadata.model_validate(
        {
            "source_id": "user-guide:compsets",
            "title": "E3SM User Guide: Compsets",
            "url": "https://docs.e3sm.org/E3SM/user-guide/compsets/",
            "section": "Compsets",
            "component": "User Guide",
            "version": "latest",
            "authority": "official",
            "provenance": "official test source",
        }
    )
    return [
        Evidence(
            chunk_id="user-guide:compsets#chunk-1",
            text="Compsets define active, data, stub, or prescribed components.",
            score=0.5,
            source=source,
            matched_terms=["compsets"],
            coverage=0.5,
        )
    ]


def _client(**kwargs: Any) -> tuple[ArgoChatClient, FakeTransport]:
    temperature = kwargs.pop("temperature", None)
    transport = kwargs.pop("transport", None) or FakeTransport(**kwargs)
    client = ArgoChatClient(
        user="testuser",
        model="gpt4o",
        base_url=DEFAULT_ARGO_BASE_URL,
        transport=transport,
        temperature=temperature,
    )
    return client, transport


# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------


def test_argo_settings_defaults(clear_argo_env: None) -> None:
    settings = load_settings(load_dotenv_file=False)

    assert settings.argo_model == DEFAULT_ARGO_MODEL
    assert settings.argo_base_url == DEFAULT_ARGO_BASE_URL
    assert settings.argo_user is None
    assert settings.argo_enabled is False


def test_argo_enablement_requires_flag_and_user(clear_argo_env: None) -> None:
    assert Settings(assistant_generator="argo").argo_enabled is False
    assert Settings(argo_user="testuser").argo_enabled is False
    assert Settings(assistant_generator="argo", argo_user="testuser").argo_enabled is True
    assert Settings(assistant_generator="ARGO", argo_user="testuser").argo_enabled is True


def test_argo_user_falls_back_to_existing_anl_env_var(
    clear_argo_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """ANL tooling already exports ARGO_API_KEY; accept it as the username."""
    monkeypatch.setenv("ARGO_API_KEY", "fromapikey")
    assert load_settings(load_dotenv_file=False).argo_user == "fromapikey"

    monkeypatch.setenv("ARGO_USER", "fromuser")
    assert load_settings(load_dotenv_file=False).argo_user == "fromuser"


def test_selecting_argo_does_not_enable_livai(clear_argo_env: None) -> None:
    settings = Settings(assistant_generator="argo", argo_user="testuser", livai_api_key="secret")

    assert settings.argo_enabled is True
    assert settings.livai_enabled is False


# --------------------------------------------------------------------------
# Request shape
# --------------------------------------------------------------------------


def test_argo_request_uses_body_auth_and_documented_endpoint() -> None:
    client, transport = _client()

    client.complete(build_argo_messages("How do I choose a compset?", _evidence()))

    assert transport.url == "https://apps.inside.anl.gov/argoapi/api/v1/resource/chat/"
    assert transport.json_body is not None
    # Argo authenticates on a body field, not an Authorization header.
    assert transport.json_body["user"] == "testuser"
    assert transport.json_body["model"] == "gpt4o"
    # A top-level system field is rejected when messages are present.
    assert "system" not in transport.json_body


def test_argo_omits_temperature_by_default() -> None:
    """Claude Sonnet 5 on Argo returns 400 when temperature is present at all."""
    client, transport = _client()

    client.complete(build_argo_messages("question", _evidence()))

    assert transport.json_body is not None
    assert "temperature" not in transport.json_body


def test_argo_sends_temperature_only_when_configured() -> None:
    client, transport = _client(temperature=0.0)

    client.complete(build_argo_messages("question", _evidence()))

    assert transport.json_body is not None
    assert transport.json_body["temperature"] == 0.0


def test_argo_temperature_setting_parses_blank_as_unset(
    clear_argo_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert load_settings(load_dotenv_file=False).argo_temperature is None

    monkeypatch.setenv("ARGO_TEMPERATURE", "")
    assert load_settings(load_dotenv_file=False).argo_temperature is None

    monkeypatch.setenv("ARGO_TEMPERATURE", "0.2")
    assert load_settings(load_dotenv_file=False).argo_temperature == 0.2


def test_argo_prompt_keeps_system_constraints_separate_from_evidence() -> None:
    messages = build_argo_messages("How do I choose a compset?", _evidence())

    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == SYSTEM_PROMPT
    assert messages[1]["role"] == "user"
    assert "How do I choose a compset?" in messages[1]["content"]
    assert "user-guide:compsets" in messages[1]["content"]
    assert SYSTEM_PROMPT not in messages[1]["content"]


def test_argo_prompt_matches_livai_prompt() -> None:
    """One prompt builder keeps evidence-first wording identical across providers."""
    from e3sm_ai_platform.integrations.livai import build_livai_messages

    question = "How do I choose a compset?"
    assert build_argo_messages(question, _evidence()) == build_livai_messages(question, _evidence())


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------


def test_argo_rejects_non_https_base_url() -> None:
    with pytest.raises(ArgoProviderError) as excinfo:
        ArgoChatClient(
            user="testuser",
            model="gpt4o",
            base_url="http://apps.inside.anl.gov/argoapi",
            transport=FakeTransport(),
        )

    assert excinfo.value.code == "invalid_https_base_url"


@pytest.mark.parametrize(
    ("body", "expected_code"),
    [
        (
            "You selected: gpt4turbo, which is an invalid model. "
            "Consult the documentation for details.",
            "invalid_model",
        ),
        (
            "Invalid JSON body: 1 validation error for Prompt\nuser\n  Field required",
            "invalid_request_body",
        ),
        (
            "You passed a messages field along with a system and or prompt field. "
            "Please only pass messages with any system and user prompts included.",
            "invalid_request_body",
        ),
    ],
)
def test_argo_classifies_diagnostics_returned_with_http_200(body: str, expected_code: str) -> None:
    """Guard the case where a gateway diagnostic arrives with a success status.

    The live gateway returns 400 for these inputs, so the status check normally
    fires first. This covers the fallback path: without it, gateway prose
    returned with a 200 would reach the user as a cited E3SM answer.
    """
    client, _ = _client(payload={"response": body})

    with pytest.raises(ArgoProviderError) as excinfo:
        client.complete(build_argo_messages("question", _evidence()))

    assert excinfo.value.code == expected_code


def test_argo_detects_relayed_upstream_provider_error() -> None:
    """Some faults arrive as a nested object rather than a string."""
    client, _ = _client(payload={"response": {"error": {"code": 500, "message": "Internal"}}})

    with pytest.raises(ArgoProviderError) as excinfo:
        client.complete(build_argo_messages("question", _evidence()))

    assert excinfo.value.code == "upstream_provider_error"


@pytest.mark.parametrize(
    ("kwargs", "expected_code"),
    [
        ({"payload": {"response": "   "}}, "empty_content"),
        ({"payload": {"no_response_field": "x"}}, "upstream_provider_error"),
        ({"status_code": 503, "payload": {"response": "down"}}, "http_503"),
        # Verified live: invalid model / bad body return 400, upstream fault 500.
        (
            {
                "status_code": 400,
                "payload": {"response": "You selected: gpt4turbo, which is an invalid model."},
            },
            "http_400",
        ),
        ({"status_code": 500, "payload": {"response": "Internal error"}}, "http_500"),
        ({"body_text": "<html>gateway</html>"}, "invalid_json_response"),
        ({"raise_exc": httpx.ConnectError("no route to host")}, "transport_error"),
    ],
)
def test_argo_failure_modes_are_sanitized(kwargs: dict[str, Any], expected_code: str) -> None:
    client, _ = _client(**kwargs)

    with pytest.raises(ArgoProviderError) as excinfo:
        client.complete(build_argo_messages("question", _evidence()))

    assert excinfo.value.code == expected_code


def test_argo_accepts_answer_that_merely_mentions_error_wording() -> None:
    """Error matching inspects only the opening of the reply."""
    answer = (
        "Compsets are selected with create_newcase. If you pass an unknown name "
        "the tool reports that it is an invalid model configuration."
    )
    client, _ = _client(payload={"response": answer})

    assert client.complete(build_argo_messages("question", _evidence())) == answer


# --------------------------------------------------------------------------
# Generator behavior
# --------------------------------------------------------------------------


def test_argo_generator_preserves_server_citations_and_evidence() -> None:
    client = FakeChatClient()
    generator = ArgoEvidenceGenerator(client)

    response = generator(
        question="How do I choose a compset?",
        route=RouteName.CURATED_RAG,
        evidence=_evidence(),
        include_evidence=True,
        reason="curated",
    )

    assert response.generation_mode is GenerationMode.LLM
    assert response.debug["argo_used"] is True
    assert "Argo answer." in response.answer
    # Citations are server-attached and never taken from the model.
    assert [citation.source_id for citation in response.citations] == ["user-guide:compsets"]
    assert len(response.evidence) == 1


def test_argo_failure_falls_back_to_deterministic_cited_answer() -> None:
    generator = ArgoEvidenceGenerator(FakeChatClient(fail=True))

    response = generator(
        question="How do I choose a compset?",
        route=RouteName.CURATED_RAG,
        evidence=_evidence(),
        include_evidence=True,
        reason="curated",
    )

    assert response.generation_mode is GenerationMode.DETERMINISTIC_FALLBACK
    assert response.debug["argo_fallback"] is True
    assert response.debug["argo_error_code"] == "invalid_model"
    assert [citation.source_id for citation in response.citations] == ["user-guide:compsets"]
    assert "I have not added claims beyond these cited sources." in response.answer


def test_argo_is_not_called_for_non_curated_routes() -> None:
    client = FakeChatClient()
    generator = ArgoEvidenceGenerator(client)

    response = generator(
        question="When is the next workshop?",
        route=RouteName.WEB_SEARCH,
        evidence=[],
        include_evidence=True,
        reason="web",
    )

    assert client.messages is None
    assert response.generation_mode is GenerationMode.DETERMINISTIC


def test_argo_debug_never_exposes_user_or_endpoint() -> None:
    client = ArgoChatClient(
        user="secretuser",
        model="gpt4o",
        base_url=DEFAULT_ARGO_BASE_URL,
        transport=FakeTransport(raise_exc=httpx.ConnectError("boom")),
    )
    response = ArgoEvidenceGenerator(client)(
        question="How do I choose a compset?",
        route=RouteName.CURATED_RAG,
        evidence=_evidence(),
        include_evidence=True,
        reason="curated",
    )

    serialized = response.model_dump_json()
    assert "secretuser" not in serialized
    assert "apps.inside.anl.gov" not in serialized


# --------------------------------------------------------------------------
# Wiring
# --------------------------------------------------------------------------


def test_build_generator_returns_none_unless_enabled(clear_argo_env: None) -> None:
    assert build_generator(Settings()) is None
    assert build_generator(Settings(assistant_generator="argo")) is None
    assert isinstance(
        build_generator(Settings(assistant_generator="argo", argo_user="testuser")),
        ArgoEvidenceGenerator,
    )


def test_provider_selection_is_exclusive(clear_argo_env: None) -> None:
    from e3sm_ai_platform.integrations.livai import LivAIEvidenceGenerator

    assert build_provider_generator(Settings()) is None
    assert isinstance(
        build_provider_generator(Settings(assistant_generator="argo", argo_user="testuser")),
        ArgoEvidenceGenerator,
    )
    assert isinstance(
        build_provider_generator(Settings(assistant_generator="livai", livai_api_key="secret")),
        LivAIEvidenceGenerator,
    )


def test_service_uses_deterministic_default_without_argo_user(clear_argo_env: None) -> None:
    service = CompassService(settings=load_settings(load_dotenv_file=False))

    response = service.query(QueryRequest(question="How do I choose an E3SM compset?"))

    assert response.generation_mode is GenerationMode.DETERMINISTIC
    assert "argo_used" not in response.debug


def test_service_routes_through_argo_when_configured(clear_argo_env: None) -> None:
    transport = FakeTransport(payload={"response": "Compsets select the component set."})
    client = ArgoChatClient(
        user="testuser", model="gpt4o", base_url=DEFAULT_ARGO_BASE_URL, transport=transport
    )
    service = CompassService(
        generator=ArgoEvidenceGenerator(client),
        settings=load_settings(load_dotenv_file=False),
    )

    response = service.query(QueryRequest(question="How do I choose an E3SM compset?"))

    assert transport.calls == 1
    assert response.generation_mode is GenerationMode.LLM
    assert response.debug["argo_used"] is True
    assert response.citations
