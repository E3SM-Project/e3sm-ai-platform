"""Backend settings loaded from environment and optional local .env."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_LIVAI_BASE_URL = "https://livai-api.llnl.gov/"
DEFAULT_LIVAI_MODEL = "gpt-5.5"
DEFAULT_ARGO_BASE_URL = "https://apps.inside.anl.gov/argoapi"
DEFAULT_ARGO_MODEL = "claudesonnet5"
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
RETRIEVAL_MODES = frozenset({"lexical", "semantic", "hybrid"})
ENV_FILE = Path(__file__).parents[3] / ".env"


@dataclass(frozen=True)
class Settings:
    """Runtime settings for provider selection and local prototype access."""

    assistant_generator: str = "deterministic"
    livai_api_key: str | None = None
    livai_model: str = DEFAULT_LIVAI_MODEL
    livai_base_url: str = DEFAULT_LIVAI_BASE_URL
    argo_user: str | None = None
    argo_model: str = DEFAULT_ARGO_MODEL
    argo_base_url: str = DEFAULT_ARGO_BASE_URL
    argo_temperature: float | None = None
    ollama_model: str = "compass-gemma3:4b"
    ollama_base_url: str = "http://localhost:11434/v1/"
    ollama_timeout_seconds: float = 120.0
    ollama_context_tokens: int = 4096
    ollama_max_output_tokens: int = 512
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
        """Validate retrieval and local inference configuration."""
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
        if not self.ollama_model.strip():
            raise ValueError("ollama_model must not be empty")
        if (
            not math.isfinite(self.ollama_timeout_seconds)
            or not 0 < self.ollama_timeout_seconds <= 300
        ):
            raise ValueError("ollama_timeout_seconds must be finite and between 0 and 300")
        if not 1024 <= self.ollama_context_tokens <= 32768:
            raise ValueError("ollama_context_tokens must be between 1024 and 32768")
        if not 0 < self.ollama_max_output_tokens < self.ollama_context_tokens - 512:
            raise ValueError("ollama_max_output_tokens must leave room for prompt and template")

    @property
    def livai_enabled(self) -> bool:
        """LivAI is explicitly enabled only when requested and a key is present."""
        return self.assistant_generator.lower() == "livai" and bool(self.livai_api_key)

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
        backend = self.assistant_generator.lower()
        if backend == "livai" and not self.livai_enabled:
            return "INFERENCE_BACKEND=livai but LIVAI_API_KEY is not set; using deterministic."
        if backend == "argo" and not self.argo_enabled:
            return "INFERENCE_BACKEND=argo but ARGO_USER is not set; using deterministic."
        if backend not in {"deterministic", "livai", "argo", "ollama"}:
            return (
                f"INFERENCE_BACKEND={self.assistant_generator!r} is not a known provider; "
                "using deterministic."
            )
        return None


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
    return Settings(
        assistant_generator=os.getenv("INFERENCE_BACKEND", "deterministic"),
        livai_api_key=os.getenv("LIVAI_API_KEY") or None,
        livai_model=os.getenv("LIVAI_MODEL", DEFAULT_LIVAI_MODEL),
        livai_base_url=os.getenv("LIVAI_BASE_URL", DEFAULT_LIVAI_BASE_URL),
        argo_user=os.getenv("ARGO_USER") or os.getenv("ARGO_API_KEY") or None,
        argo_model=os.getenv("ARGO_MODEL", DEFAULT_ARGO_MODEL),
        argo_base_url=os.getenv("ARGO_BASE_URL", DEFAULT_ARGO_BASE_URL),
        argo_temperature=_optional_float(os.getenv("ARGO_TEMPERATURE")),
        ollama_model=os.getenv("OLLAMA_MODEL", "compass-gemma3:4b"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1/"),
        ollama_timeout_seconds=float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120")),
        ollama_context_tokens=int(os.getenv("OLLAMA_CONTEXT_TOKENS", "4096")),
        ollama_max_output_tokens=int(os.getenv("OLLAMA_MAX_OUTPUT_TOKENS", "512")),
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
