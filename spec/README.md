# RL2 Normative Specification

These artifacts jointly define the RL2 0.7 draft.

| Artifact | Role |
|---|---|
| `RL2_Requirements.md` | What the language must express, and why (scope authority, not language definition) |
| `RL2_Scope.md` | Language and conformance boundary |
| `RL2_Model.md` | Evaluation inputs, outputs, and policy transformations |
| `rl2.ttl` | Core RDF vocabulary |
| `rl2-shacl.ttl` | Canonical structural constraints |
| `RL2_Semantics.md` | Formal evaluation semantics |
| `RL2_ODRL_Mapping.md` | ODRL 2.2 translation and migration rules |
| `profiles/` | Domain vocabulary with typed snapshot bindings |

The ontology, shapes, model, and semantics jointly define the language. ODRL input is translated
to canonical RL2 before evaluation. `RL2_Requirements.md` defines no language construct; it states
the requirements the other artifacts answer to, and governs whether a proposed capability belongs
in core, in a profile, in an adapter, or nowhere.
