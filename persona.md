# RL2 Project Context and Guidance

This document provides context and principles for working with the RL2 specification. Think of it as orientation for collaborators — human or AI.

## 1. Domain

RL2 (Rights Language 2) is a policy language for digital rights and data governance. It is a semantic superset of ODRL 2.2, adding operational semantics and formal verification.

**Standards foundation:** RDF, OWL, SHACL, ODRL, PROV, related W3C specs.

**Formal methods:** Semantics, logics, proofs, verification, type theory. Primary tooling is Dafny (with Go extraction); Lean and other proof assistants may be used for independent validation.

## 2. Working Stance

- **Skeptical and questioning.** Validate logic and edge cases. Ask: does this make sense?
- **Minimal design.** Prefer parameters/generics over verbosity. If something can be derived, don't declare it.
- **Precise writing.** Every word earns its place. No filler.
- **Reuse before invention.** Existing constructs should be used or extended before creating new ones.
- **Verify when uncertain.** Check authoritative sources before asserting facts. Ask if access is restricted.

## 3. Sources of Truth

Documents have a priority order. When they conflict, higher-priority sources win:

1. **TTL + SHACL** (rl2.ttl, rl2p.ttl, rl2-shacl.ttl, rl2p-shacl.ttl)
2. **RL2_Semantics.md**
3. **RL2_Architecture.md**
4. **RL2_Protocol.md**
5. **RL2_Vocabulary.md** (derived from TTL; explanatory)
6. **Examples and prose** (illustrative, not normative)

If prose contradicts TTL/SHACL, the TTL/SHACL is correct and prose should be updated.

## 4. Vocabulary Stability

The ontology files define stable IRIs and structures:

- rl2.ttl, rl2p.ttl — class and property definitions
- rl2-shacl.ttl, rl2p-shacl.ttl — validation constraints

Changes to these files require explicit discussion. Avoid:
- Renaming or reinterpreting existing IRIs
- Adding new classes/properties without clear need
- Weakening SHACL constraints

## 5. Architecture Invariants

RL2 has a strict three-stage evaluation pipeline:

1. **Derivation** — I/O logic transformer, monotone
2. **Conflict resolution** — strategy-based, non-monotone
3. **Protocol wrapping** — case tracking, requirements

These stages exist for good reasons (verifiability, auditability, performance). Mixing concerns across stages breaks important properties. When proposing changes, consider which stage they belong to.

## 6. Semantic Conservatism

The language is intentionally constrained. Before introducing new:
- Policy types
- Condition forms
- Norm categories
- State fields

...check whether existing constructs already cover the use case. Extension is fine when justified; invention for convenience is not.

## 7. Naming Stability

These identifiers are stable and should not be renamed or aliased:
- State components (Σ.Events, Σ.ObligationState, etc.)
- State values (Pending, Active, Fulfilled, Violated)
- Norm classes (Privilege, Duty, Prohibition, Claim, Power, Liability, Immunity)
- Protocol entities (Case, Requirement, Decision, EvaluationResult)

Consistency across documents matters for mechanization.

## 8. Change Discipline

When making changes:
- Apply the smallest change that satisfies the goal
- Don't refactor unrelated code or prose
- Don't reorganize structure unless asked
- Scope changes to files explicitly mentioned

Helpful "cleanup" often introduces inconsistency or breaks things downstream.

## 9. Ambiguity

If an instruction is unclear, ask. Don't guess. Reasonable assumptions often aren't.

## 10. Formal Properties

RL2 is designed for mechanization. Changes to:
- Inference rules
- Transition systems
- Typing judgments
- Formal definitions

...must preserve:
- Dafny/Lean encodability
- Monotonicity of derivation
- Totality of the evaluator

When in doubt about whether a change affects formal properties, flag it.
