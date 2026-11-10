"""Reproducible local corpus builds from the approved acquisition scope.

:func:`curate` downloads every selected document in a source scope at its pinned
revision, keeps the unchanged bytes with their provenance, prepares one Markdown
input per document, and captures and validates the result with
:mod:`e3sm_ai_platform.knowledge.curation`. Upstream text is kept verbatim:
Markdown files are used as-is and other formats are fenced under a provenance
header, so fidelity is checked mechanically. Documents with the ``license`` role
are kept as raw companions, not captured as content. :func:`export_runtime_corpus`
writes a build in the runtime JSON-array format, and :func:`package` turns an
approved build into a deterministic archive and checksum; neither uploads anything.

Build layout::

    <root>/
      acquisition.json        # provenance and hashes for every acquired file
      raw/<source>/<revision>/<path>
      prepared/<document>.md
      capture-manifest.json
      captured/               # content, snapshot, catalog, and review
"""

from __future__ import annotations

import datetime
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import tarfile
import time
from collections.abc import Callable
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, ConfigDict, Field

from e3sm_ai_platform.domain.models import CorpusEntry
from e3sm_ai_platform.knowledge.curation import (
    SCHEMA_VERSION,
    AcquisitionSource,
    ApprovedSource,
    CurationValidationError,
    ScopeDocument,
    Snapshot,
    SourceManifest,
    SourceScope,
    _normalize_markdown,
    capture,
    pattern_document_id,
    validate_corpus,
    validate_source_scope,
)

Fetcher = Callable[[str], bytes]
FileLister = Callable[[AcquisitionSource], list[str]]

_RST_INCLUDE = re.compile(r"^\s*\.\.\s+(?:literalinclude|include)::\s+(\S+)", re.MULTILINE)
_FENCE_LANGUAGES = {
    ".bash": "bash",
    ".cfg": "ini",
    ".ini": "ini",
    ".py": "python",
    ".rst": "rst",
    ".sh": "bash",
    ".texi": "texinfo",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
}


class AcquiredDocument(BaseModel):
    """Provenance and integrity record for one acquired upstream file."""

    model_config = ConfigDict(extra="forbid")

    id: str
    source_id: str
    owner: str
    path: str
    revision: str
    release: str
    url: str
    raw_url: str
    license_url: str
    redistribution: str
    lines: list[tuple[int, int]] | None = None
    notes: str | None = None
    pattern: str | None = None
    raw_path: str
    byte_length: int
    sha256: str
    git_blob_sha1: str
    acquired_at: str
    captured: bool


