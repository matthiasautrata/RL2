# RL2 Backlog

**Date:** 2025-01-05
**Status:** Post-v0.4 Implementation

---

## Completed in v0.4

### Permission-Bound Duties (ODRL Compatibility)

**Status:** COMPLETED

Implemented the Unified State Approach for conditioning privileges on prior duty fulfillment:

- Added `rl2:targetNorm`, `rl2:obligationStateOperand`, `rl2:dutyPerformerOperand`, `rl2:currentAgent`, `rl2:priority` to ontology
- Updated Σ to include `DutyPerformer` tracking
- Extended `resolve()` function for norm-targeted operands
- Added `rl2p:performer` to protocol
- Updated all documentation and use cases

See commit history for implementation details.

---

## Remaining Items

### Other ODRL Compatibility Issues

#### Inheritance (`odrl:inheritFrom`)

RL2 explicitly excludes runtime inheritance, requiring a pre-processing/flattening step. While semantically equivalent results can be achieved, it is not a syntactic superset.

**Recommendation:** Explicitly document the transformation required for `inheritFrom` in ODRL mapping documentation.

#### Conflict Strategies (`odrl:conflict`)

ODRL allows policies to specify their conflict resolution strategy (e.g., `perm:perm`, `prohibit:perm`). RL2 relies on numeric priorities and compilation-time resolution.

**Recommendation:** Document how ODRL conflict strategies map to RL2 priority-based resolution in ODRL coverage documentation.

#### Policy Request Type

ODRL defines `odrl:Request` as a policy class. `rl2.ttl` lacks a policy-level Request; `rl2p.ttl` introduces a runtime `rl2p:Request` (evaluation artifact, not a policy container).

**Recommendation:** Add `rl2:Request` policy subclass or document mapping for `odrl:Request` policies.

---

### Documentation Claim Refinement

The claim in `RL2_ODRL_Coverage.md` that "RL2 is a strict superset of ODRL" should be softened to **"Semantic Superset"** or **"Expressive Superset"** to acknowledge that transformation/compilation is required for certain ODRL features (inheritance, permission-bound duties with different actions).

---

## Future Considerations

- Formal verification targets (Why3, K Framework, Lean 4) - see RL2_ResearchPlan.md
- Data contract alignment (DPROD, ODCS) - see RL2_White_Paper.md
- Authorization engine compilation (Cedar, OPA) - ongoing research
