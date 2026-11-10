# Corpus curation scope

`sources.json` is the human-owned, approved acquisition scope for official E3SM
documentation: one entry per repository at a pinned revision, listing the selected
files. Selected documents approve acquisition only, not capture fidelity,
scientific correctness, or publication. See the
[scope format](../docs/dev/corpus-curation.md#source-scope-format).

`make corpus-curate` builds a local corpus from every selected document. It
derives its own pinned capture manifest; `sources.json` is never passed to
`capture` or `refresh`. Before publication, each document requires a raw
snapshot, normalization, and reviewer approval.

```text
corpus/
  sources.json          # human-owned approved scope (tracked)
  questions.json        # representative questions and expected documents (tracked)
  local/                # git-ignored; not a backup
    corpus/             # make corpus-curate output
      acquisition.json  # provenance and hashes for every acquired file
      raw/              # unchanged upstream files
      prepared/         # verbatim Markdown inputs
      capture-manifest.json
      captured/         # content, snapshot, catalog, review
    coverage.json       # make corpus-coverage report
    release/            # make corpus-package output (approved builds only)
```

See [corpus curation](../docs/dev/corpus-curation.md) for the workflow.
