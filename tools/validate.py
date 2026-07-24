#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyshacl>=0.26", "rdflib>=7.0"]
# ///
"""
RL2 SHACL validation harness.

Validates RL2 policies against the core ontology (rl2.ttl, rl2p.ttl) and SHACL
shapes (rl2-shacl.ttl, rl2p-shacl.ttl). Targets may be:

  - Turtle files (.ttl), validated directly, or
  - Markdown use cases (.md), whose ```turtle fenced blocks are extracted and
    concatenated into one data graph before validation.

Usage:
    uv run tools/validate.py                       # all usecases/*.md
    uv run tools/validate.py usecases/foo.md ...   # specific files
    uv run tools/validate.py --shapes-only         # just load ontology + shapes
    uv run tools/validate.py -v                     # print full violation report

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
ONTOLOGY_FILES = ["rl2.ttl", "rl2p.ttl"]
SHAPES_FILES = ["rl2-shacl.ttl", "rl2p-shacl.ttl"]

# Standard prefixes injected before markdown-extracted Turtle so illustrative
# snippets that omit their own @prefix lines still resolve. A block's own @prefix
# declaration (if present) simply re-binds — Turtle allows redeclaration.
PREAMBLE = """\
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix rl2p: <https://rl2.example/protocol#> .
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


def main() -> int:
    ap = argparse.ArgumentParser(description="RL2 SHACL validator")
    ap.add_argument("targets", nargs="*", help="Markdown or Turtle files to validate")
    ap.add_argument("--shapes-only", action="store_true", help="Only load ontology + shapes")
    ap.add_argument("-v", "--verbose", action="store_true", help="Print full SHACL reports")
    args = ap.parse_args()

    print(f"Loading ontology: {', '.join(ONTOLOGY_FILES)}")
    ont = load_graph(ONTOLOGY_FILES)
    print(f"Loading shapes:   {', '.join(SHAPES_FILES)}")
    shapes = load_graph(SHAPES_FILES)
    print(f"  ontology: {len(ont)} triples · shapes: {len(shapes)} triples\n")

    if args.shapes_only:
        print("Ontology and shapes parsed OK.")
        return 0

    targets = args.targets or sorted(str(p) for p in (ROOT / "usecases").glob("*.md"))
    fails, skipped, passed, warned = [], [], [], []

    for t in targets:
        target = ROOT / t if not Path(t).is_absolute() else Path(t)
        rel = target.relative_to(ROOT) if str(target).startswith(str(ROOT)) else target
        try:
            data, note = build_data_graph(target, ont)
        except Exception as exc:  # parse error in the extracted turtle
            fails.append(rel)
            print(f"✗ {rel}\n    PARSE ERROR: {exc}")
            continue
        if data is None:
            skipped.append(rel)
            print(f"– {rel}  (skipped: {note})")
            continue

        try:
            _, _, report_text = validate(
                data_graph=data,  # ontology already merged in
                shacl_graph=shapes,
                inference="rdfs",
                advanced=True,
                meta_shacl=False,
            )
        except Exception as exc:  # a bad file must not abort the whole suite
            fails.append(rel)
            print(f"✗ {rel}\n    VALIDATION ERROR: {exc}")
            continue

        # SHACL conformance depends only on sh:Violation results; warnings/info
        # do not break conformance (pyshacl's `conforms` flag is stricter).
        n = report_text.count("Severity: sh:Violation")
        w = report_text.count("Severity: sh:Warning")
        if n == 0:
            (warned if w else passed).append(rel)
            wtxt = f"  (⚠ {w} warning(s))" if w else ""
            print(f"✓ {rel}  ({len(data)} triples){wtxt}")
        else:
            fails.append(rel)
            wtxt = f", {w} warning(s)" if w else ""
            print(f"✗ {rel}  ({n} violation(s){wtxt})")
            if args.verbose:
                print("\n".join("    " + ln for ln in report_text.splitlines()))

    print(f"\n{'='*60}")
    print(f"PASS {len(passed)} · WARN-ONLY {len(warned)} · FAIL {len(fails)} · SKIP {len(skipped)}")
    if fails and not args.verbose:
        print("Re-run with -v <file> to see violation details.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
