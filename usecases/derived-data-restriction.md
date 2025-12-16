# Use Case 20: Derived Data Restriction

**Pattern:** Complex prohibition with reverse-engineering test  
**Vocabulary Demonstrated:** `Prohibition`, conditional evaluation  
**Category:** External Data Licenses  
**Status:** DRAFT

---

## Business Context

Data vendors protect their investment through restrictions on derived works. The key principle:

> "You may create derived data, but only if it cannot be reverse-engineered back to the source data."

This is more nuanced than a simple prohibition. Derived data is permitted — even encouraged — but the source data's commercial value must remain protected.

## Scenario

A bank licenses market data from a vendor. The bank wants to:
1. Use raw data for internal trading (permitted)
2. Create risk analytics for internal use (permitted)
3. Sell aggregated market indicators to clients (depends)

Whether #3 is permitted depends on whether the indicators can be reverse-engineered to reconstruct the source data.

## Policy Intent

> "Derived works may be distributed externally ONLY IF they cannot be reverse-engineered to the underlying data."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Not a blanket prohibition | Derived data is allowed |
| Conditional restriction | Depends on reversibility |
| Subjective test | "Can it be reverse-engineered?" |
| Vendor discretion | Vendor may make determination |

## Real-World Terms

### CME Group

> "Licensee shall have no right to use the Data... in the creation of derivative works as may be determined in CME's sole discretion."

### Turquoise (LSEG)

> "No Data Charges are payable for the internal or external distribution of such Original Works provided they cannot be reverse engineered in any way back to the underlying Data, and/or effectively substituted for that Data. In the event that an Original Work can be reverse engineered, or used as a substitute, Data Charges... will apply."

### ICE Data

> "Licensee shall have no right to use the Data for purposes of... the creation, issuance, distribution, marketing and/or maintenance of any index products... without entering into a separate Data and Trademark License Agreement."

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Prohibition: Distribute Reversible Derivatives      │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Prohibited Action: distribute                       │
│  Object: Derived Data                                │
│  Condition: derivative.isReversible = true           │
└─────────────────────────────────────────────────────┘
            │
            │ Alternatively (permissive framing)
            ▼
┌─────────────────────────────────────────────────────┐
│  Privilege: Distribute Non-Reversible Derivatives    │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Action: distribute                                  │
│  Object: Derived Data                                │
│  Condition: derivative.isReversible = false          │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

```
Request: Licensee wants to distribute Derived Work W

1. Is W derived from licensed data? YES/NO
   - If NO → not covered by this restriction
2. Can W be reverse-engineered to source data?
   - Assessment criteria (see below)
3. If reversible → DENY or require additional license
   If not reversible → PERMIT
```

## Reversibility Assessment

The "reverse-engineering test" is inherently subjective. Common criteria:

| Factor | Low Risk | High Risk |
|--------|----------|-----------|
| Aggregation level | Summary across 1000+ records | Single record values |
| Time delay | T+30 days | Real-time |
| Transformation | Complex algorithm | Simple filtering |
| Granularity | Daily averages | Tick-by-tick |
| Identifiability | Anonymous | Specific instruments |

## Examples

### Permitted (Non-Reversible)

- Monthly sector performance indices
- Volatility indicators aggregated across markets
- Anonymized trading pattern analysis

### Prohibited (Reversible)

- Real-time price feeds relabeled
- End-of-day values with minimal aggregation
- Instrument-specific analytics that reveal source prices

### Gray Area (Requires Approval)

- Industry benchmark indices
- Risk factors derived from pricing
- Composite indicators using licensed data

## Contractual Resolution

Because reversibility is subjective, contracts often specify:

1. **Pre-approval:** Licensee must get vendor approval before distributing
2. **Self-assessment:** Licensee certifies non-reversibility
3. **Vendor discretion:** Vendor can determine reversibility
4. **Safe harbors:** Specific transformation thresholds

## Comparison with Related Use Cases

| Use Case | Focus |
|----------|-------|
| **derived-data-restriction** | Conditional based on reversibility |
| no-redistribution (19) | Blanket prohibition |
| pass-through-terms (23) | Obligations on downstream |

## Profile Requirements

```turtle
@prefix license: <https://example.org/profile/license#> .

license:isReversibleOperand a rl2:LeftOperand ;
    rdfs:label "Is Reversible" ;
    rl2:resolutionPath "asset.derivationMetadata.reversible" ;
    rdfs:range xsd:boolean ;
    rdfs:comment "Whether the derived data can be reverse-engineered to source." .

license:derivationDepthOperand a rl2:LeftOperand ;
    rdfs:label "Derivation Depth" ;
    rl2:resolutionPath "asset.derivationMetadata.transformationCount" ;
    rdfs:comment "Number of transformation steps from source." .

license:aggregationLevelOperand a rl2:LeftOperand ;
    rdfs:label "Aggregation Level" ;
    rl2:resolutionPath "asset.derivationMetadata.recordCount" ;
    rdfs:comment "Number of source records aggregated." .
```

## Tiered Approach

Some licenses define tiers based on derivation characteristics:

| Tier | Criteria | Permission |
|------|----------|------------|
| Tier 1 | >100 records, >7 day delay | No fee, no approval |
| Tier 2 | 10-100 records, 1-7 day delay | Approval required |
| Tier 3 | <10 records, <1 day delay | Additional license fee |

## Audit Requirements

For derived data distribution:
- Source data identification
- Transformation description
- Reversibility self-assessment
- Vendor approval (if required)
- Distribution recipients

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder for RL2 implementation
# Will demonstrate: Prohibition with condition on derivation metadata
```

---

## References

- CME Derived Data License Agreement
- ICE Derived Data License Agreement
- Turquoise Market Data Policy
- LSEG Data Terms — Derived Data provisions
