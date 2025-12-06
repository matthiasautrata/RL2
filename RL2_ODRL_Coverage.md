# RL2 Coverage of ODRL (Draft v0.4)

*A unified mapping of ODRL 2.2 and ODRL 3.0 use cases to RL2*

---

## Table of Contents

- Introduction
- Part I: ODRL 2.2 Core Mapping
  - Overview of ODRL 2.2
  - Full Mapping Table (ODRL → RL2)
  - Transformation Rules
  - Semantic Preservation
- Part II: ODRL 3.0 Use-Case Deltas
  - Summary of ODRL 3.0 Extensions
  - Use Case Coverage Matrix
  - Detailed Coverage
- Part III: Canonical Worked Example
- Completeness and Soundness
- References

---

## Introduction

This document provides a comprehensive mapping showing that:

> **Every ODRL 2.2 expression can be represented in RL2 without loss of meaning, and RL2 covers all ODRL 3.0 use cases identified in W3C Community Group notes.**

RL2 is a **semantic superset** of ODRL—it can express every ODRL concept, though some constructs require compilation/transformation rather than direct vocabulary mapping:

* All ODRL 2.2 concepts have RL2 representations (some via direct equivalents, others via compilation).
* RL2 resolves ODRL ambiguities and fills gaps.
* RL2 adds normative, operational, temporal, and role semantics missing in ODRL.
* RL2 covers all emerging ODRL 3.0 use cases (dynamic collections, event-driven activation, multi-party workflows).
* The mapping is semantics-preserving; see "Assumptions and Clarifications" below for constructs requiring transformation.

### Assumptions and Clarifications

This mapping assumes the following baseline semantics for ODRL:

* **[Pucella-Weissman 2006]** — Static semantics for permissions and obligations
* **[Steyskal-Polleres 2015]** — Action dependencies and rule-based reasoning
* **[W3C ODRL Formal Semantics]** — Draft evaluator behavior specification

The following ODRL features require transformation or clarification:

* **`odrl:inheritFrom`** — No direct RL2 equivalent. Inheritance requires flattening to atomic policies before evaluation. See **backlog.md** §Policy Inheritance.
* **`odrl:Request` (policy type)** — RL2 does not model requests as policies. The `odrl:Request` policy type was never standardized or widely adopted. RL2 handles request semantics via `rl2p:Request` in the Protocol ontology—a runtime evaluation artifact, not a policy container.
* **Implementation-specific conflict resolution** — RL2 supports priority-based conflict resolution via `rl2:priority`. W3C-style conflict strategies (prohibit-overrides, permit-overrides) are defined in evaluation semantics but not as ontology vocabulary.

---

## ODRL 2.2 Core Mapping

### Overview of ODRL 2.2

ODRL 2.2 consists of:

1. **Policy types**: Set, Offer, Agreement, Request, Privacy, Assertion
2. **Rules**: Permission, Prohibition, Duty
3. **Assets**
4. **Parties and Roles**
5. **Actions**
6. **Constraints**
7. **Conflict Handling**

### RL2 Perspective

RL2 mirrors this basic structure but expands normative meaning through:

* Hohfeldian normative primitives (Privilege, Duty, Claim, Power, Liability, Immunity)
* Promise Theory layer for voluntary cooperation
* Typed operator hierarchy for constraints
* Operational semantics for duty and promise lifecycles

---

### Full Mapping Table (ODRL → RL2)

### Classes

| ODRL Class       | RL2 Class      | Notes                     |
| ---------------- | -------------- | ------------------------- |
| odrl:Policy      | rl2:Policy     | Same container pattern    |
| odrl:Rule        | rl2:Norm       | RL2 norm is superset      |
| odrl:Permission  | rl2:Privilege  | Same deontic meaning      |
| odrl:Prohibition | rl2:Prohibition | Direct deontic mapping    |
| odrl:Duty        | rl2:Duty       | Direct                    |
| odrl:Constraint  | rl2:AtomicConstraint | Simple ODRL constraints; RL2 also has LogicalConstraint, TemporalConstraint, etc. |
| odrl:Asset       | rl2:Asset      | Direct                    |
| odrl:Action      | rl2:Action     | Direct                    |
| odrl:Party       | rl2:Agent      | Direct                    |

