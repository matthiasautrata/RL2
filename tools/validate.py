#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyshacl>=0.26", "rdflib>=7.0"]
# ///
"""
RL2 SHACL validation harness.

Validates RL2 policies against the core ontology and SHACL shapes. Targets may be:

  - Turtle files (.ttl), validated directly, or
  - Markdown use cases (.md), whose ```turtle fenced blocks are extracted and
    concatenated into one data graph before validation.

Usage:
    uv run tools/validate.py                       # all conformance/usecases/*.md
    uv run tools/validate.py conformance/usecases/foo.md ...
    uv run tools/validate.py --shapes-only         # just load ontology + shapes
    uv run tools/validate.py -v                     # print full warning/violation reports
    uv run tools/validate.py --strict               # also fail (exit 1) on warnings

SHACL conformance (`sh:conforms`) is true exactly when a graph has no `sh:Violation`
results — warnings do not affect it. That is reported separately from the project
"gate" (warning-free), which `--strict` enforces for release/conformance CI.

Exit code is non-zero if any target fails to parse or does not conform.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Graph

ROOT = Path(__file__).resolve().parent.parent
CORE_ONTOLOGY_FILES = ["spec/rl2.ttl"]
CORE_SHAPES_FILES = ["spec/rl2-shacl.ttl"]

# Standard prefixes injected before markdown-extracted Turtle so illustrative
# snippets that omit their own @prefix lines still resolve. A block's own @prefix
# declaration (if present) simply re-binds — Turtle allows redeclaration.
PREAMBLE = """\
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dc:   <http://purl.org/dc/elements/1.1/> .
"""

TURTLE_FENCE = re.compile(r"```turtle\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
# Markers that indicate a use case's RL2 model is a stub, not real Turtle.
PLACEHOLDER_HINTS = ("placeholder", "to be added", "tbd")


def load_graph(paths: list[str]) -> Graph:
    g = Graph()
    for p in paths:
        g.parse(ROOT / p, format="turtle")
    return g


def extract_turtle(md_path: Path) -> tuple[str, bool]:
    """Return (concatenated turtle, is_placeholder_only)."""
    text = md_path.read_text()
    blocks = TURTLE_FENCE.findall(text)
    real = [b for b in blocks if not _looks_placeholder(b)]
    return "\n".join(real), (bool(blocks) and not real)


def extract_fences(md_path: Path) -> list[tuple[int, str]]:
    """Return [(start_line, body)] for each non-placeholder ```turtle fence.

    Used by per-fence mode, where each fence is validated as its own graph —
    the right model for reference docs whose fences are independent, standalone
    illustrations (a shared IRI reused across sections must not merge).
    """
    text = md_path.read_text()
    out: list[tuple[int, str]] = []
    for m in TURTLE_FENCE.finditer(text):
        body = m.group(1)
        if _looks_placeholder(body):
            continue
        start_line = text.count("\n", 0, m.start(1)) + 1
        out.append((start_line, body))
    return out


def _looks_placeholder(block: str) -> bool:
    code = "\n".join(
        ln for ln in block.splitlines() if ln.strip() and not ln.strip().startswith("#")
    ).strip()
    if not code:  # only comments / blank
        return True
    # Illustrative pseudo-Turtle: authors use "..." / "…" as elisions, which is
    # not parseable. Treat such blocks as documentation, not validatable data.
    if re.search(r"(^|\s)(\.\.\.|…)(\s|$)", code) or "..." in code:
        return True
    low = block.lower()
    return any(h in low for h in PLACEHOLDER_HINTS) and len(code) < 200


def build_data_graph(target: Path, ontology: Graph) -> tuple[Graph | None, str]:
    """Return (graph, note). graph is None when there is nothing to validate.

    The ontology is merged into the data graph: RL2 policies reference ontology
    individuals (operators like rl2:eq, state enums like rl2:Fulfilled, runtime
    refs like rl2:currentAgent), and SHACL `sh:class` checks need those types
    present as facts — pyshacl's `ont_graph` only feeds inference, not validation.
    """
    g = Graph()
    g += ontology
    if target.suffix == ".ttl":
        g.parse(target, format="turtle")
        return g, ""
    turtle, placeholder_only = extract_turtle(target)
    if not turtle.strip():
        return None, "no turtle blocks" if not placeholder_only else "placeholder only"
    g.parse(data=PREAMBLE + turtle, format="turtle")
    return g, ""


def run_shacl(data: Graph, shapes: Graph) -> tuple[int, int, str]:
    """Validate a data graph; return (violations, warnings, report_text)."""
    _, _, report_text = validate(
        data_graph=data,  # ontology already merged in
        shacl_graph=shapes,
        inference="rdfs",
        advanced=True,
        meta_shacl=False,
    )
    # pyshacl reports malformed SHACL/SPARQL as a textual Validation Failure rather than
    # raising. Treating that as zero counted violations would make an invalid shapes graph pass.
    if "Validation Failure" in report_text:
        raise ValueError(report_text.strip())
    return (
        report_text.count("Severity: sh:Violation"),
        report_text.count("Severity: sh:Warning"),
        report_text,
    )


def validate_whole(target: Path, rel, ont: Graph, shapes: Graph, verbose: bool) -> str:
    """Validate a target as one graph (all fences concatenated). Returns category."""
    try:
        data, note = build_data_graph(target, ont)
    except Exception as exc:  # parse error in the extracted turtle
        print(f"✗ {rel}\n    PARSE ERROR: {exc}")
        return "fail"
    if data is None:
        print(f"– {rel}  (skipped: {note})")
        return "skip"
    try:
        n, w, report_text = run_shacl(data, shapes)
    except Exception as exc:  # a bad file must not abort the whole suite
        print(f"✗ {rel}\n    VALIDATION ERROR: {exc}")
        return "fail"
    # SHACL conformance depends only on sh:Violation results; warnings/info do
    # not break conformance (pyshacl's `conforms` flag is stricter).
    if n == 0:
        # sh:conforms is true (no violations); warnings still fail the strict gate.
        wtxt = f"  (⚠ {w} warning(s))" if w else ""
        glyph = "⚠" if w else "✓"
        print(f"{glyph} {rel}  ({len(data)} triples){wtxt}")
        if verbose and w:
            print("\n".join("    " + ln for ln in report_text.splitlines()))
        return "warn" if w else "pass"
    wtxt = f", {w} warning(s)" if w else ""
    print(f"✗ {rel}  ({n} violation(s){wtxt})")
    if verbose:
        print("\n".join("    " + ln for ln in report_text.splitlines()))
    return "fail"


def validate_per_fence(target: Path, rel, ont: Graph, shapes: Graph, verbose: bool) -> str:
    """Validate each ```turtle fence independently. Returns the file's category.

    A file passes when every fence parses and conforms. This is the right model
    for reference docs: each fence is a standalone illustration, so a shared
    example IRI reused across sections must not merge into one graph.
    """
    fences = extract_fences(target)
    if not fences:
        print(f"– {rel}  (skipped: no turtle blocks)")
        return "skip"

    tot_viol = tot_warn = 0
    bad: list[str] = []
    reports: list[str] = []
    for start_line, body in fences:
        loc = f"{rel}:{start_line}"
        g = Graph()
        g += ont
        try:
            g.parse(data=PREAMBLE + body, format="turtle")
        except Exception as exc:
            bad.append(f"    ✗ fence@{start_line}: PARSE ERROR: {str(exc).splitlines()[0]}")
            continue
        try:
            n, w, report_text = run_shacl(g, shapes)
        except Exception as exc:
            bad.append(f"    ✗ fence@{start_line}: VALIDATION ERROR: {str(exc).splitlines()[0]}")
            continue
        tot_warn += w
        if verbose and w:
            reports.append(f"    SHACL report for fence@{start_line}:")
            reports.append("\n".join("        " + ln for ln in report_text.splitlines()))
        if n:
            tot_viol += n
            bad.append(f"    ✗ fence@{start_line}: {n} violation(s)")
            if verbose and not w:
                reports.append(f"    SHACL report for fence@{start_line}:")
                reports.append("\n".join("        " + ln for ln in report_text.splitlines()))

    ok = len(fences) - sum(1 for b in bad if b.lstrip().startswith("✗"))
    if not bad:
        wtxt = f"  (⚠ {tot_warn} warning(s))" if tot_warn else ""
        glyph = "⚠" if tot_warn else "✓"
        print(f"{glyph} {rel}  ({len(fences)} fence(s)){wtxt}")
        if reports:
            print("\n".join(reports))
        return "warn" if tot_warn else "pass"
    print(f"✗ {rel}  ({ok}/{len(fences)} fence(s) OK, {tot_viol} violation(s))")
    print("\n".join(bad))
    if reports:
        print("\n".join(reports))
    return "fail"


def main() -> int:
    ap = argparse.ArgumentParser(description="RL2 SHACL validator")
    ap.add_argument("targets", nargs="*", help="Markdown or Turtle files to validate")
    ap.add_argument("--shapes-only", action="store_true", help="Only load ontology + shapes")
    ap.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print full SHACL reports for warnings and violations",
    )
    ap.add_argument(
        "--per-fence",
        action="store_true",
        help="Validate each ```turtle fence as its own graph (for reference docs "
        "whose fences are independent illustrations, not one cumulative scenario)",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Treat warning-only files as failures (release/conformance gate). "
        "SHACL conformance is unaffected — this is the stricter project gate.",
    )
    args = ap.parse_args()

    ontology_files = list(CORE_ONTOLOGY_FILES)
    shapes_files = list(CORE_SHAPES_FILES)

    print(f"Loading ontology: {', '.join(ontology_files)}")
    ont = load_graph(ontology_files)
    print(f"Loading shapes:   {', '.join(shapes_files)}")
    shapes = load_graph(shapes_files)
    print(f"  ontology: {len(ont)} triples · shapes: {len(shapes)} triples\n")

    if args.shapes_only:
        print("Ontology and shapes parsed OK.")
        return 0

    targets = args.targets or sorted(
        str(p) for p in (ROOT / "conformance" / "usecases").glob("*.md")
    )
    fails, skipped, passed, warned = [], [], [], []

    for t in targets:
        target = ROOT / t if not Path(t).is_absolute() else Path(t)
        rel = target.relative_to(ROOT) if str(target).startswith(str(ROOT)) else target

        if args.per_fence and target.suffix == ".md":
            outcome = validate_per_fence(target, rel, ont, shapes, args.verbose)
        else:
            outcome = validate_whole(target, rel, ont, shapes, args.verbose)
        {"pass": passed, "warn": warned, "fail": fails, "skip": skipped}[outcome].append(rel)

    print(f"\n{'='*60}")
    evaluated = len(passed) + len(warned) + len(fails)
    conforming = len(passed) + len(warned)  # sh:conforms: no sh:Violation
    print(f"PASS {len(passed)} · WARN-ONLY {len(warned)} · FAIL {len(fails)} · SKIP {len(skipped)}")
    if evaluated:
        print(
            f"SHACL conformance (no sh:Violation): {conforming}/{evaluated}  ·  "
            f"warning-free gate: {len(passed)}/{evaluated}"
        )
    if args.strict and warned:
        print(f"--strict: {len(warned)} warning-only file(s) counted as failures.")
    if fails and not args.verbose:
        print("Re-run with -v <file> to see violation details.")
    return 1 if (fails or (args.strict and warned)) else 0


if __name__ == "__main__":
    sys.exit(main())
