"""Representative-question coverage for a local corpus build.

:func:`measure_coverage` runs each question in ``corpus/questions.json`` against
a build written by :func:`~e3sm_ai_platform.knowledge.corpus_build.curate`,
using the application's chunking, retrieval, routing, and deterministic
generation with default settings. It reports which expected documents are
retrieved and cited. It measures whether mapped evidence is surfaced; it does
not judge answer quality or set pass/fail thresholds.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from e3sm_ai_platform.application.generation import generate_response
from e3sm_ai_platform.application.service import CompassService
from e3sm_ai_platform.domain.models import CorpusEntry, QueryRequest
from e3sm_ai_platform.infrastructure.settings import Settings
from e3sm_ai_platform.knowledge.corpus import chunk_corpus
from e3sm_ai_platform.knowledge.curation import SCHEMA_VERSION, CurationValidationError
from e3sm_ai_platform.knowledge.retrieval import InMemoryVectorStore, build_retriever

SEARCH_K = 8
ANSWER_TOP_K = 4


class CoverageQuestion(BaseModel):
    """A representative question and the documents that should support it."""

    model_config = ConfigDict(extra="forbid")

    id: str
    question: str
    expected_documents: list[str]


class QuestionSet(BaseModel):
    """Versioned representative questions for coverage checks."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = SCHEMA_VERSION
    questions: list[CoverageQuestion]


class QuestionCoverage(BaseModel):
    """Retrieved and cited documents for one question."""

    id: str
    route: str
    expected: list[str]
    retrieved: list[str]
    cited: list[str]
    expected_retrieved: list[str]
    expected_cited: list[str]


class CoverageReport(BaseModel):
    """Coverage results for every question against one corpus build."""

    schema_version: int = SCHEMA_VERSION
    snapshot_sha256: str
    search_k: int = SEARCH_K
    answer_top_k: int = ANSWER_TOP_K
    expected_total: int
    expected_retrieved_total: int
    questions_citing_expected: int
    questions: list[QuestionCoverage]


def load_questions(path: Path | str) -> QuestionSet:
    """Load a question set and reject duplicate or empty entries.

    Parameters
    ----------
    path : Path or str
        Question set JSON, such as ``corpus/questions.json``.

    Returns
    -------
    QuestionSet
        The validated question set.

    Raises
    ------
    CurationValidationError
        If the file is invalid or has duplicate IDs, blank questions, or
        questions without expected documents.
    """
    try:
        questions = QuestionSet.model_validate_json(Path(path).read_bytes())
    except (OSError, ValueError) as error:
        raise CurationValidationError(f"invalid question set: {error}") from error
    ids = [question.id for question in questions.questions]
    failures = ["duplicate question IDs"] if len(ids) != len(set(ids)) else []
    for question in questions.questions:
        if not question.question.strip():
            failures.append(f"blank question: {question.id}")
        if not question.expected_documents:
            failures.append(f"no expected documents: {question.id}")
    if failures:
        raise CurationValidationError("; ".join(failures))

    return questions


def measure_coverage(build_root: Path | str, questions_path: Path | str) -> CoverageReport:
    """Run every question against a corpus build and report document coverage.

    Parameters
    ----------
    build_root : Path or str
        Build directory written by ``curate``.
    questions_path : Path or str
        Question set JSON, such as ``corpus/questions.json``.

    Returns
    -------
    CoverageReport
        Per-question retrieved and cited documents and overall totals.

    Raises
    ------
    CurationValidationError
        If the question set is invalid or names documents absent from the build.
    """
    root = Path(build_root)
    questions = load_questions(questions_path)
    entries = _build_entries(root)
    known = {entry.source_id for entry in entries}
    missing = sorted(
        {doc for question in questions.questions for doc in question.expected_documents} - known
    )
    if missing:
        raise CurationValidationError(f"expected documents not in build: {', '.join(missing)}")

    settings = Settings()
    store = build_retriever(settings)
    store.add(chunk_corpus(entries))
    service = CompassService(retriever=store, generator=generate_response, settings=settings)
    results = [_measure(service, store, question) for question in questions.questions]
    report = CoverageReport(
        snapshot_sha256=_sha256_file(root / "captured" / "snapshot.json"),
        expected_total=sum(len(result.expected) for result in results),
        expected_retrieved_total=sum(len(result.expected_retrieved) for result in results),
        questions_citing_expected=sum(bool(result.expected_cited) for result in results),
        questions=results,
    )

    return report


def _build_entries(root: Path) -> list[CorpusEntry]:
    """Return one corpus entry per captured document in a build."""
    try:
        snapshot = json.loads((root / "captured" / "snapshot.json").read_text(encoding="utf-8"))
        acquisition = json.loads((root / "acquisition.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise CurationValidationError(f"invalid corpus build: {error}") from error
    documents = {document["id"]: document for document in acquisition["documents"]}

    return [
        CorpusEntry(
            source_id=record["id"],
            title=record["title"] or record["id"],
            url=record["url"],
            section=documents[record["id"]]["path"],
            component=documents[record["id"]]["source_id"],
            version=record["revision"],
            provenance="local corpus build; unreviewed",
            text=(root / "captured" / record["content_path"]).read_text(encoding="utf-8"),
        )
        for record in snapshot["records"]
    ]


def _measure(
    service: CompassService, store: InMemoryVectorStore, question: CoverageQuestion
) -> QuestionCoverage:
    """Answer one question and compare retrieved and cited documents with expectations."""
    response = service.query(QueryRequest(question=question.question, top_k=ANSWER_TOP_K))
    retrieved = list(
        dict.fromkeys(item.source.source_id for item in store.search(question.question, SEARCH_K))
    )
    cited = sorted({citation.source_id for citation in response.citations})
    expected = sorted(question.expected_documents)

    return QuestionCoverage(
        id=question.id,
        route=response.route.value,
        expected=expected,
        retrieved=retrieved,
        cited=cited,
        expected_retrieved=[doc for doc in expected if doc in retrieved],
        expected_cited=[doc for doc in expected if doc in cited],
    )


def _sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