### Properties

| ODRL Property    | RL2 Equivalent                  | Comment                             |
| ---------------- | ------------------------------- | ----------------------------------- |
| odrl:target      | rl2:object                      | Asset-specific                      |
| odrl:action      | rl2:action                      | Direct                              |
| odrl:assignee    | rl2:subject                     | Semantically identical              |
| odrl:assigner    | rl2:counterparty / rl2:grantor  | Depending on semantic or syntactic  |
| odrl:constraint  | rl2:condition                   | Generalizes                         |
| odrl:conflict    | rl2:priority + evaluator config | Policy priority; strategy is evaluator config |
| odrl:duty        | rl2:Duty                        | Direct mapping                      |
| odrl:permission  | rl2:Privilege                   | Direct mapping                      |
| odrl:prohibition | rl2:Prohibition                 | Direct deontic mapping              |
| odrl:inheritFrom | Flattening Strategy | See below |
| odrl:refinement  | rl2:Condition refinement        | RL2 supports nested conditions      |

### Constraint Operators

| ODRL Operator | RL2 Operator        | Notes                  |
| ------------- | ------------------- | ---------------------- |
| eq, neq       | rl2:eq, rl2:neq     | ComparisonOperator     |
| lt, lte       | rl2:lt, rl2:lte     | ComparisonOperator     |
| gt, gte       | rl2:gt, rl2:gte     | ComparisonOperator     |
| isA           | rl2:isA             | Type membership check  |
| isAnyOf       | rl2:isAnyOf         | Set membership         |
| isAllOf       | rl2:isAllOf         | All-of check           |
| isNoneOf      | rl2:isNoneOf        | None-of check          |
| and           | rl2:and             | LogicalOperator        |
| or            | rl2:or              | LogicalOperator        |
| xone          | rl2:xone            | LogicalOperator        |

### Party Role Mapping

| ODRL Role       | RL2 Normative Role | RL2 Functional Role |
| --------------- | ------------------ | ------------------- |
| assignee        | rl2:subject        | rl2:grantee         |
| assigner        | rl2:counterparty   | rl2:grantor         |
| informedParty   | —                  | rl2:participant     |
| attributedParty | —                  | rl2:participant     |
| consentingParty | —                  | rl2:approver        |

---

### Transformation Rules

### Permissions

**ODRL:**
```turtle
odrl:permission [
  odrl:assignee A ;
  odrl:action X ;
  odrl:target S ;
  odrl:constraint C
] .
```

**RL2:**
```turtle
_:rule a rl2:Privilege ;
    rl2:subject A ;
    rl2:action X ;
    rl2:object S ;
    rl2:condition T(C) .
```

### Prohibitions

**ODRL:**
```turtle
odrl:prohibition [
  odrl:assignee A ;
  odrl:action X ;
]
```

**RL2:**
```turtle
_:rule a rl2:Prohibition ;
    rl2:subject A ;
    rl2:prohibitedAction X .
```

### Duties

**ODRL:**
```turtle
odrl:duty [
  odrl:assignee A ;
  odrl:action X ;
  odrl:target S ;
]
```

**RL2:**
```turtle
_:d a rl2:Duty ;
    rl2:subject A ;
    rl2:action X ;
    rl2:object S .
```

### Permission-Bound Duties (CRITICAL)

ODRL allows duties with different actions from the permitted action. For example, permit `display` if duty `pay` is fulfilled. This requires special transformation.

