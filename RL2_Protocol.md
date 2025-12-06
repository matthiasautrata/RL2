---
title: "RL2 Evaluation Protocol"
subtitle: "A Companion Specification for Interoperable Policy Evaluation"
version: "0.4"
status: "Draft"
date: 2025-01-05
---

## Table of Contents

- Introduction
- Design Principles
- Request
- Evaluation Result
- Duty Requirement
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
* Receiving evaluation decisions with associated duties
* Recording duty fulfillment evidence
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
Request → Context Assertions → Evaluation → Duty Requirements → Fulfillment Claims → Re-evaluation → ...
```

The complete state can be reconstructed from the event history.

## Provenance

Every evaluation result, duty requirement, and fulfillment claim includes:

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

rl2p:activeDuties a owl:ObjectProperty ;
    rdfs:domain rl2p:EvaluationResult ;
    rdfs:range rl2p:DutyRequirement ;
    rdfs:comment "Duties that must be fulfilled for access to proceed or continue." .

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
ex:eval1 a rl2p:EvaluationResult ;
    rl2p:evaluatedRequest ex:request1 ;
    rl2p:decision rl2p:Permit ;
    rl2p:activeDuties ex:dutyReq1 , ex:dutyReq2 ;
    rl2p:matchedPolicies ex:loanAccessPolicy ;
    rl2p:matchedNorms ex:loanAccessPrivilege ;
    rl2p:evaluationTime "2025-01-15T09:00:01Z"^^xsd:dateTime ;
    rl2p:explanation "Access permitted with 2 duties required." .
```

---

# Duty Requirement

A **DutyRequirement** represents a duty imposed by policy evaluation.

## Duty Lifecycle States

DutyRequirement uses `rl2:ObligationState` from RL2 Core directly, ensuring semantic alignment:

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

The states are defined in RL2 Core (`rl2:Pending`, `rl2:Active`, `rl2:Fulfilled`, `rl2:Violated`) and used directly here via the `rl2p:dutyStatus` property.

## Ontology

```turtle
rl2p:DutyRequirement a owl:Class ;
    rdfs:label "Duty Requirement" ;
    rdfs:comment """A duty that must be fulfilled as a condition of access.
    Captures the duty definition at the time of evaluation for audit purposes.""" .

rl2p:requiresDuty a owl:ObjectProperty ;
    rdfs:domain rl2p:DutyRequirement ;
    rdfs:range rl2:Duty ;
    rdfs:comment "Reference to the duty definition in the policy." .

rl2p:sourcePolicy a owl:ObjectProperty ;
    rdfs:domain rl2p:DutyRequirement ;
    rdfs:range rl2:Policy ;
    rdfs:comment "The policy that imposed this duty." .

rl2p:dutyStatus a owl:ObjectProperty ;
    rdfs:domain rl2p:DutyRequirement ;
    rdfs:range rl2:ObligationState ;
    rdfs:comment """Current lifecycle status of this duty requirement.
    Uses rl2:ObligationState from RL2 Core (Pending, Active, Fulfilled, Violated)
    to ensure semantic alignment between the ontology and protocol.""" .

rl2p:imposedTime a owl:DatatypeProperty ;
    rdfs:domain rl2p:DutyRequirement ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When this duty requirement was imposed." .

rl2p:fulfilledByAction a owl:ObjectProperty ;
    rdfs:domain rl2p:DutyRequirement ;
    rdfs:range rl2:Action ;
    rdfs:comment "The action that fulfilled this duty requirement (if fulfilled)." .

rl2p:fulfilledByEvent a owl:ObjectProperty ;
    rdfs:domain rl2p:DutyRequirement ;
    rdfs:range rl2:Event ;
    rdfs:comment "The event/log entry evidencing fulfillment of this duty requirement." .

rl2p:fulfillmentEvidence a owl:ObjectProperty ;
    rdfs:domain rl2p:DutyRequirement ;
    rdfs:comment "Reference to evidence (document, signature, record) supporting fulfillment." .

rl2p:dutyLabel a owl:DatatypeProperty ;
    rdfs:domain rl2p:DutyRequirement ;
    rdfs:range xsd:string ;
    rdfs:comment "Human-readable label for the duty requirement." .

rl2p:dutyDescription a owl:DatatypeProperty ;
    rdfs:domain rl2p:DutyRequirement ;
    rdfs:range xsd:string ;
    rdfs:comment "Human-readable description of what the duty requires." .
```

## Example

