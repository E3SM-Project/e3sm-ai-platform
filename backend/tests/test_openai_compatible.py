"""Tests for the generic OpenAI-compatible provider and the deprecated LivAI alias.

Every test runs offline. The ``openai`` SDK's ``chat.completions`` surface is
injected, so no test depends on reaching LLNL, GitHub, or any other gateway.
"""

from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any

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
    DEFAULT_OPENAI_COMPATIBLE_MODEL,
    DEFAULT_OPENAI_COMPATIBLE_TEMPERATURE,
    LEGACY_LIVAI_BASE_URL,
    LEGACY_LIVAI_MODEL,
    Settings,
    load_settings,
)
from e3sm_ai_platform.integrations.openai_compatible import (
    PROVIDER_NAME,
    OpenAICompatibleChatClient,
    OpenAICompatibleEvidenceGenerator,
    OpenAICompatibleProviderError,
    build_generator,
)
from e3sm_ai_platform.integrations.prompting import (
    MAX_EVIDENCE_PROMPT_CHARS,
    SYSTEM_PROMPT,
    build_messages,
)

PROVIDER_ENV_KEYS = [
    "INFERENCE_BACKEND",
    "OPENAI_COMPATIBLE_API_KEY",
    "OPENAI_COMPATIBLE_MODEL",
    "OPENAI_COMPATIBLE_BASE_URL",
    "OPENAI_COMPATIBLE_TEMPERATURE",
    "LIVAI_API_KEY",
    "LIVAI_MODEL",
    "LIVAI_BASE_URL",
    "ARGO_USER",
    "ARGO_API_KEY",
    "CORS_ALLOW_ORIGINS",
]

TEST_URL = "https://gateway.example.org/v1"


def _sdk_response(content: str | None, *, spec_compliant: bool = True) -> Any:
    """Shape a response like the ``openai`` SDK returns, optionally off-spec.

    GitHub Copilot omits ``object`` and ``created``; ``spec_compliant=False``
    reproduces that so the client is proven tolerant of it.
    """
    message = SimpleNamespace(content=content, role="assistant")
    choice = SimpleNamespace(message=message, index=0, finish_reason="stop")
    fields: dict[str, Any] = {"choices": [choice], "id": "chatcmpl-test", "model": "test"}
    if spec_compliant:
        fields["object"] = "chat.completion"
        fields["created"] = 0
    return SimpleNamespace(**fields)


class FakeCompletions:
    """Callable standing in for ``client.chat.completions.create``.

    Records the request and returns a scripted SDK-shaped response.
    """

    def __init__(
        self,
        response: Any = None,
        raise_exc: Exception | None = None,
    ) -> None:
        self.response = response if response is not None else _sdk_response("Provider answer.")
        self.raise_exc = raise_exc
        self.calls = 0
        self.last_request: dict[str, Any] | None = None

    def __call__(self, **kwargs: Any) -> Any:
        self.calls += 1
        self.last_request = kwargs
        if self.raise_exc is not None:
            raise self.raise_exc
        return self.response


class FakeChatClient:
    def __init__(self, response: str = "Provider answer.", fail: bool = False) -> None:
        self.response = response
        self.fail = fail
        self.messages: list[dict[str, str]] | None = None

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.messages = messages
        if self.fail:
            raise OpenAICompatibleProviderError("request_error")
        return self.response


@pytest.fixture
def clear_provider_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    for key in PROVIDER_ENV_KEYS:
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


def _client(
    completions: FakeCompletions | None = None,
    base_url: str = TEST_URL,
    **kwargs: Any,
) -> tuple[OpenAICompatibleChatClient, FakeCompletions]:
    fake = completions or FakeCompletions()
    client = OpenAICompatibleChatClient(
        api_key="secret-key",
        model="gpt-4o",
        base_url=base_url,
        create_completion=fake,
        **kwargs,
    )
    return client, fake


# --------------------------------------------------------------------------
# Settings: new names
# --------------------------------------------------------------------------


