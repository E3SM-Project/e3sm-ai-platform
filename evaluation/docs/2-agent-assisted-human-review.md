# Agent-assisted human review (#37)

Question IDs refer to [`corpus/questions.json`](../../corpus/questions.json).

1. **Agent first pass:** Check each assigned question against the corpus snapshot
   and record a finding, evidence, and any proposed action.
2. **Human sign-off:** Check flagged cases and spot-check clean findings. Record
   verdicts only for cases you verify; leave the others pending.

**Corpus snapshot SHA-256:** `fa6a9a2d514aeda9f60306ba46024354eb2d69a23b9006cd8a299b53f7d9d626`.

**Run order:** Pilot one batch per section and spot-check its evidence. Once the
criteria are settled, run the remaining batches in parallel in fresh sessions.
Use the same snapshot throughout and merge the read-only reports afterward.

## Answerable sample

**Sample selection:**

- 20 of 80 answerable questions, chosen for coverage rather than at random.
- Covers all six feature areas, five answerable scenarios, and four personas.
- Excludes questions already reviewed by a person.
- Use batch 1 as the pilot.

### Agent Prompt

```text
Read evaluation/docs/2-agent-assisted-human-review.md for the review workflow
and the IDs in answerable batch <number>. Use corpus/questions.json and only
sources in the local build at corpus/local/corpus-expanded. Verify the snapshot
hash recorded above. Do not edit files. For each ID, open the source
passages and check whether expected_documents together support the full answer.
Flag missing, optional, or alternative sources and any version mismatch.
Report one row per ID: agent finding (supported, partial, unsupported, or
unverified), evidence (document ID, passage locator, short quote), and proposed
action. Leave the human verdict pending. Mark inaccessible evidence unverified.
```

<!-- Local snapshot (not tracked): corpus/local/corpus-expanded/captured/snapshot.json.
     Read source passages from the sibling content/ directory. -->

### Results:

| Batch | Question ID | Agent finding | Human verdict | Evidence | Action |
| --- | --- | --- | --- | --- | --- |
| 1 | `syn-running-clone-case-newuser` | | Pending | | |
| 1 | `syn-components-eam-cosp-developer` | | Pending | | |
| 1 | `syn-diagnostics-qbo-inputs-analyst` | | Pending | | |
| 1 | `syn-tools-xcdat-djf-analyst` | | Pending | | |
| 1 | `syn-environment-zstash-checksum-researcher` | | Pending | | |
| 2 | `syn-running-restart-after-crash-newuser` | | Pending | | |
| 2 | `syn-components-elm-phenology-v3-researcher` | | Pending | | |
| 2 | `syn-diagnostics-plots-online-vague-newuser` | | Pending | | |
| 2 | `syn-environment-mache-new-machine-developer` | | Pending | | |
| 2 | `syn-data-esgf-cmip-native-newuser` | | Pending | | |
| 3 | `syn-running-throughput-vague-newuser` | | Pending | | |
| 3 | `syn-components-eam-avgflag-analyst` | | Pending | | |
| 3 | `syn-diagnostics-diags-native-grid-analyst` | | Pending | | |
| 3 | `syn-tools-ncclimo-highfreq-researcher` | | Pending | | |
| 3 | `syn-environment-e2c-handlers-developer` | | Pending | | |
| 4 | `syn-components-mpaso-oqu240-vague-newuser` | | Pending | | |
| 4 | `syn-diagnostics-zppy-reference-path-analyst` | | Pending | | |
| 4 | `syn-tools-ncremap-dim-order-analyst` | | Pending | | |
| 4 | `syn-environment-unified-windows-vague-newuser` | | Pending | | |
| 4 | `syn-data-reproduce-v2-researcher` | | Pending | | |

## Should-refuse questions

Include all 20. Reuse the [prior near-miss verdicts](1-synthetic-questions.md#answer-expectations)
for the first three only if the questions and relevant corpus evidence are unchanged.

Split pending IDs into batches of up to five.

### Agent Prompt

```text
Read the should-refuse section of evaluation/docs/2-agent-assisted-human-review.md.
Review assigned IDs <IDs> using corpus/questions.json and only sources in the
local build at corpus/local/corpus-expanded. Verify the snapshot hash recorded
above. Do not edit files. Search for a complete answer, open
the closest passages, and distinguish related facts from sufficient evidence.
Report one row per ID: agent finding (refusal warranted, answerable, or
unverified), evidence (search terms and any relevant document ID, passage
locator, and short quote), and proposed action. State what is missing or what
answers the question. Leave the human verdict pending. If relevant sources are
inaccessible or the search is incomplete, use unverified.
```

<!-- Local snapshot (not tracked): corpus/local/corpus-expanded/captured/snapshot.json.
     Read source passages from the sibling content/ directory. -->

### Results:

| Question ID | Agent finding | Human verdict | Evidence | Action |
| --- | --- | --- | --- | --- |
| `syn-refuse-pmcpu-max-walltime-newuser` | | Previously reviewed | | Confirm unchanged |
| `syn-refuse-hpc-nco-version-analyst` | | Previously reviewed | | Confirm unchanged |
| `syn-refuse-ace-predictions-researcher` | | Previously reviewed | | Confirm unchanged |
| `syn-refuse-frontier-account-newuser` | | Pending | | |
| `syn-refuse-v3lr-sypd-researcher` | | Pending | | |
| `syn-refuse-pace-api-developer` | | Pending | | |
| `syn-refuse-wrf-downscaling-researcher` | | Pending | | |
| `syn-refuse-ecs-v3-researcher` | | Pending | | |
| `syn-refuse-mali-calving-developer` | | Pending | | |
| `syn-refuse-fates-pft-developer` | | Pending | | |
| `syn-refuse-marbl-developer` | | Pending | | |
| `syn-refuse-diags-fail-threshold-analyst` | | Pending | | |
| `syn-refuse-zppy-highres-perlmutter-analyst` | | Pending | | |
| `syn-refuse-e2c-cmip7-researcher` | | Pending | | |
| `syn-refuse-gpu-purchase-analyst` | | Pending | | |
| `syn-refuse-unified-114-developer` | | Pending | | |
| `syn-refuse-zarr-convert-analyst` | | Pending | | |
| `syn-refuse-hpss-quota-researcher` | | Pending | | |
| `syn-refuse-v3-rrm-citation-researcher` | | Pending | | |
| `syn-refuse-screamv1-ai-release-researcher` | | Pending | | |
