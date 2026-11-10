# Issue #20: Reproducible corpus build and question coverage

## Scope and result

Build date: 2026-11-10. Repository baseline: `3f6f29d`; the later download-retry
fix (`268a0fe`) does not change build output.

The operator approved candidates for all 18 [representative questions][questions]
on 2026-11-10 ([source mapping][scope-approval]). `make corpus-curate` built a
local corpus from every selected document in [`corpus/sources.json`][scope]:

| Measure | Result |
| --- | ---: |
| Sources | 16 |
| Files acquired at pinned revisions | 85 |
| Documents captured | 65 |
| License and notice companions kept raw only | 20 |
| Build size | 8.1 MB |
| Retrieval chunks with the current chunker | 4,060 |
| Build time, including 1 s request intervals | 1 min 45 s |

All 65 documents are verbatim upstream text: Markdown as-is, other formats fenced
under a provenance header ([workflow]). `make corpus-validate` passes;
`validate --require-approved` fails because review is not approved. Nothing was
reviewed, published, packaged, or integrated into the runtime corpus.

The build supersedes the [hand-prepared pilot][pilot]. Its six files are
byte-identical (SHA-256 and Git blob) to the pilot's independently verified
downloads; the hand-converted Markdown is not used.

## Coverage method

A local script (`corpus/local/coverage/coverage.py`, git-ignored) runs each
question through the application's own chunking, lexical retrieval, routing, and
deterministic generation with default settings: no model provider and no network.
It compares two corpora:

- **New:** the 65 captured documents, one corpus entry per document.
- **Shipped:** the packaged 31-entry `curated_corpus.json`.

Expected documents for each question are the selected documents linked from that
question's section of the [source mapping][mapping], matched by pinned URL; 81
question–document pairs in total. “Top 8” counts distinct documents among the
eight highest-ranked chunks. Citations come from the default top-4 answer.

This measures whether retrieval surfaces the mapped evidence. It does not judge
answer correctness, and the expected sets include some context-only documents.

## Results

| Question | Expected | In top 8 | Expected cited / cited | Shipped corpus route |
| --- | ---: | ---: | --- | --- |
| `model-components` | 6 | 2 | 1 / 3 | curated |
| `eam-eamxx-mixed` | 4 | 2 | 1 / 2 | curated |
| `model-science-configurations` | 3 | 2 | 0 / 1 | insufficient evidence |
| `tutorial-first-run` | 4 | 1 | 1 / 4 | curated |
| `tutorial-diagnostics-example` | 4 | 2 | 1 / 2 | curated |
| `tutorial-version-migration` | 4 | 0 | 0 / 4 | curated |
| `tools-atmosphere-ocean` | 4 | 0 | 0 / 4 | curated |
| `tools-nco-xcdat` | 5 | 2 | 1 / 3 | curated |
| `tools-environment-choice` | 5 | 3 | 3 / 3 | curated |
| `user-guide-compset` | 3 | 1 | 0 / 3 | curated |
| `running-case-setup` | 4 | 3 | 2 / 3 | curated |
| `user-guide-history` | 3 | 2 | 1 / 1 | curated |
| `diagnostics-zppy-climatology` | 7 | 2 | 1 / 3 | curated |
| `diagnostics-qbo-inputs` | 6 | 1 | 0 / 2 | curated |
| `diagnostics-missing-plots` | 3 | 3 | 1 / 2 | curated |
| `cross-project-mpas-output` | 7 | 0 | 0 / 3 | curated |
| `cross-project-reproduce-campaign` | 6 | 1 | 1 / 4 | curated |
| `cross-project-result-comparability` | 3 | 2 | 1 / 3 | insufficient evidence |
| **Total** | **81** | **29** | | |

## Findings

- **Source coverage is complete; retrieval coverage is not.** Every mapped
  document is in the corpus, and every question now gets a curated answer with
  citations. The shipped corpus returns insufficient evidence for two. But only
  29 of 81 expected documents rank in the top 8, and six questions cite no
  expected document.
- **Misses follow vocabulary.** `cross-project-mpas-output` retrieves no
  MPAS-Analysis document even though the question names it, and
  `tools-atmosphere-ocean` retrieves neither e3sm_diags defaults nor the MPAS SST
  task. `tutorial-version-migration` retrieves neither configuration guide.
- **Large whole files add noise.** The 1.4 MB NCO manual appears in the top 8 for
  four questions that do not need it and is cited for two of them. `diags-examples`, the EAM user
  guide, and the Perlmutter quick guide are the most frequent off-target citations.
- **The chunker flattens structure.** It splits on sentences into 90-word chunks
  and joins words with single spaces, so commands, configuration, and code lose
  their line breaks and fenced files are split mid-block.
- **Clear successes:** `running-case-setup`, `tools-environment-choice`,
  `user-guide-history`, and `diagnostics-missing-plots` retrieve and cite their
  mapped evidence.

These are retrieval and chunking results, not missing-source results. Adding
more documents would not fix them and could add noise.

## Remaining issues

- [ ] Reviewer approval of the build; then `make corpus-package VERSION=<label>`.
- [ ] Runtime integration: convert captured records to runtime entries without
  renaming existing citation IDs.
- [ ] Structure-aware chunking that respects headings and fenced blocks, and
  section selection or splitting for very large files (#30).
- [ ] Retrieval evaluation against these questions with judged answers (#21).
  The coverage script could become a repository command if useful.
- [ ] Publication terms: NCO's GFDL documentation license and E3SM Data Docs'
  unstated documentation terms ([source mapping][scope-approval]).
- [ ] Machine settings for Chrysalis LCRC and Perlmutter CPU remain unverified;
  no upstream example, build, or HPC job was run.

## Reproduction

```bash
make corpus-curate
make corpus-validate
uv run --package e3sm-ai-platform-backend python -I corpus/local/coverage/coverage.py \
    corpus/local/corpus docs/github-issues/20-corpus corpus/local/coverage
```

A second independent build produced identical raw files, capture manifest,
captured content, and snapshot; only `acquisition.json` timestamps differ.

[questions]: 2-representative-questions.md
[mapping]: 3-source-mapping.md
[scope-approval]: 3-source-mapping.md#approved-18-question-scope
[pilot]: 5-capture-pilot.md
[scope]: ../../../corpus/sources.json
[workflow]: ../../dev/corpus-curation.md
