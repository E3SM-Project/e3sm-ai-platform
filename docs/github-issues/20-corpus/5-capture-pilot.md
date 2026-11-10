# Issue #20: `running-case-setup` capture pilot

## Scope and result

Capture date: 2026-11-09. Repository baseline:
`17c26f5` (preparation rules in the [curation workflow][workflow]).

This is the first local capture of the six-question pilot and covers only
[`running-case-setup`][pilot-run]. The other five pilot questions and the
remaining twelve representative questions are not captured. All 18 questions
remain the coverage target.

Four prepared documents were captured locally from six acquired files. Ordinary
offline validation passes; `--require-approved` fails because review is not
approved. Nothing was published, integrated into the runtime corpus, executed,
or scientifically validated. No repository code, [source scope][scope], runtime
corpus, retrieval behavior, or evaluation contract changed.

## Selected files and revisions

All files are selected documents in the source scope. Acquisition used
`raw.githubusercontent.com` at the pinned revisions, one request per file at a
1 s interval, between 2026-11-09T23:07:18Z and 23:07:24Z. Every response was
HTTP 200.

| Source | Revision | Path | Bytes | Raw SHA-256 | Git blob |
| --- | --- | --- | ---: | --- | --- |
| E3SM v3.1.0 | `4d2e509b20d3189dcfd76631257b1240ae72bbea` | `run_e3sm.template.sh` | 20708 | `dc8d34fd221ee86caecf13b01622e8ba840c079c96395e49e7ab8a8cd9c52e2a` | `b5eef16c8e90fbd9b96642c1480c2d2f00fec2f0` |
| E3SM v3.1.0 | same | `LICENSE` | 6197 | `96729c497ce3e2a1bdcfb2fe1b4b8066d0ada4c4f624de22376038281fdf4b43` | `247287ab4c0036ef358c4fc591bb25dde229816f` |
| Bundled CIME | `025f09aba0b72177df7e22705f0eadbe351b5add` | `doc/source/ccs/setting-up-a-case.rst` | 20270 | `f00ce0a6b112c7b04bb94de6d58b072afbf4f7ae69a62fe5790a498e57247779` | `b67f6fffb6e43f799205b313619d1fcd746226e0` |
| Bundled CIME | same | `doc/source/ccs/building-a-case.rst` | 5982 | `1d04297ad35a7d8f3a30b19d918a872447a57d246e9d9ab040bbb75a7467f741` | `ee5690dace5360671eeba32160ff4c7687796b56` |
| Bundled CIME | same | `doc/source/ccs/running-a-case.rst` | 27033 | `ae4f85f7d5827bfc1eed77f7ac71ad4b71867c6dd18dc8072dcd94f3e813f65f` | `04c8a709308e910d120d89d582c8a73f1cf41c2f` |
| Bundled CIME | same | `LICENSE.TXT` | 2323 | `a77021590b3d0e5b09efee9ce01555d587567cf6344c2ba0610379c0dadfa434` | `2424196e5a696cc518fe0fee3efc5a46a938806d` |

The `v3.1.0` tag resolves to the E3SM revision above, and E3SM's `cime` gitlink
at that revision is the CIME revision above. Git blob SHA-1 values identify
repository objects; they are not the raw SHA-256 values. The two license files
are retained raw companions and are not captured as content records.

## Local artifact location

Pilot root, relative to the repository root. `corpus/local/` is git-ignored, so
these files are operator-local and never committed:

```text
corpus/local/running-case-setup/
├── README.md               # layout and reproduction notes
├── raw/                    # unchanged response bodies, acquisition.json, upstream-blob-check.txt
├── prepared/               # curator-prepared Markdown inputs
├── provenance.json         # raw-to-prepared provenance, selections, transformations
├── capture-manifest.json   # strict local capture manifest
├── captured/               # content/<id>.md, snapshot.json, catalog.json, review.json
├── scripts/                # acquire, prepare template, build manifest, verify
└── verify-report.txt       # last integrity/fidelity verification output
```

