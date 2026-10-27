"""Backend settings loaded from environment and optional local .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# The generic provider has no default URL: an operator must say which gateway
# they mean.
DEFAULT_OPENAI_COMPATIBLE_MODEL = "gpt-4o"
# Determinism is the default, but OPENAI_COMPATIBLE_TEMPERATURE=omit drops the
# parameter for models that refuse it outright.
DEFAULT_OPENAI_COMPATIBLE_TEMPERATURE = 0.0
OMIT_TEMPERATURE_VALUES = frozenset({"omit", "none", "unset"})
DEFAULT_ARGO_BASE_URL = "https://apps.inside.anl.gov/argoapi"
DEFAULT_ARGO_MODEL = "claudesonnet5"
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
RETRIEVAL_MODES = frozenset({"lexical", "semantic", "hybrid"})
ENV_FILE = Path(__file__).parents[3] / ".env"


@dataclass(frozen=True)
class Settings:
    """Runtime settings for provider selection and local prototype access."""

    assistant_generator: str = "deterministic"
    openai_compatible_api_key: str | None = None
    openai_compatible_model: str = DEFAULT_OPENAI_COMPATIBLE_MODEL
    openai_compatible_base_url: str | None = None
    # None omits the parameter entirely. Reasoning models reject any value,
    # so sending the default 0.0 would make every call fall back.
    openai_compatible_temperature: float | None = DEFAULT_OPENAI_COMPATIBLE_TEMPERATURE
    argo_user: str | None = None
    argo_model: str = DEFAULT_ARGO_MODEL
    argo_base_url: str = DEFAULT_ARGO_BASE_URL
    argo_temperature: float | None = None
    cors_allow_origins: tuple[str, ...] = ("http://localhost:5173",)
    service_name: str = "e3sm-ai-platform-backend"
    deployment_environment: str = "development"
    otlp_endpoint: str | None = None
    otlp_headers: tuple[tuple[str, str], ...] = ()
    retrieval_mode: str = "lexical"
    embedding_model: str = DEFAULT_EMBEDDING_MODEL
    retrieval_lexical_min_coverage: float = 0.18
    retrieval_lexical_min_score: float = 0.11
    retrieval_semantic_min_score: float = 0.7
    retrieval_lexical_weight: float = 0.5
    retrieval_semantic_weight: float = 0.5

    def __post_init__(self) -> None:
        """Validate retrieval configuration independently of environment loading."""
        if self.retrieval_mode not in RETRIEVAL_MODES:
            modes = ", ".join(sorted(RETRIEVAL_MODES))
            raise ValueError(f"retrieval_mode must be one of: {modes}")
        if not self.embedding_model.strip():
            raise ValueError("embedding_model must not be empty")
        if not 0.0 <= self.retrieval_lexical_min_coverage <= 1.0:
            raise ValueError("retrieval_lexical_min_coverage must be between 0 and 1")
        if self.retrieval_lexical_min_score < 0.0:
            raise ValueError("retrieval_lexical_min_score must be non-negative")
        if not -1.0 <= self.retrieval_semantic_min_score <= 1.0:
            raise ValueError("retrieval_semantic_min_score must be between -1 and 1")
        if self.retrieval_lexical_weight < 0.0 or self.retrieval_semantic_weight < 0.0:
            raise ValueError("retrieval weights must be non-negative")
        if self.retrieval_lexical_weight + self.retrieval_semantic_weight == 0.0:
            raise ValueError("at least one retrieval weight must be positive")

    @property
    def inference_backend(self) -> str:
        """Return the normalized backend name."""
        return self.assistant_generator.lower()

    @property
    def openai_compatible_enabled(self) -> bool:
        """The generic provider needs the backend selected plus a key and a base URL.

        There is no default URL on purpose: ``openai_compatible`` could mean
        LivAI, GitHub Copilot, Azure, or a local vLLM, and guessing would send
        a credential to the wrong host.
        """
        return (
            self.inference_backend == "openai_compatible"
            and bool(self.openai_compatible_api_key)
            and bool(self.openai_compatible_base_url)
        )

    @property
    def argo_enabled(self) -> bool:
        """Argo is explicitly enabled only when requested and a user is present.

        Argo authenticates with an ANL username rather than a secret, so the
        presence check is on ``argo_user``. The username is not a credential
        and access still depends on reaching the ANL network.
        """
        return self.assistant_generator.lower() == "argo" and bool(self.argo_user)

    def provider_misconfiguration(self) -> str | None:
        """Explain why a requested provider is inactive, or None when configuration is coherent.

        ``INFERENCE_BACKEND`` naming a provider whose required setting is blank
        silently falls back to deterministic generation. That is the safe
        behavior, but it is also the most common setup mistake, so startup
        surfaces it instead of leaving the operator to notice slow-looking
        deterministic answers.
        """
        backend = self.inference_backend
        if backend == "openai_compatible" and not self.openai_compatible_enabled:
            missing = []
            if not self.openai_compatible_api_key:
                missing.append("OPENAI_COMPATIBLE_API_KEY")
            if not self.openai_compatible_base_url:
                missing.append("OPENAI_COMPATIBLE_BASE_URL")
            return (
                f"INFERENCE_BACKEND={self.assistant_generator} but {' and '.join(missing)} "
                "not set; using deterministic."
            )
        if backend == "argo" and not self.argo_enabled:
            return "INFERENCE_BACKEND=argo but ARGO_USER is not set; using deterministic."
        if backend not in {"deterministic", "openai_compatible", "argo"}:
            return (
                f"INFERENCE_BACKEND={self.assistant_generator!r} is not a known provider; "
                "using deterministic."
            )
        return None


def _resolve_temperature(raw: str | None) -> float | None:
    """Parse ``OPENAI_COMPATIBLE_TEMPERATURE``.

    Unset or blank keeps the deterministic default. ``omit`` (or ``none`` /
    ``unset``) drops the field from the request entirely, which is the only
    thing that works for models that reject any temperature value rather than
    just disliking a particular one.
    """
    if raw is None or not raw.strip():
        return DEFAULT_OPENAI_COMPATIBLE_TEMPERATURE
    if raw.strip().lower() in OMIT_TEMPERATURE_VALUES:
        return None
    return float(raw)


def _optional_float(raw: str | None) -> float | None:
    """Parse an optional float env value, treating unset or blank as None."""
    if raw is None or not raw.strip():
        return None
    return float(raw)


def load_settings(load_dotenv_file: bool = True) -> Settings:
    """Load settings from environment, optionally reading backend/.env if present."""
    if load_dotenv_file:
        load_dotenv(ENV_FILE, override=False)

    raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173")
    origins = tuple(origin.strip() for origin in raw_origins.split(",") if origin.strip())
    raw_headers = os.getenv("OTLP_HEADERS", "")
    headers = tuple(
        (name.strip(), value.strip())
        for item in raw_headers.split(",")
        if "=" in item
        for name, value in [item.split("=", maxsplit=1)]
        if name.strip() and value.strip()
    )
    backend = os.getenv("INFERENCE_BACKEND", "deterministic")

    return Settings(
        assistant_generator=backend,
        openai_compatible_api_key=os.getenv("OPENAI_COMPATIBLE_API_KEY") or None,
        openai_compatible_model=(
            os.getenv("OPENAI_COMPATIBLE_MODEL") or DEFAULT_OPENAI_COMPATIBLE_MODEL
        ),
        openai_compatible_base_url=os.getenv("OPENAI_COMPATIBLE_BASE_URL") or None,
        openai_compatible_temperature=_resolve_temperature(
            os.getenv("OPENAI_COMPATIBLE_TEMPERATURE")
        ),
        argo_user=os.getenv("ARGO_USER") or os.getenv("ARGO_API_KEY") or None,
        argo_model=os.getenv("ARGO_MODEL", DEFAULT_ARGO_MODEL),
        argo_base_url=os.getenv("ARGO_BASE_URL", DEFAULT_ARGO_BASE_URL),
        argo_temperature=_optional_float(os.getenv("ARGO_TEMPERATURE")),
        cors_allow_origins=origins or ("http://localhost:5173",),
        service_name=os.getenv("SERVICE_NAME", "e3sm-ai-platform-backend"),
        deployment_environment=os.getenv("DEPLOYMENT_ENVIRONMENT", "development"),
        otlp_endpoint=os.getenv("OTLP_ENDPOINT") or None,
        otlp_headers=headers,
        retrieval_mode=os.getenv("RETRIEVAL_MODE", "lexical").lower(),
        embedding_model=os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
        retrieval_lexical_min_coverage=float(os.getenv("RETRIEVAL_LEXICAL_MIN_COVERAGE", "0.18")),
        retrieval_lexical_min_score=float(os.getenv("RETRIEVAL_LEXICAL_MIN_SCORE", "0.11")),
        retrieval_semantic_min_score=float(os.getenv("RETRIEVAL_SEMANTIC_MIN_SCORE", "0.7")),
        retrieval_lexical_weight=float(os.getenv("RETRIEVAL_LEXICAL_WEIGHT", "0.5")),
        retrieval_semantic_weight=float(os.getenv("RETRIEVAL_SEMANTIC_WEIGHT", "0.5")),
    )
