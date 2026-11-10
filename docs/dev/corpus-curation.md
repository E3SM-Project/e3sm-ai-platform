# Corpus curation

Curation and local builds have no runtime impact. Only `curate` uses the network;
tests and CI perform no live source checks.

The human-owned approved scope is
[`corpus/sources.json`](../../corpus/sources.json). A selected document approves
acquisition only, not capture fidelity, scientific correctness, or publication.
Keep review and build state out of the scope.

## Source scope format

The scope (`manifest_version` 2) records one shared `request_interval_seconds`
and a list of sources. Each source is one repository at one pinned revision:

- `id`, `identity`, `owner`, `repository_url`, and optional `canonical_url`.
- `revision`: a pinned commit; floating names such as `main` are rejected.
  Select another revision of the same repository as a separate source.
- `release`: a human-readable label, such as `v3.1.0` or a cohort name.
- `redistribution`: the terms recorded as each captured document's policy.
- `documents`: each has a unique `id`, a repository-relative `path`, an optional
  `role` (`license` marks a raw-only companion), optional `lines`, and optional
  `notes` for caveats about misleading or unverified upstream content. `lines`
  lists ascending, non-overlapping inclusive 1-based ranges, such as
  `[[14, 21], [19685, 21956]]`, to capture only part of a very large file.
- `license_url`: only when no document has the `license` role.

Document URLs are derived as `<repository_url>/blob/<revision>/<path>`, and the
license reference is the first `license` document's URL. Which questions use each
document is recorded in `corpus/questions.json`, not in the scope.

This source scope is not the capture manifest accepted by `capture` and `refresh`.
`curate` derives a separate pinned capture manifest from the scope for each build.
Do not pass `corpus/sources.json` to `capture` or `refresh`.

## Workflow

Run from the repository root; `make help` lists the targets.

1. **Curate:** `make corpus-curate` validates the scope, downloads every selected
   document at its pinned revision, prepares Markdown, captures, and verifies the
   build in `corpus/local/corpus/`. It replaces a previous build only on success.
   Timeouts and server errors are retried up to three times; other failures stop
   the build and leave the previous build unchanged.
