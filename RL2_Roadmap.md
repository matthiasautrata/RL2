---
title: "RL2 Development Roadmap"
subtitle: "Profile-Based Architecture and Phased Introduction"
version: "0.3"
status: "Draft"
date: 2025-01-04
---

## Executive Summary

RL2 adopts a **profile-based architecture** where functionality is organized into composable modules. This approach enables:

- **Incremental adoption**: Use what you need, ignore the rest
- **Clear conformance**: Testable compliance per profile
- **Reduced complexity**: Learn profiles as needed
- **Future extensibility**: Add new profiles without breaking existing ones

The roadmap proceeds in phases, with each phase introducing one or more profiles. Each profile follows a consistent documentation pattern including: scope, features, use cases, test suite, and ODRL alignment.

---

## Profile Architecture Overview

```
                    RL2-Core
                  (ODRL 2.2 Parity)
                   [REQUIRED]
                        |
        +---------------+---------------+
        |               |               |
   Hohfeldian      Promises         Events
   [OPTIONAL]      [OPTIONAL]      [OPTIONAL]
        |               |               |
        +-------+-------+               |
                |                       |
            Advanced            Generations
           [OPTIONAL]           [OPTIONAL]
```

**Key Principles:**
- **RL2-Core is required** - provides ODRL 2.2 semantic parity
- **Extensions are optional** - add capabilities beyond ODRL
- **Explicit dependencies** - profiles declare what they require
- **Testable conformance** - implementations declare supported profiles

### Conformance Declaration

```turtle
# NOTE: Conformance and profile declarations are conceptual only.
# Actual properties for conformance declaration TBD in RL2-Protocol profile.

# Example (non-normative):
# ex:MyEvaluator a rl2:Evaluator ;
#     rl2p:conformsTo rl2p:Core, rl2p:Hohfeldian, rl2p:Events .

# ex:myPolicy a rl2:Policy ;
#     rl2p:requiresProfile rl2p:Core, rl2p:Hohfeldian .
```

---

## Phase 0: RL2-Core Profile
**Status:** In Development
**Target:** Q2 2025 (W3C Community Group Submission)

### Scope

RL2-Core provides **ODRL 2.2 semantic parity** with clarified operational semantics. It includes everything needed to express permissions, prohibitions, and duties with unambiguous evaluation.

**Key Message:** "ODRL 2.2, but done right"

### Features

#### Normative Classes
- **rl2:Privilege** - Permission to perform an action (ODRL: Permission)
- **rl2:Prohibition** - Prohibition against performing an action (ODRL: Prohibition)
- **rl2:Duty** - Obligation to perform an action (ODRL: Duty)
  - **Explicit lifecycle**: Pending → Active → Fulfilled → Violated
  - **rl2:ObligationState** enumeration with defined semantics

#### Policy Containers
- **rl2:Policy** - Base policy container
- **rl2:Set** - Unilateral policy declaration (ODRL: Set)
- **rl2:Offer** - Proposed policy awaiting acceptance (ODRL: Offer)
- **rl2:Agreement** - Bilateral policy with identified parties (ODRL: Agreement)

#### Core Constructs
- **rl2:Agent** - Parties in normative relations (ODRL: Party)
- **rl2:Action** - Actions that may be performed (ODRL: Action)
- **rl2:Asset** - Resources under governance (ODRL: Asset)
- **rl2:Condition** - Constraints and requirements (ODRL: Constraint)

#### Condition Types
- **rl2:AtomicConstraint** - Simple comparisons (leftOperand, operator, rightOperand)
- **rl2:LogicalConstraint** - Logical combinations (and, or, xone, not)
- **rl2:TemporalConstraint** - Time-based constraints with intervals

#### Roles
- **rl2:subject** - Agent bearing normative status (ODRL: assignee)
- **rl2:counterparty** - Agent in relation to subject
- **rl2:grantor** - Agent granting policy (ODRL: assigner)
- **rl2:grantee** - Agent receiving policy (ODRL: assignee)

#### Minimal Actions Vocabulary

RL2-Core defines **seven interoperable actions** covering 90% of use cases:

```turtle
rl2:read        # Access and view content
rl2:write       # Create new content
rl2:modify      # Change existing content
rl2:delete      # Remove or destroy content
rl2:execute     # Run code or invoke process
rl2:distribute  # Transfer to third parties
rl2:derive      # Create derivative works
```

