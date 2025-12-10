# RL2 Backlog

**Updated:** 2025-12-08 (Protocol Completeness implemented)

---

## Design Decisions (Open)

### Profiles
#### minimal for RL2 actions (`use`, `analyze`, `distribute` What else?) and operands (`dateTime`, `purpose`, `recipient`, `spatial`, `organizaton`, `cost-center`) for minimal interoperability. 
#### ODRL profile: define ODRL standard vocabulary for actions, etc.


### Examples/use-cases

- Add concrete Hohfeldian coverage (Power, Liability, Immunity, Claim, Prohibition) examples
- Expand examples for temporal complexity, xone conditions, dynamic policy applicability
- Show promise lifecycle beyond "pending → fulfilled" (deadlines/violations)
- Use more privacy profile operands; add resolutionFunction example

## Future Research

- Formal verification targets (Why3, K Framework, Lean 4) — see RL2_ResearchPlan.md
- RL2->Rego mapping? Equivalence with others? Cedar, Immuta?
- PNF targets? Rego?
- ODRL->RL2 Transpilation


## RL2 Modularization

Yeah, this is exactly the right next move.

You’re basically saying:

> “Before we argue in the abstract, let’s see which *actual* policies translate cleanly, and where we need extra structure.”

Let me structure this into something you can actually execute.

---

## 1. Modular RL2: start with a **Core-ODRL** slice

I’d explicitly name the first slice something like:

> **RL2-Core-ODRL**
> “Minimal RL2 needed to cover ODRL 2.2 policies.”

**Scope of RL2-Core-ODRL:**

* `Policy`
* `Privilege` (Permission)
* `Prohibition`
* `Duty`
* `Condition`:

  * `AtomicConstraint`
  * `LogicalConstraint` (and/or/xone/not)
* Basic operands:

  * Attribute + temporal operands (`currentDateTime`, etc.)
* No Promises (yet)
* No explicit Hohfeld claims/powers
* No Protocol/Case machinery (only semantic level)

You still allow:

* **Consequences/remedies** → just as state-triggered duties (that’s already in your coverage doc)
* **Duty state** (`Pending/Active/Fulfilled/Violated`)
* **EventConstraint** only insofar as needed to match ODRL’s event-like constraints

Everything else (Promises, rich Hohfeld lattice, Protocol, Requirements) is “out-of-module” for now.

---

## 2. Follow-on modules to add later

Just to have the mental map:

1. **RL2-Promises**

   * `Promise`, `PromiseState`
   * Promise → Violation → Remedial Duty patterns

2. **RL2-Hohfeld**

   * Explicit Rights/Claims/Powers/Liabilities
   * Structured correlatives beyond subject/counterparty

3. **RL2-Events**

   * Rich event types
   * Event-driven policies (beyond what ODRL had)

4. **RL2-Protocol**

   * Cases, Requirements, ContextAssertions, generations

Each module can be “opt-in” for:

* The language spec
* The transpiler
* The runtime

So initially, the transpiler targets **RL2-Core-ODRL** only.

---

## 3. What the “lots of plausible use cases” should look like

I’d deliberately build a **use-case suite** as *test vectors* for RL2-Core-ODRL.

Pick 6–8 domains that ODRL people will recognize immediately:

1. **Media streaming license**

   * “User may play song X for 30 days after purchase; no redistribution.”
2. **Paid download**

   * “May download once after paying 5 units; no sharing.”
3. **Data analytics license**

   * “Researcher may use dataset for non-commercial analytics; no re-identification.”
4. **Geo-restriction**

   * “View only from EU IP ranges.”
5. **Retention + deletion**

   * “May store data for 90 days; must delete after.”
6. **Rate-limited API**

   * “Client may call API 10k times per day.”
7. **Break-glass access**

   * “In emergency, doctor may access record if obligation to justify access is created.”
8. **Sub-licensing restriction**

   * “May use, but may not sublicence to third parties.”

For each use case, give **three parallel views**:

1. **Natural-language requirement**
2. **(Idealized) ODRL 2.2 sketch**
3. **RL2-Core-ODRL encoding**:

   * Policies + Privileges/Prohibitions/Duties
   * Conditions only
   * Duty state constraints where needed

Then annotate:

* ✅ “Covered entirely by RL2-Core-ODRL”
* ⚠️ “Requires RL2-Promises”
* ⚠️ “Requires RL2-Protocol (Requirements)”
* ⚠️ “Requires RL2-Events beyond ODRL”

This becomes your **concrete answer** to:

> “Show me the policy that doesn’t translate.”

Sometimes you’ll say:

* “It does translate, but needs module X.”
* or “It translates but we must make assumption Y explicit (clarification report).”

---

## 4. How this feeds the transpiler + objections

With this setup:

* The **transpiler** target is explicitly:

  * Phase 1: RL2-Core-ODRL
  * Phase 2: + Promises, + Events, etc.
* For each input policy, the transpiler can report:

  * Which module(s) were needed
  * Which clarifications were assumed

That lets you say, calmly, to any critic:

> “Here are 20 real-world policies.
> 15 translate in pure RL2-Core-ODRL.
> 3 need Promises.
> 2 need Events.
> And here are the exact assumptions we had to make.”

That’s a devastatingly strong position.

---

## 5. Concrete next step we can do together

If you want to move immediately, we can:

* Define **RL2-Core-ODRL** as a short section (list of included constructs).
* Then work through, say, **3 use cases** end-to-end:

  * Media streaming
  * Non-commercial data analytics
  * Break-glass

Each with: NL → ODRL sketch → RL2-Core-ODRL encoding.

Once you have that pattern, you can scale it out to 20–50 cases over time.

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

3. Duty Consumption Modes
Does fulfilled duty enable one action, unlimited actions, or until expiration? Options: consumption mode property, explicit conditions with counters, or protocol-level tracking. May be addressable via existing mechanisms. As designed, duties are tracked back to the policy & duty that created them. I think they should apply wherever that duty applied. Decison: Will leave as is. Duties are not counted like coupons. Can be implemented externally.

4. Recurrent Duties
No native periodic recurrence (`FREQ=QUARTERLY`). Options: RecurrentDuty subclass, iCal-style rules, or profile-level. Complexity: each instance needs own obligation state. Can this be solved with adopting owl:time or schema:schedule or ical in the duty language? Does it need a profile and new operators, really?