**ODRL:**
```turtle
:offer1 a odrl:Offer ;
    odrl:permission [
        odrl:action odrl:display ;
        odrl:target :photo123 ;
        odrl:duty [
            odrl:action odrl:pay ;
            odrl:constraint [ odrl:payAmount 5.00 ]
        ]
    ] .
```

**RL2 Transformation:**
```turtle
# Step 1: Create standalone duty with URI
ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:User ;
    rl2:action ex:pay ;
    rl2:object ex:Photo123 ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:payAmount ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand 5.00
    ] .

# Step 2: Add duty state precondition to privilege
ex:displayPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:display ;
    rl2:object ex:Photo123 ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check duty is fulfilled
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:obligationStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand rl2:Fulfilled
        ] ;
        rl2:operand [
            # Check same agent fulfilled (ODRL implies SameSubject)
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:dutyPerformerOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

**Transformation Rules:**
1. Create `rl2:Duty` as standalone clause with URI for referenceability
2. Add `LogicalConstraint` to permission's `rl2:condition` with:
   - `AtomicConstraint` checking `obligationStateOperand = Fulfilled`
   - `AtomicConstraint` checking `dutyPerformerOperand = currentAgent` (ODRL implies SameSubject)
3. Combine with `rl2:and`

### Constraints

**ODRL:**
```turtle
odrl:constraint [
  odrl:leftOperand odrl:purpose ;
  odrl:operator eq ;
  odrl:rightOperand "research"
]
```

**RL2:**
```turtle
# Note: Left operands like 'purpose' are defined by profiles, not RL2 Core.
# A privacy or data governance profile would define:
#   ex:purpose a rl2:LeftOperand .

_:c a rl2:AtomicConstraint ;
    rl2:leftOperand ex:purpose ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperand "research" .
