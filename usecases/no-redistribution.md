# Use Case 19: No Redistribution

**Pattern:** Prohibition with pass-through obligation  
**Vocabulary Demonstrated:** `Prohibition`, downstream `Duty`  
**Category:** External Data Licenses  
**Status:** DRAFT

---

## Business Context

External data vendors (Bloomberg, LSEG, CME) universally restrict redistribution. This is the most fundamental constraint in commercial data licensing:

- **Protect revenue:** Prevent licensees from becoming competing distributors
- **Control chain of custody:** Maintain visibility into who has access
- **Enforce terms downstream:** Ensure sublicensees face same restrictions

## Scenario

A bank licenses market data from a data vendor. The license terms state:

> "Licensee shall not redistribute the Data to any third party. If Licensee provides derived works to third parties, Licensee must ensure those parties are bound by terms no less restrictive than this Agreement."

## Policy Intent

> "YOU may not redistribute the data. IF you provide derivatives, YOU must impose equivalent restrictions."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Primary constraint | Prohibition on redistribution |
| Secondary obligation | Pass-through duty on derived works |
| Scope | All forms: raw, transformed, aggregated |
| Exceptions | Regulatory disclosure, counterparty sharing |

## Real-World Terms

### Bloomberg Data License

> "User shall not... distribute or re-distribute the Licensed Data other than as expressly permitted... Separate agreements are available to Users wishing to create derivative works from and/or to redistribute the Licensed Data."

### CME Market Data License

> "Distributor shall not... sell, lease, license or otherwise distribute or redistribute the Information... except as expressly permitted."

### LSEG/Refinitiv Terms

> "Customer shall... not redistribute any Data or Derived Data... except to such regulators to the extent required for regulatory or compliance purposes."

## Normative Structure

This use case involves two connected norms:

```
┌─────────────────────────────────────────────────────┐
│  Prohibition: No Redistribution                      │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Prohibited Action: redistribute                     │
│  Object: Licensed Data                               │
│  Exception: Regulatory disclosure                    │
└─────────────────────────────────────────────────────┘
            │
            │ If derivative created and shared...
            ▼
┌─────────────────────────────────────────────────────┐
│  Duty: Pass-Through Terms                            │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Action: impose equivalent restrictions              │
│  Object: Derivative recipient                        │
│  Triggered by: Sharing derived work                  │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

```
Request: Agent A wants to redistribute Data D

1. Check Prohibition:
   - Is action = redistribute? YES
   - Is object covered? YES → DENY
   
2. Exception check:
   - Is recipient a regulator? 
   - Is disclosure legally required?
   - If YES → PERMIT with logging

Request: Agent A wants to share Derived Work W

1. Check if W derived from licensed data
2. If sharing permitted:
   - Activate pass-through Duty
   - Duty: A must bind recipient to equivalent terms
```

## Exception Patterns

| Exception | Condition | Common In |
|-----------|-----------|-----------|
| Regulatory disclosure | Recipient is regulator | All vendors |
| Counterparty notification | Transaction context | Bloomberg |
| Authorized redistributor | Separate agreement | CME, LSEG |
| Internal affiliate | Same corporate group | Most vendors |

## Comparison with Related Use Cases

| Use Case | Focus |
|----------|-------|
| **no-redistribution** | Core prohibition |
| derived-data-restriction (20) | What counts as "derived" |
| pass-through-terms (23) | Detailed downstream obligations |
| internal-use-only (18) | Simpler variant (no derivatives) |

## Profile Requirements

```turtle
@prefix license: <https://example.org/profile/license#> .

license:redistribute a rl2:Action ;
    rdfs:label "Redistribute" ;
    rdfs:comment "Transfer data to third parties outside the license scope." .

license:shareDerivative a rl2:Action ;
    rdfs:label "Share Derivative Work" .

license:imposeTerms a rl2:Action ;
    rdfs:label "Impose Equivalent Terms" ;
    rdfs:comment "Bind downstream recipient to restrictions." .

license:recipientTypeOperand a rl2:LeftOperand ;
    rl2:resolutionPath "context.recipient.type" .
```

## Audit Requirements

Vendors typically require:
- Logging of all external data transfers
- Periodic reporting on redistributor agreements
- Right to audit licensee's downstream contracts

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder for RL2 implementation
# Will demonstrate: Prohibition, conditional Duty, exception handling
```

---

## References

- Bloomberg ISDA IBOR Fallbacks Usage Terms
- CME Group Market Data License Agreement
- LSEG Market Data Terms
- ICE Derived Data License Agreement
