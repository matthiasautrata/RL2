---
title: "RL2: A Verified, Operational Rights Language"
version: "0.2"
status: "Draft"
date: 2025-01-01
---

## Introduction

Modern data governance faces a fundamental challenge: bridging the gap between policy intent and machine execution.

Organizations express policies in ODRL 2.2 or natural language, but verifying consistent interpretation and enforcement across systems remains difficult. Several open questions persist in current practice:

- **Temporal semantics:** When does an obligation become active? What constitutes violation?
- **Approval workflows:** How are multi-party approvals modeled within the policy itself?
- **Formal verification:** Can we prove properties about policy behavior before deployment?

**RL2 ("Rights Language 2")** addresses these questions by providing a semantically rigorous policy language with explicit operational semantics and a structure amenable to formal verification.

---

## What is RL2?

RL2 is a unified rights language that combines four complementary foundations:

1. **Normative Logic (DPCL/Hohfeld):** Precise definitions of Privilege, Duty, Power, and Liability based on Hohfeldian legal theory.
2. **Promise Theory:** Modeling voluntary commitments between specific agents, capturing bilateral relationships.
3. **Operational Semantics (ODRE):** Explicit state machines for obligations, defining activation, fulfillment, and violation.
4. **Formal Verification:** A structure designed to be compiled into verifiable logic (Why3, K Framework, Lean 4).

RL2 serves as a **compilation target**. Policies expressed in ODRL or other formats can be translated into RL2, producing deterministic executable specifications.

---

## Illustrative Examples

The following examples demonstrate how RL2 addresses common policy scenarios.

### Temporal Obligations: The "30-Day Deletion" Rule

**Requirement:** "The researcher must delete the data within 30 days of access."

#### ODRL Representation

```turtle
<policy> a odrl:Set ;
    odrl:permission [
        odrl:action odrl:use ;
        odrl:duty [
            odrl:action odrl:delete ;
            odrl:constraint [
                odrl:operator odrl:lte ;
                odrl:rightOperand "P30D"
            ]
        ]
    ] .
```

This representation leaves several questions to the implementer:
- What is the temporal anchor for "P30D"? Policy creation, first access, or approval?
- What is the obligation's current state (pending, active, fulfilled)?
- What constitutes violation, and how should violations be handled?

#### RL2 Representation

RL2 models this as an **Operational Duty** with a clear lifecycle.

```turtle
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix ex:   <https://example.org/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# Domain-specific actions (defined by policy/profile)
ex:use a rl2:Action .
ex:delete a rl2:Action .

# Agents and Assets
ex:Researcher a rl2:Agent .
ex:Dataset a rl2:Asset .

ex:policy a rl2:Set ;
    rl2:clause ex:usePrivilege , ex:deleteDuty .

ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset .

ex:deleteDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:delete ;
    rl2:object ex:Dataset ;
    rl2:obligationState rl2:Pending ;
    # Explicit Operational Semantics
    # Deadline: must be fulfilled within 30 days of access
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            # Deadline is 30 days after the access event
            rl2:end [ a rl2:DynamicOperandReference ;
                      rl2:dynamicOperand "event.AccessEvent.timestamp + P30D" ]
        ]
    ] .
```

This representation provides:
- **Explicit temporal anchor:** The deletion deadline is bound to 30 days after the `AccessEvent`.
- **Observable state:** The RL2 runtime tracks when this duty transitions from `Pending` to `Active` to `Fulfilled` or `Violated`.
- **Deterministic evaluation:** If `current_time > deadline` and `delete` has not occurred, the state machine transitions to `Violated`.

---

### Multi-Party Workflows: Approval and Commitment

**Requirement:** "Access requires approval from the Data Owner AND a promise of stewardship from the Researcher."

In many policy languages, multi-party approvals are handled outside the policy itself—the policy grants permission, and application code separately checks for approvals. This creates a gap between policy specification and enforcement.

RL2 models approvals and promises as **normative preconditions** within the policy:

