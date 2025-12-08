# RL2 Coverage of ODRL (v0.5)

*A Migration, Transpilation, and Coverage Guide*

---

## Executive Summary

**Can existing ODRL policies be translated to RL2?**
**Yes.** RL2 is designed as a **semantic superset** of ODRL 2.2. Any valid ODRL expression can be compiled into an RL2 representation that preserves its intent while making its operational semantics explicit.

**Why translate?**
ODRL is a descriptive language—it describes permissions and duties but lacks a rigorous execution model. It does not define *when* a duty is violated, *how* a state transition occurs, or *what* implies the satisfaction of a constraint. RL2 provides these missing operational semantics (Event Loop, State Machine, Promise Theory), transforming static policy documents into executable logic.

**The Transpilation Strategy**
We define a transformation function `T(M)` that maps ODRL models to RL2. This document defines that mapping, identifies necessary transformations (e.g., flattening inheritance), and justifies the semantic equivalence.

---

## Part I: ODRL 2.2 Core Mapping

### 1.1 Structural Mapping

RL2 mirrors ODRL's core "Policy contains Rules" structure but refines the vocabulary to be deontically precise.

| ODRL Concept | RL2 Equivalent | Rationale |
| :--- | :--- | :--- |
| **Policy** | `rl2:Policy` | Direct mapping. |
| **Rule** | `rl2:Norm` | "Rule" is syntactic; "Norm" is semantic (Deontic Logic). |
| **Permission** | `rl2:Privilege` | A "privilege" is the correct Hohfeldian term for "permission." |
| **Prohibition** | `rl2:Prohibition` | Direct mapping. |
| **Duty** | `rl2:Duty` | Direct mapping. |
| **Asset** | `rl2:Asset` | Direct mapping. |
| **Party** | `rl2:Agent` | Direct mapping. |
| **Action** | `rl2:Action` | Direct mapping. |
| **Constraint** | `rl2:Condition` | RL2 distinguishes atomic comparisons (`AtomicConstraint`) from logical structures (`LogicalConstraint`) and event patterns (`EventConstraint`). |

### 1.2 Property Mapping

| ODRL Property | RL2 Property | Semantics |
| :--- | :--- | :--- |
| `assignee` | `rl2:subject` | The agent bearing the norm (Hohfeldian subject). |
| `assigner` | `rl2:counterparty` | The agent to whom the duty is owed (Hohfeldian correlative). |
| `target` | `rl2:object` | The asset acted upon. |
| `action` | `rl2:action` | The operation being regulated. |
| `constraint` | `rl2:condition` | Activation requirements. |
| `refinement` | `rl2:condition` | Nested conditions on assets/actions. |
| `consequence` | State-Triggered Duty | See Pattern 2.4 (Consequences). |
| `remedy` | State-Triggered Duty | See Pattern 2.4 (Remedies). |

### 1.3 Operator Mapping

RL2 provides a strict superset of ODRL operators, typed for rigorous validation.

| ODRL Operator | RL2 Operator | Type |
| :--- | :--- | :--- |
| `eq`, `neq` | `rl2:eq`, `rl2:neq` | Comparison |
| `lt`, `lte`, `gt`, `gte` | `rl2:lt`, `rl2:lte`, ... | Comparison |
| `isA` | `rl2:isA` | Semantic |
| `isAnyOf`, `isAllOf` | `rl2:isAnyOf`, `rl2:isAllOf` | Set |
| `and`, `or`, `xone` | `rl2:and`, `rl2:or`, `rl2:xone` | Logical |

---

## Part II: The Transpilation Strategy `T(M)`

The mapping `T(M)` is designed to operate on the **Atomic Policy** form defined in the ODRL Information Model (Section 2.7). This standardizes the input by ensuring that complex ODRL constructs are expanded into simpler components before RL2 compilation begins.

### 2.0 Input: ODRL Atomic Form
Before applying RL2-specific transformations, the ODRL policy is normalized to its Atomic Form:
1.  **Inheritance Flattening:** Parent properties are merged into children.
2.  **Collection Explosion:** Rules with multiple Actions, Targets, or Assignees are expanded into multiple rules (Cartesian product), such that each Atomic Policy contains exactly one Action, one Target, and one Assignee.
3.  **Conflict Resolution:** Policy-level conflict strategies are applied to produce a consistent set of rules.

This Atomic Form serves as the direct input for the RL2 compilation steps below.

### 2.1 Pattern: Permission-Bound Duties

**The ODRL Pattern:**
ODRL allows embedding a `Duty` inside a `Permission` to imply a requirement: "You can do X if you do Y."

```turtle
# ODRL (Implicit Logic)
odrl:permission [
    odrl:action odrl:play ;
    odrl:duty [
        odrl:action odrl:pay ;
        odrl:constraint [ ... amount=5 ... ]
    ]
]
```

**The RL2 Transpilation:**
RL2 decouples the duty from the privilege to track their lifecycles independently. The privilege then explicitly *depends* on the duty's state.

1.  **Extract** the Duty as a standalone norm.
2.  **Inject** a condition into the Privilege that checks the Duty's state.
3.  **Bind** identities (ODRL implies SameSubject; RL2 makes it explicit).

