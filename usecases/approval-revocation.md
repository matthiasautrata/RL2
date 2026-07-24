# Use Case 27: Approval Revocation

**Pattern:** Power to alter normative relations  
**Vocabulary Demonstrated:** `Power`, `affectsNorm`  
**Category:** Access Control, Governance  
**Status:** DRAFT

---

## Business Context

Approvals are not permanent. Circumstances change:

- An employee's role changes
- A project is cancelled
- Compliance discovers a violation
- Business relationship ends

The ability to **revoke** a previously granted approval is a distinct normative power — the authority to extinguish existing privileges.

## Scenario

A Data Steward grants a researcher access to a sensitive dataset. Later, the steward learns the researcher has violated data handling policies. The steward exercises their power to revoke the access.

## Policy Intent

> "The Data Steward HAS THE POWER to revoke any access privilege they previously granted."

## Hohfeldian Analysis

This use case demonstrates the **Power-Liability** correlative:

| Position | Holder | Description |
|----------|--------|-------------|
| **Power** | Data Steward | Can revoke the researcher's privilege |
| **Liability** | Researcher | Normative position subject to change |

Key insight: Power is not permission. The steward doesn't need *permission* to revoke — they have *authority* to do so. The revocation changes the researcher's normative position from "privileged" to "not privileged."

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Power: Revocation Authority                         │
│  ─────────────────────────────────────────────────  │
│  Subject: Data Steward                               │
│  Affects: ex:researcherAccessPrivilege               │
│  Effect: Extinguish (Privilege → ∅)                  │
│  Condition: Steward originally granted the privilege │
└─────────────────────────────────────────────────────┘
            │
            │ correlates with
            ▼
┌─────────────────────────────────────────────────────┐
│  Liability: Subject to Revocation                    │
│  ─────────────────────────────────────────────────  │
│  Subject: Researcher                                 │
│  Exposed to: ex:revocationPower                      │
└─────────────────────────────────────────────────────┘
```

## Power vs Permission

| Concept | Example | Effect |
|---------|---------|--------|
| **Permission** | "You may access the data" | Allows action |
| **Power** | "You may revoke access" | Changes norms |

A permission regulates *actions on assets*. A power regulates *normative relations themselves*.

## Evaluation Logic

```
State before exercise:
  - Researcher has Privilege P (access to dataset)
  - Steward has Power W (revoke P)

Steward exercises W:
  1. Verify: Does Steward hold W? YES
  2. Verify: Is P the target of W? YES
  3. Execute: Remove P from active norms
  
State after exercise:
  - Researcher no longer has Privilege P
  - Power W may remain (can revoke future grants)
```

## Real-World Examples

### Data Governance

Data Stewards routinely have:
- Power to grant access
- Power to revoke access
- Power to modify access conditions

### Employment

HR has power to:
- Terminate employment (extinguishes employee privileges)
- Change role (modifies privilege scope)

### Contract Law

Parties may have:
- Power to terminate agreement (extinguishes mutual obligations)
- Power to assign rights (transfers privileges)

## Scope Constraints

Powers are typically scoped:

| Scope | Meaning |
|-------|---------|
| **Own grants only** | Can only revoke what you granted |
| **Domain-limited** | Can only revoke within your data domain |
| **Time-limited** | Power expires after period |
| **Reason-required** | Must document justification |

## Comparison with Related Patterns

| Use Case | Demonstrates |
|----------|--------------|
| **approval-revocation** | Power to extinguish |
| power-to-grant (40) | Power to create |
| immunity-from-termination (39) | Protection against power |
| ethics-approval (7) | Approval as event, not power |

## Distinction: Power vs Event

In **ethics-approval (7)**, approval is an *Event* — a fact that occurred. The EventConstraint checks whether the event exists.

Here, revocation is a *Power* — an authority to change norms. The Power itself is a normative position, and its exercise has normative effect.

```
Event-based (ethics-approval):
  "IF approval event exists, THEN privilege is active"
  
Power-based (approval-revocation):
  "Steward CAN cause privilege to cease to exist"
```

## Profile Requirements

```turtle
@prefix governance: <https://example.org/profile/governance#> .

governance:revoke a rl2:Action ;
    rdfs:label "Revoke" ;
    rdfs:comment "Exercise power to extinguish a norm." .

governance:grantorOperand a rl2:LeftOperand ;
    rdfs:label "Original Grantor" ;
    rl2:resolutionPath "state.grantedBy" ;
    rdfs:comment "Resolves to the agent who originally granted the privilege." .
```

## Audit Requirements

Power exercise should be logged:
- Who exercised the power
- Which norm was affected
- Timestamp
- Justification (if required)

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder for RL2 implementation
# Will demonstrate: Power, affectsNorm, Liability (correlative)
```

---

## References

- Hohfeld, W.N. "Fundamental Legal Conceptions" (1919)
- NIST SP 800-162: Guide to ABAC — Administrative policies
- ISO/IEC 27001 — Access control revocation requirements
