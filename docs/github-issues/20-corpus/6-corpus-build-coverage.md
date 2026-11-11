# Issue #20: Reproducible corpus build and question coverage

## Scope and result

Build date: 2026-11-10. Repository baseline: `3f6f29d`; the later download-retry
fix (`268a0fe`) does not change build output.

The operator approved candidates for all 18 [representative questions][questions]
on 2026-11-10 ([source mapping][scope-approval]). `make corpus-curate` built a
local corpus from every selected document in [`corpus/sources.json`][scope]:

| Measure | Result |
| --- | ---: |
| Repositories | 16 |
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

`make corpus-coverage` runs each question in [`corpus/questions.json`][question-set]
through the application's own chunking, lexical retrieval, routing, and
deterministic generation with default settings: no model provider and no network.
It uses one corpus entry per captured document. The shipped-corpus column below
came from a one-off local comparison against the packaged 31-entry
`curated_corpus.json`; the command reports only the build.

Expected documents for each question are the selected documents linked from that
question's section of the [source mapping][mapping], matched by pinned URL and
recorded in `corpus/questions.json`; 81 question–document pairs in total. “Top 8” counts distinct documents among the
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

## Follow-up: trimming and runtime use

Two #20 follow-ups after these results:

- **Trimmed oversized files.** Scope documents can now select verbatim line ranges.
  The NCO manual captures its copyright and GFDL notice and the `ncclimo` section
  (1.4 MB to 106 KB); the EAM namelist definitions capture their attribute header
  and the history-output group (293 KB to 26 KB). Retrieval chunks fell from 4,060
  to 1,176. The manual now appears off-target for one question instead of four.
  Expected documents in the top 8 rose only from 29 to 30 of 81, and 12 of 18
  questions still cite an expected document. The remaining misses are retrieval
  and chunking problems, not corpus size.
- **Opt-in runtime use.** `make corpus-export` writes the build as a runtime corpus,
  and `CORPUS_PATH` makes the backend serve it. The packaged corpus stays the
  default, and the evaluation adapter always uses it because the evaluation
  fixtures cite its source IDs.

## Expansion to documentation folders

Build date: 2026-11-10. Scope commits: `fe2ec6f` (pattern support), `c6b3a85`
(expansion), `8d39017` (explicit-entry cleanup).

### What changed

- **Folder patterns** now select all Markdown and RST documentation in E3SM
  (`docs/` and component `docs/`, excluding legacy CICE and `old/` folders), CIME,
  e3sm_diags, zppy, MPAS-Analysis, e3sm-unified, xCDAT (excluding project pages),
  E3SM Data Docs, and the running-guide site.
- **Four new sources** at their E3SM-Unified 1.13.0 versions: zstash, e3sm_to_cmip,
  mache, and MPAS-Tools.
- **Explicit additions:** the `pm-cpu` and `chrysalis` sections of E3SM's machine
  and batch configuration, and the NCO manual's `ncremap` section.
- **Cleanup:** 16 explicit entries already selected by patterns were removed, and
  their IDs in `corpus/questions.json` were replaced by pattern-derived IDs.

### Build

| Measure | Before | After |
| --- | ---: | ---: |
| Files acquired | 85 | 565 |
| Documents captured | 65 | 539 |
| Selected by patterns | — | 488 |
| Captured text | about 1 MB | 3.95 MB |
| Retrieval chunks | 1,176 | 5,902 |
| Build time | about 2 min | about 12 min |
| RST includes outside the corpus | — | 9 |

The 9 unresolved includes are zppy configuration files, MPAS-Analysis observation
tables generated at documentation build time, and xCDAT text and changelog files
outside the selected folders. None was added.

### Coverage

The comparison spans both the expansion and the ID renames; renaming does not
change which documents are expected, so the difference comes from the expansion.
The metric counts only documents mapped before the expansion, so it does not
credit relevant new pages.

