# Use Case 40: Power to Grant Access

**Pattern:** Power to create normative relations  
**Vocabulary Demonstrated:** `Power`, `affectsNorm` (creation)  
**Category:** Access Control, Delegation  
**Status:** DRAFT

---

## Business Context

Not everyone can grant access. Only designated authorities have the **power** to create access privileges. This is distinct from:

- Having access yourself (Privilege)
- Being required to grant access (Duty)
- Approving a request (Event)

Power to grant is the **authority to bring new privileges into existence**.

## Scenario

A Data Steward has authority over a data domain. When a researcher requests access, the steward exercises their power to create a new access privilege for that researcher.

## Policy Intent

> "The Data Steward HAS THE POWER to grant access privileges to researchers for datasets in their domain."

## Hohfeldian Analysis

| Position | Holder | Description |
|----------|--------|-------------|
| **Power** | Data Steward | Can create new privileges |
| **Liability** | Researcher | Position can be improved (gain privilege) |

Note: Liability here is "positive" — the researcher's position changes *favorably* when the power is exercised.

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Power: Grant Authority                              │
│  ─────────────────────────────────────────────────  │
│  Subject: Data Steward                               │
│  Affects: Privilege template for researchers         │
│  Effect: Instantiate (∅ → new Privilege)             │
│  Condition: Dataset in steward's domain              │
└─────────────────────────────────────────────────────┘
            │
            │ when exercised, creates
            ▼
┌─────────────────────────────────────────────────────┐
│  Privilege: Dataset Access (newly created)           │
│  ─────────────────────────────────────────────────  │
│  Subject: Specific Researcher                        │
│  Action: access                                      │
│  Object: Specific Dataset                            │
│  Granted By: Data Steward                            │
│  Valid Until: [time limit if any]                    │
└─────────────────────────────────────────────────────┘
```

## Power vs Permission to Grant

| Concept | Description |
|---------|-------------|
| **Permission to grant** | "You may perform the grant action" |
| **Power to grant** | "Your grant action creates normative effects" |

A person might have permission to click "grant" in a UI but lack the power to actually create a valid privilege. Conversely, a system admin might have power but policies could prohibit exercising it without approval.

## Power Scope

Powers are typically constrained:

| Constraint | Example |
|------------|---------|
| **Domain** | Only datasets tagged with steward's domain |
| **Subject class** | Only researchers with valid affiliation |
| **Time** | Grant valid for max 1 year |
| **Conditions** | Only if training completed |

## Evaluation Logic

```
Request: Steward S wants to grant Privilege P to Researcher R

1. Does S hold Power W over privilege type P? YES/NO
2. Is target R a valid subject for P? YES/NO
3. Is object O in S's domain? YES/NO
4. Are all preconditions met? YES/NO

If all YES:
  - Create new Privilege instance
  - Record S as grantor
  - Log creation event
  
If any NO:
  - Power exercise fails
  - No privilege created
```

## Delegation vs Power

| Concept | Mechanism | Effect |
|---------|-----------|--------|
| **Delegation** | Transfer power | Delegate gains power, delegator may lose it |
| **Exercise** | Use power | New norm created, power remains |

A steward can delegate their power to a deputy:
```
Steward has Power W
Steward delegates W to Deputy
Deputy now has Power W (derived)
```

## Real-World Examples

### Data Governance

Data Stewards have power to:
- Grant access to datasets in their domain
- Set access conditions
- Revoke access (separate power)

### HR Systems

Managers have power to:
- Authorize employee access to team resources
- Cannot authorize access outside their team

### Contract Authority

Officers with signing authority have power to:
- Bind the organization to agreements
- Create obligations on behalf of the org

## Comparison with Related Use Cases

| Use Case | Power Effect |
|----------|--------------|
| **power-to-grant** | Create privilege |
| approval-revocation (27) | Extinguish privilege |
| ethics-approval (7) | Approval as event (not power) |

## Key Distinction: Event vs Power

**Ethics-approval (7)** models approval as an **Event**:
- Approval either happened or didn't
- EventConstraint checks for existence
- No ongoing authority

**Power-to-grant** models grant as a **Power**:
- Steward has ongoing authority
- Each exercise creates a new norm
- Authority itself is a normative position

## Profile Requirements

```turtle
@prefix governance: <https://example.org/profile/governance#> .

governance:grantAccess a rl2:Action ;
    rdfs:label "Grant Access" ;
    rdfs:comment "Exercise power to create an access privilege." .

governance:domainOperand a rl2:LeftOperand ;
    rdfs:label "Asset Domain" ;
    rl2:resolutionPath "asset.domain" .

governance:stewardDomainOperand a rl2:LeftOperand ;
    rdfs:label "Steward's Domain" ;
    rl2:resolutionPath "agent.stewardshipDomain" .
```

## Audit Requirements

Power exercise must be logged:
- Who exercised the power
- What privilege was created
- Who is the beneficiary
- Justification/request reference
- Timestamp

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder for RL2 implementation
# Will demonstrate: Power, affectsNorm (template), privilege instantiation
```

---

## References

- Hohfeld, W.N. "Fundamental Legal Conceptions" (1919)
- NIST SP 800-162: Guide to ABAC — Administrative models
- Data Governance Institute — Stewardship authority patterns
