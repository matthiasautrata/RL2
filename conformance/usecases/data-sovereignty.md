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

This model demonstrates the Agreement structure of sovereignty:
access is granted by Privilege, but the Manufacturer retains a Power
to revoke it at any time, and holds a Claim (correlative to the
Supplier's audit Duty) to verify ongoing compliance.

```turtle
@prefix ex: <https://example.org/> .
@prefix sovereignty: <https://example.org/profile/sovereignty#> .
@prefix rl2: <https://rl2.example/ontology#> .

# ── Privilege: Supplier may access production data ──────────────
ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:Supplier ;
    rl2:action ex:access ;
    rl2:object ex:ProductionData ;
    rl2:correlativeTo ex:revocationPower .

ex:access a rl2:Action ;
    rdfs:label "Access" .

# ── Power: Manufacturer may revoke the access Privilege at any time ──
ex:revocationPower a rl2:Power ;
    rl2:subject ex:Manufacturer ;
    rl2:action sovereignty:revokeAccess ;
    rl2:affectsNorm ex:accessPrivilege ;
    rl2:correlativeTo ex:accessPrivilege .

# ── Duty: Supplier must submit to usage audits ───────────────────
ex:auditDuty a rl2:Duty ;
    rl2:subject ex:Supplier ;
    rl2:action sovereignty:auditData ;
    rl2:object ex:UsageLogs ;
    rl2:counterparty ex:Manufacturer ;
    rl2:correlativeTo ex:auditClaim .

# ── Claim: Manufacturer's right to demand the audit ──────────────
ex:auditClaim a rl2:Claim ;
    rl2:subject ex:Manufacturer ;      # right-holder
    rl2:counterparty ex:Supplier ;     # duty-bearer
    rl2:correlativeTo ex:auditDuty .

ex:dataSharingAgreement a rl2:Agreement ;
    rl2:grantor ex:Manufacturer ;
    rl2:grantee ex:Supplier ;
    rl2:clause ex:accessPrivilege, ex:revocationPower, ex:auditDuty, ex:auditClaim .
```

---

## References

- IDS Reference Architecture Model — Data Sovereignty
- Gaia-X Architecture Document
- IDSA Position Paper on Data Sovereignty
- EU Data Governance Act
