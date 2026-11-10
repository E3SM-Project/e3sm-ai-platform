# Issue #20: Source mapping

Research date: 2026-11-09. All 18 [draft questions](2-representative-questions.md)
now have source mappings. The operator approved the six-question selection and
first local capture on 2026-11-09, and the remaining twelve questions' candidates
on 2026-11-10 ([approved 18-question scope](#approved-18-question-scope)).
Selected files appear in `corpus/sources.json`; selection does not establish
capture, review approval, execution validation, or retrieval coverage.
Runtime content remains unchanged.

See the [existing-corpus audit](4-corpus-audit.md) for packaged content coverage,
metadata gaps, and priorities for the six-question pilot.

## Version selection and distribution evidence

Checked 2026-11-09. Select Unified members from the latest E3SM-Unified release's
conda-forge recipe and published dependencies, not each member's latest release.
Resolve those selected upstream tags to commits below. Select E3SM independently
from its latest stable release and CIME from that model's submodule revision.
Published conda-forge `main` artifacts establish package availability; feedstock
recipes establish declared dependencies and variants, not runtime compatibility.

| Project | Latest stable GitHub release (discovery) | Selected published conda-forge example: version / subdir / build | Selected feedstock recipe |
| --- | --- | --- | --- |
| E3SM | [v3.1.0][release-model] | Model distribution not audited as a conda-forge package | — |
| E3SM-Unified | [1.13.0][release-unified] | [1.13.0 / linux-64 / hpc_py313hade9021_0][package-unified] | [recipe.yaml][recipe] |
| e3sm_diags | [v3.2.0][release-diags] | [3.2.0 / noarch / pyhc364b38_0][package-diags] | [recipe.yaml][feedstock-diags] |
| zppy | [v3.2.0][release-zppy] | [3.2.0 / noarch / pyhc364b38_0][package-zppy] | [recipe.yaml][feedstock-zppy] |
| MPAS-Analysis | [1.15.0][release-mpas] | [1.15.0 / noarch / pyhcf101f3_0][package-mpas] | [recipe.yaml][feedstock-mpas] |
| NCO | [5.4.2][release-nco] | [5.3.9 / linux-64 / h6d1b28c_2][package-nco] | [recipe.yaml][feedstock-nco] |
| xCDAT | [v0.11.5][release-xcdat] | [0.11.2 / noarch / pyhd8ed1ab_1][package-xcdat] | [meta.yaml][feedstock-xcdat] |

Builds are examples, not a solved environment or a complete list of variants.
Version-specific package API responses are dated observations, not immutable
snapshots. SHA-256 values below identify the exact example builds above; retain
their metadata and select a compatible build set before deployment.

Rechecked 2026-11-09: recorded release tags, E3SM's CIME gitlink, Unified's
feedstock gitlink, and all six example artifact hashes match upstream evidence.
The example NCO build requires `libnetcdf >=4.10.1,<4.10.2.0a0`, while Unified's
recipe pins `libnetcdf ==4.10.0`. These examples cannot be treated as a compatible
build set. MPAS-Analysis requires `nco >=4.8.1,!=5.2.6,!=5.3.7`; this does not
resolve the `hpc` variant's NCO version. No pins were advanced.

| Example package | Artifact SHA-256 |
| --- | --- |
| E3SM-Unified | `5bfd35636c43571c23abc00d68e94e54e578fd0263440485beaf16d99d332e7c` |
| e3sm_diags | `28a862d4eca73fa66e14b9af21968dae9a6d9cb97576df0c02c275af90a8f293` |
| zppy | `8e878bd16b3182e45e7639451addbacb25b562a655fabc9feee62c39e579389a` |
| MPAS-Analysis | `2956b817cf56ffbf2ea6178c133682a95ae87b0410fd91ffbdc351143dba98b7` |
| NCO | `3e1b31f13cefcaf81514416f290a9d5e0b92a20c21f60639987ab4ce0c07eafb` |
| xCDAT | `115b777cdea35721f693b201b4ee8ee4da9715d89d380fad9d29cffd6cbf8cb2` |

### Proposed pilot baseline

- **Model:** E3SM v3.1.0, `WCYCL1850`, and `ne30pg2_r05_IcoswISC30E3r5`.
  Use its bundled CIME revision, not standalone CIME's legacy GitHub
  [latest-release endpoint][release-cime], which reports `cime5.6.4`.
- **Machines:** Chrysalis LCRC and Perlmutter CPU (`pm-cpu`). Account,
  input/reference data, mapping files, installed environment, and current facility
  settings remain unverified for both. Keep site-specific settings separate.
- **Candidate analysis cohort:** The conda-forge Unified [recipe] and published
  package agree on e3sm_diags 3.2.0, zppy 3.2.0, MPAS-Analysis 1.15.0, and
  **xCDAT 0.11.2**, not the latest individual xCDAT release. Non-`hpc` variants
  pin **NCO 5.3.9**; the `hpc` variant has no direct NCO pin, although other
  packages can depend on NCO. Verify the resolved installation separately.
- **Compatibility gate:** Do not override those constraints with independent
  latest versions and call the result validated. No solve, installation, or HPC
  workflow ran. `e3sm-tools` in the recipe is not the E3SM model release.

This replaces the historical Unified 1.11.1 recipe as the package-authority source.
The upstream Unified release records this conda-forge feedstock as a git submodule;
the recipe must be attributed to conda-forge, not treated as a locally maintained
E3SM-Project recipe. The recipe is not a complete environment lockfile.

Mappings use the selected Unified member versions, including [NCO 5.3.9][release-nco-cohort]
and [xCDAT v0.11.2][release-xcdat-cohort], not their newer discovery releases.
Other non-Unified dependencies follow their owning model/tool's constraints;
do not replace bundled revisions with independent latest versions.
All E3SM repository file references, including `user-guide-history`, use v3.1.0.
External campaign records retain their own provenance; these pins do not change
the model version that produced an archived simulation.
Migration compares e3sm_diags
v2.12.1 with the selected v3 release; the actual user's tutorial remains unidentified.
Site/Data Docs snapshots are not model releases. The tutorial's legacy dataset
does not establish output compatibility with the proposed model baseline.

## Source identity and revisions

File links below use these commits, not mutable documentation branches. Public
raw files were inspected; GitHub API metadata resolved tags and the CIME gitlink.
Repository ownership and license notices apply to the selected files, subject to
file-level exceptions checked during capture. Preserve notices and disclaimers.

| Repository / owner | Revision | Canonical documentation | License at revision |
| --- | --- | --- | --- |
| E3SM-Project/E3SM / E3SM Project | v3.1.0: `4d2e509b20d3189dcfd76631257b1240ae72bbea` | https://docs.e3sm.org/E3SM/ | [BSD-3-Clause, with separable-piece exceptions][model-license] |
| ESMCI/cime / ESMCI, UCAR and E3SM contributors | Model gitlink: `025f09aba0b72177df7e22705f0eadbe351b5add` | https://esmci.github.io/cime/ | [UCAR/Sandia permissive terms][cime-license] |
| E3SM-Project/e3sm-unified / E3SM Project | 1.13.0: `a07ba82ffb3860680161ead07ba7a06015b58716` | https://github.com/E3SM-Project/e3sm-unified | [BSD-3-Clause][unified-license] |
| E3SM-Project/e3sm_diags / E3SM Project | Unified cohort v3.2.0: `ff3ef00dad47d305859db40335d1020ea5dfaee4` | https://docs.e3sm.org/e3sm_diags/ | [BSD-3-Clause][diags-license] |
| E3SM-Project/zppy / E3SM Project | Unified cohort v3.2.0: `17ce9335fe2c828a13992df4d2f3a5631edcba2d` | https://docs.e3sm.org/zppy/ | [BSD-3-Clause][zppy-license] plus [NOTICE][zppy-notice] |
| MPAS-Dev/MPAS-Analysis / MPAS-Dev contributors | Unified cohort 1.15.0: `97bf20592a4cd939957db53ac110322243ca43dd` | https://mpas-dev.github.io/MPAS-Analysis/ | [BSD-3 with institutional notices][mpas-license] |
| E3SM-Project/E3SM-Project.github.io / E3SM Project | Site snapshot: `4b8776b015bf7d193a6e35f2c6a3b60476d52e3d` | https://docs.e3sm.org/running-e3sm-guide/ | [BSD-3-Clause][site-license] |
| E3SM-Project/e3sm_data_docs / E3SM Project | Snapshot: `f3d177dbfcf38af1b540b51f194f2d87b3cbaf85` | https://docs.e3sm.org/e3sm_data_docs/ | Documentation reuse unresolved; [index][data-index] licenses model output, not explicitly these pages. |
| nco/nco / NCO project, Charlie Zender and contributors | Unified non-`hpc` cohort 5.3.9: `b0de4bb1a14d085bbba811a95435919501a974f2` | https://nco.sourceforge.net/nco.html | [Software BSD-3-Clause][nco-license]; [manual][nco-manual] header specifies GFDL-1.3-or-later. |
| xCDAT/xcdat / xCDAT contributors | Unified cohort v0.11.2: `8238fab6bbcbcc25f8dc67b4cbe753ab6ba7edfc` | https://xcdat.readthedocs.io/ | [Apache-2.0 with LLVM exceptions][xcdat-license] |

The e3sm_diags v2.12.1 comparison uses commit
`ca41b0e5d913610c88410928951f1ed11c75663f` and its [BSD-3-Clause license][diags-v2-license].
Feedstock commits are embedded in the recipe links above. The Unified feedstock's
[own license][feedstock-license] governs its recipe; upstream licenses and notices
remain separate. Recheck applicable file-level terms for all selected feedstocks.

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

- **Scope:** An already-created baseline case on Chrysalis LCRC or Perlmutter CPU.
- **Evidence:** E3SM's [run template], functions `case_setup`, `case_build`,
  `runtime_options`, and `case_submit`; bundled CIME's [setup], [build], and [run]
  guides. In [run], use “Monitoring Progress,” “Input Data,” and
  “Troubleshooting Failures.”
- **Supported elements:** Setup/build/submission order, configuration and input
  prerequisites, `CaseStatus`, and model/component log checks.
- **Gaps:** The run template defaults to fetching `master`; do not execute it
  unchanged for a pinned release. CIME's preview contains historical Chrysalis
  paths, not verified current Chrysalis settings or Perlmutter configuration.
  Verify project, compiler, queue, input paths, and generated case settings
  separately for each machine before issuing executable instructions.
  No build or simulation ran.

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
- **Gaps:** Tutorial paths and partition target Chrysalis, one proposed context,
  but neither current Chrysalis access nor Perlmutter adaptation is verified. Its
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
- **Gaps:** Verify selected-task fields against generated v3.1.0 namelists/streams
  before relying on the general defaults claim. The analysis sea-ice introduction
  also contains a stale “not yet publicly released” statement; do not reproduce it
  as current fact. Missing-field derivations and whether a new run is needed
  require the actual available output. No configuration was generated or tested.

## Remaining question mappings

These 12 mappings complete question coverage, not evidence completeness. Reuse
pilot files where applicable; keep additional files out of initial capture unless
explicitly selected. Context fields in the question draft still apply.

### `eam-eamxx-mixed` — model understanding

- **Scope:** Distinguish atmosphere choices in the v3.1.0 source tree.
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
- **Gaps:** The site snapshot links to `master`, not a release pin. Verify current account,
  allocation, compiler, input-data, and queue prerequisites. Report proposed checks,
  not successful tutorial execution; do not submit jobs during source capture.

### `tutorial-version-migration` — tutorials and examples

- **Scope:** Compare v2.12.1 and v3.2.0 guidance pending identification of the actual tutorial.
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
  on the actual input. These sources match Unified's selected member versions;
  the `hpc` environment's resolved NCO still needs verification.
  No performance or equivalence comparison ran. The NCO manual
  specifies GFDL terms, while [doc/LICENSE][nco-doc-license] contains a GPL notice;
  resolve applicable documentation terms before redistribution.

### `tools-environment-choice` — tool selection

- **Scope:** Analysis setup on Perlmutter CPU, not building the model.
- **Evidence:** [Unified README] describes the metapackage; the conda-forge [recipe]
  and published package identify the candidate cohort. [Unified quickstart] covers
  variant checks and shared versus custom installation. [Perlmutter quick guide], “1. Installation,” and
  [Diags installation] document shared-environment activation versus custom installation.
- **Supported elements:** Choose based on available package versions and platform
  needs; a managed environment and an individual tool installation serve different scopes.
- **Gaps:** `load_latest` does not pin a Unified release; inspect the actual installed environment.
  Shared paths and historical module commands may have changed. The installation
  page includes advice to disable TLS verification; exclude that unsafe advice
  from assistant instructions and use approved certificate configuration instead.

### `user-guide-compset` — simulation configuration

- **Scope:** Active EAM and ELM with prescribed ocean conditions, subject to user intent.
- **Evidence:** [EAM user guide], “Scientifically supported compsets and grids,”
  lists `F1850`, `F2010`, and `F20TR`. [EAM compsets] expands their component names;
  CIME [create case], “Creating a new Case,” defines compset/grid/case arguments.
- **Supported elements:** A documented starting configuration, active/prescribed
  distinctions, and case-creation syntax; use E3SM guidance for scientific support.
- **Gaps:** Confirm time period, grid, forcing, and whether the user wants an
  interactive ocean. Do not substitute generic CIME/CESM example compsets or treat
  arbitrary XML entries as scientifically validated combinations.

### `user-guide-history` — simulation configuration

- **Scope:** EAM precipitation output in v3.1.0 for a specified diagnostic requirement.
- **Evidence:** The [EAM user guide], “History File Namelist Parameters,”
  and [run template], `user_nl`, include precipitation output examples.
  [EAM namelist definitions],
  entries `fincl1`, `avgflag_pertape`, `nhtfrq`, and `mfilt`, define settings and limits.
- **Supported elements:** `user_nl_eam`, field selection, frequency versus file
  grouping, and averaging semantics. The definitions identify `I` as instantaneous;
  the prose guide incorrectly repeats `A` for that choice.
- **Gaps:** Confirm the requested precipitation quantity, registered fields, stream,
  and sampling with generated namelists and output metadata. Do not repeat the typo
  or infer a field exists solely from its name. The XML notes monthly-frequency restrictions.
  These pins match the question's v3.1.0 context, not every E3SM v3 release.

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
- **Evidence:** The conda-forge [recipe] and published package provide one cohort's
  declared dependencies, not the user's resolved environment;
  [Diags v3 overview] documents the backend transition. [Diags testing], “Unit
  and integration tests” and “Complete run test,” describes image comparisons,
  versioned expectations, and a manual large-data test outside the unit suite.
- **Supported elements:** Compare package versions, input/reference data, settings,
  and outputs; consult validation evidence for the affected diagnostics.
- **Gaps:** Request both environment records and comparison artifacts before
  attributing a cause or judging equivalence. A passing image test does not establish
  metric equality or scientific comparability. Select actual version-pair changes
  rather than assume the user's upgrade crossed the v2/v3 boundary.

## Approved pilot scope

Operator approval on 2026-11-09 covers the six-question selection below,
preparation documentation, and only the first `running-case-setup` local capture.
The source scope records selected documents and pending capture/review status;
it does not track local capture outcomes. Both machine contexts remain proposed.

Selection recorded in the human-owned [source scope](../../../corpus/sources.json):

| Source | Coverage before selection | Approved additions for this pilot |
| --- | --- | --- |
| E3SM | `docs/**` covers the model user guide. Component docs and root template are excluded by the include list. | Add linked component introductions, `components/mpas-ocean/docs/user-guide/index.md`, `components/mpas-seaice/docs/user-guide/index.md`, and `run_e3sm.template.sh`. |
| e3sm_diags | `docs/**` covers the linked RST guides. | Add `examples/ex5-model-vs-obs/{ex5.py,diags.cfg}` and `e3sm_diags/driver/default_diags/lat_lon_model_vs_obs.cfg`. |
| e3sm-unified | README/docs only. | Select the pinned README/quickstart; do not reuse the obsolete local recipe path. |
| conda-forge feedstocks | Repositories absent. | Add the six linked pinned recipes as distribution/version evidence, with metadata, licenses, and notices. |
| CIME | Repository absent. | Add the bundled revision and three linked `doc/source/ccs/*.rst` files. |
| zppy | Repository absent. | Add the pinned repository, linked tutorial/include, `default.ini`, and two task templates. Defer `water_cycle.cfg`. |
| MPAS-Analysis | Repository absent. | Add the pinned repository and linked setup/task RST files. |

Use exact selected paths, not new broad wildcards. Include license companions.
The canonical documentation URLs above differ from the existing E3SM,
e3sm_diags, and E3SM-Project.github.io scope entries. Approval includes reconciling
E3SM and e3sm_diags URLs; the documentation-site source stays unchanged.
Keep the documentation-site source unchanged; no site crawl is needed for this
pilot subset. The [approved 18-question scope](#approved-18-question-scope)
later extended it.

### Additional candidates for the remaining questions

All paths resolve at the pins above. Existing scope still needs human document
selection/review even where a path already matches its include list.

| Source | Additional candidates / scope implications |
| --- | --- |
| E3SM | Linked EAM/EAMxx introductions and guides, ELM user guide, `cime_config/allactive/config_compsets.xml`, `components/eam/cime_config/config_compsets.xml`, and `components/eam/bld/namelist_files/namelist_definition.xml` are outside `docs/**`; select them at the common v3.1.0 pin. |
| E3SM-Project.github.io | Linked running-guide index and pre-production page already match `docs/**`; select the pinned snapshot without treating it as release-matched documentation. |
| e3sm_diags | Linked overview, install/configuration/Perlmutter/testing guides match `docs/**`; v2.12.1 is a separate comparison revision. QBO defaults, parameter, and driver files require path additions. |
| e3sm-unified | README/quickstart match existing scope; package dependency authority comes from conda-forge, not this repository's old recipe. |
| CIME / zppy | Extend proposed CIME paths with `doc/source/ccs/creating-a-case.rst`; add `zppy/templates/inclusions/boilerplate.bash` and preserve zppy's `NOTICE`. |
| NCO | New repository: select `doc/nco.texi` sections and `data/ncclimo`, with applicable license companions. Resolve documentation-license notices before capture. |
| xCDAT | New repository: select the overview and `xcdat/temporal.py` API/docstrings, plus `LICENSE` and `NOTICE`. |
| E3SM Data Docs | New repository: linked index, data-access page, v3 table, and its `overview.rst.inc` dependency. Documentation reuse permission remains a capture blocker. |

Do not crawl/download linked datasets, execute examples, ingest whole repositories,
or broaden pilot scope merely because these questions need more evidence.

### Approved 18-question scope

On 2026-11-10 the operator approved every candidate above for local acquisition,
including the license-flagged NCO manual and E3SM Data Docs pages. The source scope
now selects 85 documents across 16 sources, including license companions. All
paths were rechecked at their pins. Captures are organized by source document,
not by question; this mapping records which documents each question needs.

- **E3SM Data Docs** is E3SM-owned but has no repository license file; its index
  licenses model output, not explicitly these pages. The operator approved reuse
  within this E3SM project. Confirm documentation terms before external publication.
- **NCO** is not an E3SM project. Its manual specifies GFDL-1.3-or-later and
  `doc/LICENSE` contains a GPL notice. Local capture is approved; publication
  must comply with the applicable documentation license and retain notices.
- **Whole files:** the NCO manual and EAM namelist definitions are selected whole,
  not as sections. Retrieval coverage checks decide whether they need trimming.
- The site's `license_url` now pins the snapshot revision instead of `master`.

Selection still does not establish capture fidelity, review approval, execution
validation, or retrieval coverage.

## Capture gate and validation

- [x] Operator approves proposed baseline, selected documents/revisions, license
  companions, and six-question scope changes; scientific and publication review remain pending.
- [ ] Record upstream release pins separately from conda-forge artifact versions,
  builds/hashes, and feedstock commits. Resolve the target environment and check
  model/tool compatibility; latest individual releases are not a validated cohort.
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

[model-license]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/LICENSE
[cime-license]: https://github.com/ESMCI/cime/blob/025f09aba0b72177df7e22705f0eadbe351b5add/LICENSE.TXT
[unified-license]: https://github.com/E3SM-Project/e3sm-unified/blob/a07ba82ffb3860680161ead07ba7a06015b58716/LICENSE
[diags-license]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/LICENSE
[zppy-license]: https://github.com/E3SM-Project/zppy/blob/17ce9335fe2c828a13992df4d2f3a5631edcba2d/LICENSE
[mpas-license]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/97bf20592a4cd939957db53ac110322243ca43dd/LICENSE
[recipe]: https://github.com/conda-forge/e3sm-unified-feedstock/blob/1a1ec2a2cb694fe0403fdd3626ac379d5f2bd6a4/recipe/recipe.yaml
[Model user guide]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/docs/user-guide/index.md
[EAM]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/eam/docs/index.md
[ELM]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/elm/docs/index.md
[MOSART]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/mosart/docs/index.md
[MPAS-Ocean]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/mpas-ocean/docs/index.md
[MPAS-seaice]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/mpas-seaice/docs/index.md
[Examples]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/docs/source/examples.rst
[ex5.py]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/examples/ex5-model-vs-obs/ex5.py
[ex5 diags.cfg]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/examples/ex5-model-vs-obs/diags.cfg
[Input requirements]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/docs/source/input-data-requirement.rst
[lat_lon defaults]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/e3sm_diags/driver/default_diags/lat_lon_model_vs_obs.cfg
[climatologyMapSST]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/97bf20592a4cd939957db53ac110322243ca43dd/docs/users_guide/tasks/climatologyMapSST.rst
[ocean setup]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/97bf20592a4cd939957db53ac110322243ca43dd/docs/users_guide/mpaso.rst
[sea-ice setup]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/97bf20592a4cd939957db53ac110322243ca43dd/docs/users_guide/mpasseaice.rst
[run template]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/run_e3sm.template.sh
[setup]: https://github.com/ESMCI/cime/blob/025f09aba0b72177df7e22705f0eadbe351b5add/doc/source/ccs/setting-up-a-case.rst
[build]: https://github.com/ESMCI/cime/blob/025f09aba0b72177df7e22705f0eadbe351b5add/doc/source/ccs/building-a-case.rst
[run]: https://github.com/ESMCI/cime/blob/025f09aba0b72177df7e22705f0eadbe351b5add/doc/source/ccs/running-a-case.rst
[tutorial]: https://github.com/E3SM-Project/zppy/blob/17ce9335fe2c828a13992df4d2f3a5631edcba2d/docs/source/tutorial.rst
[post.mysimulation.cfg]: https://github.com/E3SM-Project/zppy/blob/17ce9335fe2c828a13992df4d2f3a5631edcba2d/docs/source/post.mysimulation.cfg
[default.ini]: https://github.com/E3SM-Project/zppy/blob/17ce9335fe2c828a13992df4d2f3a5631edcba2d/zppy/defaults/default.ini
[climo.bash]: https://github.com/E3SM-Project/zppy/blob/17ce9335fe2c828a13992df4d2f3a5631edcba2d/zppy/templates/climo.bash
[e3sm_diags.bash]: https://github.com/E3SM-Project/zppy/blob/17ce9335fe2c828a13992df4d2f3a5631edcba2d/zppy/templates/e3sm_diags.bash
[water_cycle.cfg]: https://github.com/E3SM-Project/zppy/blob/17ce9335fe2c828a13992df4d2f3a5631edcba2d/zppy/defaults/water_cycle.cfg
[climatologyMapSeaIceConcNH]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/97bf20592a4cd939957db53ac110322243ca43dd/docs/users_guide/tasks/climatologyMapSeaIceConcNH.rst
[ocean user guide]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/mpas-ocean/docs/user-guide/index.md
[sea-ice user guide]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/mpas-seaice/docs/user-guide/index.md
[E3SM setup]: https://github.com/MPAS-Dev/MPAS-Analysis/blob/97bf20592a4cd939957db53ac110322243ca43dd/docs/users_guide/e3sm.rst
[site-license]: https://github.com/E3SM-Project/E3SM-Project.github.io/blob/4b8776b015bf7d193a6e35f2c6a3b60476d52e3d/LICENSE
[nco-license]: https://github.com/nco/nco/blob/b0de4bb1a14d085bbba811a95435919501a974f2/LICENSE
[nco-doc-license]: https://github.com/nco/nco/blob/b0de4bb1a14d085bbba811a95435919501a974f2/doc/LICENSE
[xcdat-license]: https://github.com/xCDAT/xcdat/blob/8238fab6bbcbcc25f8dc67b4cbe753ab6ba7edfc/LICENSE
[diags-v2-license]: https://github.com/E3SM-Project/e3sm_diags/blob/ca41b0e5d913610c88410928951f1ed11c75663f/LICENSE
[Model overview]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/docs/index.md
[EAMxx introduction]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/eamxx/docs/index.md
[case guide]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/eamxx/docs/user/eamxx_cases.md
[ELM user guide]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/elm/docs/user-guide/index.md
[Coupled compsets]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/cime_config/allactive/config_compsets.xml
[Running guide index]: https://github.com/E3SM-Project/E3SM-Project.github.io/blob/4b8776b015bf7d193a6e35f2c6a3b60476d52e3d/docs/running-e3sm-guide/index.md
[Pre-production]: https://github.com/E3SM-Project/E3SM-Project.github.io/blob/4b8776b015bf7d193a6e35f2c6a3b60476d52e3d/docs/running-e3sm-guide/guide-prior-to-production.md
[v2 configuration]: https://github.com/E3SM-Project/e3sm_diags/blob/ca41b0e5d913610c88410928951f1ed11c75663f/docs/source/config-run.rst
[v3 configuration]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/docs/source/config-run.rst
[Diags v3 overview]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/docs/source/index.rst
[Diags installation]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/docs/source/install.rst
[nco-manual]: https://github.com/nco/nco/blob/b0de4bb1a14d085bbba811a95435919501a974f2/doc/nco.texi
[ncclimo]: https://github.com/nco/nco/blob/b0de4bb1a14d085bbba811a95435919501a974f2/data/ncclimo
[xCDAT overview]: https://github.com/xCDAT/xcdat/blob/8238fab6bbcbcc25f8dc67b4cbe753ab6ba7edfc/docs/getting-started-guide/overview.rst
[temporal API]: https://github.com/xCDAT/xcdat/blob/8238fab6bbcbcc25f8dc67b4cbe753ab6ba7edfc/xcdat/temporal.py
[Unified README]: https://github.com/E3SM-Project/e3sm-unified/blob/a07ba82ffb3860680161ead07ba7a06015b58716/README.md
[Perlmutter quick guide]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/docs/source/quickguides/quick-guide-perlmutter.rst
[EAM user guide]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/eam/docs/user-guide/index.md
[EAM compsets]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/eam/cime_config/config_compsets.xml
[create case]: https://github.com/ESMCI/cime/blob/025f09aba0b72177df7e22705f0eadbe351b5add/doc/source/ccs/creating-a-case.rst
[QBO defaults]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/e3sm_diags/driver/default_diags/qbo_model_vs_obs.cfg
[QBO parameter]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/e3sm_diags/parameter/qbo_parameter.py
[QBO driver]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/e3sm_diags/driver/qbo_driver.py
[Task boilerplate]: https://github.com/E3SM-Project/zppy/blob/17ce9335fe2c828a13992df4d2f3a5631edcba2d/zppy/templates/inclusions/boilerplate.bash
[data-index]: https://github.com/E3SM-Project/e3sm_data_docs/blob/f3d177dbfcf38af1b540b51f194f2d87b3cbaf85/docs/source/index.rst
[v3 simulation table]: https://github.com/E3SM-Project/e3sm_data_docs/blob/f3d177dbfcf38af1b540b51f194f2d87b3cbaf85/docs/source/v3/CoupledSystem/simulation_data/simulation_table.rst
[v3 campaign overview]: https://github.com/E3SM-Project/e3sm_data_docs/blob/f3d177dbfcf38af1b540b51f194f2d87b3cbaf85/docs/source/v3/CoupledSystem/simulation_data/overview.rst.inc
[Data access]: https://github.com/E3SM-Project/e3sm_data_docs/blob/f3d177dbfcf38af1b540b51f194f2d87b3cbaf85/docs/source/data_access.rst
[Diags testing]: https://github.com/E3SM-Project/e3sm_diags/blob/ff3ef00dad47d305859db40335d1020ea5dfaee4/docs/source/dev_guide/testing.rst
[EAM namelist definitions]: https://github.com/E3SM-Project/E3SM/blob/4d2e509b20d3189dcfd76631257b1240ae72bbea/components/eam/bld/namelist_files/namelist_definition.xml
[Unified quickstart]: https://github.com/E3SM-Project/e3sm-unified/blob/a07ba82ffb3860680161ead07ba7a06015b58716/docs/quickstart.md
[zppy-notice]: https://github.com/E3SM-Project/zppy/blob/17ce9335fe2c828a13992df4d2f3a5631edcba2d/NOTICE
[feedstock-license]: https://github.com/conda-forge/e3sm-unified-feedstock/blob/1a1ec2a2cb694fe0403fdd3626ac379d5f2bd6a4/LICENSE.txt
[feedstock-diags]: https://github.com/conda-forge/e3sm_diags-feedstock/blob/c862b307312f4d744546a3827c505af7623af7bb/recipe/recipe.yaml
[feedstock-zppy]: https://github.com/conda-forge/zppy-feedstock/blob/105b7c547c5040a79bf77a1c164ebd02b60eb5d4/recipe/recipe.yaml
[feedstock-mpas]: https://github.com/conda-forge/mpas-analysis-feedstock/blob/ab517cdde1531d13f5c39a5edb1908bbc0c376cd/recipe/recipe.yaml
[feedstock-nco]: https://github.com/conda-forge/nco-feedstock/blob/e8de94e9b88de18b3ec5aceee50b58502f10891a/recipe/recipe.yaml
[feedstock-xcdat]: https://github.com/conda-forge/xcdat-feedstock/blob/b456532e473ad4bcd35fc858b3291d8bc49755d7/recipe/meta.yaml
[release-model]: https://github.com/E3SM-Project/E3SM/releases/tag/v3.1.0
[release-unified]: https://github.com/E3SM-Project/e3sm-unified/releases/tag/1.13.0
[release-diags]: https://github.com/E3SM-Project/e3sm_diags/releases/tag/v3.2.0
[release-zppy]: https://github.com/E3SM-Project/zppy/releases/tag/v3.2.0
[release-mpas]: https://github.com/MPAS-Dev/MPAS-Analysis/releases/tag/1.15.0
[release-nco]: https://github.com/nco/nco/releases/tag/5.4.2
[release-xcdat]: https://github.com/xCDAT/xcdat/releases/tag/v0.11.5
[release-nco-cohort]: https://github.com/nco/nco/releases/tag/5.3.9
[release-xcdat-cohort]: https://github.com/xCDAT/xcdat/releases/tag/v0.11.2
[release-cime]: https://api.github.com/repos/ESMCI/cime/releases/latest
[package-unified]: https://api.anaconda.org/release/conda-forge/e3sm-unified/1.13.0
[package-diags]: https://api.anaconda.org/release/conda-forge/e3sm_diags/3.2.0
[package-zppy]: https://api.anaconda.org/release/conda-forge/zppy/3.2.0
[package-mpas]: https://api.anaconda.org/release/conda-forge/mpas-analysis/1.15.0
[package-nco]: https://api.anaconda.org/release/conda-forge/nco/5.3.9
[package-xcdat]: https://api.anaconda.org/release/conda-forge/xcdat/0.11.2
