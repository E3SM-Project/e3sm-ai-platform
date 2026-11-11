"""Offline, deterministic corpus curation artifacts.

This module deliberately supports two distinct JSON manifests.  An acquisition
*source scope* records approved upstream identity, revision, redistribution
terms, and selected documents; it does not contain captured content.  A local
*capture manifest* contains separately approved, pinned local Markdown inputs
(``id``, ``url``, ``revision``, ``license``, ``policy``, ``content_path``).
Capture writes normalized Markdown to ``content/<id>.md`` plus ``snapshot``,
``catalog``, and hash-bound ``review`` artifacts.  Neither validation nor
capture needs network access.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, ValidationError

SCHEMA_VERSION = 1
SCOPE_VERSION = 2
_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
_FLOATING_REVISIONS = {"head", "main", "master", "latest", "default", "stable"}
_COMMIT_SHA = re.compile(r"[0-9a-f]{40}\Z")


class CurationValidationError(ValueError):
    """Raised when a manifest or a corpus artifact fails curation validation."""


class ScopeDocument(BaseModel):
    """A selected repository file; license companions are kept raw, not captured.

    ``lines`` optionally selects inclusive 1-based line ranges to capture from a
    large file; the raw file is still acquired and kept whole.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    path: str
    role: Literal["content", "license"] = "content"
    lines: list[tuple[int, int]] | None = None
    notes: str | None = None


class AcquisitionSource(BaseModel):
    """An approved repository at one pinned revision, not a local capture input.

    ``include`` and ``exclude`` are repository-relative glob patterns, matched with
    :meth:`pathlib.PurePath.full_match`, that select additional documents from the
    repository's file listing at ``revision``. Explicit ``documents`` keep their
    IDs, notes, and line selections when a pattern matches the same path.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    identity: str
    owner: str
    repository_url: str
    canonical_url: str | None = None
    revision: str
    release: str
    redistribution: str
    license_url: str | None = None
    include: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    documents: list[ScopeDocument] = Field(default_factory=list)

    def document_url(self, document: ScopeDocument) -> str:
        """Return the pinned repository URL of a selected document."""
        return f"{self.repository_url}/blob/{self.revision}/{document.path}"

    @property
    def license_reference(self) -> str | None:
        """Return the explicit license URL or the first license document's URL."""
        licenses = [document for document in self.documents if document.role == "license"]
        return self.license_url or (self.document_url(licenses[0]) if licenses else None)


def pattern_document_id(source_id: str, path: str) -> str:
    """Return the stable document ID for a pattern-selected repository file.

    Parameters
    ----------
    source_id : str
        ID of the source that selected the file.
    path : str
        Repository-relative file path.

    Returns
    -------
    str
        ``<source_id>.<path>`` with ``/`` replaced by ``.`` and other characters
        outside ``[A-Za-z0-9_.-]`` replaced by ``-``.
    """
    return re.sub(r"[^A-Za-z0-9_.-]", "-", f"{source_id}.{path.replace('/', '.')}")


class SourceScope(BaseModel):
    """Versioned approved acquisition scope, intentionally separate from capture."""

    model_config = ConfigDict(extra="forbid")

    manifest_version: int
    request_interval_seconds: float
    sources: list[AcquisitionSource]


class ApprovedSource(BaseModel):
    """A reviewed source and its manifest-relative local Markdown input."""

    model_config = ConfigDict(extra="forbid")

    id: str
    url: str
    revision: str
    license: str
    policy: str
    content_path: str
    title: str | None = None


class SourceManifest(BaseModel):
    """The versioned list of source inputs accepted for a capture."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = SCHEMA_VERSION
    sources: list[ApprovedSource] = Field(default_factory=list)


class CorpusRecord(BaseModel):
    """A content-addressed captured source in a snapshot and catalog."""

    model_config = ConfigDict(extra="forbid")

    id: str
    url: str
    revision: str
    license: str
    policy: str
    content_path: str
    sha256: str
    title: str | None = None


class Snapshot(BaseModel):
    """A deterministic inventory of captured local documents."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = SCHEMA_VERSION
    records: list[CorpusRecord] = Field(default_factory=list)


class Catalog(BaseModel):
    """The publishable source catalog; it mirrors the snapshot inventory."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = SCHEMA_VERSION
    records: list[CorpusRecord] = Field(default_factory=list)


class ReviewArtifact(BaseModel):
    """Hash-bound review decision for one snapshot and catalog pair."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = SCHEMA_VERSION
    approved: bool = False
    snapshot_sha256: str
    catalog_sha256: str
    record_hashes: dict[str, str]


