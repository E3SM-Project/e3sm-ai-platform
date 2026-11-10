"""Reproducible local corpus builds from the approved acquisition scope.

:func:`curate` downloads every selected document in a source scope at its pinned
revision, keeps the unchanged bytes with their provenance, prepares one Markdown
input per document, and captures and validates the result with
:mod:`e3sm_ai_platform.knowledge.curation`. Upstream text is kept verbatim:
Markdown files are used as-is and other formats are fenced under a provenance
header, so fidelity is checked mechanically. License and notice files are kept
as raw companions, not captured as content. :func:`package` turns an approved
build into a deterministic archive and checksum; it never uploads anything.

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
import re
import shutil
import tarfile
import time
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, ConfigDict

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
    validate_corpus,
    validate_source_scope,
)

Fetcher = Callable[[str], bytes]

_COMPANION_PREFIXES = ("LICENSE", "NOTICE", "COPYING")
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
    url: str
    raw_url: str
    license_url: str
    access: str
    redistribution: str
    provenance: str
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


def curate(
    scope_path: Path | str,
    output_root: Path | str,
    *,
    overwrite: bool = False,
    fetch: Fetcher | None = None,
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
        record = _acquire(scope, scope_file, partial, fetch or _fetch, sleep)
        _prepare(scope, record, partial)
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
        elif _normalize_markdown(body).rstrip("\n") not in captured.read_text(encoding="utf-8"):
            failures.append(f"captured content differs from raw text for {document.id}")

    return failures


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
    """Load a scope and reject policy failures or documents outside its paths."""
    failures = validate_source_scope(path)
    if failures:
        raise CurationValidationError("; ".join(failures))
    scope = SourceScope.model_validate_json(path.read_bytes())
    ids = [document.id for source in scope.sources for document in source.documents]
    if len(ids) != len(set(ids)):
        failures.append("document IDs must be unique across sources")
    for source in scope.sources:
        for document in source.documents:
            if not _in_path_scope(document.path, source):
                failures.append(f"document outside path scope: {document.id}")
            if not document.url.startswith(f"{source.repository_url}/blob/{document.revision}/"):
                failures.append(
                    f"document URL does not match repository and revision: {document.id}"
                )
            _raw_url(source, document)
    if failures:
        raise CurationValidationError("; ".join(failures))

    return scope


def _in_path_scope(path: str, source: AcquisitionSource) -> bool:
    """Return whether a path matches an include pattern and no exclude pattern."""
    included = any(Path(path).full_match(pattern) for pattern in source.path_scope.include)
    excluded = any(Path(path).full_match(pattern) for pattern in source.path_scope.exclude)
    return included and not excluded


def _raw_url(source: AcquisitionSource, document: ScopeDocument) -> str:
    """Return the pinned raw-file URL for a GitHub-hosted document."""
    parsed = urlparse(source.repository_url)
    parts = parsed.path.strip("/").split("/")
    if parsed.scheme != "https" or parsed.netloc != "github.com" or len(parts) != 2:
        raise CurationValidationError(f"unsupported repository URL for {source.id}")
    owner, repo = parts
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{document.revision}/{document.path}"


def _acquire(
    scope: SourceScope, scope_file: Path, root: Path, fetch: Fetcher, sleep: Callable[[float], None]
) -> AcquisitionRecord:
    """Download every selected document unchanged and record its provenance."""
    documents = []
    first = True
    for source in scope.sources:
        for document in source.documents:
            if not first:
                sleep(source.request_interval_seconds)
            first = False
            raw_url = _raw_url(source, document)
            acquired_at = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
            body = fetch(raw_url)
            raw_path = Path("raw", source.id, document.revision, document.path)
            destination = root / raw_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(body)
            documents.append(
                AcquiredDocument(
                    id=document.id,
                    source_id=source.id,
                    owner=source.owner,
                    path=document.path,
                    revision=document.revision,
                    url=document.url,
                    raw_url=raw_url,
                    license_url=source.license_url,
                    access=source.access,
                    redistribution=source.redistribution,
                    provenance=document.provenance,
                    raw_path=raw_path.as_posix(),
                    byte_length=len(body),
                    sha256=_sha256(body),
                    git_blob_sha1=hashlib.sha1(b"blob %d\0" % len(body) + body).hexdigest(),
                    acquired_at=acquired_at,
                    captured=not Path(document.path).name.upper().startswith(_COMPANION_PREFIXES),
                )
            )
    record = AcquisitionRecord(scope_sha256=_sha256(scope_file.read_bytes()), documents=documents)
    (root / "acquisition.json").write_text(
        record.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )

    return record


def _prepare(scope: SourceScope, record: AcquisitionRecord, root: Path) -> None:
    """Write verbatim Markdown inputs and the strict capture manifest."""
    sources = {source.id: source for source in scope.sources}
    manifest = SourceManifest()
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
        prepared.write_text(_markdown(title, document, text), encoding="utf-8", newline="\n")
        manifest.sources.append(
            ApprovedSource(
                id=document.id,
                url=document.url,
                revision=document.revision,
                license=document.license_url,
                policy=f"{document.access} {document.redistribution}",
                content_path=content_path,
                title=title,
            )
        )
    (root / "capture-manifest.json").write_text(
        manifest.model_dump_json(indent=2, exclude_none=True) + "\n", encoding="utf-8"
    )


def _markdown(title: str, document: AcquiredDocument, text: str) -> str:
    """Wrap upstream text under a provenance header, fencing non-Markdown formats."""
    header = (
        f"# {title}\n\n"
        f"> Source: <{document.url}> at revision `{document.revision}`. Owner: "
        f"{document.owner}. License: <{document.license_url}>. Verbatim upstream "
        "text; not reviewed.\n\n"
    )
    suffixes = Path(document.path).suffixes
    if suffixes and suffixes[-1].lower() == ".md":
        return header + text
    language = next(
        (
            _FENCE_LANGUAGES[suffix.lower()]
            for suffix in reversed(suffixes)
            if suffix.lower() in _FENCE_LANGUAGES
        ),
        "text",
    )
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    body = text.rstrip("\n")

    return f"{header}{fence}{language}\n{body}\n{fence}\n"


def _fetch(
    url: str,
    *,
    get: Callable[..., httpx.Response] = httpx.get,
    sleep: Callable[[float], None] = time.sleep,
    attempts: int = 3,
) -> bytes:
    """Return the body of a successful GET, retrying transport and server errors."""
    for attempt in range(1, attempts + 1):
        try:
            response = get(url, timeout=60.0)
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
