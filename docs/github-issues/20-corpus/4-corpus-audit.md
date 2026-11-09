# Issue #20: Existing-corpus audit

## Scope and conclusion

Audit date: 2026-11-09. Repository baseline:
`c03e6d2bffc86463273ef9c9f33450b26e156eb6`.

Audited [packaged corpus][corpus]:
`backend/src/e3sm_ai_platform/knowledge/data/curated_corpus.json`.
File SHA-256:
`be5b2ffe9cbf882ddb17c208fcd37236eb7893a998b2748f194c22ca64824a06`.

The corpus provides introductory context, not a reproducible evidence baseline
for the [18 representative questions][questions]: **0 sufficient, 9 partial,
9 absent**. All records lack pinned upstream versions and capture/review metadata.
Content coverage and provenance readiness are separate findings.

Records describe themselves as static excerpts curated for phase 1 tests. The
[loader] also uses this file as the runtime default; it is not exclusively a test
fixture. This audit inspects packaged text and metadata against the question
requirements and [source mapping][mapping]. It does not test retrieval, establish
upstream quotation fidelity, or check live URL availability.

## Inventory and provenance readiness

| Component label | Entries |
| --- | ---: |
| User Guide | 5 |
| Running E3SM | 8 |
| EAM | 3 |
| EAMxx | 3 |
| ELM | 4 |
| Diagnostics | 4 |
| E3SM-Unified | 4 |
| **Total** | **31** |

- All 31 `source_id` values are unique. There are 22 distinct exact URLs and
  20 after removing fragments. These are section records, not 31 captured documents.
- All records contain `source_id`, `title`, `url`, `section`, `component`,
  `version`, `authority`, `provenance`, and `text`; they pass the existing
  [CorpusEntry schema][models]. Schema validity is not evidence completeness.
- Every record sets `version` to `latest` and `authority` to `official`.
  Neither label establishes release applicability or review approval.
- No record stores an upstream commit/page revision, owner, acquisition date,
  access policy, license, raw-content hash, normalization configuration, or
  example-validation status. The provenance strings identify test-oriented
  curation, not exact source locations or extraction history.
- The [source scope][scope] lists four repositories with no selected documents.
  Its repository-level policies do not establish capture provenance for these entries.
- No bundled record links to a hash-bound capture/review artifact. The
  [capture schema][curation] provides revision/license/policy/content-hash fields,
  but its records are not interchangeable with runtime `CorpusEntry` records.
- Content consists of short prose summaries, not captured commands, worked
  examples, configuration blocks, or tables. The current chunker also rejoins
  whitespace; structure-preserving preparation alone would not guarantee runtime
  preservation of new code/configuration blocks. Record this downstream gap,
  rather than changing chunking in this audit.

**Provenance readiness: not established for any of the 31 entries.** Preserve
test compatibility while planning reviewed replacements; do not retroactively
attach release pins to summaries without verifying them against those sources.

## Question coverage

- **Sufficient:** Packaged text supports all expected elements for the declared context.
- **Partial:** It supports substantive answer elements, but leaves required content missing.
- **Absent:** It supplies no task-specific support beyond adjacent topics or navigation.

Related IDs below identify inspected entries, not guaranteed retrieval results.
“Adjacent” entries do not count as evidence for the requested task. Versions and
other provenance gaps above apply independently to every row. Generic environment
or provenance advice alone does not establish task-specific coverage.