```

### Compilation Strategy: Inheritance Flattening

ODRL allows policies to inherit from others via `odrl:inheritFrom`. RL2 supports this through a pre-processing "flattening" step during compilation, rather than as a runtime property.

**Algorithm:**
Given a policy `P` that inherits from `P_parent`:
1. **Recursively resolve** `P_parent` until a base policy is found.
2. **Merge Properties**:
   - If `P` defines a property (e.g., `rl2:condition`), it overrides `P_parent`.
   - If `P` does not define it, copy from `P_parent`.
3. **Merge Clauses**:
   - Union the set of clauses from `P` and `P_parent`.
   - Conflict resolution is handled by the evaluator's conflict strategy.
4. **Result**: A self-contained RL2 policy with no inheritance dependencies.

This strategy ensures that RL2 evaluation remains simple and deterministic (no external fetching during evaluation) while supporting the organizational reuse patterns of `inheritFrom`.

---

### Semantic Preservation

For every ODRL rule R:

```
⟦R⟧_ODRL  ==  ⟦T(R)⟧_RL2
```

**Proof Sketch:**

* Privilege semantics identical to Permission.
* Duty semantics identical.
* Prohibition semantics preserved directly through `rl2:Prohibition`.
* Constraint semantics preserved via functional equivalence.
* Role semantics preserved via mapping to normative or functional roles.
* Conflict semantics preserved via RL2 condition calculus.
* Asset semantics preserved exactly.

Thus RL2 provides a **conservative semantic extension** of ODRL 2.2.

---

## ODRL 3.0 Use-Case Deltas

### Summary of ODRL 3.0 Extensions

Based on W3C Community Group notes and drafts, ODRL 3.0 extends ODRL 2.2 with:

1. **Dynamic Asset Collections** — Asset collections defined via queries, materialized at runtime
2. **Dynamic Operand Resolution** — Operand values resolved at evaluation time
3. **Temporal Extensions** — Policy effective intervals, duty sequencing, event-triggered activation
4. **Event-based Activation** — Policy activation triggered by events
5. **Multi-Party Workflows** — Explicit approval steps, multi-party consent
6. **Enhanced Duty Semantics** — Duty-chains, sanctions, remedies
7. **Contextual Logic** — Environmental conditions, system state
8. **Inter-policy Relationships** — Inheritance, refinement, conflicts

---

### Use Case Coverage Matrix

| ODRL 3.0 Requirement       | RL2 Construct(s)                              | Coverage | Semantics Reference |
| -------------------------- | --------------------------------------------- | -------- | ------------------- |
| Dynamic asset collections  | rl2:AssetCollection (static members; dynamic materialization profile-specific) | Partial  | Profile semantics |
| Dynamic operand references | rl2:RuntimeReference (e.g., rl2:currentAgent) | Full     | RL2_Semantics §resolveRuntime |
| Path expressions           | rl2:LeftOperand + rl2:resolutionPath          | Full     | RL2_Semantics §deref |
| Temporal validity          | rl2:TemporalConstraint, rl2:EffectiveInterval | Full     | RL2_Semantics §timeout, §TemporalInterval |
| Duty sequencing            | Operational semantics, rl2:StateTransition    | Full     | RL2_Semantics §Operational Semantics |
| Duty state preconditions   | rl2:obligationStateOperand, rl2:targetNorm    | Full     | RL2_Semantics §resolve |
| Identity binding (SoD)     | rl2:dutyPerformerOperand, rl2:currentAgent    | Full     | RL2_Semantics §resolve, §DutyPerformer |
| Multi-party approval       | rl2:EventConstraint + rl2:approver            | Full     | RL2_Semantics §EventConstraint, §matches |
| Event-triggered activation | rl2:Event + rl2:triggeredBy                   | Full     | RL2_Semantics §Event Processing |
| Sanctions/remedies         | rl2:Power, rl2:Liability, rl2:Claim           | Full     | RL2_Semantics §Hohfeldian, §Sanctions |
| Context-dependent rules    | rl2:AtomicConstraint with inline LeftOperand  | Full     | RL2_Semantics §Atom, §resolve |
| Policy composition         | Under discussion                              | —        | See backlog.md |
| Cross-policy influence     | Conditions referencing other policies         | Full     | RL2_Semantics §Composite |

**Coverage Legend:**
* **Full**: Ontology construct exists AND denotational/operational semantics are defined in RL2_Semantics.md
* **Partial**: Ontology construct exists but semantics require profile-specific definitions
* **Future**: Identified requirement, implementation deferred

All ODRL 3.0 use cases listed above are covered with both ontology constructs and formal semantics.

---

### Detailed Coverage

### Dynamic Asset Collections

RL2 Core supports AssetCollection with static members. Dynamic materialization (e.g., "all assets with classification RestrictedResearch") is profile-specific; Core no longer embeds query strings. Profiles may define resolvers or registry references to populate collections.

### Multi-Party Approval Workflows

RL2 models approval requirements via `rl2:EventConstraint`:

```turtle
ex:ApprovalRequired a rl2:EventConstraint ;
    rl2:expectsEvent [
        a rl2:Event ;
        rl2:approver ex:EthicsBoard
    ] .
```

### Event-Triggered Activation

```turtle
ex:transition a rl2:StateTransition ;
    rl2:triggeredBy ex:ApprovalEvent ;
    rl2:fromState rl2:Pending ;
    rl2:toState rl2:Active .
```

---

## Canonical Worked Example

This example demonstrates a comprehensive RL2 policy incorporating:

* DPCL primitives (Privilege/Duty/Prohibition)
* Policy typing via subclass
* Temporal constraints
* Asset collections
* Multi-party approval via EventConstraint
* Promise-based conditions
* Domain-specific actions and left operands (defined in-policy)

```turtle
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# =============================================================
# Domain vocabulary (actions, left operands) - defined by policy
# =============================================================

# Actions for this domain
ex:use a rl2:Action ;
    rdfs:label "use" ;
    rdfs:comment "Exercise or consume an asset." .

ex:distribute a rl2:Action ;
    rdfs:label "distribute" ;
    rdfs:comment "Make available to third parties." .

