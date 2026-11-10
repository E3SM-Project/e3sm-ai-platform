"""Tests for reproducible corpus builds; downloads use an in-memory fetcher."""

import hashlib
import json
import tarfile

import httpx
import pytest

from e3sm_ai_platform.knowledge.corpus import load_corpus
from e3sm_ai_platform.knowledge.corpus_build import (
    _fetch,
    curate,
    export_runtime_corpus,
    package,
    verify_build,
)
from e3sm_ai_platform.knowledge.curation import CurationValidationError, validate_corpus

REVISION = "0123456789abcdef0123456789abcdef01234567"
RAW = f"https://raw.githubusercontent.com/example/docs/{REVISION}"
FILES = {
    f"{RAW}/README.md": b"# Guide\n\nRun `./case.setup`.  \r\n",
    f"{RAW}/docs/run.rst": b"Run\n===\n\n.. code-block:: bash\n\n    ./case.submit\n\nUse ``````.\n",
    f"{RAW}/LICENSE": b"BSD-3-Clause\n",
}


def _scope(tmp_path, *, repository="https://github.com/example/docs"):
    """Write a one-source scope selecting Markdown, RST, and a license companion."""
    scope = {
        "manifest_version": 2,
        "request_interval_seconds": 2,
        "sources": [
            {
                "id": "docs",
                "identity": "Example docs",
                "owner": "Example owner",
                "repository_url": repository,
                "revision": REVISION,
                "release": "1.0",
                "redistribution": "BSD-3-Clause",
                "documents": [
                    {"id": "guide", "path": "README.md"},
                    {"id": "run", "path": "docs/run.rst", "notes": "Test caveat."},
                    {"id": "license", "path": "LICENSE", "role": "license"},
                ],
            }
        ],
    }
    path = tmp_path / "sources.json"
    path.write_text(json.dumps(scope), encoding="utf-8")
    return path


def _approve(root):
    """Mark a build's hash-bound review as approved."""
    review_path = root / "captured" / "review.json"
    review = json.loads(review_path.read_text())
    review["approved"] = True
    review_path.write_text(json.dumps(review), encoding="utf-8")


def test_curate_keeps_raw_bytes_and_captures_verbatim_text(tmp_path):
    """Curate retains raw files, fences non-Markdown text, and skips license capture."""
    pauses = []
    root = tmp_path / "build"
    snapshot = curate(_scope(tmp_path), root, fetch=FILES.__getitem__, sleep=pauses.append)

    assert [record.id for record in snapshot.records] == ["guide", "run"]
    assert pauses == [2, 2]
    record = json.loads((root / "acquisition.json").read_text())
    by_id = {document["id"]: document for document in record["documents"]}
    assert by_id["license"]["captured"] is False
    assert by_id["run"]["notes"] == "Test caveat."
    assert by_id["run"]["url"] == f"https://github.com/example/docs/blob/{REVISION}/docs/run.rst"
    assert (
        by_id["guide"]["license_url"] == f"https://github.com/example/docs/blob/{REVISION}/LICENSE"
    )
    raw = (root / by_id["guide"]["raw_path"]).read_bytes()
    assert raw == FILES[f"{RAW}/README.md"]
    assert by_id["guide"]["sha256"] == hashlib.sha256(raw).hexdigest()
    run = (root / "captured/content/run.md").read_text()
    assert "```````rst\nRun\n===\n\n.. code-block:: bash\n\n    ./case.submit\n" in run
    assert f"<https://github.com/example/docs/blob/{REVISION}/docs/run.rst>" in run
    assert (root / "captured/content/guide.md").read_text().endswith("Run `./case.setup`.\n")
    assert verify_build(root) == []
    assert validate_corpus(root / "captured", require_approved=True) == ["review is not approved"]


