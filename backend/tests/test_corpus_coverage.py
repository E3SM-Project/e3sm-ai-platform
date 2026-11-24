"""Tests for representative-question coverage of local corpus builds."""

import json
from fnmatch import fnmatchcase
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


def test_optional_documents_are_accepted_citations_without_counting_toward_recall(tmp_path):
    """Optional citations are accepted but cannot satisfy required coverage."""
    root = _build(tmp_path)
    questions = _questions(
        tmp_path,
        [
            {
                "id": "q",
                "question": "When should I run case.submit?",
                "expected_documents": ["setup"],
                "optional_documents": ["submit"],
            }
        ],
    )

    report = measure_coverage(root, questions)
    result = report.questions[0]

    assert result.optional == ["submit"]
    assert "submit" in result.accepted_cited
    assert "submit" not in result.expected_retrieved
    assert "submit" not in result.expected_cited
    assert report.expected_total == 1


def test_measure_coverage_rejects_unknown_documents_and_bad_question_sets(tmp_path):
    """Question sets must name build documents and have unique, non-empty entries."""
    root = _build(tmp_path)
    unknown = _questions(
        tmp_path, [{"id": "q", "question": "Submit?", "expected_documents": ["missing"]}]
    )
    with pytest.raises(CurationValidationError, match="not in build: missing"):
        measure_coverage(root, unknown)

    entry = {"id": "q", "question": "Submit?", "expected_documents": ["submit"]}
    with pytest.raises(CurationValidationError, match="not in build: missing"):
        measure_coverage(root, _questions(tmp_path, [{**entry, "optional_documents": ["missing"]}]))
    with pytest.raises(CurationValidationError, match="expected and optional documents overlap"):
        load_questions(_questions(tmp_path, [{**entry, "optional_documents": ["submit"]}]))
    with pytest.raises(CurationValidationError, match="duplicate question IDs"):
        load_questions(_questions(tmp_path, [entry, entry]))
    with pytest.raises(CurationValidationError, match="no expected documents: q"):
        load_questions(_questions(tmp_path, [{**entry, "expected_documents": []}]))


def test_load_questions_requires_empty_documents_only_for_should_refuse(tmp_path):
    """Only should-refuse questions may, and must, omit expected documents."""
    refuse = {"id": "r", "question": "What is E3SMv3's climate sensitivity?"}

    loaded = load_questions(
        _questions(tmp_path, [{**refuse, "expected_documents": [], "should_refuse": True}])
    )

    assert loaded.questions[0].should_refuse
    with pytest.raises(CurationValidationError, match="should-refuse question has expected"):
        load_questions(
            _questions(
                tmp_path, [{**refuse, "expected_documents": ["setup"], "should_refuse": True}]
            )
        )
    with pytest.raises(CurationValidationError, match="should-refuse question has optional"):
        load_questions(
            _questions(
                tmp_path,
                [
                    {
                        **refuse,
                        "expected_documents": [],
                        "optional_documents": ["setup"],
                        "should_refuse": True,
                    }
                ],
            )
        )
    with pytest.raises(CurationValidationError, match="invalid question set"):
        load_questions(_questions(tmp_path, [{**refuse, "expected_documents": [], "tag": "x"}]))


def test_measure_coverage_skips_should_refuse_questions(tmp_path):
    """Should-refuse questions add nothing to the coverage report or its totals."""
    root = _build(tmp_path)
    answerable = {"id": "submit", "question": "How do I submit?", "expected_documents": ["submit"]}
    refuse = {
        "id": "refuse",
        "question": "What is E3SMv3's climate sensitivity?",
        "expected_documents": [],
        "should_refuse": True,
    }

    report = measure_coverage(root, _questions(tmp_path, [answerable, refuse]))

    assert [result.id for result in report.questions] == ["submit"]
    assert report.expected_total == 1


def test_checked_in_questions_use_every_explicit_document():
    """Both question types are present and every explicit content source is mapped."""
    questions = load_questions(REPOSITORY / "corpus" / "questions.json").questions
    scope = json.loads((REPOSITORY / "corpus" / "sources.json").read_text())
    explicit = {
        document["id"]
        for source in scope["sources"]
        for document in source["documents"]
        if document.get("role", "content") == "content"
    }
    mapped = {
        doc
        for question in questions
        for doc in (*question.expected_documents, *question.optional_documents)
    }

    assert any(question.should_refuse for question in questions)
    assert any(not question.should_refuse for question in questions)
    assert explicit <= mapped, sorted(explicit - mapped)


def test_checked_in_questions_reference_selected_content_documents():
    """Required and optional sources are explicit or pattern-selected content."""
    questions = load_questions(REPOSITORY / "corpus" / "questions.json")
    scope = json.loads((REPOSITORY / "corpus" / "sources.json").read_text())
    explicit = {
        document["id"]
        for source in scope["sources"]
        for document in source["documents"]
        if document.get("role", "content") == "content"
    }

    def pattern_selected(doc_id):
        return any(
            any(fnmatchcase(doc_id, _id_glob(source["id"], p)) for p in source.get("include", []))
            and not any(
                fnmatchcase(doc_id, _id_glob(source["id"], p)) for p in source.get("exclude", [])
            )
            for source in scope["sources"]
        )

    for question in questions.questions:
        for doc_id in (*question.expected_documents, *question.optional_documents):
            assert doc_id in explicit or pattern_selected(doc_id), (question.id, doc_id)


def _id_glob(source_id, pattern):
    """Translate a path pattern into a glob over pattern-derived document IDs."""
    return f"{source_id}." + pattern.replace("**/", "*").replace("/", ".")
