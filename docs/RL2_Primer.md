---
title: "RL2 Primer"
subtitle: "A Practical Introduction to Rights Language 2"
version: "0.6"
status: "Draft"
date: 2026-07-24
---

## About This Document

> **SCOPE-2 alignment in progress.** The examples remain useful, but operational state-machine,
> Case, Requirement, protocol, and prescribed-IR explanations may describe the former scope. The
> normative model is `../spec/RL2_Model.md`; use-case migrations are tracked in
> `../conformance/usecase-disposition.md`.

This primer provides a practical introduction to reading, understanding, and writing RL2 policies. Concepts are introduced progressively, with examples at each step. Upon completion, readers will be able to:

- Understand the problems RL2 addresses
- Read RL2 policies and trace their evaluation
- Write policies for common scenarios
- Navigate reference documentation for detailed specifications

For formal definitions, see `../spec/RL2_Model.md` and `../spec/RL2_Semantics.md`. The vocabulary
reference in this directory is informative and derived from the ontology.

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
10. [Evaluation Semantics](#10-evaluation-semantics)
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

RL2 aims to be a semantic superset of ODRL—the goal is to express everything ODRL can (a complete term-by-term compatibility inventory is still open work), though some constructs require transformation during compilation (e.g., `odrl:inheritFrom` requires flattening). The following table summarizes the extensions:

| ODRL Limitation | RL2 Extension |
|-----------------|---------------|
| Implicit temporal semantics | Explicit intervals and deadlines |
| Underspecified Duty fulfillment | Pure snapshot-derived status with explicit evidence and time boundaries |
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
| 5. Evaluation Layer           | Request, immutable snapshot,      |
|                               | derived status and decision       |
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

Dynamic materialization (e.g., "all assets with classification SECRET") is profile-specific. Profiles may define resolution functions or registry references to produce a collection; RL2 Core no longer embeds query strings for this.

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
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand rl2:currentDateTime ;
            rl2:constraintOperator rl2:gte ;
            rl2:rightOperand "2025-01-01T00:00:00Z"^^xsd:dateTimeStamp
        ] ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand rl2:currentDateTime ;
            rl2:constraintOperator rl2:lte ;
            rl2:rightOperand "2025-12-31T23:59:59Z"^^xsd:dateTimeStamp
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

### Duty Status

RL2 derives a Duty's status from its content and one immutable world snapshot. The result is
Pending, Active, Fulfilled, Violated, or an explicit indeterminate status with causal errors. It
is not a transition performed by the evaluator.

An **Achievement Duty** has an action and may have a postcondition that qualifies the action
evidence. A **Maintenance Duty** has an invariant instead of an action. Either form may use one
finite half-open `dutyWindow`; its structure determines the form, so no mode flag is authored.

### Duty with Deadline

```turtle
ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:delete ;
    rl2:object ex:Dataset ;
    rl2:dutyWindow [
        a rl2:DutyWindow ;
        rl2:startInclusive "2025-03-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2025-03-16T00:00:00Z"^^xsd:dateTimeStamp
    ] .
```

This Duty is Fulfilled when qualifying deletion evidence occurs before the exclusive end. At or
after the end, no qualifying evidence means Violated.

### Prerequisite and Independent Duties

A Duty attached with `rl2:prerequisiteDuty` must be Fulfilled before its Privilege can contribute
a permit. Multiple prerequisites are conjunctive. The attached Duty is not also a Policy clause:

```turtle
ex:licensePolicy a rl2:Set ;
    rl2:clause ex:viewPrivilege .

ex:viewPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:view ;
    rl2:object ex:Photo ;
    rl2:prerequisiteDuty ex:paymentDuty .

ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:User ;
    rl2:action ex:pay ;
    rl2:object ex:PhotoLicense .
```

A Duty linked directly from a Policy with `rl2:clause` is independent. Its status is returned but
does not grant, deny, or qualify an unrelated request. Concurrent and post-use scheduling belongs
to a companion protocol rather than to core evaluation.

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