class ChangeSet(BaseModel):
    """Deterministic difference between baseline and candidate records."""

    model_config = ConfigDict(extra="forbid")

    added: list[CorpusRecord] = Field(default_factory=list)
    changed: list[CorpusRecord] = Field(default_factory=list)
    removed: list[CorpusRecord] = Field(default_factory=list)
    unchanged: list[CorpusRecord] = Field(default_factory=list)


def validate_source_scope(scope: SourceScope | Path | str) -> list[str]:
    """Return offline policy failures for an acquisition scope or its JSON path."""
    try:
        parsed = _load_source_scope(scope) if isinstance(scope, (Path, str)) else scope
    except CurationValidationError as error:
        return [str(error)]

    return _source_scope_failures(parsed)


def capture(manifest_path: Path | str, output_root: Path | str) -> Snapshot:
    """Create a standalone local snapshot from a local approved manifest."""
    manifest_file = Path(manifest_path)
    manifest = _load_manifest(manifest_file)
    snapshot, contents = _build_snapshot_with_content(manifest, manifest_file.parent)
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)

    for source in manifest.sources:
        record = next(item for item in snapshot.records if item.id == source.id)
        destination = _safe_child(root, record.content_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            contents[source.id],
            encoding="utf-8",
            newline="\n",
        )

    _write_artifacts(root, snapshot)

    return snapshot


def refresh(
    snapshot_root: Path | str,
    manifest_path: Path | str,
    candidate_root: Path | str,
) -> ChangeSet:
    """Capture a separate candidate root and write its deterministic changes file."""
    baseline = _load_snapshot(Path(snapshot_root))
    candidate = capture(manifest_path, candidate_root)
    changes = _compare_records(baseline.records, candidate.records)
    _write_json(Path(candidate_root) / "changes.json", changes.model_dump(mode="json"))

    return changes


def validate_corpus(root: Path | str, *, require_approved: bool = False) -> list[str]:
    """Return all offline validation failures for a corpus artifact root."""
    root = Path(root)
    failures: list[str] = []
    snapshot = _try_load(root / "snapshot.json", Snapshot, "snapshot", failures)
    catalog = _try_load(root / "catalog.json", Catalog, "catalog", failures)
    review = _try_load(root / "review.json", ReviewArtifact, "review", failures)
    if snapshot is None or catalog is None or review is None:
        return failures

    failures.extend(_record_failures(snapshot.records, root))
    if snapshot.records != catalog.records:
        failures.append("catalog records do not match snapshot records")
    if review.snapshot_sha256 != _file_sha256(root / "snapshot.json"):
        failures.append("review snapshot hash mismatch")
    if review.catalog_sha256 != _file_sha256(root / "catalog.json"):
        failures.append("review catalog hash mismatch")
    expected_hashes = {record.id: record.sha256 for record in snapshot.records}
    if review.record_hashes != expected_hashes:
        failures.append("review record hashes do not match snapshot")
    if require_approved and not review.approved:
        failures.append("review is not approved")

    return failures


def _normalize_markdown(content: str | bytes) -> str:
    """Decode UTF-8 and normalize only line endings, trailing space, and EOF."""
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip(" \t") for line in content.split("\n")).rstrip("\n") + "\n"


def _content_sha256(content: str | bytes) -> str:
    """Return the SHA-256 digest of normalized UTF-8 Markdown content."""
    return hashlib.sha256(_normalize_markdown(content).encode("utf-8")).hexdigest()


def _load_source_scope(path: Path | str) -> SourceScope:
    """Load and validate an offline acquisition scope, such as ``sources.json``.

    A source scope approves where a later operator may acquire from.  It is not
    accepted by :func:`capture`, which requires a separate local capture manifest.
    """
    scope = _load_model(Path(path), SourceScope, "source scope")
    failures = _source_scope_failures(scope)
    if failures:
        raise CurationValidationError("; ".join(failures))

    return scope


def _load_manifest(path: Path | str) -> SourceManifest:
    """Load the separate pinned local capture manifest required by :func:`capture`."""
    return _load_model(Path(path), SourceManifest, "manifest")


