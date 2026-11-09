# Issue #20: Source mapping

Research date: 2026-11-09. All 18 [draft questions](2-representative-questions.md)
now have source mappings. The original six remain the initial ingestion pilot;
the other mappings identify later candidates, not approved acquisition scope.
Mapping does not approve sources, validate execution, or establish retrieval
coverage. No corpus capture or runtime changes have been made.

See the [existing-corpus audit](4-corpus-audit.md) for packaged content coverage,
metadata gaps, and priorities for the six-question pilot.

## Proposed baseline

- **Model:** E3SM v3.0.2; `WCYCL1850` with
  `ne30pg2_r05_IcoswISC30E3r5` for the coupled-model scenario.
- **Machine:** Perlmutter CPU (`pm-cpu`). Account, input/reference data, mapping
  files, installed environments, and current facility settings remain unverified.
- **Analysis:** E3SM-Unified 1.11.1. Its pinned [recipe] specifies e3sm_diags 3.0.0,
  zppy 3.0.0, and MPAS-Analysis 1.13.0 together. This supports a proposed tool
  cohort, not proof of end-to-end compatibility with this model configuration.
- **Preprocessing:** The recipe specifies NCO 5.3.2 for non-`hpc` variants; verify
  the actual NCO version separately on the target system. The recipe is not a
  complete environment lockfile.

These are historical, reproducible research targets, not a latest-release claim
or an approved support matrix. Confirm this baseline before capture. The tutorial
uses its own legacy test dataset, not demonstrated v3.0.2 simulation output.

The additional mappings use the same baseline unless stated otherwise. Migration
uses e3sm_diags v2.12.1 as a comparison scenario, not the user's unidentified v2
tutorial. NCO 5.3.2 and xCDAT 0.8.0 match the analysis recipe. Documentation-site
and Data Docs snapshots below are dated research evidence, not release-matched
model instructions or proof of compatibility.

## Source identity and revisions

File links below use these commits, not mutable documentation branches. Public
raw files were inspected; GitHub API metadata resolved tags and the CIME gitlink.
Repository ownership and license notices apply to the selected files, subject to
file-level exceptions checked during capture. Preserve notices and disclaimers.

| Repository / owner | Revision | Canonical documentation | License at revision |
| --- | --- | --- | --- |
| E3SM-Project/E3SM / E3SM Project | v3.0.2: `4412b3a229320d91d4a7d66752e0774a85f14109` | https://docs.e3sm.org/E3SM/ | [BSD-3-Clause, with separable-piece exceptions][model-license] |
| ESMCI/cime / ESMCI, UCAR and E3SM contributors | E3SM's gitlink: `0cdd4b1c5c5eb2e29c6ec64667724af434847bcf` | https://esmci.github.io/cime/ | [UCAR/Sandia permissive terms][cime-license] |
| E3SM-Project/e3sm-unified / E3SM Project | 1.11.1: `6fc3d31dcbc5e72ad474bfb2f8150cd0d5a8a6e0` | https://github.com/E3SM-Project/e3sm-unified | [BSD-3-Clause][unified-license] |
| E3SM-Project/e3sm_diags / E3SM Project | v3.0.0: `7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa` | https://docs.e3sm.org/e3sm_diags/ | [BSD-3-Clause][diags-license] |
| E3SM-Project/zppy / E3SM Project | v3.0.0: `a7508c89eb53d8a4e097a9d28dc2812ba4766787` | https://docs.e3sm.org/zppy/ | [BSD-3-Clause][zppy-license] |
| MPAS-Dev/MPAS-Analysis / MPAS-Dev contributors | 1.13.0: `38429609bcb430a722684b7296916f8a5296c5e8` | https://mpas-dev.github.io/MPAS-Analysis/ | [BSD-3 with institutional notices][mpas-license] |
| E3SM-Project/E3SM-Project.github.io / E3SM Project | Site snapshot: `4b8776b015bf7d193a6e35f2c6a3b60476d52e3d` | https://docs.e3sm.org/running-e3sm-guide/ | [BSD-3-Clause][site-license] |
| E3SM-Project/e3sm_data_docs / E3SM Project | Snapshot: `f3d177dbfcf38af1b540b51f194f2d87b3cbaf85` | https://docs.e3sm.org/e3sm_data_docs/ | Documentation reuse unresolved; [index][data-index] licenses model output, not explicitly these pages. |
| nco/nco / NCO project, Charlie Zender and contributors | 5.3.2: `006119ed3e238a95fbeab3d18875bd2c3f5f3e73` | https://nco.sourceforge.net/nco.html | [Software BSD-3-Clause][nco-license]; [manual][nco-manual] header specifies GFDL-1.3-or-later. |
| xCDAT/xcdat / xCDAT contributors | v0.8.0: `b260fcb0de44a6d327085a3fe4b891cdb8e3bef9` | https://xcdat.readthedocs.io/ | [Apache-2.0 with LLVM exceptions][xcdat-license] |

