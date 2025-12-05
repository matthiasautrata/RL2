# RL2 Backlog

**Date:** 2025-01-05
**Status:** Post-v0.4 Implementation

---

# RL2 Backlog

**Date:** 2025-01-05
**Status:** Post-v0.4 Implementation

  Should
  - Tighten SHACL coverage for common patterns (e.g., event path + EventConstraint, operand range checks) once executable examples exist.


  Could

  - Add concrete Hohfeldian/Prohibition coverage (Power, Liability, Immunity, Claim, Prohibition) so the core norm types in rl2.ttl and RL2_Primer.md are actually exercised.
  - Expand examples for temporal complexity, xone/Composite conditions, and dynamic policy applicability to match operators and condition types already defined in RL2_Semantics.md and rl2.ttl.
  - Show promise lifecycle beyond “pending → fulfilled” (deadlines/violations) to reflect the Promise rules in RL2_Semantics.md.
  - Use more of the privacy profile operands and add at least one resolutionFunction example to illustrate both resolution modes promised in RL2_Vocabulary.md and the profile files.
  - Produce executable .ttl versions of the use cases and run them through rl2-shacl.ttl / rl2p-shacl.ttl; right now nothing is machine-validated.



---

## Future Considerations

- Formal verification targets (Why3, K Framework, Lean 4) - see RL2_ResearchPlan.md
- Data contract alignment (DPROD, ODCS) - see RL2_White_Paper.md
- Authorization engine compilation (Cedar, OPA) - ongoing research



## Future Considerations

- Formal verification targets (Why3, K Framework, Lean 4) - see RL2_ResearchPlan.md
- Data contract alignment (DPROD, ODCS) - see RL2_White_Paper.md
- Authorization engine compilation (Cedar, OPA) - ongoing research

## Resolved

- Clarified event path resolution and aligned examples to type-based access (`RL2_Semantics.md`, `usecases/break-glass.md`, `usecases/ethics-approval.md`)
- Fix promise state access by modeling Σ.Promises as PromiseRecord map with state accessor; examples now use `state.Promises.<id>.state` (`RL2_Semantics.md`, `usecases/data-stewardship.md`)
- Deprecated `rl2:dynamicQuery` in Core; asset collections remain with static members, dynamic materialization to be defined per profile (`rl2.ttl`, docs updated)
- Added fulfillment audit links on `rl2p:DutyRequirement` (`fulfilledByAction`, `fulfilledByEvent`, `fulfillmentEvidence`) and documented in protocol example (`rl2p.ttl`, `RL2_Protocol.md`)