**Note:** Domains define additional actions via profiles (e.g., `healthcare:prescribe`, `finance:trade`).

### What's Fixed from ODRL 2.2

| ODRL Issue | RL2-Core Solution |
|------------|-------------------|
| Undefined obligation lifecycle | Explicit state machine (Pending → Active → Fulfilled → Violated) |
| Ambiguous evaluation semantics | Formal operational semantics (RL2_Semantics.md) |
| SKOS vocabulary bloat | Minimal interoperable action set (7 actions) |
| Action/Asset refinements overengineering | Removed; use conditions for constraints |
| Unclear temporal semantics | Explicit intervals with defined evaluation |
| No conflict resolution guidance | Clear semantics: prohibition overrides privilege; use scoped conditions for exceptions |

### Use Cases

RL2-Core must demonstrate value through compelling use cases addressing ODRL's weakness: "standards without explanation why or what for."

#### UC-0.1: Basic File Access Control
**Domain:** Enterprise document management
**Scenario:** Alice may read Project X documents during business hours

```turtle
ex:fileAccessPolicy a rl2:Set ;
    rl2:clause ex:readPrivilege .

ex:readPrivilege a rl2:Privilege ;
    rl2:subject ex:Alice ;
    rl2:action rl2:read ;
    rl2:object ex:ProjectXDocs ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:start "2025-01-01T09:00:00Z"^^xsd:dateTime ;
            rl2:end "2025-12-31T17:00:00Z"^^xsd:dateTime
        ]
    ] .
```

**Evaluation:**
- Request at 10:00 AM → Permit
- Request at 6:00 PM → Deny (temporal condition fails)

**ODRL Comparison:** ODRL has same structure but undefined evaluation semantics.

---

#### UC-0.2: Data Deletion Duty with Deadline
**Domain:** Privacy compliance (data retention limits)
**Scenario:** Researcher must delete dataset within 30 days of access

```turtle
ex:researchAgreement a rl2:Agreement ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:usePrivilege, ex:deletionDuty .

ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action rl2:read ;
    rl2:object ex:Dataset .

ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action rl2:delete ;
    rl2:object ex:Dataset ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            rl2:end "2025-02-01T00:00:00Z"^^xsd:dateTime  # 30 days after access
        ]
    ] .
```

**Duty Lifecycle:**
1. **Pending** - Duty exists but activation condition not met
2. **Active** - Researcher accessed data; duty now enforceable
3. **Fulfilled** - Deletion performed before deadline
4. **Violated** - Deadline passed without deletion

**ODRL Gap:** ODRL has no duty state model. Implementations guess.

---

#### UC-0.3: Prohibition with Exception (Scoped Conditions)
**Domain:** Confidential information protection
**Scenario:** Staff may not distribute client data except to legal counsel

```turtle
ex:confidentialityPolicy a rl2:Set ;
    rl2:clause ex:distributionBan, ex:legalException .

# Scoped prohibition: applies only when recipient is NOT legal counsel
ex:distributionBan a rl2:Prohibition ;
    rl2:subject ex:Staff ;
    rl2:prohibitedAction rl2:distribute ;
    rl2:object ex:ClientData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:recipient ;
        rl2:constraintOperator rl2:neq ;
        rl2:rightOperandRef ex:LegalCounsel
    ] .

# Exception: applies only when recipient IS legal counsel
ex:legalException a rl2:Privilege ;
    rl2:subject ex:Staff ;
    rl2:action rl2:distribute ;
    rl2:object ex:ClientData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:recipient ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef ex:LegalCounsel
    ] .
```

**Evaluation (no conflict - conditions partition the space):**
- Request to distribute to LegalCounsel → Permit (only privilege applies)
- Request to distribute to external party → Deny (only prohibition applies)

**Note:** The complementary conditions (eq vs neq) ensure the prohibition and privilege never overlap, avoiding any conflict that would require resolution.

**ODRL Gap:** No clear pattern for exceptions. RL2 shows scoped conditions as the clean approach.

---

#### UC-0.4: Multi-Clause Agreement
**Domain:** Research data sharing
**Scenario:** Complete agreement with use rights, duties, and prohibitions

