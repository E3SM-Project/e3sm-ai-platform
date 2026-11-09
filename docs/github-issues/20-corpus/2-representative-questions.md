# Issue #20: Representative questions

Working draft for source selection, not an executable benchmark or reference
answer set. Each heading gives a stable question ID and review status. Expected
elements are evidence requirements, not verified claims. Sources are candidates;
exact sections, revisions, and corpus coverage remain to be checked.

Review wording and relevance first, then resolve context and evidence gaps.
Mark questions reviewed only after checking their supporting evidence. Preserve
IDs when rewording; record replacements if the underlying intent changes.

Under #21, promote reviewed cases into
[`evaluation/fixtures/e3sm_questions.json`](../../../evaluation/fixtures/e3sm_questions.json)
where supported by the evaluation contract. Keep held-out cases separate from
retrieval tuning. No fixture schema or test changes belong to this draft.

## Model understanding

### model-components — draft

- **Question:** Which E3SM components represent atmosphere, land, rivers, ocean,
  and sea ice, and how do they interact in a coupled simulation?
- **Context:** E3SM release and coupled configuration.
- **Expected elements:** Component roles, exchanged quantities, and distinctions
  between active and data components.
- **Candidate sources:** [Model docs], component technical guides, coupling docs.
- **Evidence gaps:** Select a release and locate authoritative coupling details.

### eam-eamxx-mixed — draft

- **Question:** What is the documented distinction between EAM and EAMxx when
  choosing an atmosphere configuration?
- **Context:** E3SM release, science goal, and target machine.
- **Expected elements:** Scientific and configuration differences, documented
  availability, and support limits; do not assume interchangeability.
- **Candidate sources:** [Model docs], EAM/EAMxx guides, release notes.
- **Evidence gaps:** Verify release-specific capability and support statements.

### model-configuration-support — draft

- **Question:** Does a compset appearing in E3SM source mean that its configuration
  is scientifically validated and supported?
- **Context:** Release, compset, grid, and machine.
- **Expected elements:** Distinguish configuration existence, execution testing,
  scientific validation, and project support; qualify unsupported claims.
- **Candidate sources:** [Model resources], [E3SM user guide], release definitions.
- **Evidence gaps:** Find explicit validation and support evidence for the chosen
  configuration rather than infer it from code.

## Tutorials and examples

### tutorial-first-run — draft

- **Question:** Which official tutorial should I follow for my first E3SM run,
  and what must I prepare before starting?
- **Context:** Experience, E3SM release, machine, account, and data access.
- **Expected elements:** Suitable tutorial, prerequisites, major steps, and an
  observable completion check; ask for missing machine or version context.
- **Candidate sources:** [Official tutorials], [Running guide], [CIME docs].
- **Evidence gaps:** Select a tutorial and verify its release and access needs.

### tutorial-diagnostics-example — draft

- **Question:** Where is an official example comparing model climatology with
  observations in e3sm_diags, and how can I follow it?
- **Context:** e3sm_diags version, machine, variables, and input/reference data.
- **Expected elements:** Example files, preprocessing, parameters, execution,
  expected outputs, and data-access constraints.
- **Candidate sources:** [Diagnostics examples], corresponding repository files.
- **Evidence gaps:** Pin example revision and check execution evidence; do not
  label the example validated merely because it is documented.

### tutorial-version-migration — draft

- **Question:** Can I follow an e3sm_diags v2 tutorial unchanged with v3?
- **Context:** Exact tutorial, installed version, environment, and data layout.
- **Expected elements:** Compare documented API, dependencies, and example
  requirements; separate verified compatibility from untested assumptions.
- **Candidate sources:** [Diagnostics docs], tagged tutorial files, release notes.
- **Evidence gaps:** Identify both versions and any migration guidance; state
  insufficient evidence if unchanged execution cannot be established.

## Tool selection

### tools-atmosphere-ocean — draft

- **Question:** Which tools should I use to evaluate atmospheric precipitation
  and ocean sea-surface-temperature biases in E3SM output?
