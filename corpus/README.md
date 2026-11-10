# Corpus curation scope

`sources.json` is the human-owned, approved acquisition scope for official E3SM
documentation. It is not the capture manifest consumed by
`backend/scripts/corpus.py`. Selected documents approve acquisition only, not
capture fidelity, scientific correctness, or publication; an empty document
list means no selection for that source.

For capture, derive a separate local capture manifest from this scope. That
file-backed manifest names selected local inputs and pins each upstream revision
before it is passed to the curation CLI. Before publication, each selected
document requires that manifest, a raw snapshot, normalization, and reviewer
approval. Keep the two manifest types and acquisition outputs separate:

```text
corpus/
  sources.json          # human-owned approved scope (tracked)
  local/                # git-ignored operator-local captures; not a backup
    <capture>/
      raw/              # unchanged upstream files and acquisition records
      prepared/         # curator-prepared Markdown inputs
      provenance.json   # raw-to-prepared provenance
      capture-manifest.json # strict pinned manifest for the curation CLI
      captured/         # CLI output: content, snapshot, catalog, review
```

See [corpus curation](../docs/dev/corpus-curation.md) for the offline workflow.
