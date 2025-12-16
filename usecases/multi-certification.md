# Use Case 44: Multi-Certification Required

**Pattern:** All conditions from a set must hold  
**Vocabulary Demonstrated:** `isAllOf`  
**Category:** Vocabulary Completeness, Compliance  
**Status:** DRAFT

---

## Business Context

Access to sensitive systems may require multiple certifications:

- Security clearance AND ethics training AND role certification
- All required certifications must be current
- Missing any one disqualifies access

## Scenario

A defense contractor's classified project requires:

> "Personnel must hold ALL of the following: (1) Active security clearance, (2) Project-specific access certification, (3) Current ethics training, (4) Need-to-know attestation."

## Policy Intent

> "Access is PERMITTED only if the person holds ALL required certifications."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Cardinality | All in set |
| Check | Each must be valid |
| Failure | Missing any one = deny |
| Dynamic | Certifications may expire |

## Comparison: isAnyOf vs isAllOf vs isNoneOf

| Operator | Meaning | Example |
|----------|---------|---------|
| `isAnyOf` | Value in set (at least one) | "Purpose is one of approved purposes" |
| `isAllOf` | All values in set | "Has all required certifications" |
| `isNoneOf` | Value not in set | "Country not sanctioned" |

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Access Classified System                 │
│  ─────────────────────────────────────────────────  │
│  Subject: Contractor                                 │
│  Action: access                                      │
│  Object: Classified Project Data                     │
│  Condition:                                          │
│    agent.certifications isAllOf {                    │
│      SecurityClearance,                              │
│      ProjectAccess,                                  │
│      EthicsTraining,                                 │
│      NeedToKnow                                      │
│    }                                                 │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

```
Given agent's certifications list L
Required certifications set R = {A, B, C, D}

isAllOf(L, R) evaluates to:
  - TRUE if R ⊆ L (all required are held)
  - FALSE if any element of R is not in L

Request: Agent with certs {A, B, C, D, E}
  - All of {A, B, C, D} present? YES
  - isAllOf = TRUE → PERMIT

Request: Agent with certs {A, B, D}
  - C missing
  - isAllOf = FALSE → DENY
```

## Certification Validity

Each certification may have validity constraints:

```turtle
ex:certification [
    ex:type ex:SecurityClearance ;
    ex:validUntil "2026-01-01"^^xsd:dateTime ;
    ex:status ex:Active
] .
```

The `isAllOf` check must also verify each is valid, not just present.

## Real-World Examples

### Healthcare

Access to patient records requires: HIPAA training, role authorization, active credentials.

### Financial Services

Trading system access requires: Series 7, firm registration, compliance attestation.

### Government

Classified access requires: background check, clearance level, need-to-know, briefing acknowledgment.

## Profile Requirements

```turtle
@prefix certification: <https://example.org/profile/certification#> .

certification:agentCertificationsOperand a rl2:LeftOperand ;
    rdfs:label "Agent Certifications" ;
    rl2:resolutionPath "agent.certifications.types" .

certification:SecurityClearance a certification:CertificationType .
certification:ProjectAccess a certification:CertificationType .
certification:EthicsTraining a certification:CertificationType .
certification:NeedToKnow a certification:CertificationType .
```

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate isAllOf operator
```

---

## References

- NIST SP 800-53 — Personnel security
- Defense contractor security requirements
- Healthcare credentialing standards