The pilot was first written to a temporary system directory and moved here
unchanged; validation and verification were rerun at this location. This
directory is not a backup: `git clean -x` or removing the clone deletes it.
Copy it to durable storage before relying on it beyond this pilot.

## Preparation and provenance

| Capture ID | Upstream file | Selected source lines | Omitted lines | Method |
| --- | --- | --- | --- | --- |
| `e3sm-run-template` | `run_e3sm.template.sh` | 1–141, 372–576 | 142–371, 577–603 | Exact line ranges in fenced `bash` blocks by script |
| `cime-case-setup` | `setting-up-a-case.rst` | 1–145, 321–364 | 146–320 | Manual RST-to-Markdown conversion |
| `cime-case-build` | `building-a-case.rst` | 1–158 (all) | none | Manual RST-to-Markdown conversion |
| `cime-case-run` | `running-a-case.rst` | 1–191, 211–221 | 192–210, 222–598 | Manual RST-to-Markdown conversion |

- **Template selections:** configuration flags and `main` call order;
  `case_setup`, `custom_pelayout`, `case_build`, `runtime_options`, and
  `case_submit`. Omitted: the `user_nl` function's `user_nl_eam` and
  `user_nl_elm` settings (history output plus non-history options), the empty
  MPAS streams hook, `fetch_code`, `create_newcase`, `copy_script`, and shell
  helpers.
- **CIME setup omissions:** data-model stream customization and CESM-specific
  active-component guidance (CAM, CLM, MOSART, CICE, POP2, CISM), which upstream
  marks `TODO:: remove cesm specific docs`.
- **CIME run omissions:** node-failure and MPI-retry machine settings, restarts,
  output data control, and pre/post-processing, which are outside the selection.
- **Transformations:** RST headings to Markdown headings; inline literals and
  single-backtick interpreted text to code spans; `code-block` and `::` literal
  blocks to fenced blocks with common indentation removed; note, warning, and
  important admonitions to labelled blockquotes; grid and simple tables to pipe
  tables, adding a header row to the headerless simple table; `contents`
  directives and labels omitted; `:ref:` cross-references reduced to link text.
  Upstream wording and typographical errors are unchanged.
- **Curator annotations** appear only in blockquotes labelled “Curator note (not
  upstream content)”. Each document opens with one stating its revision,
  selected and omitted lines, and that nothing was executed or machine-validated.
- **Preparer:** Claude Opus 5.5 through Claude Code, operator-supervised. No
  conversion tool was used for the CIME files; re-running the scripts does not
  regenerate them.

`provenance.json` records each document's owner, repository, path, revision,
release, canonical URL, access constraints, license and companion path,
redistribution terms, raw hashes, acquisition time, selections, method,
prepared hash, and `example_validation: unexecuted`. It also records the Python
version, SHA-256 of each pilot script, and the capture CLI repository commit.
The capture manifest carries only the strict fields accepted by the CLI. Each
record uses the pinned GitHub blob URL; capture IDs match the source-scope
document IDs and do not collide with runtime citation IDs.

| Capture ID | Prepared SHA-256 | Captured (normalized) SHA-256 |
| --- | --- | --- |
| `e3sm-run-template` | `435ba66ca0669cfdbd9b480a6d803ac32a09d70b50de9712b0e086ba4d6315f9` | `1f6adaf02a0da30ac8b62213d253328701e086c8cf40542acf6cf1660c7c7dc0` |
| `cime-case-setup` | `0154f78b0e693fb96d02a696e8cb7b402c2a975ab252990b16f0aefca9072932` | same |
| `cime-case-build` | `3c127918ea7b9df522b7050a4eda601c64d290177a1375c65c46e7ded3011491` | same |
| `cime-case-run` | `afb7408dfcb5425d0b6779790b9ae0e7d3b996ddf8c151610e4829a1d486d1dd` | same |