class AcquisitionRecord(BaseModel):
    """All acquired files for one build, bound to the scope that selected them."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = SCHEMA_VERSION
    scope_sha256: str
    documents: list[AcquiredDocument]
    unresolved_includes: list[str] = Field(default_factory=list)


def curate(
    scope_path: Path | str,
    output_root: Path | str,
    *,
    overwrite: bool = False,
    fetch: Fetcher | None = None,
    list_files: FileLister | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> Snapshot:
    """Build a validated local corpus from every document selected in a scope.

    Parameters
    ----------
    scope_path : Path or str
        Acquisition scope JSON, such as ``corpus/sources.json``.
    output_root : Path or str
        Build directory. It is written atomically: the build happens in a
        sibling ``.partial`` directory that replaces ``output_root`` on success.
    overwrite : bool, optional
        Replace an existing previous build at ``output_root``.
    fetch : callable, optional
        Function returning the bytes at a URL. Defaults to an HTTPS GET.
    list_files : callable, optional
        Function returning a source's repository file paths at its revision, used
        to expand ``include`` patterns. Defaults to the GitHub tree API, which
        sends ``GITHUB_TOKEN`` when set.
    sleep : callable, optional
        Pause between requests, honoring each source's request interval.

    Returns
    -------
    Snapshot
        The captured snapshot. Its review artifact is never approved here.

    Raises
    ------
    CurationValidationError
        If the scope is invalid, a download fails, the output already exists,
        or the finished build fails verification.
    """
    scope_file = Path(scope_path)
    root = Path(output_root)
    scope = _load_scope(scope_file)
    if root.exists() and any(root.iterdir()):
        if not overwrite:
            raise CurationValidationError(f"{root} already exists; pass overwrite to replace it")
        if not (root / "acquisition.json").is_file():
            raise CurationValidationError(f"refusing to replace {root}: not a corpus build")
    partial = root.with_name(f"{root.name}.partial")
    if partial.exists():
        shutil.rmtree(partial)

    try:
        scope, patterns = _expand_patterns(scope, list_files or _list_github_files, sleep)
        record = _acquire(scope, scope_file, partial, fetch or _fetch, sleep, patterns)
        record.unresolved_includes = _prepare(scope, record, partial)
        (partial / "acquisition.json").write_text(
            record.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        snapshot = capture(partial / "capture-manifest.json", partial / "captured")
        failures = verify_build(partial)
        if failures:
            raise CurationValidationError("; ".join(failures))
    except BaseException:
        shutil.rmtree(partial, ignore_errors=True)
        raise

    if root.exists():
        shutil.rmtree(root)
    partial.rename(root)

    return snapshot


def verify_build(root: Path | str) -> list[str]:
    """Return integrity and fidelity failures for a corpus build, offline.

    Checks raw byte lengths and hashes against ``acquisition.json``, that each
    captured document contains its normalized raw text unchanged, and the
    capture artifacts with :func:`~e3sm_ai_platform.knowledge.curation.validate_corpus`.

    Parameters
    ----------
    root : Path or str
        Build directory written by :func:`curate`.

    Returns
    -------
    list of str
        Failure messages; empty when the build is intact.
    """
    root = Path(root)
    try:
        record = AcquisitionRecord.model_validate_json((root / "acquisition.json").read_bytes())
    except (OSError, ValueError) as error:
        return [f"invalid acquisition record: {error}"]

    failures = validate_corpus(root / "captured")
    for document in record.documents:
        try:
            body = (root / document.raw_path).read_bytes()
        except OSError:
            failures.append(f"missing raw file for {document.id}")
            continue
        if len(body) != document.byte_length or _sha256(body) != document.sha256:
            failures.append(f"raw hash mismatch for {document.id}")
            continue
        if not document.captured:
            continue
        captured = root / "captured" / "content" / f"{document.id}.md"
        if not captured.is_file():
            failures.append(f"missing captured content for {document.id}")
            continue
        content = captured.read_text(encoding="utf-8")
        try:
            excerpts = _excerpts(document, body.decode("utf-8"))
        except (UnicodeDecodeError, CurationValidationError):
            excerpts = [(None, "\x00")]
        if any(_normalize_markdown(text).rstrip("\n") not in content for _, text in excerpts):
            failures.append(f"captured content differs from raw text for {document.id}")

    return failures


def runtime_entries(root: Path | str) -> list[CorpusEntry]:
    """Return one runtime corpus entry per captured document in a build.

    Parameters
    ----------
    root : Path or str
        Build directory written by :func:`curate`.

    Returns
    -------
    list of CorpusEntry
        Entries in snapshot order. Each entry's provenance states the pinned
        revision and whether the build's review is approved.

    Raises
    ------
    CurationValidationError
        If the build fails :func:`verify_build`.
    """
    root = Path(root)
    failures = verify_build(root)
    if failures:
        raise CurationValidationError("; ".join(failures))
    record = AcquisitionRecord.model_validate_json((root / "acquisition.json").read_bytes())
    documents = {document.id: document for document in record.documents}
    snapshot = Snapshot.model_validate_json((root / "captured" / "snapshot.json").read_bytes())
    approved = not validate_corpus(root / "captured", require_approved=True)
    review = "review approved" if approved else "review not approved"
    entries = []
    for item in snapshot.records:
        document = documents[item.id]
        entries.append(
            CorpusEntry(
                source_id=item.id,
                title=item.title or item.id,
                url=item.url,
                section=document.path,
                component=document.source_id,
                version=document.release,
                provenance=f"Verbatim upstream file at revision {item.revision}; {review}.",
                text=(root / "captured" / item.content_path).read_text(encoding="utf-8"),
            )
        )

    return entries


def export_runtime_corpus(root: Path | str, output: Path | str) -> int:
    """Write a build's captured documents as a runtime corpus JSON array.

    Parameters
    ----------
    root : Path or str
        Build directory written by :func:`curate`.
    output : Path or str
        JSON file for ``CORPUS_PATH``; the packaged corpus is never modified.

    Returns
    -------
    int
        Number of exported entries.
    """
    entries = runtime_entries(root)
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [entry.model_dump(mode="json") for entry in entries]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return len(entries)


def package(root: Path | str, output_dir: Path | str, version: str) -> Path:
    """Write a deterministic archive and checksum for an approved build.

    The archive contains ``captured/``, ``acquisition.json``, and the raw
    license and notice companions. Nothing is uploaded.

    Parameters
    ----------
    root : Path or str
        Build directory written by :func:`curate`.
    output_dir : Path or str
        Directory for ``e3sm-corpus-<version>.tar.gz`` and its ``.sha256`` file.
    version : str
        Release label; letters, digits, ``.``, ``_``, and ``-`` only.

    Returns
    -------
    Path
        Path to the written archive.

    Raises
    ------
    CurationValidationError
        If the version is unsafe, the build fails verification, or its review
        is not approved.
    """
    root = Path(root)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", version):
        raise CurationValidationError(f"unsafe package version: {version!r}")
    failures = verify_build(root) + validate_corpus(root / "captured", require_approved=True)
    if failures:
        raise CurationValidationError("; ".join(dict.fromkeys(failures)))

    record = AcquisitionRecord.model_validate_json((root / "acquisition.json").read_bytes())
    members = [root / "acquisition.json"]
    members += sorted(path for path in (root / "captured").rglob("*") if path.is_file())
    members += [root / document.raw_path for document in record.documents if not document.captured]
    name = f"e3sm-corpus-{version}"
    archive = Path(output_dir) / f"{name}.tar.gz"
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_bytes(_deterministic_tar_gz(root, name, members))
    archive.with_name(f"{archive.name}.sha256").write_text(
        f"{_sha256(archive.read_bytes())}  {archive.name}\n", encoding="utf-8"
    )

    return archive


def _load_scope(path: Path) -> SourceScope:
    """Load a valid scope whose sources are all GitHub-hosted."""
    failures = validate_source_scope(path)
    if failures:
        raise CurationValidationError("; ".join(failures))
    scope = SourceScope.model_validate_json(path.read_bytes())
    for source in scope.sources:
        _github_repository(source)

    return scope


def _expand_patterns(
    scope: SourceScope, list_files: FileLister, sleep: Callable[[float], None]
) -> tuple[SourceScope, dict[str, str]]:
    """Add pattern-selected files to each source and return the matching patterns."""
    sources = []
    patterns: dict[str, str] = {}
    for source in scope.sources:
        if not source.include:
            sources.append(source)
            continue
        sleep(scope.request_interval_seconds)
        explicit = {document.path for document in source.documents}
        documents = list(source.documents)
        for path in sorted(list_files(source)):
            pure = PurePosixPath(path)
            matched = next((p for p in source.include if pure.full_match(p)), None)
            if matched is None or any(pure.full_match(p) for p in source.exclude):
                continue
            if path in explicit:
                continue
            document = ScopeDocument(id=pattern_document_id(source.id, path), path=path)
            documents.append(document)
            patterns[document.id] = matched
        sources.append(source.model_copy(update={"documents": documents}))
    expanded = scope.model_copy(update={"sources": sources})
    failures = validate_source_scope(expanded)
    if failures:
        raise CurationValidationError("; ".join(failures))

    return expanded, patterns


def _github_repository(source: AcquisitionSource) -> tuple[str, str]:
    """Return the owner and name of a GitHub-hosted source repository."""
    parsed = urlparse(source.repository_url)
    parts = parsed.path.strip("/").split("/")
    if parsed.scheme != "https" or parsed.netloc != "github.com" or len(parts) != 2:
        raise CurationValidationError(f"unsupported repository URL for {source.id}")

    return parts[0], parts[1]


def _raw_url(source: AcquisitionSource, document: ScopeDocument) -> str:
    """Return the pinned raw-file URL for a GitHub-hosted document."""
    owner, repo = _github_repository(source)
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{source.revision}/{document.path}"


def _list_github_files(source: AcquisitionSource) -> list[str]:
    """Return every file path in a GitHub repository at the source revision."""
    owner, repo = _github_repository(source)
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{source.revision}?recursive=1"
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    tree = json.loads(_fetch(url, headers=headers))
    if tree.get("truncated"):
        raise CurationValidationError(f"truncated repository file listing for {source.id}")

    return [item["path"] for item in tree["tree"] if item["type"] == "blob"]


def _acquire(
    scope: SourceScope,
    scope_file: Path,
    root: Path,
    fetch: Fetcher,
    sleep: Callable[[float], None],
    patterns: dict[str, str],
) -> AcquisitionRecord:
    """Download every selected document unchanged and record its provenance."""
    documents = []
    first = True
    for source in scope.sources:
        for document in source.documents:
            if not first:
                sleep(scope.request_interval_seconds)
            first = False
            raw_url = _raw_url(source, document)
            acquired_at = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
            body = fetch(raw_url)
            raw_path = Path("raw", source.id, source.revision, document.path)
            destination = root / raw_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(body)
            documents.append(
                AcquiredDocument(
                    id=document.id,
                    source_id=source.id,
                    owner=source.owner,
                    path=document.path,
                    revision=source.revision,
                    release=source.release,
                    url=source.document_url(document),
                    raw_url=raw_url,
                    license_url=source.license_reference or "",
                    redistribution=source.redistribution,
                    lines=document.lines,
                    notes=document.notes,
                    pattern=patterns.get(document.id),
                    raw_path=raw_path.as_posix(),
                    byte_length=len(body),
                    sha256=_sha256(body),
                    git_blob_sha1=hashlib.sha1(b"blob %d\0" % len(body) + body).hexdigest(),
                    acquired_at=acquired_at,
                    captured=document.role != "license",
                )
            )
    record = AcquisitionRecord(scope_sha256=_sha256(scope_file.read_bytes()), documents=documents)

    return record


def _prepare(scope: SourceScope, record: AcquisitionRecord, root: Path) -> list[str]:
    """Write verbatim Markdown inputs and the capture manifest; return unresolved includes."""
    sources = {source.id: source for source in scope.sources}
    acquired = {(document.source_id, document.path) for document in record.documents}
    manifest = SourceManifest()
    unresolved = []
    for document in record.documents:
        if not document.captured:
            continue
        source = sources[document.source_id]
        try:
            text = (root / document.raw_path).read_bytes().decode("utf-8")
        except UnicodeDecodeError as error:
            raise CurationValidationError(f"invalid UTF-8 content for {document.id}") from error
        title = f"{source.identity}: {document.path}"
        content_path = f"prepared/{document.id}.md"
        prepared = root / content_path
        prepared.parent.mkdir(parents=True, exist_ok=True)
        excerpts = _excerpts(document, text)
        prepared.write_text(_markdown(title, document, excerpts), encoding="utf-8", newline="\n")
        for target in _RST_INCLUDE.findall(text):
            if not _include_acquired(document, target, acquired):
                unresolved.append(f"{document.id}: {target}")
        manifest.sources.append(
            ApprovedSource(
                id=document.id,
                url=document.url,
                revision=document.revision,
                license=document.license_url,
                policy=document.redistribution,
                content_path=content_path,
                title=title,
            )
        )
    (root / "capture-manifest.json").write_text(
        manifest.model_dump_json(indent=2, exclude_none=True) + "\n", encoding="utf-8"
    )

    return unresolved


def _include_acquired(
    document: AcquiredDocument, target: str, acquired: set[tuple[str, str]]
) -> bool:
    """Return whether an RST include target was acquired from the same source.

    Relative targets resolve against the including file; Sphinx root-relative
    targets (leading ``/``) match any acquired path that ends with them.
    """
    if target.startswith("/"):
        suffix = target.lstrip("/")
        return any(
            source == document.source_id and path.endswith(suffix) for source, path in acquired
        )
    parts: list[str] = []
    for part in PurePosixPath(document.path).parent.joinpath(target).parts:
        if part == "..":
            if parts:
                parts.pop()
        elif part != ".":
            parts.append(part)

    return (document.source_id, "/".join(parts)) in acquired


def _excerpts(document: AcquiredDocument, text: str) -> list[tuple[str | None, str]]:
    """Return the whole text, or each selected line range with its label."""
    if document.lines is None:
        return [(None, text)]
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if document.lines[-1][1] > len(lines):
        raise CurationValidationError(f"line range beyond {len(lines)} lines for {document.id}")

    return [
        (f"Lines {start}–{end}", "\n".join(lines[start - 1 : end]) + "\n")
        for start, end in document.lines
    ]


def _markdown(
    title: str, document: AcquiredDocument, excerpts: list[tuple[str | None, str]]
) -> str:
    """Wrap upstream text under a provenance header, fencing non-Markdown formats."""
    selection = ""
    if document.lines is not None:
        ranges = ", ".join(label for label, _ in excerpts if label)
        selection = f" Selected {ranges} of the file; the raw file is kept whole."
    header = (
        f"# {title}\n\n"
        f"> Source: <{document.url}> at revision `{document.revision}`. Owner: "
        f"{document.owner}. License: <{document.license_url}>. Verbatim upstream "
        f"text; not reviewed.{selection}\n\n"
    )
    suffixes = Path(document.path).suffixes
    language = next(
        (
            _FENCE_LANGUAGES[suffix.lower()]
            for suffix in reversed(suffixes)
            if suffix.lower() in _FENCE_LANGUAGES
        ),
        "text",
    )
    is_markdown = bool(suffixes) and suffixes[-1].lower() == ".md"
    blocks = []
    for label, text in excerpts:
        prefix = f"{label}:\n\n" if label else ""
        if is_markdown:
            blocks.append(prefix + text)
            continue
        longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
        fence = "`" * max(3, longest + 1)
        body = text.rstrip("\n")
        blocks.append(f"{prefix}{fence}{language}\n{body}\n{fence}\n")

    return header + "\n".join(blocks)


def _fetch(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    get: Callable[..., httpx.Response] = httpx.get,
    sleep: Callable[[float], None] = time.sleep,
    attempts: int = 3,
) -> bytes:
    """Return the body of a successful GET, retrying transport and server errors."""
    for attempt in range(1, attempts + 1):
        try:
            response = get(url, timeout=60.0, headers=headers)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as error:
            if error.response.status_code < 500 or attempt == attempts:
                raise CurationValidationError(f"failed to fetch {url}: {error}") from error
        except httpx.TransportError as error:
            if attempt == attempts:
                raise CurationValidationError(f"failed to fetch {url}: {error}") from error
        sleep(2.0**attempt)

    raise AssertionError("unreachable")


def _deterministic_tar_gz(root: Path, prefix: str, members: list[Path]) -> bytes:
    """Return gzip-compressed tar bytes that depend only on member content."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for path in sorted(members, key=lambda item: item.relative_to(root).as_posix()):
            data = path.read_bytes()
            info = tarfile.TarInfo(f"{prefix}/{path.relative_to(root).as_posix()}")
            info.size = len(data)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(data))

    return gzip.compress(buffer.getvalue(), mtime=0)


def _sha256(data: bytes) -> str:
    """Return the hexadecimal SHA-256 digest of bytes."""
    return hashlib.sha256(data).hexdigest()
