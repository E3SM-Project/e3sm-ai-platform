# Corpus review checklist

Use this checklist to approve a local corpus build before packaging it. A review
takes about an hour. Approval covers the exact build reviewed: rebuilding resets
it, so review again after any rebuild.

Work from the repository root. You need GitHub access to open the source links.

## 1. Build and check

```bash
make corpus-curate     # downloads pinned files; about 12 minutes
make corpus-validate   # must finish without errors
make corpus-coverage   # prints the per-question table
```

- [ ] `make corpus-validate` passes.
- [ ] Note the coverage totals for the review record.

Files to review:

- **Inventory:** [`corpus/sources.json`](../../corpus/sources.json), one line per
  document under each source.
- **Captured documents:** `corpus/local/corpus/captured/content/<id>.md`.
- **Raw license files:** `corpus/local/corpus/raw/<source>/<revision>/`.
- **Questions:** [`corpus/questions.json`](../../corpus/questions.json).

## 2. Selection

For each source in `sources.json`:

- [ ] The repository and owner are the authoritative upstream project.
- [ ] `revision` matches `release`. For tagged releases,
      `git ls-remote --tags <repository_url> | grep <revision>` lists the tag.
      Snapshots, feedstock recipes, and the CIME submodule have no tag; confirm
      the `release` label explains the choice.
- [ ] Each source's `include` and `exclude` patterns select its user-facing
      documentation without unrelated content; explicit documents help answer
      at least one question in `questions.json`.
- [ ] Nothing important is missing for a question; list gaps in the review record
      instead of approving with silent gaps.

## 3. Licenses

- [ ] Each source has a `"role": "license"` document or a `license_url`.
- [ ] The source's `redistribution` text matches its raw license file.
- [ ] Known exceptions are acceptable for the intended use:
  - **NCO manual:** GFDL-1.3-or-later; its excerpt must keep the copyright and
    license notice (lines 14–21).
  - **E3SM Data Docs:** no license file; reuse within E3SM was approved on
    2026-11-10. Confirm before any external publication.

## 4. Caveats

Documents are verbatim and may contain outdated or unsafe advice. Caveats are
recorded as `notes` in `sources.json`, not in the captured files.

- [ ] Open every document that has `notes` and confirm the note is accurate.
- [ ] Skim the remaining documents for advice that should be flagged, such as:
  - disabling security checks (for example, TLS verification);
  - links to `master` or `latest` instead of a pinned version;
  - machine paths, accounts, modules, or queues presented as current.
- [ ] Add or correct `notes` in `sources.json` for anything found.

## 5. Spot-check content

`make corpus-validate` already proves each captured file matches its raw
download. Check presentation:

- [ ] Open three captured documents of different types (Markdown, RST, and a
      script or configuration file). The header link opens the same file at the
      same revision on GitHub, and the text matches.
- [ ] `nco-manual.md` contains the license notice and the `ncclimo` section only.
- [ ] `e3sm-eam-namelist-definitions.md` contains the attribute header and the
      history-output entries only.

## 6. Decide

**If changes are needed:** list them in the pull request or issue. After the
changes are merged, rebuild and review again.

**If approved:**

1. In `corpus/local/corpus/captured/review.json`, change `"approved": false`
   to `"approved": true`. Change nothing else.
2. Confirm approval and package the release:

   ```bash
   uv run --package e3sm-ai-platform-backend python backend/scripts/corpus.py validate corpus/local/corpus/captured --require-approved
   make corpus-package VERSION=0.1.0
   ```

3. Record the review in the issue or pull request: reviewer, date,
   `snapshot_sha256` from `review.json`, coverage totals, gaps, and the archive's
   SHA-256 from `corpus/local/release/e3sm-corpus-0.1.0.tar.gz.sha256`.

Packaging creates a local archive only. Publishing it, or replacing the packaged
runtime corpus, needs a separate decision.
