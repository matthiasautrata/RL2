---
title: "RL2 Evaluation Protocol"
subtitle: "A Companion Specification for Interoperable Policy Evaluation"
version: "0.6"
status: "Draft"
date: 2026-07-24
---

## Table of Contents

- Introduction
- Design Principles
- Request
- Evaluation Result
- Universal Requirement (Duties, Promises, Claims)
- Fulfillment as Context
- Case Lifecycle
- Context
- Decisions
- Worked Example
- Comparison with Other Standards
- References

---

# Introduction

This document defines the **RL2 Evaluation Protocol** — a standard format for:

* Submitting access requests to RL2 policy evaluators
* Receiving evaluation decisions with associated requirements (duties, promises, claims)
* Recording fulfillment evidence
* Tracking access cases through their complete lifecycle
* Enabling interoperability between independently implemented evaluators

The protocol is designed to be:

* **Implementation-agnostic**: Any language, any runtime
* **Serialization-flexible**: RDF/Turtle, JSON-LD, or other formats
* **Chainable**: Results from one evaluator can feed into the next
* **Auditable**: Complete provenance for compliance and governance

This specification complements RL2 Core (the policy ontology) and RL2 Semantics (the formal evaluation rules).

---

# Design Principles

## Separation of Concerns

| Specification | Scope |
|---------------|-------|
| **RL2 Core** | Policy structure: norms, conditions, agents, assets |
| **RL2 Semantics** | Evaluation rules: how to determine if a norm applies |
| **RL2 Protocol** | Request/response formats: interoperable data exchange |

## Immutability

* **Requests** are immutable once submitted
* **Cases** are append-only event logs
* **History** is never modified, only extended

## Event Sourcing

Cases are modeled as ordered sequences of events:

```
Request → Context Assertions → Evaluation → Requirements → Fulfillment Claims → Re-evaluation → ...
```

The complete state can be reconstructed from the event history.

## Provenance

Every evaluation result, requirement, and fulfillment claim includes:

* Timestamp
* Source reference (policy, agent, evidence)
* Linkage to the originating request

---

# Request

A **Request** represents a request to evaluate whether an action is permitted.

Note: Request is defined in RL2 Protocol, not RL2 Core. A request is a runtime artifact for policy evaluation, not a normative policy type.

## Ontology

```turtle
rl2p:Request a owl:Class ;
    rdfs:label "Request" ;
    rdfs:comment """A request to evaluate policy for a specific action.
    Defined in RL2 Protocol (not Core) as it is a runtime evaluation
    artifact, not a normative policy. Requests are immutable once created.""" .

rl2p:requestedAction a owl:ObjectProperty ;
    rdfs:domain rl2p:Request ;
    rdfs:range rl2:Action ;
    rdfs:comment "The action the requestor wishes to perform." .

rl2p:requestedAsset a owl:ObjectProperty ;
    rdfs:domain rl2p:Request ;
    rdfs:range rl2:Asset ;
    rdfs:comment "The asset on which the action would be performed." .

rl2p:requestingAgent a owl:ObjectProperty ;
    rdfs:domain rl2p:Request ;
    rdfs:range rl2:Agent ;
    rdfs:comment "The agent who would perform the action." .

rl2p:requestor a owl:ObjectProperty ;
    rdfs:domain rl2p:Request ;
    rdfs:range rl2:Agent ;
    rdfs:comment "The agent submitting this request (may differ from requestingAgent)." .

rl2p:requestTime a owl:DatatypeProperty ;
    rdfs:domain rl2p:Request ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When the request was submitted." .
```

**Note on Delegation:** When `requestor` differs from `requestingAgent`, validation of delegation authority is outside the scope of RL2. Implementations must authenticate requestors and verify delegation rights before policy evaluation.

## Example

```turtle
ex:request1 a rl2p:Request ;
    rl2p:requestedAction ex:accessLoanData ;
    rl2p:requestedAsset ex:LoanPortfolio ;
    rl2p:requestingAgent ex:Alice ;
    rl2p:requestor ex:AliceWorkstation ;
    rl2p:requestTime "2025-01-15T09:00:00Z"^^xsd:dateTime .
```

---

# Evaluation Result

An **EvaluationResult** represents the outcome of evaluating a request against policies.

## Ontology