The e3sm_diags v2.12.1 comparison uses commit
`ca41b0e5d913610c88410928951f1ed11c75663f` and its [BSD-3-Clause license][diags-v2-license].

## Initial pilot mappings

All mappings are **partial** until the listed gaps are resolved. The evidence
files in this section form the proposed pilot capture subset, plus license notices
and the [recipe]; `water_cycle.cfg` is inspection-only. Normalize relevant sections
while retaining complete raw files and provenance separately from CLI output.

### `model-components` — model understanding

- **Scope:** The coupled-model baseline above; component roles and selected
  exchanges, not an exhaustive coupling-field inventory.
- **Evidence:** [Model user guide], “Supported Coupled Compsets,” identifies the
  prognostic components. Component introductions name and describe [EAM], [ELM],
  [MOSART], [MPAS-Ocean], and [MPAS-seaice]. MOSART explicitly connects ELM runoff
  to freshwater input to the ocean.
- **Supported elements:** Component identity, coupled configuration, and the
  land–river–ocean connection.
- **Gaps:** ELM's introduction is a placeholder. Detailed atmosphere/ocean/ice
  exchanges and active-versus-data-component semantics need additional evidence.
  Do not infer a complete coupling explanation from component names.

### `tutorial-diagnostics-example` — tutorials and examples

- **Scope:** e3sm_diags example 5: model climatology versus observations for
  surface air temperature, not the precipitation diagnostic used below.
- **Evidence:** [Examples], “5. Model Climatology vs Observation Climatology” and
  “Running the Examples”; [ex5.py] supplies paths and runner configuration;
  [ex5 diags.cfg] specifies `TREFHT`, ERA-Interim, regions, and seasons.
- **Supported elements:** Example selection, required artifacts, documented
  execution approach, and results location. [Input requirements] explains
  climatology/time-series formats and preprocessing conventions.
- **Gaps:** Docs link to mutable `master` files and load a `latest` environment;
  replace those references with the pins here before capture. Legacy NERSC paths
  and the example's older model data need access checks. The result link is not
  version-bound execution evidence. Verify that the Python runner applies the
  supplied configuration before calling this a validated example. Input guidance
  includes legacy version-qualified commands; do not present all as v3 prescriptions.

### `tools-atmosphere-ocean` — tool selection

- **Scope:** Seasonal precipitation and sea-surface-temperature bias maps.
- **Evidence:** e3sm_diags [lat_lon defaults] defines `PRECT` comparisons with GPCP
  and ERA5. MPAS-Analysis [climatologyMapSST] documents ocean SST maps, observations,
  comparison grids, seasons, and reference-period settings.
- **Supported elements:** Concrete diagnostic capabilities support e3sm_diags
  for precipitation and MPAS-Analysis for MPAS ocean SST. [Input requirements]
  and the MPAS [ocean setup] section describe preparation requirements.
- **Gaps:** This is not an exclusive tool ranking: the e3sm_diags defaults also
  contain SST comparisons. Verify model variable availability, units/derivations,
  reference periods, observation access, and grid compatibility before prescribing
  either workflow.

### `running-case-setup` — simulation configuration

- **Scope:** An already-created baseline case on Perlmutter CPU.
- **Evidence:** E3SM's [run template], functions `case_setup`, `case_build`,
  `runtime_options`, and `case_submit`; bundled CIME's [setup], [build], and [run]
  guides. In [run], use “Monitoring case job statuses,” “Input data,” and
  “Troubleshooting a job that fails.”
- **Supported elements:** Setup/build/submission order, configuration and input
  prerequisites, `CaseStatus`, and model/component log checks.
- **Gaps:** The run template defaults to fetching `master`; do not execute it
  unchanged for a pinned release. CIME's machine examples are not Perlmutter
  configuration. Verify project, compiler, queue, input paths, and generated case
  settings before issuing executable instructions. No build or simulation ran.

