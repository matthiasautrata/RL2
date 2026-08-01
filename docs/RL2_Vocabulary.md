---
title: "RL2 Vocabulary Reference"
subtitle: "Complete Class and Property Definitions"
version: "0.6"
status: "Draft"
date: 2026-07-24
purpose: "Reference documentation for all RL2 ontology and protocol terms"
---

## About This Document

> **SCOPE-2 alignment in progress.** This document is an informative, currently hand-maintained
> view of `../spec/rl2.ttl` and `../spec/rl2-shacl.ttl`. Protocol terms are retained historical
> coverage and are not part of core language conformance. A generated-table check is planned.

This document provides complete reference documentation for every class, property, and named individual in the RL2 ontology. It is organized for lookup, not learning.

For readers new to RL2, **RL2_Primer.md** provides a progressive introduction to the concepts.

The ontology and SHACL shapes are authoritative; this document is a reader-oriented lookup view.

### Document Structure

- Section 2: Namespace and conformance
- Section 3: Class index (alphabetical listing)
- Sections 4-10: Class definitions by layer
- Section 11: Property reference
- Section 12: Named individuals (operators and enumerations)
- Section 13: SHACL validation summary

### Normative Status

The canonical definitions are in **rl2.ttl** (OWL ontology) and **rl2-shacl.ttl** (SHACL shapes). This document provides explanatory prose for those normative files.

---

## Table of Contents

