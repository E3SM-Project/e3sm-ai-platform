"""Synchronous E3SM Compass evaluator adapter."""

from __future__ import annotations

from dataclasses import replace
from functools import lru_cache
from typing import Any

from e3sm_ai_platform.application.generation import generate_response
from e3sm_ai_platform.application.service import CompassService
from e3sm_ai_platform.domain.models import QueryRequest
from e3sm_ai_platform.infrastructure.settings import load_settings


@lru_cache(maxsize=1)
def _service() -> CompassService:
    """Return the evaluator's cached application service without HTTP wiring.

    Generation is pinned to the deterministic generator regardless of
    ``INFERENCE_BACKEND``. The suite asserts routing, evidence, and citation
    behavior, none of which depend on provider wording, and a developer with
    any LLM provider configured in ``backend/.env`` would otherwise turn every
    run into live, non-reproducible, billable model calls. The packaged corpus
    is pinned the same way: the evaluation fixtures cite its source IDs, so a
    local ``CORPUS_PATH`` must not change the evaluated corpus.
    """
    settings = replace(load_settings(), corpus_path=None)
    return CompassService(generator=generate_response, settings=settings)


def evaluate(question: str) -> dict[str, Any]:
    """Return the stable E3SM Compass evaluator mapping contract."""
    response = _service().query(QueryRequest(question=question, top_k=6, include_evidence=True))
    evidence = [item.model_dump(mode="json") for item in response.retrieved_evidence]

    return {
        "answer": response.answer,
        "route": response.route.value,
        "retrieved_evidence": evidence,
        "citations": [item.model_dump(mode="json") for item in response.citations],
        "insufficient_evidence": response.insufficient_evidence,
    }
