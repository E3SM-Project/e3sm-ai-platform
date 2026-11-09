# Issue #20: Pilot source mapping

Research date: 2026-11-09. This maps one [draft question](2-representative-questions.md)
per use case to public, pinned upstream files. It proposes acquisition scope;
it does not approve sources, validate example execution, or establish retrieval
coverage. No corpus capture or runtime changes have been made.

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

## Question mappings

All mappings are **partial** until the listed gaps are resolved. The evidence
files below form the proposed capture subset, plus license notices and the
[recipe]; `water_cycle.cfg` is inspection-only. Normalize relevant sections while
retaining complete raw files and provenance separately from CLI output.

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
The canonical documentation URLs above differ from the existing E3SM and
e3sm_diags scope entries. Treat URL reconciliation as an approval decision, not
an automatic change to `corpus/sources.json`.
Keep the documentation-site source unchanged; no site crawl is needed for this
subset. Additional coupling, variable-definition, or NCO sources require a later
explicit selection rather than an implicit scope expansion.

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
  integrity, code/configuration fidelity, resolved includes, and the six question
  mappings. The validator does not perform these checks. Do not execute upstream
  examples or submit HPC jobs as part of ingestion.
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