1. [About This Document](#about-this-document)
2. [Namespace and Conformance](#2-namespace-and-conformance)
3. [Class Index](#3-class-index)
4. [Normative Layer Classes](#4-normative-layer-classes)
5. [Promise Theory Layer Classes](#5-promise-theory-layer-classes)
6. [Agent and Role Classes](#6-agent-and-role-classes)
7. [Action, Asset, and Condition Classes](#7-action-asset-and-condition-classes)
8. [Operational Layer Classes](#8-operational-layer-classes)
9. [Policy Container Classes](#9-policy-container-classes)
10. [Operator Classes](#10-operator-classes)
11. [Property Reference](#11-property-reference)
12. [Named Individuals](#12-named-individuals)
13. [SHACL Validation Summary](#13-shacl-validation-summary)
14. [RL2 Protocol Vocabulary (rl2p:)](#14-rl2-protocol-vocabulary-rl2p)

---

## 2. Namespace and Conformance

### Namespace

The RL2 namespace is:

```
https://rl2.example/ontology#
```

The conventional prefix is `rl2:`.

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
```

### Ontology Declaration

```turtle
<https://rl2.example/ontology>
  a owl:Ontology ;
  rdfs:label "RL2 Ontology" ;
  dc:description "A unified normative, descriptive, and operational rights language." ;
  owl:versionInfo "0.6" ;
  owl:versionIRI <https://rl2.example/ontology/0.6> .
```

### Conformance

An RL2-conformant policy:
1. Uses classes and properties from the `rl2:` namespace
2. Passes SHACL validation against `rl2-shacl.ttl`
3. Uses policy types, norm types, and states defined in this specification

Implementations MAY extend RL2 with additional classes and properties, provided they do not conflict with RL2 semantics.

### Extensibility

RL2 shapes are intentionally non-closed (`sh:closed` is not set). This allows:
- Domain profiles to add properties to RL2 classes
- Applications to attach implementation-specific metadata
- Future versions to extend without breaking existing data

---

## 3. Class Index

Alphabetical listing of all RL2 classes with brief descriptions.

| Class | Layer | Description |
|-------|-------|-------------|
| `rl2:Action` | Structural | An action that may be performed on an asset |
| `rl2:Agent` | Role | Any party participating in normative or functional roles |
| `rl2:Agreement` | Policy | Bilateral/multilateral policy with consenting parties |
| `rl2:Assertion` | Policy | Policy stating claims about normative status |
| `rl2:Asset` | Structural | A resource subject to normative control |
| `rl2:AssetCollection` | Structural | A collection of assets |
| `rl2:AtomicConstraint` | Condition | Simple comparison constraint |
| `rl2:Claim` | Normative | Correlative entitlement held by another agent |
| `rl2:ComparisonOperator` | Operator | Operators for comparing values |
| `rl2:Condition` | Condition | Base class for constraints |
| `rl2:Duty` | Normative | An obligation imposed on an agent |
| `rl2:DutyWindow` | Normative | Finite half-open interval for one Duty occurrence |
| `rl2:RuntimeReference` | Value | Value reference resolved at evaluation time (e.g., `currentAgent`) |
| `rl2:Event` | Operational | Observable event triggering transitions |
| `rl2:EventConstraint` | Condition | Constraint requiring an event to occur |
| `rl2:Immunity` | Normative | Protection against another's power |
| `rl2:LeftOperand` | Condition | Property or attribute for condition evaluation |
| `rl2:Liability` | Normative | Exposure to exercise of power |
| `rl2:LogicalConstraint` | Condition | Combines conditions via logical operators |
| `rl2:LogicalOperator` | Operator | Operators for combining conditions |
| `rl2:Norm` | Normative | Base class for normative relations |
| `rl2:ObligationState` | Operational | State enumeration for duties |
| `rl2:Offer` | Policy | Policy proposed awaiting acceptance |
| `rl2:Operator` | Operator | Abstract base class for operators |
| `rl2:Policy` | Policy | Container for normative clauses |
| `rl2:Power` | Normative | Ability to alter normative relations |
| `rl2:Privacy` | Policy | Data protection policy |
| `rl2:Privilege` | Normative | Absence of duty not to perform an action |
| `rl2:Prohibition` | Normative | Prohibition on performing an action |
| `rl2:Promise` | Promise | Voluntary commitment between agents |
| `rl2:PromiseState` | Operational | State enumeration for promises |
| `rl2:Set` | Policy | Unilateral policy declaration |
| `rl2:StateTransition` | Operational | Transition in system state |

---

## 4. Normative Layer Classes

The normative layer defines the fundamental types of normative relations.

### rl2:Norm

**Definition**: A normative relation in the DPCL (normative specification) sense.

**Type**: `owl:Class`

**Subclasses**: Privilege, Duty, Prohibition, Claim, Power, Liability, Immunity

**Properties** (common to all norms):
- `rl2:subject` — Agent bearing the normative status
- `rl2:counterparty` — Agent in correlative position (optional)
- `rl2:action` — Action specified in the norm
- `rl2:object` — Asset the norm concerns
- `rl2:condition` — Condition for norm activation

**Notes**: Norm is abstract; use specific subclasses in policies.

---

### rl2:Privilege

**Definition**: A normative absence of duty not to perform an action. The subject is permitted to perform the action.

**Type**: `owl:Class`

**Superclass**: `rl2:Norm`

**Required Properties**:
- `rl2:subject` — Agent who has the privilege
- `rl2:action` — Action that is permitted
- `rl2:object` — Asset the privilege concerns

**Optional Properties**:
- `rl2:condition` — When the privilege is active
- `rl2:prerequisiteDuty` — A Duty that must be Fulfilled before this Privilege can contribute a permit; repeat for conjunctive prerequisites
- `rl2:counterparty` — Agent who cannot demand the subject refrain

**SHACL Shape**: `rl2:PrivilegeShape`

**Example**:
```turtle
ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset .
```

**Hohfeldian Context**: Privilege correlates with No-Claim. If Alice has a privilege to X, Bob has no claim that Alice not X.

---

### rl2:Duty

**Definition**: An obligation imposed on an agent, represented canonically as either an
Achievement Duty or a Maintenance Duty.

**Type**: `owl:Class`

**Superclass**: `rl2:Norm`

**Properties required for both forms**:
- `rl2:subject` — Agent who bears the duty
- `rl2:object` — Asset the duty concerns

**Canonical content (exactly one form)**:
- Achievement: exactly one `rl2:action`; optional `rl2:postCondition`
- Maintenance: exactly one `rl2:invariant`; no `rl2:action` or `rl2:postCondition`

**Optional common properties**:
- `rl2:condition` — Applicability guard only
- `rl2:dutyWindow` — Finite half-open assessment interval
- `rl2:counterparty` — Agent to whom the duty is owed
- `rl2:obligationState` — Optional serialization of a derived known status; never evaluator input

**SHACL Shape**: `rl2:DutyShape`, `rl2:DutyStateShape`, `rl2:DutyWindowShape`

**Example**:
```turtle
ex:reportDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:submitReport ;
    rl2:object ex:Dataset ;
    rl2:dutyWindow [
        a rl2:DutyWindow ;
        rl2:startInclusive "2025-06-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2025-07-01T00:00:00Z"^^xsd:dateTimeStamp
    ] .

ex:serviceAvailable a rl2:LeftOperand ;
    rl2:resolutionPath "asset.serviceAvailable" ;
    rdfs:range xsd:boolean .

ex:availabilityDuty a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:object ex:Service ;
    rl2:invariant [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:serviceAvailable ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand true
    ] ;
    rl2:dutyWindow [
        a rl2:DutyWindow ;
        rl2:startInclusive "2025-06-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2025-07-01T00:00:00Z"^^xsd:dateTimeStamp
    ] .
```

**Hohfeldian Context**: Duty correlates with Claim. If Alice has a duty to X, Bob (the counterparty) has a claim that Alice X.

**Status**: `dutyStatus` derives Pending, Active, Fulfilled, or Violated from the Duty and immutable
snapshot. Core semantics do not prescribe a persistent state machine.

**Ownership**: A Duty used through `rl2:prerequisiteDuty` is referenced by one or more Privileges
and is not also a Policy clause. Sharing one Duty node shares one status result, so one qualifying
fulfillment can satisfy every owner. A Duty linked directly from a Policy with `rl2:clause` is
independent; its status does not change an access decision.

---

### rl2:DutyWindow

**Definition**: The finite assessment interval for one Duty occurrence.

**Type**: `owl:Class`

**Required Properties**:
- `rl2:startInclusive` — Inclusive `xsd:dateTimeStamp` start
- `rl2:endExclusive` — Exclusive `xsd:dateTimeStamp` end, strictly later than the start

The interval is `[startInclusive, endExclusive)`. It does not recur or reset. Repeated periods use
distinct Duty nodes.

**SHACL Shape**: `rl2:DutyWindowShape`

---

### rl2:Prohibition

**Definition**: A prohibition on performing an action. The subject must not perform the action.

**Type**: `owl:Class`

**Superclass**: `rl2:Norm`

**Required Properties**:
- `rl2:subject` — Agent who is prohibited
- `rl2:prohibitedAction` — Action that is forbidden
- `rl2:object` — Asset the prohibition concerns

**Optional Properties**:
- `rl2:condition` — When the prohibition applies

**SHACL Shape**: `rl2:ProhibitionShape`

**Example**:
```turtle
ex:distributionBan a rl2:Prohibition ;
    rl2:subject ex:Researcher ;
    rl2:prohibitedAction ex:distribute ;
    rl2:object ex:Dataset .
```

**Notes**: In strict Hohfeldian terms, a prohibition is a Duty to refrain. RL2 models it as a distinct class for practical policy authoring. Use `rl2:prohibitedAction` (subproperty of `rl2:action`) for the forbidden action.

---

### rl2:Claim

**Definition**: A correlative entitlement held by one agent against another. The claim-holder can demand performance of a corresponding duty.

**Type**: `owl:Class`

**Superclass**: `rl2:Norm`

**Required Properties**:
- `rl2:subject` — Agent who holds the claim (the right-holder)
- `rl2:counterparty` — Agent against whom the claim is held (the duty-bearer)
- `rl2:correlativeTo` — Exactly one corresponding `rl2:Duty` (C6b). The Claim's content
  (action/object/condition) is **derived** from this Duty; the Claim does not author its own.

**Derived (not authored on the Claim)**: `rl2:action`, `rl2:object`, `rl2:condition` — taken
from the correlative Duty. The Duty's roles must mirror the Claim (`Duty.subject =
Claim.counterparty`, `Duty.counterparty = Claim.subject`).

**SHACL Shape**: `rl2:ClaimShape`

**Example** (the Claim derives its content from `ex:aliceDuty`):
```turtle
ex:aliceDuty a rl2:Duty ;
    rl2:subject ex:Alice ;        # duty-bearer  = Claim.counterparty
    rl2:counterparty ex:Bob ;     # right-holder = Claim.subject
    rl2:action ex:deliver ;
    rl2:object ex:Report .

ex:deliver a rl2:Action .

ex:bobClaim a rl2:Claim ;
    rl2:subject ex:Bob ;          # right-holder
    rl2:counterparty ex:Alice ;   # duty-bearer
    rl2:correlativeTo ex:aliceDuty .
```

**Hohfeldian Context**: Claim is the correlative of Duty. Claims and duties are two sides of the same relationship — RL2 authors the Duty and derives the Claim from it (C6b).

---

### rl2:Power

**Definition**: The ability of an agent to alter normative relations — to create, modify, or extinguish norms.

**Type**: `owl:Class`

**Superclass**: `rl2:Norm`

**Required Properties**:
- `rl2:subject` — Agent who holds the power
- `rl2:affectsNorm` — The norm that can be affected

**Optional Properties**:
- `rl2:condition` — When the power can be exercised

**SHACL Shape**: `rl2:PowerShape`

**Example**:
```turtle
ex:grantAccessPower a rl2:Power ;
    rl2:subject ex:Manager ;
    rl2:affectsNorm ex:accessPrivilegeTemplate .
```

**Hohfeldian Context**: Power correlates with Liability. When Alice exercises a power, Bob (who has liability) has their normative position changed.

---

### rl2:Liability

**Definition**: Exposure to the exercise of power by another agent. The liable party's normative position may be changed.

**Type**: `owl:Class`

**Superclass**: `rl2:Norm`

**Required Properties**:
- `rl2:subject` — Agent who is liable (exposed)
- `rl2:exposedTo` — The Power to which they are exposed

**SHACL Shape**: `rl2:LiabilityShape`

**Example**:
```turtle
ex:managerPower a rl2:Power ;
    rl2:subject ex:Manager ;
    rl2:affectsNorm ex:employeePrivilege .

ex:employeeLiability a rl2:Liability ;
    rl2:subject ex:Employee ;
    rl2:exposedTo ex:managerPower .
```

**Hohfeldian Context**: Liability is the correlative of Power.

---

### rl2:Immunity

**Definition**: Protection of an agent from having their normative position altered by another's power.

**Type**: `owl:Class`

**Superclass**: `rl2:Norm`

**Required Properties**:
- `rl2:subject` — Agent who is protected
- `rl2:immuneFrom` — The Power they are protected from

**SHACL Shape**: `rl2:ImmunityShape`

**Example**:
```turtle
ex:terminationPower a rl2:Power ;
    rl2:subject ex:Dean ;
    rl2:affectsNorm ex:employmentPrivilege .

ex:tenureImmunity a rl2:Immunity ;
    rl2:subject ex:Professor ;
    rl2:immuneFrom ex:terminationPower .
```

**Hohfeldian Context**: Immunity correlates with Disability (not modeled as a class in RL2). If Alice has immunity from Bob's power, Bob is disabled from exercising that power against Alice.

---

## 5. Promise Theory Layer Classes

### rl2:Promise

**Definition**: A voluntary cooperative commitment from one agent (promisor) to another (promisee).

**Type**: `owl:Class`

**Required Properties**:
- `rl2:promisor` — Agent making the promise
- `rl2:promisee` — Agent receiving the promise
- **Exactly one** of the three disjoint content properties:
  - `rl2:promisedAction` — Tun-sollen: an Action the promisor will perform
  - `rl2:promisedState` — Sein-sollen: a Condition the promisor will keep true
  - `rl2:promisedDuty` — suretyship: a Duty the promisor will see fulfilled

**Optional Properties**:
- `rl2:object` — Asset of an action or state Promise; an Offer may leave it for Acceptance binding
- `rl2:promiseState` — Serialization of a known derived status; never authoritative evaluator input

**SHACL Shapes**: `rl2:PromiseShape`, `rl2:PromiseStateShape`

**Example**:
```turtle
ex:dataStewardshipDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:steward ;
    rl2:object ex:Dataset .

ex:dataPromise a rl2:Promise ;
    rl2:promisor ex:Researcher ;
    rl2:promisee ex:DataOwner ;
    rl2:promisedDuty ex:dataStewardshipDuty .   # suretyship
```

**Notes**: Promises are fundamentally different from Duties:
- Duties are imposed; promises are voluntary
- Duties may have abstract counterparties; promises always have specific promisees
- Promises may *create* duties but are not themselves duties

---

### Promise Content Properties

**Definition**: What a promise commits to, expressed by **exactly one** of three
disjoint properties. This replaces the former polymorphic `rl2:promiseContent`
(a union of Action/Duty/Condition), which let one intent be encoded several ways.
Canonical form requires a single shape per proposition.

| Property | Range | Deontic sense | Fulfilled when |
|----------|-------|---------------|----------------|
| `rl2:promisedAction` | `rl2:Action` | Tun-sollen ("I will do X") | the promisor has performed the action on the authored or acceptance-bound object (subsumption-aware) |
| `rl2:promisedState` | `rl2:Condition` | Sein-sollen ("X will hold") | the condition evaluates true |
| `rl2:promisedDuty` | `rl2:Duty` | Suretyship ("I will see D fulfilled") | the Duty's ObligationState reaches Fulfilled |

**Notes**: `promisedDuty` does **not** make the promisor the Duty's `rl2:subject`;
the duty-bearer is assigned explicitly on the Duty. A promise (voluntary commitment,
Promise Theory) remains distinct from the Hohfeldian Duty it references. Its status is defined
in core, but pure Offer acceptance rejects this content because neither canonical Duty form
represents general suretyship. A profile may define an explicit transformation.

---

## 6. Agent and Role Classes

### rl2:Agent

**Definition**: Any party participating in a normative or functional role.

**Type**: `owl:Class`

**Notes**:
- RL2 intentionally leaves Agent open-ended
- Agents may be people, organizations, or automated systems
- Profiles may define Agent subclasses for specific domains
- No SHACL shape restricts Agent structure

**Example**:
```turtle
ex:Alice a rl2:Agent .
ex:ResearchInstitute a rl2:Agent .
ex:DataPlatform a rl2:Agent .
```

---

## 7. Action, Asset, and Condition Classes

### rl2:Action

**Definition**: An action that may be performed on an asset.

**Type**: `owl:Class`

**Notes**:
- RL2 Core does not define specific action instances
- Actions are provided by domain profiles as **individuals** of this class
- Action hierarchies are expressed using `rl2:includedIn`, not `rdfs:subClassOf`
- Examples: `play`, `use`, `distribute`, `delete`, `modify`

**Example**:
```turtle
# Profile-defined actions (flat)
ex:use a rl2:Action .
ex:distribute a rl2:Action .
ex:delete a rl2:Action .

# Action hierarchy via includedIn
ex:fineTune a rl2:Action ;
    rl2:includedIn ex:trainModel .
ex:trainModel a rl2:Action .
```

---

### rl2:Asset

**Definition**: A resource or object subject to normative control.

**Type**: `owl:Class`

**Notes**:
- Assets may be data, content, services, or abstract resources
- RL2 Core does not constrain asset structure
- Profiles may define Asset subclasses

---

### rl2:AssetCollection

**Definition**: A collection of assets. **`rdfs:subClassOf rl2:Asset`** (C7) — a collection is itself an Asset, so it can be the object of a norm and can itself be a member of another collection.

**Type**: `owl:Class` (subclass of `rl2:Asset`)

**Properties**:
- `rl2:member` — Direct member assets (not transitively closed in core)

**SHACL Shape**: `rl2:AssetCollectionShape`

**Example**:
```turtle
ex:sensitiveAssets a rl2:AssetCollection ;
    rl2:member ex:customerData ;
    rl2:member ex:financialRecords .
```

**Membership semantics (C7)**: Core matching uses **direct** `rl2:member` links only, resolved against the evaluation snapshot (stable for the duration of an evaluation). Because `AssetCollection ⊑ Asset`, a member may itself be a collection, but core does **not** auto-flatten nested collections — transitive membership is a profile/derived concern. Dynamic materialization is likewise profile-specific: RL2 Core specifies no query string; profiles may define resolution functions or registry references if needed.

---

### rl2:Condition

**Definition**: Base class for constraints that must hold for a norm or policy to be active.

**Type**: `owl:Class`

**Subclasses**: AtomicConstraint, LogicalConstraint, EventConstraint

**Common Properties**:
- `rl2:constraintOperator` — Operator for evaluation

**Notes**: Dynamic value resolution uses `LeftOperand` with `resolutionPath` (for left-side values) or `RuntimeReference` (for right-side values like `currentAgent`).

---

### rl2:AtomicConstraint

**Definition**: A simple comparison constraint with left operand, operator, and right operand.

**Type**: `owl:Class`

**Superclass**: `rl2:Condition`

**Required Properties**:
- `rl2:leftOperand` — Property being evaluated
- `rl2:constraintOperator` — Comparison operator (must be ComparisonOperator)
- One of: `rl2:rightOperand` (literal) or `rl2:rightOperandRef` (resource)

**Optional Properties**:
- `rl2:targetNorm` — Specifies which duty/norm or Offer-stage promise to query. Required
  for all four core state-query operands; SHACL selects the required target class by operand.

**SHACL Shapes**: `rl2:AtomicConstraintShape`, `rl2:NormStateConstraintShape`

**Example (simple comparison)**:
```turtle
ex:purpose a rl2:LeftOperand ;
    rl2:resolutionPath "context.purpose" .

ex:purposeCheck a rl2:AtomicConstraint ;
    rl2:leftOperand ex:purpose ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperand "research" .
```

**Example (duty state as precondition)**:
```turtle
# Check if a specific duty is fulfilled
ex:dutyCheck a rl2:AtomicConstraint ;
    rl2:targetNorm ex:paymentDuty ;
    rl2:leftOperand rl2:obligationStateOperand ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperandRef rl2:Fulfilled .

# Check if the current agent fulfilled the duty (Tun-sollen pattern)
ex:performerCheck a rl2:AtomicConstraint ;
    rl2:targetNorm ex:paymentDuty ;
    rl2:leftOperand rl2:dutyPerformerOperand ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperandRef rl2:currentAgent .
```

---

### rl2:LogicalConstraint

**Definition**: A condition combining other conditions via logical operators.

**Type**: `owl:Class`

**Superclass**: `rl2:Condition`

**Required Properties**:
- `rl2:constraintOperator` — Logical operator (and, or, xone, not)
- `rl2:operand` — Sub-conditions (exactly one for `not`; at least two for `and`, `or`, and `xone`)

**SHACL Shape**: `rl2:LogicalConstraintShape`

**Example**:
```turtle
ex:combined a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:and ;
    rl2:operand ex:purposeCheck ;
    rl2:operand ex:timeCheck .
```

**Notes**:
- `rl2:not` requires exactly one operand
- `rl2:and`, `rl2:or`, `rl2:xone` require at least two operands
- These operand cardinalities are enforced by SHACL shapes in `rl2-shacl.ttl`.

---

### rl2:EventConstraint

**Definition**: A condition requiring a specific event to have occurred.

**Type**: `owl:Class`

**Superclass**: `rl2:Condition`

**Required Properties**:
- `rl2:expectsEvent` — The event that must exist in state

**SHACL Shape**: `rl2:EventConstraintShape`

**Example**:
```turtle
ex:approvalRequired a rl2:EventConstraint ;
    rl2:expectsEvent [
        a rl2:Event ;
        rl2:approver ex:DataOwner
    ] .
```

**Notes**: The expected event acts as a pattern. An actual event matches if it has the same type and all specified properties.

---

### rl2:RuntimeReference

**Definition**: A value reference resolved at evaluation time. Used in `rightOperandRef` for dynamic comparisons.

**Type**: `owl:Class`

**Core Instances**:
- `rl2:currentAgent` — Resolves to `Env.Agent` (the requesting agent)

**Notes**:
- `RuntimeReference` represents comparison *values*, not conditions
- Used with `dutyPerformerOperand` for identity binding patterns
- SHACL warns when `dutyPerformerOperand` is compared against non-RuntimeReference IRIs (security concern)

**Example**:
```turtle
# Tun-sollen: current agent must have fulfilled the duty
ex:identityCheck a rl2:AtomicConstraint ;
    rl2:targetNorm ex:paymentDuty ;
    rl2:leftOperand rl2:dutyPerformerOperand ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperandRef rl2:currentAgent .  # RuntimeReference
```

---

### rl2:LeftOperand

**Definition**: A property or attribute to be evaluated in a condition.

**Type**: `owl:Class`

**Notes**:
- RL2 Core defines four state-query instances plus `currentDateTime` (see below)
- Profiles define additional domain-specific operands (purpose, dateTime, recipient, etc.)
- Examples: `purpose`, `dateTime`, `spatial`, `payAmount`

**Core Instances**:

| Instance | Description | Requires |
|----------|-------------|----------|
| `rl2:obligationStateOperand` | Queries the Duty status derived from policy content and the WorldSnapshot | `rl2:targetNorm` (Duty-valued) |
| `rl2:dutyPerformerOperand` | Projects the unambiguous fulfillment actor from WorldSnapshot evidence | `rl2:targetNorm` (Duty-valued) |
| `rl2:promiseStateOperand` | Queries the Promise status derived from policy content and the WorldSnapshot | `rl2:targetNorm` (Promise-valued) |
| `rl2:promisorOperand` | Reads the Agent bound by the targeted Promise's immutable policy content | `rl2:targetNorm` (Promise-valued) |

**Example (Tun-sollen pattern — "I must fulfill the duty myself")**:
```turtle
ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Resource ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:obligationStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:Fulfilled
        ] ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:dutyPerformerOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

---

## 8. Operational Layer Classes

### rl2:Event

**Definition**: An observable occurrence pattern used to select immutable WorldSnapshot evidence.
Storage append behavior is not part of core semantics. `Performed` and `DutyPerformer` are derived
from matching evidence rather than independently asserted status fields.

**Type**: `owl:Class` (event *kinds* are individuals of this class; kind subsumption via `rl2:eventKindIncludedIn`, not `rdfs:subClassOf`)

**Optional Properties**:
- `rl2:eventTime` — When the evidence occurrence happened; core temporal selection uses this value
- `rl2:eventSequence` — Optional future-protocol/storage metadata; ignored by core evidence
  selection and never used to break a semantic tie
- `rl2:operationalAgent` — Agent performing the event (the witness performer)
- `rl2:eventAction` — **(S6)** The action an `ActionPerformed` event witnesses (drives `Performed`)
- `rl2:eventObject` — **(S6)** The asset/resource acted upon
- `rl2:eventKindIncludedIn` — **(S6)** Transitive individual-level event-kind subsumption (the counterpart of `rl2:includedIn` for actions)
- `rl2:participant` — General participant in the event
- `rl2:approver` — Agent whose approval this event represents
- `rl2p:affectsCase` — The case this event affects (scope)
- `rl2:after` — Event that must precede this one. **Outside the specified evaluator core
  (S8a)**: implementation-defined semantics, not evaluated by `evalIR`; an authoring/profile
  hint until bounded temporal semantics are specified (WP-4).

**SHACL Shape**: `rl2:EventShape`

**Example**:
```turtle
ex:accessEvent a rl2:Event ;
    rl2:operationalAgent ex:Researcher .

ex:approvalEvent a rl2:Event ;
    rl2:approver ex:DataOwner .
```

---

### rl2:ObligationState

**Definition**: Enumeration of known semantic results for a Duty.

**Type**: `owl:Class`

**Members**: `rl2:Pending`, `rl2:Active`, `rl2:Fulfilled`, `rl2:Violated`

**Usage**: A derived known result may be serialized via `rl2:obligationState`. The property is not
authoritative evaluator input.

**State Descriptions**:
- **Pending**: Exists but not yet fulfilled or violated; for duties this often means activation condition not yet met
- **Active**: Duty is active and must be fulfilled
- **Fulfilled**: Duty has been satisfied
- **Violated**: Duty was not fulfilled within required constraints

The result is derived independently for each snapshot. Achievement and Maintenance criteria are
defined in `RL2_Semantics.md`; no transition sequence is required by core RL2.

---

### rl2:PromiseState

**Definition**: Enumeration of known semantic results for a Promise.

**Type**: `owl:Class`

**Members**: `rl2:Pending`, `rl2:Fulfilled`, `rl2:Violated` (shared with `rl2:ObligationState`; promises do not use `Active`)

**Usage**: A derived known result may be serialized via `rl2:promiseState`. The property is not
authoritative evaluator input.

**State Descriptions**:
- **Pending**: Promise exists but has not been fulfilled or violated (Active is not used for promises; linked duties projecting to Active collapse to Pending)
- **Fulfilled**: Promise content has been satisfied
- **Violated**: Promise was broken or deadline expired

The retained future protocol projects `rl2:ObligationState` through
`rl2p:requirementStatus`. That projection is not part of core language conformance.

---

### rl2:StateTransition

**Definition**: A transition in system state resulting from events or actions.

**Type**: `owl:Class`

**Required Properties**:
- `rl2:triggeredBy` — Event that caused the transition
- `rl2:fromState` — State before transition
- `rl2:toState` — State after transition

**SHACL Shape**: `rl2:StateTransitionShape`

**Example**:
```turtle
ex:activation a rl2:StateTransition ;
    rl2:triggeredBy ex:accessEvent ;
    rl2:fromState rl2:Pending ;
    rl2:toState rl2:Active .
```

---

## 9. Policy Container Classes

### rl2:Policy

**Definition**: A container of one or more normative clauses.

**Type**: `owl:Class`

**Subclasses**: Set, Offer, Agreement, Privacy, Assertion

**Properties**:
- `rl2:clause` — Norms contained in the policy (required, at least one)
- `rl2:grantor` — Agent who issues the policy (optional)
- `rl2:grantee` — Agent who receives privileges (optional)
- `rl2:condition` — Activation condition for the policy (optional)
- `rl2:policyGeneration` — Generation identifier (optional)

**SHACL Shape**: `rl2:PolicyShape`

**Notes**: Policy is typically used through its subclasses. Policy-level conditions enable dynamic applicability.

---

### rl2:Set

**Definition**: A unilateral policy declaration without identified counterparties.

**Type**: `owl:Class`

**Superclass**: `rl2:Policy`

**Notes**:
- Sets express normative positions without binding specific parties
- No acceptance required
- Use for public licenses, general terms, policy templates

**Example**:
```turtle
ex:termsOfService a rl2:Set ;
    rl2:clause ex:acceptableUse .
```

---

### rl2:Offer

**Definition**: A policy proposed by an assigner to potential assignees, awaiting acceptance.

**Type**: `owl:Class`

**Superclass**: `rl2:Policy`

**Notes**:
- Promises are voluntary commitments but create no Agreement Duty or correlative Claim before acceptance
- Pure materialization produces an Agreement or an attributed rejection
- Promise-valued targets are permitted only between sibling clauses of the same Offer
- An Offer condition is proposed Agreement applicability, not offer validity
- Grantor identifies the offering party

**Example**:
```turtle
ex:licenseOffer a rl2:Offer ;
    rl2:grantor ex:Publisher ;
    rl2:clause ex:usePrivilege .
```

---

### rl2:Agreement

**Definition**: A bilateral or multilateral policy with identified, consenting parties.

**Type**: `owl:Class`

**Superclass**: `rl2:Policy`

**Required Properties** (additional to Policy):
- `rl2:grantor` — Must be specified
- `rl2:grantee` — Must be specified

**SHACL Shape**: `rl2:AgreementShape`

**Notes**:
- All parties are explicitly identified
- Duties create enforceable obligations
- Violations have normative consequences
- A materialized Agreement contains no Promise clauses

**Example**:
```turtle
ex:dataContract a rl2:Agreement ;
    rl2:grantor ex:DataProvider ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:accessPrivilege ;
    rl2:clause ex:deletionDuty .
```

---

### rl2:Privacy

**Definition**: A policy governing personal data processing and data subject rights.

**Type**: `owl:Class`

**Superclass**: `rl2:Policy`

**Typical Contents**:
- Duties on data controllers (processing limitations, retention)
- Privileges for data subjects (access, deletion, portability)
- Conditions related to consent and purpose

**Note**: For comprehensive GDPR coverage, Privacy policies benefit from integration with vocabularies such as DPV (Data Privacy Vocabulary) and GDPRtEXT. See [Rodríguez-Doncel 2024] for analysis of policy language coverage of GDPR informational items.

**Example**:
```turtle
ex:privacyPolicy a rl2:Privacy ;
    rl2:clause ex:processOnlyWithConsent ;
    rl2:clause ex:subjectAccessRight .
```

---

### rl2:Assertion

**Definition**: A policy stating claims or facts about normative status.

**Type**: `owl:Class`

**Superclass**: `rl2:Policy`

**Notes**:
- Declares that certain privileges, duties, or conditions hold
- Does not necessarily create norms
- Use for compliance statements, certifications, status declarations

**Example**:
```turtle
ex:complianceAssertion a rl2:Assertion ;
    rl2:clause ex:gdprComplianceStatement .
```

---

## 10. Operator Classes

### rl2:Operator

**Definition**: Abstract base class for constraint operators.

**Type**: `owl:Class`

**Subclasses**: LogicalOperator, ComparisonOperator

---

### rl2:LogicalOperator

**Definition**: Operators for combining conditions.

**Type**: `owl:Class`

**Superclass**: `rl2:Operator`

**Members**: `rl2:and`, `rl2:or`, `rl2:xone`, `rl2:not`

---

### rl2:ComparisonOperator

**Definition**: Operators for comparing values.

**Type**: `owl:Class`

**Superclass**: `rl2:Operator`

**Members**: `rl2:eq`, `rl2:neq`, `rl2:lt`, `rl2:lte`, `rl2:gt`, `rl2:gte`, `rl2:isA`, `rl2:isAnyOf`, `rl2:isAllOf`, `rl2:isNoneOf`

---

## 11. Property Reference

### Normative Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:subject` | Norm | Agent | Agent bearing the normative status |
| `rl2:counterparty` | Norm | Agent | Agent in correlative position |
| `rl2:action` | Norm | Action | Action specified in the norm |
| `rl2:prohibitedAction` | Prohibition | Action | Action that is forbidden (subproperty of action) |
| `rl2:includedIn` | Action | Action | Action taxonomy: narrower action included in broader (transitive) |
| `rl2:object` | Norm, Promise | Asset | Asset the norm or Promise concerns; may be acceptance-bound for action/state Offers |
| `rl2:condition` | Norm, Policy | Condition | Activation condition |
| `rl2:prerequisiteDuty` | Privilege | Duty | Applicable Duty that must be Fulfilled before the Privilege can contribute a permit |
| `rl2:correlativeTo` | Norm | Norm | Links correlative Hohfeldian positions |
| `rl2:affectsNorm` | Power | Norm | Norm that the power can affect |
| `rl2:exposedTo` | Liability | Power | Power to which liability is exposed |
| `rl2:immuneFrom` | Immunity | Power | Power from which immunity protects |
| `rl2:priority` | Norm | xsd:integer | Numeric priority for conflict resolution (higher wins) |

### Promise Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:promisor` | Promise | Agent | Agent making the promise |
| `rl2:promisee` | Promise | Agent | Agent receiving the promise |
| `rl2:promisedAction` | Promise | Action | Tun-sollen content; object may be authored or acceptance-bound |
| `rl2:promisedState` | Promise | Condition | Sein-sollen content |
| `rl2:promisedDuty` | Promise | Duty | Suretyship content |
| `rl2:promiseState` | Promise | PromiseState | Current promise state |

### Policy Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:clause` | Policy | Clause | Norm or Promise contained in the policy, subject to policy-type SHACL rules |
| `rl2:clauseOf` | Clause | Policy | Inverse of clause |
| `rl2:grantor` | Policy | Agent | Agent issuing the policy |
| `rl2:grantee` | Policy | Agent | Agent receiving privileges |
| `rl2:policyGeneration` | Policy | xsd:anyURI | Generation identifier |
| `rl2:requiresProfile` | Policy | Profile | Required profile; unsupported or incompatible versions cause load-time rejection |

### Profile Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:profileVersion` | Profile | xsd:string | SemVer profile version used for same-major, at-least-required-version negotiation |

### Role Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:approver` | Norm ∪ Event | Agent | Agent whose approval is required |
| `rl2:operationalAgent` | Norm ∪ Event | Agent | Agent performing operational actions |
| `rl2:participant` | Event | Agent | General participant |

### Condition Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:leftOperand` | Condition | LeftOperand | Property being evaluated |
| `rl2:constraintOperator` | Condition | Operator | Operator for evaluation |
| `rl2:rightOperand` | Condition | (literal) | Literal value for comparison |
| `rl2:rightOperandRef` | Condition | (resource) | Resource for comparison |
| `rl2:targetNorm` | AtomicConstraint | Norm (RDFS); Promise admitted by SHACL | Duty/norm or same-Offer sibling Promise whose state to query; core materialization rewrites only `promiseStateOperand` targets and rejects unsupported Promise queries |
| `rl2:operand` | LogicalConstraint | Condition | Sub-condition |
| `rl2:expectsEvent` | EventConstraint | Event | Required event |
| `rl2:resolutionPath` | LeftOperand | xsd:string | Sandboxed path resolved from the evaluation environment |
| `rl2:resolutionFunction` | LeftOperand | xsd:string | Profile-defined external/derived resolver name; outside the specified evaluator core |

### Event Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:eventTime` | Event | xsd:dateTime | When event occurred (coarse order) |
| `rl2:eventSequence` | Event | xsd:integer | Optional future-protocol/storage sequence; ignored by core evaluation |
| `rl2:eventAction` | Event | Action | Action an ActionPerformed event witnesses (S6) |
| `rl2:eventObject` | Event | — | Asset/resource acted upon (S6) |
| `rl2:eventKindIncludedIn` | Event | Event | Transitive event-kind subsumption (S6) |
| `rl2:after` | Event | Event | Temporal sequence (outside the specified evaluator core, S8a) |

### Operational Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:obligationState` | Duty | ObligationState | Optional serialization of derived known Duty status |
| `rl2:postCondition` | Duty | Condition | Achievement witness qualification condition |
| `rl2:invariant` | Duty | Condition | Maintenance condition that must hold throughout the window |
| `rl2:dutyWindow` | Duty | DutyWindow | Optional finite half-open assessment interval |
| `rl2:startInclusive` | DutyWindow | xsd:dateTimeStamp | Inclusive interval start |
| `rl2:endExclusive` | DutyWindow | xsd:dateTimeStamp | Exclusive interval end |
| `rl2:triggeredBy` | StateTransition | Event | Triggering event |
| `rl2:fromState` | StateTransition | (any) | State before transition |
| `rl2:toState` | StateTransition | (any) | State after transition |

### Asset Collection Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:member` | AssetCollection | Asset | Static member |

---

## 12. Named Individuals

### Logical Operators

| Individual | Type | Description |
|------------|------|-------------|
| `rl2:and` | LogicalOperator | Conjunction: all operands must hold |
| `rl2:or` | LogicalOperator | Disjunction: at least one must hold |
| `rl2:xone` | LogicalOperator | Exclusive or: exactly one must hold |
| `rl2:not` | LogicalOperator | Negation: operand must not hold |

### Comparison Operators

| Individual | Type | Description |
|------------|------|-------------|
| `rl2:eq` | ComparisonOperator | Equal to |
| `rl2:neq` | ComparisonOperator | Not equal to |
| `rl2:lt` | ComparisonOperator | Less than |
| `rl2:lte` | ComparisonOperator | Less than or equal |
| `rl2:gt` | ComparisonOperator | Greater than |
| `rl2:gte` | ComparisonOperator | Greater than or equal |
| `rl2:isA` | ComparisonOperator | Type membership |
| `rl2:isAnyOf` | ComparisonOperator | Value in set |
| `rl2:isAllOf` | ComparisonOperator | Satisfies all in set |
| `rl2:isNoneOf` | ComparisonOperator | Value not in set |

### Obligation States

| Individual | Type | Description |
|------------|------|-------------|
| `rl2:Pending` | ObligationState | Exists, not fulfilled/violated (often pre-activation for duties) |
| `rl2:Active` | ObligationState | Must be fulfilled |
| `rl2:Fulfilled` | ObligationState | Successfully completed |
| `rl2:Violated` | ObligationState | Failed to fulfill |

### Promise States

| Individual | Type | Description |
|------------|------|-------------|
| `rl2:Pending` | PromiseState | Commitment exists, not fulfilled or violated (no Active for promises) |
| `rl2:Fulfilled` | PromiseState | Successfully kept |
| `rl2:Violated` | PromiseState | Broken |

### Left Operand Instances

| Individual | Type | Description |
|------------|------|-------------|
| `rl2:obligationStateOperand` | LeftOperand | Queries derived Duty status for `targetNorm` |
| `rl2:dutyPerformerOperand` | LeftOperand | Projects the fulfillment actor from snapshot evidence |
| `rl2:promiseStateOperand` | LeftOperand | Queries derived Promise status for `targetNorm` |
| `rl2:promisorOperand` | LeftOperand | Reads the targeted Promise's declared promisor |
| `rl2:currentDateTime` | LeftOperand | Resolves to `WorldSnapshot.evaluationTime` |

### Runtime Reference Instances

| Individual | Type | Description |
|------------|------|-------------|
| `rl2:currentAgent` | RuntimeReference | Resolves to Env.Agent at evaluation time |

---

## 13. SHACL Validation Summary

The following SHACL shapes validate RL2 policies. See **rl2-shacl.ttl** for complete definitions.

### Policy Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:PolicyShape` | rl2:Policy | At least one clause; optional grantor, grantee, condition, generation |
| `rl2:AgreementShape` | rl2:Agreement | Requires grantor and grantee |

### Norm Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:PrivilegeShape` | rl2:Privilege | Requires subject, action, object; validates prerequisite Duty values |
| `rl2:PrerequisiteDutyShape` | prerequisite Duty objects | Enforces Privilege and Policy ownership and no independent clause role |
| `rl2:DutyShape` | rl2:Duty | Requires one canonical Achievement or Maintenance content form |
| `rl2:DutyStateShape` | rl2:Duty | Valid obligationState values |
| `rl2:ProhibitionShape` | rl2:Prohibition | Requires subject, prohibitedAction, object |
| `rl2:ClaimShape` | rl2:Claim | Requires subject, counterparty, and exactly one correlative Duty; rejects authored action/object/condition and enforces mirrored party roles |
| `rl2:PowerShape` | rl2:Power | Requires subject, affectsNorm |
| `rl2:LiabilityShape` | rl2:Liability | Requires subject, exposedTo |
| `rl2:ImmunityShape` | rl2:Immunity | Requires subject, immuneFrom |

### Promise Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:PromiseShape` | rl2:Promise | Requires promisor, promisee, and exactly one of promisedAction/promisedState/promisedDuty |
| `rl2:PromiseStateShape` | rl2:Promise | Valid promiseState values |

### Condition Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:AtomicConstraintShape` | rl2:AtomicConstraint | Requires leftOperand, ComparisonOperator, rightOperand or rightOperandRef; validates targetNorm if present |
| `rl2:NormStateConstraintShape` | AtomicConstraint with obligationStateOperand/dutyPerformerOperand | Requires exactly one Norm-valued targetNorm |
| `rl2:PromiseStateConstraintShape` | AtomicConstraint with promiseStateOperand/promisorOperand | Requires exactly one Promise-valued targetNorm |
| `rl2:PromiseTargetLocalityShape` | AtomicConstraint with a Promise-valued targetNorm | Requires the target and containing condition to belong to the same Offer |
| `rl2:LogicalConstraintShape` | rl2:LogicalConstraint | Requires one LogicalOperator; operator-specific shapes require one operand for not and at least two for and/or/xone |
| `rl2:EventConstraintShape` | rl2:EventConstraint | Requires expectsEvent |
| `rl2:DynamicOperandPairingShape` | AtomicConstraint with dutyPerformerOperand | Warns if rightOperandRef is not a RuntimeReference |

### Operational Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:EventShape` | rl2:Event | At most one operationalAgent |
| `rl2:StateTransitionShape` | rl2:StateTransition | Requires triggeredBy, fromState, toState |
| `rl2:AssetCollectionShape` | rl2:AssetCollection | Members are Assets |
| `rl2:NormPriorityShape` | rl2:Norm | Priority must be an integer |

---

## 14. RL2 Protocol Vocabulary (rl2p:)

The retained RL2 Protocol namespace (`https://rl2.example/protocol#`, prefix `rl2p:`) defines
experimental runtime artifacts. See `../future/protocol/rl2p.ttl`; these terms are outside core
language conformance under SCOPE-2.

### rl2p:Requirement (Universal Runtime Obligation)

**Definition**: A runtime obligation that must be fulfilled. Universal structure tracking Duties, Promises, and Claims at runtime.

**Type**: `owl:Class`

**Required Properties**:
- `rl2p:sourceNorm` — The norm or promise that created this requirement
- `rl2p:sourcePolicy` — The policy containing the source norm
- `rl2p:requirementStatus` — Current lifecycle status (uses `rl2:ObligationState`)
- `rl2p:imposedTime` — When the requirement was created

**Optional Properties**:
- `rl2p:counterparty` — The agent who holds the correlative position (for Claims)
- `rl2p:fulfilledByAction` — Action that fulfilled the requirement
- `rl2p:fulfilledByEvent` — Event evidencing fulfillment
- `rl2p:fulfillmentEvidence` — Reference to supporting evidence
- `rl2p:requirementLabel` — Human-readable label
- `rl2p:requirementDescription` — Human-readable description

Former lifecycle projection rules are preserved in `../future/protocol/` while the core derives
Duty and Promise status directly from a WorldSnapshot.

**SHACL Shape**: `rl2p:RequirementShape`, `rl2p:RequirementFulfillmentAuditShape`

The former Promise-as-generator workflow is preserved in `../future/protocol/RL2_Protocol.md`;
this entry lists the retained experimental properties only.

**Example (Duty-sourced Requirement)**:
```turtle
ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:Licensee ; rl2:action ex:pay ; rl2:object ex:License .

ex:licenseAgreement a rl2:Agreement ;
    rl2:grantor ex:Licensor ; rl2:grantee ex:Licensee ;
    rl2:clause ex:paymentDuty .

ex:paymentReq a rl2p:Requirement ;
    rl2p:sourceNorm ex:paymentDuty ;
    rl2p:sourcePolicy ex:licenseAgreement ;
    rl2p:requirementStatus rl2:Pending ;
    rl2p:imposedTime "2025-01-15T10:00:00Z"^^xsd:dateTime .
```

**Example (Promise-sourced Requirement with Counterparty)**:
```turtle
ex:dataQualityPromise a rl2:Promise ;
    rl2:promisor ex:DataProvider ; rl2:promisee ex:DataConsumer ;
    rl2:promisedState ex:qualityThresholdMet ;
    rl2:object ex:DataAsset .

ex:DataAsset a rl2:Asset .

# A Promise's natural home is an Offer. (In an accepted Agreement it would have
# crystallized into a Duty + correlative Claim.)
ex:dataOffer a rl2:Offer ;
    rl2:grantor ex:DataProvider ; rl2:grantee ex:DataConsumer ;
    rl2:clause ex:dataQualityPromise .

ex:dataQualityReq a rl2p:Requirement ;
    rl2p:sourceNorm ex:dataQualityPromise ;
    rl2p:sourcePolicy ex:dataOffer ;
    rl2p:counterparty ex:DataConsumer ;  # The promisee/Claim holder
    rl2p:requirementStatus rl2:Pending ;
    rl2p:imposedTime "2025-01-15T10:00:00Z"^^xsd:dateTime .
```

**Hohfeldian Mapping**:

| Hohfeldian Norm | Protocol Artifact |
|-----------------|-------------------|
| Duty | `rl2p:Requirement` (sourceNorm → Duty) |
| Promise | `rl2p:Requirement` (sourceNorm → Promise) |
| Claim | `rl2p:Requirement` (with counterparty) |
| Privilege | `rl2p:Decision` (Permit) |
| Power | Normative ability to alter a relation; the actual mutation mechanism is outside core evaluation |
| Immunity | Not an effect or a `rl2p:Decision` — a precondition that blocks `ExercisePower`: `ImmunityActive(a, n) → ¬canExercise(Power(h, n))` (see `RL2_Semantics.md`, “Powers and Immunities”) |

---

### Request Property Reference

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2p:requestingAgent` | Request | Agent | Agent that would perform the requested action |
| `rl2p:requestor` | Request | Agent | Agent submitting the request; may differ from requestingAgent |
| `rl2p:requestedAction` | Request | Action | Requested action |
| `rl2p:requestedAsset` | Request | Asset | Asset on which the action is requested |
| `rl2p:requestTime` | Request | xsd:dateTime | Submission time |

### Context Assertion Property Reference

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2p:forRequest` | ContextAssertion | Request | Request for which the assertion supplies context |
| `rl2p:contextSubject` | ContextAssertion | rdfs:Resource | Resource about which a value is asserted |
| `rl2p:contextProperty` | ContextAssertion | LeftOperand | Operand/property being asserted |
| `rl2p:contextValue` | ContextAssertion | (literal) | Literal value; exclusive with contextValueRef |
| `rl2p:contextValueRef` | ContextAssertion | (resource) | Resource value; exclusive with contextValue |
| `rl2p:assertedBy` | ContextAssertion | Agent | Agent or system reporting the assertion |
| `rl2p:assertedTime` | ContextAssertion | xsd:dateTime | Assertion time |
| `rl2p:performer` | ContextAssertion | Agent | Agent that performed the witnessed action; distinct from assertedBy and consumed by witness derivation |

### Case Property Reference

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2p:initialRequest` | Case | Request | Request that created the Case |
| `rl2p:caseCreated` | Case | xsd:dateTime | Creation time |
| `rl2p:caseStatus` | Case | CaseStatus | Current materialized status projection |
| `rl2p:policyGeneration` | Case | xsd:anyURI | Immutable policy generation selected at Case creation |
| `rl2p:evaluationHistory` | Case | EvaluationResult | Evaluations associated with the Case |
| `rl2p:expirationTime` | Case | xsd:dateTime | Expiration time, when applicable |
| `rl2p:caseNote` | Case | xsd:string | Administrative note |

### Evaluation Result Property Reference

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2p:evaluatedRequest` | EvaluationResult | Request | Request evaluated |
| `rl2p:decision` | EvaluationResult | Decision | Evaluation decision |
| `rl2p:evaluationTime` | EvaluationResult | xsd:dateTime | Evaluation time |
| `rl2p:matchedPolicies` | EvaluationResult | Policy | Policies evaluated for the request |
| `rl2p:matchedNorms` | EvaluationResult | Norm | Matching normative clauses |
| `rl2p:explanation` | EvaluationResult | xsd:string | Human-readable explanation |

### Requirement Property Reference

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2p:sourceNorm` | Requirement | Norm \| Promise | The norm or promise that created this requirement |
| `rl2p:sourcePolicy` | Requirement | Policy | Policy containing the source norm |
| `rl2p:counterparty` | Requirement | Agent | Agent holding correlative position (Claim holder) |
| `rl2p:requirementStatus` | Requirement | ObligationState | Current lifecycle status |
| `rl2p:imposedTime` | Requirement | xsd:dateTime | When requirement was created |
| `rl2p:fulfilledByAction` | Requirement | Action | Action that fulfilled the requirement |
| `rl2p:fulfilledByEvent` | Requirement | Event | Event evidencing fulfillment |
| `rl2p:fulfillmentEvidence` | Requirement \| ContextAssertion | (any) | Supporting evidence; deliberately domain-unrestricted for both audit and fulfillment-as-context use |
| `rl2p:requirementLabel` | Requirement | xsd:string | Human-readable label |
| `rl2p:requirementDescription` | Requirement | xsd:string | Human-readable description |
| `rl2p:activeRequirements` | EvaluationResult | Requirement | Requirements that must be fulfilled |

---

### Protocol Left Operands

| Left Operand | Description |
|---------------|-------------|
| `rl2p:requirementFulfilled` | Left operand for querying whether a Requirement is fulfilled (an `rl2:LeftOperand` individual, not an OWL property) |

---

## Appendix: Design Notes

### Why No-Claim and Disability Are Not Classes

Hohfeld identified these as correlatives of Privilege and Immunity respectively. RL2 does not model them as explicit classes because:

1. They represent *absences* of positions, not positions themselves
2. They are inferrable: absence of Claim implies No-Claim; absence of Power implies Disability
3. Modeling absences as classes is ontologically problematic

### Why Prohibition Is a Separate Class

In strict Hohfeldian terms, prohibition is a Duty to refrain. RL2 separates it because:

1. Policy authors express prohibitions as "may not" rather than "duty to not"
2. `rl2:prohibitedAction` is clearer than negated action constructs
3. It aligns with ODRL and eases translation

### Open Shapes Design

SHACL shapes are intentionally non-closed to support:

1. Profile extensions (adding domain-specific properties)
2. Implementation metadata (tracking, provenance)
3. Forward compatibility (new properties in future versions)

### Profile Extensibility Points

RL2 Core leaves these deliberately open for profiles to define:

- **Actions**: Domain-specific action instances
- **LeftOperands**: Domain-specific evaluation properties
- **Assets**: Domain-specific asset types
- **Agents**: Domain-specific agent classifications
- **Temporal extensions**: Richer temporal operators (Allen relations, recurrence) if needed

---

## References

For complete bibliography and glossary, see **RL2_References.md**.

---

*This informative reference covers RL2 core version 0.6 and the retained rl2p 0.5 future-protocol
vocabulary. Core normative definitions are in `../spec/rl2.ttl` and
`../spec/rl2-shacl.ttl`; protocol files under `../future/protocol/` are non-core.*
