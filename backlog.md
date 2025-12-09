# RL2 Backlog

**Updated:** 2025-12-08 (Protocol Completeness implemented)

---

## Design Decisions (Open)

### Profiles
#### minimal for RL2 actions (`use`, `analyze`, `distribute` What else?) and operands (`dateTime`, `purpose`, `recipient`, `spatial`, `organizaton`, `cost-center`) fir minimal interoperability. 
#### ODRL profile: define ODRL standard vocabulary for actions, etc.

### Context Subject Typing
`rl2p:contextSubject` is untyped. Options: split into IRI/Literal properties, require resource-only, or use SHACL `sh:or` validation. **(Status: Verify if already addressed)**

### Recurrent Duties
No native periodic recurrence (`FREQ=QUARTERLY`). Options: RecurrentDuty subclass, iCal-style rules, or profile-level. Complexity: each instance needs own obligation state. Can this be solved with adopting owl:time or schema:schedule or ical in the duty language? Does it need a profile and new operators, really?

### Duty Consumption Modes
Does fulfilled duty enable one action, unlimited actions, or until expiration? Options: consumption mode property, explicit conditions with counters, or protocol-level tracking. May be addressable via existing mechanisms. As designed, duties are tracked back to the policy & duty that created them. I think they should apply wherever that duty applied.

- Add concrete Hohfeldian coverage (Power, Liability, Immunity, Claim, Prohibition) examples
- Expand examples for temporal complexity, xone/Composite conditions, dynamic policy applicability
- Show promise lifecycle beyond "pending → fulfilled" (deadlines/violations)
- Use more privacy profile operands; add resolutionFunction example

## Open Questions

### **Promise→Duty Generation Mechanism:** Alresady resolve??? The `contentHolds` function evaluates Promise conditions, but the explicit mechanism for *creating* Requirements when Promises are violated needs clarification in RL2_Semantics.md. Open Question Resolution (Promise Generation)
You identified a gap in Open Question 1: "The explicit mechanism for creating Requirements when Promises are violated needs clarification."
The Mathematician recommends adding a specific "Remedial Generation Rule" to RL2_Semantics.md.
Concept: When a Sein-Sollen Promise (Invariant) enters the PromiseViolated state, it triggers a StateTransition that instantiates a remedial Duty.
Action: We will draft this rule during the implementation phase to ensure the "Promise as Generator" logic is formally specified.

### **Rejection Semantics:** Already resolved by tracking agent in RL2P? Active disapproval vs absence of approval. Options: separate RejectionEvent type, outcome property on ApprovalEvent, or rejection as Prohibition activation.

### SHACL Enhancements
- State machine validation (ObligationState, PromiseState transitions) — requires SHACL-SPARQL
- Case state machine formalization (rl2p) — requires SHACL-SPARQL
- Inverse property declarations — nice-to-have for SPARQL convenience

---

## Future Research

- Formal verification targets (Why3, K Framework, Lean 4) — see RL2_ResearchPlan.md
- RL2->Rego mapping? Equivalence with others? Cedar, Immuta?
- PNF targets? Rego?
- ODRL->RL2 Transpilation

---

## Resolved

### Temporal Classes Simplification (2025-12-07)
Removed `rl2:TemporalConstraint` and `rl2:EffectiveInterval` from RL2 Core. These were syntactic sugar over `rl2:AtomicConstraint` with datetime comparisons. Added `rl2:currentDateTime` as Core LeftOperand (parallel to `rl2:currentAgent`). All temporal logic now uses explicit AtomicConstraints with comparison operators. Bumped ontology to version 0.5. Benefits:
- Reduced ontology surface area
- Eliminated "magic" semantics (implicit "now" comparison)
- Aligned with PNF propositional goal
- Time is now "just another comparable value"

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


### Protocol Completeness (Promise and Power Tracking)

**Status:** Implemented (v0.5)

#### Problem Statement

`rl2p` tracked only `DutyRequirement`, but RL2 Core defines richer constructs:
- `Promise` has its own lifecycle (`PromiseState`) but couldn't be tracked
- `Claim` (the correlative of Duty) had no explicit representation
- Power exercise was implicit — no audit link for "show all Emergency Override uses"

#### Resolution: Universal Requirement

**Core Insight — Promise as Generator (Sein-Sollen vs Tun-Sollen):**
- **Promise = Sein-Sollen (Ought-to-Be):** Required state of the world (invariant)
- **Duty = Tun-Sollen (Ought-to-Do):** Action to achieve/restore that state (remedy)

When the world deviates from the Promise's invariant, the evaluator generates a Duty/Requirement to fix it.

**Protocol Changes:**

| Change | From | To |
|--------|------|-----|
| Rename class | `DutyRequirement` | `rl2p:Requirement` |
| Genericize source | `requiresDuty` (range: `rl2:Duty`) | `rl2p:sourceNorm` (range: `rl2:Norm \| rl2:Promise`) |
| Add beneficiary | — | `rl2p:counterparty` (for Claims) |

**Impact:**
- **RL2 Core:** No change. Retains semantic distinctions.
- **RL2 Protocol:** Simplified. One structure tracks all runtime obligations.

**Hohfeldian Mapping:**

| Hohfeldian Norm | Runtime Meaning | Protocol Artifact |
|-----------------|-----------------|-------------------|
| Duty | "Must Do" | `rl2p:Requirement` |
| Promise | "Must Do" (Voluntary) | `rl2p:Requirement` (sourceNorm → Promise) |
| Claim | "Owed To" | `rl2p:Requirement` (with counterparty) |
| Privilege | "Can Do" | `rl2p:Decision` (Permit) |
| Power | "Can Change" | `rl2p:Decision` (Permit State Change) |
| Immunity | "Cannot Be Changed" | `rl2p:Decision` (Deny State Change) |
| Liability | "Can Be Changed" | Implicit (side effect of Power) |

#### Design Decisions (Resolved)

1. **State Machine:** Use `rl2:ObligationState` uniformly for all Requirements. The Promise vs Duty distinction lives in `sourceNorm`, not in status.

2. **Power Exercise Audit:** `rl2p:Decision` is sufficient. Power exercise can be inferred from Decision + matched norms. No explicit `exercisedPower` property needed.