```turtle
ex:dutyReq1 a rl2p:DutyRequirement ;
    rl2p:requiresDuty ex:managerApprovalDuty ;
    rl2p:sourcePolicy ex:loanAccessPolicy ;
    rl2p:dutyStatus rl2:Active ;  # Activation condition has been met; duty must be performed
    rl2p:imposedTime "2025-01-15T09:00:01Z"^^xsd:dateTime .

# After fulfillment:
# ex:dutyReq1
#     rl2p:dutyStatus rl2:Fulfilled ;
#     rl2p:fulfilledByAction ex:approveLoan ;
#     rl2p:fulfilledByEvent ex:managerApprovalEvent ;
#     rl2p:fulfillmentEvidence ex:approvalRecord123 .

# Human-readable labels are available via the linked duty:
# ex:managerApprovalDuty rdfs:label "Manager Approval" ;
#     rdfs:comment "Obtain approval from department manager before accessing loan data." .
```

## Duty Set Enrichment

When the semantic `Eval()` function returns a `DutySet`, each `Duty` must be transformed into a `DutyRequirement` for the protocol response:

```
enrich : (Duty, Policy, State, Timestamp) → DutyRequirement

enrich(d, P, Σ, t) =
    DutyRequirement where
        requiresDuty = d
        sourcePolicy = P
        dutyStatus   = Σ.ObligationState(d)
        imposedTime  = t
```

This transformation:
1. **Links to the source duty** via `rl2p:requiresDuty`
2. **Records provenance** via `rl2p:sourcePolicy`
3. **Captures current status** from the evaluation state
4. **Timestamps the imposition** using the evaluation time

---

# Fulfillment as Context

Duty fulfillment is modeled as **context assertions** about duties. This provides a uniform pattern: all facts relevant to evaluation—whether about agents, assets, or duty completion—are context assertions referencing the request.

## Pattern

A fulfillment assertion uses:
- `rl2p:contextSubject` → the duty requirement
- `rl2p:contextProperty` → `rl2p:dutyFulfilled` (a left operand for fulfillment status)
- `rl2p:contextValue` → `"true"` or evidence reference

## Vocabulary

```turtle
rl2p:dutyFulfilled a rl2:LeftOperand ;
    rdfs:label "Duty Fulfilled" ;
    rdfs:comment "Left operand indicating duty fulfillment status." .

rl2p:fulfillmentEvidence a owl:ObjectProperty ;
    rdfs:domain rl2p:ContextAssertion ;
    rdfs:comment "Reference to evidence (document, signature, log entry, approval record)." .
```

## Example

```turtle
# Manager approval fulfillment - as context assertion
ex:fulfillment1 a rl2p:ContextAssertion ;
    rl2p:forRequest ex:request1 ;
    rl2p:contextSubject ex:dutyReq1 ;
    rl2p:contextProperty rl2p:dutyFulfilled ;
    rl2p:contextValue "true"^^xsd:boolean ;
    rl2p:fulfillmentEvidence ex:approvalEmail123 ;
    rl2p:assertedTime "2025-01-15T10:30:00Z"^^xsd:dateTime ;
    rl2p:assertedBy ex:BobManager .
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
3. **Duty fulfillment claim** → duty states update
4. **Time advancement** → temporal conditions may change
5. **Any event modifying Σ** → may activate/deactivate policies

> **Key principle**: Any event that modifies Σ triggers re-evaluation of the applicable policy set, not just duty-related events.

## Policy Activation via Events

When an event enters Σ, policies with EventConstraint conditions may become applicable:

```
Event arrives → Σ.Events updated →
  ApplicablePolicies(U, Env) recomputed →
    New duties may activate
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

| Decision | Meaning | Duties |
|----------|---------|--------|
| **Permit** | Access granted unconditionally | No outstanding duties |
| **PermitWithObligations** | Access granted contingent on duty fulfillment | Has duties; all must be fulfilled |
| **Deny** | Access denied | N/A |
| **Indeterminate** | Cannot decide | Missing context or evaluation error |
| **NotApplicable** | No matching policy | Request falls outside policy scope |

---

# Worked Example

This example demonstrates the complete lifecycle described in the introduction:

1. User requests access to resource with context
2. Evaluator renders decision with possible duties
3. Duty-fulfillment claims are added (case history/provenance)
4. Case is re-evaluated and fully approved
5. Fully approved decision is handed to entitlements system
6. After some time, access expires with creation of a new duty

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

