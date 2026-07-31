# Use Case 41: Liability Exposure

**Pattern:** Exposure to another's power  
**Vocabulary Demonstrated:** `Liability`, `exposedTo`  
**Category:** Hohfeldian Relations  
**Status:** DRAFT

---

## Business Context

When one party has power, another has liability — their normative position may change without their consent:

- **Employment:** Employee liable to employer's hiring/firing power
- **Contracts:** Parties liable to termination powers
- **Governance:** Citizens liable to legislative power

Liability is not inherently negative — it can be exposure to beneficial change.

## Scenario

An employee in a data governance role is subject to their manager's authority:

> "Manager may assign or revoke data stewardship responsibilities for team members."

The employee has **liability** to the manager's power over role assignments.

## Hohfeldian Analysis

| Position | Holder | Description |
|----------|--------|-------------|
| **Power** | Manager | Can assign/revoke roles |
| **Liability** | Employee | Subject to role changes |

Liability is the correlative of Power — they describe the same relationship from different viewpoints.

## Policy Intent

> "Employee's data access privileges may be changed by Manager exercising role assignment power."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Passive position | Subject doesn't act; power is exercised on them |
| Correlative | Every Power has corresponding Liability |
| Scope | Limited to specific powers |
| Positive/Negative | Can gain or lose rights |

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Power: Assign Role                                  │
│  ─────────────────────────────────────────────────  │
│  Subject: Manager                                    │
│  Affects: Employee's data access privileges          │
│  Scope: Team members only                            │
└─────────────────────────────────────────────────────┘
            │
            │ correlates with
            ▼
┌─────────────────────────────────────────────────────┐
│  Liability: Subject to Role Assignment               │
│  ─────────────────────────────────────────────────  │
│  Subject: Employee                                   │
│  Exposed To: Manager's assignRolePower               │
│  Effect: Privileges may change                       │
└─────────────────────────────────────────────────────┘
```

## Positive vs Negative Liability

| Type | Power Effect | Example |
|------|--------------|---------|
| **Positive** | Gain rights | Manager assigns new access |
| **Negative** | Lose rights | Manager revokes access |
| **Mixed** | Both possible | Role reassignment |

## Comparison with Break-Glass (Use Case 3)

Break-glass demonstrates liability in the emergency context:
- The employee who breaks the glass accepts personal liability
- This is liability to *consequences*, slightly different from Hohfeldian liability to *power*

This use case focuses on pure Hohfeldian liability: exposure to another's power.

## Real-World Examples

### Employment

Employee liable to:
- Hiring power (gain employment)
- Firing power (lose employment)
- Promotion power (change level)

### Data Governance

Data consumer liable to:
- Steward's grant power (gain access)
- Steward's revoke power (lose access)
- Owner's policy change power (terms change)

### Corporate Governance

Shareholders liable to:
- Board's dividend power
- Merger power (ownership changes)

## Evaluation Logic

Liability is primarily descriptive — it doesn't drive evaluation directly. However, it's useful for:

1. **Documentation:** Making power relationships explicit
2. **Notification:** Alerting liable parties to power exercise
3. **Audit:** Tracking who was affected by power exercise

```
When Manager exercises assignRolePower:
1. Identify liable parties (team members)
2. Apply normative change to each
3. Record that liability was realized
```

## Profile Requirements

```turtle
@prefix governance: <https://example.org/profile/governance#> .

governance:assignRolePower a rl2:Power ;
    rdfs:label "Power to Assign Role" ;
    rl2:subject ex:Manager ;
    rl2:affectsNorm ex:dataAccessPrivilegeTemplate .

governance:roleAssignmentLiability a rl2:Liability ;
    rl2:subject ex:Employee ;
    rl2:exposedTo governance:assignRolePower .
```

---

## RL2 Model

This model demonstrates the Power/Liability correlative pair: the
Manager's Power to reach into the Employee's data-access privileges
correlates with the Employee's Liability to that exercise.

```turtle
@prefix ex: <https://example.org/> .
@prefix governance: <https://example.org/profile/governance#> .
@prefix rl2: <https://rl2.example/ontology#> .

# ── The privilege template the Power can alter ───────────────────
ex:dataAccessPrivilegeTemplate a rl2:Privilege ;
    rl2:subject ex:Employee ;
    rl2:action ex:access ;
    rl2:object ex:TeamDataset .

ex:access a rl2:Action ;
    rdfs:label "Access" .

# ── Power: Manager may assign/revoke the Employee's role-linked access ──
governance:assignRolePower a rl2:Power ;
    rl2:subject ex:Manager ;
    rl2:affectsNorm ex:dataAccessPrivilegeTemplate ;
    rl2:correlativeTo governance:roleAssignmentLiability .

# ── Liability: the Employee's exposure to that Power ─────────────
governance:roleAssignmentLiability a rl2:Liability ;
    rl2:subject ex:Employee ;
    rl2:exposedTo governance:assignRolePower ;
    rl2:correlativeTo governance:assignRolePower .

ex:stewardshipRoles a rl2:Set ;
    rl2:grantor ex:Manager ;
    rl2:clause governance:assignRolePower, governance:roleAssignmentLiability .
```

---

## References

- Hohfeld, W.N. "Fundamental Legal Conceptions" (1919)
- Employment law — at-will doctrine
- Corporate governance — fiduciary powers
- Administrative law — delegated powers
