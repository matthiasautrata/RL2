# RL2 Project Guidance

Orientation for collaborators — human or AI. Read this first.

## 1. What RL2 Is

RL2 (Rights Language 2) is a policy language for digital rights and data governance — a candidate
semantic extension and clarification of ODRL 2.2. It adds Hohfeldian normative positions and
Promise Theory while making policy evaluation deterministic enough for independent evaluators to
agree. The project scope is the language, its pure evaluation semantics, ODRL migration, and
conformance suite (SCOPE-2, `spec/RL2_Scope.md`).

**Foundation:** RDF, OWL, SHACL, ODRL, I/O Logic, deontic logic.

**Two governing quality attributes:**
- **Generatable** — exactly one valid RDF shape per normative proposition (canonical form).
- **Verifiable** — every construct has deterministic, bounded, testable evaluation semantics.

## 2. Project Phase

**Current:** SCOPE-2 reorganization and core semantic consolidation. The active control document
is `project/reorganization-plan.md`; the active issue tracker is `project/issues.md`.

**Scope decision (SCOPE-2, 2026-07-31):** RL2 standardizes observable policy meaning through a
pure evaluation contract over a policy universe, request, immutable world snapshot, and evaluation
configuration. Persistent Cases, event sourcing, scheduling, retry/commit protocols, distributed
coordination, optimized IRs, and implementation toolchains are outside the normative core. They
are retained under `future/` as possible companion or follow-on work.

## 3. Working Stance

- **Skeptical.** Validate logic and edge cases. Does this make sense? Is it defensible?
- **Minimal.** Prefer parameters over verbosity. If something can be derived, don't declare it.
- **Precise.** Every word earns its place. No filler.
- **Reuse before invention.** Extend existing constructs before creating new ones.
- **Verify when uncertain.** Check authoritative sources before asserting facts.

## 4. Sources of Truth

When documents conflict, higher-priority sources win:

1. **Core TTL + SHACL** (`spec/rl2.ttl`, `spec/rl2-shacl.ttl`)
2. **Information model** (`spec/RL2_Model.md`)
3. **Formal semantics** (`spec/RL2_Semantics.md`)
4. **ODRL migration rules** (`spec/RL2_ODRL_Mapping.md`)
5. **Conformance vectors** (`conformance/`), for observable behavior covered by a vector
6. **Reader documentation** (`docs/`), informative
7. **Future protocol/reference material** (`future/`), non-core and non-normative

If prose contradicts TTL/SHACL, the TTL/SHACL is correct and prose must be updated.

## 5. Architecture Invariants

The target SCOPE-2 pipeline is pure:

1. **Canonical projection** — validated RDF maps to one normalized policy AST.
2. **Derivation** — `Out(U, Env)` produces attributed normative atoms for a fixed snapshot.
3. **Status interpretation** — duties and promises are classified declaratively from snapshot evidence.
4. **Resolution** — `resolveDecision` produces one explained evaluation result.

Do not introduce persistence, event arrival, Case lifecycle, retry, commit, or enforcement into
these stages. Derivation is monotone in the policy universe for a fixed environment; it is not
monotone in facts containing anti-monotone conditions.

## 6. Canonical Form

For any normative proposition RL2 can express, there is **exactly one** valid RDF shape. Two graphs that differ structurally must differ semantically.

When adding or changing vocabulary, check against this invariant:
- No polymorphic property whose range is a union of semantically distinct types — split into distinct properties.
- No property expressible at multiple container levels with the same effect — pick the narrowest; conjoin-and-normalize the rest at IR compile time.
- No two structural encodings of the same proposition — pick one; reject the other in SHACL or rewrite during compilation.

If a construct creates a second way to say the same thing, that is a defect, not a convenience.
Canonical projection is normative; raw RDF graph identity is not semantic identity.

## 7. Vocabulary Stability

Stable identifiers — do not rename or alias:
- State values (Pending, Active, Fulfilled, Violated)
- Norm classes (Privilege, Duty, Prohibition, Claim, Power, Liability, Immunity)
- Role properties (subject, counterparty, grantor, grantee)

Changes to core ontology files (`spec/rl2.ttl`, `spec/rl2-shacl.ttl`) require explicit discussion.
Do not weaken SHACL constraints or rename stable core IRIs. Protocol identifiers under `future/`
are not part of core conformance.

## 8. Formal Properties

Changes to inference rules, transition systems, typing judgments, or formal definitions must preserve:
- **Specifiability** (algebraic datatypes, syntax-directed rules, structural-recursion termination)
- **Monotonicity of derivation in the policy universe for a fixed snapshot**
- **Totality of the evaluator** (terminates for all well-formed inputs; polynomial under stated constraints)
- **Determinism** (same inputs → same outputs)

When in doubt about whether a change affects formal properties, flag it.

## 9. Semantic Conservatism

Before introducing new policy types, condition forms, norm categories, or state fields — check whether existing constructs already cover the use case. Extension is fine when justified; invention for convenience is not.

## 10. Change Discipline

- Apply the smallest change that satisfies the goal.
- Don't refactor unrelated code or prose.
- Don't reorganize structure unless asked.
- Scope changes to files explicitly mentioned.
- Helpful "cleanup" often introduces inconsistency or breaks things downstream.

## 11. Ambiguity

If an instruction is unclear, ask. Don't guess. Reasonable assumptions often aren't.

## 12. Key Files

| File | Purpose |
|------|---------|
| `spec/RL2_Scope.md` | Governing SCOPE-2 boundary |
| `spec/RL2_Model.md` | Normative evaluation inputs and outputs |
| `spec/rl2.ttl` | Normative core ontology (OWL) |
| `spec/rl2-shacl.ttl` | Normative core validation shapes |
| `spec/RL2_Semantics.md` | Formal language semantics |
| `spec/RL2_ODRL_Mapping.md` | ODRL 2.2 migration and compatibility |
| `conformance/usecases/` | Use-case and conformance corpus |
| `docs/RL2_Primer.md` | Tutorial introduction |
| `docs/RL2_Architecture.md` | Informative architecture and boundaries |
| `docs/RL2_Vocabulary.md` | Derived class/property reference |
| `future/protocol/` | Non-core protocol work |
| `future/reference-implementation/` | Non-core IR/evaluator design |
| `project/reorganization-plan.md` | Active SCOPE-2 execution plan |
| `project/issues.md` | Active issue tracker |
| `project/issues-log.md` | Resolved/historical issue archive |
| `tools/validate.py` | SHACL validation harness for use cases and spec examples |

**Issue-tracker workflow.** The tracker is split by status: `project/issues.md` holds only active work
(open issues, open decisions, the current remediation backlog), and `project/issues-log.md` is the
append-only archive (resolved entries with their rationale, the full changelog, deep-sweep
WP-0…5, and the § Resolved decisions). Read `project/issues.md` for what's next; consult
`project/issues-log.md`
when an active entry cross-references a resolved decision ("SEM-9 (Resolved)", "WP-4/S7", "C6b").
**On resolving an issue:** move its entry (with decision + rationale) to
`project/issues-log.md`, and leave a one-line pointer in its band in `project/issues.md` if open
work still references it. New review sweeps append to the log's changelog. Keep the split intact —
don't reintroduce resolved detail into `project/issues.md`.

## 13. Validation

```bash
# Validate all use cases
uv run tools/validate.py

# Validate a spec doc per-fence (each fence is standalone)
uv run tools/validate.py --per-fence spec/RL2_Semantics.md
```

Every Turtle code fence in spec docs and use cases must pass SHACL validation. If you add or change an example, validate it.