```turtle
ex:dataAgreement a rl2:Agreement ;
    rl2:grantor ex:University ;
    rl2:grantee ex:Researcher ;
    rl2:clause
        ex:useForResearch,      # May use for academic purposes
        ex:attributionDuty,     # Must cite source
        ex:commercialBan .      # May not use commercially

ex:useForResearch a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action rl2:read ;
    rl2:object ex:StudyData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:purpose ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "research"
    ] .

ex:attributionDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:attribute ;
    rl2:object ex:StudyData ;
    rl2:obligationState rl2:Active .

ex:commercialBan a rl2:Prohibition ;
    rl2:subject ex:Researcher ;
    rl2:prohibitedAction rl2:use ;
    rl2:object ex:StudyData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:purpose ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "commercial"
    ] .
```

**Evaluation:**
- Request with purpose=research → PermitWithObligations (attributionDuty)
- Request with purpose=commercial → Deny (prohibition)

---

#### UC-0.5: Temporal Validity Window
**Domain:** Software licensing
**Scenario:** License valid only during subscription period

```turtle
ex:softwareLicense a rl2:Agreement ;
    rl2:grantor ex:SoftwareVendor ;
    rl2:grantee ex:Customer ;
    rl2:clause ex:executionRight .

ex:executionRight a rl2:Privilege ;
    rl2:subject ex:Customer ;
    rl2:action rl2:execute ;
    rl2:object ex:Software ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:start "2025-01-01T00:00:00Z"^^xsd:dateTime ;
            rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime
        ]
    ] .
```

**Evaluation:**
- Request on 2025-06-15 → Permit (within interval)
- Request on 2026-01-01 → Deny (interval expired)

---

#### UC-0.6: Asset Collections
**Domain:** Department-wide data access
**Scenario:** Managers may read any document in their department

```turtle
ex:deptAccessPolicy a rl2:Set ;
    rl2:clause ex:managerAccess .

ex:managerAccess a rl2:Privilege ;
    rl2:subject ex:Manager ;
    rl2:action rl2:read ;
    rl2:object ex:DeptDocuments .

ex:DeptDocuments a rl2:AssetCollection ;
    rl2:member ex:doc1, ex:doc2, ex:doc3 .
```

**Evaluation:** Request for any document in collection → Permit

---

#### UC-0.7: Pre-Duty and Post-Duty
**Domain:** Controlled substance access
**Scenario:** May access after approval; must report after use

```turtle
ex:substanceAccess a rl2:Agreement ;
    rl2:clause ex:accessPrivilege, ex:approvalDuty, ex:reportingDuty .

ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action rl2:access ;
    rl2:object ex:ControlledSubstance .

# Pre-duty: must be fulfilled BEFORE access
ex:approvalDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:obtainApproval ;
    rl2:object ex:ControlledSubstance ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:EventConstraint ;
        rl2:expectsEvent ex:ManagerApprovalEvent
    ] .

# Post-duty: must be fulfilled AFTER access (within 24 hours)
ex:reportingDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:report ;
    rl2:object ex:UsageLog ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            rl2:end "2025-01-16T09:00:00Z"^^xsd:dateTime  # 24 hours after access
        ]
    ] .
```

**Evaluation Flow:**
1. Initial request → PermitWithObligations (approvalDuty Pending, reportingDuty Pending)
2. After approval event → approvalDuty becomes Fulfilled
3. After access → reportingDuty becomes Active
4. After report submitted → reportingDuty becomes Fulfilled

---

#### UC-0.8: Prohibition Override Behavior
**Domain:** Healthcare record access
**Scenario:** Demonstrate that activated prohibitions override privileges

```turtle
ex:healthcarePolicy a rl2:Set ;
    rl2:clause ex:doctorAccess, ex:emergencyBlock .

ex:doctorAccess a rl2:Privilege ;
    rl2:subject ex:Doctor ;
    rl2:action rl2:read ;
    rl2:object ex:PatientRecord .

# Emergency lockdown prohibits all access
ex:emergencyBlock a rl2:Prohibition ;
    rl2:subject ex:Doctor ;
    rl2:prohibitedAction rl2:read ;
    rl2:object ex:PatientRecord ;
    rl2:condition [
        a rl2:ContextualConstraint ;
        rl2:contextPath "system.emergencyMode" ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "true"
    ] .
```

