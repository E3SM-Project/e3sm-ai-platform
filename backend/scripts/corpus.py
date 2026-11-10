"""Curation CLI for acquisition scopes, local captures, and corpus artifacts.

``validate-sources`` validates an upstream acquisition scope (for example,
``corpus/sources.json``).  ``curate`` downloads every selected document in a
scope at its pinned revision and builds a validated local corpus; it is the only
command that uses the network.  ``capture`` and ``refresh`` instead require a
separate pinned local capture manifest with local Markdown content.  ``package``
archives an approved build locally without uploading it.  ``coverage`` reports
which expected documents each representative question retrieves and cites.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from e3sm_ai_platform.application.corpus_coverage import measure_coverage
from e3sm_ai_platform.knowledge.corpus_build import curate, package, verify_build
from e3sm_ai_platform.knowledge.curation import (
    CurationValidationError,
    capture,
    refresh,
    validate_corpus,
    validate_source_scope,
)


def main() -> int:
    """Run the local-only corpus curation command line interface."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    capture_parser = commands.add_parser(
        "capture", help="capture a separate pinned local manifest into a corpus root"
    )
    capture_parser.add_argument("manifest", type=Path)
    capture_parser.add_argument("output", type=Path)
    refresh_parser = commands.add_parser(
        "refresh", help="write a separate candidate corpus and changes.json"
    )
    refresh_parser.add_argument(
        "snapshot", type=Path, help="existing corpus root containing snapshot.json"
    )
    refresh_parser.add_argument("manifest", type=Path)
    refresh_parser.add_argument("output", type=Path)
    validate_parser = commands.add_parser(
        "validate", help="validate corpus artifacts without network access"
    )
    validate_parser.add_argument("root", type=Path)
    validate_parser.add_argument(
        "--require-approved", action="store_true", help="require a hash-bound approved review"
    )
    source_scope_parser = commands.add_parser(
        "validate-sources", help="validate an offline acquisition scope, not a capture manifest"
    )
    source_scope_parser.add_argument(
        "path", type=Path, help="acquisition scope JSON, e.g. corpus/sources.json"
    )
    curate_parser = commands.add_parser(
        "curate", help="download selected scope documents and build a validated local corpus"
    )
    curate_parser.add_argument("scope", type=Path, help="acquisition scope JSON")
    curate_parser.add_argument("output", type=Path, help="build directory")
    curate_parser.add_argument(
        "--overwrite", action="store_true", help="replace a previous build at output"
    )
    verify_parser = commands.add_parser(
        "verify-build", help="check a curate build's raw hashes, fidelity, and artifacts offline"
    )
    verify_parser.add_argument("root", type=Path, help="build directory from curate")
    package_parser = commands.add_parser(
        "package", help="archive an approved build with a checksum; never uploads"
    )
    package_parser.add_argument("root", type=Path, help="build directory from curate")
    package_parser.add_argument("output", type=Path, help="directory for the archive")
    package_parser.add_argument("--version", required=True, help="release label")
    coverage_parser = commands.add_parser(
        "coverage", help="report expected documents retrieved and cited per question"
    )
    coverage_parser.add_argument("root", type=Path, help="build directory from curate")
    coverage_parser.add_argument("questions", type=Path, help="question set JSON")
    coverage_parser.add_argument("--output", type=Path, help="write the JSON report here")
    args = parser.parse_args()
    try:
        if args.command == "curate":
            snapshot = curate(args.scope, args.output, overwrite=args.overwrite)
            print(f"captured {len(snapshot.records)} documents in {args.output}")
        elif args.command == "verify-build":
            failures = verify_build(args.root)
            if failures:
                parser.error("; ".join(failures))
        elif args.command == "coverage":
            _print_coverage(measure_coverage(args.root, args.questions), args.output)
        elif args.command == "package":
            print(package(args.root, args.output, args.version))
        elif args.command == "capture":
            capture(args.manifest, args.output)
        elif args.command == "refresh":
            refresh(args.snapshot, args.manifest, args.output)
        elif args.command == "validate-sources":
            failures = validate_source_scope(args.path)
            if failures:
                parser.error("; ".join(failures))
        else:
            failures = validate_corpus(args.root, require_approved=args.require_approved)
            if failures:
                parser.error("; ".join(failures))
    except CurationValidationError as error:
        parser.error(str(error))
    return 0


def _print_coverage(report, output: Path | None) -> None:
    """Print a per-question coverage table and optionally save the JSON report."""
    print(f"{'question':38} {'expected':>8} {'retrieved':>9} {'cited':>5}  route")
    for item in report.questions:
        print(
            f"{item.id:38} {len(item.expected):>8} {len(item.expected_retrieved):>9} "
            f"{len(item.expected_cited):>5}  {item.route}"
        )
    print(
        f"expected documents retrieved: {report.expected_retrieved_total}/{report.expected_total}; "
        f"questions citing an expected document: {report.questions_citing_expected}/"
        f"{len(report.questions)}"
    )
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