## Step 2: Evaluator Renders Decision with Duties

```turtle
# Initial evaluation: Permit with duties
ex:eval1 a rl2p:EvaluationResult ;
    rl2p:evaluatedRequest ex:request1 ;
    rl2p:decision rl2p:Permit ;
    rl2p:activeDuties ex:dutyReq1 , ex:dutyReq2 ;
    rl2p:matchedPolicies ex:loanAccessPolicy ;
    rl2p:matchedNorms ex:loanAccessPrivilege ;
    rl2p:evaluationTime "2025-01-15T09:00:01Z"^^xsd:dateTime ;
    rl2p:explanation "Access permitted. 2 duties must be fulfilled." .

# Duty 1: Manager Approval (Active - condition met, awaiting fulfillment)
ex:dutyReq1 a rl2p:DutyRequirement ;
    rl2p:requiresDuty ex:managerApprovalDuty ;
    rl2p:sourcePolicy ex:loanAccessPolicy ;
    rl2p:dutyLabel "Manager Approval" ;
    rl2p:dutyDescription "Obtain approval from department manager." ;
    rl2p:dutyStatus rl2:Active ;
    rl2p:imposedTime "2025-01-15T09:00:01Z"^^xsd:dateTime .

# Duty 2: Data Handling Training (Pending - waiting for training window to open)
ex:dutyReq2 a rl2p:DutyRequirement ;
    rl2p:requiresDuty ex:dataHandlingTrainingDuty ;
    rl2p:sourcePolicy ex:loanAccessPolicy ;
    rl2p:dutyLabel "Data Handling Training" ;
    rl2p:dutyDescription "Complete data handling certification course." ;
    rl2p:dutyStatus rl2:Pending ;
    rl2p:imposedTime "2025-01-15T09:00:01Z"^^xsd:dateTime .

# Case updated with evaluation
ex:case1 rl2p:evaluationHistory ex:eval1 .
```

## Step 3: Duty Fulfillment Context Added

```turtle
# Manager approves - fulfillment as context assertion
ex:fulfillment1 a rl2p:ContextAssertion ;
    rl2p:forRequest ex:request1 ;
    rl2p:contextSubject ex:dutyReq1 ;
    rl2p:contextProperty rl2p:dutyFulfilled ;
    rl2p:contextValue "true"^^xsd:boolean ;
    rl2p:fulfillmentEvidence ex:approvalEmail123 ;
    rl2p:assertedTime "2025-01-15T10:30:00Z"^^xsd:dateTime ;
    rl2p:assertedBy ex:BobManager .

# Alice completes training - fulfillment as context assertion
ex:fulfillment2 a rl2p:ContextAssertion ;
    rl2p:forRequest ex:request1 ;
    rl2p:contextSubject ex:dutyReq2 ;
    rl2p:contextProperty rl2p:dutyFulfilled ;
    rl2p:contextValue "true"^^xsd:boolean ;
    rl2p:fulfillmentEvidence ex:trainingCertificate456 ;
    rl2p:assertedTime "2025-01-15T14:00:00Z"^^xsd:dateTime ;
    rl2p:assertedBy ex:Alice .
```

## Step 4: Re-evaluation with Full Approval

```turtle
# Re-evaluation after duties fulfilled
ex:eval2 a rl2p:EvaluationResult ;
    rl2p:evaluatedRequest ex:request1 ;
    rl2p:decision rl2p:Permit ;
    rl2p:activeDuties [ ] ;  # No remaining duties
    rl2p:matchedPolicies ex:loanAccessPolicy ;
    rl2p:matchedNorms ex:loanAccessPrivilege ;
    rl2p:evaluationTime "2025-01-15T14:05:00Z"^^xsd:dateTime ;
    rl2p:explanation "Access permitted. All duties fulfilled." .

# Case status updated
ex:case1
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
# - All duties in ex:eval2 rl2p:activeDuties are empty
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

## Step 6: Expiration Creates Re-certification Duty

```turtle
# One year later: access expires
# (This could be triggered by a scheduler or temporal event)

ex:expirationEvent a rl2:Event ;
    rl2p:affectsCase ex:case1 ;
    rl2:eventTime "2026-01-15T09:00:00Z"^^xsd:dateTime .

# Case status updated
ex:case1 rl2p:caseStatus rl2p:Expired .

# Re-certification duty is created (could be a new case or extension)
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
| Obligations/Duties | ✓ Fire-and-forget | ✓ State machine | ✓ State machine |
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
