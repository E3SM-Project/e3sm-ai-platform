"""Tests for representative-question coverage of local corpus builds."""

import json
from pathlib import Path

import pytest

from e3sm_ai_platform.application.corpus_coverage import load_questions, measure_coverage
from e3sm_ai_platform.knowledge.corpus_build import curate
from e3sm_ai_platform.knowledge.curation import CurationValidationError

REPOSITORY = Path(__file__).parents[2]
REVISION = "0123456789abcdef0123456789abcdef01234567"
RAW = f"https://raw.githubusercontent.com/example/docs/{REVISION}"
FILES = {
    f"{RAW}/setup.md": b"# Setup\n\nRun case.setup after xmlchange to configure the case.\n",
    f"{RAW}/submit.md": b"# Submit\n\nRun case.submit to submit the job to the batch queue.\n",
}


def _build(tmp_path):
    """Curate a two-document build with an in-memory fetcher."""
    source = {
        "id": "docs",
        "identity": "Example docs",
        "owner": "Example owner",
        "repository_url": "https://github.com/example/docs",
        "revision": REVISION,
        "release": "1.0",
        "redistribution": "BSD-3-Clause",
        "license_url": "https://example.test/license",
        "documents": [{"id": "setup", "path": "setup.md"}, {"id": "submit", "path": "submit.md"}],
    }
    scope = tmp_path / "sources.json"
    scope.write_text(
        json.dumps({"manifest_version": 2, "request_interval_seconds": 1, "sources": [source]}),
        encoding="utf-8",
    )
    root = tmp_path / "build"
    curate(scope, root, fetch=FILES.__getitem__, sleep=lambda _: None)
    return root


def _questions(tmp_path, questions):
    """Write a question set file."""
    path = tmp_path / "questions.json"
    path.write_text(json.dumps({"schema_version": 1, "questions": questions}), encoding="utf-8")
    return path


def test_measure_coverage_reports_retrieved_and_cited_documents(tmp_path):
    """Coverage compares retrieval and citations with each question's expectations."""
    root = _build(tmp_path)
    questions = _questions(
        tmp_path,
        [
            {
                "id": "submit",
                "question": "How do I submit the case job?",
                "expected_documents": ["submit"],
            }
        ],
    )

    report = measure_coverage(root, questions)

    result = report.questions[0]
    assert result.expected_retrieved == ["submit"]
    assert result.retrieved[0] == "submit"
    assert set(result.expected_cited) <= {"submit"}
    assert report.expected_total == 1
    assert report.expected_retrieved_total == 1
    assert measure_coverage(root, questions) == report


def test_measure_coverage_rejects_unknown_documents_and_bad_question_sets(tmp_path):
    """Question sets must name build documents and have unique, non-empty entries."""
    root = _build(tmp_path)
    unknown = _questions(
        tmp_path, [{"id": "q", "question": "Submit?", "expected_documents": ["missing"]}]
    )
    with pytest.raises(CurationValidationError, match="not in build: missing"):
        measure_coverage(root, unknown)

    entry = {"id": "q", "question": "Submit?", "expected_documents": ["submit"]}
    with pytest.raises(CurationValidationError, match="duplicate question IDs"):
        load_questions(_questions(tmp_path, [entry, entry]))
    with pytest.raises(CurationValidationError, match="no expected documents: q"):
        load_questions(_questions(tmp_path, [{**entry, "expected_documents": []}]))


def test_checked_in_questions_reference_selected_content_documents():
    """Every expected document is a selected, captured (non-license) scope document."""
    questions = load_questions(REPOSITORY / "corpus" / "questions.json")
    scope = json.loads((REPOSITORY / "corpus" / "sources.json").read_text())
    selected = {
        document["id"]
        for source in scope["sources"]
        for document in source["documents"]
        if document.get("role", "content") == "content"
    }

    assert len(questions.questions) == 18
    for question in questions.questions:
        assert set(question.expected_documents) <= selected, question.id
