# Issue #20: Corpus review request

Review of the expanded corpus build from #34 in three parts: automated agent
checks (done), author confirmation, and colleague judgment and approval. The
agent never approves.

- **Build reviewed:** current scope on `feature/20-corpus`; the snapshot is
  unchanged since `ee1ea40`. 565 files acquired, 539 documents captured, 26
  license files kept raw.
- **`snapshot_sha256`:**
  `fa6a9a2d514aeda9f60306ba46024354eb2d69a23b9006cd8a299b53f7d9d626`
- **Results:** [`6-corpus-build-coverage.md`](6-corpus-build-coverage.md),
  section "Expansion to documentation folders".

## Scope of PR #34

Done:

- Ingest all Markdown and RST documentation of the selected repositories
  through folder patterns.
- Add four sources: zstash, e3sm_to_cmip, mache, and MPAS-Tools.
- Add the `pm-cpu` and `chrysalis` machine and batch configuration and the NCO
  `ncremap` section.
- Replace 16 explicit entries already selected by patterns with pattern-derived
  IDs.
- State in the coverage report that coverage measures whether retrieval finds
  documents, not whether answers are complete; per-question evidence gaps are in
  the [source mapping](3-source-mapping.md).
- Add warning notes to pages that advise disabling SSL verification.

Deferred:

- Sources zppy-interfaces and chemdyg, and external projects such as
  pcmdi_metrics, LIVVkit, TempestRemap, ESMF, and MOAB.
- Content not in Git: NERSC Perlmutter and LCRC Chrysalis user documentation,
  E3SM papers, and campaign run scripts. These need new approval and a web
  acquisition method; no issue is open yet.
- Gaps documents cannot fill: user logs and data, generated output, and
  execution checks.

## 1. Agent pre-review (done 2026-11-10)

| Check | Result |
| --- | --- |
| Build | `verify-build` passes: raw hashes, verbatim content, and capture artifacts. `validate --require-approved` fails only because review is not approved. |
| Tags vs releases | All 13 tagged sources match their `release` label, including CIME `cime6.1.173`. The 8 untagged sources are the documentation-site and Data Docs snapshots and the six feedstock recipes; their labels say so. |
| License documents | All 21 sources have a `license` document, except E3SM Data Docs, which has no license file and uses `license_url`. |
| Redistribution vs license files | Consistent for all 21: BSD-3 (most E3SM projects, zstash, mache, feedstocks), MIT (e3sm_to_cmip), Apache-2.0 (xCDAT), UCAR/Sandia (CIME), BSD-style LANS/UCAR (MPAS-Tools), and NCO's BSD-3 software license with a GPL-3 `doc/LICENSE` notice and GFDL manual notice. |
| Header links | All 539 captured documents link to the pinned file URL and revision. |
| Trimmed files | `nco-manual` holds only the GFDL notice and the `ncclimo` and `ncremap` sections. `e3sm-eam-namelist-definitions` holds the attribute header and 82 history-output entries. `e3sm-machines` holds only `pm-cpu` and `chrysalis`; `e3sm-batch` holds the generic `slurm` and `nersc_slurm` sections plus those two machines. |
| Unresolved includes | 9: zppy `post.rrm_simulation.cfg`, `post.mpas_analysis_model_vs_model.cfg`, and `testing_e3sm_unified.cfg`; MPAS-Analysis generated observation tables (`ocean_obs_table.rst`, `seaice_obs_table.rst`, `all_obs.rst`); xCDAT `demos.txt`, `notebook-examples.txt`, and `../HISTORY.rst`. None added. |
| Coverage | 17 of 81 expected documents in the top 8; 10 of 18 questions cite one. No expected document retrieved for `tutorial-version-migration`, `tools-atmosphere-ocean`, `user-guide-compset`, `diagnostics-qbo-inputs`, or `cross-project-mpas-output`. |

**Caveat scan:** 846 hits in 120 documents for content that may be outdated or
apply only to specific sites; 20 documents already have notes, 100 do not. The
content is public, so the concern is answer accuracy; only the disabled-TLS
advice is unsafe and is noted. The other hits are accepted as-is: they are
pinned upstream documentation, answers cite them, and refreshing sources is
#31's work.

