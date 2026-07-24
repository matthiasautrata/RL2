# Use Case 33: Data Sovereignty

**Pattern:** Provider-controlled data exchange  
**Vocabulary Demonstrated:** `Agreement` structure, bilateral control  
**Category:** EU Data Spaces, IDS  
**Status:** DRAFT

---

## Business Context

Data sovereignty means data owners retain control even after sharing:

- **Provider sets terms:** Not "take it or leave it" but negotiated
- **Usage controlled:** Policies travel with data
- **Audit rights:** Provider can verify compliance
- **Revocation:** Provider can withdraw access

This is the core principle of IDS and Gaia-X.

## Scenario

An automotive manufacturer shares production data with a supplier. The manufacturer retains sovereignty:

> "Data remains under Manufacturer's control. Supplier access is governed by this Agreement. Manufacturer may audit usage and revoke access at any time."

## Policy Intent

> "Data exchange occurs ONLY under mutually agreed terms with ongoing provider control."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Control retained | Provider maintains authority |
| Terms negotiated | Not unilateral imposition |
| Ongoing | Not just at access time |
| Enforceable | Technical and legal mechanisms |

## IDS Data Sovereignty Principles

1. **Data remains at source** (or controlled copy)
2. **Policies travel with data**
3. **Usage is monitored/enforced**
4. **Provider can intervene**

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Agreement: Data Sharing Contract                    │
│  ─────────────────────────────────────────────────  │
│  Grantor: Manufacturer (data provider)               │
│  Grantee: Supplier (data consumer)                   │
│  Clauses:                                            │
│    - accessPrivilege (with conditions)               │
│    - purposeRestriction                              │
│    - retentionLimit                                  │
│    - auditDuty (on Supplier)                         │
│    - revocationPower (held by Manufacturer)          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Power: Revocation Authority                         │
│  ─────────────────────────────────────────────────  │
│  Subject: Manufacturer                               │
│  Affects: accessPrivilege                            │
│  Effect: May extinguish at any time                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Claim: Audit Right                                  │
│  ─────────────────────────────────────────────────  │
│  Claim Holder: Manufacturer                          │
│  Claim Against: Supplier                             │
│  Content: May audit data usage                       │
└─────────────────────────────────────────────────────┘
```

## Sovereignty Components

| Component | RL2 Mechanism |
|-----------|---------------|
| Access control | Privilege with conditions |
| Usage restriction | Prohibition, purpose constraint |
| Ongoing control | Power to revoke |
| Verification | Claim to audit |
| Time limits | Temporal conditions |
| Deletion | Duty on termination |

## Negotiation Flow

```
Provider                          Consumer
    │                                 │
    │──── Offer (proposed terms) ────▶│
    │                                 │
    │◀─── Counter-offer ──────────────│
    │                                 │
    │──── Revised Offer ─────────────▶│
    │                                 │
    │◀─── Accept ─────────────────────│
    │                                 │
    └────── Agreement formed ─────────┘
```

## Technical Enforcement

Data sovereignty requires:
- **Policy enforcement point** in consumer's environment
- **Usage logging** for audit
- **Remote attestation** of policy adherence
- **Secure deletion** on demand

## Profile Requirements

```turtle
@prefix sovereignty: <https://example.org/profile/sovereignty#> .

sovereignty:dataProviderOperand a rl2:LeftOperand ;
    rl2:resolutionPath "context.agreement.grantor" .

sovereignty:usageLogOperand a rl2:LeftOperand ;
    rl2:resolutionPath "state.usageLogs" .

sovereignty:auditData a rl2:Action ;
    rdfs:label "Audit Data Usage" .

sovereignty:revokeAccess a rl2:Action ;
    rdfs:label "Revoke Access" .
```

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate Agreement with Power and Claim
```

---

## References

- IDS Reference Architecture Model — Data Sovereignty
- Gaia-X Architecture Document
- IDSA Position Paper on Data Sovereignty
- EU Data Governance Act