```turtle
rl2p:EvaluationResult a owl:Class ;
    rdfs:label "Evaluation Result" ;
    rdfs:comment "The outcome of evaluating an access request against policies." .

rl2p:decision a owl:ObjectProperty ;
    rdfs:domain rl2p:EvaluationResult ;
    rdfs:range rl2p:Decision ;
    rdfs:comment "The access decision." .

rl2p:evaluatedRequest a owl:ObjectProperty ;
    rdfs:domain rl2p:EvaluationResult ;
    rdfs:range rl2p:Request ;
    rdfs:comment "The request that was evaluated." .

rl2p:activeRequirements a owl:ObjectProperty ;
    rdfs:domain rl2p:EvaluationResult ;
    rdfs:range rl2p:Requirement ;
    rdfs:comment "Requirements (from Duties, Promises, or Claims) that must be fulfilled." .

rl2p:matchedPolicies a owl:ObjectProperty ;
    rdfs:domain rl2p:EvaluationResult ;
    rdfs:range rl2:Policy ;
    rdfs:comment "Policies that were evaluated for this request." .

rl2p:matchedNorms a owl:ObjectProperty ;
    rdfs:domain rl2p:EvaluationResult ;
    rdfs:range rl2:Norm ;
    rdfs:comment "Specific norms (privileges, prohibitions) that matched." .

rl2p:evaluationTime a owl:DatatypeProperty ;
    rdfs:domain rl2p:EvaluationResult ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When the evaluation was performed." .

rl2p:explanation a owl:DatatypeProperty ;
    rdfs:domain rl2p:EvaluationResult ;
    rdfs:range xsd:string ;
    rdfs:comment "Human-readable explanation of the decision." .
```

## Example

```turtle
ex:request1 a rl2p:Request ;
    rl2p:requestedAction ex:accessLoanData ;
    rl2p:requestedAsset ex:LoanPortfolio ;
    rl2p:requestingAgent ex:Alice ;
    rl2p:requestTime "2025-01-15T09:00:00Z"^^xsd:dateTime .

ex:managerApprovalDuty a rl2:Duty ;
    rl2:subject ex:BobManager ; rl2:action ex:approve ; rl2:object ex:LoanPortfolio .

ex:loanAccessPolicy a rl2:Policy ;
    rl2:clause ex:loanAccessPrivilege , ex:managerApprovalDuty .

ex:dataQualityPromise a rl2:Promise ;
    rl2:promisor ex:DataProvider ; rl2:promisee ex:DataConsumer ;
    rl2:promisedState ex:qualityThresholdMet .

ex:dataOffer a rl2:Offer ;                 # Promises live in Offers, not Agreements
    rl2:grantor ex:DataProvider ; rl2:grantee ex:DataConsumer ;
    rl2:clause ex:dataQualityPromise .

ex:req1 a rl2p:Requirement ;
    rl2p:sourceNorm ex:managerApprovalDuty ;
    rl2p:sourcePolicy ex:loanAccessPolicy ;
    rl2p:requirementStatus rl2:Active ;
    rl2p:imposedTime "2025-01-15T09:00:01Z"^^xsd:dateTime .

ex:req2 a rl2p:Requirement ;
    rl2p:sourceNorm ex:dataQualityPromise ;
    rl2p:sourcePolicy ex:dataOffer ;
    rl2p:counterparty ex:DataConsumer ;
    rl2p:requirementStatus rl2:Pending ;
    rl2p:imposedTime "2025-01-15T09:00:01Z"^^xsd:dateTime .

ex:eval1 a rl2p:EvaluationResult ;
    rl2p:evaluatedRequest ex:request1 ;
    rl2p:decision rl2p:Permit ;
    rl2p:activeRequirements ex:req1 , ex:req2 ;
    rl2p:matchedPolicies ex:loanAccessPolicy ;
    rl2p:matchedNorms ex:loanAccessPrivilege ;
    rl2p:evaluationTime "2025-01-15T09:00:01Z"^^xsd:dateTime ;
    rl2p:explanation "Access permitted with 2 requirements to fulfill." .
```

---

# Universal Requirement (Duties, Promises, Claims)

A **Requirement** (`rl2p:Requirement`) is a universal structure for tracking all runtime obligations, regardless of their source (Duty, Promise, or Claim).

## The "Promise as Generator" Concept

RL2 distinguishes between two types of "ought":

1.  **Sein-Sollen (Ought-to-Be):** A required state of the world (invariant). Modeled as `rl2:Promise`.
2.  **Tun-Sollen (Ought-to-Do):** An action to achieve or restore that state. Modeled as `rl2:Duty`.

When the world deviates from a Promise's invariant (Sein-Sollen), the evaluator generates a remedial Duty (Tun-Sollen) to fix it. The Protocol tracks both as **Requirements**, distinguishing them by their `sourceNorm`.

## Hohfeldian Mapping

| Hohfeldian Norm | Runtime Meaning | Protocol Artifact |
|-----------------|-----------------|-------------------|
| Duty | "Must Do" | `rl2p:Requirement` (sourceNorm → Duty) |
| Promise | "Must Do" (Voluntary) | `rl2p:Requirement` (sourceNorm → Promise) |
| Claim | "Owed To" | `rl2p:Requirement` (with counterparty) |
| Privilege | "Can Do" | `rl2p:Decision` (Permit) |
| Power | "Can Change" | `rl2p:Decision` (Permit State Change) |
| Immunity | "Cannot Be Changed" | `rl2p:Decision` (Deny State Change) |

## Requirement Lifecycle

