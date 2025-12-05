---
title: "RL2 Primer"
subtitle: "A Practical Introduction to Rights Language 2"
version: "0.4"
status: "Draft"
date: 2025-01-05
audience: "Students, practitioners, and implementers new to RL2"
prerequisites: "Basic familiarity with RDF and policy concepts"
---

## About This Document

This primer provides a practical introduction to reading, understanding, and writing RL2 policies. Concepts are introduced progressively, with examples at each step. Upon completion, readers will be able to:

- Understand the problems RL2 addresses
- Read RL2 policies and trace their evaluation
- Write policies for common scenarios
- Navigate reference documentation for detailed specifications

For formal definitions and complete class/property specifications, see **RL2_Vocabulary.md**.

---

## Table of Contents

1. [Motivation](#1-motivation)
2. [Architecture Overview](#2-architecture-overview)
3. [Agents and Assets](#3-agents-and-assets)
4. [Privileges](#4-privileges)
5. [Obligations: Duties and Prohibitions](#5-obligations-duties-and-prohibitions)
6. [Hohfeldian Relations: Claims, Powers, and Immunities](#6-hohfeldian-relations-claims-powers-and-immunities)
7. [Promises: Voluntary Commitments](#7-promises-voluntary-commitments)
8. [Conditions](#8-conditions)
9. [Policy Containers](#9-policy-containers)
10. [Operational Semantics](#10-operational-semantics)
11. [Complete Example](#11-complete-example)
12. [Further Reading](#12-further-reading)

---

## 1. Motivation

### The Problem

Consider a policy statement:

> "Researchers may use the dataset for academic purposes. They must delete it within 30 days of access."

Implementation of this statement raises several questions:

- When does the 30-day period begin? At download, first access, or approval?
- What constitutes the operational meaning of "must"? What are the consequences of non-compliance?
- How is deletion verified?
- If multiple downloads occur, does each initiate a new 30-day period?

Existing policy languages such as ODRL enable expression of these rules but leave interpretation to implementers. Different systems may interpret identical policies differently.

### The Solution

RL2 provides **precise operational semantics**. Every construct has a defined meaning independent of interpretation:

```
                     ODRL Policy
                          |
                          v
                   +-------------+
                   |  Compiler   |  (resolves ambiguity, supplies defaults)
                   +-------------+
                          |
                          v
                     RL2 Policy
                          |
                          v
                   +-------------+
                   |  Evaluator  |  (deterministic evaluation)
                   +-------------+
                          |
                          v
                 Permit / Deny / Obligations
```

An RL2 policy admits exactly one interpretation. The evaluator produces consistent results across implementations.

### RL2 Extensions to ODRL

RL2 is a semantic superset of ODRL—it can express everything ODRL can, though some constructs require transformation during compilation (e.g., `odrl:inheritFrom` requires flattening). The following table summarizes the extensions:

| ODRL Limitation | RL2 Extension |
|-----------------|---------------|
| Implicit temporal semantics | Explicit intervals and deadlines |
| Undefined obligation lifecycle | State machine: Pending → Active → Fulfilled/Violated |
| Permission-focused model | Full Hohfeldian framework (Claims, Powers, Immunities) |
| No voluntary commitment model | Promise Theory integration |
| Ambiguous evaluation | Formal operational semantics |

---

## 2. Architecture Overview

### Information Model

```
+------------------------------------------------------------------+
|                           POLICY                                  |
|  (Set, Offer, Agreement, Privacy, Assertion)                     |
|                                                                   |
|   grantor -----> Agent                                           |
|   grantee -----> Agent                                           |
|   condition --> Condition (optional: applicability constraint)   |
|                                                                   |
|   clauses:                                                        |
|   +----------------------------------------------------------+   |
|   |  NORM                                                     |   |
|   |  (Privilege, Duty, Prohibition, Claim, Power, ...)       |   |
|   |                                                           |   |
|   |   subject ------> Agent (bearer of the norm)             |   |
|   |   action -------> Action (governed action)               |   |
|   |   object -------> Asset (target resource)                |   |
|   |   condition ----> Condition (applicability constraint)   |   |
|   +----------------------------------------------------------+   |
+------------------------------------------------------------------+
```

A **Policy** serves as a container for **Norms**. Each norm associates an **Agent** with an **Action** on an **Asset**, optionally subject to a **Condition**.

### Conceptual Layers

RL2 is organized into eight conceptual layers:

```
+-------------------------------------------------------------------+
| 8. Policy Generation Layer    | Version control: policies in      |
|                               | force at specific times           |
+-------------------------------+-----------------------------------+
| 7. Policy Container Layer     | Groups norms into policies        |
|                               | (Set, Offer, Agreement, etc.)     |
+-------------------------------+-----------------------------------+
| 6. Temporal/Context Layer     | Time windows, environment checks  |
+-------------------------------+-----------------------------------+
| 5. Operational Layer          | Events, state transitions,        |
|                               | obligation lifecycle              |
+-------------------------------+-----------------------------------+
| 4. Action/Asset/Condition     | Governed resources and applicable |
|    Layer                      | constraints                       |
+-------------------------------+-----------------------------------+
| 3. Role Layer                 | Participation roles               |
|                               | (subject, grantor, approver...)   |
+-------------------------------+-----------------------------------+
| 2. Promise Theory Layer       | Voluntary bilateral commitments   |
+-------------------------------+-----------------------------------+
| 1. Normative Layer            | Fundamental norm types            |
|                               | (Privilege, Duty, Claim, Power..) |
+-------------------------------+-----------------------------------+
```

The following sections address these layers from the bottom up, beginning with foundational normative concepts.

---

## 3. Agents and Assets

Every policy involves parties performing actions on resources. RL2 terms these **Agents** and **Assets**.

### Agents

An Agent is any party that can participate in a policy:

- Persons (researchers, employees, customers)
- Organizations (companies, departments, committees)
- Systems (services, applications, automated processes)

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix ex:  <https://example.org/> .

ex:Alice a rl2:Agent .
ex:ResearchTeam a rl2:Agent .
ex:DataPlatform a rl2:Agent .
```

RL2 does not prescribe internal agent structure; this is implementation-defined. The relevant property is that agents can serve as norm subjects and policy parties.

### Assets

An Asset is any resource governed by a policy:

- Data (datasets, files, records)
- Content (documents, images, videos)
- Services (APIs, computational resources)
- Abstract resources (quotas, permissions)

```turtle
ex:CustomerDataset a rl2:Asset .
ex:ResearchReport a rl2:Asset .
ex:AnalyticsAPI a rl2:Asset .
```

### Asset Collections

Groups of assets may be governed together via **AssetCollection**:

```turtle
ex:SensitiveData a rl2:AssetCollection ;
    rl2:member ex:CustomerDataset ;
    rl2:member ex:EmployeeRecords ;
    rl2:member ex:FinancialData .
```

Collections may also be defined dynamically via query:

```turtle
ex:AllClassifiedDocuments a rl2:AssetCollection ;
    rl2:dynamicQuery "SELECT ?doc WHERE { ?doc ex:classification 'SECRET' }" .
```

---

## 4. Privileges

A **Privilege** is the simplest norm type, expressing permission.

### Definition

A Privilege declares that the subject has no duty to refrain from the specified action. A privilege does not create obligations on other parties; it establishes that the holder is permitted to act.

### Structure

```turtle
ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;      # Bearer of the privilege
    rl2:action ex:use ;              # Permitted action
    rl2:object ex:Dataset .          # Target resource
```

This states: "The Researcher has a privilege to use the Dataset."

### Example with Condition

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix ex:  <https://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Action definition (typically provided by profiles)
ex:use a rl2:Action .

# Agents and asset
ex:Alice a rl2:Agent .
ex:ResearchDataset a rl2:Asset .

# The privilege
ex:aliceUsePrivilege a rl2:Privilege ;
    rl2:subject ex:Alice ;
    rl2:action ex:use ;
    rl2:object ex:ResearchDataset ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:start "2025-01-01T00:00:00Z"^^xsd:dateTime ;
            rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime
        ]
    ] .
```

This states: "Alice may use the Research Dataset during 2025."

### Closed-World Semantics

In the absence of an applicable privilege, access is not permitted. RL2 follows a closed-world assumption: authorization requires explicit grant.

---

## 5. Obligations: Duties and Prohibitions

Privileges specify what agents *may* do. Duties and prohibitions specify what agents *must* and *must not* do.

### Duties

A **Duty** is an obligation to perform an action. Unlike a privilege (which merely permits), a duty creates a requirement subject to fulfillment or violation.

```turtle
ex:reportDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:submitReport ;
    rl2:object ex:Dataset .
```

This states: "The Researcher has a duty to submit a report about the Dataset."

### Duty Lifecycle

A key distinction of RL2 is that duties have a **lifecycle**:

```
     +----------+
     |  Pending |  (duty exists but not yet activated)
     +----+-----+
          |
          | activation condition becomes true
          v
     +----------+
     |  Active  |  (duty must be fulfilled)
     +----+-----+
          |
     +----+----+
     |         |
     v         v
+---------+ +---------+
|Fulfilled| |Violated |
+---------+ +---------+
  (done)     (deadline passed without fulfillment)
```

Section 10 provides detailed treatment of this lifecycle.

### Duty with Deadline

```turtle
ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:delete ;
    rl2:object ex:Dataset ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:end "2025-03-15T23:59:59Z"^^xsd:dateTime
        ]
    ] .
```

This duty must be fulfilled by March 15, 2025. If the action is not performed by that time, the duty transitions to Violated.

### Prohibitions

A **Prohibition** specifies that an action must not be performed:

```turtle
ex:distributionBan a rl2:Prohibition ;
    rl2:subject ex:Researcher ;
    rl2:prohibitedAction ex:distribute ;
    rl2:object ex:Dataset .
```

This states: "The Researcher must not distribute the Dataset."

Prohibitions use `rl2:prohibitedAction` rather than `rl2:action` to make intent explicit in the RDF structure and enable clear queries.

### Prohibition as Explicit Class

While a prohibition is logically equivalent to a duty to refrain, RL2 models Prohibition explicitly for the following reasons:

1. Policy authors naturally express "must not do X" rather than "duty to not do X"
2. The property `rl2:prohibitedAction` provides clear semantics
3. Alignment with ODRL and similar languages facilitates translation

---

## 6. Hohfeldian Relations: Claims, Powers, and Immunities

RL2 models the full **Hohfeldian framework**—eight fundamental legal concepts forming the basis of normative relations.

### Background

Wesley Hohfeld, an early 20th-century legal scholar, observed that legal relations occur in correlative pairs. When one party holds a certain position, another party necessarily holds a **correlative** position:

```
+-------------+     correlative     +-------------+
|  Privilege  | <-----------------> |  No-Claim   |
+-------------+                     +-------------+
If Alice has a privilege to X,      Bob has no claim that Alice not X
(she may do X)                      (he cannot demand she refrain)


+-------------+     correlative     +-------------+
|    Duty     | <-----------------> |    Claim    |
+-------------+                     +-------------+
If Alice has a duty to X,           Bob has a claim that Alice X
(she must do X)                     (he can demand performance)


+-------------+     correlative     +-------------+
|    Power    | <-----------------> |  Liability  |
+-------------+                     +-------------+
If Alice has power to change        Bob is liable to have his
Bob's position,                     position changed


+-------------+     correlative     +-------------+
|  Immunity   | <-----------------> | Disability  |
+-------------+                     +-------------+
If Alice is immune from Bob's       Bob is disabled from exercising
power,                              that power over Alice
```

### RL2 Norm Types

RL2 models these Hohfeldian concepts as norm types:

| RL2 Class | Semantics |
|-----------|-----------|
| `rl2:Privilege` | Permission to perform an action |
| `rl2:Duty` | Obligation to perform an action |
| `rl2:Prohibition` | Obligation to refrain from an action (RL2 addition) |
| `rl2:Claim` | Right to demand performance from another |
| `rl2:Power` | Ability to change another's normative position |
| `rl2:Liability` | Exposure to position change by another |
| `rl2:Immunity` | Protection from position change by another's power |

Note: **No-Claim** and **Disability** are not modeled as classes. They represent *absences* of positions, inferred rather than explicitly stated.

### Claims

When Alice has a duty to Bob, Bob has a claim against Alice:

```turtle
ex:aliceDuty a rl2:Duty ;
    rl2:subject ex:Alice ;
    rl2:action ex:deliverReport ;
    rl2:object ex:Report ;
    rl2:counterparty ex:Bob .

ex:bobClaim a rl2:Claim ;
    rl2:claimHolder ex:Bob ;
    rl2:claimAgainst ex:Alice ;
    rl2:correlativeTo ex:aliceDuty .
```

Both representations serve distinct purposes:
- The **Duty** specifies what Alice must do
- The **Claim** specifies what Bob can demand

### Powers

A **Power** is the ability to change another's normative position:

```turtle
ex:managerPower a rl2:Power ;
    rl2:subject ex:Manager ;
    rl2:affectsNorm ex:accessPrivilegeTemplate .

ex:employeeLiability a rl2:Liability ;
    rl2:subject ex:Employee ;
    rl2:exposedTo ex:managerPower .
```

When the manager exercises this power, new privileges may be created for employees.

### Immunities

An **Immunity** protects against position changes:

```turtle
ex:tenureImmunity a rl2:Immunity ;
    rl2:subject ex:Professor ;
    rl2:immuneFrom ex:firingPower .
```

This states that the Professor's employment cannot be terminated via the standard firing power.

### Application Scope

For simple policies, Privilege, Duty, and Prohibition may suffice. The full Hohfeldian framework is applicable when modeling:

- **Contractual relationships** with correlative rights and duties
- **Authorization hierarchies** where agents can grant or revoke access
- **Protected positions** with immunity from modification

---

## 7. Promises: Voluntary Commitments

RL2 incorporates **Promise Theory** to model voluntary commitments between agents. Promises differ fundamentally from norms.

### Promises vs. Duties

| Aspect | Duty | Promise |
|--------|------|---------|
| **Source** | Imposed by policy | Voluntary commitment |
| **Nature** | "You must" | "I will" |
| **Parties** | May have abstract counterparty | Requires specific promisee |
| **Creation** | Policy author defines | Promisor actively commits |

### Significance

Consider two statements:

1. *"Researchers must delete data within 30 days"* — This is a **Duty**, imposed by policy regardless of agreement.

2. *"Alice commits to Bob to handle data responsibly"* — This is a **Promise**, a voluntary commitment by Alice to Bob.

The distinction is relevant for:
- **Provenance**: Why does this obligation exist?
- **Enforcement**: Who can demand performance?
- **Trust**: Promises indicate voluntary cooperation

### Structure

```turtle
ex:stewardshipPromise a rl2:Promise ;
    rl2:promisor ex:Researcher ;       # Maker of the promise
    rl2:promisee ex:DataOwner ;        # Recipient
    rl2:promiseContent ex:DataStewardshipDuty ;  # Content of promise
    rl2:promiseState rl2:PromisePending .        # Current state
```

### Promise States

Promises have a lifecycle:

```
+----------------+
| PromisePending |  (commitment made, not yet fulfilled)
+-------+--------+
        |
   +----+----+
   |         |
   v         v
+----------------+  +----------------+
|PromiseFulfilled|  |PromiseViolated |
+----------------+  +----------------+
```

### Promises as Norm Sources

When Alice promises Bob to delete data, this may generate:
- A **Duty** on Alice (to delete)
- A **Claim** for Bob (to have deletion performed)

The promise is the *source*; the norms are the *effects*. This enables tracking of obligation provenance.

### Promises as Conditions

Policies may require promises as preconditions:

```turtle
ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:SensitiveData ;
    rl2:condition [
        a rl2:Condition ;
        rl2:requires ex:stewardshipPromise
    ] .
```

This states: "The researcher may access sensitive data only if the stewardship promise has been made."

---

## 8. Conditions

Most norms do not apply unconditionally. Constraints—time windows, purpose restrictions, approval requirements—are modeled as **Conditions**.

### Condition Hierarchy

```
                    Condition
                        |
     +------------------+------------------+
     |          |       |        |         |
  Atomic    Logical  Temporal Context   Event
Constraint Constraint Constraint Constraint Constraint
                                           |
                                      Dynamic
                                    OperandRef
```

### Atomic Constraints

The simplest condition compares a property to a value:

```turtle
ex:purposeConstraint a rl2:AtomicConstraint ;
    rl2:leftOperand ex:purpose ;    # Property to evaluate
    rl2:constraintOperator rl2:eq ; # Comparison operator
    rl2:rightOperand "research" .   # Required value
```

This requires: "The purpose must equal 'research'."

**Comparison operators**:

| Operator | Semantics |
|----------|-----------|
| `rl2:eq` | Equal to |
| `rl2:neq` | Not equal to |
| `rl2:lt` | Less than |
| `rl2:lte` | Less than or equal |
| `rl2:gt` | Greater than |
| `rl2:gte` | Greater than or equal |
| `rl2:isA` | Type membership |
| `rl2:isAnyOf` | Set membership |
| `rl2:isAllOf` | Satisfies all |
| `rl2:isNoneOf` | Set exclusion |

### Logical Constraints

Conditions may be combined with logical operators:

```turtle
ex:combinedConstraint a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:and ;
    rl2:operand ex:purposeConstraint ;
    rl2:operand ex:locationConstraint .
```

**Logical operators**:

| Operator | Semantics |
|----------|-----------|
| `rl2:and` | All operands must be true |
| `rl2:or` | At least one operand must be true |
| `rl2:xone` | Exactly one operand must be true |
| `rl2:not` | Operand must be false |

### Temporal Constraints

Temporal constraints use **EffectiveInterval** to specify validity periods:

```turtle
ex:validityPeriod a rl2:TemporalConstraint ;
    rl2:interval [
        a rl2:EffectiveInterval ;
        rl2:start "2025-01-01T00:00:00Z"^^xsd:dateTime ;
        rl2:end "2025-06-30T23:59:59Z"^^xsd:dateTime
    ] .
```

**Open intervals**: Both start and end are optional:
- Start only: "from January 1 onwards" (open-ended)
- End only: "until June 30" (deadline)
- Both: "from January 1 to June 30" (closed interval)

### Contextual Constraints

Contextual constraints evaluate the execution environment using `AtomicConstraint` with an inline `LeftOperand`:

```turtle
ex:locationCheck a rl2:AtomicConstraint ;
    rl2:leftOperand [ a rl2:LeftOperand ;
                      rl2:resolutionPath "request.location.country" ] ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperand "DE" .
```

This requires that the request originate from Germany. The inline `LeftOperand` with `resolutionPath` accesses the context path at evaluation time.

### Event Constraints

Event constraints require prior occurrence of specified events:

```turtle
ex:approvalRequired a rl2:EventConstraint ;
    rl2:expectsEvent [
        a rl2:Event ;
        rl2:approver ex:DataOwner
    ] .
```

This requires: "An approval event from the DataOwner must have occurred."

### Dynamic Operand References

Values not known until evaluation time may be specified dynamically:

```turtle
ex:dynamicDeadline a rl2:DynamicOperandReference ;
    rl2:dynamicOperand "event.AccessEvent.timestamp + P30D" .
```

This evaluates to "30 days after the access event occurred."

### Composite Conditions

Conditions may be composed. The following privilege requires:
- Purpose is research
- Time is within 2025
- Approval has been granted

```turtle
ex:complexPrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand ex:purpose ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand "research"
        ] ;
        rl2:operand [
            a rl2:TemporalConstraint ;
            rl2:interval [
                a rl2:EffectiveInterval ;
                rl2:start "2025-01-01T00:00:00Z"^^xsd:dateTime ;
                rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime
            ]
        ] ;
        rl2:operand [
            a rl2:EventConstraint ;
            rl2:expectsEvent [
                a rl2:Event ;
                rl2:approver ex:DataOwner
            ]
        ]
    ] .
```

### Duty State as Precondition

A common pattern is conditioning a privilege on prior duty fulfillment. RL2 supports this via two special left operands that query the state memory (Σ):

| Left Operand | Queries | Returns |
|--------------|---------|---------|
| `rl2:obligationStateOperand` | `Σ.ObligationState(targetNorm)` | Pending, Active, Fulfilled, Violated |
| `rl2:dutyPerformerOperand` | `Σ.DutyPerformer(targetNorm)` | Agent who fulfilled, or ⊥ |

These operands require `rl2:targetNorm` to specify which norm to query.

**Deontic Philosophy Connection:**

| German Term | English | RL2 Pattern |
|-------------|---------|-------------|
| *Tun-sollen* | Ought-to-do (personal) | `obligationState = Fulfilled` AND `dutyPerformer = currentAgent` |
| *Sein-sollen* | Ought-to-be (impersonal) | `obligationState = Fulfilled` only |

**Pattern 1: Sein-sollen (Anyone May Fulfill)**

"Access is permitted if the duty is fulfilled by anyone."

```turtle
ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Resource ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:paymentDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand rl2:Fulfilled
    ] .
```

**Pattern 2: Tun-sollen (Same Agent Must Fulfill)**

"Access is permitted only if I personally fulfilled the duty."

```turtle
ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Resource ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check: Is the duty fulfilled?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:obligationStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand rl2:Fulfilled
        ] ;
        rl2:operand [
            # Check: Did I fulfill it?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:dutyPerformerOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

**Pattern 3: Separation of Duty (Different Agent Must Fulfill)**

"Access is permitted only if someone OTHER than me fulfilled the prerequisite."

This pattern implements the Two-Man Rule for sensitive operations:

```turtle
ex:approvalPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:approveTransfer ;
    rl2:object ex:WireTransfer ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:preparationDuty ;
            rl2:leftOperand rl2:obligationStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand rl2:Fulfilled
        ] ;
        rl2:operand [
            # NOT EQUAL: A different agent must have fulfilled
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:preparationDuty ;
            rl2:leftOperand rl2:dutyPerformerOperand ;
            rl2:constraintOperator rl2:neq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

For more patterns, see **usecases/README.md** which documents 10 use cases demonstrating duty state preconditions.

### Profile-Declared Operands

In the examples above, `ex:purpose` is used as a left operand. Where does it come from?

RL2 Core defines the **mechanism** for conditions (operators, constraint types) but does not define domain-specific operands like `purpose`, `location`, or `dataOwner`. These are provided by **profiles**—domain-specific extensions that declare operands with explicit resolution semantics.

**Architectural Principle**: All runtime and contextual data access goes through declared `rl2:LeftOperand` instances with explicit resolution paths.

**Example Profile Declaration**:

```turtle
@prefix privacy: <https://rl2.example/profile/privacy#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

privacy:purposeOperand a rl2:LeftOperand ;
    rdfs:label "Purpose" ;
    rl2:resolutionPath "context.purpose" ;
    rdfs:range privacy:Purpose .

privacy:dataOwnerOperand a rl2:LeftOperand ;
    rdfs:label "Data Owner" ;
    rl2:resolutionPath "asset.dataOwner" ;
    rdfs:range rl2:Agent .
```

**Usage in Policy**:

```turtle
ex:gdprPrivilege a rl2:Privilege ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand privacy:dataOwnerOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .
```

**Resolution Path Roots**:

| Root | Meaning | Example |
|------|---------|---------|
| `agent` | Requesting agent | `agent.department` |
| `asset` | Requested asset | `asset.classification` |
| `state` | System state (Σ) | `state.Events.approval.operationalAgent` |
| `context` | Request context | `context.purpose` |
| `request` | Request metadata | `request.requestTime` |

This architecture ensures:
- **No ad-hoc vocabulary** — Profiles own domain operands
- **Formal grounding** — All access maps to `resolve`/`deref` in the semantics
- **Type safety** — Operands declare expected ranges
- **Validation** — SHACL verifies operand usage

See **profiles/** for example profiles and **RL2_Semantics.md** for the formal resolution semantics.

---

## 9. Policy Containers

Individual norms are bundled into coherent packages via **Policy** containers.

### Structure

```turtle
ex:dataUsePolicy a rl2:Policy ;
    rl2:grantor ex:DataOwner ;          # Issuing party
    rl2:grantee ex:Researcher ;         # Receiving party
    rl2:clause ex:usePrivilege ;        # Contained norms
    rl2:clause ex:reportDuty ;
    rl2:clause ex:distributionBan .
```

A policy bundles norms (via `rl2:clause`) and identifies the parties.

### Policy Types

RL2 defines five policy types:

| Type | Application | Characteristics |
|------|-------------|-----------------|
| **Set** | Public terms, general rules | No specific counterparty |
| **Offer** | Proposed terms awaiting acceptance | No obligations until accepted |
| **Agreement** | Binding contract between parties | Both parties identified and consenting |
| **Privacy** | Data protection policies | Duties on controllers, rights for subjects |
| **Assertion** | Claims about status | Declares facts; does not create norms |

### Set

A Set is a policy without identified counterparties:

```turtle
ex:termsOfService a rl2:Set ;
    rl2:clause ex:acceptableUsePrivilege ;
    rl2:clause ex:noAbuseDuty .
```

No acceptance is required; these constitute standing rules.

### Offer

An Offer proposes terms that become binding upon acceptance:

```turtle
ex:licenseOffer a rl2:Offer ;
    rl2:grantor ex:DataProvider ;
    rl2:clause ex:usePrivilege ;
    rl2:clause ex:attributionDuty .
```

Until acceptance, no obligations are created.

### Agreement

An Agreement binds specific, consenting parties:

```turtle
ex:dataContract a rl2:Agreement ;
    rl2:grantor ex:DataProvider ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:accessPrivilege ;
    rl2:clause ex:deletionDuty ;
    rl2:clause ex:confidentialityDuty .
```

Both parties are identified. SHACL validation requires Agreements to have both `grantor` and `grantee`.

### Policy-Level Conditions

Policies may have applicability conditions:

```turtle
ex:emergencyPolicy a rl2:Set ;
    rl2:condition [
        a rl2:EventConstraint ;
        rl2:expectsEvent [ a ex:EmergencyDeclaration ]
    ] ;
    rl2:clause ex:emergencyAccessPrivilege .
```

This policy applies only when an emergency has been declared.

### Policy Generations

Policies evolve over time. RL2 tracks this via **policy generations**—immutable snapshots of all policies in force at a given time.

```turtle
ex:dataPolicy a rl2:Agreement ;
    rl2:policyGeneration <https://example.org/generations/2025-Q1> ;
    rl2:clause ex:accessPrivilege .
```

Key concepts:
- A **generation** represents the complete policy universe at a point in time
- Events can activate/deactivate policies *within* a generation
- Content changes (additions, amendments) create a *new* generation
- Cases are evaluated under the generation in effect at creation

This approach enables reproducible evaluation and audit trails.

---

## 10. Operational Semantics

This section addresses what distinguishes RL2 from static policy languages: **operational semantics**. Policies are not merely declarations—they are state machines that evolve over time.

### Events

An **Event** is an observable occurrence that can trigger state changes:

```turtle
ex:accessEvent a rl2:Event ;
    rl2:operationalAgent ex:Alice ;
    rl2:participant ex:Alice .
```

Events include:
- Actions performed (data accessed)
- Approvals granted (manager approved request)
- Time advancement (deadline passed)
- External signals (system notifications)

### Duty State Machine

The duty lifecycle in detail:

```
                          +----------+
                          | Pending  |
                          +----+-----+
                               |
         condition becomes true|
                               v
                          +----------+
            +------------>|  Active  |<-------------+
            |             +----+-----+              |
            |                  |                    |
            |         +--------+--------+          |
            |         |                 |          |
   time passes,       v                 v          |
   still active  +---------+      +---------+      |
                 |Fulfilled|      |Violated |      |
                 +---------+      +---------+      |
                 action done      deadline passed
                                  without action
```

**Pending**: The duty exists but its activation condition is not satisfied.
**Active**: The condition is satisfied; the duty must be fulfilled.
**Fulfilled**: The required action was performed.
**Violated**: The deadline passed without fulfillment.

### Lifecycle Trace

The following traces a deletion duty through its lifecycle:

**1. Initial State (Pending)**

```turtle
ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:delete ;
    rl2:object ex:Dataset ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:end "2025-03-15T23:59:59Z"^^xsd:dateTime
        ]
    ] .
```

The duty exists in Pending state, awaiting activation.

**2. Activation (Pending → Active)**

An event occurs: the researcher accesses the dataset on January 15. The system evaluates the duty's condition. If the condition is tied to access:

```turtle
rl2:condition [
    a rl2:EventConstraint ;
    rl2:expectsEvent [ a ex:AccessEvent ]
] .
```

With access having occurred, the condition is satisfied. The duty transitions to Active.

```turtle
ex:deletionDuty rl2:obligationState rl2:Active .
```

**3. Monitoring**

On February 20, the system evaluates:
- Is the duty Active? Yes.
- Has the delete action been performed? No.
- Has the deadline passed? No (deadline is March 15).

No transition occurs. The duty remains Active.

**4a. Fulfillment (Active → Fulfilled)**

On March 1, the researcher performs the deletion. The system evaluates:
- Is the duty Active? Yes.
- Has the delete action been performed? Yes.

The duty transitions to Fulfilled.

```turtle
ex:deletionDuty rl2:obligationState rl2:Fulfilled .
```

**4b. Violation (Active → Violated)**

Alternatively, if March 16 arrives without deletion:
- Is the duty Active? Yes.
- Has the delete action been performed? No.
- Has the deadline passed? Yes.

The duty transitions to Violated.

```turtle
ex:deletionDuty rl2:obligationState rl2:Violated .
```

### State Transitions

RL2 formally models transitions:

```turtle
ex:activationTransition a rl2:StateTransition ;
    rl2:triggeredBy ex:accessEvent ;
    rl2:fromState rl2:Pending ;
    rl2:toState rl2:Active .
```

This creates an audit trail documenting how and why states changed.

### Significance

Without operational semantics, "must delete within 30 days" is underspecified:
- When does the period begin?
- What are the consequences of non-compliance?
- How is compliance tracked?

With operational semantics:
- The duty starts Pending and activates on a specified event
- Violation is a defined state with specified consequences
- Every transition is traceable

---

## 11. Complete Example

The following constructs a complete policy applying the concepts introduced.

### Scenario

A research institution shares datasets with external researchers under these rules:

1. Researchers may use the dataset for academic purposes during 2025
2. Researchers must submit a report by June 30
3. Researchers must delete the data by December 31
4. Researchers may not distribute the data to third parties
5. Access requires approval from the Data Governance Committee

### Complete Policy

```turtle
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix ex:   <https://example.org/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# ============================================
# Domain Definitions (typically from profile)
# ============================================

ex:use a rl2:Action .
ex:submitReport a rl2:Action .
ex:delete a rl2:Action .
ex:distribute a rl2:Action .

ex:purpose a rl2:LeftOperand .

# ============================================
# Agents and Assets
# ============================================

ex:ResearchInstitution a rl2:Agent .
ex:DataGovernanceCommittee a rl2:Agent .
ex:ExternalResearcher a rl2:Agent .
ex:ResearchDataset a rl2:Asset .

# ============================================
# The Policy
# ============================================

ex:dataAccessAgreement a rl2:Agreement ;
    rl2:grantor ex:ResearchInstitution ;
    rl2:grantee ex:ExternalResearcher ;
    rl2:policyGeneration <https://example.org/generations/2025-v1> ;
    rl2:clause ex:usePrivilege ;
    rl2:clause ex:reportDuty ;
    rl2:clause ex:deletionDuty ;
    rl2:clause ex:distributionProhibition .

# ============================================
# Clause 1: Use Privilege
# Researcher may use the dataset for academic purposes during 2025,
# subject to committee approval
# ============================================

ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:ExternalResearcher ;
    rl2:action ex:use ;
    rl2:object ex:ResearchDataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Purpose must be academic
            a rl2:AtomicConstraint ;
            rl2:leftOperand ex:purpose ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand "academic"
        ] ;
        rl2:operand [
            # Valid during 2025
            a rl2:TemporalConstraint ;
            rl2:interval [
                a rl2:EffectiveInterval ;
                rl2:start "2025-01-01T00:00:00Z"^^xsd:dateTime ;
                rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime
            ]
        ] ;
        rl2:operand [
            # Requires committee approval
            a rl2:EventConstraint ;
            rl2:expectsEvent [
                a rl2:Event ;
                rl2:approver ex:DataGovernanceCommittee
            ]
        ]
    ] .

# ============================================
# Clause 2: Report Duty
# Researcher must submit report by June 30
# ============================================

ex:reportDuty a rl2:Duty ;
    rl2:subject ex:ExternalResearcher ;
    rl2:action ex:submitReport ;
    rl2:object ex:ResearchDataset ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:end "2025-06-30T23:59:59Z"^^xsd:dateTime
        ]
    ] .

# ============================================
# Clause 3: Deletion Duty
# Researcher must delete data by December 31
# ============================================

ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:ExternalResearcher ;
    rl2:action ex:delete ;
    rl2:object ex:ResearchDataset ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime
        ]
    ] .

# ============================================
# Clause 4: Distribution Prohibition
# Researcher may not distribute to third parties
# ============================================

ex:distributionProhibition a rl2:Prohibition ;
    rl2:subject ex:ExternalResearcher ;
    rl2:prohibitedAction ex:distribute ;
    rl2:object ex:ResearchDataset .
```

### Evaluation Trace

The following traces evaluation when the researcher requests access:

**Request**: External Researcher requests to use Research Dataset for academic purposes on February 15, 2025.

**Step 1: Identify applicable policies**

The system examines all policies and their conditions. `ex:dataAccessAgreement` has no policy-level condition; it is applicable.

**Step 2: Identify matching norms**

Within the policy, identify norms matching the request (subject=ExternalResearcher, action=use, object=ResearchDataset):
- `ex:usePrivilege` matches ✓

**Step 3: Evaluate conditions**

For `ex:usePrivilege`, evaluate the conjunction of three conditions:

1. Purpose = "academic"? Check request context. **Yes** ✓
2. Time within 2025? February 15 is in [Jan 1, Dec 31]. **Yes** ✓
3. Committee approval exists? Check event log for approval event. **Yes** ✓

All conditions are satisfied.

**Step 4: Check for prohibitions**

Is there an active prohibition on use? `ex:distributionProhibition` applies to `distribute`, not `use`. **No conflict**.

**Step 5: Check for active duties**

Are there unfulfilled duties?
- `ex:reportDuty` is Pending (deadline June 30)
- `ex:deletionDuty` is Pending (deadline Dec 31)

No duties are violated.

**Step 6: Decision**

Result: **PermitWithObligations**

The researcher may proceed. Pending duties are tracked.

### Alternative Outcomes

If committee approval had not been granted:
- Condition 3 fails
- The privilege is Inactive
- Result: **NotApplicable** (no matching active privilege)

If the researcher attempted to distribute:
- `ex:distributionProhibition` matches
- Its condition (none) is trivially satisfied
- Result: **Deny** (active prohibition)

---

## 12. Further Reading

### Reference Documentation

- **RL2_Vocabulary.md** — Complete class and property reference
- **rl2.ttl** — Normative OWL ontology
- **rl2-shacl.ttl** — SHACL validation shapes
- **profiles/** — Domain-specific profiles with declared operands

### Formal Semantics

- **RL2_Semantics.md** — Mathematical definitions of evaluation, state transitions, and typing rules

### Runtime Behavior

- **RL2_Protocol.md** — Interchange of evaluation requests and results between systems

### Background and Motivation

- **RL2_White_Paper.md** — Rationale, architectural overview, comparison to related systems

### Implementation

- **RL2_ResearchPlan.md** — Roadmap for formal verification and mechanization

### References and Glossary

- **RL2_References.md** — Complete bibliography and term definitions

### Quick Reference

| Objective | Construct |
|-----------|-----------|
| Permit an action | `rl2:Privilege` |
| Require an action | `rl2:Duty` |
| Forbid an action | `rl2:Prohibition` |
| Model a held right | `rl2:Claim` |
| Model authority to change rules | `rl2:Power` |
| Model voluntary commitment | `rl2:Promise` |
| Set a time window | `rl2:TemporalConstraint` with `rl2:EffectiveInterval` |
| Require approval | `rl2:EventConstraint` with `rl2:approver` |
| Combine conditions | `rl2:LogicalConstraint` with `rl2:and`/`rl2:or` |
| Bundle norms | `rl2:Policy` with `rl2:clause` |
| Create bilateral agreement | `rl2:Agreement` |
| Access contextual data | Profile-declared `rl2:LeftOperand` with `rl2:resolutionPath` |

---

## Glossary

For definitions of terms used in this document, see **RL2_References.md**.

---

*This primer covers RL2 version 0.4. For updates and errata, see the RL2 repository.*