def _build_snapshot_with_content(
    manifest: SourceManifest, root: Path
) -> tuple[Snapshot, dict[str, str]]:
    """Build a snapshot and retain the exact normalized bytes capture will write."""
    failures = _source_failures(manifest, root)
    if failures:
        raise CurationValidationError("; ".join(failures))
    records = []
    contents: dict[str, str] = {}
    for source in sorted(manifest.sources, key=lambda item: item.id):
        input_path = _safe_child(root, source.content_path)
        try:
            normalized = _normalize_markdown(input_path.read_bytes())
        except UnicodeDecodeError as error:
            raise CurationValidationError(f"invalid UTF-8 content for {source.id}") from error
        contents[source.id] = normalized
        records.append(
            CorpusRecord(
                id=source.id,
                url=source.url,
                revision=source.revision,
                license=source.license,
                policy=source.policy,
                content_path=f"content/{source.id}.md",
                sha256=_content_sha256(normalized),
                title=source.title,
            )
        )

    return Snapshot(records=records), contents


def _compare_records(baseline: list[CorpusRecord], candidate: list[CorpusRecord]) -> ChangeSet:
    """Classify records by ID and full record value in deterministic ID order."""
    old = {record.id: record for record in baseline}
    new = {record.id: record for record in candidate}
    changes = ChangeSet(
        added=[new[key] for key in sorted(new.keys() - old.keys())],
        changed=[new[key] for key in sorted(new.keys() & old.keys()) if new[key] != old[key]],
        removed=[old[key] for key in sorted(old.keys() - new.keys())],
        unchanged=[new[key] for key in sorted(new.keys() & old.keys()) if new[key] == old[key]],
    )

    return changes


def _load_snapshot(root: Path | str) -> Snapshot:
    """Load a snapshot artifact from a corpus root."""
    return _load_model(Path(root) / "snapshot.json", Snapshot, "snapshot")


def _write_artifacts(root: Path, snapshot: Snapshot) -> None:
    catalog = Catalog(records=snapshot.records)
    _write_json(root / "snapshot.json", snapshot.model_dump(mode="json"))
    _write_json(root / "catalog.json", catalog.model_dump(mode="json"))
    review = ReviewArtifact(
        snapshot_sha256=_file_sha256(root / "snapshot.json"),
        catalog_sha256=_file_sha256(root / "catalog.json"),
        record_hashes={record.id: record.sha256 for record in snapshot.records},
    )
    _write_json(root / "review.json", review.model_dump(mode="json"))


def _source_scope_failures(scope: SourceScope) -> list[str]:
    failures: list[str] = []
    if scope.manifest_version != SCOPE_VERSION:
        failures.append(f"manifest_version must be {SCOPE_VERSION}")
    if scope.request_interval_seconds <= 0:
        failures.append("request_interval_seconds must be positive")
    if not scope.sources:
        failures.append("empty source scope")
    source_ids = [source.id for source in scope.sources]
    if len(source_ids) != len(set(source_ids)):
        failures.append("duplicate source IDs")
    document_ids = [document.id for source in scope.sources for document in source.documents]
    if len(document_ids) != len(set(document_ids)):
        failures.append("duplicate document IDs")
    for source in scope.sources:
        if not _SAFE_ID.fullmatch(source.id):
            failures.append(f"unsafe source id: {source.id}")
        for field in ("identity", "owner", "release", "redistribution"):
            if not getattr(source, field).strip():
                failures.append(f"missing {field} for {source.id}")
        for field in ("repository_url", "canonical_url", "license_url"):
            value = getattr(source, field)
            if value is not None and not _is_http_url(value):
                failures.append(f"invalid {field} for {source.id}")
        if not _COMMIT_SHA.fullmatch(source.revision):
            failures.append(
                f"unpinned revision for {source.id}: use a full 40-character commit SHA"
            )
        if not source.documents and not source.include:
            failures.append(f"no selected documents for {source.id}")
        if source.license_reference is None:
            failures.append(f"missing license document or license_url for {source.id}")
        if source.exclude and not source.include:
            failures.append(f"exclude patterns without include patterns for {source.id}")
        for pattern in source.include + source.exclude:
            if not _is_safe_pattern(pattern):
                failures.append(f"invalid path pattern for {source.id}: {pattern!r}")
        paths = [document.path for document in source.documents]
        if len(paths) != len(set(paths)):
            failures.append(f"duplicate document paths for {source.id}")
        for document in source.documents:
            if not _SAFE_ID.fullmatch(document.id):
                failures.append(f"unsafe document id for {source.id}: {document.id}")
            if not _is_safe_path(document.path):
                failures.append(f"invalid document path for {source.id}: {document.path!r}")
            if document.notes is not None and not document.notes.strip():
                failures.append(f"blank notes for {source.id}: {document.id}")
            if document.lines is not None and not _are_ordered_ranges(document.lines):
                failures.append(f"invalid line ranges for {source.id}: {document.id}")

    return failures