### `diagnostics-zppy-climatology` — diagnostics workflows

- **Scope:** Monthly EAM output, regridded seasonal climatologies, and only the
  e3sm_diags `lat_lon` set for the first pilot.
- **Evidence:** zppy's [tutorial], “Example 1,” and its literal include
  [post.mysimulation.cfg] define tasks and dependencies. [default.ini] defines
  `[climo]` and `[e3sm_diags]` settings. [climo.bash] invokes NCO and places climo
  files; [e3sm_diags.bash] links inputs, configures the runner, and copies results.
  [Input requirements] and [lat_lon defaults] supply diagnostic-side evidence.
- **Supported elements:** Input paths, years, mapping/reference data, task
  configuration, preprocessing flow, and output/status locations.
- **Gaps:** Tutorial paths and partition target Chrysalis, not Perlmutter. Its
  campaign example enables diagnostics needing more than monthly climatologies;
  explicitly restrict pilot sets instead of copying it wholesale. The tutorial's
  campaign-file path is stale: the actual file is [water_cycle.cfg] under
  `zppy/defaults/`. Inspect it for this discrepancy; defer campaign-wide ingestion.
  Adapted configuration, NCO behavior, data access, and successful execution remain
  unverified. Preserve `literalinclude` content during normalization.

### `cross-project-mpas-output` — cross-project guidance

- **Scope:** MPAS-Analysis `climatologyMapSST` and `climatologyMapSeaIceConcNH`.
- **Evidence:** MPAS-Analysis [ocean setup] and [sea-ice setup], “Setting up
  Standalone” sections, identify monthly analysis-member/stream requirements.
  [climatologyMapSST] and [climatologyMapSeaIceConcNH] identify the selected tasks.
  E3SM's [ocean user guide], “Customizing runs,” and [sea-ice user guide],
  “Configuring Model Input and Output,” explain namelist and `SourceMods` stream
  overrides. The MPAS-Analysis [E3SM setup] section claims E3SM defaults support
  analysis without modifications.
- **Supported elements:** Where output is configured and how analysis inputs
  connect to component streams; distinguish standalone guidance from E3SM setup.
- **Gaps:** Verify selected-task fields against generated v3.0.2 namelists/streams
  before relying on the general defaults claim. The analysis sea-ice introduction
  also contains a stale “not yet publicly released” statement; do not reproduce it
  as current fact. Missing-field derivations and whether a new run is needed
  require the actual available output. No configuration was generated or tested.

## Remaining question mappings

These 12 mappings complete question coverage, not evidence completeness. Reuse
pilot files where applicable; keep additional files out of initial capture unless
explicitly selected. Context fields in the question draft still apply.

### `eam-eamxx-mixed` — model understanding

- **Scope:** Distinguish atmosphere choices in the v3.0.2 source tree.
- **Evidence:** [EAM] describes its dynamical core and parameterizations;
  [EAMxx introduction] describes C++/Kokkos, performance portability, and its
  available SCREAM configuration. [Model overview] marks EAMxx not yet supported.
- **Supported elements:** Architectural/scientific distinctions and the release's
  explicit support caveat; source presence does not make EAMxx interchangeable with EAM.
- **Gaps:** EAMxx's [case guide] is only a heading and introductory sentence.
  Machine/configuration suitability and detailed physics comparisons need further
  release-specific evidence. Do not present the v3 support caveat as timeless.

### `model-science-configurations` — model understanding

- **Scope:** Water-cycle and carbon-cycle capabilities of the selected release.
- **Evidence:** [Model user guide], “Supported Coupled Compsets”; [ELM user guide],
  “Steps to build and run ELM,” states v3 water-cycle runs include active land BGC
  and interactive phenology. [Coupled compsets] defines `WCYCL1850` and retains a
  separately labeled “E3SM V1 BGC experiment compsets” section.
- **Supported elements:** Science capabilities overlap: water-cycle configurations
  are not necessarily prescribed-phenology or carbon-cycle-free configurations.
- **Gaps:** The legacy BGC aliases do not establish v3 validation or support.
  Full ocean carbon feedbacks, atmospheric CO2 coupling, and suitability for a
  particular experiment need explicit component/campaign evidence.

### `tutorial-first-run` — tutorials and examples

