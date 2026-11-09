# Corpus curation

Acquisition and local capture have no runtime impact. Tests and CI perform no
live source checks.

The human-owned approved scope is
[`corpus/sources.json`](../../corpus/sources.json). It records approved sources,
license references, rate limits, path scopes, and selected documents. An empty
document list means no selection for that source. A selected document approves
acquisition only, not capture fidelity, scientific correctness, or publication.
Keep local capture outcomes separate from this policy.

This source scope is not the manifest accepted by `backend/scripts/corpus.py`.
For each capture, an operator derives a separate local capture manifest from the
scope. The capture manifest is file-backed: it selects local input files and
pins the upstream revision and source metadata for every selected document.
Do not pass `corpus/sources.json` to `capture` or `refresh`.

## Workflow

1. **Acquire and prepare:** acquire only selected pinned files within the source
   scope, respecting request intervals. Retain raw originals and prepare Markdown
   as described below. Stop for approval if a required include is outside selection.
2. **Capture:** derive a separate pinned local capture manifest from the scope
   and prepared inputs. Save inputs, provenance, and resulting artifacts outside Git.
3. **Offline refresh:** use the saved snapshot and another local, pinned capture
   manifest to write a separate candidate corpus; do not fetch live URLs.
4. **Reviewer approval:** verify source identity, pinned revision, license and
   attribution requirements, scope, and normalized content. Record approval in
   the generated review artifact.
5. **Validate:** validate manifest JSON and offline snapshot/Markdown metadata;
   do not fetch sources during validation.

Do not publish a document without a pinned revision, raw snapshot, normalized
copy, and reviewer approval.

## Raw retention and preparation

Use an operator-local directory outside the repository with `raw/`, `prepared/`,
`capture-manifest.json`, `provenance.json`, and a separate captured corpus root.
Retain acquisition/preparation scripts there when needed for reproduction. Record
the exact location and commands in the capture report; temporary storage is not
a durable archive.

Save complete upstream response bodies unchanged, including license/notice
companions. Record byte length, SHA-256, repository/owner, repository-relative
path, canonical documentation URL, pinned file URL and revision, UTC acquisition
time, HTTP result, access constraints, and applicable license references. Where
available, verify response bytes against the pinned Git blob identity. A Git blob
hash is not a raw SHA-256 or a package artifact hash.

Prepare selected sections, not unrelated repository content:

- Convert RST headings, inline markup, references, lists, tables, and admonitions
  to Markdown. Preserve heading hierarchy and warning/notice text.
- Fence commands, scripts, configuration, and recipe excerpts. Preserve indentation,
  line continuations, ordering, placeholders, comments, and table cell content.
- Resolve relevant `include` and `literalinclude` content at the same pinned
  revision. Record included paths and line/section selections; do not fetch links
  or datasets merely because a page references them.
- Record raw-to-prepared paths, selected source line ranges/headings, omissions,
  link rewrites, annotations, preparation method/tool version, and prepared hashes.
  Label curator notes separately; never silently fix upstream commands or claims.
- Keep release content distinct from development content. Record upstream commits,
  feedstock revisions, and package versions/builds/hashes separately. Declared
  dependencies do not establish a solved environment or machine compatibility.
- Record example validation as unexecuted unless separate execution evidence
  exists. Do not run upstream examples, install environments, or submit HPC jobs
  during capture. Keep site-specific settings separate for each proposed machine.

The CLI accepts local UTF-8 inputs as Markdown; it does not fetch or convert RST,
retain raw originals, or verify scientific correctness. It normalizes CRLF/CR to
LF, removes trailing spaces/tabs on each line, and writes one final newline.
Leading indentation and internal whitespace remain intact. Check whether trailing
spaces have semantic meaning before capture, including Markdown hard breaks.

Keep the strict capture manifest separate from both the acquisition scope and a
richer local `provenance.json`; the manifest rejects unknown fields. It contains
`schema_version` and `sources`; each source has `id`, `url`, `revision`,
`license`, `policy`, `content_path`, and optional `title`. Capture IDs must match
`[A-Za-z0-9][A-Za-z0-9_.-]*`, and `content_path` is relative to the manifest.
Capture rejects floating revisions such as `main` or `master` and duplicate IDs
or URLs; validation also rejects duplicate normalized content. Capture writes
`content/<id>.md`, `snapshot.json`, `catalog.json`, and `review.json`. Do not
rename existing runtime citation IDs as part of capture.

## Integrity, fidelity, and publication

Operator-local integrity checks, not repository tooling, verify raw byte hashes,
pinned blob identities, selected path policy, and raw/prepared/captured file
correspondence. The offline CLI validator checks record metadata, safe content
paths, normalized hashes, duplicate records, catalog consistency, and hash-bound
review artifacts. It does not verify source scope membership, raw acquisition,
RST conversion, scientific accuracy, or answer coverage.

Manually compare prepared and captured content with the selected raw sections.
Check headings, command/configuration blocks, warnings, tables, resolved includes,
omissions, and citation targets. Record fidelity findings and remaining question
gaps separately from automated checks. Passing checks never grants review
approval or publication.

Leave generated `review.json` with `approved: false` until an authorized reviewer
approves the hash-bound snapshot. Confirm ordinary validation passes and
`--require-approved` rejects the unapproved snapshot. Publication requires separate
authorization and retained license/notice companions.

Keep the packaged runtime corpus format, a JSON array in `curated_corpus.json`,
unchanged. The CLI does not export runtime entries; runtime integration and
structure-preserving chunking need separate work.
Defer JSONL migration and GitHub Release automation until a reviewed baseline exists.

## Commands

Run these from the repository root. Paths below are operator-local examples.

```bash
# Validate the checked-in human-owned source scope.
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate-sources corpus/sources.json

# Capture selected local files named by a pinned local capture manifest.
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py capture /path/to/capture-manifest.json /path/to/current-corpus

# Build a separate offline candidate from a current snapshot and local manifest.
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py refresh /path/to/current-corpus /path/to/capture-manifest.json /path/to/candidate-corpus

# Validate corpus artifacts and require hash-bound reviewer approval.
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate /path/to/candidate-corpus
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate /path/to/candidate-corpus --require-approved
```
