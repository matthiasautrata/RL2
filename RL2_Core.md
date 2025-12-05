---
title: "RL2 Core Specification"
subtitle: "A Unified Normative, Descriptive, and Operational Rights Language"
version: "0.4"
status: "Draft"
date: 2025-01-05
---

## Overview

RL2 ("Rights Language 2") is a next-generation policy language designed as a standalone successor to existing rights languages. It provides a **semantic superset** of capabilities found in ODRL 2.2, DPCL, Promise Theory, and ODRE—expressing every concept these languages can express, though not necessarily replicating their vocabulary verbatim.

RL2 unifies:
- **Descriptive policies** (permissions, prohibitions, duties)
- **Normative relations** (powers, claims, liabilities, promises)
- **Operational behavior** (events, triggers, state transitions)
- **Temporal constraints** (validity intervals, deadlines)

This document provides an overview of RL2 and directs you to detailed documentation.

---

## Documentation Structure

RL2 documentation follows a two-document pedagogical approach:

| Document | Purpose | Audience |
|----------|---------|----------|
| **[RL2_Primer.md](RL2_Primer.md)** | Learn RL2 concepts progressively | New users, students |
| **[RL2_Vocabulary.md](RL2_Vocabulary.md)** | Look up class and property definitions | Implementers, reference |

**Start with the Primer** if you're new to RL2. Use the **Vocabulary** as a reference once you understand the concepts.

---

## Normative Files

The RL2 ontology and validation shapes are defined in machine-readable files:

| File | Description |
|------|-------------|
| **[rl2.ttl](rl2.ttl)** | Complete RL2 OWL ontology in Turtle format |
| **[rl2-shacl.ttl](rl2-shacl.ttl)** | SHACL shapes for syntax validation |
| **[profiles/](profiles/)** | Domain-specific profiles with declared operands |

These files are **normative**. The Primer and Vocabulary provide explanatory prose.

RL2's OWL-based representation enables decidable policy reasoning within OWL-DL bounds, following principles established in semantic policy frameworks [OWL-POLAR].

---

## Conceptual Model

RL2 consists of **eight layers**:

```
+-------------------------------------------------------------------+
| 8. Policy Generation Layer    | Versioning and immutable snapshots|
+-------------------------------+-----------------------------------+
| 7. Policy Container Layer     | Set, Offer, Agreement, Privacy    |
+-------------------------------+-----------------------------------+
| 6. Temporal/Context Layer     | Time intervals, environment       |
+-------------------------------+-----------------------------------+
| 5. Operational Layer          | Events, state transitions         |
+-------------------------------+-----------------------------------+
| 4. Action/Asset/Condition     | What you govern and constraints   |
+-------------------------------+-----------------------------------+
| 3. Role Layer                 | Subject, grantor, approver...     |
+-------------------------------+-----------------------------------+
| 2. Promise Theory Layer       | Voluntary bilateral commitments   |
+-------------------------------+-----------------------------------+
| 1. Normative Layer            | Privilege, Duty, Claim, Power...  |
+-------------------------------+-----------------------------------+
```

See **RL2_Primer.md §2** for detailed explanation.

---

## Information Model

```
+------------------------------------------------------------------+
|                           POLICY                                  |
|  (Set, Offer, Agreement, Privacy, Assertion)                     |
|                                                                   |
|   grantor -----> Agent                                           |
|   grantee -----> Agent                                           |
|   condition --> Condition (when policy applies)                  |
|                                                                   |
|   clauses:                                                        |
|   +----------------------------------------------------------+   |
|   |  NORM                                                     |   |
|   |  (Privilege, Duty, Prohibition, Claim, Power, ...)       |   |
|   |                                                           |   |
|   |   subject ------> Agent                                  |   |
|   |   action -------> Action                                 |   |
|   |   object -------> Asset                                  |   |
|   |   condition ----> Condition                              |   |
|   +----------------------------------------------------------+   |
+------------------------------------------------------------------+
```

