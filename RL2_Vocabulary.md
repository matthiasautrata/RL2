---
title: "RL2 Vocabulary Reference"
subtitle: "Complete Class and Property Definitions"
version: "0.2"
status: "Draft"
date: 2025-01-01
purpose: "Reference documentation for all RL2 ontology terms"
---

## About This Document

This document provides complete reference documentation for every class, property, and named individual in the RL2 ontology. It is organized for lookup, not learning.

For readers new to RL2, **RL2_Primer.md** provides a progressive introduction to the concepts.

This document serves as the authoritative lookup reference for RL2 terms.

### Document Structure

- Section 2: Namespace and conformance
- Section 3: Class index (alphabetical listing)
- Sections 4-11: Class definitions by layer
- Section 12: Property reference
- Section 13: Operators and enumerations
- Section 14: SHACL validation summary

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
9. [Temporal Classes](#9-temporal-classes)
10. [Policy Container Classes](#10-policy-container-classes)
11. [Operator Classes](#11-operator-classes)
12. [Property Reference](#12-property-reference)
13. [Named Individuals](#13-named-individuals)
14. [SHACL Validation Summary](#14-shacl-validation-summary)

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
  owl:versionInfo "0.2" ;
  owl:versionIRI <https://rl2.example/ontology/0.2> .
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
| `rl2:ContextualConstraint` | Condition | Constraint depending on environment |
| `rl2:Duty` | Normative | An obligation imposed on an agent |
| `rl2:DynamicOperandReference` | Condition | Reference resolved at evaluation time |
| `rl2:EffectiveInterval` | Temporal | A time interval with start and end |
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
| `rl2:PromiseContent` | Promise | Union type for promise content |
| `rl2:PromiseState` | Operational | State enumeration for promises |
| `rl2:Set` | Policy | Unilateral policy declaration |
| `rl2:StateTransition` | Operational | Transition in system state |
| `rl2:TemporalConstraint` | Condition | Time-based condition |

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

**Definition**: An obligation imposed on an agent to perform an action.

**Type**: `owl:Class`

**Superclass**: `rl2:Norm`

**Required Properties**:
- `rl2:subject` — Agent who bears the duty
- `rl2:action` — Action that must be performed
- `rl2:object` — Asset the duty concerns

**Optional Properties**:
- `rl2:condition` — When/how the duty applies (often includes deadline)
- `rl2:counterparty` — Agent to whom the duty is owed
- `rl2:obligationState` — Current lifecycle state

**SHACL Shape**: `rl2:DutyShape`, `rl2:DutyStateShape`

**Example**:
```turtle
ex:reportDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:submitReport ;
    rl2:object ex:Dataset ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [ rl2:end "2025-06-30T23:59:59Z"^^xsd:dateTime ]
    ] .
```

**Hohfeldian Context**: Duty correlates with Claim. If Alice has a duty to X, Bob (the counterparty) has a claim that Alice X.

**Lifecycle**: See `rl2:ObligationState` for the Pending → Active → Fulfilled/Violated state machine.

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
- `rl2:claimHolder` — Agent who holds the claim (the right-holder)
- `rl2:claimAgainst` — Agent against whom the claim is held (the duty-bearer)

**Optional Properties**:
- `rl2:correlativeTo` — The corresponding Duty
- `rl2:condition` — When the claim is active

**SHACL Shape**: `rl2:ClaimShape`

**Example**:
```turtle
ex:bobClaim a rl2:Claim ;
    rl2:claimHolder ex:Bob ;
    rl2:claimAgainst ex:Alice ;
    rl2:correlativeTo ex:aliceDuty .
```

**Hohfeldian Context**: Claim is the correlative of Duty. Claims and duties are two sides of the same relationship.

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
- `rl2:promiseContent` — What is promised (Action, Duty, or Condition)

**Optional Properties**:
- `rl2:promiseState` — Current state of the promise

**SHACL Shapes**: `rl2:PromiseShape`, `rl2:PromiseStateShape`

**Example**:
```turtle
ex:dataPromise a rl2:Promise ;
    rl2:promisor ex:Researcher ;
    rl2:promisee ex:DataOwner ;
    rl2:promiseContent ex:dataStewardshipDuty ;
    rl2:promiseState rl2:PromisePending .
```

**Notes**: Promises are fundamentally different from Duties:
- Duties are imposed; promises are voluntary
- Duties may have abstract counterparties; promises always have specific promisees
- Promises may *create* duties but are not themselves duties

---

### rl2:PromiseContent

**Definition**: Union type for what may constitute the content of a promise.

**Type**: `owl:Class` (union)

**Members**: `rl2:Action`, `rl2:Duty`, `rl2:Condition`

**Notes**: This is a union class used as the range of `rl2:promiseContent`. The promisor commits to performing an Action, fulfilling a Duty, or ensuring a Condition holds.

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

### Union Classes for Role Properties

**rl2:NormOrEvent**: Union of `rl2:Norm` and `rl2:Event`. Used as domain for properties applicable to both, such as `rl2:approver` and `rl2:operationalAgent`.

**rl2:ConditionOrEvent**: Union of `rl2:Condition` and `rl2:Event`. Used as range for `rl2:requires`.

---

## 7. Action, Asset, and Condition Classes

### rl2:Action

**Definition**: An action that may be performed on an asset.

**Type**: `owl:Class`

**Notes**:
- RL2 Core does not define specific action instances
- Actions are provided by domain profiles
- Examples: `play`, `use`, `distribute`, `delete`, `modify`

**Example**:
```turtle
# Profile-defined actions
ex:use a rl2:Action .
ex:distribute a rl2:Action .
ex:delete a rl2:Action .
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

**Definition**: A collection of assets, possibly dynamically determined.

**Type**: `owl:Class`

**Properties**:
- `rl2:member` — Static member assets
- `rl2:dynamicQuery` — Query expression for dynamic membership

**SHACL Shape**: `rl2:AssetCollectionShape`

**Example**:
```turtle
ex:sensitiveAssets a rl2:AssetCollection ;
    rl2:member ex:customerData ;
    rl2:member ex:financialRecords .

ex:classifiedDocs a rl2:AssetCollection ;
    rl2:dynamicQuery "SELECT ?d WHERE { ?d ex:classification 'SECRET' }" .
```

**Security Note**: Implementations must sanitize `dynamicQuery` values to prevent injection attacks.

---

### rl2:Condition

**Definition**: Base class for constraints that must hold for a norm or policy to be active.

**Type**: `owl:Class`

**Subclasses**: AtomicConstraint, LogicalConstraint, TemporalConstraint, ContextualConstraint, EventConstraint, DynamicOperandReference

**Common Properties**:
- `rl2:constraintOperator` — Operator for evaluation
- `rl2:requires` — Composite requirements

---

### rl2:AtomicConstraint

**Definition**: A simple comparison constraint with left operand, operator, and right operand.

**Type**: `owl:Class`

**Superclass**: `rl2:Condition`

**Required Properties**:
- `rl2:leftOperand` — Property being evaluated
- `rl2:constraintOperator` — Comparison operator (must be ComparisonOperator)
- One of: `rl2:rightOperand` (literal) or `rl2:rightOperandRef` (resource)

**SHACL Shape**: `rl2:AtomicConstraintShape`

**Example**:
```turtle
ex:purposeCheck a rl2:AtomicConstraint ;
    rl2:leftOperand ex:purpose ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperand "research" .
```

---

### rl2:LogicalConstraint

**Definition**: A condition combining other conditions via logical operators.

**Type**: `owl:Class`

**Superclass**: `rl2:Condition`

**Required Properties**:
- `rl2:constraintOperator` — Logical operator (and, or, xone, not)
- `rl2:operand` — Sub-conditions (at least one)

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

---

### rl2:TemporalConstraint

**Definition**: A condition based on time intervals.

**Type**: `owl:Class`

**Superclass**: `rl2:Condition`

**Required Properties**:
- `rl2:interval` — The EffectiveInterval to check against

**SHACL Shape**: `rl2:TemporalConstraintShape`

**Example**:
```turtle
ex:validity a rl2:TemporalConstraint ;
    rl2:interval [
        a rl2:EffectiveInterval ;
        rl2:start "2025-01-01T00:00:00Z"^^xsd:dateTime ;
        rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime
    ] .
```

---

### rl2:ContextualConstraint

**Definition**: A constraint depending on the evaluation context or environment.

**Type**: `owl:Class`

**Superclass**: `rl2:Condition`

**Required Properties**:
- `rl2:contextPath` — Path expression into the context

**SHACL Shape**: `rl2:ContextualConstraintShape`

**Example**:
```turtle
ex:locationCheck a rl2:ContextualConstraint ;
    rl2:contextPath "request.location.country" ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperand "DE" .
```

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

### rl2:DynamicOperandReference

**Definition**: A reference resolved at evaluation time, enabling computed values.

**Type**: `owl:Class`

**Superclass**: `rl2:Condition`

**Required Properties**:
- `rl2:dynamicOperand` — Path expression to resolve

**SHACL Shape**: `rl2:DynamicOperandReferenceShape`

**Example**:
```turtle
ex:deadlineRef a rl2:DynamicOperandReference ;
    rl2:dynamicOperand "event.AccessEvent.timestamp + P30D" .
```

**Security Note**: Implementations must sanitize path expressions to prevent injection attacks.

---

### rl2:LeftOperand

**Definition**: A property or attribute to be evaluated in a condition.

**Type**: `owl:Class`

**Notes**:
- RL2 Core does not define specific left operand instances
- Profiles define domain-specific operands (purpose, dateTime, recipient, etc.)
- Examples: `purpose`, `dateTime`, `spatial`, `payAmount`

---

## 8. Operational Layer Classes

### rl2:Event

**Definition**: An observable occurrence that may trigger obligations or state transitions.

**Type**: `owl:Class`

**Optional Properties**:
- `rl2:operationalAgent` — Agent performing the event
- `rl2:participant` — General participant in the event
- `rl2:approver` — Agent whose approval this event represents
- `rl2:after` — Event that must precede this one

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

**Definition**: Enumeration of possible states for a duty's lifecycle.

**Type**: `owl:Class`

**Members**: `rl2:Pending`, `rl2:Active`, `rl2:Fulfilled`, `rl2:Violated`

**Usage**: Assign via `rl2:obligationState` property on Duty instances.

**State Descriptions**:
- **Pending**: Duty exists but activation condition not yet met
- **Active**: Duty is active and must be fulfilled
- **Fulfilled**: Duty has been satisfied
- **Violated**: Duty was not fulfilled within required constraints

**State Machine**:
```
Pending --[condition true]--> Active
Active  --[action done]-----> Fulfilled
Active  --[deadline passed]-> Violated
```

---

### rl2:PromiseState

**Definition**: Enumeration of possible states for a promise's lifecycle.

**Type**: `owl:Class`

**Members**: `rl2:PromisePending`, `rl2:PromiseFulfilled`, `rl2:PromiseViolated`

**Usage**: Assign via `rl2:promiseState` property on Promise instances.

**State Descriptions**:
- **PromisePending**: Promise made but not yet fulfilled
- **PromiseFulfilled**: Promise content has been satisfied
- **PromiseViolated**: Promise was broken or deadline expired

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

## 9. Temporal Classes

### rl2:EffectiveInterval

**Definition**: A time interval with explicit start and/or end points.

**Type**: `owl:Class`

**Optional Properties**:
- `rl2:start` — Start of interval (xsd:dateTime)
- `rl2:end` — End of interval (xsd:dateTime)

**SHACL Shape**: `rl2:EffectiveIntervalShape`

**Interval Patterns**:
- **Closed** (both start and end): "from X to Y"
- **Open-ended** (start only): "from X onwards"
- **Deadline** (end only): "until Y"
- **Unbounded** (neither): "always" (use sparingly)

**Validation**: SHACL enforces `start ≤ end` when both are present.

**Example**:
```turtle
# Closed interval
ex:year2025 a rl2:EffectiveInterval ;
    rl2:start "2025-01-01T00:00:00Z"^^xsd:dateTime ;
    rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime .

# Deadline only
ex:deadline a rl2:EffectiveInterval ;
    rl2:end "2025-06-30T23:59:59Z"^^xsd:dateTime .
```

**Scope Note**: RL2 Core provides interval-based temporal constraints. Richer temporal operators (Allen's interval relations, recurrence patterns) are delegated to domain profiles.

---

## 10. Policy Container Classes

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
- Creates no obligations until accepted
- Upon acceptance, becomes an Agreement
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

## 11. Operator Classes

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

## 12. Property Reference

### Normative Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:subject` | Norm | Agent | Agent bearing the normative status |
| `rl2:counterparty` | Norm | Agent | Agent in correlative position |
| `rl2:action` | Norm | Action | Action specified in the norm |
| `rl2:prohibitedAction` | Prohibition | Action | Action that is forbidden (subproperty of action) |
| `rl2:object` | Norm | Asset | Asset the norm concerns |
| `rl2:condition` | Norm, Policy | Condition | Activation condition |
| `rl2:correlativeTo` | Norm | Norm | Links correlative Hohfeldian positions |
| `rl2:claimHolder` | Claim | Agent | Agent who holds a claim |
| `rl2:claimAgainst` | Claim | Agent | Agent against whom claim is held |
| `rl2:affectsNorm` | Power | Norm | Norm that the power can affect |
| `rl2:exposedTo` | Liability | Power | Power to which liability is exposed |
| `rl2:immuneFrom` | Immunity | Power | Power from which immunity protects |

### Promise Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:promisor` | Promise | Agent | Agent making the promise |
| `rl2:promisee` | Promise | Agent | Agent receiving the promise |
| `rl2:promiseContent` | Promise | PromiseContent | What is promised |
| `rl2:promiseState` | Promise | PromiseState | Current promise state |

### Policy Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:clause` | Policy | Norm | Norm contained in the policy |
| `rl2:clauseOf` | Norm | Policy | Inverse of clause |
| `rl2:grantor` | Policy | Agent | Agent issuing the policy |
| `rl2:grantee` | Policy | Agent | Agent receiving privileges |
| `rl2:policyGeneration` | Policy | xsd:anyURI | Generation identifier |

### Role Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:approver` | NormOrEvent | Agent | Agent whose approval is required |
| `rl2:operationalAgent` | NormOrEvent | Agent | Agent performing operational actions |
| `rl2:participant` | Event | Agent | General participant |

### Condition Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:leftOperand` | Condition | LeftOperand | Property being evaluated |
| `rl2:constraintOperator` | Condition | Operator | Operator for evaluation |
| `rl2:rightOperand` | Condition | (literal) | Literal value for comparison |
| `rl2:rightOperandRef` | Condition | (resource) | Resource for comparison |
| `rl2:operand` | LogicalConstraint | Condition | Sub-condition |
| `rl2:requires` | Condition | ConditionOrEvent | Composite requirement |
| `rl2:interval` | TemporalConstraint | EffectiveInterval | Time interval |
| `rl2:contextPath` | ContextualConstraint | xsd:string | Path into context |
| `rl2:dynamicOperand` | DynamicOperandReference | xsd:string | Path expression |
| `rl2:expectsEvent` | EventConstraint | Event | Required event |

### Temporal Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:start` | EffectiveInterval | xsd:dateTime | Interval start |
| `rl2:end` | EffectiveInterval | xsd:dateTime | Interval end |
| `rl2:after` | Event | Event | Temporal sequence |

### Operational Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:obligationState` | Duty | ObligationState | Current duty state |
| `rl2:triggeredBy` | StateTransition | Event | Triggering event |
| `rl2:fromState` | StateTransition | (any) | State before transition |
| `rl2:toState` | StateTransition | (any) | State after transition |

### Asset Collection Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `rl2:member` | AssetCollection | Asset | Static member |
| `rl2:dynamicQuery` | AssetCollection | xsd:string | Query for dynamic membership |

---

## 13. Named Individuals

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
| `rl2:Pending` | ObligationState | Not yet activated |
| `rl2:Active` | ObligationState | Must be fulfilled |
| `rl2:Fulfilled` | ObligationState | Successfully completed |
| `rl2:Violated` | ObligationState | Failed to fulfill |

### Promise States

| Individual | Type | Description |
|------------|------|-------------|
| `rl2:PromisePending` | PromiseState | Awaiting fulfillment |
| `rl2:PromiseFulfilled` | PromiseState | Successfully kept |
| `rl2:PromiseViolated` | PromiseState | Broken |

---

## 14. SHACL Validation Summary

The following SHACL shapes validate RL2 policies. See **rl2-shacl.ttl** for complete definitions.

### Policy Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:PolicyShape` | rl2:Policy | At least one clause; optional grantor, grantee, condition, generation |
| `rl2:AgreementShape` | rl2:Agreement | Requires grantor and grantee |

### Norm Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:PrivilegeShape` | rl2:Privilege | Requires subject, action, object |
| `rl2:DutyShape` | rl2:Duty | Requires subject, action, object |
| `rl2:DutyStateShape` | rl2:Duty | Valid obligationState values |
| `rl2:ProhibitionShape` | rl2:Prohibition | Requires subject, prohibitedAction, object |
| `rl2:ClaimShape` | rl2:Claim | Requires claimHolder, claimAgainst |
| `rl2:PowerShape` | rl2:Power | Requires subject, affectsNorm |
| `rl2:LiabilityShape` | rl2:Liability | Requires subject, exposedTo |
| `rl2:ImmunityShape` | rl2:Immunity | Requires subject, immuneFrom |

### Promise Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:PromiseShape` | rl2:Promise | Requires promisor, promisee, promiseContent |
| `rl2:PromiseStateShape` | rl2:Promise | Valid promiseState values |

### Condition Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:AtomicConstraintShape` | rl2:AtomicConstraint | Requires leftOperand, ComparisonOperator, rightOperand or rightOperandRef |
| `rl2:LogicalConstraintShape` | rl2:LogicalConstraint | Requires LogicalOperator, at least one operand |
| `rl2:TemporalConstraintShape` | rl2:TemporalConstraint | Requires interval |
| `rl2:ContextualConstraintShape` | rl2:ContextualConstraint | Requires contextPath |
| `rl2:DynamicOperandReferenceShape` | rl2:DynamicOperandReference | Requires dynamicOperand |
| `rl2:EventConstraintShape` | rl2:EventConstraint | Requires expectsEvent |

### Temporal Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:EffectiveIntervalShape` | rl2:EffectiveInterval | start ≤ end when both present |

### Operational Shapes

| Shape | Target | Validates |
|-------|--------|-----------|
| `rl2:EventShape` | rl2:Event | At most one operationalAgent |
| `rl2:StateTransitionShape` | rl2:StateTransition | Requires triggeredBy, fromState, toState |
| `rl2:AssetCollectionShape` | rl2:AssetCollection | Members are Assets; at most one dynamicQuery |

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
- **Temporal extensions**: Allen relations, recurrence, etc.

---

## References

For complete bibliography and glossary, see **RL2_References.md**.

---

*This vocabulary reference covers RL2 version 0.2. The normative definitions are in rl2.ttl and rl2-shacl.ttl.*
