# Use Case 23: Pass-Through Terms

**Pattern:** Downstream obligation propagation  
**Vocabulary Demonstrated:** `Duty` on sublicensee, chain of obligations  
**Category:** External Data Licenses  
**Status:** DRAFT

---

## Business Context

When a licensee is permitted to share data downstream (to customers, partners, or sublicensees), the original restrictions must follow. This creates a chain:

```
Vendor → Licensee → Sublicensee → End User
         └─────────────────────────────────┘
              Same restrictions apply
```

The licensee has a **Duty** to impose equivalent terms on any downstream recipient.

## Scenario

A data aggregator licenses reference data from multiple vendors. The aggregator may redistribute to its customers, but must:

1. Bind customers to equivalent use restrictions
2. Ensure customers cannot further redistribute
3. Maintain audit trail of downstream agreements
4. Remain liable for customer violations

## Policy Intent

> "If Licensee redistributes data, Licensee MUST impose terms no less restrictive than this Agreement on all recipients."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Trigger | Redistribution or derivative sharing |
| Obligation | Impose equivalent restrictions |
| Scope | All downstream recipients |
| Liability | Licensee remains responsible |

## Real-World Terms

### Bloomberg

> "Separate agreements are available to Users wishing to create derivative works from and/or to redistribute the Licensed Data beyond the right and license granted herein."

### Fannie Mae

> "Licensee will strictly prohibit End Users from reselling, disclosing or redistributing the Data externally... The EULAs will further contain terms and conditions substantially similar to Section 3.2 applicable to End Users."

### TPICAP

> "To the extent that the Subscriber is granted the right to redistribute any Data... it shall ensure that a Customer Agreement is in place, which shall not purport to offer any rights over and above the rights granted to the Subscriber."

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Redistribute (if licensed)              │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Action: redistribute                                │
│  Object: Licensed Data                               │
│  Condition: hasRedistributionRights = true           │
└─────────────────────────────────────────────────────┘
            │
            │ triggers
            ▼
┌─────────────────────────────────────────────────────┐
│  Duty: Impose Equivalent Terms                       │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Action: bindToTerms                                 │
│  Object: Downstream Recipient                        │
│  Counterparty: Original Vendor                       │
│  Content: Terms no less restrictive                  │
└─────────────────────────────────────────────────────┘
            │
            │ results in
            ▼
┌─────────────────────────────────────────────────────┐
│  Agreement: Downstream License                       │
│  ─────────────────────────────────────────────────  │
│  Grantor: Licensee                                   │
│  Grantee: Downstream Recipient                       │
│  Clauses: [inherited restrictions]                   │
└─────────────────────────────────────────────────────┘
```

## What "No Less Restrictive" Means

| Original Term | Permitted Downstream | Prohibited Downstream |
|---------------|---------------------|----------------------|
| Internal use only | Internal use only | Broader use |
| No redistribution | No redistribution | Redistribution rights |
| Display only | Display only | Non-display use |
| 1-year retention | ≤1-year retention | Longer retention |

The licensee MAY add stricter terms but MUST NOT relax them.

## Evaluation Logic

```
Request: Licensee wants to redistribute to Recipient R

1. Does Licensee have redistribution rights? YES/NO
2. If YES:
   - Create pass-through Duty
   - Duty: Licensee must bind R to equivalent terms
   - Track: Downstream agreement must exist before delivery
3. Verify downstream agreement exists
4. If verified → PERMIT redistribution
   If not → DENY until agreement in place
```

## Chain Liability

The original vendor typically retains rights against the entire chain:

```turtle
# Vendor can enforce against any party in chain
ex:vendorEnforcementRight a rl2:Claim ;
    rl2:subject ex:Vendor ;          # right-holder
    rl2:counterparty ex:Licensee ;   # duty-bearer (direct)
    rdfs:comment "Licensee liable for downstream violations" .
```

## Profile Requirements

```turtle
@prefix license: <https://example.org/profile/license#> .

license:bindToTerms a rl2:Action ;
    rdfs:label "Bind to Terms" ;
    rdfs:comment "Impose license restrictions on downstream party." .

license:hasDownstreamAgreementOperand a rl2:LeftOperand ;
    rl2:resolutionPath "state.downstreamAgreements.exists" ;
    rdfs:range xsd:boolean .

license:downstreamRecipientOperand a rl2:LeftOperand ;
    rl2:resolutionPath "context.recipient" .
```

---

## RL2 Model

This model demonstrates the full chain: a conditional Privilege to
redistribute, the Duty it triggers to bind downstream recipients to
equivalent terms, the resulting downstream Agreement carrying an
inherited restriction, and the Vendor's Claim against the Licensee
for the whole chain.

```turtle
@prefix ex: <https://example.org/> .
@prefix license: <https://example.org/profile/license#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:hasRedistributionRightsOperand a rl2:LeftOperand ;
    rdfs:label "Has Redistribution Rights" ;
    rl2:resolutionPath "context.licensee.hasRedistributionRights" ;
    rdfs:range xsd:boolean .

# ── Privilege: redistribute, if licensed to do so ────────────────
ex:redistributePrivilege a rl2:Privilege ;
    rl2:subject ex:Licensee ;
    rl2:action ex:redistribute ;
    rl2:object ex:LicensedData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:hasRedistributionRightsOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "true"^^xsd:boolean
    ] .

ex:redistribute a rl2:Action ;
    rdfs:label "Redistribute" .

# ── Duty: impose equivalent terms, triggered by that same right ──
ex:bindToTermsDuty a rl2:Duty ;
    rl2:subject ex:Licensee ;
    rl2:action license:bindToTerms ;
    rl2:object ex:DownstreamRecipient ;
    rl2:counterparty ex:Vendor ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:hasRedistributionRightsOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "true"^^xsd:boolean
    ] ;
    rl2:correlativeTo ex:vendorEnforcementRight .

# ── Vendor's Claim against the Licensee for the whole chain ──────
ex:vendorEnforcementRight a rl2:Claim ;
    rl2:subject ex:Vendor ;          # right-holder
    rl2:counterparty ex:Licensee ;   # duty-bearer (direct)
    rl2:correlativeTo ex:bindToTermsDuty ;
    rdfs:comment "Licensee liable for downstream violations." .

# ── Downstream Agreement: the inherited restriction, no weaker ───
ex:noFurtherRedistribution a rl2:Prohibition ;
    rl2:subject ex:DownstreamRecipient ;
    rl2:prohibitedAction ex:redistribute ;
    rl2:object ex:LicensedData .

ex:downstreamAgreement a rl2:Agreement ;
    rl2:grantor ex:Licensee ;
    rl2:grantee ex:DownstreamRecipient ;
    rl2:clause ex:noFurtherRedistribution .

ex:vendorLicenseAgreement a rl2:Agreement ;
    rl2:grantor ex:Vendor ;
    rl2:grantee ex:Licensee ;
    rl2:clause ex:redistributePrivilege, ex:bindToTermsDuty, ex:vendorEnforcementRight .
```

---

## References

- Bloomberg Data License Terms
- Fannie Mae Data License Agreement
- TPICAP Master License Agreement
- Standard software sublicensing patterns
