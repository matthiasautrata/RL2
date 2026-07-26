# RL2 Project Guidance

Orientation for collaborators — human or AI. Read this first.

## 1. What RL2 Is

RL2 (Rights Language 2) is a policy language for digital rights and data governance — a semantic superset of ODRL 2.2, designed as a candidate for ODRL 3.0. It adds Hohfeldian normative positions, Promise Theory, operational semantics, and formal verification.

**Foundation:** RDF, OWL, SHACL, ODRL, I/O Logic, deontic logic.

**Two governing quality attributes:**
- **Generatable** — exactly one valid RDF shape per normative proposition (canonical form).
- **Verifiable** — every construct maps deterministically to a bounded evaluation machine.

## 2. Project Phase

**Current:** Spec work — extensions, semantics for ontology and protocol. Bands 1-3 in `issues.md` (SEM-1..8, HOHF-1..5, PROM-1..8, EXPR-1..6). The ontology and protocol are the priority; documentation follows.

**Next (parallel, gradual):** Dafny/Go implementation, starting with a de-risking spike — replicate a minimal evm-dafny-style proof (3-4 opcodes) in Dafny 4.11, extract to Go, confirm it works. Use [Consensys/evm-dafny](https://github.com/Consensys/evm-dafny) as architectural reference. Creusot (verify Rust directly) is the fallback if the Dafny→Go spike fails. See `research/verification-toolchain-comparison.md` for the full toolchain comparison.

Spec work takes precedence until it nears a stable state. Do not start Dafny implementation until the open SEM issues are resolved.

## 3. Working Stance

- **Skeptical.** Validate logic and edge cases. Does this make sense? Is it defensible?
- **Minimal.** Prefer parameters over verbosity. If something can be derived, don't declare it.
- **Precise.** Every word earns its place. No filler.
- **Reuse before invention.** Extend existing constructs before creating new ones.
- **Verify when uncertain.** Check authoritative sources before asserting facts.

## 4. Sources of Truth

When documents conflict, higher-priority sources win:

1. **TTL + SHACL** (rl2.ttl, rl2p.ttl, rl2-shacl.ttl, rl2p-shacl.ttl)
2. **RL2_Semantics.md**
3. **RL2_Architecture.md**
4. **RL2_IR.md** (compilation-target design; must match Semantics via the equivalence obligation)
5. **RL2_Protocol.md**
6. **RL2_Vocabulary.md** (derived from TTL; explanatory)
7. **Examples and prose** (illustrative, not normative)

If prose contradicts TTL/SHACL, the TTL/SHACL is correct and prose must be updated.

## 5. Architecture Invariants

Three-stage evaluation pipeline:

1. **Derivation** — I/O logic transformer, monotone. `Out(U, Env)` produces normative atoms.
2. **Conflict resolution** — strategy-based, non-monotone. `resolveDecision` picks a decision.
3. **Protocol wrapping** — case tracking, requirements.

Do not mix concerns across stages. Derivation must be monotone and total; resolution is where defeasibility lives. Separation is what makes polynomial-time evaluation and formal verification possible.

## 6. Canonical Form

For any normative proposition RL2 can express, there is **exactly one** valid RDF shape. Two graphs that differ structurally must differ semantically.

When adding or changing vocabulary, check against this invariant:
- No polymorphic property whose range is a union of semantically distinct types — split into distinct properties.
- No property expressible at multiple container levels with the same effect — pick the narrowest; conjoin-and-normalize the rest at IR compile time.
- No two structural encodings of the same proposition — pick one; reject the other in SHACL or rewrite during compilation.

If a construct creates a second way to say the same thing, that is a defect, not a convenience. See `RL2_Architecture.md` §Canonical Form.

## 7. Vocabulary Stability

Stable identifiers — do not rename or alias:
- State components (Σ.Events, Σ.ObligationState, Σ.DutyPerformer, etc.)
- State values (Pending, Active, Fulfilled, Violated)
- Norm classes (Privilege, Duty, Prohibition, Claim, Power, Liability, Immunity)
- Protocol entities (Case, Requirement, Decision, EvaluationResult)
- Role properties (subject, counterparty, grantor, grantee)

Changes to ontology files (rl2.ttl, rl2p.ttl, rl2-shacl.ttl, rl2p-shacl.ttl) require explicit discussion. Do not weaken SHACL constraints or rename existing IRIs.

## 8. Formal Properties

Changes to inference rules, transition systems, typing judgments, or formal definitions must preserve:
- **Dafny encodability** (algebraic datatypes, syntax-directed rules, fuel-bounded execution)
- **Monotonicity of derivation** (`Out` is monotone in facts)
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
| `rl2.ttl` | Normative ontology (OWL) |
| `rl2-shacl.ttl` | Validation shapes |
| `rl2p.ttl` | Protocol ontology |
| `rl2p-shacl.ttl` | Protocol validation shapes |
| `RL2_Semantics.md` | Formal denotational + operational semantics |
| `RL2_Architecture.md` | Evaluation pipeline, functional model, design rationale |
| `RL2_IR.md` | Intermediate representation (compilation target, construct correspondence, equivalence obligation) |
| `RL2_Protocol.md` | Runtime evaluation protocol |
| `RL2_Vocabulary.md` | Complete class/property reference (derived from TTL) |
| `RL2_Primer.md` | Tutorial introduction |
| `issues.md` | Consolidated issue tracker with priority bands |
| `tools/validate.py` | SHACL validation harness for use cases and spec examples |

## 13. Validation

```bash
# Validate all use cases
uv run tools/validate.py

# Validate a spec doc per-fence (each fence is standalone)
uv run tools/validate.py --per-fence RL2_Semantics.md
```

Every Turtle code fence in spec docs and use cases must pass SHACL validation. If you add or change an example, validate it.