Requirement uses `rl2:ObligationState` from RL2 Core uniformly:

```
┌─────────┐    condition     ┌────────┐
│ Pending │───────────────▶│ Active │
└─────────┘      holds       └────────┘
                                │
             ┌────────────┴────────────┐
             │                         │
        performed                  timeout
             │                         │
             ▼                         ▼
       ┌───────────┐            ┌──────────┐
       │ Fulfilled │            │ Violated │
       └───────────┘            └──────────┘
```

**State Mapping Note:** See **RL2_Semantics.md** §Promise and duty states vs protocol requirement status for the canonical mapping. `rl2p:requirementStatus` always uses `rl2:ObligationState`; a promise effective now may surface as an `Active` requirement while its PromiseState remains `Pending`, and terminal states map directly.

## Ontology

```turtle
rl2p:Requirement a owl:Class ;
    rdfs:label "Requirement" ;
    rdfs:comment """A universal runtime obligation that must be fulfilled.
    Tracks Duties, Promises, and Claims at runtime.""" .

rl2p:sourceNorm a owl:ObjectProperty ;
    rdfs:domain rl2p:Requirement ;
    rdfs:comment """Reference to the norm or promise that created this requirement.
    Range: rl2:Norm | rl2:Promise.""" .

rl2p:sourcePolicy a owl:ObjectProperty ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range rl2:Policy ;
    rdfs:comment "The policy containing the norm that created this requirement." .

rl2p:counterparty a owl:ObjectProperty ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range rl2:Agent ;
    rdfs:comment """The agent who holds the correlative position (for Claims).
    When sourceNorm is a Duty, counterparty is the Claim holder.
    When sourceNorm is a Promise, counterparty is the promisee.""" .

rl2p:requirementStatus a owl:ObjectProperty ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range rl2:ObligationState ;
    rdfs:comment """Current lifecycle status of this requirement.
    Uses rl2:ObligationState (Pending, Active, Fulfilled, Violated).""" .

rl2p:imposedTime a owl:DatatypeProperty ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When this requirement was created/imposed." .

rl2p:fulfilledByAction a owl:ObjectProperty ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range rl2:Action ;
    rdfs:comment "The action that fulfilled this requirement (if fulfilled)." .

rl2p:fulfilledByEvent a owl:ObjectProperty ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range rl2:Event ;
    rdfs:comment "The event/log entry evidencing fulfillment of this requirement." .

rl2p:fulfillmentEvidence a owl:ObjectProperty ;
    rdfs:comment "Reference to evidence (document, signature, record) supporting fulfillment. Dual-use: Requirement (audit trail) and ContextAssertion (fulfillment-as-context, below); no rdfs:domain restriction." .

rl2p:requirementLabel a owl:DatatypeProperty ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range xsd:string ;
    rdfs:comment "Human-readable label for this requirement." .

rl2p:requirementDescription a owl:DatatypeProperty ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range xsd:string ;
    rdfs:comment "Human-readable description of what must be done." .
```

## Examples

**1. Standard Duty (Manager Approval)**
```turtle
ex:managerApprovalDuty a rl2:Duty ;
    rl2:subject ex:BobManager ; rl2:action ex:approve ; rl2:object ex:LoanPortfolio .

ex:loanAccessPolicy a rl2:Policy ;
    rl2:clause ex:managerApprovalDuty .

ex:req1 a rl2p:Requirement ;
    rl2p:sourceNorm ex:managerApprovalDuty ;
    rl2p:sourcePolicy ex:loanAccessPolicy ;
    rl2p:requirementStatus rl2:Active ;
    rl2p:imposedTime "2025-01-15T09:00:01Z"^^xsd:dateTime .
```

**2. Promise-sourced Requirement (Data Quality)**
```turtle
ex:dataQualityPromise a rl2:Promise ;
    rl2:promisor ex:DataProvider ; rl2:promisee ex:DataConsumer ;
    rl2:promisedState ex:qualityThresholdMet .

ex:dataOffer a rl2:Offer ;                 # Promises live in Offers, not Agreements
    rl2:grantor ex:DataProvider ; rl2:grantee ex:DataConsumer ;
    rl2:clause ex:dataQualityPromise .

ex:req2 a rl2p:Requirement ;
    rl2p:sourceNorm ex:dataQualityPromise ;  # The promise itself
    rl2p:sourcePolicy ex:dataOffer ;
    rl2p:counterparty ex:DataConsumer ;       # The promisee (Claim holder)
    rl2p:requirementStatus rl2:Pending ;
    rl2p:imposedTime "2025-01-15T09:00:01Z"^^xsd:dateTime .
```

---

# Fulfillment as Context

Requirement fulfillment is modeled as **context assertions**. This provides a uniform pattern: all facts relevant to evaluation—whether about agents, assets, or requirement completion—are context assertions referencing the request.

## Pattern

