---
title: "RL2 Primer"
subtitle: "A Practical Introduction to the Rights Language 2"
version: "0.2"
status: "Draft"
date: 2025-01-01
audience: "Students, practitioners, and implementers new to RL2"
prerequisites: "Basic familiarity with RDF and policy concepts"
---

## About This Document

This primer teaches you to read, understand, and write RL2 policies. It builds concepts progressively, with examples at each step. By the end, you will be able to:

- Understand what problems RL2 solves
- Read RL2 policies and trace their evaluation
- Write policies for common scenarios
- Know where to look for detailed reference material

For formal definitions and complete class/property specifications, see **RL2_Vocabulary.md**.

---

## Table of Contents

1. [Why RL2?](#1-why-rl2)
2. [The Big Picture](#2-the-big-picture)
3. [Agents and Assets](#3-agents-and-assets)
4. [Your First Norm: The Privilege](#4-your-first-norm-the-privilege)
5. [Obligations: Duties and Prohibitions](#5-obligations-duties-and-prohibitions)
6. [The Correlatives: Claims and Beyond](#6-the-correlatives-claims-and-beyond)
7. [Promises: Voluntary Commitments](#7-promises-voluntary-commitments)
8. [Conditions: When Rules Apply](#8-conditions-when-rules-apply)
9. [Policies: Bundling Norms Together](#9-policies-bundling-norms-together)
10. [The Operational Layer: How Duties Come to Life](#10-the-operational-layer-how-duties-come-to-life)
11. [Putting It All Together](#11-putting-it-all-together)
12. [Where to Go Next](#12-where-to-go-next)

---

## 1. Why RL2?

### The Problem

Imagine you need to express this policy:

> "Researchers may use the dataset for academic purposes. They must delete it within 30 days of access."

This seems simple. But when you try to implement it, questions arise:

- 30 days from *when*? When they download it? When they first open it? When they're approved?
- What does "must" mean operationally? Is it just a guideline, or does violation have consequences?
- How do you track whether the deletion actually happened?
- What if they download it twice—does each download start a new 30-day clock?

Existing policy languages like ODRL let you *express* these rules, but they leave these questions to the implementer. Different systems interpret the same policy differently.

### The Solution

RL2 provides **precise, operational semantics**. Every construct has a clear meaning that doesn't depend on interpretation:

```
                     ODRL Policy
                          |
                          v
                   +-------------+
                   |  Compiler   |  (fills in gaps, resolves ambiguity)
                   +-------------+
                          |
                          v
                     RL2 Policy
                          |
                          v
                   +-------------+
                   |  Evaluator  |  (deterministic decisions)
                   +-------------+
                          |
                          v
                 Permit / Deny / Obligations
```

When you write a policy in RL2, there's no ambiguity about what it means. The evaluator produces the same result every time.

### What RL2 Adds

RL2 is a strict superset of ODRL. It adds:

| Gap in ODRL | RL2 Solution |
|-------------|--------------|
| Implicit temporal semantics | Explicit intervals and deadlines |
| Unclear obligation lifecycle | State machine: Pending → Active → Fulfilled/Violated |
| Permission-focused | Full Hohfeldian framework (Claims, Powers, Immunities) |
| No voluntary commitments | Promise Theory integration |
| Ambiguous evaluation | Formal operational semantics |

Let's learn how it works.

---

## 2. The Big Picture

Before diving into details, let's see how RL2's pieces fit together.

### The Information Model

```
+------------------------------------------------------------------+
|                           POLICY                                  |
|  (Set, Offer, Agreement, Privacy, Assertion)                     |
|                                                                   |
|   grantor -----> Agent                                           |
|   grantee -----> Agent                                           |
|   condition --> Condition (optional: when policy applies)        |
|                                                                   |
|   clauses:                                                        |
|   +----------------------------------------------------------+   |
|   |  NORM                                                     |   |
|   |  (Privilege, Duty, Prohibition, Claim, Power, ...)       |   |
|   |                                                           |   |
|   |   subject ------> Agent (who bears the norm)             |   |
|   |   action -------> Action (what they do)                  |   |
|   |   object -------> Asset (what it's about)                |   |
|   |   condition ----> Condition (when it applies)            |   |
|   +----------------------------------------------------------+   |
+------------------------------------------------------------------+
```

A **Policy** is a container that holds **Norms**. Each norm connects an **Agent** to an **Action** on an **Asset**, possibly under some **Condition**.

### The Eight Layers

RL2 is organized into eight conceptual layers. You don't need to understand all of them to get started, but knowing they exist helps you navigate:

```
+-------------------------------------------------------------------+
| 8. Policy Generation Layer    | Versioning: which policies are    |
|                               | in force at what time             |
+-------------------------------+-----------------------------------+
| 7. Policy Container Layer     | Groups norms into policies        |
|                               | (Set, Offer, Agreement, etc.)     |
+-------------------------------+-----------------------------------+
| 6. Temporal/Context Layer     | Time windows, environment checks  |
+-------------------------------+-----------------------------------+
| 5. Operational Layer          | Events, state transitions,        |
|                               | duty lifecycle                    |
+-------------------------------+-----------------------------------+
| 4. Action/Asset/Condition     | The things you govern and the     |
|    Layer                      | constraints that apply            |
+-------------------------------+-----------------------------------+
| 3. Role Layer                 | Who plays what part               |
|                               | (subject, grantor, approver...)   |
+-------------------------------+-----------------------------------+
| 2. Promise Theory Layer       | Voluntary bilateral commitments   |
+-------------------------------+-----------------------------------+
| 1. Normative Layer            | The fundamental norm types        |
|                               | (Privilege, Duty, Claim, Power..) |
+-------------------------------+-----------------------------------+
```

We'll work through these bottom-up, starting with the foundational normative concepts.

---

## 3. Agents and Assets

Every policy involves someone doing something to something. RL2 calls these **Agents** and **Assets**.

### Agents

An Agent is any party that can participate in a policy. This includes:

- People (researchers, employees, customers)
- Organizations (companies, departments, committees)
- Systems (services, applications, automated processes)

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix ex:  <https://example.org/> .

ex:Alice a rl2:Agent .
ex:ResearchTeam a rl2:Agent .
ex:DataPlatform a rl2:Agent .
```

RL2 doesn't prescribe what an agent looks like internally—that's for your system to define. What matters is that agents can be subjects of norms and parties to policies.

### Assets

An Asset is anything that can be governed by a policy:

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

Sometimes you need to govern groups of assets together. An **AssetCollection** lets you do this:

```turtle
ex:SensitiveData a rl2:AssetCollection ;
    rl2:member ex:CustomerDataset ;
    rl2:member ex:EmployeeRecords ;
    rl2:member ex:FinancialData .
```

Collections can also be dynamic, populated by a query at evaluation time:

```turtle
ex:AllClassifiedDocuments a rl2:AssetCollection ;
    rl2:dynamicQuery "SELECT ?doc WHERE { ?doc ex:classification 'SECRET' }" .
```

---

## 4. Your First Norm: The Privilege

The simplest thing a policy can say is "you may do this." In RL2, that's a **Privilege**.

### What Is a Privilege?

A Privilege grants permission. More precisely, it declares that the subject has *no duty to refrain* from the action. This is a subtle but important point: a privilege doesn't create an obligation on anyone else. It just says "you're allowed."

### Anatomy of a Privilege

```turtle
ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;      # Who has the privilege
    rl2:action ex:use ;              # What they may do
    rl2:object ex:Dataset .          # What it's about
```

Reading this aloud: "The Researcher has a privilege to use the Dataset."

### A Complete Example

Let's write a simple privilege with a condition:

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix ex:  <https://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Define our action (profiles provide these)
ex:use a rl2:Action .

# Define our agents and asset
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

This says: "Alice may use the Research Dataset during 2025."

### What Happens Without a Privilege?

If no privilege exists for an action, the default is **not permitted**. RL2 follows a closed-world assumption: access requires explicit authorization.

---

## 5. Obligations: Duties and Prohibitions

Privileges tell you what you *may* do. Duties and prohibitions tell you what you *must* and *must not* do.

### Duties: What You Must Do

A **Duty** is an obligation to perform an action. Unlike a privilege (which just permits), a duty creates a requirement that can be fulfilled or violated.

```turtle
ex:reportDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:submitReport ;
    rl2:object ex:Dataset .
```

Reading this: "The Researcher has a duty to submit a report about the Dataset."

### The Duty Lifecycle

This is where RL2 differs from other policy languages. A duty isn't just a static statement—it has a **lifecycle**:

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

We'll explore this lifecycle in detail in Section 10.

### A Duty with a Deadline

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

This duty must be fulfilled by March 15, 2025. If the action isn't performed by then, the duty transitions to Violated.

### Prohibitions: What You Must Not Do

A **Prohibition** says you may not perform an action. It's the opposite of a privilege.

```turtle
ex:distributionBan a rl2:Prohibition ;
    rl2:subject ex:Researcher ;
    rl2:prohibitedAction ex:distribute ;
    rl2:object ex:Dataset .
```

Reading this: "The Researcher must not distribute the Dataset."

Note that prohibitions use `rl2:prohibitedAction` instead of `rl2:action`. This makes the intent explicit in the RDF and enables clearer queries.

### Why Not Just Use "Duty to Refrain"?

Technically, a prohibition is equivalent to "a duty not to do something." RL2 models Prohibition explicitly because:

1. Policy authors think "you may not do X" more naturally than "you have a duty to not do X"
2. It enables `rl2:prohibitedAction` as a clear property
3. It aligns with ODRL and other languages, easing translation

---

## 6. The Correlatives: Claims and Beyond

So far we've covered Privilege, Duty, and Prohibition. But RL2 models the full **Hohfeldian framework**—eight fundamental legal concepts that form the backbone of normative relations.

### Why Hohfeld?

Wesley Hohfeld, a legal scholar in the early 1900s, observed that legal relations come in pairs. When one party has a certain position, another party necessarily has a **correlative** position:

```
+-------------+     correlative     +-------------+
|  Privilege  | <-----------------> |  No-Claim   |
+-------------+                     +-------------+
If Alice has a privilege to X,      Bob has no claim that Alice not X
(she may do X)                      (he can't demand she refrain)


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

### What RL2 Models

RL2 models these Hohfeldian concepts as norm types:

| RL2 Class | Meaning |
|-----------|---------|
| `rl2:Privilege` | You may do something |
| `rl2:Duty` | You must do something |
| `rl2:Prohibition` | You must not do something (RL2 addition) |
| `rl2:Claim` | You can demand someone else do something |
| `rl2:Power` | You can change someone's normative position |
| `rl2:Liability` | Your position can be changed by another |
| `rl2:Immunity` | Your position cannot be changed by another's power |

Note: **No-Claim** and **Disability** are not modeled as classes. They represent *absences* of positions, which we infer rather than state explicitly.

### Claims: The Correlative of Duty

When Alice has a duty to Bob, Bob has a claim against Alice. RL2 lets you model this directly:

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

Why model both? Because they serve different purposes:
- The **Duty** tells Alice what she must do
- The **Claim** tells Bob what he can demand

### Powers: Changing Normative Relations

A **Power** is the ability to change someone's normative position. Think of it as meta-level authority.

Example: A manager has the power to grant access privileges to team members.

```turtle
ex:managerPower a rl2:Power ;
    rl2:subject ex:Manager ;
    rl2:affectsNorm ex:accessPrivilegeTemplate .

ex:employeeLiability a rl2:Liability ;
    rl2:subject ex:Employee ;
    rl2:exposedTo ex:managerPower .
```

When the manager exercises this power, they can create new privileges for employees.

### Immunities: Protection from Powers

An **Immunity** protects someone from having their position changed:

```turtle
ex:tenureImmunity a rl2:Immunity ;
    rl2:subject ex:Professor ;
    rl2:immuneFrom ex:firingPower .
```

This says the Professor cannot have their employment terminated by the normal firing power.

### When to Use the Full Framework

For simple policies, you may only need Privilege, Duty, and Prohibition. The full Hohfeldian framework becomes valuable when modeling:

- **Contractual relationships** where parties have correlative rights and duties
- **Authorization hierarchies** where some agents can grant or revoke others' access
- **Protected positions** where certain agents have immunity from changes

---

## 7. Promises: Voluntary Commitments

RL2 includes **Promise Theory**, which models voluntary commitments between agents. Promises are fundamentally different from norms.

### Promises vs. Duties

| Aspect | Duty | Promise |
|--------|------|---------|
| **Source** | Imposed by policy | Voluntary commitment |
| **Nature** | "You must" | "I will" |
| **Parties** | May have abstract counterparty | Always has specific promisee |
| **Creation** | Policy author defines | Promisor actively commits |

### Why This Matters

Consider two statements:

1. *"Researchers must delete data within 30 days"* — This is a **Duty**. It's imposed by policy, whether the researcher agreed or not.

2. *"Alice commits to Bob to handle data responsibly"* — This is a **Promise**. Alice voluntarily made this commitment to Bob.

The difference matters for:
- **Provenance**: Why does this obligation exist?
- **Enforcement**: Who can demand performance?
- **Trust**: Promises reflect willing cooperation

### Anatomy of a Promise

```turtle
ex:stewardshipPromise a rl2:Promise ;
    rl2:promisor ex:Researcher ;       # Who makes the promise
    rl2:promisee ex:DataOwner ;        # Who receives it
    rl2:promiseContent ex:DataStewardshipDuty ;  # What's promised
    rl2:promiseState rl2:PromisePending .        # Current state
```

### Promise States

Like duties, promises have a lifecycle:

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

### Promises Can Create Norms

When Alice promises Bob to delete data, this may give rise to:
- A **Duty** on Alice (to delete)
- A **Claim** for Bob (to have it deleted)

The promise is the *source*; the norms are the *effects*. This allows tracking of *why* a duty exists.

### Using Promises as Conditions

Policies can require a promise as a precondition:

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

This says: "The researcher may access sensitive data only if they have made the stewardship promise."

---

## 8. Conditions: When Rules Apply

Most norms don't apply unconditionally. They have constraints—time windows, purpose restrictions, approval requirements. RL2 models these as **Conditions**.

### The Condition Hierarchy

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

### Atomic Constraints: Simple Comparisons

The simplest condition compares a property to a value:

```turtle
ex:purposeConstraint a rl2:AtomicConstraint ;
    rl2:leftOperand ex:purpose ;    # The property to check
    rl2:constraintOperator rl2:eq ; # The comparison
    rl2:rightOperand "research" .   # The required value
```

This says: "The purpose must equal 'research'."

**Comparison operators**:
| Operator | Meaning |
|----------|---------|
| `rl2:eq` | Equal to |
| `rl2:neq` | Not equal to |
| `rl2:lt` | Less than |
| `rl2:lte` | Less than or equal |
| `rl2:gt` | Greater than |
| `rl2:gte` | Greater than or equal |
| `rl2:isA` | Is of type |
| `rl2:isAnyOf` | Is one of (set membership) |
| `rl2:isAllOf` | Satisfies all of |
| `rl2:isNoneOf` | Is none of (exclusion) |

### Logical Constraints: Combining Conditions

You can combine conditions with logical operators:

```turtle
ex:combinedConstraint a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:and ;
    rl2:operand ex:purposeConstraint ;
    rl2:operand ex:locationConstraint .
```

**Logical operators**:
| Operator | Meaning |
|----------|---------|
| `rl2:and` | All operands must be true |
| `rl2:or` | At least one operand must be true |
| `rl2:xone` | Exactly one operand must be true |
| `rl2:not` | The operand must be false |

### Temporal Constraints: Time Windows

Temporal constraints use **EffectiveInterval** to specify when something applies:

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

### Contextual Constraints: Environment Checks

Contextual constraints check the evaluation environment:

```turtle
ex:locationCheck a rl2:ContextualConstraint ;
    rl2:contextPath "request.location.country" ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperand "DE" .
```

This checks that the request originates from Germany.

### Event Constraints: Approval Requirements

Event constraints require that something has happened:

```turtle
ex:approvalRequired a rl2:EventConstraint ;
    rl2:expectsEvent [
        a rl2:Event ;
        rl2:approver ex:DataOwner
    ] .
```

This says: "An approval event from the DataOwner must have occurred."

### Dynamic Operand References

Sometimes values aren't known until evaluation time. Dynamic references let you compute them:

```turtle
ex:dynamicDeadline a rl2:DynamicOperandReference ;
    rl2:dynamicOperand "event.AccessEvent.timestamp + P30D" .
```

This evaluates to "30 days after the access event occurred."

### Composing Conditions

Real policies combine these. Here's a privilege that requires:
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

---

## 9. Policies: Bundling Norms Together

Individual norms are useful, but real-world policies bundle multiple norms into coherent packages. That's what **Policy** containers do.

### Policy Structure

```turtle
ex:dataUsePolicy a rl2:Policy ;
    rl2:grantor ex:DataOwner ;          # Who issues the policy
    rl2:grantee ex:Researcher ;         # Who receives it
    rl2:clause ex:usePrivilege ;        # The norms it contains
    rl2:clause ex:reportDuty ;
    rl2:clause ex:distributionBan .
```

A policy bundles norms (via `rl2:clause`) and identifies the parties involved.

### Policy Types

RL2 defines five policy types for different situations:

| Type | Use Case | Key Feature |
|------|----------|-------------|
| **Set** | Public terms, general rules | No specific counterparty |
| **Offer** | Proposed terms awaiting acceptance | Creates no obligations until accepted |
| **Agreement** | Binding contract between parties | Both parties identified and consenting |
| **Privacy** | Data protection policies | Typically duties on controllers, rights for subjects |
| **Assertion** | Claims about status | Declares facts, doesn't create norms |

### Set: Unilateral Declarations

A Set is a policy without identified counterparties. Think of it as "the rules of the house":

```turtle
ex:termsOfService a rl2:Set ;
    rl2:clause ex:acceptableUsePrivilege ;
    rl2:clause ex:noAbuseDuty .
```

No acceptance is required—these are the standing rules.

### Offer: Awaiting Acceptance

An Offer proposes terms that become binding upon acceptance:

```turtle
ex:licenseOffer a rl2:Offer ;
    rl2:grantor ex:DataProvider ;
    rl2:clause ex:usePrivilege ;
    rl2:clause ex:attributionDuty .
```

Until someone accepts, no obligations are created.

### Agreement: Bilateral Contract

An Agreement binds specific, consenting parties:

```turtle
ex:dataContract a rl2:Agreement ;
    rl2:grantor ex:DataProvider ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:accessPrivilege ;
    rl2:clause ex:deletionDuty ;
    rl2:clause ex:confidentialityDuty .
```

Both parties are identified. SHACL validation requires that Agreements have both `grantor` and `grantee`.

### Policy-Level Conditions

Policies themselves can have conditions. A policy is only *applicable* when its condition holds:

```turtle
ex:emergencyPolicy a rl2:Set ;
    rl2:condition [
        a rl2:EventConstraint ;
        rl2:expectsEvent [ a ex:EmergencyDeclaration ]
    ] ;
    rl2:clause ex:emergencyAccessPrivilege .
```

This policy only applies when an emergency has been declared.

### Policy Generations

Over time, policies change. RL2 tracks this via **policy generations**—immutable snapshots of all policies in force at a point in time.

```turtle
ex:dataPolicy a rl2:Agreement ;
    rl2:policyGeneration <https://example.org/generations/2025-Q1> ;
    rl2:clause ex:accessPrivilege .
```

Key concepts:
- A **generation** is the complete policy universe at a point in time
- Events can activate/deactivate policies *within* a generation
- Changing policy content (adding, amending) creates a *new* generation
- Cases are evaluated under the generation in effect when created

This enables reproducible evaluation and audit trails.

---

## 10. The Operational Layer: How Duties Come to Life

This section covers what makes RL2 fundamentally different from static policy languages: **operational semantics**. Policies aren't just declarations—they're state machines that evolve over time.

### Events: What Happens in the World

An **Event** is something observable that can trigger state changes:

```turtle
ex:accessEvent a rl2:Event ;
    rl2:operationalAgent ex:Alice ;
    rl2:participant ex:Alice .
```

Events include:
- Actions performed (someone accessed data)
- Approvals granted (a manager approved a request)
- Time advancing (a deadline passed)
- External signals (a system notification)

### The Duty State Machine

We introduced this earlier, but now let's trace through it:

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

**Pending**: The duty exists but its activation condition isn't met yet.
**Active**: The condition is met; the duty must now be fulfilled.
**Fulfilled**: The required action was performed.
**Violated**: The deadline passed without fulfillment.

### Tracing a Duty's Lifecycle

Let's trace our deletion duty through its lifecycle:

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

The duty exists but is pending—perhaps waiting for the researcher to first access the data.

**2. Activation (Pending → Active)**

An event occurs: the researcher accesses the dataset on January 15. The system evaluates the duty's condition. Let's say the condition was actually tied to access:

```turtle
rl2:condition [
    a rl2:EventConstraint ;
    rl2:expectsEvent [ a ex:AccessEvent ]
] .
```

Now that access has occurred, the condition is true. The duty transitions to Active.

```turtle
ex:deletionDuty rl2:obligationState rl2:Active .
```

**3. Clock Ticking**

Time passes. On February 20, the system evaluates:
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

**4b. Alternative: Violation (Active → Violated)**

If instead March 16 arrives without deletion:
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

This creates an audit trail of how and why states changed.

### Why Operational Semantics Matter

Without operational semantics, "must delete within 30 days" is ambiguous:
- When does the clock start?
- What happens if they don't?
- How do we track it?

With operational semantics:
- The duty starts Pending and activates on a specific event
- Violation is a defined state with consequences
- Every transition is traceable

---

## 11. Putting It All Together

Let's build a complete, realistic policy from scratch, applying everything we've learned.

### The Scenario

A research institution shares datasets with external researchers under these rules:

1. Researchers may use the dataset for academic purposes during 2025
2. They must submit a report by June 30
3. They must delete the data by December 31
4. They may not distribute the data to third parties
5. Access requires approval from the Data Governance Committee

### The Complete Policy

```turtle
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix ex:   <https://example.org/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# ============================================
# Domain Definitions (would come from profile)
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

### Tracing an Evaluation

Let's trace what happens when the researcher tries to access the data:

**Request**: External Researcher wants to use Research Dataset for academic purposes on February 15, 2025.

**Step 1: Find applicable policies**

The system looks at all policies and their conditions. `ex:dataAccessAgreement` has no policy-level condition, so it's applicable.

**Step 2: Find matching norms**

Within the policy, find norms that match the request (subject=ExternalResearcher, action=use, object=ResearchDataset):
- `ex:usePrivilege` matches ✓

**Step 3: Evaluate conditions**

For `ex:usePrivilege`, check the AND of three conditions:

1. Purpose = "academic"? Check request context. **Yes** ✓
2. Time within 2025? February 15 is in [Jan 1, Dec 31]. **Yes** ✓
3. Committee approval exists? Check event log for approval event. **Yes** ✓

All conditions pass.

**Step 4: Check for prohibitions**

Is there an active prohibition on use? `ex:distributionProhibition` is for `distribute`, not `use`. **No conflict**.

**Step 5: Check for active duties**

Are there unfulfilled duties?
- `ex:reportDuty` is Pending (deadline June 30)
- `ex:deletionDuty` is Pending (deadline Dec 31)

Neither is violated.

**Step 6: Decision**

Result: **PermitWithObligations**

The researcher may proceed, but has pending duties to track.

### What If Conditions Fail?

If the committee hadn't approved:
- Condition 3 would fail
- The privilege would be Inactive
- Result: **NotApplicable** (no matching active privilege)

If the researcher tried to distribute:
- `ex:distributionProhibition` matches
- Its condition (none) is trivially true
- Result: **Deny** (active prohibition)

---

## 12. Where to Go Next

You now understand the core concepts of RL2. Here's where to go for more:

### Reference Documentation

- **RL2_Vocabulary.md** — Complete class-by-class and property-by-property reference
- **rl2.ttl** — The normative OWL ontology
- **rl2-shacl.ttl** — SHACL validation shapes

### Formal Semantics

- **RL2_Semantics.md** — Mathematical definitions of evaluation, state transitions, and typing rules

### Runtime Behavior

- **RL2_Protocol.md** — How to exchange evaluation requests and results between systems

### Background and Motivation

- **RL2_White_Paper.md** — Why RL2 exists, architectural overview, comparison to other systems

### Implementation

- **RL2_ResearchPlan.md** — Roadmap for formal verification and mechanization

### Quick Reference Card

| I want to... | Use this... |
|--------------|-------------|
| Permit an action | `rl2:Privilege` |
| Require an action | `rl2:Duty` |
| Forbid an action | `rl2:Prohibition` |
| Model a right held by someone | `rl2:Claim` |
| Model authority to change rules | `rl2:Power` |
| Model voluntary commitment | `rl2:Promise` |
| Set a time window | `rl2:TemporalConstraint` with `rl2:EffectiveInterval` |
| Require approval | `rl2:EventConstraint` with `rl2:approver` |
| Combine conditions | `rl2:LogicalConstraint` with `rl2:and`/`rl2:or` |
| Bundle norms into a policy | `rl2:Policy` with `rl2:clause` |
| Make a bilateral agreement | `rl2:Agreement` |

---

## Glossary

**Agent**: Any party that can participate in policies (people, organizations, systems).

**Asset**: Any resource governed by policies (data, content, services).

**Claim**: A right held by one agent against another (correlative of Duty).

**Condition**: A constraint that must hold for a norm to be active.

**Duty**: An obligation to perform an action.

**Event**: An observable occurrence that can trigger state changes.

**Generation**: An immutable snapshot of all policies in force at a point in time.

**Immunity**: Protection from having one's normative position changed.

**Liability**: Exposure to having one's normative position changed.

**Norm**: A rule establishing what may, must, or must not be done.

**Policy**: A container bundling norms together with party information.

**Power**: The ability to change normative relations.

**Privilege**: Permission to perform an action.

**Prohibition**: A rule that an action must not be performed.

**Promise**: A voluntary commitment from one agent to another.

---

*This primer covers RL2 version 0.2. For updates and errata, see the RL2 repository.*
