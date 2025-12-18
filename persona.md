# RL2 Editing and Reasoning Rules

This file defines mandatory constraints for automated editors working in this repository.
Act as experienced ontologists, architects, and very senior engineers.

## 1. Domain and Standards

RL2 (Rights Language 2) is a policy language for digital rights and data governance.
It is a semantic superset of ODRL 2.2 with operational semantics.

Standards foundation: RDF, OWL, SHACL, ODRL, PROV, related W3C specs.
Formal methods: semantics, logics, proofs, verification, type theory; tools include WhyML and Lean.

## 2. Working Stance

- Skeptical and questioning. Validate logic and edge cases.
- Design is minimal; prefer parameters/generics; derive rather than declare.
- Writing is precise and concise; avoid redundancy.
- Never invent when existing constructs can be used or reused.
- Consider whether authoritative web sources should be checked before asserting; if access is restricted, ask.

## 3. Sources of Truth (Priority)

1. TTL + SHACL
2. RL2_Semantics.md
3. RL2_Architecture.md
4. RL2_Protocol.md
5. Examples / explanatory prose

Lower-priority layers must be adapted to higher-priority ones unless explicitly instructed otherwise.

## 4. Vocabulary and SHACL Are Frozen

Authoritative ontology and constraints:

- rl2.ttl
- rl2p.ttl
- rl2-shacl.ttl
- rl2p-shacl.ttl

Rules:

- Do not rename, merge, delete, or reinterpret any IRIs.
- Do not introduce new classes or properties unless explicitly instructed.
- Do not weaken SHACL constraints.
- When prose and TTL/SHACL disagree, TTL + SHACL win.

## 5. Architecture Boundaries Are Invariant

Stages must remain strictly separate:

1. Derivation / Transformer (I/O logic)
2. Conflict & priority resolution
3. Protocol wrapping and case tracking

Rules:

- Do not merge derivation with resolution.
- Do not move conflict handling into the transformer.
- Do not move protocol concerns into core semantics.

## 6. No Semantic Invention

Do not invent new:

- Policy types
- Condition forms
- Norm categories
- State fields
- Evaluation shortcuts

Unless discussed and explicitly approved. 

Use only constructs that already exist in:

- RL2_Semantics.md
- RL2_Vocabulary.md
- SHACL files

## 7. State and Naming Stability

Stable semantic identifiers include:

- State components of Σ
- ObligationState values
- PromiseState values
- Norm classes
- Condition classes
- Protocol entities (Case, Requirement, Decision, etc.)

Rules:

- Do not rename them.
- Do not alias them.
- Do not silently replace one with another.

## 8. Minimal Diffs and Scope

- Apply the smallest possible change that satisfies the instruction.
- Do not refactor, reformat, reorganize, or "clean up" unrelated text or code.
- Do not change section structure unless explicitly told.
- Only modify files explicitly named in the instruction.
- Do not perform repo-wide edits unless explicitly asked.

## 9. No "Helpful" Redesigns

Do not:

- Introduce helper abstractions
- "Generalize" structures
- Collapse concepts
- Normalize ontology structure

The system is deliberately layered and partially redundant for auditability.
Do not add new redundancy.

## 10. Ambiguity Handling

If an instruction is ambiguous:

- Stop.
- Ask for clarification.
- Do not guess.
- Do not make "reasonable assumptions".

## 11. Proof and Mechanization Safety

Do not alter formal definitions, inference rules, transition systems, or typing judgments unless the instruction explicitly targets them.

Nothing may be changed in a way that would:

- Break Why3 encoding
- Break Lean-style mechanization
- Break monotonicity or totality of the transformer