A fulfillment assertion uses:
- `rl2p:contextSubject` → the requirement
- `rl2p:contextProperty` → `rl2p:requirementFulfilled` (a left operand)
- `rl2p:contextValue` → `"true"` or evidence reference

## Vocabulary

```turtle
rl2p:requirementFulfilled a rl2:LeftOperand ;
    rdfs:label "Requirement Fulfilled" ;
    rdfs:comment "Left operand indicating requirement fulfillment status." .
```

`rl2p:fulfillmentEvidence` is defined above under Universal Requirement; it is domain-unrestricted, so it applies equally here on `rl2p:ContextAssertion`.

## Example

```turtle
ex:request1 a rl2p:Request ;
    rl2p:requestedAction ex:accessLoanData ;
    rl2p:requestedAsset ex:LoanPortfolio ;
    rl2p:requestingAgent ex:Alice ;
    rl2p:requestTime "2025-01-15T09:00:00Z"^^xsd:dateTime .

# Manager approval fulfillment - as context assertion
ex:fulfillment1 a rl2p:ContextAssertion ;
    rl2p:forRequest ex:request1 ;
    rl2p:contextSubject ex:req1 ;
    rl2p:contextProperty rl2p:requirementFulfilled ;
    rl2p:contextValue "true"^^xsd:boolean ;
    rl2p:fulfillmentEvidence ex:approvalEmail123 ;
    rl2p:assertedTime "2025-01-15T10:30:00Z"^^xsd:dateTime ;
    rl2p:assertedBy ex:BobManager ;
    rl2p:performer ex:BobManager .
```

---

# Case Lifecycle

A **Case** tracks the complete lifecycle of an access request from submission through enforcement and expiration.

## Ontology

```turtle
rl2p:Case a owl:Class ;
    rdfs:label "Case" ;
    rdfs:comment """An access case that evolves through evaluation, fulfillment, and enforcement.
    Cases are append-only event logs providing complete audit trails.""" .

rl2p:initialRequest a owl:ObjectProperty ;
    rdfs:domain rl2p:Case ;
    rdfs:range rl2p:Request ;
    rdfs:comment "The original request that created this case." .

rl2p:evaluationHistory a owl:ObjectProperty ;
    rdfs:domain rl2p:Case ;
    rdfs:range rl2p:EvaluationResult ;
    rdfs:comment "All evaluations performed for this case (ordered by time)." .

rl2p:caseStatus a owl:ObjectProperty ;
    rdfs:domain rl2p:Case ;
    rdfs:range rl2p:CaseStatus ;
    rdfs:comment "Current status of the case." .

rl2p:CaseStatus a owl:Class ;
    owl:oneOf (rl2p:CasePending rl2p:Approved rl2p:Denied rl2p:Expired rl2p:Revoked) .

rl2p:CasePending a rl2p:CaseStatus ;
    rdfs:label "Pending" ;
    rdfs:comment "Access request is under evaluation or awaiting duty fulfillment." .

rl2p:Approved a rl2p:CaseStatus ;
    rdfs:label "Approved" ;
    rdfs:comment "Access has been granted and all duties fulfilled." .

rl2p:Denied a rl2p:CaseStatus ;
    rdfs:label "Denied" ;
    rdfs:comment "Access has been denied by policy." .

rl2p:Expired a rl2p:CaseStatus ;
    rdfs:label "Expired" ;
    rdfs:comment "Access grant has expired and requires re-certification." .

rl2p:Revoked a rl2p:CaseStatus ;
    rdfs:label "Revoked" ;
    rdfs:comment "Access has been explicitly revoked." .

rl2p:caseCreated a owl:DatatypeProperty ;
    rdfs:domain rl2p:Case ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When the case was created." .

rl2p:expirationTime a owl:DatatypeProperty ;
    rdfs:domain rl2p:Case ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When the access grant expires (if approved)." .

rl2p:caseNote a owl:DatatypeProperty ;
    rdfs:domain rl2p:Case ;
    rdfs:range xsd:string ;
    rdfs:comment "Administrative notes on the case." .

rl2p:policyGeneration a owl:DatatypeProperty ;
    rdfs:domain rl2p:Case ;
    rdfs:range xsd:anyURI ;
    rdfs:comment """The policy generation under which this case is evaluated.
    Once set at case creation, the generation is immutable for that case.
    This ensures reproducible evaluation and clear auditability.""" .
```

**Policy Generation Binding**: At case creation, the evaluator sets `rl2p:policyGeneration` from its current generation identifier. This generation determines the PolicyUniverse U for all evaluations of that case. Future evaluations use the same generation unless an explicit migration workflow is invoked (outside RL2 scope). This ensures:

- **Reproducibility**: Same case + same generation = same evaluation
- **Auditability**: The policy universe is always identifiable
- **Grandfather clauses**: Old cases continue under old rules until explicitly migrated

