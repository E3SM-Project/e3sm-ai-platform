"""Tests for selecting the runtime corpus with CORPUS_PATH."""

import json

from e3sm_ai_platform import evaluation
from e3sm_ai_platform.application.service import CompassService
from e3sm_ai_platform.infrastructure.settings import Settings, load_settings

ENTRY = {
    "source_id": "local-guide",
    "title": "Local guide",
    "url": "https://example.test/guide",
    "section": "guide.md",
    "component": "docs",
    "version": "1.0",
    "provenance": "test corpus",
    "text": "Run case.submit to submit the job to the batch queue.",
}


def test_corpus_path_setting_selects_runtime_corpus(tmp_path, monkeypatch):
    """CORPUS_PATH loads a JSON-array corpus; unset keeps the packaged corpus."""
    corpus = tmp_path / "corpus.json"
    corpus.write_text(json.dumps([ENTRY]), encoding="utf-8")
    monkeypatch.setenv("CORPUS_PATH", str(corpus))

    settings = load_settings(load_dotenv_file=False)

    assert settings.corpus_path == str(corpus)
    assert [entry.source_id for entry in CompassService(settings=settings).entries] == [
        "local-guide"
    ]
    assert len(CompassService(settings=Settings()).entries) > 1


def test_corpus_snapshot_id_identifies_loaded_content(tmp_path):
    """The snapshot ID identifies loaded content, not file formatting."""
    compact, indented, changed = (tmp_path / name for name in ("a.json", "b.json", "c.json"))
    compact.write_text(json.dumps([ENTRY]), encoding="utf-8")
    indented.write_text(json.dumps([ENTRY], indent=4), encoding="utf-8")
    changed.write_text(json.dumps([{**ENTRY, "text": "Changed."}]), encoding="utf-8")

    def snapshot(path):
        return CompassService(settings=Settings(corpus_path=str(path))).corpus_snapshot_id

    assert snapshot(compact).startswith("sha256:")
    assert snapshot(compact) == snapshot(indented)
    assert snapshot(compact) != snapshot(changed)
    assert CompassService(settings=Settings()).corpus_snapshot_id != snapshot(compact)


def test_evaluator_ignores_corpus_path(tmp_path, monkeypatch):
    """The evaluation adapter keeps the packaged corpus its fixtures cite."""
    corpus = tmp_path / "corpus.json"
    corpus.write_text(json.dumps([ENTRY]), encoding="utf-8")
    monkeypatch.setenv("CORPUS_PATH", str(corpus))
    evaluation._service.cache_clear()
    try:
        source_ids = {entry.source_id for entry in evaluation._service().entries}
    finally:
        evaluation._service.cache_clear()

    assert "local-guide" not in source_ids
    assert "user-guide:compsets" in source_ids