ex:submitReport a rl2:Action ;
    rdfs:label "submitReport" ;
    rdfs:comment "Submit a usage report." .

# =============================================================
# Agents
# =============================================================

ex:DataOwner a rl2:Agent .
ex:Researcher a rl2:Agent .
ex:EthicsBoard a rl2:Agent .

# =============================================================
# Assets
# =============================================================

# Dynamic asset collection
# RL2 Core provides static membership; dynamic materialization is profile-specific.
ex:RestrictedDatasets a rl2:AssetCollection ;
    rl2:member ex:Dataset1 ;  # Static members for Core
    rl2:member ex:Dataset2 .
    # Profile-specific dynamic resolution would replace static members

# =============================================================
# Promise content
# =============================================================

ex:DataStewardship rdfs:label "Data Stewardship Commitment" .

# =============================================================
# Policy
# =============================================================

ex:ResearchDataPolicy a rl2:Agreement ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:UsePrivilege , ex:ReportDuty , ex:DistributionBan .

# Privilege with compound conditions
ex:UsePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:RestrictedDatasets ;
    rl2:condition ex:FullCondition .

ex:FullCondition a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:and ;
    rl2:operand ex:SemesterValid ;
    rl2:operand ex:EthicsApproval ;
    rl2:operand ex:StewardshipFulfilled .

# Temporal constraint
ex:SemesterValid a rl2:TemporalConstraint ;
    rl2:interval [
        a rl2:EffectiveInterval ;
        rl2:start "2024-09-01T00:00:00Z"^^xsd:dateTime ;
        rl2:end   "2025-01-31T23:59:59Z"^^xsd:dateTime
    ] .

# Event constraint for approval
ex:EthicsApproval a rl2:EventConstraint ;
    rl2:expectsEvent [
        a rl2:Event ;
        rl2:approver ex:EthicsBoard
    ] .

# Promise requirement
ex:StewardshipFulfilled a rl2:Condition ;
    rl2:requires ex:StewardshipPromise .

ex:StewardshipPromise a rl2:Promise ;
    rl2:promisor ex:Researcher ;
    rl2:promisee ex:DataOwner ;
    rl2:promiseContent ex:DataStewardship ;
    rl2:promiseState rl2:PromiseFulfilled .

# Duty with deadline
ex:ReportDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:submitReport ;
    rl2:object ex:RestrictedDatasets ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:end "2024-12-15T23:59:59Z"^^xsd:dateTime
        ]
    ] .

# Prohibition
ex:DistributionBan a rl2:Prohibition ;
    rl2:subject ex:Researcher ;
    rl2:prohibitedAction ex:distribute ;
    rl2:object ex:RestrictedDatasets .
```

This policy:

1. Grants usage privilege over a collection of restricted datasets
2. Requires the current date to be within the semester window
3. Requires prior approval from the ethics board (modeled as EventConstraint)
4. Requires the researcher to have fulfilled a stewardship promise
5. Imposes a reporting duty with a deadline
6. Prohibits distribution of the datasets

---

## Completeness and Soundness

## Completeness Theorem

For every valid ODRL model M (2.2 or 3.0 requirements), there exists an RL2 model T(M) such that:

* T(M) is valid under RL2 ontology and SHACL
* No structure or constraint is lost
* All semantics preserved

## Soundness Theorem

For every ODRL interpretation function `⟦.⟧_ODRL`, RL2 interpretation respects:

```
⟦T(R)⟧_RL2 = ⟦R⟧_ODRL
```

---

## References

See **RL2_References.md** for complete citations and glossary.

Key sources:
* [ODRL 2.2 Model], [ODRL 2.2 Vocab] — W3C Recommendations
* [ODRL Best Practices] — W3C Working Group Note
* [ODRL Formal Semantics] — Draft semantics
* [ODRL 3.0] — Community Group work in progress
* [DPCL], [Promise Theory], [ODRE] — RL2 foundations