def test_settings_defaults(clear_provider_env: None) -> None:
    settings = load_settings(load_dotenv_file=False)

    assert settings.assistant_generator == "deterministic"
    assert settings.inference_backend == "deterministic"
    assert settings.openai_compatible_api_key is None
    assert settings.openai_compatible_base_url is None
    assert settings.openai_compatible_model == DEFAULT_OPENAI_COMPATIBLE_MODEL
    assert settings.openai_compatible_enabled is False
    assert settings.openai_compatible_from_legacy_livai is False


def test_enablement_requires_backend_key_and_base_url(clear_provider_env: None) -> None:
    """There is no default URL; guessing one could send a key to the wrong host."""
    assert Settings(assistant_generator="openai_compatible").openai_compatible_enabled is False
    assert (
        Settings(
            assistant_generator="openai_compatible", openai_compatible_api_key="k"
        ).openai_compatible_enabled
        is False
    )
    assert (
        Settings(
            assistant_generator="openai_compatible", openai_compatible_base_url=TEST_URL
        ).openai_compatible_enabled
        is False
    )
    assert (
        Settings(
            assistant_generator="openai_compatible",
            openai_compatible_api_key="k",
            openai_compatible_base_url=TEST_URL,
        ).openai_compatible_enabled
        is True
    )