```turtle
# RL2 (Explicit Logic)
# 1. Standalone Duty
ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:User ;
    rl2:action ex:pay ;
    rl2:object ex:Asset .

# 2. Conditional Privilege
ex:playPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:play ;
    rl2:object ex:Asset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # State Check (Sein-sollen)
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:obligationStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand rl2:Fulfilled
        ] ;
        rl2:operand [
            # Identity Check (Tun-sollen / SameSubject)
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:dutyPerformerOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

**Justification:** This transformation preserves the "conditional permission" meaning but allows the payment duty to be tracked, audited, and potentially fulfilled *before* the access request (pre-payment) or *after* (post-payment), depending on the state machine.

### 2.2 Pattern: Inheritance (`inheritFrom`)

**The ODRL Pattern:**
Policies can inherit properties from other policies. This creates a dependency graph that must be resolved at runtime (or fails if the parent is offline).

**The RL2 Transpilation:**
RL2 performs **Compile-Time Flattening**.

`T(ChildPolicy)` = `Merge(Child, Resolve(Parent))`

1.  Recursively resolve parent policies.
2.  Union all clauses (norms).
3.  Merge policy-level metadata (child overrides parent).
4.  Output a self-contained `rl2:Policy` with no external dependencies.

**Justification:** Runtime inheritance is an operational anti-pattern in distributed systems (latency, availability risks). Flattening ensures policies are immutable, self-contained artifacts ready for high-performance evaluation.

### 2.3 Pattern: Abstract "Constraints"

**The ODRL Pattern:**
`odrl:constraint` mixes temporal checks, state checks, and attribute matches into one bucket.

**The RL2 Transpilation:**
The compiler analyzes the `leftOperand` to categorize the constraint:

*   `dateTime` / `duration` → **Temporal Constraint** (mapped to `rl2:AtomicConstraint` with `rl2:currentDateTime`)
*   `event` / `state` → **Event/State Constraint** (mapped to `rl2:EventConstraint` or `rl2:obligationStateOperand`)
*   Other attributes → **Context Constraint** (mapped to `rl2:AtomicConstraint` with profile-defined operands)

### 2.4 Pattern: Consequences and Remedies

**The ODRL Pattern:**
ODRL uses `consequence` (on Duty) and `remedy` (on Prohibition) to define obligations that arise upon violation.
- `consequence`: "If Duty A fails, then Duty B must be done."
- `remedy`: "If Prohibition P is violated, then Duty D must be done."

**The RL2 Transpilation:**
RL2 models these as **State-Triggered Duties**. The "remedial" duty is a standalone norm whose activation condition is the violation state of the original norm.

**Example (Consequence):**
```turtle
# 1. Primary Duty (Active)
ex:primaryDuty a rl2:Duty .

# 2. Consequence Duty (Pending)
ex:fineDuty a rl2:Duty ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:primaryDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand rl2:Violated
    ] .
```

**Example (Remedy):**
For a Prohibition, the violation is an event (the prohibited action occurred). The remedial duty is conditioned on that event.
```turtle
# Remedy Duty (Pending)
ex:remedyDuty a rl2:Duty ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:EventConstraint ;
        rl2:expectsEvent [
            a rl2:Event ;
            rl2:action ex:prohibitedAction ; # The action that was banned
            # Additional matching criteria...
        ]
    ] .
```

**Justification:** This approach unifies "normal" logic and "exception" logic. A consequence is simply a duty that activates when another duty fails. This removes the need for special properties like `consequence` and `remedy`, reducing the ontology surface area while increasing expressiveness (e.g., chains of consequences are naturally supported).

---

## Part III: Addressing ODRL Ambiguities

RL2 fixes known ambiguities in ODRL 2.2 profiles.

### 3.1 The "Party" Ambiguity
ODRL `assigner` and `assignee` are overloaded.
*   **RL2 Fix:** We split roles into **Normative** (Subject/Counterparty) and **Functional** (Grantor/Grantee).
    *   *Example:* In a "Break Glass" policy, the admin defines it (Grantor), but the user is the Subject. In ODRL, the "assigner" is often implicitly the system, which is confusing.

### 3.2 The "Duty" Ambiguity
ODRL `Duty` covers both "Must do X" (Obligation) and "If you do X, you get Y" (Condition).
*   **RL2 Fix:** We distinguish **Duty** (a Norm that can be violated) from **Condition** (a logic gate).
    *   If it's a condition for access, it's a `Constraint` on the Privilege.
    *   If it's a requirement that persists (e.g., delete data in 30 days), it's a `Duty`.

### 3.3 The "Implicit Logic" Ambiguity
ODRL assumes `SameSubject` (assignee of permission = assignee of duty) unless specified.
*   **RL2 Fix:** Identity binding is always explicit via `dutyPerformerOperand`.
    *   Allows modeling **Separation of Duty** (dutyPerformer != currentAgent) just as easily as SameSubject.

---

## Part IV: ODRL 3.0 & Advanced Features

RL2 is already aligned with emerging ODRL 3.0 requirements.

| ODRL 3.0 Need | RL2 Solution |
| :--- | :--- |
| **Promises** | First-class `rl2:Promise` class with `PromisePending`, `PromiseFulfilled`, `PromiseViolated` states. |
| **Event Triggers** | `rl2:Event` and `rl2:StateTransition` (e.g., policy activates on "Publication" event). |
| **Dynamic Collections** | `rl2:AssetCollection` (Core) + Profile-defined resolution queries. |
| **Strict Semantics** | `RL2_Semantics.md` defines the formal calculus (tun-sollen vs sein-sollen). |
| **Runtime Protocol** | `rl2p` defines the Request/Response/Trace format standardizing the "Request" policy type. |

---

## Conclusion

**Transpilation is the Path Forward.**
Organizations with existing ODRL assets do not need to discard them. They can use the `T(M)` transpilation strategy to compile ODRL into RL2.

**The Result:**
*   **Backwards Compatible:** Old policies still work.
*   **Forwards Capable:** New capabilities (Promises, Events, Formal Verification) become available.
*   **Risk Reduced:** Ambiguous "implied" logic becomes explicit "executable" logic.

RL2 is not a competitor to ODRL; it is the **runtime realization** of the ODRL vision.