## Case State Transitions

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐ │
│ Request │───▶│ Pending │───▶│ Approved │───▶│ Expired │─┘
└─────────┘    └─────────┘    └──────────┘    └─────────┘
                    │              │
                    │              │
                    ▼              ▼
               ┌─────────┐   ┌─────────┐
               │ Denied  │   │ Revoked │
               └─────────┘   └─────────┘
```

Transitions:
* **Request → Pending**: Case created from access request
* **Pending → Approved**: All duties fulfilled, evaluation permits
* **Pending → Denied**: Evaluation denies (prohibition or unfulfillable duties)
* **Approved → Expired**: Expiration time reached
* **Approved → Revoked**: Explicit revocation
* **Expired → Pending**: Re-certification initiated (new evaluation cycle)

---

# Re-evaluation Triggers

Policy evaluation is triggered when the evaluation context changes. This ensures dynamic policy applicability: as events occur, different policies may become applicable to the case.

## Trigger Events

1. **Initial request** → first evaluation
2. **Context assertion arrival** → facts about agents/assets change
3. **Requirement fulfillment claim** → requirement states update
4. **Time advancement** → temporal conditions may change
5. **Any event modifying Σ** → may activate/deactivate policies

> **Key principle**: Any event that modifies Σ triggers re-evaluation of the applicable policy set, not just duty-related events.

## Policy Activation via Events

When an event enters Σ, policies with EventConstraint conditions may become applicable:

```
Event arrives → Σ.Events updated →
  ApplicablePolicies(U, Env) recomputed →
    New requirements may activate
```

This models workflows where external events (e.g., committee approval) trigger additional policy requirements without branching the duty lifecycle.

---

# Context

**Context** represents facts about the environment, agents, and assets used during evaluation.

## Ontology

```turtle
rl2p:ContextAssertion a owl:Class ;
    rdfs:label "Context Assertion" ;
    rdfs:comment """A contextual fact provided for policy evaluation.
    Context assertions reference the request they belong to, allowing
    facts to arrive from different systems at different times.
    Duty fulfillment evidence is modeled as context assertions.""" .

rl2p:forRequest a owl:ObjectProperty ;
    rdfs:domain rl2p:ContextAssertion ;
    rdfs:range rl2p:Request ;
    rdfs:comment "The request this assertion provides context for." .

rl2p:contextSubject a owl:ObjectProperty ;
    rdfs:domain rl2p:ContextAssertion ;
    rdfs:comment "The subject of the assertion (typically an agent or asset)." .

rl2p:contextProperty a owl:ObjectProperty ;
    rdfs:domain rl2p:ContextAssertion ;
    rdfs:range rl2:LeftOperand ;
    rdfs:comment "The property being asserted (a left operand)." .

rl2p:contextValue a owl:DatatypeProperty ;
    rdfs:domain rl2p:ContextAssertion ;
    rdfs:comment "The value of the property (literal)." .

rl2p:contextValueRef a owl:ObjectProperty ;
    rdfs:domain rl2p:ContextAssertion ;
    rdfs:comment "The value of the property (resource reference)." .

rl2p:assertedTime a owl:DatatypeProperty ;
    rdfs:domain rl2p:ContextAssertion ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When this assertion was made." .

rl2p:assertedBy a owl:ObjectProperty ;
    rdfs:domain rl2p:ContextAssertion ;
    rdfs:range rl2:Agent ;
    rdfs:comment "The agent or system that made this assertion." .
```

## Example

```turtle
ex:request1 a rl2p:Request ;
    rl2p:requestedAction ex:accessLoanData ;
    rl2p:requestedAsset ex:LoanPortfolio ;
    rl2p:requestingAgent ex:Alice ;
    rl2p:requestTime "2025-01-15T09:00:00Z"^^xsd:dateTime .

# Multiple assertions can reference the same request
ex:ctx1 a rl2p:ContextAssertion ;
    rl2p:forRequest ex:request1 ;
    rl2p:contextSubject ex:Alice ;
    rl2p:contextProperty ex:department ;
    rl2p:contextValueRef ex:AutoFinance ;
    rl2p:assertedTime "2025-01-15T09:00:00Z"^^xsd:dateTime ;
    rl2p:assertedBy ex:HRSystem .

ex:ctx2 a rl2p:ContextAssertion ;
    rl2p:forRequest ex:request1 ;
    rl2p:contextSubject ex:Alice ;
    rl2p:contextProperty ex:securityClearance ;
    rl2p:contextValue "Level2" ;
    rl2p:assertedTime "2025-01-15T09:00:00Z"^^xsd:dateTime ;
    rl2p:assertedBy ex:SecuritySystem .
```

---

# Decisions

## Ontology

```turtle
rl2p:Decision a owl:Class ;
    rdfs:label "Decision" ;
    rdfs:comment "The outcome of a policy evaluation." ;
    owl:oneOf (rl2p:Permit rl2p:PermitWithObligations rl2p:Deny rl2p:Indeterminate rl2p:NotApplicable) .

rl2p:Permit a rl2p:Decision ;
    rdfs:label "Permit" ;
    rdfs:comment "Access is permitted unconditionally (no outstanding duties)." .

