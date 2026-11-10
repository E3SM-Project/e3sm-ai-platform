# Corpus curation scope

`sources.json` is the human-owned, approved acquisition scope for official E3SM
documentation. Selected documents approve acquisition only, not capture fidelity,
scientific correctness, or publication; an empty document list means no
selection for that source.

`make corpus-curate` builds a local corpus from every selected document. It
derives its own pinned capture manifest; `sources.json` is never passed to
`capture` or `refresh`. Before publication, each document requires a raw
snapshot, normalization, and reviewer approval.

```text
corpus/
  sources.json          # human-owned approved scope (tracked)
  local/                # git-ignored; not a backup
    corpus/             # make corpus-curate output
      acquisition.json  # provenance and hashes for every acquired file
      raw/              # unchanged upstream files
      prepared/         # verbatim Markdown inputs
      capture-manifest.json
      captured/         # content, snapshot, catalog, review
    release/            # make corpus-package output (approved builds only)
```

See [corpus curation](../docs/dev/corpus-curation.md) for the workflow.