- **Scope:** A new Perlmutter CPU user preparing a short coupled-model test.
- **Evidence:** [Running guide index] organizes the workflow; [Pre-production],
  “Configuring the Model Run” and “Testing the model,” covers machine/project,
  paths, pinned code, short tests, and restart/PE-layout checks. Pair with the
  release-pinned [run template] and CIME [run] guide for completion checks.
- **Supported elements:** A documented learning path, required choices, short-run
  milestones, and observable checks before production.
- **Gaps:** The site snapshot links to `master`, not v3.0.2. Verify current account,
  allocation, compiler, input-data, and queue prerequisites. Report proposed checks,
  not successful tutorial execution; do not submit jobs during source capture.

### `tutorial-version-migration` — tutorials and examples

- **Scope:** Compare v2.12.1 and v3.0.0 guidance pending identification of the actual tutorial.
- **Evidence:** Both [v2 configuration] and [v3 configuration] document
  `CoreParameter`, `runner.run_diags`, and custom `-d` configuration. [Diags v3 overview],
  “Current State,” claims user-API backward compatibility while describing the
  CDAT-to-Xarray/xCDAT backend change. [Diags installation] documents environment options.
- **Supported elements:** Recheck dependencies, data layout, diagnostic parameters,
  and machine paths rather than assume every v2 instruction requires a rewrite.
- **Gaps:** A v2.12.1 sample does not represent every v2 tutorial. Locate the exact
  tutorial/version and compare its requirements; API compatibility is not proof
  of identical numerical results or unchanged execution.

### `tools-nco-xcdat` — tool selection

- **Scope:** Monthly/seasonal climatologies from EAM output; compare workflow fit, not speed rankings.
- **Evidence:** The [NCO manual][nco-manual], “ncclimo netCDF Climatology Generator,” describes
  climatology generation, splitting, and optional regridding; [ncclimo] is the
  implementation used by [climo.bash]. [xCDAT overview], “Features,” and
  [temporal API], `TemporalAccessor.climatology`, document Python climatologies,
  time-bound weighting, calendars, reference periods, and seasonal configuration.
- **Supported elements:** Batch/file-oriented NCO versus an xarray-based analysis
  workflow, with explicit metadata and grid prerequisites.
- **Gaps:** Check native-grid handling, bounds, missing data, and seasonal weighting
  on the actual input. No performance or equivalence comparison ran. The NCO manual
  specifies GFDL terms, while [doc/LICENSE][nco-doc-license] contains a GPL notice;
  resolve applicable documentation terms before redistribution.

### `tools-environment-choice` — tool selection

- **Scope:** Analysis setup on Perlmutter CPU, not building the model.
- **Evidence:** [Unified README] describes the metapackage; [recipe] identifies the
  proposed cohort. [Perlmutter quick guide], “1. Installation,” and
  [Diags installation] document shared-environment activation versus custom installation.
- **Supported elements:** Choose based on available package versions and platform
  needs; a managed environment and an individual tool installation serve different scopes.
- **Gaps:** `load_latest` does not pin 1.11.1; inspect the actual installed environment.
  Shared paths and historical module commands may have changed. The installation
  page includes advice to disable TLS verification; exclude that unsafe advice
  from assistant instructions and use approved certificate configuration instead.

### `user-guide-compset` — simulation configuration

- **Scope:** Active EAM and ELM with prescribed ocean conditions, subject to user intent.
- **Evidence:** [EAM user guide], “Scientifically supported compsets and grids,”
  lists `F1850`, `F2010`, and `F20TR`. [EAM compsets] expands their component names;
  CIME [create case], “Calling create_newcase,” defines compset/grid/case arguments.
- **Supported elements:** A documented starting configuration, active/prescribed
  distinctions, and case-creation syntax; use E3SM guidance for scientific support.
- **Gaps:** Confirm time period, grid, forcing, and whether the user wants an
  interactive ocean. Do not substitute generic CIME/CESM example compsets or treat
  arbitrary XML entries as scientifically validated combinations.

### `user-guide-history` — simulation configuration

- **Scope:** EAM precipitation output in v3.0.2 for a specified diagnostic requirement.
- **Evidence:** [EAM user guide], “History File Namelist Parameters,” and [run template],
  `user_nl`, include precipitation output examples. [EAM namelist definitions],
  entries `fincl1`, `avgflag_pertape`, `nhtfrq`, and `mfilt`, define settings and limits.