rl2p:PermitWithObligations a rl2p:Decision ;
    rdfs:label "Permit with Obligations" ;
    rdfs:comment "Access is permitted contingent on fulfillment of associated duties." .

rl2p:Deny a rl2p:Decision ;
    rdfs:label "Deny" ;
    rdfs:comment "Access is denied by policy." .

rl2p:Indeterminate a rl2p:Decision ;
    rdfs:label "Indeterminate" ;
    rdfs:comment "Evaluation could not reach a decision (e.g., missing information)." .

rl2p:NotApplicable a rl2p:Decision ;
    rdfs:label "Not Applicable" ;
    rdfs:comment "No policies apply to this request." .
```

## Decision Semantics

| Decision | Meaning | Requirements |
|----------|---------|--------|
| **Permit** | Access granted unconditionally | No outstanding requirements |
| **PermitWithObligations** | Access granted contingent on fulfillment | Has requirements; all must be fulfilled |
| **Deny** | Access denied | N/A |
| **Indeterminate** | Cannot decide | Missing context or evaluation error |
| **NotApplicable** | No matching policy | Request falls outside policy scope |

**Semantic Correspondence**: At the semantic level (RL2_Semantics.md), `Eval` returns `(Decision, State, DutySet)`. The Protocol lifts `PermitWithObligations` into a first-class decision to make contingent permits explicitly visible to consuming systems. Specifically:
- Semantic `Permit` + empty `DutySet` → Protocol `rl2p:Permit`
- Semantic `Permit` + non-empty `DutySet` → Protocol `rl2p:PermitWithObligations` + `activeRequirements`

---

# Worked Example

This example demonstrates the complete lifecycle described in the introduction:

1. User requests access to resource with context
2. Evaluator renders decision with possible requirements (duties)
3. Fulfillment claims are added (case history/provenance)
4. Case is re-evaluated and fully approved
5. Fully approved decision is handed to entitlements system
6. After some time, access expires with creation of a new requirement

## Domain Vocabulary (Profile)

```turtle
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix rl2p: <https://rl2.example/protocol#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# Actions (domain-specific)
ex:accessLoanData a rl2:Action ;
    rdfs:label "Access Loan Data" .

ex:recertifyAccess a rl2:Action ;
    rdfs:label "Recertify Access" .

# Left Operands (domain-specific)
ex:department a rl2:LeftOperand ;
    rdfs:label "Department" .

# Agents
ex:Alice a rl2:Agent ;
    rdfs:label "Alice" .

ex:BobManager a rl2:Agent ;
    rdfs:label "Bob (Manager)" .

ex:HRSystem a rl2:Agent ;
    rdfs:label "HR System" .

ex:EntitlementsSystem a rl2:Agent ;
    rdfs:label "Entitlements System" .

# Assets
ex:LoanPortfolio a rl2:Asset ;
    rdfs:label "Loan Portfolio Dataset" .

# Organizational Unit
ex:AutoFinance a ex:Department ;
    rdfs:label "Auto Finance Department" .
```

## Step 1: User Requests Access

```turtle
# Alice requests access to loan data
ex:request1 a rl2p:Request ;
    rl2p:requestedAction ex:accessLoanData ;
    rl2p:requestedAsset ex:LoanPortfolio ;
    rl2p:requestingAgent ex:Alice ;
    rl2p:requestor ex:Alice ;
    rl2p:requestTime "2025-01-15T09:00:00Z"^^xsd:dateTime .

# Context: Alice is in the AutoFinance department
ex:ctx1 a rl2p:ContextAssertion ;
    rl2p:forRequest ex:request1 ;
    rl2p:contextSubject ex:Alice ;
    rl2p:contextProperty ex:department ;
    rl2p:contextValueRef ex:AutoFinance ;
    rl2p:assertedTime "2025-01-15T09:00:00Z"^^xsd:dateTime ;
    rl2p:assertedBy ex:HRSystem .

# Case is created
ex:case1 a rl2p:Case ;
    rl2p:initialRequest ex:request1 ;
    rl2p:caseStatus rl2p:CasePending ;
    rl2p:caseCreated "2025-01-15T09:00:00Z"^^xsd:dateTime .
```

## Step 2: Evaluator Renders Decision with Requirements

```turtle
ex:request1 a rl2p:Request ;
    rl2p:requestedAction ex:accessLoanData ;
    rl2p:requestedAsset ex:LoanPortfolio ;
    rl2p:requestingAgent ex:Alice ;
    rl2p:requestTime "2025-01-15T09:00:00Z"^^xsd:dateTime .

ex:managerApprovalDuty a rl2:Norm .
ex:dataHandlingTrainingDuty a rl2:Norm .

ex:loanAccessPolicy a rl2:Policy ;
    rl2:clause ex:loanAccessPrivilege , ex:managerApprovalDuty , ex:dataHandlingTrainingDuty .