| Question ID | Coverage | Related packaged `source_id` values | Missing answer elements |
| --- | --- | --- | --- |
| `model-components` | Partial | `eam:overview`, `elm:overview`, `user-guide:compsets` | MOSART, MPAS ocean/sea-ice roles and actual coupling exchanges; configuration-specific active/data behavior. |
| `eam-eamxx-mixed` | Partial | `eam:overview`, `eam:configuration`, `eamxx:overview`, `eamxx:configuration` | Release-specific scientific differences, available configurations, machine applicability, and support limits. |
| `model-science-configurations` | Absent | Adjacent: `elm:overview`, `elm-parameters` | Named configurations and their water/carbon capabilities, interactive versus prescribed processes, and validation limits. Generic process lists are insufficient. |
| `tutorial-first-run` | Partial | `running-guide:create-newcase`, `running-guide:case-setup`, `running-case-build`, `running-guide:run-and-submit` | A selected tutorial, concrete machine/account/data preparation, complete instructions, and observable completion checks. |
| `tutorial-diagnostics-example` | Partial | `diagnostics-run`, `diagnostics-parameters` | An identified example, files, data access, preprocessing, and runnable configuration. Existing text identifies parameter categories, input formats, and output types, not example-specific results. |
| `tutorial-version-migration` | Absent | Adjacent: `e3sm-unified:troubleshooting` | Version-pair API/dependency differences, tutorial comparison, and verified migration requirements. |
| `tools-atmosphere-ocean` | Absent | Adjacent: `diagnostics:atmosphere` | Precipitation/SST task capabilities, MPAS-Analysis selection criteria, and variable/grid/reference prerequisites. |
| `tools-nco-xcdat` | Absent | Adjacent: `e3sm-unified:tools` | Named NCO/xCDAT operations, command-line versus Python tradeoffs, calendars/bounds, and grid limitations. |
| `tools-environment-choice` | Partial | `e3sm-unified:overview`, `e3sm-unified:activation`, `e3sm-unified:tools` | Perlmutter-specific environment choices, package/version inventory, and individual-installation constraints. |
| `user-guide-compset` | Partial | `user-guide:compsets`, `user-guide-grids`, `running-guide:create-newcase` | Supported atmosphere/land aliases, prescribed ocean choices, compatible grids, and scientific validation evidence. |
| `running-case-setup` | Partial | `running-guide:case-setup`, `running-case-build`, `running-guide:run-and-submit`, `user-guide:namelists` | Complete ordered commands, bundled CIME applicability, machine settings, input checks, and run-status/log interpretation. |
| `user-guide-history` | Partial | `eam-history` | Registered precipitation fields, exact stream/frequency/averaging settings, release-specific constraints, and output verification. |
| `diagnostics-zppy-climatology` | Partial | `diagnostics-parameters`, `diagnostics-run` | All zppy configuration, task dependencies, NCO/regridding steps, years/mapping data, and workflow status checks. |
| `diagnostics-qbo-inputs` | Absent | None | QBO variables/frequency/vertical coordinates, reference coverage, preprocessing, and zppy configuration. |
| `diagnostics-missing-plots` | Absent | Adjacent: `diagnostics-viewer`, `e3sm-unified:troubleshooting` | zppy task/status/log locations, dependency checks, and diagnostics-versus-publication failure distinctions. User artifacts remain necessary for diagnosis. |
| `cross-project-mpas-output` | Absent | None | MPAS-Analysis tasks, ocean/sea-ice streams and analysis members, model-side controls, and missing-output limitations. |
| `cross-project-reproduce-campaign` | Absent | Adjacent: `provenance-reproducibility` | A named released simulation, data-access records, exact run/diagnostics artifacts, and versioned reference data. |
| `cross-project-result-comparability` | Absent | Adjacent: `e3sm-unified:troubleshooting`, `provenance-reproducibility` | Diagnostic-specific package/method changes, output-comparison procedure, and validation evidence. General version/input/provenance reminders do not support a comparability verdict. |

## Duplication and content-quality findings

No duplicate IDs or exact whitespace-normalized text were found. Four exact URL
groups recur, with different sections and distinct text:

| Shared URL path on `docs.e3sm.org` | Entries | Sections |
| --- | ---: | --- |
| `/E3SM/user-guide/` | 2 | Overview and provenance |
| `/running-e3sm-guide/guide-prior-to-production/` | 5 | Cases, creation, setup, build, and namelists |
| `/running-e3sm-guide/guide-production/` | 3 | Submission, XML configuration, and restarts |
| `/E3SM/ELM/user-guide/` | 3 | Surface data, parameters, and history |

Repeated page URLs are not duplicate content. EAM overview/configuration and
diagnostics parameter/run records also overlap in topic, but remain distinct
summaries. Review section identity and citation precision before any consolidation.

- **History citation mismatch:** `user-guide:history-output` describes archives,
  not how to request fields. The [evaluation fixture][fixtures] expects this ID
  for its history question, while `eam-history` holds the relevant introductory
  content. Matching fixture IDs does not establish answer support.
- **Diagnostics capability claim:** `diagnostics:atmosphere` broadly asserts ocean
  and sea-ice support without naming tasks or input conventions. Verify its scope
  against mapped diagnostic definitions; do not infer MPAS-Analysis capabilities.
- **Release-sensitive claims:** EAMxx configuration/support, E3SM-Unified contents,
  setup-after-XML-change guidance, and submission/log behavior require pinned
  source checks. These are verification candidates, not automatically false claims.
