# Issue #20: Scope of PR #34 and follow-up work

The [coverage report](6-corpus-build-coverage.md) found two separate problems:

- **Retrieval misses documents.** Every mapped document is in the corpus, but
  only 30 of 81 expected documents ranked in the top 8 before the documentation
  expansion, and 17 of 81 after it; 8 of 18 questions now cite none.
- **Sources answer questions only partially.** The
  [source mapping](3-source-mapping.md) rates every question as partial, with
  listed evidence gaps. No document-by-document check has confirmed whether the
  captured text contains each answer's key facts.

Fixing retrieval does not close content gaps, and adding sources does not fix
retrieval. PR #34 now includes the full Git documentation expansion; remaining
work is review, retrieval quality, and content that is not in Git.

## In PR #34

- [x] Add complete documentation ingestion for all selected repo source files
- [x] Add 4 additional document repo sources: zstash, e3sm_to_cmip, mache, mpas_tools (zppy-interfaces and chemdyg deferred)
- [x] External repo sources deferred (e.g. pcmdi_metrics, LIVVkit, TempestRemap, ESMF, MOAB)
- [x] Add release-defined `pm-cpu` and `chrysalis` machine and batch configuration, and the NCO `ncremap` section
- [x] Replace 16 explicit entries already selected by patterns with pattern-derived IDs

Small, documentation-only changes that complete #20's "check representative-question
coverage and record evidence gaps" item:

- [x] Clarify in the coverage report that 30/81 measures whether retrieval finds
      documents, not answer completeness; link the per-question gaps in the source
      mapping.
- [x] Commit the [PR review request](7-pr-review.md).
- [ ] Add notes for the documents flagged by the agent caveat scan, then complete
      the author and colleague reviews.
- [ ] Optional: an agent pass recording whether each question's captured
      documents contain its key facts, as input for the colleague review. Skip
      unless the reviewer wants it; it adds judgment-heavy content to a large PR.

## Follow-up work

| Problem                    | Where     | Work                                                                                                                                                                                                          |
| -------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Retrieval misses documents | #21       | Benchmark lexical, semantic, and hybrid retrieval; fix the recorded vocabulary misses and the ranking loss from the larger corpus (30/81 to 17/81); replace the chunker so commands and headings stay intact. |
| Answers are not judged     | #21       | Expert reference answers, answer and citation metrics, and migration of the evaluation fixtures to the curated corpus.                                                                                        |
| Shared index               | #30       | Build indexes from the approved, packaged corpus build.                                                                                                                                                       |
| Missing content            | New issue | Content not in Git: current NERSC Perlmutter and LCRC Chrysalis user documentation, E3SM papers, and campaign run scripts. Not document gaps: user logs and data, generated output, and execution checks.     |
| Keeping sources current    | #31       | Refresh pinned sources when upstream releases change; scope updates are reviewable diffs.                                                                                                                     |

The remaining content gaps stay out of PR #34: facility documentation and papers
need new approval and a web acquisition method, and the rest cannot be filled by
documents at all.