# Initial evaluation: Permit with requirements
ex:eval1 a rl2p:EvaluationResult ;
    rl2p:evaluatedRequest ex:request1 ;
    rl2p:decision rl2p:PermitWithObligations ;
    rl2p:activeRequirements ex:req1 , ex:req2 ;
    rl2p:matchedPolicies ex:loanAccessPolicy ;
    rl2p:matchedNorms ex:loanAccessPrivilege ;
    rl2p:evaluationTime "2025-01-15T09:00:01Z"^^xsd:dateTime ;
    rl2p:explanation "Access permitted. 2 requirements must be fulfilled." .

# Requirement 1: Manager Approval (Active - condition met, awaiting fulfillment)
ex:req1 a rl2p:Requirement ;
    rl2p:sourceNorm ex:managerApprovalDuty ;
    rl2p:sourcePolicy ex:loanAccessPolicy ;
    rl2p:requirementLabel "Manager Approval" ;
    rl2p:requirementDescription "Obtain approval from department manager." ;
    rl2p:requirementStatus rl2:Active ;
    rl2p:imposedTime "2025-01-15T09:00:01Z"^^xsd:dateTime .

# Requirement 2: Data Handling Training (Pending - waiting for training window to open)
ex:req2 a rl2p:Requirement ;
    rl2p:sourceNorm ex:dataHandlingTrainingDuty ;
    rl2p:sourcePolicy ex:loanAccessPolicy ;
    rl2p:requirementLabel "Data Handling Training" ;
    rl2p:requirementDescription "Complete data handling certification course." ;
    rl2p:requirementStatus rl2:Pending ;
    rl2p:imposedTime "2025-01-15T09:00:01Z"^^xsd:dateTime .

# Case created and updated with evaluation
ex:case1 a rl2p:Case ;
    rl2p:initialRequest ex:request1 ;
    rl2p:caseStatus rl2p:CasePending ;
    rl2p:caseCreated "2025-01-15T09:00:00Z"^^xsd:dateTime ;
    rl2p:evaluationHistory ex:eval1 .
```

## Step 3: Fulfillment Context Added

```turtle
ex:request1 a rl2p:Request ;
    rl2p:requestedAction ex:accessLoanData ;
    rl2p:requestedAsset ex:LoanPortfolio ;
    rl2p:requestingAgent ex:Alice ;
    rl2p:requestTime "2025-01-15T09:00:00Z"^^xsd:dateTime .

# Manager approves - fulfillment as context assertion
ex:fulfillment1 a rl2p:ContextAssertion ;
    rl2p:forRequest ex:request1 ;
    rl2p:contextSubject ex:req1 ;
    rl2p:contextProperty rl2p:requirementFulfilled ;
    rl2p:contextValue "true"^^xsd:boolean ;
    rl2p:fulfillmentEvidence ex:approvalEmail123 ;
    rl2p:performer ex:BobManager ;
    rl2p:assertedTime "2025-01-15T10:30:00Z"^^xsd:dateTime ;
    rl2p:assertedBy ex:BobManager .

# Alice completes training - fulfillment as context assertion
ex:fulfillment2 a rl2p:ContextAssertion ;
    rl2p:forRequest ex:request1 ;
    rl2p:contextSubject ex:req2 ;
    rl2p:contextProperty rl2p:requirementFulfilled ;
    rl2p:contextValue "true"^^xsd:boolean ;
    rl2p:fulfillmentEvidence ex:trainingCertificate456 ;
    rl2p:performer ex:Alice ;
    rl2p:assertedTime "2025-01-15T14:00:00Z"^^xsd:dateTime ;
    rl2p:assertedBy ex:Alice .
```

## Step 4: Re-evaluation with Full Approval

```turtle
ex:request1 a rl2p:Request ;
    rl2p:requestedAction ex:accessLoanData ;
    rl2p:requestedAsset ex:LoanPortfolio ;
    rl2p:requestingAgent ex:Alice ;
    rl2p:requestTime "2025-01-15T09:00:00Z"^^xsd:dateTime .

ex:loanAccessPolicy a rl2:Policy ;
    rl2:clause ex:loanAccessPrivilege .

# First evaluation, referenced in the case's evaluationHistory below
ex:eval1 a rl2p:EvaluationResult ;
    rl2p:evaluatedRequest ex:request1 ;
    rl2p:evaluationTime "2025-01-15T09:00:01Z"^^xsd:dateTime ;
    rl2p:decision rl2p:PermitWithObligations .

# Re-evaluation after requirements fulfilled
# Note: activeRequirements is omitted when all requirements are fulfilled
ex:eval2 a rl2p:EvaluationResult ;
    rl2p:evaluatedRequest ex:request1 ;
    rl2p:decision rl2p:Permit ;
    rl2p:matchedPolicies ex:loanAccessPolicy ;
    rl2p:matchedNorms ex:loanAccessPrivilege ;
    rl2p:evaluationTime "2025-01-15T14:05:00Z"^^xsd:dateTime ;
    rl2p:explanation "Access permitted. All requirements fulfilled." .

