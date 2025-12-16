# codex.md — Operational Rules for Automated Editing in the RL2 Repository

This file defines strict, machine-enforceable constraints for automated editors.
It complements (not replaces) claude.md.

Claude governs *thinking and reasoning*.
Codex governs *safe execution and editing*.

These rules are mandatory.

---

## 1. Vocabulary and SHACL Are Frozen

The following files define the **authoritative ontology and constraints**:

- rl2.ttl
- rl2p.ttl
- rl2-shacl.ttl
- rl2p-shacl.ttl

Rules:
- Do NOT rename, merge, delete, or reinterpret any IRIs.
- Do NOT introduce new classes or properties unless explicitly instructed.
- Do NOT weaken SHACL constraints.
- When prose and TTL/SHACL disagree: **TTL + SHACL win.**

---

## 2. Architecture Boundaries Are Invariant

The following stages MUST remain strictly separate:

1. Derivation / Transformer (I/O logic)
2. Conflict & priority resolution
3. Protocol wrapping and case tracking

Rules:
- Do NOT merge derivation with resolution.
- Do NOT move conflict handling into the transformer.
- Do NOT move protocol concerns into core semantics.

---

## 3. Minimal Diffs Only

Rules:
- Apply the **smallest possible change** that satisfies the instruction.
- Do NOT refactor, reformat, reorganize, or “clean up” unrelated text or code.
- Do NOT change section structure unless explicitly told.

---

## 4. No Semantic Invention

Rules:
- Do NOT invent new:
  - Policy types
  - Condition forms
  - Norm categories
  - State fields
  - Evaluation shortcuts
- Use only constructs that already exist in:
  - RL2_Semantics.md
  - RL2_Vocabulary.md
  - SHACL files

---

## 5. State and Naming Stability

The following are **stable semantic identifiers**:

- State components of Σ
- ObligationState values
- PromiseState values
- Norm classes
- Condition classes
- Protocol entities (Case, Requirement, Decision, etc.)

Rules:
- Do NOT rename them.
- Do NOT alias them.
- Do NOT silently replace one with another.

---

## 6. Cross-File Consistency Rule

Priority order when conflicts exist:

1. TTL + SHACL
2. RL2_Semantics.md
3. RL2_Architecture.md
4. RL2_Protocol.md
5. Examples / explanatory prose

Rules:
- Lower-priority layers must be adapted to higher-priority ones.
- Never the reverse unless explicitly instructed.

---

## 7. No “Helpful” Redesigns

Rules:
- Do NOT:
  - Introduce helper abstractions
  - “Generalize” structures
  - Collapse concepts
  - Normalize ontology structure
- The system is deliberately layered and partially redundant for auditability.

---

## 8. Ambiguity Handling

If an instruction is ambiguous:

- STOP.
- ASK for clarification.
- Do NOT guess.
- Do NOT make “reasonable assumptions”.

---

## 9. Proof and Mechanization Safety

Rules:
- Do NOT alter:
  - Formal definitions
  - Inference rules
  - Transition systems
  - Typing judgments
unless the instruction explicitly targets them.

Nothing may be changed in a way that would:
- Break Why3 encoding
- Break Lean-style mechanization
- Break monotonicity or totality of the transformer

---

## 10. Scope Control

Rules:
- Only modify files explicitly named in the instruction.
- Do NOT perform repo-wide edits unless explicitly asked.

---

End of codex.md
