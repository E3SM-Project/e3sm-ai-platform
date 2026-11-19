# Synthetic evaluation questions

[`corpus/questions.json`](../../corpus/questions.json) holds 100 generated
questions for the retrieval and answer baseline defined in
[scoring.md](scoring.md): 80 answerable and 20 should-refuse. All were written
from the curated corpus for #37.

A person reviewed the 16 questions the model flagged (see
[Process](#process)). The rest are model-verified only; review a sample of
their expected documents before trusting baseline results.

## Fields

Each question has `id` (`syn-` prefix), `question`, and `expected_documents`,
plus:

| Field                         | Values                                                                                                     |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `feature`                     | `running-cases`, `model-components`, `diagnostics`, `analysis-tools`, `environment-tooling`, `data-access` |
| `scenario`                    | `single-document`, `multi-document`, `version-specific`, `troubleshooting`, `vague`, `should-refuse`       |
| `persona`                     | `new-user`, `analyst`, `model-developer`, `researcher`                                                     |
| `origin`                      | `synthetic-37`                                                                                             |
| `should_refuse`               | `true` when no corpus document answers; `expected_documents` is then empty                                 |
| `needs_review`, `review_note` | Set when the expected documents or the scenario fit are uncertain                                          |

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
and `verify-build` passes.

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
   and add 2 verified should-refuse candidates.

In total, 169 candidates (150 initial, 3 added in round 2, and 16 written in
the coverage fill) produced the final 100: 80 answerable and 20 should-refuse.

| Step | Checks | Changes |
| --- | --- | --- |
| Round 1 | Generate, verify, select by grid balance, persona realism, verified documents, and no near-duplicates | Selected 64 answerable and 18 should-refuse questions from the 150 candidates |
| Round 2 | Re-read every expected passage; corpus-wide text search for other answering documents; re-search refusals; grid gaps | Added 6 documents to 5 questions; removed 1 document that only linked elsewhere (scenario changed to single-document); reworded 1 question to fit troubleshooting; replaced 1 question; replaced 3 questions with 3 new candidates to fill analysis-tools and data-access persona gaps; refusals unchanged |
| Round 3 | Near-duplicate scan (question wording and shared documents); recheck changes | Reworded 1 question that overlapped another; added 5 review flags. Stopped at the 3-round limit. |
| Fill | Same verification and near-duplicate scan | Added 16 answerable and 2 should-refuse questions, for 100 in total; added 1 document to an existing question; reworded 1 new question that overlapped another |
| Human review | The 16 flagged questions | Resolved all 16 flags: added expected documents to 2 questions, reworded 1 question, kept 3 near-miss refusals, and added answer expectations for 16 questions; added 2 corpus gaps; reported 2 upstream documentation issues ([e3sm_diags#1109](https://github.com/E3SM-Project/e3sm_diags/issues/1109), [e3sm-unified#159](https://github.com/E3SM-Project/e3sm-unified/issues/159)) |

Deliberate pairs remain: an answerable question next to a should-refuse near
miss on the same topic (for example, v3.LR citation versus v3.RRM citation,
and the conda-forge NCO version versus the hpc-variant NCO version).

## Final coverage

| Feature             | Single | Multi | Version | Trouble | Vague | Refuse | Total |
| ------------------- | ------ | ----- | ------- | ------- | ----- | ------ | ----- |
| running-cases       | 6      | 2     | 0       | 2       | 3     | 5      | 18    |
| model-components    | 5      | 3     | 3       | 3       | 3     | 4      | 21    |
| diagnostics         | 5      | 6     | 2       | 3       | 2     | 2      | 20    |
| analysis-tools      | 4      | 1     | 3       | 2       | 0     | 0      | 10    |
| environment-tooling | 6      | 3     | 2       | 3       | 3     | 4      | 21    |
| data-access         | 2      | 0     | 2       | 0       | 1     | 5      | 10    |
| Total               | 28     | 15    | 12      | 13      | 12    | 20     | 100   |

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

## Answer expectations

Some answers are correct only with a qualifier:

- `syn-running-chrysalis-queue-newuser`, `syn-running-pmcpu-paths-developer`:
  say the values come from the release's machine and batch XML, and to check
  current facility settings if needed.
- `syn-components-cmip7-compset-researcher`: describe `WCYCL1850-CMIP7` as
  defined in the release's compset XML (`e3sm-coupled-compsets`), not as
  validated or supported for CMIP7 production runs.
- `syn-environment-diags-install-newuser`,
  `syn-diagnostics-zppy-install-latest-analyst`,
  `syn-environment-zstash-dtn-newuser`: do not present disabling SSL
  verification as an install step. If mentioned, say the guide includes it for
  networks that intercept SSL, that it turns off certificate checking and is
  not recommended, and that users who hit SSL errors should ask their site
  administrators about configuring the site's certificate.
- `syn-tools-nco-unified-version-analyst`,
  `syn-environment-unified-versions-researcher`: give versions from
  `unified-recipe` and the package recipes (for example, NCO 5.3.9,
  e3sm_diags 3.2.0, zppy 3.2.0, MPAS-Analysis 1.15.0), not the `1.13.0rc1`
  pins in `e3sm-unified.docs.packages.md`.
- `syn-environment-unified-variants-developer`: say the 1.13.0 feedstock builds
  `nompi` and `hpc` (`unified-variants`), and that `hpc` omits system-library
  packages (such as NCO, MOAB, and TempestRemap) that the HPC deployment
  provides through Spack. Other docs mention `mpich` and `openmpi` variants; do
  not claim those builds exist for 1.13.0.
- `syn-components-elm-docs-vague-developer`: name the Developer Guide for code
  and the Technical Guide for the science. Note that the introduction says the
  Developer Guide explains data structures, but the captured Developer Guide
  covers only testing.
- `syn-diagnostics-diags-v2-to-v3-researcher`: say v3 replaced the CDAT back
  end with xarray and xCDAT and kept the run API backward-compatible. Do not
  claim v2 and v3 give identical numbers; the corpus does not document the
  v2-to-v3 regression testing or its tolerances.
- `syn-components-mpas-analysis-setup-researcher`: say the MPAS-Analysis docs
  state E3SM runs need no namelist or stream changes, and the E3SM MPAS-Ocean
  guide confirms monthly `timeSeriesStatsMonthly` output by default. Do not
  promise every task works unchanged. For standalone sea ice, give the
  analysis-member and stream settings from `mpas-seaice-setup`, and do not
  repeat its stale "not yet publicly released" statement.
- `syn-diagnostics-obs-data-vague-newuser`: give both Perlmutter observation
  paths, `/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/`
  (`diags-perlmutter-guide`) and
  `/global/cfs/cdirs/e3sm/e3sm_diags/obs_for_e3sm_diags/`
  (`e3sm_diags.docs.source.quickguides.quick-guide-general.rst`). Say the guides
  disagree and to check which path exists on Perlmutter; do not present either
  as confirmed. Reported upstream in
  [E3SM-Project/e3sm_diags#1109](https://github.com/E3SM-Project/e3sm_diags/issues/1109).
- Near-miss should-refuse questions: refuse, but it is fine to mention the
  nearby fact without treating it as the answer.
  - `syn-refuse-pmcpu-max-walltime-newuser`: `e3sm-batch` lists a 30-minute
    pm-cpu default that it says is not the limit.
  - `syn-refuse-hpc-nco-version-analyst`: the recipes pin NCO only for non-hpc
    variants.
  - `syn-refuse-ace-predictions-researcher`: the AI training overview links to
    ACE but does not document its use.

## Review list

No questions are flagged. To flag one, set `needs_review` to true and explain
why in `review_note`, then list it here with its expected documents.

## Corpus gaps

Realistic questions the corpus cannot answer:

- Current facility limits and accounts: maximum queue walltimes, and E3SM on
  machines beyond the `pm-cpu` and `chrysalis` XML excerpts (for example,
  Frontier).
- Measured throughput (SYPD) for standard configurations.
- e3sm_diags v2-to-v3 regression-testing results and tolerances.
- MPAS-Ocean and MPAS-Seaice default analysis-member and stream settings in
  E3SM v3.1.0. No MPAS document lists them; the namelist defaults and streams
  templates are not captured.
- Scientific results, such as E3SMv3 climate sensitivity.
- E3SM's own domain-file generation page (linked from the grid guide, not
  captured) and EAMxx case setup (the captured page is only a heading).
- Land-ice (MALI) configuration such as calving, MARBL ocean biogeochemistry,
  and FATES parameter files and PFTs (the corpus only links to external FATES
  docs).
- CMIP7 conversion with e3sm_to_cmip; only CMIP7 compsets are present.
- The NCO version in the hpc Unified variant (provided by Spack), and
  releases after E3SM-Unified 1.13.0.
- ACE documentation: not ingested; the corpus only links to the ACE repository.
- The SCREAMv1 AI dataset release and the v3.RRM citation (upstream lists both
  as coming soon or TBD).
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