| Build | Documents | Expected documents in top 8 | Questions citing an expected document |
| --- | ---: | ---: | ---: |
| Before expansion | 65 | 30 / 81 | 12 / 18 |
| After expansion | 539 | 17 / 81 | 10 / 18 |
| After, without developer docs | 440 | 17 / 81 | 9 / 18 |

Off-target citations come mostly from E3SM component docs (16 of 51, led by
EAMxx user and developer pages), MPAS-Analysis (7, including developer
tutorials), and explicit documents (7). Some displaced results are relevant new
pages, such as CIME's case-control index and multi-year example for
`running-case-setup` and E3SM-Unified's introduction and tool guide for
`tools-environment-choice`; others are noise, such as EAMxx developer pages for
`user-guide-compset`.

### Caveat scan

An automated scan of all 539 documents found 846 hits in 120 documents for
content that may be outdated or apply only to specific sites. Twenty of those
documents already have notes; 100 do not.

| Pattern | Hits | Documents without notes |
| --- | ---: | ---: |
| Machine paths | 504 | 52 |
| `master`, `main`, or `load_latest` references | 279 | 75 |
| Accounts, queues, or partitions | 36 | 15 |
| `module` commands | 21 | 7 |
| Disabled TLS verification | 6 | 2 |

Only the disabled-TLS advice is unsafe. The two documents that repeat the advice
already flagged in `diags-install`, `zppy.docs.source.getting_started.rst` and
`zstash.docs.source.getting_started.rst`, now carry notes. The other hits are
accepted as-is: the content is public upstream documentation at pinned
revisions, answers cite it, and refreshing sources is #31's work.

### Conclusion

Coverage numbers measure whether lexical retrieval finds the documents mapped to
each question, not whether answers are complete; every question remains partial
in the [source mapping][mapping]. The expansion makes the corpus cover the
E3SM documentation sets instead of hand-picked pages, but with eight times as
many documents, lexical retrieval ranks mapped evidence lower: expected documents
in the top 8 fell from 30 to 17 of 81. Fixing ranking and chunking is #21 work;
narrowing the corpus would trade breadth for this metric.

**Developer docs stay.** Removing them did not improve retrieval (17/81 either
way) and lowered questions citing expected documents from 10 to 9.

## Ingestion method

Pinned Git acquisition is the ingestion method for this corpus: every selected
source is a public GitHub repository, so files are fetched at exact commits with
byte hashes and no crawling. Evaluating crawlers such as Crawl4AI, sitemap
discovery, and incremental updates for hosted documentation is deferred until a
needed source is not available from Git; refresh automation belongs to #31.

## Remaining issues

- [ ] Reviewer approval of the build using the
  [review checklist](../../dev/corpus-review.md); then
  `make corpus-package VERSION=<label>`.
- [ ] Decide whether the reviewed build replaces the packaged corpus; that requires
  updated evaluation fixtures because their citations use packaged source IDs.
- [ ] Structure-aware chunking that respects headings and fenced blocks (#21), and
  shared indexes built from exported or packaged builds (#30).
- [ ] Retrieval evaluation against these questions with judged answers (#21),
  building on `corpus/questions.json` and `make corpus-coverage`.
- [ ] Publication terms: NCO's GFDL documentation license and E3SM Data Docs'
  unstated documentation terms ([source mapping][scope-approval]).
- [ ] Machine settings for Chrysalis LCRC and Perlmutter CPU remain unverified;
  no upstream example, build, or HPC job was run.

## Reproduction

```bash
make corpus-curate
make corpus-validate
make corpus-coverage
```

A second independent build produced identical raw files, capture manifest,
captured content, and snapshot; only `acquisition.json` timestamps differ.

[questions]: 2-representative-questions.md
[mapping]: 3-source-mapping.md
[scope-approval]: 3-source-mapping.md#approved-18-question-scope
[pilot]: 5-capture-pilot.md
[question-set]: ../../../corpus/questions.json
[scope]: ../../../corpus/sources.json
[workflow]: ../../dev/corpus-curation.md