**Evaluation (prohibition overrides when activated):**
- Normal mode: doctorAccess matches, emergencyBlock condition fails → Permit
- Emergency mode: both match, prohibition activated → Deny (prohibition overrides privilege)

---

#### UC-0.9: Offer and Acceptance Pattern
**Domain:** Terms of service
**Scenario:** Vendor offers terms; customer must accept

```turtle
# Initial state: Offer
ex:serviceTerms a rl2:Offer ;
    rl2:grantor ex:ServiceProvider ;
    rl2:grantee ex:Customer ;
    rl2:clause ex:serviceUse .

ex:serviceUse a rl2:Privilege ;
    rl2:subject ex:Customer ;
    rl2:action rl2:use ;
    rl2:object ex:CloudService .

# After acceptance: Agreement (implementation-specific transition)
# Offer is immutable; new Agreement created referencing Offer
```

**ODRL Alignment:** Same Policy types, but RL2 clarifies transition semantics.

---

#### UC-0.10: Complex Logical Conditions
**Domain:** Export control compliance
**Scenario:** May distribute data only to approved countries for approved purposes

```turtle
ex:exportPolicy a rl2:Set ;
    rl2:clause ex:distributionRight .

ex:distributionRight a rl2:Privilege ;
    rl2:subject ex:Company ;
    rl2:action rl2:distribute ;
    rl2:object ex:TechnicalData ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand ex:destinationCountry ;
            rl2:constraintOperator rl2:isAnyOf ;
            rl2:rightOperand ("US" "CA" "UK" "AU")
        ] , [
            a rl2:AtomicConstraint ;
            rl2:leftOperand ex:purpose ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand "research"
        ]
    ] .
```

**Evaluation:**
- Request to UK for research → Permit (both conditions satisfied)
- Request to UK for commercial → Deny (purpose condition fails)
- Request to CN for research → Deny (country condition fails)

---

### Test Suite

**Source:** Adapted from ODRL Evaluator open source test suite
**Coverage:** 50+ test cases

#### Test Categories
1. **Privilege Evaluation** (10 tests)
   - Basic matching (action, asset, agent)
   - Temporal constraints
   - Conditional activation

2. **Prohibition Evaluation** (10 tests)
   - Prohibition matching
   - Conflict resolution
   - Conditional prohibitions

3. **Duty Lifecycle** (15 tests)
   - State transitions (Pending → Active → Fulfilled/Violated)
   - Deadline enforcement
   - Pre-duty vs post-duty patterns

4. **Conditions** (10 tests)
   - Atomic constraints (eq, neq, lt, gte, isAnyOf)
   - Logical operators (and, or, xone, not)
   - Temporal intervals

5. **Policy Containers** (5 tests)
   - Set, Offer, Agreement semantics
   - Multi-clause policies
   - Policy-level conditions (future)

#### Test Format

Each test includes:
- **Input policy** (Turtle)
- **Input request** (agent, action, asset, context)
- **Expected decision** (Permit/Deny/PermitWithObligations/NotApplicable)
- **Expected state changes** (duty state transitions)
- **Explanation** (why this decision)

**Example Test:**

```turtle
# Test: duty-lifecycle-activation
# Description: Duty transitions from Pending to Active when condition holds

# Input Policy
ex:policy a rl2:Agreement ;
    rl2:clause ex:deletionDuty .

ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:Alice ;
    rl2:action rl2:delete ;
    rl2:object ex:Data ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:EventConstraint ;
        rl2:expectsEvent ex:AccessEvent
    ] .

# Input Request
{
  "requestingAgent": "ex:Alice",
  "requestedAction": "rl2:delete",
  "requestedAsset": "ex:Data",
  "context": {
    "events": ["ex:AccessEvent"]  # Access event occurred
  }
}

# Expected Result
{
  "decision": "PermitWithObligations",
  "stateChanges": {
    "ex:deletionDuty": {
      "oldState": "rl2:Pending",
      "newState": "rl2:Active"
    }
  },
  "activeDuties": ["ex:deletionDuty"]
}
```

