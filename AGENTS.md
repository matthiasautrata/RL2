# RL2 Project Guidance

RL2 is a deterministic policy language that extends and clarifies ODRL 2.2. Its core proposal is
the language, pure evaluation semantics, ODRL migration contract, and conformance corpus. It is
designed for reliable machine generation while remaining readable as RDF.

## Working principles

- Prefer a smaller orthogonal language to speculative completeness.
- Give every core construct deterministic, bounded, testable semantics.
- Require one canonical RDF form for each expressible proposition.
- Treat missing, invalid, conflicting, and unknown inputs explicitly.
- Keep persistence, protocols, enforcement, and implementation architecture outside the core.
- Check authoritative sources before making claims about ODRL or related standards.

## Sources of truth

When artifacts conflict, use this order:

1. `spec/rl2.ttl` and `spec/rl2-shacl.ttl`
2. `spec/RL2_Model.md`
3. `spec/RL2_Semantics.md`
4. `spec/RL2_ODRL_Mapping.md`
5. `conformance/`
6. informative material under `docs/`

The core norm classes are `Privilege`, `Duty`, and `Prohibition`. `Promise` is Offer content that
materializes into a Duty. Do not add vocabulary without showing that existing constructs cannot
express the use case.

## Evaluation boundary

The evaluator is a pure function over a finite policy universe, request, immutable world snapshot,
and evaluation configuration. Its stages are canonical projection, declarative Duty and Promise
status interpretation, attributed normative derivation, and conflict resolution.

Do not introduce mutable cases, event arrival, scheduling, retries, commits, resource reservation,
or distributed coordination into these stages. `future/README.md` records possible follow-on work;
it is not normative.

## Canonical form

- Do not create polymorphic properties spanning semantically different ranges.
- Do not allow the same proposition at multiple container levels.
- Reject or normalize alternate structural encodings during canonical projection.
- Keep policy and clause provenance in derived results.

Changes to inference rules or formal definitions must preserve determinism, totality under the
declared finite bounds, syntax-directed evaluation, and monotonicity of `Out` in its selected
policy set for a fixed environment.

## Change discipline

- Make the smallest coherent change.
- Update ontology, SHACL, model, semantics, examples, and references together when their contract
  changes.
- Do not include design history, issue identifiers, or obsolete alternatives in publication text.
- Use `uv` for Python tools.
- Use `apply_patch` for manual file edits.

## Validation

```bash
UV_CACHE_DIR=/tmp/rl2-uv-cache uv run tools/validate.py
UV_CACHE_DIR=/tmp/rl2-uv-cache uv run tools/validate.py --per-fence spec/RL2_Semantics.md
```

Every changed Turtle file and Turtle code fence must parse and satisfy the core SHACL shapes.