def test_new_env_names_are_read_verbatim(
    clear_provider_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("INFERENCE_BACKEND", "openai_compatible")
    monkeypatch.setenv("OPENAI_COMPATIBLE_API_KEY", "k")
    monkeypatch.setenv("OPENAI_COMPATIBLE_MODEL", "gpt-4o-mini")
    # No /v1 here; the Copilot endpoint serves /chat/completions at the root.
    monkeypatch.setenv("OPENAI_COMPATIBLE_BASE_URL", "https://api.business.githubcopilot.com")

    settings = load_settings(load_dotenv_file=False)

    assert settings.openai_compatible_enabled is True
    assert settings.openai_compatible_model == "gpt-4o-mini"
    assert settings.openai_compatible_base_url == "https://api.business.githubcopilot.com"
    assert settings.openai_compatible_from_legacy_livai is False
    assert settings.deprecation_notice() is None


# --------------------------------------------------------------------------
# Settings: deprecated livai alias
# --------------------------------------------------------------------------


def test_livai_alias_with_untouched_legacy_env_still_works(
    clear_provider_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An existing LivAI .env must keep working with zero edits.

    The old client appended /v1 to LIVAI_BASE_URL. The alias preserves that so
    the deployment reaches the same endpoint it always did.
    """
    monkeypatch.setenv("INFERENCE_BACKEND", "livai")
    monkeypatch.setenv("LIVAI_API_KEY", "legacy-key")
    monkeypatch.setenv("LIVAI_MODEL", "gpt-5.5")
    monkeypatch.setenv("LIVAI_BASE_URL", "https://livai-api.llnl.gov/")

    settings = load_settings(load_dotenv_file=False)

    assert settings.inference_backend == "openai_compatible"
    assert settings.openai_compatible_enabled is True
    assert settings.openai_compatible_api_key == "legacy-key"
    assert settings.openai_compatible_model == "gpt-5.5"
    assert settings.openai_compatible_base_url == "https://livai-api.llnl.gov/v1"
    assert settings.openai_compatible_from_legacy_livai is True
    notice = settings.deprecation_notice()
    assert notice is not None and "OPENAI_COMPATIBLE_BASE_URL" in notice


def test_livai_alias_falls_back_to_historical_defaults(
    clear_provider_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("INFERENCE_BACKEND", "livai")
    monkeypatch.setenv("LIVAI_API_KEY", "legacy-key")

    settings = load_settings(load_dotenv_file=False)

    assert settings.openai_compatible_base_url == LEGACY_LIVAI_BASE_URL
    assert settings.openai_compatible_model == LEGACY_LIVAI_MODEL
    assert settings.openai_compatible_enabled is True


def test_legacy_url_already_ending_in_v1_is_not_doubled(
    clear_provider_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("INFERENCE_BACKEND", "livai")
    monkeypatch.setenv("LIVAI_API_KEY", "k")
    monkeypatch.setenv("LIVAI_BASE_URL", "https://livai-api.llnl.gov/v1/")

    assert load_settings(load_dotenv_file=False).openai_compatible_base_url == (
        "https://livai-api.llnl.gov/v1"
    )


def test_legacy_variables_are_ignored_unless_backend_is_livai(
    clear_provider_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Stale LIVAI_* lines in a copied .env must not leak into another provider.

    If they did, a Copilot token could be sent to the LLNL endpoint, and a
    plain deterministic start would log a spurious deprecation notice.
    """
    monkeypatch.setenv("LIVAI_API_KEY", "old-key")
    monkeypatch.setenv("LIVAI_MODEL", "gpt-5.5")
    monkeypatch.setenv("LIVAI_BASE_URL", "https://livai-api.llnl.gov/")

    monkeypatch.setenv("INFERENCE_BACKEND", "deterministic")
    deterministic = load_settings(load_dotenv_file=False)
    assert deterministic.openai_compatible_api_key is None
    assert deterministic.openai_compatible_base_url is None
    assert deterministic.openai_compatible_from_legacy_livai is False
    assert deterministic.deprecation_notice() is None

    monkeypatch.setenv("INFERENCE_BACKEND", "openai_compatible")
    monkeypatch.setenv("OPENAI_COMPATIBLE_API_KEY", "copilot-token")
    monkeypatch.setenv("OPENAI_COMPATIBLE_BASE_URL", TEST_URL)
    generic = load_settings(load_dotenv_file=False)
    assert generic.openai_compatible_api_key == "copilot-token"
    assert generic.openai_compatible_base_url == TEST_URL
    assert generic.openai_compatible_from_legacy_livai is False


def test_new_names_override_legacy_under_the_alias(
    clear_provider_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A half-migrated .env (alias backend, new variable names) still resolves."""
    monkeypatch.setenv("INFERENCE_BACKEND", "livai")
    monkeypatch.setenv("OPENAI_COMPATIBLE_API_KEY", "new-key")
    monkeypatch.setenv("OPENAI_COMPATIBLE_BASE_URL", TEST_URL)
    monkeypatch.setenv("LIVAI_API_KEY", "old-key")
    monkeypatch.setenv("LIVAI_BASE_URL", "https://livai-api.llnl.gov/")

    settings = load_settings(load_dotenv_file=False)

    assert settings.openai_compatible_api_key == "new-key"
    # Explicit new URL is verbatim; no /v1 is appended to it.
    assert settings.openai_compatible_base_url == TEST_URL
    assert settings.openai_compatible_from_legacy_livai is True


def test_misconfiguration_names_the_missing_variables(clear_provider_env: None) -> None:
    only_backend = Settings(assistant_generator="openai_compatible").provider_misconfiguration()
    only_key = Settings(
        assistant_generator="openai_compatible", openai_compatible_api_key="k"
    ).provider_misconfiguration()
    alias = Settings(assistant_generator="livai").provider_misconfiguration()
    complete = Settings(
        assistant_generator="openai_compatible",
        openai_compatible_api_key="k",
        openai_compatible_base_url=TEST_URL,
    ).provider_misconfiguration()

    assert only_backend is not None
    assert "OPENAI_COMPATIBLE_API_KEY" in only_backend
    assert "OPENAI_COMPATIBLE_BASE_URL" in only_backend
    assert only_key is not None and "OPENAI_COMPATIBLE_BASE_URL" in only_key
    assert alias is not None and "INFERENCE_BACKEND=livai" in alias
    assert complete is None


def test_alias_misconfiguration_names_the_legacy_variable(
    clear_provider_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An operator still on the alias is editing LIVAI_*, so say LIVAI_API_KEY."""
    monkeypatch.setenv("INFERENCE_BACKEND", "livai")

    warning = load_settings(load_dotenv_file=False).provider_misconfiguration()

    assert warning is not None
    assert "LIVAI_API_KEY" in warning
    assert "OPENAI_COMPATIBLE_BASE_URL" not in warning  # URL defaulted under the alias


def test_unknown_backend_is_reported(clear_provider_env: None) -> None:
    unknown = Settings(assistant_generator="anthropic").provider_misconfiguration()
    assert unknown is not None and "anthropic" in unknown


# --------------------------------------------------------------------------
# Prompt (shared with Argo via prompting.py)
# --------------------------------------------------------------------------


def test_prompt_contains_question_evidence_and_constraints() -> None:
    messages = build_messages("How do I choose a compset?", _evidence())

    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == SYSTEM_PROMPT
    assert messages[1]["role"] == "user"
    assert "How do I choose a compset?" in messages[1]["content"]
    assert "user-guide:compsets" in messages[1]["content"]
    assert "official test source" in messages[1]["content"]
    assert SYSTEM_PROMPT not in messages[1]["content"]


def test_prompt_context_is_deterministically_bounded() -> None:
    evidence = _evidence()
    evidence[0].text = "x" * (MAX_EVIDENCE_PROMPT_CHARS * 2)

    user_content = build_messages("question", evidence)[1]["content"]

    assert len(user_content) < MAX_EVIDENCE_PROMPT_CHARS + 200
    assert "truncated deterministically" in user_content


# --------------------------------------------------------------------------
# Request shape
# --------------------------------------------------------------------------


def test_request_uses_model_messages_and_temperature() -> None:
    client, fake = _client()

    client.complete(build_messages("question", _evidence()))

    assert fake.calls == 1
    assert fake.last_request is not None
    assert fake.last_request["model"] == "gpt-4o"
    assert fake.last_request["temperature"] == 0.0
    assert fake.last_request["messages"][0]["role"] == "system"


def test_temperature_can_be_omitted_for_models_that_reject_it() -> None:
    client, fake = _client(temperature=None)

    client.complete(build_messages("question", _evidence()))

    assert fake.last_request is not None
    assert "temperature" not in fake.last_request


def test_base_url_is_used_verbatim_without_appending_v1(monkeypatch: pytest.MonkeyPatch) -> None:
    """The old client forced /v1; Copilot 404s under it. The URL is now literal."""
    captured: dict[str, Any] = {}

    class _SpyOpenAI:
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=lambda **_: None))

    monkeypatch.setattr("e3sm_ai_platform.integrations.openai_compatible.OpenAI", _SpyOpenAI)

    OpenAICompatibleChatClient(
        api_key="k", model="gpt-4o", base_url="https://api.business.githubcopilot.com"
    )

    assert captured["base_url"] == "https://api.business.githubcopilot.com"
    assert captured["api_key"] == "k"


# --------------------------------------------------------------------------
# Response handling
# --------------------------------------------------------------------------


def test_accepts_off_spec_response_missing_object_field() -> None:
    """GitHub Copilot omits ``object`` and ``created``; the client must not care."""
    client, _ = _client(FakeCompletions(_sdk_response("READY", spec_compliant=False)))

    assert client.complete(build_messages("question", _evidence())) == "READY"


@pytest.mark.parametrize(
    ("response", "expected_code"),
    [
        (_sdk_response("   "), "empty_content"),
        (_sdk_response(None), "malformed_response"),
        (SimpleNamespace(choices=[]), "malformed_response"),
        (SimpleNamespace(error="rate limited"), "malformed_response"),
    ],
)
def test_bad_responses_are_sanitized(response: Any, expected_code: str) -> None:
    client, _ = _client(FakeCompletions(response))

    with pytest.raises(OpenAICompatibleProviderError) as excinfo:
        client.complete(build_messages("question", _evidence()))

    assert excinfo.value.code == expected_code


def test_sdk_exception_is_sanitized_to_request_error() -> None:
    client, _ = _client(FakeCompletions(raise_exc=RuntimeError("secret-key " + TEST_URL)))

    with pytest.raises(OpenAICompatibleProviderError) as excinfo:
        client.complete(build_messages("question", _evidence()))

    assert excinfo.value.code == "request_error"
    assert "secret-key" not in str(excinfo.value)


def test_rejects_non_https_base_url_before_sending() -> None:
    client, fake = _client(base_url="http://gateway.example.org/v1")

    with pytest.raises(OpenAICompatibleProviderError) as excinfo:
        client.complete(build_messages("question", _evidence()))

    assert excinfo.value.code == "invalid_https_base_url"
    assert fake.calls == 0


# --------------------------------------------------------------------------
# Generator
# --------------------------------------------------------------------------


def test_generator_preserves_server_citations_and_evidence() -> None:
    generator = OpenAICompatibleEvidenceGenerator(FakeChatClient())

    response = generator(
        question="How do I choose a compset?",
        route=RouteName.CURATED_RAG,
        evidence=_evidence(),
        include_evidence=True,
        reason="curated",
    )

    assert response.generation_mode is GenerationMode.LLM
    assert response.debug["provider"] == PROVIDER_NAME
    assert response.debug["provider_used"] is True
    assert "Provider answer." in response.answer
    assert [c.source_id for c in response.citations] == ["user-guide:compsets"]
    assert len(response.evidence) == 1


def test_generator_failure_falls_back_to_deterministic_cited_answer() -> None:
    generator = OpenAICompatibleEvidenceGenerator(FakeChatClient(fail=True))

    response = generator(
        question="How do I choose a compset?",
        route=RouteName.CURATED_RAG,
        evidence=_evidence(),
        include_evidence=True,
        reason="curated",
    )

    assert response.generation_mode is GenerationMode.DETERMINISTIC_FALLBACK
    assert response.debug["provider_fallback"] is True
    assert response.debug["provider_error_code"] == "request_error"
    assert [c.source_id for c in response.citations] == ["user-guide:compsets"]
    assert "I have not added claims beyond these cited sources." in response.answer


def test_generator_is_not_called_for_non_curated_routes() -> None:
    client = FakeChatClient()
    generator = OpenAICompatibleEvidenceGenerator(client)

    response = generator(
        question="When is the next workshop?",
        route=RouteName.WEB_SEARCH,
        evidence=[],
        include_evidence=True,
        reason="web",
    )

    assert client.messages is None
    assert response.generation_mode is GenerationMode.DETERMINISTIC
    assert "provider" not in response.debug


def test_fallback_debug_never_exposes_secret_or_endpoint() -> None:
    client, _ = _client(
        FakeCompletions(raise_exc=RuntimeError("secret-key gateway.example.org")),
    )
    response = OpenAICompatibleEvidenceGenerator(client)(
        question="How do I choose a compset?",
        route=RouteName.CURATED_RAG,
        evidence=_evidence(),
        include_evidence=True,
        reason="curated",
    )

    serialized = response.model_dump_json()
    assert "secret-key" not in serialized
    assert "gateway.example.org" not in serialized


# --------------------------------------------------------------------------
# Wiring
# --------------------------------------------------------------------------


def test_build_generator_returns_none_unless_fully_configured(clear_provider_env: None) -> None:
    assert build_generator(Settings()) is None
    assert build_generator(Settings(assistant_generator="openai_compatible")) is None
    assert (
        build_generator(
            Settings(assistant_generator="openai_compatible", openai_compatible_api_key="k")
        )
        is None
    )
    assert isinstance(
        build_generator(
            Settings(
                assistant_generator="openai_compatible",
                openai_compatible_api_key="k",
                openai_compatible_base_url=TEST_URL,
            )
        ),
        OpenAICompatibleEvidenceGenerator,
    )


def test_livai_alias_builds_the_generic_generator(clear_provider_env: None) -> None:
    generator = build_provider_generator(
        Settings(
            assistant_generator="livai",
            openai_compatible_api_key="k",
            openai_compatible_base_url=LEGACY_LIVAI_BASE_URL,
        )
    )
    assert isinstance(generator, OpenAICompatibleEvidenceGenerator)


def test_provider_selection_is_exclusive(clear_provider_env: None) -> None:
    from e3sm_ai_platform.integrations.argo import ArgoEvidenceGenerator

    assert build_provider_generator(Settings()) is None
    assert isinstance(
        build_provider_generator(Settings(assistant_generator="argo", argo_user="u")),
        ArgoEvidenceGenerator,
    )
    assert isinstance(
        build_provider_generator(
            Settings(
                assistant_generator="openai_compatible",
                openai_compatible_api_key="k",
                openai_compatible_base_url=TEST_URL,
            )
        ),
        OpenAICompatibleEvidenceGenerator,
    )


def test_bad_base_url_does_not_break_service_construction() -> None:
    """CompassService is built lazily; a construction error would 500 every request."""
    client, fake = _client(base_url="http://gateway.example.org/v1")
    service = CompassService(
        generator=OpenAICompatibleEvidenceGenerator(client),
        settings=load_settings(load_dotenv_file=False),
    )

    response = service.query(QueryRequest(question="How do I choose an E3SM compset?"))

    assert response.generation_mode is GenerationMode.DETERMINISTIC_FALLBACK
    assert response.debug["provider_error_code"] == "invalid_https_base_url"
    assert response.citations
    assert fake.calls == 0
    assert service.health()["status"] == "ok"


def test_service_uses_deterministic_default_without_provider(clear_provider_env: None) -> None:
    service = CompassService(settings=load_settings(load_dotenv_file=False))

    response = service.query(QueryRequest(question="How do I choose an E3SM compset?"))

    assert response.generation_mode is GenerationMode.DETERMINISTIC
    assert "provider_used" not in response.debug


def test_service_routes_through_provider_when_configured(clear_provider_env: None) -> None:
    client, fake = _client(FakeCompletions(_sdk_response("Compsets select the component set.")))
    service = CompassService(
        generator=OpenAICompatibleEvidenceGenerator(client),
        settings=load_settings(load_dotenv_file=False),
    )

    response = service.query(QueryRequest(question="How do I choose an E3SM compset?"))

    assert fake.calls == 1
    assert response.generation_mode is GenerationMode.LLM
    assert response.debug["provider_used"] is True
    assert response.citations


# --------------------------------------------------------------------------
# Temperature is reachable from configuration
# --------------------------------------------------------------------------


def test_temperature_defaults_to_zero_and_blank_keeps_it(
    clear_provider_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert load_settings(load_dotenv_file=False).openai_compatible_temperature == (
        DEFAULT_OPENAI_COMPATIBLE_TEMPERATURE
    )

    monkeypatch.setenv("OPENAI_COMPATIBLE_TEMPERATURE", "")
    assert load_settings(load_dotenv_file=False).openai_compatible_temperature == 0.0

    monkeypatch.setenv("OPENAI_COMPATIBLE_TEMPERATURE", "0.7")
    assert load_settings(load_dotenv_file=False).openai_compatible_temperature == 0.7


@pytest.mark.parametrize("sentinel", ["omit", "OMIT", " none ", "unset"])
def test_temperature_sentinel_disables_the_parameter(
    clear_provider_env: None, monkeypatch: pytest.MonkeyPatch, sentinel: str
) -> None:
    """Some reasoning models reject any value, so the field must be droppable."""
    monkeypatch.setenv("OPENAI_COMPATIBLE_TEMPERATURE", sentinel)

    assert load_settings(load_dotenv_file=False).openai_compatible_temperature is None


@pytest.mark.parametrize("configured", [0.0, None, 0.7])
def test_build_generator_forwards_configured_temperature(
    clear_provider_env: None, configured: float | None
) -> None:
    """Regression: build_generator dropped temperature, so omit was unreachable."""
    generator = build_generator(
        Settings(
            assistant_generator="openai_compatible",
            openai_compatible_api_key="k",
            openai_compatible_base_url=TEST_URL,
            openai_compatible_temperature=configured,
        )
    )

    assert generator is not None
    client = generator.client
    assert isinstance(client, OpenAICompatibleChatClient)
    assert client.temperature == configured


def test_configured_omit_reaches_the_request_body(clear_provider_env: None) -> None:
    """End to end: an operator setting omit must produce a request without it."""
    client, fake = _client(temperature=None)

    client.complete(build_messages("question", _evidence()))

    assert fake.last_request is not None
    assert "temperature" not in fake.last_request