---

## Namespace

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
```

---

## Quick Example

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix ex:  <https://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# A research data agreement
ex:dataAgreement a rl2:Agreement ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:usePrivilege, ex:deletionDuty, ex:distributionBan .

# Researcher may use dataset during 2025
ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:start "2025-01-01T00:00:00Z"^^xsd:dateTime ;
            rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime
        ]
    ] .

# Researcher must delete data by deadline
ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:delete ;
    rl2:object ex:Dataset ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime
        ]
    ] .

# Researcher may not distribute
ex:distributionBan a rl2:Prohibition ;
    rl2:subject ex:Researcher ;
    rl2:prohibitedAction ex:distribute ;
    rl2:object ex:Dataset .
```

See **RL2_Primer.md §11** for a complete walkthrough.

---

## Duty State as Precondition Example

RL2 supports conditioning privileges on duty fulfillment. This example shows a "pay-to-play" pattern where access requires prior payment:

```turtle
# The payment duty
ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:User ;
    rl2:action ex:pay ;
    rl2:object ex:Subscription .

# Access requires payment AND that the current user paid
ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Content ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check 1: Is the duty fulfilled?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:obligationStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand rl2:Fulfilled
        ] ;
        rl2:operand [
            # Check 2: Did I (current agent) fulfill it?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:dutyPerformerOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

See **usecases/README.md** for more patterns including Sein-sollen, Separation of Duty, and specific agent binding.

---

## Related Specifications

| Document | Description |
|----------|-------------|
| **[RL2_Semantics.md](RL2_Semantics.md)** | Formal denotational and operational semantics |
| **[RL2_Protocol.md](RL2_Protocol.md)** | Runtime evaluation protocol |
| **[RL2_ODRL_Coverage.md](RL2_ODRL_Coverage.md)** | ODRL 2.2 feature coverage mapping |
| **[RL2_White_Paper.md](RL2_White_Paper.md)** | Motivation, architecture, positioning |
| **[RL2_References.md](RL2_References.md)** | Citations and glossary |

---

## Design Principles

### Standalone & Self-Contained
RL2 does not import or depend on external ODRL definitions. All constructs are defined natively.

### Normative Completeness
RL2 incorporates the full Hohfeldian framework: Privilege, Duty, Claim, Power, Liability, Immunity.

### Operational Semantics
Policies have stateful behavior. Duties follow a lifecycle: Pending → Active → Fulfilled/Violated. State can be queried via `obligationStateOperand` and `dutyPerformerOperand` to enable:
- **Duty state preconditions** — Privileges conditioned on prior duty fulfillment
- **Identity binding** — Tun-sollen (same agent) vs. Sein-sollen (any agent)
- **Separation of Duty** — Two-man rules requiring different agents

### Profile-Declared Operands
All runtime and contextual data access goes through declared `rl2:LeftOperand` instances with explicit resolution paths. This architectural principle ensures:
- **No ad-hoc vocabulary** — Profiles own domain-specific operands
- **Formal grounding** — All access maps to `resolve`/`deref` semantics
- **Type safety** — Operands declare expected ranges
- **Validation** — SHACL can verify operand usage and path roots

See **profiles/** for example profiles and **RL2_Semantics.md** for resolution semantics.

### RDF-native, SHACL-validated
The ontology is fully RDF/OWL, with SHACL shapes defining structural constraints.

### Mechanization-Ready
The semantics map directly to verification frameworks (Why3, K, Lean 4).

---

## References

See **[RL2_References.md](RL2_References.md)** for complete citations.

Key sources:
- [Hohfeld 1919] — Fundamental Legal Conceptions
- [DPCL] — Language Template for Normative Specifications
- [Promise Theory] — Burgess & Bergstra
- [ODRE] — Operational semantics for duty lifecycle
- [OWL 2], [SHACL], [RDF 1.1] — Semantic web foundations