- **Supported elements:** `user_nl_eam`, field selection, frequency versus file
  grouping, and averaging semantics. The definitions identify `I` as instantaneous;
  the prose guide incorrectly repeats `A` for that choice.
- **Gaps:** Confirm the requested precipitation quantity, registered fields, stream,
  and sampling with generated namelists and output metadata. Do not repeat the typo
  or infer a field exists solely from its name. The XML notes monthly-frequency restrictions.

### `diagnostics-qbo-inputs` — diagnostics workflows

- **Scope:** Monthly zonal-wind time series for the pinned QBO workflow.
- **Evidence:** [Input requirements], “Preprocessing Steps,” specifies monthly `U`
  and equal test/reference year counts. [QBO defaults] chooses `U` and ERA-Interim;
  [QBO parameter] enables time-series inputs; [QBO driver], `run_diag` and
  `_unify_plev`, handles spatial reduction and pressure units. [e3sm_diags.bash]
  and [default.ini] connect time-series paths and reference-year settings to zppy.
- **Supported elements:** Diagnostic-specific variable/frequency, reference
  configuration, preprocessing, and vertical-coordinate considerations.
- **Gaps:** Verify available stratospheric levels, record length, reference coverage,
  and the generated configuration. Source-level year handling and the documentation's
  equal-duration rule need reconciliation for the selected period; no QBO run was tested.

### `diagnostics-missing-plots` — diagnostics workflows

- **Scope:** A troubleshooting checklist, with no user logs or configuration yet supplied.
- **Evidence:** [tutorial], “Debugging failures,” describes `.status`, job-output,
  and debug checks. [Task boilerplate] records running status; [e3sm_diags.bash]
  distinguishes diagnostics failure from web-copy failure and identifies result paths.
- **Supported elements:** Check task enablement/dependencies, job status, logs,
  local results, and publication separately; preprocessing success is not diagnostics success.
- **Gaps:** Request shareable configuration, failed-task logs, and year/path details.
  Public guidance cannot identify the actual failure or justify a targeted rerun.
  Do not recommend destructive cleanup or replay generated scripts without review.

### `cross-project-reproduce-campaign` — cross-project guidance

- **Scope:** Data Docs' `v3.LR.piControl` example, not assumed to use the pilot's exact patch release.
- **Evidence:** [v3 simulation table] links that simulation to ESGF/HPSS;
  [v3 campaign overview] supplies overview-paper references and explicitly states
  that v3 run scripts are not archived in this repository. [Data access] describes
  native versus processed data and warns that archived scripts need adaptation.
  [recipe], [tutorial], and [Examples] provide separate analysis-workflow context.
- **Supported elements:** Find released data and follow provenance links while
  distinguishing documented workflow examples from exact campaign reproduction.
- **Gaps:** Exact model commit, member/years, diagnostics scripts, reference-data
  versions, and access must be established for the selected run. Data Docs' model-output
  CC BY 4.0 statement does not establish permission to redistribute its documentation.

### `cross-project-result-comparability` — cross-project guidance

- **Scope:** A comparison procedure; old/new environments and changed metrics remain unspecified.
- **Evidence:** [recipe] provides one environment's package provenance;
  [Diags v3 overview] documents the backend transition. [Diags testing], “Unit
  and integration tests” and “Complete run test,” describes image comparisons,
  versioned expectations, and a manual large-data test outside the unit suite.
- **Supported elements:** Compare package versions, input/reference data, settings,
  and outputs; consult validation evidence for the affected diagnostics.
- **Gaps:** Request both environment records and comparison artifacts before
  attributing a cause or judging equivalence. A passing image test does not establish
  metric equality or scientific comparability. Select actual version-pair changes
  rather than assume the user's upgrade crossed the v2/v3 boundary.

## Scope changes requiring approval

Compare with the human-owned [source scope](../../../corpus/sources.json):

| Source | Current coverage | Requested scope for this pilot |
| --- | --- | --- |
| E3SM | `docs/**` covers the model user guide. Component docs and root template are excluded by the include list. | Add linked component introductions, `components/mpas-ocean/docs/user-guide/index.md`, `components/mpas-seaice/docs/user-guide/index.md`, and `run_e3sm.template.sh`. |
| e3sm_diags | `docs/**` covers the linked RST guides. | Add `examples/ex5-model-vs-obs/{ex5.py,diags.cfg}` and `e3sm_diags/driver/default_diags/lat_lon_model_vs_obs.cfg`. |
| e3sm-unified | README/docs only. | Add `recipes/e3sm-unified/meta.yaml` as version-provenance evidence. |
| CIME | Repository absent. | Add the pinned repository and the three linked `doc/source/users_guide/*.rst` files. |
| zppy | Repository absent. | Add the pinned repository, linked tutorial/include, `default.ini`, and two task templates. Defer `water_cycle.cfg`. |
| MPAS-Analysis | Repository absent. | Add the pinned repository and linked setup/task RST files. |