2. **Validate:** `make corpus-validate` rechecks the scope and the build offline.
3. **Coverage:** `make corpus-coverage` runs the questions in
   [`corpus/questions.json`](../../corpus/questions.json) against the build and
   reports which expected documents each one retrieves and cites.
   Optionally, `make corpus-export` writes the build for the backend's
   `CORPUS_PATH` ([runtime use](#runtime-use)).
4. **Review:** an authorized reviewer checks the build and records approval in
   `captured/review.json`. Never set approval as part of curation.
5. **Package:** `make corpus-package VERSION=<label>` archives an approved build
   locally. It refuses unapproved builds and never uploads anything.

`capture` and `refresh` remain available for hand-prepared local manifests; they
do not fetch live URLs. Do not publish a document without a pinned revision, raw
snapshot, normalized copy, and reviewer approval.

## Build contents

`corpus/local/` is git-ignored; never commit build outputs. It is not a backup:
`git clean -x` or removing the clone deletes it.

```text
corpus/local/corpus/
  acquisition.json        # provenance and hashes for every acquired file
  raw/<source>/<revision>/<path>  # unchanged upstream bytes
  prepared/<document>.md  # verbatim Markdown inputs
  capture-manifest.json   # strict pinned manifest derived from the scope
  captured/               # content/<id>.md, snapshot, catalog, review
```

`acquisition.json` records, for each file, the document and source IDs, owner,
repository path, pinned revision, release label, derived and raw URLs, license
URL, redistribution terms, notes, byte length, SHA-256, Git blob SHA-1,
and UTC acquisition time. It also records the SHA-256 of the scope that selected
the files. A Git blob hash is not a raw SHA-256 or a package artifact hash.

## Preparation

Curation keeps upstream text verbatim; it does not convert formats. It captures
whole files unless a document selects `lines`; use that only for very large files
whose unrelated content adds retrieval noise, and include any license notice the
excerpt must carry. Each prepared document starts with a title and a provenance
line (source URL, revision, owner, license, and any selected ranges), followed by
the upstream text; each selected range is labeled and kept verbatim:

- Markdown files are used as-is.
- Other formats, including RST, Texinfo, XML, YAML, configuration, and scripts,
  are fenced with a language tag. The fence is longer than any backtick run in
  the text, so the upstream text is never altered.
- Documents with the `license` role are kept as raw companions and are not
  captured as content.
- Includes are not resolved. Select each needed file, such as an included
  configuration, as its own document.

Capture normalizes CRLF/CR to LF, removes trailing spaces and tabs on each line,
and writes one final newline. Leading indentation and internal whitespace remain
intact. Format conversion and structure-preserving chunking are deferred.

Keep release content distinct from development content. Record upstream commits,
feedstock revisions, and package versions/builds/hashes separately. Declared
dependencies do not establish a solved environment or machine compatibility.
Never execute upstream examples, install environments, or submit HPC jobs during
curation. Record caveats about misleading upstream content in the document's
`notes` in the scope.

The capture manifest contains `schema_version` and `sources`; each source has
`id`, `url`, `revision`, `license`, `policy`, `content_path`, and optional
`title`, and the manifest rejects unknown fields. Capture IDs must match
`[A-Za-z0-9][A-Za-z0-9_.-]*` and be unique across sources. Capture rejects
floating revisions such as `main` or `master` and duplicate IDs or URLs;
validation also rejects duplicate normalized content. Do not rename existing
runtime citation IDs as part of capture.

## Integrity, review, and publication

`validate-sources` rejects unpinned revisions, unsafe IDs and paths, duplicate
IDs, and sources without a license reference; `curate` also rejects non-GitHub
repositories. `verify-build`,
run by `curate` and `corpus-validate`, checks offline that:

- raw byte lengths and SHA-256 values match `acquisition.json`;
- each captured document contains its normalized raw text, or each selected
  line range, unchanged;
- capture artifacts pass `validate`: record metadata, safe content paths,
  normalized hashes, duplicate records, catalog consistency, and the hash-bound
  review artifact.

These checks do not verify scientific accuracy, retrieval coverage, or upstream
Git blob identities through the GitHub API. Because text is verbatim, review
focuses on selection, licensing, and flagged upstream caveats rather than
conversion fidelity. Passing checks never grants review approval or publication.

Leave `review.json` with `approved: false` until an authorized reviewer approves
the hash-bound snapshot; `validate --require-approved` rejects it until then.
`package` writes `e3sm-corpus-<version>.tar.gz` and a `.sha256` file containing
`acquisition.json`, `captured/`, and the raw license and notice companions. The
archive is deterministic for identical inputs. Publishing it requires separate
authorization; GitHub Release automation and JSONL migration are deferred.

## Question coverage

`corpus/questions.json` lists each representative question and the selected
documents that should support it, following the
[source mapping](../github-issues/20-corpus/3-source-mapping.md). Update it with
the mapping; tests check that every expected document is a selected,
non-license document in the scope.

`coverage` loads one corpus entry per captured document and answers each question
with the application's chunking, lexical retrieval, routing, and deterministic
generation, using default settings, no provider, and no network. Per question,
it reports the expected documents among the distinct documents in the top eight
chunks and among the top-four answer's citations. `make corpus-coverage` prints
a table and writes `corpus/local/coverage.json`. The report has no pass/fail
threshold and does not judge answer quality; retrieval evaluation belongs to #21.

## Runtime use

The backend uses the packaged `curated_corpus.json` unless `CORPUS_PATH` names
another runtime corpus. `make corpus-export` verifies the build and writes
`corpus/local/runtime-corpus.json` in the same JSON-array format, one entry per
captured document; the packaged corpus is never modified. Set `CORPUS_PATH` to
that file's absolute path in `backend/.env` to try the build in the API and UI.
Each entry's provenance states its pinned revision and whether review is
approved; exporting does not approve anything. `/health` reports the loaded
corpus's `snapshot_id`, and query traces carry it as `rag.corpus_snapshot_id`,
so answers can be tied to the corpus that produced them.

The evaluation adapter always uses the packaged corpus because its fixtures cite
packaged source IDs. Replacing the packaged corpus is a separate decision that
requires review approval and updated evaluation fixtures.

## Commands

Run these from the repository root. Paths other than the `make` defaults are
examples.

```bash
# Build, validate, and (after approval) package the local corpus.
make corpus-curate
make corpus-validate
make corpus-coverage
make corpus-export
make corpus-package VERSION=0.1.0

# Underlying CLI commands.
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate-sources corpus/sources.json
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py curate corpus/sources.json corpus/local/corpus --overwrite
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py verify-build corpus/local/corpus
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py coverage corpus/local/corpus corpus/questions.json --output corpus/local/coverage.json
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py export corpus/local/corpus corpus/local/runtime-corpus.json
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate corpus/local/corpus/captured --require-approved
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py package corpus/local/corpus corpus/local/release --version 0.1.0

# Capture or refresh hand-prepared inputs named by a pinned local manifest.
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py capture /path/to/capture-manifest.json /path/to/current-corpus
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py refresh /path/to/current-corpus /path/to/capture-manifest.json /path/to/candidate-corpus
```