RL2 models the **Hohfeldian framework**—six of Hohfeld's eight fundamental positions (Privilege, Duty, Claim, Power, Liability, Immunity), plus Prohibition. The two omitted positions—No-Right and Disability—are the "absence" correlatives and are treated as derived rather than reified as classes.

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
    rl2:subject ex:Bob ;          # right-holder
    rl2:counterparty ex:Alice ;   # duty-bearer
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
ex:firingPower a rl2:Power ;
    rl2:subject ex:Dean ;
    rl2:affectsNorm ex:employmentPrivilege .

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
ex:DataStewardshipDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:steward ;
    rl2:object ex:Dataset .

ex:stewardshipPromise a rl2:Promise ;
    rl2:promisor ex:Researcher ;       # Maker of the promise
    rl2:promisee ex:DataOwner ;        # Recipient
    rl2:promisedDuty ex:DataStewardshipDuty ;  # Suretyship: see the duty fulfilled
    rl2:promiseState rl2:Pending .              # Current state
```
Pending/Active/Fulfilled/Violated are shared state individuals; promises never use `Active`.

### Promise Status

Promise status, like Duty status, is derived anew from the supplied snapshot rather than advanced
through a stored state machine. Promises have no `Active` value:

| Aspect | Duty (4 states) | Promise (3 states) |
|--------|-----------------|-------------------|
| **Pending** | A declared window has not started | Commitment made, awaiting fulfillment |
| **Active** | Applicable and not yet fulfilled | *Not applicable* |
| **Fulfilled/Violated** | Derived from evidence, invariant, and time | Derived from promise content and evidence |

These values describe the current evaluation result; they are not required to be terminal in
stored application state. A later snapshot can yield a different Promise status.

### Promises as Norm Sources

When Alice promises Bob to delete data, this may generate:
- A **Duty** on Alice (to delete)
- A **Claim** for Bob (to have deletion performed)

The promise is the *source*; the norms are the *effects*. This enables tracking of obligation provenance.

### Promises as Conditions

Policies may require promises as preconditions:

```turtle
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix ex:   <https://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:stewardshipPromise a rl2:Promise ;
    rl2:promisor ex:Researcher ;
    rl2:promisee ex:DataOwner ;
    rl2:promisedAction ex:steward ;
    rl2:object ex:Dataset ;
    rl2:promiseState rl2:Pending .

ex:stewardshipStateOperand a rl2:LeftOperand ;
    rl2:resolutionPath "state.Promises.stewardshipPromise.state" ;
    rdfs:range rl2:PromiseState .

ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:SensitiveData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:stewardshipStateOperand ;
        rl2:constraintOperator rl2:neq ;
        rl2:rightOperandRef rl2:Violated
    ] .
```

This states: "The researcher may access sensitive data only if the stewardship promise has been made and not violated." Conditions on norm state (or Promise state, as here) are expressed as `AtomicConstraint`s over a profile-declared `LeftOperand` with a `resolutionPath` into Σ — the same mechanism used for duty-state preconditions (§ Duty State as Precondition) — not via a distinct dependency link.

---

## 8. Conditions

Most norms do not apply unconditionally. Constraints—time windows, purpose restrictions, approval requirements—are modeled as **Conditions**.

### Condition Hierarchy

```
                    Condition
                        |
          +-------------+-------------+
          |             |             |
       Atomic       Logical        Event
     Constraint   Constraint    Constraint
```

Note: Temporal conditions use `AtomicConstraint` with `rl2:currentDateTime` as the left operand (see §Temporal Constraints below).

Note: Dynamic value resolution on the left side uses `LeftOperand` with `resolutionPath`. Dynamic value resolution on the right side (e.g., comparing to the current agent) uses `RuntimeReference`.

### Atomic Constraints

The simplest condition compares a property to a value:

```turtle
ex:purpose a rl2:LeftOperand ;
    rl2:resolutionPath "context.purpose" .

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

Temporal constraints use **currentDateTime** with comparison operators to specify validity periods:

```turtle
# Closed interval: from January 1 to June 30
ex:validityPeriod a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:and ;
    rl2:operand [
        a rl2:AtomicConstraint ;
        rl2:leftOperand rl2:currentDateTime ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperand "2025-01-01T00:00:00Z"^^xsd:dateTimeStamp
    ] ;
    rl2:operand [
        a rl2:AtomicConstraint ;
        rl2:leftOperand rl2:currentDateTime ;
        rl2:constraintOperator rl2:lte ;
        rl2:rightOperand "2025-06-30T23:59:59Z"^^xsd:dateTimeStamp
    ] .

# Deadline only: until June 30
ex:deadline a rl2:AtomicConstraint ;
    rl2:leftOperand rl2:currentDateTime ;
    rl2:constraintOperator rl2:lte ;
    rl2:rightOperand "2025-06-30T23:59:59Z"^^xsd:dateTimeStamp .
```

**Temporal patterns**:
- **Start only**: `currentDateTime gte startDate` (from date onwards)
- **End only**: `currentDateTime lte endDate` (deadline)
- **Both**: combine with `rl2:and` (closed interval)

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

### Composed Conditions and Dependencies

Conditions are composed with logical constraints (`rl2:and`, `rl2:or`, `rl2:xone`, `rl2:not`). The following privilege requires:
- Purpose is research
- Time is within 2025
- Approval has been granted

```turtle
ex:purpose a rl2:LeftOperand ;
    rl2:resolutionPath "context.purpose" .

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
            a rl2:LogicalConstraint ;
            rl2:constraintOperator rl2:and ;
            rl2:operand [
                a rl2:AtomicConstraint ;
                rl2:leftOperand rl2:currentDateTime ;
                rl2:constraintOperator rl2:gte ;
                rl2:rightOperand "2025-01-01T00:00:00Z"^^xsd:dateTimeStamp
            ] ;
            rl2:operand [
                a rl2:AtomicConstraint ;
                rl2:leftOperand rl2:currentDateTime ;
                rl2:constraintOperator rl2:lte ;
                rl2:rightOperand "2025-12-31T23:59:59Z"^^xsd:dateTimeStamp
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

### Duty Status Queries and Prerequisites

Use `rl2:prerequisiteDuty` for the ordinary rule “this Duty must be Fulfilled before this
Privilege applies.” State-query operands remain available when a condition needs to compare or
bind Duty-derived data for some other purpose:

| Left Operand | Queries | Returns |
|--------------|---------|---------|
| `rl2:obligationStateOperand` | Derived status of `targetNorm` | Pending, Active, Fulfilled, Violated |
| `rl2:dutyPerformerOperand` | Unambiguous fulfillment evidence for `targetNorm` | Agent who fulfilled, or Missing/Conflict |

These operands require `rl2:targetNorm` to specify which Duty to query. Do not restate an attached
Duty's basic Fulfilled test with `obligationStateOperand`; `prerequisiteDuty` already supplies it.

**Deontic Philosophy Connection:**

| German Term | English | RL2 Pattern |
|-------------|---------|-------------|
| *Tun-sollen* | Ought-to-do (personal) | `prerequisiteDuty` plus `dutyPerformer = currentAgent` |
| *Sein-sollen* | Ought-to-be (impersonal) | `prerequisiteDuty` alone |

This example requires the requesting agent to have performed the prerequisite personally:

```turtle
ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:User ;
    rl2:action ex:pay ;
    rl2:object ex:Resource .

ex:accessPolicy a rl2:Set ;
    rl2:clause ex:accessPrivilege .

ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Resource ;
    rl2:prerequisiteDuty ex:paymentDuty ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:paymentDuty ;
        rl2:leftOperand rl2:dutyPerformerOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .
