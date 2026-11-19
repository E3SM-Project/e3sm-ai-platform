# Synthetic evaluation questions

[`corpus/questions.json`](../../corpus/questions.json) holds 100 generated
questions for the retrieval and answer baseline defined in
[scoring.md](scoring.md): 80 answerable and 20 should-refuse. All were written
from the curated corpus for #37.

The questions are not human-verified. Review the expected documents before
trusting baseline results (see [Review list](#review-list)).

## Fields

Each question has `id` (`syn-` prefix), `question`, and `expected_documents`,
plus:

| Field | Values |
| --- | --- |
| `feature` | `running-cases`, `model-components`, `diagnostics`, `analysis-tools`, `environment-tooling`, `data-access` |
| `scenario` | `single-document`, `multi-document`, `version-specific`, `troubleshooting`, `vague`, `should-refuse` |
| `persona` | `new-user`, `analyst`, `model-developer`, `researcher` |
| `origin` | `synthetic-37` |
| `should_refuse` | `true` when no corpus document answers; `expected_documents` is then empty |
| `needs_review`, `review_note` | Set when the expected documents or the scenario fit are uncertain |

`make corpus-coverage` skips should-refuse questions.

## Framework

Dimensions follow Hamel Husain's
[test-data framework](https://hamel.dev/blog/posts/field-guide/#a-framework-for-generating-realistic-test-data),
adapted to the corpus:

- **Feature:** running cases (CIME, running-E3SM guide, machine and batch
  XML); model components (EAM, EAMxx, ELM, MOSART, MPAS-Ocean, MPAS-Seaice,
  data ocean); diagnostics (e3sm_diags, zppy, MPAS-Analysis); analysis tools
  (NCO, xCDAT); environment and tooling (E3SM-Unified, mache, zstash,
  e3sm_to_cmip, MPAS-Tools, feedstock recipes); data access (E3SM Data Docs).
- **Scenario:** answer in one document; answer across documents or projects;
  depends on a version; troubleshooting; vague or loosely worded; should
  refuse (out of scope, or in domain but undocumented, including near misses).
- **Persona:** new user on a first run, analyst running diagnostics, model
  developer, researcher reproducing or using published simulations. Wording
  ranges from jargon to plain, lowercase fragments.

## Process

Source: the local build `corpus/local/corpus-expanded` (539 documents). Its
`acquisition.json` `scope_sha256` matches the current `corpus/sources.json`,
and `verify-build` passes. `corpus/local/corpus` is an older 65-document build.

The model read documents directly. It did not use the application's
retrieval, `make corpus-coverage`, or the web.

1. **Generate.** For sampled feature × scenario × persona combinations, read
   the documents, then write one question as that persona would ask it.
   Started with one-document how-tos, then the other scenarios. Of 168
   drafts, 18 that repeated another draft's document and topic were dropped,
   leaving 150 candidates: 125 answerable and 25 should-refuse.
2. **Verify each candidate.** For each expected document, a pattern must
   match the passage that answers the question; the passage was read. For
   each should-refuse question, the corpus text was searched (`rg`) for its
   key terms. Every expected ID exists in the build manifest.
3. **Select and refine** over 3 rounds (below).
4. **Fill coverage.** Write 16 more answerable questions so every explicit
   content document in `sources.json` is expected by at least one question,
   and add 2 verified should-refuse candidates. These went through the same
   checks and a final near-duplicate scan.

| Round | Checks | Changes |
| --- | --- | --- |
| 1 | Generate, verify, select by grid balance, persona realism, verified documents, and no near-duplicates | 150 candidates → 82 selected (64 answerable, 18 should-refuse) |
| 2 | Re-read every expected passage; corpus-wide text search for other answering documents; re-search refusals; grid gaps | Added 6 documents to 5 questions; removed 1 document that only linked elsewhere (scenario changed to single-document); reworded 1 question to fit troubleshooting; replaced 1 question; replaced 3 questions with 3 new candidates to fill analysis-tools and data-access persona gaps; refusals unchanged |
| 3 | Near-duplicate scan (question wording and shared documents); recheck changes | Reworded 1 question that overlapped another; added 5 review flags. Stopped at the 3-round limit. |
| Fill | Same verification on 16 new answerable and 2 should-refuse questions | Added 18 questions; added 1 document to an existing question; reworded 1 new question that overlapped another |

Deliberate pairs remain: an answerable question next to a should-refuse near
miss on the same topic (for example, v3.LR citation versus v3.RRM citation,
and the conda-forge NCO version versus the hpc-variant NCO version).

## Final coverage

| Feature | Single | Multi | Version | Trouble | Vague | Refuse | Total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| running-cases | 6 | 2 | 0 | 2 | 3 | 5 | 18 |
| model-components | 5 | 3 | 3 | 3 | 3 | 4 | 21 |
| diagnostics | 5 | 6 | 2 | 3 | 2 | 2 | 20 |
| analysis-tools | 4 | 1 | 3 | 2 | 0 | 0 | 10 |
| environment-tooling | 6 | 3 | 2 | 3 | 3 | 4 | 21 |
| data-access | 2 | 0 | 2 | 0 | 1 | 5 | 10 |
| Total | 28 | 15 | 12 | 13 | 12 | 20 | 100 |

Personas: new-user 26, analyst 23, model-developer 27, researcher 24.

Empty cells: version-specific running cases, vague and should-refuse analysis
tools, and multi-document and troubleshooting data access.

## Verification limits

- The model wrote the questions, chose expected documents, and assigned all
  tags.
- A document counts as expected when a read passage answers the question.
  Other answering documents were found by keyword search, which can miss
  documents that use different words.
- Should-refuse questions were confirmed by keyword absence plus reading the
  closest hits. A different phrasing could still find a partial answer.
- Several documents are release snapshots: machine and batch XML, Unified
  package pins, and paths may not match current facilities.

## Review list

| Question | Note |
| --- | --- |
| `syn-running-chrysalis-queue-newuser` | Answer comes from release-defined batch XML, not current facility settings. |
| `syn-running-pmcpu-paths-developer` | Answer comes from release-defined machine XML, not current facility settings. |
| `syn-running-domain-files-developer` | E3SM's grid guide links a domain-file page that is not in the corpus; only the generic CIME `gen_domain` description answers. |
| `syn-components-cmip7-compset-researcher` | Compset XML entries are not scientific validation. |
| `syn-components-eamxx-support-researcher` | `e3sm-eamxx-cases` has only a heading and one sentence; it names the topic but does not explain case setup. |
| `syn-components-elm-docs-vague-developer` | `e3sm-elm-introduction` is placeholder text that only links to the guides. |
| `syn-components-mpas-analysis-setup-researcher` | Source notes: the E3SM default-output claim is unverified for v3.1.0, and the sea-ice page has a stale release statement. |
| `syn-diagnostics-obs-data-vague-newuser` | The general quick guide and the Perlmutter guide give different Perlmutter observation paths. |
| `syn-diagnostics-diags-v2-to-v3-researcher` | API compatibility is not numerical equivalence; confirm the v2 page fits. |
| `syn-tools-nco-unified-version-analyst` | `e3sm-unified.docs.packages.md` lists NCO 5.3.6 for 1.13.0rc1; the recipe pins 5.3.9. |
| `syn-environment-unified-versions-researcher` | `e3sm-unified.docs.packages.md` shows 1.13.0rc1 pins that differ from the released recipe. |
| `syn-environment-unified-variants-developer` | The feedstock variant file lists only `nompi` and `hpc`; other docs describe `mpich` and `openmpi` variants. |
| `syn-environment-diags-install-newuser` | The page also advises disabling SSL verification; that advice must not be presented as guidance. |
| `syn-refuse-pmcpu-max-walltime-newuser` | The batch XML `walltimemax` for pm-cpu is documented as a default, not the limit; confirm refusal is intended. |
| `syn-refuse-hpc-nco-version-analyst` | Recipes pin NCO only for non-hpc variants; confirm no other source records the hpc NCO version. |
| `syn-refuse-ace-predictions-researcher` | The AI training overview links to ACE; confirm a link alone is not an answer. |

## Corpus gaps

Realistic questions the corpus cannot answer:

- Current facility limits and accounts: maximum queue walltimes, and E3SM on
  machines beyond the `pm-cpu` and `chrysalis` XML excerpts (for example,
  Frontier).
- Measured throughput (SYPD) for standard configurations.
- Scientific results, such as E3SMv3 climate sensitivity.
- E3SM's own domain-file generation page (linked from the grid guide, not
  captured) and EAMxx case setup (the captured page is only a heading).
- Land-ice (MALI) configuration such as calving, MARBL ocean biogeochemistry,
  and FATES parameter files and PFTs (the corpus only links to external FATES
  docs).
- CMIP7 conversion with e3sm_to_cmip; only CMIP7 compsets are present.
- The NCO version in the hpc Unified variant (provided by Spack), and
  releases after E3SM-Unified 1.13.0.
- ACE emulator usage, the SCREAMv1 AI dataset release, and the v3.RRM citation
  (upstream lists the last two as coming soon or TBD).
- Whether zppy's `high_res_v1` campaign works on Perlmutter (upstream TODO).
- NERSC HPSS project quotas and PACE API access.

## Regenerate

1. Use a build whose `acquisition.json` `scope_sha256` matches
   `corpus/sources.json` (`shasum -a 256 corpus/sources.json`) and that passes
   `uv run --all-packages python backend/scripts/corpus.py verify-build <build> --scope corpus/sources.json`.
2. Read documents under `<build>/captured/content/`; IDs come from
   `<build>/capture-manifest.json`.
3. Follow the [process](#process): generate, verify against the text, select,
   refine for up to 3 rounds, and fill coverage so every explicit content
   document is expected.
4. Check the file loads:
   `make corpus-coverage CORPUS_BUILD=<build>`. Do not use its results to
   change questions.
5. Run `uv run --all-packages pytest backend/tests/test_corpus_coverage.py`.

The candidate pool and verification scripts were working files and are not
checked in.