The template hashes differ only because capture removed trailing whitespace on
template lines 17 (a comment) and 428 (after a shell argument); neither has
semantic meaning. No raw file contains carriage returns. Other trailing
whitespace in the raw files occurs only on blank lines or in omitted ranges.

## Integrity and fidelity checks

Operator-local `scripts/verify_pilot.py` passed:

- Raw byte length, SHA-256, and computed Git blob SHA-1 match `acquisition.json`;
  blob SHA and byte length match the GitHub contents API for all six files.
- Each file path, revision, and pinned URL matches exactly one selected document
  in `corpus/sources.json`, inside its include and outside its exclude patterns.
- Prepared hashes match `provenance.json`. Captured content equals the CLI
  normalization of each prepared file; snapshot hashes, URLs, and revisions match.
- Every `code-block` and `::` literal block in the selected RST ranges appears
  unchanged after dedenting as a fenced block (setup 13, build 6, run 11), with
  no extra fences. Both template ranges match the raw lines exactly after normalization.
- A token-level diff of selected RST prose against captured Markdown found no
  differences for build or run. For setup it found only the added pipe-table
  header (`File or directory | Description`) and one script artifact: the `#`
  of a shell comment inside a verified code block, which the script strips as heading syntax.

Manual fidelity review findings:

- Heading hierarchy matches the selected sections. All 11 selected admonitions
  (setup 6, build 4, run 1) are preserved with unchanged text.
- Seven `:ref:` cross-references were reduced to link text. Four targets are
  captured sections, but no longer linked: `xmlquery` and `xmlchange` (twice) in
  `cime-case-setup`, and `check_input_data` (“Input Data”) in `cime-case-run`.
  Three targets are not captured: multiple instances, model timing data, and
  troubleshooting run-time problems.
- In setup's namelist list, upstream indents item 1's continuation by two spaces,
  so RST renders it as a block quote after the item. The Markdown renders it as
  an item paragraph, matching item 2's form.
- The upstream `preview_run` example output contains historical Chrysalis
  environment settings and library paths (no module loads), an individual
  user's home/scratch paths, a `debug` partition, and an
  `e3sm` account. It is preserved verbatim with a curator caveat.
- Upstream inconsistencies are preserved, not fixed: run says `preview_namelist`
  while setup says `preview_namelists`; the `.case.run` row says `case.setup`
  removes the file; the `Macros.cmake` row refers to `Macros.make`; and the
  `CaseStatus` example is dated 2017.

## Coverage for `running-case-setup`

The [audit][audit] classifies this question as partial. These captures add pinned,
locally verified evidence but do not change that classification because they
are unreviewed and outside the runtime corpus.

| Expected element | Captured evidence | Remaining limitation |
| --- | --- | --- |
| Ordered setup, build, and submission steps | Template `main` order; CIME configure → `case.setup` → `case.build` → `preview_run` → `case.submit` | Template order includes `create_newcase` and its unpinned `fetch_code` |
| Configuration and input prerequisites | `xmlquery`/`xmlchange`, `case.setup --reset`, `$DIN_LOC_ROOT`, `check_input_data --download`, PE layout, wallclock/project/queue | No verified machine values |
| Rebuild and build logs | Rebuild triggers, `--clean`/`--clean-all`, `.bldlog` files compressed on success | Example tree uses `oneapi-ifx`/MPICH, not a verified site toolchain |
| Run-completion checks | `CaseStatus` success entries, `$CASEROOT/timing`, short-term archiving, STDOUT/STDERR, `cpl.log` first, component logs | Status strings not checked against a v3.1.0 case; detailed troubleshooting target not captured |
| Machine-specific versus general settings | Template defaults and `custom_pelayout` core counts; preview caveat | No current Chrysalis LCRC or Perlmutter CPU settings |