# Case status updated
ex:case1 a rl2p:Case ;
    rl2p:initialRequest ex:request1 ;
    rl2p:caseCreated "2025-01-15T09:00:00Z"^^xsd:dateTime ;
    rl2p:evaluationHistory ex:eval1 , ex:eval2 ;
    rl2p:caseStatus rl2p:Approved ;
    rl2p:expirationTime "2026-01-15T09:00:00Z"^^xsd:dateTime .
```

## Step 5: Handoff to Entitlements System

```turtle
# The entitlements system receives the approved case
# All context assertions (including fulfillment) reference the request
# The evaluator can query: all ContextAssertions where forRequest = ex:request1

# The entitlements system can verify:
# - ex:case1 rl2p:caseStatus rl2p:Approved
# - All requirements in ex:eval2 rl2p:activeRequirements are empty
# - Fulfillment evidence via context assertions (ex:fulfillment1, ex:fulfillment2)
# - Expiration: 2026-01-15

# Then provision access accordingly
ex:accessGrant1 a ex:AccessGrant ;
    ex:grantedFor ex:case1 ;
    ex:grantedTo ex:Alice ;
    ex:grantedAsset ex:LoanPortfolio ;
    ex:grantedBy ex:EntitlementsSystem ;
    ex:grantTime "2025-01-15T14:10:00Z"^^xsd:dateTime ;
    ex:expiresAt "2026-01-15T09:00:00Z"^^xsd:dateTime .
```

## Step 6: Expiration Creates Re-certification Requirement

```turtle
# One year later: access expires
# (This could be triggered by a scheduler or temporal event)

ex:request1 a rl2p:Request ;
    rl2p:requestedAction ex:accessLoanData ;
    rl2p:requestedAsset ex:LoanPortfolio ;
    rl2p:requestingAgent ex:Alice ;
    rl2p:requestTime "2025-01-15T09:00:00Z"^^xsd:dateTime .

ex:expirationEvent a rl2:Event ;
    rl2p:affectsCase ex:case1 ;
    rl2:eventTime "2026-01-15T09:00:00Z"^^xsd:dateTime .

# Case status updated
ex:case1 a rl2p:Case ;
    rl2p:initialRequest ex:request1 ;
    rl2p:caseCreated "2025-01-15T09:00:00Z"^^xsd:dateTime ;
    rl2p:caseStatus rl2p:Expired .

# Re-certification requirement is created (could be a new case or extension)
ex:recertCase1 a rl2p:Case ;
    rl2p:initialRequest ex:recertRequest1 ;
    rl2p:caseStatus rl2p:CasePending ;
    rl2p:caseCreated "2026-01-15T09:00:00Z"^^xsd:dateTime ;
    rl2p:caseNote "Re-certification required for expired access grant." .

ex:recertRequest1 a rl2p:Request ;
    rl2p:requestedAction ex:recertifyAccess ;
    rl2p:requestedAsset ex:LoanPortfolio ;
    rl2p:requestingAgent ex:Alice ;
    rl2p:requestTime "2026-01-15T09:00:00Z"^^xsd:dateTime .
```

---

# Comparison with Other Standards

| Feature | XACML | ODRL | RL2 Protocol |
|---------|-------|------|--------------|
| Request format | ✓ XML-based | ✓ RDF-based | ✓ RDF-based |
| Response format | ✓ XML-based | ✓ (informal) | ✓ RDF-based |
| Obligations/Duties | ✓ Fire-and-forget | ✓ State machine | ✓ Universal Requirement |
| Fulfillment evidence | ✗ | ✗ | ✓ ContextAssertion |
| Case lifecycle | ✗ (stateless) | ✗ | ✓ Case with history |
| Provenance chain | ✗ | Partial (existingReport) | ✓ Context assertions |
| Expiration/renewal | ✗ | Partial | ✓ CaseStatus + Events |
| Interop handoff | ✗ | ✗ | ✓ Case is portable |

### Key Differences

**vs XACML**: XACML is stateless — each request is independent. RL2 Protocol tracks the complete case lifecycle with fulfillment evidence and can hand off approved cases to downstream systems.

**vs ODRL**: ODRL's formal semantics define `existingReport` for history but don't standardize the format. RL2 Protocol provides a complete, interoperable format for requests, results, fulfillment claims, and cases.

---

# References

See **RL2_References.md** for complete citations and glossary.

RL2 Specifications:
* rl2.ttl — Core ontology (OWL)
* rl2-shacl.ttl — SHACL validation shapes
* RL2_Semantics.md — Formal evaluation semantics

Key external sources:
* [XACML 3.0] — PDP/PEP architecture
* [OB-XACML] — Obligation handling patterns
* [ODRL 2.2 Model], [ODRL Formal Semantics] — Policy language foundations
