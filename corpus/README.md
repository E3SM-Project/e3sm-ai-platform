# E3SM knowledge corpus

`sources.json` is the human-owned scope of the corpus: each source is one
repository at a pinned commit, selecting files by folder pattern or explicit
path. `questions.json` lists the representative questions and the documents each
should retrieve. See [corpus curation](../docs/dev/corpus-curation.md) for the
workflow and [scope format](../docs/dev/corpus-curation.md#source-scope-format).

## Contents

Versions follow E3SM v3.1.0, its bundled CIME (`cime6.1.173`), and the
E3SM-Unified 1.13.0 release. Each source contributes its documentation folders
(Markdown and RST) plus specific files that answer the representative questions.
License files are kept with the build but not searched. `sources.json` is the
authoritative list. The current scope builds 539 documents; `acquisition.json`
in the build lists each one by source.

| Source | Documentation folders | Specific files |
| --- | --- | --- |
| E3SM | `docs/` and component `docs/` (excluding legacy CICE and `old/` pages) | `run_e3sm.template.sh`; compset XML; excerpts of the EAM namelist definitions and the `pm-cpu`/`chrysalis` machine and batch XML |
| CIME | `doc/source/` | — |
| Running-E3SM guide site | `docs/` | — |
| e3sm_diags | `docs/source/` | Example run script and config, default diagnostic configs, QBO parameter and driver code; one v2.12.1 page |
| zppy | `docs/source/` | Default and example configs, `climo` and `e3sm_diags` job templates |
| MPAS-Analysis | `docs/` | — |
| E3SM Data Docs | `docs/source/` (including `.rst.inc`) | — |
| E3SM-Unified | `docs/` | `README.md` |
| zstash, e3sm_to_cmip, mache, MPAS-Tools | `docs/` (MPAS-Tools: `conda_package/docs/`) | — |
| xCDAT | `docs/` (excluding project pages) | `temporal.py` |
| NCO | — | `ncclimo` script; manual excerpts for `ncclimo` and `ncremap` |
| conda-forge feedstocks (E3SM-Unified, e3sm_diags, zppy, MPAS-Analysis, NCO, xCDAT) | — | Recipe files: versions and dependencies |

## Local files

```text
corpus/
  sources.json          # corpus scope (tracked)
  questions.json        # representative questions and expected documents (tracked)
  local/                # git-ignored; not a backup
    corpus/             # make corpus-curate output
      acquisition.json  # provenance and hashes for every acquired file
      raw/              # unchanged upstream files
      prepared/         # verbatim Markdown inputs
      capture-manifest.json
      captured/         # content, snapshot, catalog, review
    coverage.json       # make corpus-coverage report
    runtime-corpus.json # make corpus-export output for CORPUS_PATH
    release/            # make corpus-package output (approved builds only)
```
