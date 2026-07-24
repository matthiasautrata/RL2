# Use Case 48: Compliance Attestation

**Pattern:** Status declaration  
**Vocabulary Demonstrated:** `Assertion` policy type  
**Category:** Vocabulary Completeness, Compliance  
**Status:** DRAFT

---

## Business Context

Organizations need to declare compliance status:

- "We are GDPR compliant"
- "This system meets SOC 2 requirements"
- "Data processing follows ISO 27001"

These are **assertions** — statements about normative status rather than grants of permission.

## Scenario

A data processor publishes a compliance assertion:

> "This organization asserts that its data processing operations comply with GDPR Articles 5, 6, and 32."

## Policy Intent

> "We ASSERT that specified compliance requirements are met."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Type | Statement of fact |
| Effect | Does not grant permissions |
| Verifiable | May be audited |
| Temporal | Valid at point in time |

## Assertion vs Other Policy Types

| Policy Type | Purpose |
|-------------|---------|
| `Set` | Unilateral declaration of permissions |
| `Offer` | Proposal awaiting acceptance |
| `Agreement` | Binding mutual obligations |
| `Privacy` | Data protection policy |
| **`Assertion`** | Statement about normative status |

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Assertion: GDPR Compliance Statement                │
│  ─────────────────────────────────────────────────  │
│  Asserter: DataProcessor                             │
│  Claims:                                             │
│    - Lawful basis established (Art. 6)               │
│    - Data minimization practiced (Art. 5)            │
│    - Security measures implemented (Art. 32)         │
│  Valid as of: 2025-01-01                             │
│  Evidence: Audit report reference                    │
└─────────────────────────────────────────────────────┘
```

## What Assertions Assert

| Claim Type | Example |
|------------|---------|
| Compliance status | "We comply with GDPR" |
| Certification | "We hold ISO 27001 certification" |
| Capability | "We can process data type X" |
| Limitation | "We do not process children's data" |

## Evaluation Use

Assertions don't directly grant access but may be preconditions:

```turtle
ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:Processor ;
    rl2:action ex:process ;
    rl2:object ex:PersonalData ;
    rl2:condition [
        # Processor must have GDPR assertion on file
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:processorComplianceAssertionOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef ex:GDPRCompliant
    ] .
```

## Assertion Lifecycle

```
Draft → Published → Verified → Expired/Revoked
          │            │
          │            └── May be audited
          └── Publicly available
```

## Assertion Evidence

Assertions may link to supporting evidence:

```turtle
ex:gdprAssertion a rl2:Assertion ;
    rl2:clause ex:gdprComplianceStatement ;
    ex:evidence [
        a ex:AuditReport ;
        ex:auditor ex:BigFourFirm ;
        ex:date "2024-12-01"^^xsd:date ;
        ex:scope "GDPR compliance review"
    ] .
```

## Real-World Examples

### SOC 2 Reports

Service organizations assert control compliance.

### GDPR Article 30

Records of processing activities are assertions about data handling.

### Gaia-X Self-Descriptions

Participants assert capabilities and compliance.

## Profile Requirements

```turtle
@prefix compliance: <https://example.org/profile/compliance#> .

compliance:complianceStatusOperand a rl2:LeftOperand ;
    rl2:resolutionPath "agent.complianceAssertions" .

compliance:GDPRCompliant a compliance:ComplianceStatus .
compliance:SOC2TypeII a compliance:ComplianceStatus .
compliance:ISO27001Certified a compliance:ComplianceStatus .
```

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate Assertion policy type
```

---

## References

- ODRL — Assertion policy type
- GDPR Article 30 — Records of processing activities
- SOC 2 reporting framework
- Gaia-X Self-Description framework
