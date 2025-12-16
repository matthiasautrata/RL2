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
    rl2:claimHolder ex:Vendor ;
    rl2:claimAgainst ex:Licensee ;  # Direct
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

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate triggered Duty, downstream Agreement
```

---

## References

- Bloomberg Data License Terms
- Fannie Mae Data License Agreement
- TPICAP Master License Agreement
- Standard software sublicensing patterns