Use exact selected paths, not new broad wildcards. Include license companions.
The canonical documentation URLs above differ from the existing E3SM,
e3sm_diags, and E3SM-Project.github.io scope entries. Treat URL reconciliation as
an approval decision, not an automatic change to `corpus/sources.json`.
Keep the documentation-site source unchanged; no site crawl is needed for this
pilot subset. Mapping the remaining questions does not approve or enlarge it.

### Additional candidates for the remaining questions

All paths resolve at the pins above. Existing scope still needs human document
selection/review even where a path already matches its include list.

| Source | Additional candidates / scope implications |
| --- | --- |
| E3SM | Linked EAM/EAMxx introductions and guides, ELM user guide, `cime_config/allactive/config_compsets.xml`, `components/eam/cime_config/config_compsets.xml`, and `components/eam/bld/namelist_files/namelist_definition.xml`; these are outside `docs/**`. |
| E3SM-Project.github.io | Linked running-guide index and pre-production page already match `docs/**`; select the pinned snapshot without treating it as v3.0.2 documentation. |
| e3sm_diags | Linked overview, install/configuration/Perlmutter/testing guides match `docs/**`; v2.12.1 is a separate comparison revision. QBO defaults, parameter, and driver files require path additions. |
| e3sm-unified | README is already in scope; retain the pilot recipe addition for version provenance. |
| CIME / zppy | Extend proposed CIME paths with `doc/source/users_guide/create-a-case.rst`; add `zppy/templates/inclusions/boilerplate.bash` to the proposed zppy selection. |
| NCO | New repository: select `doc/nco.texi` sections and `data/ncclimo`, with applicable license companions. Resolve documentation-license notices before capture. |
| xCDAT | New repository: select the overview and `xcdat/temporal.py` API/docstrings, plus `LICENSE` and `NOTICE`. |
| E3SM Data Docs | New repository: linked index, data-access page, v3 table, and its `overview.rst.inc` dependency. Documentation reuse permission remains a capture blocker. |

Do not crawl/download linked datasets, execute examples, ingest whole repositories,
or broaden pilot scope merely because these questions need more evidence.

## Capture gate and validation

- [ ] Human approves baseline, selected documents/revisions, licenses, and scope changes.
- [ ] Resolve gaps needed for the chosen answer scope; retain explicit partial
  coverage for unresolved elements rather than claim complete answers.
- [ ] Retain complete raw upstream files separately, with byte hashes and a local
  provenance record connecting each raw file/revision to its normalized copy.
  The CLI stores normalized content only; it does not archive or hash raw originals.
- [ ] Prepare Markdown under the existing [curation workflow](../../dev/corpus-curation.md).
  Capture treats any UTF-8 input as Markdown and normalizes whitespace; it does
  not check or convert formats. Convert RST and resolve includes, and fence code,
  configuration, and recipe excerpts before capture.
- [ ] Derive a separate pinned local capture manifest. Do not pass
  `corpus/sources.json` to `capture`, and do not commit generated artifacts.
- [ ] Manually review selection completeness, approved path scope, raw-file
  integrity, code/configuration fidelity, resolved includes, and mappings for the
  selected question subset. The validator does not perform these checks. Do not
  execute upstream examples or submit HPC jobs as part of ingestion.
- [ ] Run offline CLI validation for record metadata, safe paths, normalized
  content hashes, duplicate records, and review-artifact consistency.
- [ ] Record hash-bound review approval and pass `validate --require-approved`
  before publication. Example execution and retrieval evaluation remain separate.