The template's caveat is explicit in its capture: it defaults to cloning
`master` with `CHECKOUT="latest"`, so the unchanged template is not pinned
executable guidance for v3.1.0. A reviewer should also confirm one technical
question the captured evidence does not settle. CIME warns that `xmlchange`
after `case.setup` is not reflected without `case.setup --reset`. The template's
`custom_pelayout` runs before `case_setup`, and `case_setup` ends with
`./case.setup --reset` after its own `xmlchange` calls, but `runtime_options`
(template lines 503–559) applies `xmlchange` after setup and build without
another reset. The captured evidence does not state which of those variables
the warning covers.

## Machine contexts

Both contexts remain proposed. No environment solve, installation, build, or
HPC job ran.

- **Chrysalis LCRC:** The template's `custom_pelayout` lists 64 cores per node.
  CIME's preview output is historical Chrysalis evidence, not current settings.
  Unverified: project/account, partition, compiler and modules, input-data root,
  scratch paths, and generated case settings.
- **Perlmutter CPU (`pm-cpu`):** The template defaults to `MACHINE=pm-cpu`,
  `${PSCRATCH}`, SLURM `sacctmgr` account discovery, and 128 cores per node in
  `custom_pelayout`. Unverified: project/account, QOS/queue, compiler and
  modules, input-data root, and generated case settings. CIME's preview example
  is not Perlmutter guidance.

Keep site-specific settings separate; neither context's values were captured
from facility documentation.

## Remaining evidence gaps

- Current facility documentation or a generated case for each machine.
- The CIME troubleshooting and timing pages behind the lost cross-references.
- `doc/source/ccs/creating-a-case.rst`, a mapped candidate not approved for this capture.
- Restart and continuation guidance in the omitted run-guide sections.
- Reconciliation with the packaged `running-guide:*` and `running-*` entries.
- Execution evidence that the captured commands and status strings behave as
  documented for E3SM v3.1.0.

## Reproduction

Network access is needed only for acquisition and blob checks. Run the
repository commands from the repository root with the existing environment.

```bash
R="$PWD/corpus/local/running-case-setup"

# Acquire, then compare with GitHub blob SHAs (see the pilot README).
python3 -I "$R/scripts/acquire.py" "$R"
gh api "repos/ESMCI/cime/contents/doc/source/ccs/running-a-case.rst?ref=025f09aba0b72177df7e22705f0eadbe351b5add" --jq '.sha + " " + (.size|tostring)'

# Prepare the template excerpt and manifests. CIME Markdown is hand-prepared.
python3 -I "$R/scripts/prepare_run_template.py" "$R"
python3 -I "$R/scripts/build_manifest.py" "$R" "$PWD/corpus/sources.json" 17c26f5

# Capture and validate offline.
UV_NO_SYNC=1 uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate-sources corpus/sources.json
UV_NO_SYNC=1 uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py capture "$R/capture-manifest.json" "$R/captured"
UV_NO_SYNC=1 uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate "$R/captured"
UV_NO_SYNC=1 uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate "$R/captured" --require-approved
python3 -I "$R/scripts/verify_pilot.py" "$R" "$PWD/corpus/sources.json"
```

Observed: `validate-sources` and `validate` exit 0; `--require-approved` exits 2
with `corpus.py: error: review is not approved`; verification reports
`integrity checks: passed`. `review.json` records `approved: false`.

## Pending

- [ ] Manual review of prepared content against raw sections by an authorized reviewer.
- [ ] Technical and scientific validation of commands, status checks, and
  machine guidance for E3SM v3.1.0 on each proposed machine.
- [ ] Hash-bound review approval; `validate --require-approved` passing.
- [ ] Runtime integration: conversion of captured records to runtime entries
  and structure-preserving chunking, with existing citation IDs preserved.
- [ ] Publication with retained license companions, under separate authorization.
- [ ] Capture of the remaining five pilot questions.

[workflow]: ../../dev/corpus-curation.md
[scope]: ../../../corpus/sources.json
[audit]: 4-corpus-audit.md
[pilot-run]: 3-source-mapping.md#running-case-setup--simulation-configuration
