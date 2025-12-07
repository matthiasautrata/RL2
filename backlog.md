# RL2 Backlog

**Updated:** 2025-12-07

---

## Design Decisions (Open)

### PNF Semantic Boundary
The PNF proposal (v0.7) commits to "propositional + bounded transitive closure" as the execution semantic class. This excludes general rule evaluation, open quantification, arbitrary joins, and open-world inference. **Action:** Verify this boundary is acceptable by hand-compiling representative use cases (break-glass, separation of duty, GDPR erasure, high-volume entitlements) to PNF and confirming no essential expressiveness is lost.

### Alignment Modules
Optional `owl:equivalentClass` mappings to standard vocabularies (PROV-O for Case/Event, OWL-Time for EffectiveInterval, FOAF for Agent). Enables interoperability while keeping core standalone.

### Common Profile
Baseline actions (`use`, `read`, `modify`, `delete`, `transfer`) and operands (`dateTime`, `purpose`, `recipient`, `spatial`) for cross-implementation interoperability. Enables ODRL compilation without profile-specific mappings.

### Rejection Semantics
Active disapproval vs absence of approval. Options: separate RejectionEvent type, outcome property on ApprovalEvent, or rejection as Prohibition activation. Affects Case lifecycle and audit trails.

### Policy Inheritance
Current position: skeptical. Inheritance requires flattening, has ambiguous override semantics, and hinders auditability. Recommendation: use explicit policy composition instead.

### Context Subject Typing
`rl2p:contextSubject` is untyped. Options: split into IRI/Literal properties, require resource-only, or use SHACL `sh:or` validation.

### Recurrent Duties
No native periodic recurrence (`FREQ=QUARTERLY`). Options: RecurrentDuty subclass, iCal-style rules, or profile-level. Complexity: each instance needs own obligation state. May be addressable via Power exercise creating new duties.

### Duty Consumption Modes
Does fulfilled duty enable one action, unlimited actions, or until expiration? Options: consumption mode property, explicit conditions with counters, or protocol-level tracking. May be addressable via existing mechanisms.

### Profile Guidance
Documentation for RL2-Minimal (Privilege/Prohibition/Duty), RL2-Standard (+Promise/EventConstraint), RL2-Full (+Power/Liability/Immunity/Claim). This is documentation work, not spec change.

---

## Deferred Spec Items

### Namespace
Finalize persistent URI (e.g., `https://w3id.org/rl2/core#`) — pending organizational ownership decision.

### SHACL Enhancements
- State machine validation (ObligationState, PromiseState transitions) — requires SHACL-SPARQL
- Case state machine formalization (rl2p) — requires SHACL-SPARQL
- Inverse property declarations — nice-to-have for SPARQL convenience

### Profiles
- Financial services entitlement profile — out of scope for core
- GDPR/DPV guidance for `rl2:Privacy` — profile-specific

### Implementation-Time
- JSON-LD context file (`rl2-context.jsonld`)
- Comprehensive test suite (positive/negative cases)
- Master specification index — revisit when spec stabilizes

### Cross-Cutting
- Provenance links — use W3C PROV layering when needed

---

## Should

- Tighten SHACL coverage for common patterns (event path + EventConstraint, operand range checks) once executable examples exist

---

## Could

- Add concrete Hohfeldian coverage (Power, Liability, Immunity, Claim, Prohibition) examples
- Expand examples for temporal complexity, xone/Composite conditions, dynamic policy applicability
- Show promise lifecycle beyond "pending → fulfilled" (deadlines/violations)
- Use more privacy profile operands; add resolutionFunction example
- Produce executable .ttl versions of use cases and validate against SHACL

---

## Future Research

- Formal verification targets (Why3, K Framework, Lean 4) — see RL2_ResearchPlan.md
- Data contract alignment (DPROD, ODCS) — RL2 Promise maps naturally to SLO structure
- Authorization engine compilation (Cedar, OPA)
- OPAL comparison — RL2 uses operational semantics vs OPAL's model-theoretic approach; both rigorous, different focus (enforcement vs audit)

---

## Resolved

### Spec Fixes (2025-01-06)
- Created `rl2:RuntimeReference` class, removed broken `DynamicOperandReference`
- Added identity-binding SHACL warning (`DynamicOperandPairingShape`)
- Hardened path grammar with security requirements
- Clarified Promise vs Duty legal distinction in `rl2:PromiseContent`
- Removed `rl2:dynamicQuery` from Core
- Added `sh:xone` mutual exclusion for rightOperand/rightOperandRef
- Aligned abstract syntax names with OWL (Atom→AtomicConstraint, Transition→StateTransition)

### Earlier
- Clarified event path resolution and aligned examples to type-based access
- Fixed promise state access via `state.Promises.<id>.state`
- Added fulfillment audit links on `rl2p:DutyRequirement`
- Dynamic policy applicability — events change which policies apply, not branch duties
- Multi-party agreements — expressible via EventConstraint with `rl2:and`/`rl2:or`
- Expressive completeness — see RL2_Semantics.md §Expressive Characterization