**Test Suite Structure:**
```
tests/
  core/
    privilege/
      basic-match.ttl
      temporal-constraint.ttl
      ...
    prohibition/
      basic-prohibition.ttl
      conflict-resolution.ttl
      ...
    duty/
      state-pending-to-active.ttl
      state-active-to-fulfilled.ttl
      state-active-to-violated.ttl
      ...
    conditions/
      atomic-eq.ttl
      logical-and.ttl
      temporal-interval.ttl
      ...
    containers/
      set-evaluation.ttl
      agreement-bilateral.ttl
      ...
```

### ODRL 2.2 Alignment

**Coverage Matrix:**

| ODRL 2.2 Construct | RL2-Core Equivalent | Semantic Change |
|--------------------|---------------------|-----------------|
| odrl:Policy | rl2:Policy | Same |
| odrl:Set | rl2:Set | Same |
| odrl:Offer | rl2:Offer | Same |
| odrl:Agreement | rl2:Agreement | Same |
| odrl:Permission | rl2:Privilege | Renamed (Hohfeldian alignment) |
| odrl:Prohibition | rl2:Prohibition | Same |
| odrl:Duty | rl2:Duty | + Explicit state machine |
| odrl:assignee | rl2:subject | Renamed (clearer semantics) |
| odrl:assigner | rl2:grantor | Renamed |
| odrl:Constraint | rl2:Condition | Renamed + typed hierarchy |
| odrl:Action | rl2:Action | Same |
| odrl:Asset | rl2:Asset | Same |
| odrl:Party | rl2:Agent | Renamed |

**Migration Path:**
- Simple syntactic transformation (XSLT/SPARQL)
- Map ODRL action vocabulary to RL2 minimal actions or domain profiles
- Clarify duty activation/deadline semantics explicitly

### Deliverables