- **Context:** Model components, variables, grids, output frequency, and references.
- **Expected elements:** Match diagnostic needs to documented capabilities of
  e3sm_diags and MPAS-Analysis; explain data preparation and coverage limits.
- **Candidate sources:** [Tool catalog], [Diagnostics docs], [MPAS-Analysis docs].
- **Evidence gaps:** Confirm specific diagnostic tasks and input requirements.

### tools-nco-xcdat — draft

- **Question:** Should I use NCO or xCDAT to compute climatologies from E3SM
  atmosphere output?
- **Context:** File layout, native or regridded data, calendar, computing resources,
  and preference for command-line or Python workflows.
- **Expected elements:** Compare supported operations and prerequisites; explain
  selection criteria without unsupported performance or accuracy rankings.
- **Candidate sources:** [Tool catalog], official NCO and xCDAT documentation.
- **Evidence gaps:** Locate operation-specific guidance and grid/calendar limits.

### tools-unified-role — draft

- **Question:** What does E3SM-Unified provide for analysis and post-processing,
  and do I still need separate instructions to build the E3SM model?
- **Context:** Machine, E3SM-Unified version, and intended task.
- **Expected elements:** Distinguish the analysis environment from model build
  configuration; identify the relevant installation and build guidance.
- **Candidate sources:** [Unified repository], [Model docs], [Running guide].
- **Evidence gaps:** Verify environment contents and platform-specific setup.

## Simulation configuration

### user-guide-compset — draft

- **Question:** How do I choose an E3SM compset for an atmosphere and land simulation?
- **Context:** Release, science goal, active/data components, grid, and machine.
- **Expected elements:** Explain compset selection, supported combinations, and
  how to query available configurations; clarify ambiguous simulation intent.
- **Candidate sources:** [E3SM user guide], [CIME docs], tagged configuration files.
- **Evidence gaps:** Verify an appropriate configuration against the chosen release.

### running-case-setup — draft

- **Question:** After creating a case, which setup and build commands should I run
  before submitting it?
- **Context:** E3SM release, bundled CIME revision, machine, compiler, and case state.
- **Expected elements:** Ordered setup/build steps, prerequisites, and completion
  checks; distinguish machine-specific settings from general commands.
- **Candidate sources:** [Running guide], [CIME docs], release-matched run script.
- **Evidence gaps:** Confirm command order and options for the selected revision.

### user-guide-history — draft

- **Question:** How can I request additional history output fields in E3SM?
- **Context:** E3SM v3.0.2, EAM component, required fields and frequency, and case state.
- **Expected elements:** Relevant namelist settings, field availability, output
  streams, and how to verify output; avoid inventing field names or defaults.
- **Candidate sources:** Tagged EAM user/namelist docs and source definitions.
- **Evidence gaps:** Locate v3.0.2 evidence for the requested fields and settings.

## Diagnostics workflows

### diagnostics-zppy-climatology — draft

- **Question:** How do I configure zppy to produce seasonal atmosphere climatology
  diagnostics with e3sm_diags from monthly E3SM output?
- **Context:** Tool versions, variables, years, grid, reference data, and machine.
- **Expected elements:** Required inputs, climatology/regridding steps, task
  dependencies, configuration sections, and output checks.
- **Candidate sources:** [zppy docs], [Diagnostics docs], matching defaults/templates.
- **Evidence gaps:** Verify compatible versions and a complete example configuration.

### diagnostics-qbo-inputs — draft

- **Question:** What model output and reference data do I need for QBO diagnostics
  in e3sm_diags, and how do I configure the run through zppy?
- **Context:** Tool versions, available fields, vertical levels, frequency, and years.
- **Expected elements:** Diagnostic-specific inputs, time-series preparation,
  reference requirements, and configuration; flag missing required output.
- **Candidate sources:** [Diagnostics docs], QBO definitions, [zppy docs] and templates.
- **Evidence gaps:** Find version-pinned variable, time-coverage, and preprocessing
  requirements rather than infer them from generic diagnostic examples.

