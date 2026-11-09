# Issue #20: Corpus pre-analysis

## Conclusion

Public official sources are a reasonable starting point, but repositories linked
from [e3sm.org/tools](https://e3sm.org/tools/) alone do not establish coverage of
all six [Chat Assistant use cases](https://github.com/E3SM-Project/e3sm-ai-platform/issues/20).
Expand discovery to model documentation, running guides, tutorials, selected
public Confluence pages, and relevant upstream documentation.

This is a source-selection assessment, not a completed corpus audit or validation
of example execution.

## Coverage and source priorities

| Use case | Initial sources and remaining needs |
| --- | --- |
| Model understanding | [E3SM model and component docs](https://docs.e3sm.org/E3SM/), release notes, and selected scientific references. Tool docs alone do not explain model science. |
| Tutorials and examples | [Official tutorials](https://e3sm.org/resources/e3sm-tutorials/), public workshop practicums, and release-matched repository examples. Record machine and data requirements. |
| Tool selection | Tool catalog plus maintained capability, input, and limitation documentation. Prioritize tools needed by representative questions. |
| Simulation configuration | [CIME docs](https://esmci.github.io/cime/versions/master/html/index.html), the [E3SM running guide](https://docs.e3sm.org/running-e3sm-guide/), and release-matched compset, grid, namelist, and machine definitions. |
| Diagnostics workflows | [zppy](https://docs.e3sm.org/zppy/_build/html/main/index.html) and [e3sm_diags](https://docs.e3sm.org/e3sm_diags/_build/html/main/index.html) guides, defaults, templates, diagnostic definitions, derived variables, and preprocessing requirements. |
| Cross-project guidance | Documented integrations and compatible versions across workflow tools, including MPAS-Analysis, NCO, xCDAT, and E3SM-Unified. |

Prioritize these sources before broad repository ingestion. Add
[E3SM Data Docs](https://docs.e3sm.org/e3sm_data_docs/_build/html/index.html),
facility guidance, scientific papers, and other tools where questions expose gaps.

The E3SM documentation homepage notes that migration from Confluence remains
incomplete. Check public access per page; do not assume the entire wiki is public.

## Questions before large-scale ingestion

Use the [representative question draft](2-representative-questions.md) to review
coverage and guide source selection.

1. Draft representative questions across all six use cases, including common
   tasks, version-specific questions, cross-tool workflows, and unsupported cases.
2. Map each question to required context, expected answer elements, candidate
   evidence, and known gaps. Do not finalize reference answers without evidence.
3. Pilot ingestion on a small source subset. Check preservation of commands,
   configuration examples, tables, section context, and source metadata.
4. Use #21 to evaluate retrieval, answer support, citations, and appropriate
   clarification or insufficient-evidence responses.
5. Expand sources from observed gaps and retain held-out evaluation questions.

For example, asking what a diagnostic set needs before running through zppy
requires evidence about output variables, frequency, preprocessing, reference
data, configuration, and workflow dependencies—not just tool descriptions.

## Authority and reproducibility

- Pin release tags and commits, or page revisions and retrieval dates. Do not mix
  development documentation with released behavior without an explicit label.
- Match CIME evidence to the revision used by the selected E3SM release.
- Distinguish source-defined configurations from scientifically validated,
  supported configurations.
- Distinguish documented examples from examples verified for a specific release
  and environment. Record validation evidence or mark execution unverified.
- Record owner, canonical URL, provenance, applicable versions and machines,
  public-access status, and license. Public instructions do not guarantee access
  to referenced datasets or compute systems.

Source coverage is sufficient for an initial baseline when representative
questions have traceable evidence or explicit gaps. Retrieval and answer quality
still require evaluation in #21. Follow the existing
[corpus curation workflow](../../dev/corpus-curation.md) for capture and approval.
