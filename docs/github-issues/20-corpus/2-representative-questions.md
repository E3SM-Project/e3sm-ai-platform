# Issue #20: Representative questions

Working draft for source selection, not an executable benchmark or reference
answer set. Each heading gives a stable question ID and review status. Expected
elements are evidence requirements, not verified claims. Sources are candidates;
exact sections, revisions, and corpus coverage remain to be checked.

This revision addresses task relevance and overlap. User/domain review and source
verification remain pending, so all questions retain draft status. Context fields
identify information to collect, not facts supplied by the question. Ask for
missing context only when it changes the answer; do not invent commands, paths,
support claims, or diagnoses. Mark questions reviewed only after checking their
supporting evidence. Preserve IDs when rewording; record changed intents below.

Under #21, promote reviewed cases into
[`evaluation/fixtures/e3sm_questions.json`](../../../evaluation/fixtures/e3sm_questions.json)
where supported by the evaluation contract. Keep held-out cases separate from
retrieval tuning. No fixture schema or test changes belong to this draft.

See [source mapping](3-source-mapping.md) for all 18 questions, proposed versions,
inspected evidence, and remaining capture gates. Six questions remain the initial
ingestion pilot; mapping the others does not expand approved acquisition scope.

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

### model-science-configurations — draft

- **Question:** Which processes and configurations in a selected E3SM release
  support water-cycle research versus carbon-cycle feedback studies?
- **Context:** Model release, research question, and configurations being compared.
- **Expected elements:** Identify applicable configurations and any overlap;
  explain relevant processes, active components, prescribed versus interactive
  behavior, and scientific limitations. Do not assume separate configuration families.
- **Candidate sources:** [Model docs], [Model resources], campaign descriptions,
  and model-description papers referenced by official documentation.
- **Evidence gaps:** Select comparable released configurations and verify process
  and validation claims rather than generalize across E3SM versions.

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

- **Question:** I found an e3sm_diags v2 tutorial but have v3 installed. Which
  instructions should I recheck before using it?
- **Context:** Exact tutorial, installed version, environment, and data layout.
- **Expected elements:** Identify version-sensitive API, dependency, and example
  requirements; prefer a matching tutorial and distinguish verified changes from
  items that still need checking.
- **Candidate sources:** [Diagnostics docs], tagged tutorial files, release notes.
- **Evidence gaps:** Identify both versions and any migration guidance; state
  insufficient evidence where compatibility cannot be established.

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

### tools-environment-choice — draft

- **Question:** Should I use E3SM-Unified or install analysis tools individually
  to run atmosphere and ocean diagnostics on Perlmutter?
- **Context:** Required tools/versions, available environment, and CPU/GPU target.
- **Expected elements:** Compare documented environment options, package
  availability, and version constraints; do not confuse analysis setup with
  compiling the E3SM model.
- **Candidate sources:** [Unified repository], [Diagnostics docs], [MPAS-Analysis docs].
- **Evidence gaps:** Confirm current platform guidance and an environment containing
  compatible versions of the requested tools.

## Simulation configuration

### user-guide-compset — draft

- **Question:** How do I choose an E3SM compset for an atmosphere and land simulation?
- **Context:** Release, science goal, active/data components, grid, and machine.
- **Expected elements:** Clarify active versus prescribed components, select a
  compset/grid, and explain case creation. Distinguish source-defined combinations
  from scientifically validated and supported configurations.
- **Candidate sources:** [E3SM user guide], [CIME docs], tagged configuration files.
- **Evidence gaps:** Verify an appropriate configuration against the chosen release.

### running-case-setup — draft

- **Question:** After creating an E3SM case, how do I set it up, build it, submit
  it, and check whether the run succeeded?
- **Context:** E3SM release, bundled CIME revision, machine, compiler, and case state.
- **Expected elements:** Ordered setup/build/submission steps, prerequisites, and
  run-completion checks; distinguish machine-specific settings from general commands.
- **Candidate sources:** [Running guide], [CIME docs], release-matched run script.
- **Evidence gaps:** Confirm command order and options for the selected revision.

### user-guide-history — draft

- **Question:** In E3SM v3.0.2 using EAM, how do I add precipitation fields to
  history output at the frequency needed for my planned diagnostics?
- **Context:** Diagnostic set, required precipitation quantity/frequency, existing
  history streams, and case state. This release is a draft scenario, not a support target.
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

### diagnostics-missing-plots — draft