### diagnostics-undocumented-set — draft

- **Question:** Our group has a private diagnostic set. What exact zppy settings
  will run it without any changes?
- **Context:** No private configuration or documentation has been provided.
- **Expected elements:** State insufficient evidence for exact settings; request
  shareable interface/configuration details and offer only documented extension guidance.
- **Candidate sources:** [zppy docs] and [Diagnostics docs] extension guidance only.
- **Evidence gaps:** The private set's interface, dependencies, and compatibility
  are unavailable; public documentation cannot establish unchanged execution.

## Cross-project guidance

### cross-project-workflow — draft

- **Question:** How do E3SM history files become climatologies and diagnostic plots
  through zppy, NCO, and e3sm_diags?
- **Context:** Component, tool versions, history streams, target grid, and diagnostic set.
- **Expected elements:** Trace data and task dependencies across projects, including
  file conventions, variable transformations, regridding, and failure checkpoints.
- **Candidate sources:** [Running guide], [zppy docs], [Diagnostics docs], NCO docs.
- **Evidence gaps:** Verify interfaces against one compatible version combination.

### cross-project-reproduce-campaign — draft

- **Question:** Where can I find the configuration and data needed to reproduce
  diagnostics for a publicly released E3SM simulation?
- **Context:** Campaign, experiment, ensemble member, model release, and desired diagnostics.
- **Expected elements:** Connect simulation provenance, data-access instructions,
  preprocessing, and diagnostics configuration; distinguish reproduction from approximation.
- **Candidate sources:** [Data Docs], linked run provenance, [zppy docs], [Diagnostics docs].
- **Evidence gaps:** Select a simulation and check whether exact scripts, references,
  and accessible data are available; report missing artifacts explicitly.

### cross-project-version-guarantee — draft

- **Question:** Will installing the newest zppy and e3sm_diags guarantee that my
  older E3SM workflow produces identical results?
- **Context:** Original and proposed versions, environment, configuration, and data.
- **Expected elements:** Do not guarantee identical results without evidence;
  distinguish API compatibility, successful execution, and numerical equivalence.
- **Candidate sources:** Tool release notes, [Unified repository], validation records.
- **Evidence gaps:** No version pair or comparison results supplied; request them
  and state what public compatibility evidence cannot establish.

## Review notes

- Reused fixture IDs: `eam-eamxx-mixed`, `user-guide-compset`,
  `running-case-setup`, and `user-guide-history`. Added context and expectations
  still need review; existing fixture source IDs are not evidence of coverage.
- `tools-unified-role` replaces the misleading model-build framing of the existing
  `unified-build` question for this draft. The executable fixture remains unchanged.
- First iteration: confirm task relevance, choose target releases and machines,
  and identify missing questions. Then attach exact source sections/revisions and
  review expected elements. Keep unresolved gaps visible rather than invent answers.

[Model docs]: https://docs.e3sm.org/E3SM/
[Model resources]: https://e3sm.org/resources/model/
[E3SM user guide]: https://docs.e3sm.org/E3SM/user-guide/
[Official tutorials]: https://e3sm.org/resources/e3sm-tutorials/
[Running guide]: https://docs.e3sm.org/running-e3sm-guide/
[CIME docs]: https://esmci.github.io/cime/versions/master/html/index.html
[Tool catalog]: https://e3sm.org/tools/
[Diagnostics docs]: https://docs.e3sm.org/e3sm_diags/_build/html/main/index.html
[Diagnostics examples]: https://docs.e3sm.org/e3sm_diags/_build/html/main/examples.html
[zppy docs]: https://docs.e3sm.org/zppy/_build/html/main/index.html
[MPAS-Analysis docs]: https://mpas-dev.github.io/MPAS-Analysis/main/index.html
[Unified repository]: https://github.com/E3SM-Project/e3sm-unified
[Data Docs]: https://docs.e3sm.org/e3sm_data_docs/_build/html/index.html