```

Omit the condition when any qualifying performer is acceptable. Use `neq` instead of `eq` for a
separation-of-duty rule. The prerequisite relation still performs the Fulfilled check in either
case.

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
@prefix privacy: <https://example.org/profile/privacy#> .

privacy:dataOwnerOperand a rl2:LeftOperand ;
    rl2:resolutionPath "asset.dataOwner" .

ex:gdprPrivilege a rl2:Privilege ;
    rl2:subject ex:DataSubject ;
    rl2:action ex:requestErasure ;
    rl2:object ex:PersonalData ;
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
| `state` | Snapshot time, evidence, and profile state facts | `state.Events.approval.operationalAgent` |
| `context` | Evaluation-scoped snapshot facts | `context.purpose` |
| `request` | Core Request fields | `request.requestingAgent` |
| `global` | Caller-supplied aggregate snapshot facts | `global.activeSessions.count` |

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

An Offer proposes terms that become binding upon acceptance. It is the natural home
for **Promises** — voluntary commitments, made or demanded — alongside any restated
externally-imposed Duties (e.g. a statutory obligation the offeror must flag):

```turtle
ex:licenseOffer a rl2:Offer ;
    rl2:grantor ex:DataProvider ;
    rl2:clause ex:usePrivilege ;
    rl2:clause ex:attributionDuty .
```

Until acceptance, no obligations are created: a Promise binds its promisor but
creates no correlative Claim, and there is no consenting counterparty to demand
performance.

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

**Crystallization.** Acceptance turns an Offer into an Agreement: each Promise
*crystallizes* into a Duty plus its correlative Claim (acceptance supplies the
claim-holder the bare Promise lacked), and any restated external Duties carry
through. An executed Agreement therefore contains **only Norms — Duties and Claims,
never Promises**. A Promise creates no correlative, so one sitting in a signed
Agreement would be inert goodwill; SHACL rejects it (use an `rl2:Assertion` for a
non-binding recital). Promises live in Offers; Duties live in Agreements. See
*Crystallization (Offer → Agreement)* in `RL2_Semantics.md` for the full mapping.

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
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:policyGeneration "https://example.org/generations/2025-Q1"^^xsd:anyURI ;
    rl2:clause ex:accessPrivilege .
```

Key concepts:

- A **generation** identifies one immutable policy universe.
- Content changes create a new generation rather than mutating an evaluation input.
- A caller selects the generation and supplies the world snapshot for each evaluation.
- Persisting that selection in a Case or audit record is companion-protocol behavior.

These inputs make an evaluation reproducible without prescribing storage or workflow.

---

## 10. Evaluation Semantics

Core evaluation is one pure function:

```text
Eval(PolicyUniverse, Request, WorldSnapshot, EvaluationConfiguration)
    -> EvaluationResult
```

The snapshot fixes evaluation time, attributed facts, and evidence. The evaluator validates those
inputs, derives the normative envelope and Duty/Promise statuses, then resolves Privilege and
Prohibition conflicts. Missing or conflicting decisive data yields `Indeterminate` with causal
diagnostics; no implicit default or live lookup supplies a value.

### Re-evaluation Is Not a State Transition

Consider an Achievement Duty whose window ends at the start of March 16:

| Supplied snapshot | Derived status |
|---|---|
| Before the window starts | Pending |
| March 1, no qualifying deletion evidence | Active |
| March 1, qualifying deletion evidence exists | Fulfilled |
| March 16, no qualifying deletion evidence | Violated |

Each row is a separate evaluation of immutable inputs. RL2 does not require an implementation to
store the earlier result, process a clock event, or mutate the Duty. Applications may persist
results and build audit trails, but persistence, scheduling, Cases, and distributed protocols are
future companion concerns.

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