- **Citation granularity:** Broad page URLs and generic section labels do not
  locate the evidence for each summary. Reacquire exact mapped sections and retain
  extraction context instead of treating these summaries as verbatim source text.

## Priorities for the six-question pilot

The pilot has **4 partial and 2 absent** content mappings. No pilot record is
provenance-ready. Approve source scope, revisions, licenses, and preparation rules
before acquisition. Existing summaries do not fill gaps in the mapped upstream sources.

| Order | Pilot question | Proposed evidence action |
| --- | --- | --- |
| 1 | `running-case-setup` | Capture bundled CIME setup/build/run sections and the release run template; add completion and machine prerequisites. [Mapping][pilot-run] |
| 2 | `tutorial-diagnostics-example` | Capture the pinned example guide, Python/configuration pair, and input requirements; keep execution unverified. [Mapping][pilot-example] |
| 3 | `diagnostics-zppy-climatology` | Reuse diagnostic inputs; add zppy tutorial/include, defaults, and task templates for the restricted climatology workflow. [Mapping][pilot-zppy] |
| 4 | `tools-atmosphere-ocean` | Add precipitation definitions and the MPAS SST task; document prerequisites without claiming exclusive tool rankings. [Mapping][pilot-tools] |
| 5 | `model-components` | Add release/component guides and resolve missing coupling evidence or explicitly retain partial answer scope. [Mapping][pilot-model] |
| 6 | `cross-project-mpas-output` | Reuse MPAS task evidence; add model-side stream/namelist guidance and verify selected-task requirements. [Mapping][pilot-mpas] |

This order favors shared prerequisites, not scientific importance. Keep later
questions and unclear-license sources outside initial capture unless explicitly
selected. The mapping's compatibility, licensing, and missing-artifact gates remain open.

## Proposed artifact contract

This is a recommendation for approval, not a schema, storage, or release change:

- **Git:** Keep acquisition policy in `corpus/sources.json`. Define selected
  documents/revisions, schema/preparation/tool versions, and eventual artifact
  locations/checksums in a reviewable corpus definition. Policy is not a capture manifest.
- **Curated snapshot:** Keep normalized Markdown, inventory, license notices, and
  hash-bound review records. Retain raw originals and byte hashes separately;
  the current CLI preserves normalized content only.
- **Runtime:** Retain the JSON-array contract initially. Capture/catalog records
  need an explicit conversion to runtime entries; the capture CLI does not supply
  that export. Preserve citation identities: existing IDs can contain `:`, while
  capture IDs currently cannot. Do not rename fixture IDs incidentally.
- **Distribution:** Defer JSONL and GitHub Release automation until a reviewed,
  redistributable baseline exists. Later releases should carry a versioned archive
  and checksum, fetched during build/deployment rather than request handling.
- **Retrieval:** Keep embeddings/indexes derived from the corpus snapshot;
  packaging decisions do not establish retrieval or answer quality. Evaluate those in #21.

## Follow-up boundary

This audit completes the review of existing packaged content against the question
set. Next: approve initial source/version selection and corpus preparation rules,
then perform the small capture pilot under the [curation workflow][workflow].
Do not mark ingestion, example validation, runtime integration, or publication complete.
No corpus entries, acquisition policy, runtime code, or evaluation fixtures changed.

[corpus]: ../../../backend/src/e3sm_ai_platform/knowledge/data/curated_corpus.json
[loader]: ../../../backend/src/e3sm_ai_platform/knowledge/corpus.py
[models]: ../../../backend/src/e3sm_ai_platform/domain/models.py
[curation]: ../../../backend/src/e3sm_ai_platform/knowledge/curation.py
[scope]: ../../../corpus/sources.json
[fixtures]: ../../../evaluation/fixtures/e3sm_questions.json
[workflow]: ../../dev/corpus-curation.md
[questions]: 2-representative-questions.md
[mapping]: 3-source-mapping.md
[pilot-run]: 3-source-mapping.md#running-case-setup--simulation-configuration
[pilot-example]: 3-source-mapping.md#tutorial-diagnostics-example--tutorials-and-examples
[pilot-zppy]: 3-source-mapping.md#diagnostics-zppy-climatology--diagnostics-workflows
[pilot-tools]: 3-source-mapping.md#tools-atmosphere-ocean--tool-selection
[pilot-model]: 3-source-mapping.md#model-components--model-understanding
[pilot-mpas]: 3-source-mapping.md#cross-project-mpas-output--cross-project-guidance