def _is_http_url(value: str) -> bool:
    """Return whether a nonblank value is an absolute HTTP(S) URL."""
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_safe_path(value: str) -> bool:
    """Accept a nonempty repository-relative file path without traversal or globs."""
    path = Path(value)
    return bool(
        value.strip()
        and not any(character in value for character in "\\\x00*?[]")
        and not path.is_absolute()
        and "" not in value.split("/")
        and not any(part in {"", ".", ".."} for part in path.parts)
    )


def _is_safe_pattern(value: str) -> bool:
    """Accept a nonempty repository-relative glob without traversal components."""
    path = Path(value)
    return bool(
        value.strip()
        and not any(character in value for character in "\\\x00")
        and not path.is_absolute()
        and "" not in value.split("/")
        and not any(part in {".", ".."} for part in path.parts)
    )


def _are_ordered_ranges(ranges: list[tuple[int, int]]) -> bool:
    """Accept nonempty, positive, ascending, non-overlapping inclusive ranges."""
    previous_end = 0
    for start, end in ranges:
        if start <= previous_end or end < start:
            return False
        previous_end = end
    return bool(ranges)


def _is_unpinned_revision(revision: str) -> bool:
    """Return whether revision is blank or a known moving reference."""
    return not revision.strip() or revision.strip().lower() in _FLOATING_REVISIONS


def _source_failures(manifest: SourceManifest, root: Path) -> list[str]:
    failures = _record_metadata_failures(manifest.sources)
    for source in manifest.sources:
        try:
            path = _safe_child(root, source.content_path)
            if not path.is_file():
                failures.append(f"missing content file for {source.id}: {source.content_path}")
        except CurationValidationError as error:
            failures.append(f"unsafe content path for {source.id}: {error}")

    return failures


def _record_failures(records: list[CorpusRecord], root: Path) -> list[str]:
    failures = _record_metadata_failures(records)
    for record in records:
        try:
            path = _safe_child(root, record.content_path)
            if not path.is_file():
                failures.append(f"missing content file for {record.id}: {record.content_path}")
            elif _content_sha256(path.read_bytes()) != record.sha256:
                failures.append(f"content hash mismatch for {record.id}")
        except (CurationValidationError, UnicodeDecodeError) as error:
            failures.append(f"broken content for {record.id}: {error}")

    return failures


def _record_metadata_failures(records: list[Any]) -> list[str]:
    failures: list[str] = []
    for attr, label in (("id", "IDs"), ("url", "URLs")):
        values = [getattr(record, attr) for record in records]
        if len(values) != len(set(values)):
            failures.append(f"duplicate {label}")
    hashes = [getattr(record, "sha256", None) for record in records]
    known_hashes = [value for value in hashes if value]
    if len(known_hashes) != len(set(known_hashes)):
        failures.append("duplicate content hashes")
    for record in records:
        if not _SAFE_ID.fullmatch(record.id):
            failures.append(f"unsafe id: {record.id}")
        if not _is_http_url(record.url):
            failures.append(f"invalid URL for {record.id}")
        if not all(
            str(getattr(record, field, "")).strip() for field in ("revision", "license", "policy")
        ):
            failures.append(f"incomplete provenance or policy for {record.id}")
        if _is_unpinned_revision(str(record.revision)):
            failures.append(f"unpinned revision for {record.id}")

    return failures


def _safe_child(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or not relative or any(part in {"", ".", ".."} for part in path.parts):
        raise CurationValidationError("path is not a safe relative path")
    resolved_root = root.resolve()
    resolved = (resolved_root / path).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise CurationValidationError("path escapes root")

    return resolved


def _load_model(path: Path, model: type[BaseModel], label: str) -> Any:
    try:
        return model.model_validate_json(path.read_bytes())
    except (OSError, ValidationError, ValueError) as error:
        raise CurationValidationError(f"invalid {label}: {error}") from error


def _try_load(path: Path, model: type[BaseModel], label: str, failures: list[str]) -> Any | None:
    try:
        return _load_model(path, model, label)
    except CurationValidationError as error:
        failures.append(str(error))
        return None


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )


def _file_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""