[model-license]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/LICENSE
[cime-license]: https://github.com/ESMCI/cime/blob/0cdd4b1c5c5eb2e29c6ec64667724af434847bcf/LICENSE.TXT
[unified-license]: https://github.com/E3SM-Project/e3sm-unified/blob/6fc3d31dcbc5e72ad474bfb2f8150cd0d5a8a6e0/LICENSE
[diags-license]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/LICENSE
[zppy-license]: https://github.com/E3SM-Project/zppy/blob/a7508c89eb53d8a4e097a9d28dc2812ba4766787/LICENSE
[mpas-license]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/38429609bcb430a722684b7296916f8a5296c5e8/LICENSE
[recipe]: https://github.com/E3SM-Project/e3sm-unified/blob/6fc3d31dcbc5e72ad474bfb2f8150cd0d5a8a6e0/recipes/e3sm-unified/meta.yaml
[Model user guide]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/docs/user-guide/index.md
[EAM]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/eam/docs/index.md
[ELM]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/elm/docs/index.md
[MOSART]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/mosart/docs/index.md
[MPAS-Ocean]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/mpas-ocean/docs/index.md
[MPAS-seaice]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/mpas-seaice/docs/index.md
[Examples]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/docs/source/examples.rst
[ex5.py]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/examples/ex5-model-vs-obs/ex5.py
[ex5 diags.cfg]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/examples/ex5-model-vs-obs/diags.cfg
[Input requirements]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/docs/source/input-data-requirement.rst
[lat_lon defaults]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/e3sm_diags/driver/default_diags/lat_lon_model_vs_obs.cfg
[climatologyMapSST]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/38429609bcb430a722684b7296916f8a5296c5e8/docs/users_guide/tasks/climatologyMapSST.rst
[ocean setup]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/38429609bcb430a722684b7296916f8a5296c5e8/docs/users_guide/mpaso.rst
[sea-ice setup]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/38429609bcb430a722684b7296916f8a5296c5e8/docs/users_guide/mpasseaice.rst
[run template]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/run_e3sm.template.sh
[setup]: https://github.com/ESMCI/cime/blob/0cdd4b1c5c5eb2e29c6ec64667724af434847bcf/doc/source/users_guide/setting-up-a-case.rst
[build]: https://github.com/ESMCI/cime/blob/0cdd4b1c5c5eb2e29c6ec64667724af434847bcf/doc/source/users_guide/building-a-case.rst
[run]: https://github.com/ESMCI/cime/blob/0cdd4b1c5c5eb2e29c6ec64667724af434847bcf/doc/source/users_guide/running-a-case.rst
[tutorial]: https://github.com/E3SM-Project/zppy/blob/a7508c89eb53d8a4e097a9d28dc2812ba4766787/docs/source/tutorial.rst
[post.mysimulation.cfg]: https://github.com/E3SM-Project/zppy/blob/a7508c89eb53d8a4e097a9d28dc2812ba4766787/docs/source/post.mysimulation.cfg
[default.ini]: https://github.com/E3SM-Project/zppy/blob/a7508c89eb53d8a4e097a9d28dc2812ba4766787/zppy/defaults/default.ini
[climo.bash]: https://github.com/E3SM-Project/zppy/blob/a7508c89eb53d8a4e097a9d28dc2812ba4766787/zppy/templates/climo.bash
[e3sm_diags.bash]: https://github.com/E3SM-Project/zppy/blob/a7508c89eb53d8a4e097a9d28dc2812ba4766787/zppy/templates/e3sm_diags.bash
[water_cycle.cfg]: https://github.com/E3SM-Project/zppy/blob/a7508c89eb53d8a4e097a9d28dc2812ba4766787/zppy/defaults/water_cycle.cfg
[climatologyMapSeaIceConcNH]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/38429609bcb430a722684b7296916f8a5296c5e8/docs/users_guide/tasks/climatologyMapSeaIceConcNH.rst
[ocean user guide]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/mpas-ocean/docs/user-guide/index.md
[sea-ice user guide]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/mpas-seaice/docs/user-guide/index.md
[E3SM setup]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/38429609bcb430a722684b7296916f8a5296c5e8/docs/users_guide/e3sm.rst
[site-license]: https://github.com/E3SM-Project/E3SM-Project.github.io/blob/4b8776b015bf7d193a6e35f2c6a3b60476d52e3d/LICENSE
[nco-license]: https://github.com/nco/nco/blob/006119ed3e238a95fbeab3d18875bd2c3f5f3e73/LICENSE
[nco-doc-license]: https://github.com/nco/nco/blob/006119ed3e238a95fbeab3d18875bd2c3f5f3e73/doc/LICENSE
[xcdat-license]: https://github.com/xCDAT/xcdat/blob/b260fcb0de44a6d327085a3fe4b891cdb8e3bef9/LICENSE
[diags-v2-license]: https://github.com/E3SM-Project/e3sm_diags/blob/ca41b0e5d913610c88410928951f1ed11c75663f/LICENSE
[Model overview]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/docs/index.md
[EAMxx introduction]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/eamxx/docs/index.md
[case guide]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/eamxx/docs/user/eamxx_cases.md
[ELM user guide]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/elm/docs/user-guide/index.md
[Coupled compsets]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/cime_config/allactive/config_compsets.xml
[Running guide index]: https://github.com/E3SM-Project/E3SM-Project.github.io/blob/4b8776b015bf7d193a6e35f2c6a3b60476d52e3d/docs/running-e3sm-guide/index.md
[Pre-production]: https://github.com/E3SM-Project/E3SM-Project.github.io/blob/4b8776b015bf7d193a6e35f2c6a3b60476d52e3d/docs/running-e3sm-guide/guide-prior-to-production.md
[v2 configuration]: https://github.com/E3SM-Project/e3sm_diags/blob/ca41b0e5d913610c88410928951f1ed11c75663f/docs/source/config-run.rst
[v3 configuration]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/docs/source/config-run.rst
[Diags v3 overview]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/docs/source/index.rst
[Diags installation]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/docs/source/install.rst
[nco-manual]: https://github.com/nco/nco/blob/006119ed3e238a95fbeab3d18875bd2c3f5f3e73/doc/nco.texi
[ncclimo]: https://github.com/nco/nco/blob/006119ed3e238a95fbeab3d18875bd2c3f5f3e73/data/ncclimo
[xCDAT overview]: https://github.com/xCDAT/xcdat/blob/b260fcb0de44a6d327085a3fe4b891cdb8e3bef9/docs/getting-started-guide/overview.rst
[temporal API]: https://github.com/xCDAT/xcdat/blob/b260fcb0de44a6d327085a3fe4b891cdb8e3bef9/xcdat/temporal.py
[Unified README]: https://github.com/E3SM-Project/e3sm-unified/blob/6fc3d31dcbc5e72ad474bfb2f8150cd0d5a8a6e0/README.md
[Perlmutter quick guide]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/docs/source/quickguides/quick-guide-perlmutter.rst
[EAM user guide]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/eam/docs/user-guide/index.md
[EAM compsets]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/eam/cime_config/config_compsets.xml
[create case]: https://github.com/ESMCI/cime/blob/0cdd4b1c5c5eb2e29c6ec64667724af434847bcf/doc/source/users_guide/create-a-case.rst
[EAM namelist definitions]: https://github.com/E3SM-Project/E3SM/blob/4412b3a229320d91d4a7d66752e0774a85f14109/components/eam/bld/namelist_files/namelist_definition.xml
[QBO defaults]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/e3sm_diags/driver/default_diags/qbo_model_vs_obs.cfg
[QBO parameter]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/e3sm_diags/parameter/qbo_parameter.py
[QBO driver]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/e3sm_diags/driver/qbo_driver.py
[Task boilerplate]: https://github.com/E3SM-Project/zppy/blob/a7508c89eb53d8a4e097a9d28dc2812ba4766787/zppy/templates/inclusions/boilerplate.bash
[data-index]: https://github.com/E3SM-Project/e3sm_data_docs/blob/f3d177dbfcf38af1b540b51f194f2d87b3cbaf85/docs/source/index.rst
[v3 simulation table]: https://github.com/E3SM-Project/e3sm_data_docs/blob/f3d177dbfcf38af1b540b51f194f2d87b3cbaf85/docs/source/v3/CoupledSystem/simulation_data/simulation_table.rst
[v3 campaign overview]: https://github.com/E3SM-Project/e3sm_data_docs/blob/f3d177dbfcf38af1b540b51f194f2d87b3cbaf85/docs/source/v3/CoupledSystem/simulation_data/overview.rst.inc
[Data access]: https://github.com/E3SM-Project/e3sm_data_docs/blob/f3d177dbfcf38af1b540b51f194f2d87b3cbaf85/docs/source/data_access.rst
[Diags testing]: https://github.com/E3SM-Project/e3sm_diags/blob/7c7956f5a8e10ed11ee0b6bfe69c3e522576f1aa/docs/source/dev_guide/testing.rst
