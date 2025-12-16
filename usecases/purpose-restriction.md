# Use Case 24: Purpose Restriction

**Pattern:** Purpose whitelist  
**Vocabulary Demonstrated:** `isAnyOf`  
**Category:** Data Contracts, Privacy  
**Status:** DRAFT

---

## Business Context

A data provider makes a dataset available but restricts its use to specific, approved purposes. This is fundamental to:

- **GDPR Article 5(1)(b):** Purpose limitation principle
- **Data marketplace terms:** Providers specify permitted uses
- **Contractual data sharing:** Bilateral agreements scope usage

## Scenario

A financial institution provides customer analytics data to internal teams. The data may only be used for:
- Risk assessment
- Fraud detection
- Regulatory reporting

Use for marketing, product development, or sale to third parties is prohibited.

## Policy Intent

> "Data may be used ONLY IF the declared purpose is one of the approved purposes."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Constraint type | Set membership (whitelist) |
| Enforcement point | Request time |
| Failure mode | Deny if purpose not in approved set |
| Audit requirement | Log declared purpose with each access |

## Real-World Examples

### Bloomberg Data License

From Bloomberg's terms: Data may be used for "internal commercial (non-consumer related) use only" — effectively a purpose whitelist excluding consumer-facing applications.

### GDPR Consent

Data collected for "newsletter delivery" cannot be repurposed for "profiling" without additional consent — each purpose is a discrete permission.

### IDS Data Spaces

The International Data Spaces Reference Architecture includes purpose constraints as a core policy pattern for data sovereignty.

## Evaluation Logic

```
Given:
  - Request declares purpose P
  - Policy defines approved set {P1, P2, P3}
  
Evaluate:
  IF P ∈ {P1, P2, P3} THEN Permit
  ELSE Deny
```

## Comparison with Related Patterns

| Pattern | Mechanism | RL2 Operator |
|---------|-----------|--------------|
| Purpose whitelist | P must be in set | `isAnyOf` |
| Purpose blacklist | P must NOT be in set | `isNoneOf` |
| Exact purpose match | P must equal specific value | `eq` |
| Purpose hierarchy | P must be subtype of category | `isA` |

## Profile Requirements

This use case requires a profile that declares:

1. **Purpose operand:** Resolves to the declared purpose from the request context
2. **Purpose vocabulary:** Enumeration of valid purpose values

```turtle
@prefix datacontract: <https://example.org/profile/datacontract#> .

datacontract:purposeOperand a rl2:LeftOperand ;
    rdfs:label "Declared Purpose" ;
    rl2:resolutionPath "context.purpose" .

datacontract:RiskAssessment a datacontract:Purpose .
datacontract:FraudDetection a datacontract:Purpose .
datacontract:RegulatoryReporting a datacontract:Purpose .
datacontract:Marketing a datacontract:Purpose .
```

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No purpose declared | Deny (fail-closed) |
| Multiple purposes declared | All must be in whitelist |
| Purpose hierarchy (sub-purpose) | Depends on profile semantics |
| Unknown purpose value | Deny |

## Relationship to Other Use Cases

- **geo-restriction (25):** Same pattern, different operand (jurisdiction vs purpose)
- **gdpr-erasure (9):** Purpose operand already shown but with `eq`, not `isAnyOf`
- **no-ml-training (30):** Specific purpose prohibition (blacklist approach)

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder for RL2 implementation
```

---

## References

- GDPR Article 5(1)(b) — Purpose limitation
- IDS Reference Architecture Model — Usage Control Policies
- Bloomberg Data License Terms — Permitted Use Clauses
