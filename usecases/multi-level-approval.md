# Use Case 31: Multi-Level Approval

**Pattern:** Sequential approval chain  
**Vocabulary Demonstrated:** Multiple `EventConstraint`, ordered dependencies  
**Category:** Data Contracts, Governance  
**Status:** DRAFT

---

## Business Context

Sensitive data access often requires approval from multiple authorities in sequence:

1. Direct manager approves business need
2. Data steward approves data appropriateness
3. Legal reviews contractual implications
4. Compliance confirms regulatory alignment

Each approval is a prerequisite for the next.

## Scenario

A bank employee requests access to customer transaction data for a new analytics project. Required approvals:

1. **Manager:** Confirms legitimate business purpose
2. **Data Owner:** Confirms data is appropriate for use case
3. **Compliance:** Confirms no regulatory barriers
4. **Security:** Confirms technical controls in place

## Policy Intent

> "Access is PERMITTED only when ALL required approvals have been obtained IN ORDER."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Approvers | Multiple distinct authorities |
| Sequence | May be ordered or parallel |
| All required | Access denied if any missing |
| Timeout | Approvals may expire |

## Normative Structure

### Sequential Approvals

```
┌─────────────────────────────────────────────────────┐
│  EventConstraint: Manager Approval                   │
│  ─────────────────────────────────────────────────  │
│  Expects: Event with approver = Manager              │
│  Must occur before: Data Owner Approval              │
└─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────┐
│  EventConstraint: Data Owner Approval                │
│  ─────────────────────────────────────────────────  │
│  Expects: Event with approver = DataOwner            │
│  After: Manager Approval                             │
│  Must occur before: Compliance Approval              │
└─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────┐
│  EventConstraint: Compliance Approval                │
│  ─────────────────────────────────────────────────  │
│  Expects: Event with approver = Compliance           │
│  After: Data Owner Approval                          │
└─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────┐
│  Privilege: Access Data                              │
│  ─────────────────────────────────────────────────  │
│  Condition: All approvals obtained                   │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

```
Request: User wants to access sensitive data

For each required approval in sequence:
  1. Check if approval event exists
  2. If ordered: Check it occurred after previous approval
  3. If any missing → DENY with "pending approval from X"

If all present and ordered correctly → PERMIT
```

## Parallel vs Sequential

| Pattern | Use Case |
|---------|----------|
| **Sequential** | Each approver needs prior context |
| **Parallel** | Independent reviews can occur simultaneously |
| **Hybrid** | Some parallel, some sequential |

### Parallel Example

```turtle
# No ordering constraint - all must exist but order doesn't matter
ex:parallelApprovalAccess a rl2:Privilege ;
    rl2:subject ex:Employee ;
    rl2:action ex:access ;
    rl2:object ex:CustomerTransactionData ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [ a rl2:EventConstraint ; rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:Legal ] ] ;
        rl2:operand [ a rl2:EventConstraint ; rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:Compliance ] ] ;
        rl2:operand [ a rl2:EventConstraint ; rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:Security ] ]
    ] .
```

## Approval Expiration

Approvals often have validity periods:

```turtle
ex:managerApproval a rl2:Event ;
    rl2:approver ex:Manager ;
    rl2:eventTime "2025-01-15T10:00:00Z"^^xsd:dateTime ;
    ex:validUntil "2025-04-15T10:00:00Z"^^xsd:dateTime .
```

Condition must check both existence AND validity.

## Escalation

If an approver doesn't respond within SLA:

- Escalate to their manager
- Auto-approve (for low-risk)
- Auto-deny (for high-risk)

## Profile Requirements

```turtle
@prefix approval: <https://example.org/profile/approval#> .

# Approval events are read from the state event log; the segment after
# state.Events must name a declared Event type.
ex:ApprovalEvent a rl2:Event ;
    rdfs:comment "An approval decision carrying approver, level and validity." .

approval:approvalLevelOperand a rl2:LeftOperand ;
    rl2:resolutionPath "state.Events.ApprovalEvent.approvalLevel" .

approval:approvalValidUntilOperand a rl2:LeftOperand ;
    rl2:resolutionPath "state.Events.ApprovalEvent.validUntil" .

approval:Manager a approval:ApproverRole .
approval:DataOwner a approval:ApproverRole .
approval:Compliance a approval:ApproverRole .
approval:Security a approval:ApproverRole .
```

---

## RL2 Model

All four approval events must be present. (Ordering, when required, is enforced
by comparing event timestamps via a profile-declared operand; the base pattern
below requires only presence.)

```turtle
ex:sensitiveDataAccess a rl2:Privilege ;
    rl2:subject ex:Employee ;
    rl2:action ex:access ;
    rl2:object ex:CustomerTransactionData ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [ a rl2:EventConstraint ; rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:Manager ] ] ;
        rl2:operand [ a rl2:EventConstraint ; rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:DataOwner ] ] ;
        rl2:operand [ a rl2:EventConstraint ; rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:Compliance ] ] ;
        rl2:operand [ a rl2:EventConstraint ; rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:Security ] ]
    ] .
```

---

## References

- NIST SP 800-162 — Multi-level access control
- SOX compliance — Segregation of approval duties
- Enterprise access governance patterns