def test_curate_is_reproducible_and_atomic(tmp_path):
    """Rebuilds match; existing builds need overwrite; failures leave no output."""
    scope = _scope(tmp_path)
    first, second = tmp_path / "first", tmp_path / "second"
    curate(scope, first, fetch=FILES.__getitem__, sleep=lambda _: None)
    curate(scope, second, fetch=FILES.__getitem__, sleep=lambda _: None)
    assert (first / "captured/snapshot.json").read_bytes() == (
        second / "captured/snapshot.json"
    ).read_bytes()

    with pytest.raises(CurationValidationError, match="already exists"):
        curate(scope, first, fetch=FILES.__getitem__, sleep=lambda _: None)
    curate(scope, first, overwrite=True, fetch=FILES.__getitem__, sleep=lambda _: None)

    def failing(url):
        raise CurationValidationError(f"failed to fetch {url}")

    with pytest.raises(CurationValidationError, match="failed to fetch"):
        curate(scope, tmp_path / "failed", fetch=failing, sleep=lambda _: None)
    assert not (tmp_path / "failed").exists()
    assert not (tmp_path / "failed.partial").exists()

    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    (unrelated / "keep.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(CurationValidationError, match="not a corpus build"):
        curate(scope, unrelated, overwrite=True, fetch=FILES.__getitem__, sleep=lambda _: None)
    assert (unrelated / "keep.txt").is_file()


def test_curate_rejects_invalid_or_unsupported_scopes(tmp_path):
    """Invalid scopes and non-GitHub repositories fail before any download."""
    with pytest.raises(CurationValidationError, match="unsupported repository URL"):
        curate(_scope(tmp_path, repository="https://gitlab.example/docs"), tmp_path / "out")
    scope_path = _scope(tmp_path)
    scope = json.loads(scope_path.read_text())
    scope["sources"][0]["revision"] = "main"
    scope_path.write_text(json.dumps(scope), encoding="utf-8")
    with pytest.raises(CurationValidationError, match="unpinned revision for docs"):
        curate(scope_path, tmp_path / "out")


def test_verify_build_detects_raw_and_captured_tampering(tmp_path):
    """Verification binds captured content to the raw bytes it came from."""
    root = tmp_path / "build"
    curate(_scope(tmp_path), root, fetch=FILES.__getitem__, sleep=lambda _: None)
    raw = root / "raw/docs" / REVISION / "docs/run.rst"
    raw.write_bytes(raw.read_bytes() + b"changed\n")
    assert verify_build(root) == ["raw hash mismatch for run"]


def test_package_requires_approval_and_is_deterministic(tmp_path):
    """Packaging refuses unapproved builds and archives licenses with captured content."""
    root = tmp_path / "build"
    curate(_scope(tmp_path), root, fetch=FILES.__getitem__, sleep=lambda _: None)
    with pytest.raises(CurationValidationError, match="review is not approved"):
        package(root, tmp_path / "release", "1.0.0")
    with pytest.raises(CurationValidationError, match="unsafe package version"):
        package(root, tmp_path / "release", "../1")

    _approve(root)
    archive = package(root, tmp_path / "release", "1.0.0")
    first = archive.read_bytes()
    assert package(root, tmp_path / "release", "1.0.0").read_bytes() == first
    checksum = archive.with_name("e3sm-corpus-1.0.0.tar.gz.sha256").read_text()
    assert checksum == f"{hashlib.sha256(first).hexdigest()}  e3sm-corpus-1.0.0.tar.gz\n"
    with tarfile.open(archive) as contents:
        names = contents.getnames()
    assert f"e3sm-corpus-1.0.0/raw/docs/{REVISION}/LICENSE" in names
    assert "e3sm-corpus-1.0.0/captured/content/run.md" in names
    assert "e3sm-corpus-1.0.0/acquisition.json" in names
    assert not any("/prepared/" in name for name in names)


def test_fetch_retries_transient_failures_only():
    """Timeouts and server errors are retried; client errors fail immediately."""
    request = httpx.Request("GET", "https://example.test/file")
    calls, pauses = [], []

    def flaky(url, timeout):
        calls.append(url)
        if len(calls) < 3:
            raise httpx.ConnectTimeout("timed out", request=request)
        return httpx.Response(200, content=b"ok", request=request)

    assert _fetch("https://example.test/file", get=flaky, sleep=pauses.append) == b"ok"
    assert pauses == [2.0, 4.0]

    def status(code):
        def get(url, timeout):
            calls.append(url)
            return httpx.Response(code, request=request)

        return get

    calls.clear()
    with pytest.raises(CurationValidationError, match="404"):
        _fetch("https://example.test/file", get=status(404), sleep=pauses.append)
    assert len(calls) == 1
    calls.clear()
    with pytest.raises(CurationValidationError, match="503"):
        _fetch("https://example.test/file", get=status(503), sleep=lambda _: None)
    assert len(calls) == 3


def test_export_runtime_corpus_loads_with_review_state_in_provenance(tmp_path):
    """Exports use the runtime JSON-array format and record review approval."""
    root = tmp_path / "build"
    curate(_scope(tmp_path), root, fetch=FILES.__getitem__, sleep=lambda _: None)
    output = tmp_path / "runtime" / "corpus.json"

    assert export_runtime_corpus(root, output) == 2
    entries = load_corpus(output)
    assert [entry.source_id for entry in entries] == ["guide", "run"]
    assert entries[1].section == "docs/run.rst"
    assert entries[1].version == "1.0"
    assert entries[1].provenance.endswith("review not approved.")
    _approve(root)
    export_runtime_corpus(root, output)
    assert load_corpus(output)[0].provenance.endswith("review approved.")

    (root / "captured/content/run.md").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(CurationValidationError, match="content hash mismatch"):
        export_runtime_corpus(root, output)


def test_curate_captures_only_selected_line_ranges(tmp_path):
    """Line selections capture verbatim ranges, keep raw files whole, and are validated."""
    scope_path = _scope(tmp_path)
    scope = json.loads(scope_path.read_text())
    scope["sources"][0]["documents"][1]["lines"] = [[1, 2], [6, 6]]
    scope_path.write_text(json.dumps(scope), encoding="utf-8")
    root = tmp_path / "build"

    curate(scope_path, root, fetch=FILES.__getitem__, sleep=lambda _: None)

    run = (root / "captured/content/run.md").read_text()
    assert "Selected Lines 1–2, Lines 6–6 of the file" in run
    assert "Lines 1–2:\n\n```rst\nRun\n===\n```" in run
    assert "Lines 6–6:\n\n```rst\n    ./case.submit\n```" in run
    assert "code-block" not in run
    assert (root / "raw/docs" / REVISION / "docs/run.rst").read_bytes() == FILES[
        f"{RAW}/docs/run.rst"
    ]
    assert verify_build(root) == []

    for lines, message in (
        ([[1, 99]], "line range beyond 8 lines"),
        ([[3, 1]], "invalid line ranges"),
    ):
        scope["sources"][0]["documents"][1]["lines"] = lines
        scope_path.write_text(json.dumps(scope), encoding="utf-8")
        with pytest.raises(CurationValidationError, match=message):
            curate(scope_path, tmp_path / "bad", fetch=FILES.__getitem__, sleep=lambda _: None)
