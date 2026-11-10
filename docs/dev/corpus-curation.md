# Corpus curation

Curation and local builds have no runtime impact. Only `curate` uses the network;
tests and CI perform no live source checks.

The human-owned approved scope is
[`corpus/sources.json`](../../corpus/sources.json). It records approved sources,
license references, rate limits, path scopes, and selected documents. An empty
document list means no selection for that source. A selected document approves
acquisition only, not capture fidelity, scientific correctness, or publication.
Keep local build outcomes separate from this policy.

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
3. **Review:** an authorized reviewer checks the build and records approval in
   `captured/review.json`. Never set approval as part of curation.
4. **Package:** `make corpus-package VERSION=<label>` archives an approved build
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
repository path, pinned revision and URL, raw URL, license URL, access and
redistribution terms, selection provenance, byte length, SHA-256, Git blob SHA-1,
and UTC acquisition time. It also records the SHA-256 of the scope that selected
the files. A Git blob hash is not a raw SHA-256 or a package artifact hash.

## Preparation

Curation keeps upstream text verbatim; it does not convert formats or select
sections. Section notes in a document's scope `provenance` describe which parts
answer a question; the whole file is still captured. Each prepared document starts with a title and a provenance line
(source URL, revision, owner, and license), followed by the upstream text:

- Markdown files are used as-is.
- Other formats, including RST, Texinfo, XML, YAML, configuration, and scripts,
  are fenced with a language tag. The fence is longer than any backtick run in
  the text, so the upstream text is never altered.
- Files named `LICENSE*`, `NOTICE*`, or `COPYING*` are kept as raw companions and
  are not captured as content.
- Includes are not resolved. Select each needed file, such as an included
  configuration, as its own document.

Capture normalizes CRLF/CR to LF, removes trailing spaces and tabs on each line,
and writes one final newline. Leading indentation and internal whitespace remain
intact. Format conversion and structure-preserving chunking are deferred.

Keep release content distinct from development content. Record upstream commits,
feedstock revisions, and package versions/builds/hashes separately. Declared
dependencies do not establish a solved environment or machine compatibility.
Never execute upstream examples, install environments, or submit HPC jobs during
curation. Record caveats about misleading upstream content in the selected
document's `provenance` in the scope.

The capture manifest contains `schema_version` and `sources`; each source has
`id`, `url`, `revision`, `license`, `policy`, `content_path`, and optional
`title`, and the manifest rejects unknown fields. Capture IDs must match
`[A-Za-z0-9][A-Za-z0-9_.-]*` and be unique across sources. Capture rejects
floating revisions such as `main` or `master` and duplicate IDs or URLs;
validation also rejects duplicate normalized content. Do not rename existing
runtime citation IDs as part of capture.

## Integrity, review, and publication

`curate` rejects documents outside their source's path scope, URLs that do not
match the repository and revision, and non-GitHub repositories. `verify-build`,
run by `curate` and `corpus-validate`, checks offline that:

- raw byte lengths and SHA-256 values match `acquisition.json`;
- each captured document contains its normalized raw text unchanged;
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

Keep the packaged runtime corpus format, a JSON array in `curated_corpus.json`,
unchanged. The CLI does not export runtime entries; runtime integration needs
separate work.

## Commands

Run these from the repository root. Paths other than the `make` defaults are
examples.

```bash
# Build, validate, and (after approval) package the local corpus.
make corpus-curate
make corpus-validate
make corpus-package VERSION=0.1.0

# Underlying CLI commands.
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate-sources corpus/sources.json
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py curate corpus/sources.json corpus/local/corpus --overwrite
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py verify-build corpus/local/corpus
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate corpus/local/corpus/captured --require-approved
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py package corpus/local/corpus corpus/local/release --version 0.1.0

# Capture or refresh hand-prepared inputs named by a pinned local manifest.
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py capture /path/to/capture-manifest.json /path/to/current-corpus
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py refresh /path/to/current-corpus /path/to/capture-manifest.json /path/to/candidate-corpus
```