```turtle
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix ex:   <https://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Domain-specific action
ex:use a rl2:Action .

# Agents and Assets
ex:Researcher a rl2:Agent .
ex:DataOwner a rl2:Agent .
ex:Dataset a rl2:Asset .

# Custom promise content
ex:DataStewardship rdfs:label "Data Stewardship Commitment" .

ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand ex:OwnerApproval ;
        rl2:operand ex:StewardshipPromiseCheck
    ] .

ex:OwnerApproval a rl2:EventConstraint ;
    rl2:expectsEvent [
        a rl2:Event ;
        rl2:approver ex:DataOwner
    ] .

ex:StewardshipPromiseCheck a rl2:Condition ;
    rl2:requires ex:StewardshipPromise .

ex:StewardshipPromise a rl2:Promise ;
    rl2:promiser ex:Researcher ;
    rl2:promisee ex:DataOwner ;
    rl2:promiseContent ex:DataStewardship ;
    rl2:promiseState rl2:PromiseFulfilled .
```

The policy is self-contained: the `Privilege` evaluates to active only when the required `Event` (approval) and `Promise` exist in the system state. The enforcement logic is specified within the policy, not in application code.

---

### Dynamic Workflows: Conditional Policy Activation

**Requirement:** "The committee can choose to review or decline. If they accept, the requester must obtain full approval."

Some workflows require different policies to apply depending on events that occur during execution. Rather than modeling this as branching within a single policy, RL2 uses **policy-level activation conditions**—separate policies that become applicable when their preconditions are met:

```turtle
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix ex:   <https://example.org/> .

# Domain-specific actions and events
ex:submitForReview a rl2:Action .
ex:obtainFullApproval a rl2:Action .
ex:CommitteeAcceptance a rl2:Event .

# Policy 1: Initial review request (always applicable)
ex:reviewRequestPolicy a rl2:Set ;
    rl2:clause ex:askCommitteeDuty .

ex:askCommitteeDuty a rl2:Duty ;
    rl2:subject ex:Requester ;
    rl2:action ex:submitForReview ;
    rl2:object ex:Case .

# Policy 2: Full review (applicable only when committee accepts)
ex:fullReviewPolicy a rl2:Set ;
    rl2:condition [
        a rl2:EventConstraint ;
        rl2:expectsEvent [ a ex:CommitteeAcceptance ]
    ] ;
    rl2:clause ex:obtainApprovalDuty .

ex:obtainApprovalDuty a rl2:Duty ;
    rl2:subject ex:Requester ;
    rl2:action ex:obtainFullApproval ;
    rl2:object ex:Case .
```

The workflow behavior:
- **Committee declines:** Only `reviewRequestPolicy` ever applied. Case concludes.
- **Committee accepts:** `CommitteeAcceptance` event enters state Σ → `fullReviewPolicy` becomes applicable → new duty activates.

Events change which policies apply, rather than branching within a single policy. The RL2 evaluator re-assesses applicable policies on each context change, making dynamic workflows a natural consequence of the architecture.

---

## Architecture Overview

RL2 integrates into existing systems through three components:

**Compiler**
- Input: ODRL 2.2 or native RL2 policies.
- Process: Translates ODRL into RL2 structures, reporting any semantic gaps that require explicit choices (e.g., "Duty missing temporal anchor—please specify").
- Output: A validated RL2 graph.

**Evaluator (Kernel)**
- A small, side-effect-free decision function (suitable for implementation in Rust, OCaml, or verified languages).
- Input: RL2 graph + event log + current state.
- Output: `Permit` / `Deny` / `Violations` / `Pending obligations`.

**Enforcer**
- The API gateway or data platform that queries the evaluator and acts on decisions.

---

## Motivation and Applications

As automated systems—including AI agents—take on compliance and enforcement tasks, they require policies with unambiguous semantics. A policy language with formal operational semantics enables:

- **Automated reasoning:** Agents can evaluate whether actions satisfy constraints without human interpretation.
- **Audit trails:** The state machine produces a verifiable record of obligation states and transitions.
- **Formal verification:** Policy properties can be proven before deployment using standard verification tools.

RL2 bridges high-level legal intent and machine execution by making policy semantics explicit and deterministic.

---

## References

See **RL2_References.md** for complete citations and glossary.

**RL2 Specifications:**
- RL2_Core.md — Core ontology
- RL2_Semantics.md — Formal semantics
- RL2_Protocol.md — Evaluation protocol
- RL2_ODRL_Coverage.md — ODRL compatibility
- RL2_ResearchPlan.md — Mechanization roadmap (Why3, K, Lean 4)