ex:purpose a rl2:LeftOperand ;
    rl2:resolutionPath "context.purpose" .

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
    rl2:policyGeneration "https://example.org/generations/2025-v1"^^xsd:anyURI ;
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
            a rl2:LogicalConstraint ;
            rl2:constraintOperator rl2:and ;
            rl2:operand [
                a rl2:AtomicConstraint ;
                rl2:leftOperand rl2:currentDateTime ;
                rl2:constraintOperator rl2:gte ;
                rl2:rightOperand "2025-01-01T00:00:00Z"^^xsd:dateTimeStamp
            ] ;
            rl2:operand [
                a rl2:AtomicConstraint ;
                rl2:leftOperand rl2:currentDateTime ;
                rl2:constraintOperator rl2:lte ;
                rl2:rightOperand "2025-12-31T23:59:59Z"^^xsd:dateTimeStamp
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
    rl2:dutyWindow [
        a rl2:DutyWindow ;
        rl2:startInclusive "2025-01-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2025-07-01T00:00:00Z"^^xsd:dateTimeStamp
    ] .

# ============================================
# Clause 3: Deletion Duty
# Researcher must delete data by December 31
# ============================================

ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:ExternalResearcher ;
    rl2:action ex:delete ;
    rl2:object ex:ResearchDataset ;
    rl2:dutyWindow [
        a rl2:DutyWindow ;
        rl2:startInclusive "2025-01-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2026-01-01T00:00:00Z"^^xsd:dateTimeStamp
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
3. Committee approval evidence exists in the supplied snapshot? **Yes** ✓

All conditions are satisfied.

**Step 4: Check for prohibitions**

Is there an active prohibition on use? `ex:distributionProhibition` applies to `distribute`, not `use`. **No conflict**.

**Step 5: Report independent Duty status**

The policy also contains two independent Duties:
- `ex:reportDuty` is Pending (deadline June 30)
- `ex:deletionDuty` is Pending (deadline Dec 31)

Their statuses are part of the evaluation result but do not gate `ex:usePrivilege`.

**Step 6: Decision**

Result: **Permit**

The researcher may proceed. A companion protocol may package the independent Duty statuses as
runtime requirements, but that is not part of the core decision.

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

- `RL2_Vocabulary.md` — Informative class and property reference
- `../spec/rl2.ttl` — Normative OWL ontology
- `../spec/rl2-shacl.ttl` — SHACL validation shapes
- `../spec/profiles/` — Domain-specific profiles with declared operands

### Formal Semantics

- `../spec/RL2_Model.md` — Evaluation inputs and outputs
- `../spec/RL2_Semantics.md` — Mathematical definitions of policy evaluation
- `RL2_Architecture.md` — Pure evaluation boundary and design rationale

### Future Work

- `../future/protocol/` — Retained protocol/workflow research
- `../future/reference-implementation/` — Retained IR/evaluator design ideas

### Project Status

- `../project/issues.md` — Active issue tracker
- `../project/reorganization-plan.md` — SCOPE-2 work plan

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
| Set a time window | `rl2:AtomicConstraint` with `rl2:currentDateTime` using `rl2:gte`/`rl2:lte` |
| Require approval | `rl2:EventConstraint` with `rl2:approver` |
| Combine conditions | `rl2:LogicalConstraint` with `rl2:and`/`rl2:or` |
| Bundle norms | `rl2:Policy` with `rl2:clause` |
| Create bilateral agreement | `rl2:Agreement` |
| Access contextual data | Profile-declared `rl2:LeftOperand` with `rl2:resolutionPath` |

---

## Glossary

For definitions of terms used in this document, see **RL2_References.md**.

---

*This primer covers RL2 version 0.6. For updates and errata, see the RL2 repository.*

---

## Appendix A: ODRL Mapping Reference

This appendix provides detailed mapping tables for translating ODRL 2.2 policies to RL2. For transpilation patterns and worked examples, see **usecases/**.

### A.1 Structural Mapping

| ODRL Concept | RL2 Equivalent | Notes |
|:-------------|:---------------|:------|
| Policy | `rl2:Policy` | Direct mapping |
| Rule | `rl2:Norm` | "Rule" is syntactic; "Norm" is semantic |
| Permission | `rl2:Privilege` | Hohfeldian term for "permission" |
| Prohibition | `rl2:Prohibition` | Direct mapping |
| Duty | `rl2:Duty` | Direct mapping |
| Asset | `rl2:Asset` | Direct mapping |
| Party | `rl2:Agent` | Direct mapping |
| Action | `rl2:Action` | Direct mapping |
| Constraint | `rl2:Condition` | RL2 distinguishes AtomicConstraint, LogicalConstraint, EventConstraint |

### A.2 Property Mapping

| ODRL Property | RL2 Property | Semantics |
|:--------------|:-------------|:----------|
| `assignee` | `rl2:subject` | Agent bearing the norm |
| `assigner` | `rl2:counterparty` | Agent to whom duty is owed |
| `target` | `rl2:object` | Asset acted upon |
| `action` | `rl2:action` | Operation being regulated |
| `constraint` | `rl2:condition` | Activation requirements |
| `refinement` | `rl2:condition` | Nested conditions on assets/actions |
| `relation` | *(no RL2-core equivalent)* | ODRL asset relations are out of core; would need a profile |
| `consequence` | State-triggered Duty | Duty conditioned on violation state |
| `remedy` | State-triggered Duty | Duty conditioned on prohibition violation |

### A.3 Operator Mapping

| ODRL Operator | RL2 Operator | Type |
|:--------------|:-------------|:-----|
| `eq`, `neq` | `rl2:eq`, `rl2:neq` | Comparison |
| `lt`, `lte`, `gt`, `gte` | `rl2:lt`, `rl2:lte`, `rl2:gt`, `rl2:gte` | Comparison |
| `isA` | `rl2:isA` | Semantic |
| `isAnyOf`, `isAllOf` | `rl2:isAnyOf`, `rl2:isAllOf` | Set |
| `isNoneOf` | `rl2:isNoneOf` | Set |
| `and`, `or`, `xone` | `rl2:and`, `rl2:or`, `rl2:xone` | Logical |

### A.4 Key Transpilation Patterns

#### Permission-Bound Duties

ODRL embeds duties inside permissions to imply "you can do X if you do Y." RL2 decouples these:

1. Extract the duty as a standalone norm
2. Add a condition to the privilege checking duty state
3. Make identity binding explicit (ODRL implies SameSubject)

See **usecases/pay-to-play.md** for the complete pattern.

#### Inheritance (`inheritFrom`)

RL2 performs compile-time flattening:
- Recursively resolve parent policies
- Union all clauses
- Output self-contained policy with no external dependencies

#### Consequences and Remedies

RL2 models these as state-triggered duties:
- The remedial duty has `rl2:obligationState rl2:Pending`
- Its condition checks `rl2:obligationStateOperand eq rl2:Violated` on the original duty

See **usecases/quality-circuit-breaker.md** for violation chains.

### A.5 ODRL Ambiguities Resolved by RL2

| Ambiguity | ODRL Behavior | RL2 Resolution |
|:----------|:--------------|:---------------|
| Party roles | `assigner`/`assignee` overloaded | Split into normative (subject/counterparty) and functional (grantor/grantee) roles |
| Duty role and fulfillment | Permission duty vs Policy obligation is structural; fulfillment remains application-dependent | Explicit prerequisite vs independent role plus snapshot-derived status |
| Identity binding | Implicit SameSubject assumption | Explicit via `dutyPerformerOperand` constraint |
| Evaluation | Processing is described but key inputs remain application-dependent | Pure `Eval` over an explicit Request and WorldSnapshot |

### A.6 RL2 Extensions Beyond ODRL

| Capability | ODRL 2.2 | RL2 |
|:-----------|:---------|:----|
| Event-based conditions | Not supported | `rl2:EventConstraint` |
| Duty fulfillment | Application-dependent | Pure snapshot-derived status with explicit evidence and time boundaries |
| Identity binding patterns | Implied | Explicit `dutyPerformerOperand` with `eq`/`neq` |
| Promises | Not supported | First-class `rl2:Promise` |
| Hohfeldian relations | Partial (Permission, Prohibition, Duty) | Full (adds Claim, Power, Liability, Immunity) |
| Violation detection | Not supported | State tracking with `rl2:Violated` |

---

*End of Appendix A*