- **Question:** zppy completed preprocessing, but I cannot find any e3sm_diags
  plots. What should I check before rerunning the workflow?
- **Context:** Tool versions, enabled tasks, year ranges, output location, task
  status, and shareable logs/configuration; none of these artifacts are supplied yet.
- **Expected elements:** Explain documented status/log checks, task dependencies,
  and output locations. Request relevant artifacts before diagnosing a cause or
  recommending a targeted rerun; do not assume successful preprocessing proves diagnostics ran.
- **Candidate sources:** [zppy docs] debugging guidance, task templates, [Diagnostics docs].
- **Evidence gaps:** Public docs support a checklist, not an exact failure diagnosis
  without the user's configuration and logs.

## Cross-project guidance

### cross-project-mpas-output — draft

- **Question:** What output must I enable in an E3SM ocean and sea-ice run so
  MPAS-Analysis can compute my chosen diagnostics?
- **Context:** Model/tool versions, analysis tasks, component configuration, and
  available output. Distinguish planning a new run from analyzing an existing one.
- **Expected elements:** Connect MPAS-Analysis task inputs to component output
  streams and analysis settings. Check whether required quantities can be derived
  from available output or require a new run; do not promise to recover missing sampling.
- **Candidate sources:** [MPAS-Analysis docs], MPAS-Ocean/sea-ice guides in [Model docs],
  and release-matched stream/namelist definitions.
- **Evidence gaps:** Select tasks and verify their output requirements across both
  model and analysis documentation.

### cross-project-reproduce-campaign — draft

- **Question:** Where can I find the configuration and data needed to reproduce
  diagnostics for a publicly released E3SM simulation?
- **Context:** Campaign, experiment, ensemble member, model release, and desired diagnostics.
- **Expected elements:** Connect simulation provenance, data-access instructions,
  preprocessing, and diagnostics configuration; distinguish reproduction from approximation.
- **Candidate sources:** [Data Docs], linked run provenance, [zppy docs], [Diagnostics docs].
- **Evidence gaps:** Select a simulation and check whether exact scripts, references,
  and accessible data are available; report missing artifacts explicitly.

### cross-project-result-comparability — draft

- **Question:** My e3sm_diags metrics changed after upgrading E3SM-Unified. How
  should I check whether they remain comparable with my earlier results?
- **Context:** Old/new environments, tool versions, configuration, model/reference
  data, and changed metrics; no comparison artifacts are supplied yet.
- **Expected elements:** Trace relevant package and method changes, compare inputs
  and settings, and identify documented validation checks. Do not infer the cause
  or scientific equivalence from an environment upgrade alone.
- **Candidate sources:** [Unified repository], [Diagnostics docs], dependency release
  notes, and validation records relevant to the changed metrics.
- **Evidence gaps:** Request version pairs and comparison artifacts; state
  insufficient evidence for an exact cause or comparability verdict without them.

## Review notes

- Retained three questions per use case. Added science-capability comparison,
  missing-plot troubleshooting, and model-to-MPAS-Analysis output planning; removed
  overlap between the cross-project workflow and zppy configuration questions.
- Replaced intents/IDs: `model-configuration-support` with
  `model-science-configurations`; `tools-unified-role` with `tools-environment-choice`;
  `diagnostics-undocumented-set` with `diagnostics-missing-plots`;
  `cross-project-workflow` with `cross-project-mpas-output`; and
  `cross-project-version-guarantee` with `cross-project-result-comparability`.
  Configuration-support checks now belong to `user-guide-compset`.
- Retained fixture-derived IDs: `eam-eamxx-mixed`, `user-guide-compset`,
  `running-case-setup`, and `user-guide-history`. The setup question now covers
  submission/completion; the history question now explicitly names a release and
  component. Review those changed expectations before #21 promotion. The earlier
  `unified-build` framing remains excluded; executable fixtures are unchanged.
- Version migration, missing plots, and changed metrics test useful partial
  guidance plus clarification/insufficient evidence, not blanket refusal. #21
  must account for those distinctions before converting them into scored cases.
- Pending user/domain review: confirm target releases and machines, prioritize
  science topics and diagnostic sets, and decide whether additional land/river
  examples are needed. Perlmutter and v3.0.2 are scenarios, not approved corpus scope.
- Next evidence pass: attach exact sections/revisions and verify expected elements.
  No reference answers or examples have been validated by this relevance review.

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
