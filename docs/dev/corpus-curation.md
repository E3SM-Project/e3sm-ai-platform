# Corpus curation

Curation builds a local E3SM knowledge corpus from documentation pinned in
[`corpus/sources.json`](../../corpus/sources.json). What the corpus contains is
summarized in [`corpus/README.md`](../../corpus/README.md).

Builds have no runtime effect unless you opt in with `CORPUS_PATH`. Only
`make corpus-curate` uses the network; tests and CI stay offline. Selecting a
document in the scope approves acquisition only, not correctness or publication.

## Workflow

Run from the repository root.

| Step | Command | Result |
| --- | --- | --- |
| 1. Curate | `make corpus-curate` | Downloads every selected file at its pinned revision and builds `corpus/local/corpus/`. Set `GITHUB_TOKEN` to avoid GitHub API rate limits. |
| 2. Validate | `make corpus-validate` | Rechecks the scope and the build offline. |
| 3. Coverage | `make corpus-coverage` | Reports which expected documents each [representative question](../../corpus/questions.json) retrieves and cites. |
| 4. Review | [Review checklist](corpus-review.md) | An authorized reviewer sets `approved` in `captured/review.json`. Curation never approves. |
| 5. Package | `make corpus-package VERSION=<label>` | Writes a deterministic local archive and `.sha256` for an approved build. Never uploads. |

Optional: `make corpus-export` writes the build for the backend
([runtime use](#runtime-use)).

A failed build leaves the previous one unchanged; timeouts and server errors are
retried up to three times. `corpus/local/` is git-ignored and is not a backup.
The underlying CLI is `backend/scripts/corpus.py`; run it with `--help` for
subcommands, including `capture` and `refresh` for hand-prepared manifests.

## Source scope format

`sources.json` (`manifest_version` 2) sets a shared `request_interval_seconds`
and lists sources. Each source is one GitHub repository at one pinned commit:

| Field | Meaning |
| --- | --- |
| `id`, `identity`, `owner`, `repository_url`, `canonical_url` | Source identity; `canonical_url` is optional. |
| `revision` | Pinned commit. Branch names such as `main` are rejected. Use a separate source for another revision. |
| `release` | Human-readable version label, such as `v3.1.0`. |
| `redistribution` | Terms recorded on every captured document. |
| `include`, `exclude` | Optional glob patterns, such as `docs/**/*.md`; `**` spans folders. |
| `documents` | Explicit files: `id`, `path`, and optional `role`, `lines`, `notes`. |
| `license_url` | Only when the source has no `license` document. |

- **Pattern-selected files** get IDs `<source>.<path>` with `/` replaced by `.`,
  for example `cime.doc.source.ccs.timers.rst`. The file list comes from the
  GitHub tree API at the pinned commit, so selection is reproducible.
- **Explicit documents** add files outside the patterns, or attach `notes` to a
  pattern-selected path (the explicit ID wins).
- **`role: "license"`** keeps a file with the build without making it searchable.
- **`lines`** captures only inclusive 1-based ranges, such as
  `[[14, 21], [19685, 21956]]`, from very large files. Include any license
  notice the excerpt must carry.
- **`notes`** record caveats about misleading or unverified upstream content.

Which questions use each document is recorded in `corpus/questions.json`, not
in the scope.

## How documents are captured

Text stays verbatim; nothing is converted. Each captured document starts with a
title and a provenance line (pinned URL, revision, owner, license, any line
ranges), followed by the upstream text:

- Markdown is used as-is.
- Other formats (RST, XML, YAML, scripts, Texinfo) are wrapped in a code fence
  longer than any backtick run in the text.
- Includes are not resolved. `curate` reports RST includes that point outside
  the corpus, and `acquisition.json` records them as `unresolved_includes`.

Never run upstream examples, install environments, or submit HPC jobs during
curation.

## What validation guarantees

`make corpus-validate` checks, offline, that:

- the scope has pinned revisions, safe IDs and paths, no duplicate IDs, and a
  license reference for every source;
- every raw file matches the byte length and SHA-256 in `acquisition.json`;
- every captured document contains its raw text, or each selected line range,
  unchanged;
- the capture artifacts and the hash-bound `review.json` are consistent.

It does not check scientific accuracy or retrieval quality, and passing never
approves a build. `validate --require-approved` fails until a reviewer approves.

## Question coverage

`corpus/questions.json` maps each representative question to the documents that
should support it; tests check that each one is selected in the scope.

`make corpus-coverage` answers each question with the application's own
chunking, lexical retrieval, and deterministic generation (no LLM, no network):

- **Top 8:** an expected document counts as retrieved if any of its chunks is
  among the 8 highest-ranked chunks.
- **Cited:** an expected document counts as cited if one of the 4 chunks cited
  in the answer comes from it.

The report (`corpus/local/coverage.json`) is a baseline, not a pass/fail check;
retrieval evaluation is #21.

## Runtime use

The backend serves the packaged `curated_corpus.json` unless `CORPUS_PATH` names
another corpus. To try a build in the API and UI:

```bash
make corpus-export   # writes corpus/local/runtime-corpus.json
```

Then set `CORPUS_PATH` to that file's absolute path in `backend/.env`. Exporting
does not approve anything. `/health` reports the loaded corpus's `snapshot_id`,
and query traces carry it as `rag.corpus_snapshot_id`.

The evaluation adapter always uses the packaged corpus because its fixtures cite
packaged source IDs. Replacing the packaged corpus requires review approval and
updated fixtures.