| Pattern | Hits | Unnoted documents | Examples needing a decision |
| --- | ---: | ---: | --- |
| Disabled TLS verification | 6 | 2 | `zppy.docs.source.getting_started.rst` lines 123–124 and `zstash.docs.source.getting_started.rst` lines 127–128 (`ssl_verify false`); already noted in `diags-install` |
| Accounts, queues, partitions | 36 | 15 | e3sm_diags `quickguides/quick-guide-*` (7 pages), `zppy-defaults`, `zppy-tutorial-config`, `mache.docs.users_guide.quick_start.md`, ELM `interpinic` and `surface_dataset`, EAMxx developer pages |
| `module` commands | 21 | 7 | `zstash.docs.source.tutorial.rst`, `zppy.docs.source.campaigns.rst`, `xcdat.docs.getting-started-guide.getting-started-hpc-jupyter.rst` |
| Machine paths | 504 | 52 | `E3SM.components.eam.docs.user-guide.aerosol_phys_prop.md`, e3sm_diags quick guides for Anvil, Chrysalis, and Compy |
| `master`, `main`, `load_latest` | 279 | 75 | `e3sm_data_docs.docs.source.v2.WaterCycle.reproducing_simulations.reproduction_table.rst` (66 links) |

## 2. Author review (before handoff)

- [x] Add notes for the two TLS documents above.
- [ ] Open three documents (Markdown, RST, and a script or configuration) next
  to their header link on GitHub: the text matches.
- [ ] Optional: an agent pass recording whether each question's captured
  documents contain its key facts. Skip unless the colleague wants it.
- [ ] Fill in the review record below: snapshot, coverage, gaps.

## 3. Colleague review (about 45 minutes)

Judgment and approval. Do not approve if anything is unclear; request changes.

### Rebuild and check (about 15 minutes, mostly waiting)

```bash
gh pr checkout 34                       # or: git fetch origin && git checkout feature/20-corpus
uv sync --all-packages
export GITHUB_TOKEN=$(gh auth token)    # optional; avoids GitHub API rate limits
make corpus-curate                      # 565 pinned files, about 12 minutes
make corpus-validate                    # must finish without errors
make corpus-coverage                    # per-question table, about 1 minute
python3 -c "import json; print(json.load(open('corpus/local/corpus/captured/review.json'))['snapshot_sha256'])"
```

- [ ] Your `snapshot_sha256` equals the author's (above). A mismatch means the
  build is not reproducible: stop and report it.

### Sources and selection (about 20 minutes)

```bash
# Documents per source
python3 -c "import json, collections; c = collections.Counter(d['source_id'] for d in json.load(open('corpus/local/corpus/acquisition.json'))['documents'] if d['captured']); [print(f'{s:24} {n:4}') for s, n in c.most_common()]"

# Files selected for one source (replace cime)
python3 -c "import json, sys; [print(d['path']) for d in json.load(open('corpus/local/corpus/acquisition.json'))['documents'] if d['source_id'] == sys.argv[1]]" cime
```

- [ ] Each source is the authoritative project at a sensible version, and its
  `include`/`exclude` patterns in `corpus/sources.json` select the right files.
- [ ] Expected documents in `corpus/questions.json` are relevant; missing
  evidence is listed in your reply.

### Caveats (about 5 minutes)

```bash
# Documents that already have notes
python3 -c "import json; [print(f\"{d['id']}: {d['notes']}\") for s in json.load(open('corpus/sources.json'))['sources'] for d in s['documents'] if d.get('notes')]"
```

- [ ] Existing notes are accurate.

### Licenses (about 3 minutes)

- [ ] The NCO excerpt keeps its copyright and GFDL notice:
  `head -20 corpus/local/corpus/captured/content/nco-manual.md`.
- [ ] E3SM Data Docs reuse is recorded as limited to E3SM (`redistribution`
  for `e3sm_data_docs` in `corpus/sources.json`).

Publishing NCO or Data Docs content outside the project is not part of this review.

### Decide

**Request changes:** reply with the list; changes go into #34, and the build is
reviewed again.

**Approve:**

```bash
python3 -c "import json, pathlib; p = pathlib.Path('corpus/local/corpus/captured/review.json'); d = json.loads(p.read_text()); d['approved'] = True; p.write_text(json.dumps(d, indent=2, sort_keys=True) + '\n')"
uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate corpus/local/corpus/captured --require-approved
make corpus-package VERSION=0.1.0
cat corpus/local/release/e3sm-corpus-0.1.0.tar.gz.sha256
```

This creates a local archive only. Nothing is published.

## Review record

| Field | Value |
| --- | --- |
| Agent pre-review | Section 1, 2026-11-10 |
| Author / date | |
| Colleague (approver) / date | |
| `snapshot_sha256` (author / colleague) | `fa6a9a2d…` / |
| Coverage totals | 17 / 81 retrieved; 10 / 18 cite an expected document |
| Archive SHA-256 | |
| Gaps or requested changes | |