1. **RL2_Core_Profile.md** - Complete profile specification
2. **rl2-core.ttl** - Core ontology (OWL/Turtle)
3. **rl2-core-shacl.ttl** - Validation shapes
4. **rl2-actions-minimal.ttl** - 7 core actions
5. **RL2_Core_Semantics.md** - Operational semantics for Core
6. **tests/core/** - 50+ test cases
7. **RL2_Core_ODRL_Mapping.md** - Detailed ODRL alignment
8. **Reference implementation** - Python/JavaScript evaluator

### Dependencies
- None (Core is the foundation)

---

## Phase 1: Extension Profiles
**Status:** Planned
**Target:** Q4 2025

### Profiles in Phase 1

#### RL2-Hohfeldian Profile
**Scope:** Claims, Powers, Liabilities, Immunities

**Key Features:**
- `rl2:Claim` - Entitlement held against another agent
- `rl2:Power` - Ability to alter normative relations
- `rl2:Liability` - Exposure to exercise of power
- `rl2:Immunity` - Protection from power exercise
- `rl2:correlativeTo` - Link correlative Hohfeldian positions
- Sanctions and remedies via Power/Liability

**Use Cases:**
- UC-1.1: Contract modification rights (Power to extend deadline)
- UC-1.2: Data subject rights (Claim with correlative Duty)
- UC-1.3: Irrevocable grants (Immunity from revocation)
- UC-1.4: Compensatory obligations (Liability triggered by violation)
- UC-1.5: Waiver mechanisms (Power to extinguish Claims)

**Test Suite:** 25 tests covering correlatives, power exercise, immunities

**Dependencies:** RL2-Core (builds on Duty)

---

#### RL2-Protocol
**Scope:** Runtime evaluation protocol

**When Needed:** As soon as state tracking and state changes are required (Phase 1+)

**Key Features:**
- `rl2p:Request` - Access request structure
- `rl2p:EvaluationResult` - Decision with provenance
- `rl2p:DutyRequirement` - Runtime duty tracking
- `rl2p:Case` - Long-running evaluation context
- `rl2p:ContextAssertion` - External facts for evaluation

**Use Cases:**
- UC-1.6: Multi-stage access request workflow
- UC-1.7: Duty fulfillment evidence submission
- UC-1.8: Audit trail for compliance review
- UC-1.9: Re-evaluation after state change
- UC-1.10: Distributed evaluator interoperability

**Test Suite:** 20 tests for request/response protocol

**Dependencies:** RL2-Core

**Note:** Protocol is needed when implementations track state over time (duty lifecycle, promise tracking). For stateless evaluation (simple permission checks), Core alone suffices.

---

### Deliverables (Phase 1)

1. **RL2_Hohfeldian_Profile.md**
2. **RL2_Protocol.md** (already exists, formalize as profile)
3. **rl2-hohfeldian.ttl**, **rl2p.ttl**
4. **Test suites** (45 additional tests)
5. **Use case catalog** (10 new scenarios)

---

## Phase 2: Advanced Operational Semantics
**Status:** Planned
**Target:** Q2 2026

### Profiles in Phase 2

#### RL2-Events Profile
**Scope:** Event-driven workflows and state transitions

**Key Features:**
- `rl2:Event` - Observable occurrences
- `rl2:StateTransition` - State change tracking
- `rl2:EventConstraint` - Conditions requiring events
- `rl2:after` - Event sequencing
- Policy-level conditions (dynamic policy activation)

**Use Cases:**
- UC-2.1: Approval workflow (committee vote activates policy)
- UC-2.2: Sequential duty enforcement (A before B)
- UC-2.3: Event-triggered obligations
- UC-2.4: Multi-stage access control
- UC-2.5: Workflow state machines

**Test Suite:** 30 tests

**Dependencies:** RL2-Core, RL2-Protocol

---

#### RL2-Promises Profile
**Scope:** Voluntary commitment model

**Key Features:**
- `rl2:Promise` - Bilateral voluntary commitment
- `rl2:PromiseState` - Promise lifecycle
- Distinction from imposed Duty (deontic vs. voluntary)

**Use Cases:**
- UC-2.6: Service level agreements (SLAs)
- UC-2.7: Voluntary data sharing commitments
- UC-2.8: Best-effort obligations without sanctions
- UC-2.9: Cooperative commitments between autonomous agents
- UC-2.10: Promise chains (A promises to B if B promises to C)

**Test Suite:** 20 tests

**Dependencies:** RL2-Core (needs Duty for promiseContent)

---

### Deliverables (Phase 2)

1. **RL2_Events_Profile.md**
2. **RL2_Promises_Profile.md**
3. **rl2-events.ttl**, **rl2-promises.ttl**
4. **Test suites** (50 additional tests)
5. **Use case catalog** (10 new scenarios)

---

## Phase 3: Enterprise Features
**Status:** Planned
**Target:** Q4 2026

### Profiles in Phase 3

#### RL2-Generations Profile
**Scope:** Policy versioning and lifecycle management

**Key Features:**
- `rl2:policyGeneration` - Immutable policy snapshots
- Generation-to-Case binding
- Grandfather clause support
- Reproducible evaluation under historical policy sets

**Use Cases:**
- UC-3.1: Regulatory transition periods
- UC-3.2: Grandfather clause implementation
- UC-3.3: Audit trail for compliance ("law in effect when case filed")
- UC-3.4: Policy evolution without breaking existing cases
- UC-3.5: A/B testing of policy changes

**Test Suite:** 20 tests

**Dependencies:** RL2-Core, RL2-Protocol

---

#### RL2-Privacy Profile (Domain Profile)
**Scope:** Privacy-specific patterns and constructs

**Key Features:**
- `rl2:Privacy` - Policy subclass for data protection
- Privacy-specific left operands (purpose, processing basis)
- Consent modeling patterns
- Data subject rights patterns (access, rectification, erasure)

**Use Cases:**
- UC-3.6: GDPR Article 6 legal bases
- UC-3.7: Purpose limitation enforcement
- UC-3.8: Data subject access requests
- UC-3.9: Right to erasure workflows
- UC-3.10: Cross-border transfer restrictions

**Test Suite:** 25 tests

**Dependencies:** RL2-Core, RL2-Hohfeldian (for rights/claims)

---

### Deliverables (Phase 3)

1. **RL2_Generations_Profile.md**
2. **RL2_Privacy_Profile.md**
3. **rl2-generations.ttl**, **rl2-privacy.ttl**
4. **Test suites** (45 additional tests)
5. **Use case catalog** (10 new scenarios)
6. **Privacy profile guide** (GDPR implementation patterns)

---

## Documentation Pattern (Repeating)

Each profile follows this structure:

### 1. Profile Overview
- **Profile Name & Identifier**
- **Status** (Draft, Stable, Deprecated)
- **Version**
- **Short Description**

### 2. Dependencies
- **Required Profiles** (must be supported)
- **Optional Profiles** (enhances functionality if present)

### 3. Features
- **Classes Added** (with descriptions)
- **Properties Added** (with domains/ranges)
- **Individuals/Enumerations** (if any)

### 4. Use Cases
**Minimum 5 use cases per profile**

For each use case:
- **UC-X.Y: Title**
- **Domain** (Healthcare, Finance, Privacy, etc.)
- **Scenario** (natural language description)
- **Requirements** (bulleted functional requirements)
- **RL2 Policy** (complete working example in Turtle)
- **Test Cases** (request → expected decision)
- **Implementation Notes** (guidance for developers)
- **Comparison** (how this differs from ODRL or other approaches)

### 5. Test Suite
- **Test Coverage Matrix**
- **Test Categories** (by feature area)
- **Test Location** (path to test files)
- **Expected Test Count**

### 6. Conformance
- **Conformance Requirements** (MUST/SHOULD/MAY per RFC 2119)
- **Validation** (SHACL shapes, if any)
- **Conformance Declaration** (example)

### 7. ODRL Alignment (if applicable)
- **ODRL 2.2 Coverage** (what ODRL features this addresses)
- **Extensions Beyond ODRL** (what's new)
- **Migration Notes** (how to convert ODRL to RL2)

### 8. Examples
- **Minimal Example** (simplest possible use)
- **Typical Example** (common real-world use)
- **Advanced Example** (complex scenario showing full capabilities)

### 9. Implementation Guidance
- **Evaluator Requirements** (what implementations must do)
- **Performance Considerations**
- **Security Considerations**
- **Common Pitfalls**

### 10. References
- **Normative References** (specifications relied upon)
- **Informative References** (background reading)
- **Related Profiles**

---

## Test Suite Strategy

### Adaptation from ODRL Evaluator

**Source:** [ODRL Evaluator](https://github.com/nicosResearchAndDevelopment/odrl-evaluator) (and similar open source projects)

**Approach:**
1. **Inventory existing ODRL tests** - Catalog test scenarios
2. **Translate to RL2 syntax** - Convert ODRL policies to RL2
3. **Clarify ambiguous semantics** - Make ODRL's undefined behavior explicit
4. **Extend with RL2 features** - Add tests for state machines, Hohfeldian relations, etc.

**Test Translation Pattern:**

```turtle
# ODRL Test (ambiguous duty semantics)
odrl:permission [
    odrl:action odrl:read ;
    odrl:duty [
        odrl:action odrl:delete ;
        odrl:constraint [
            odrl:leftOperand odrl:dateTime ;
            odrl:operator odrl:lt ;
            odrl:rightOperand "2025-12-31"
        ]
    ]
] .

# RL2 Translation (explicit lifecycle)
rl2:Privilege [
    rl2:action rl2:read ;
    # Duty is separate, linked via policy container
] .

rl2:Duty [
    rl2:action rl2:delete ;
    rl2:obligationState rl2:Pending ;  # Explicit state
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [ rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime ]
    ]
] .
```

**Added Test Dimensions:**
- Duty state transitions (not in ODRL tests)
- Hohfeldian correlatives (not in ODRL)
- Promise fulfillment (not in ODRL)
- Event-driven workflows (not in ODRL)

### Test Suite Organization

```
tests/
  core/
    privilege/       # 10 tests
    prohibition/     # 10 tests
    duty/            # 15 tests (lifecycle emphasis)
    conditions/      # 10 tests
    containers/      # 5 tests
  hohfeldian/
    claims/          # 10 tests
    powers/          # 10 tests
    correlatives/    # 5 tests
  protocol/
    requests/        # 10 tests
    evaluation/      # 5 tests
    fulfillment/     # 5 tests
  events/
    workflows/       # 15 tests
    sequencing/      # 10 tests
    activation/      # 5 tests
  promises/
    lifecycle/       # 10 tests
    fulfillment/     # 10 tests
  generations/
    versioning/      # 10 tests
    transitions/     # 10 tests
  privacy/
    gdpr/            # 15 tests
    consent/         # 10 tests
```

**Total Coverage:** 200+ tests across all profiles

---

## Timeline Summary

| Quarter | Phase | Profiles | Test Count | Total Tests |
|---------|-------|----------|------------|-------------|
| Q2 2025 | Phase 0 | Core | 50 | 50 |
| Q4 2025 | Phase 1 | Hohfeldian, Protocol | 45 | 95 |
| Q2 2026 | Phase 2 | Events, Promises | 50 | 145 |
| Q4 2026 | Phase 3 | Generations, Privacy | 45 | 190 |

---

## W3C Submission Strategy

### Submission 1: RL2-Core (Q2 2025)
**Package Contents:**
- RL2_Core_Profile.md
- RL2_Core_Semantics.md
- rl2-core.ttl, rl2-core-shacl.ttl
- rl2-actions-minimal.ttl
- tests/core/ (50 tests)
- 10 use cases
- ODRL 2.2 mapping document
- Reference implementation

**Message:** "ODRL 2.2 with unambiguous semantics. Everything else is optional extensions."

---

### Submission 2: Extension Profiles (Q4 2025)
**Package Contents:**
- RL2_Profiles_Catalog.md
- Hohfeldian and Protocol profile specs
- Test suites (45 tests)
- 10 additional use cases
- Conformance mechanism documentation

**Message:** "Building blocks for advanced scenarios. Adopt what you need."

---

### Submission 3: Production Profiles (Q4 2026)
**Package Contents:**
- Events, Promises, Generations, Privacy profiles
- Complete test suite (190 tests)
- Domain-specific guides (Privacy/GDPR)
- Implementation reports (at least 2 independent implementations)

**Message:** "Production-ready for enterprise governance at scale."

---

## Success Criteria

### Technical Success
- ✓ All profiles have complete specifications
- ✓ All profiles have test suites (>80% coverage)
- ✓ At least 2 independent conformant implementations per profile
- ✓ ODRL 2.2 feature parity demonstrated

### Community Success
- ✓ W3C Community Group adoption
- ✓ Industry implementations (at least 3 organizations)
- ✓ Published use case reports from real deployments
- ✓ Contributions from multiple organizations

### Adoption Success
- ✓ RL2-Core adopted as ODRL successor recommendation path
- ✓ Extension profiles demonstrate value beyond ODRL
- ✓ Domain profiles (Privacy, Media, Finance) emerge from community

---

## Open Questions

### Technical
1. Should Privacy be Phase 1 or Phase 3?
2. What granularity for domain profiles (Media, Finance, Healthcare)?
3. Do we need an RL2-Temporal-Advanced profile, or is Core sufficient?

### Process
1. W3C Community Group vs. Working Group?
2. Formal liaison with ODRL CG?
3. Conformance testing infrastructure (who hosts)?

### Community
1. How to encourage independent implementations?
2. Reference implementation language (Python/JS/both)?
3. Profile governance (who can propose new profiles)?

---

## References

- [ODRL 2.2](https://www.w3.org/TR/odrl-model/)
- [ODRL Evaluator](https://github.com/nicosResearchAndDevelopment/odrl-evaluator)
- [W3C Process Document](https://www.w3.org/Consortium/Process/)
- RL2_Core.md
- RL2_Semantics.md
- RL2_Protocol.md
- RL2_References.md

---

## Appendix A: Profile Dependency Matrix

| Profile | Depends On | Optional With | Conflicts With |
|---------|------------|---------------|----------------|
| Core | (none) | (all) | (none) |
| Hohfeldian | Core | Promises, Events | (none) |
| Promises | Core | Hohfeldian, Events | (none) |
| Protocol | Core | (all) | (none) |
| Events | Core, Protocol | Promises, Generations | (none) |
| Generations | Core, Protocol | Events | (none) |
| Privacy | Core | Hohfeldian, Protocol | (none) |

---

## Appendix B: Conformance Levels

### Minimal Conformance
- **Profiles:** Core only
- **Use Case:** Simple access control (ODRL replacement)
- **Implementation Effort:** Low

### Standard Conformance
- **Profiles:** Core + Protocol + Hohfeldian
- **Use Case:** Enterprise data governance with duties and rights
- **Implementation Effort:** Medium

### Full Conformance
- **Profiles:** Core + Protocol + Hohfeldian + Events + Generations
- **Use Case:** Production governance at scale with workflows
- **Implementation Effort:** High

### Domain Conformance (Privacy)
- **Profiles:** Core + Protocol + Hohfeldian + Privacy
- **Use Case:** GDPR compliance and privacy governance
- **Implementation Effort:** Medium-High

---

*End of RL2 Roadmap*
