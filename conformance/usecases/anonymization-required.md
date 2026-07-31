# Use Case 29: Anonymization Required

**Pattern:** Processing constraint before use  
**Vocabulary Demonstrated:** `Duty` as precondition to `Privilege`  
**Category:** Data Contracts, Privacy  
**Status:** DRAFT

---

## Business Context

Sensitive data often cannot be used in its raw form. Before downstream use, it must be:

- **Anonymized:** Remove identifying information
- **Pseudonymized:** Replace identifiers with tokens
- **Aggregated:** Combine to prevent individual identification
- **Masked:** Redact sensitive fields

This creates a "process before use" pattern.

## Scenario

A healthcare organization shares patient data with researchers. The data sharing agreement requires:

> "Before any analysis, Recipient must apply the approved anonymization procedure. Raw patient identifiers must never be exposed to research staff."

## Policy Intent

> "Analysis is PERMITTED only AFTER anonymization has been performed."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Precondition | Transformation must occur first |
| Duty | Apply specified transformation |
| Gate | Privilege blocked until duty fulfilled |
| Verification | May require certification |

## Real-World Examples

### GDPR Recital 26

Anonymized data falls outside GDPR scope, incentivizing anonymization before processing.

### HIPAA Safe Harbor

Specifies 18 identifier types that must be removed for de-identification.

### IDS Data Spaces

"Anonymization" is a listed policy pattern in the Mobility Data Space.

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Duty: Anonymize Data                                │
│  ─────────────────────────────────────────────────  │
│  Subject: Data Processor                             │
│  Action: anonymize                                   │
│  Object: Raw Dataset                                 │
│  Output: Anonymized Dataset                          │
│  State: Pending → Fulfilled                          │
└─────────────────────────────────────────────────────┘
            │
            │ must be fulfilled before
            ▼
┌─────────────────────────────────────────────────────┐
│  Privilege: Analyze Data                             │
│  ─────────────────────────────────────────────────  │
│  Subject: Researcher                                 │
│  Action: analyze                                     │
│  Object: Anonymized Dataset                          │
│  Condition: anonymizationDuty.state = Fulfilled      │
└─────────────────────────────────────────────────────┘
```

## Sequencing Pattern

This is the "Tun-sollen" pattern applied to data transformation:

```
Raw Data ──[anonymize]──▶ Anonymized Data ──[analyze]──▶ Results
              │                                │
              │                                │
         Duty fulfilled                   Privilege active
```

## Anonymization Standards

| Standard | Approach |
|----------|----------|
| K-anonymity | Each record indistinguishable from k-1 others |
| L-diversity | Sensitive attributes have l distinct values per group |
| Differential privacy | Mathematical privacy guarantee |
| HIPAA Safe Harbor | Remove 18 specified identifier types |

## Verification

How to verify anonymization was performed correctly?

| Method | Description |
|--------|-------------|
| Automated check | System verifies transformation applied |
| Certification | Processor attests to compliance |
| Audit | Third party reviews process |
| Technical enforcement | Raw data never accessible to analysts |

## Profile Requirements

```turtle
@prefix privacy: <https://example.org/profile/privacy#> .

privacy:anonymize a rl2:Action ;
    rdfs:label "Anonymize" ;
    rdfs:comment "Apply anonymization transformation to remove identifiers." .

privacy:anonymizationStatusOperand a rl2:LeftOperand ;
    rl2:resolutionPath "asset.anonymizationRecord.status" .

privacy:anonymizationMethodOperand a rl2:LeftOperand ;
    rl2:resolutionPath "asset.anonymizationRecord.method" .
```

---

## RL2 Model

This model demonstrates a Duty (anonymize) that gates a Privilege
(analyze): the researcher's privilege only becomes exercisable once
the anonymization duty's recorded status is `"fulfilled"`.

```turtle
@prefix ex: <https://example.org/> .
@prefix privacy: <https://example.org/profile/privacy#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ── Duty: anonymize before any downstream use ────────────────────
ex:anonymizationDuty a rl2:Duty ;
    rl2:subject ex:DataProcessor ;
    rl2:action privacy:anonymize ;
    rl2:object ex:RawPatientDataset ;
    rl2:counterparty ex:HealthcareOrganization .

# ── Privilege: analyze, gated on the duty's fulfilled status ────
ex:analyzeAnonymizedData a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:analyze ;
    rl2:object ex:AnonymizedDataset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand privacy:anonymizationStatusOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "fulfilled"
    ] .

ex:analyze a rl2:Action ;
    rdfs:label "Analyze" .

ex:dataSharingAgreement a rl2:Agreement ;
    rl2:grantor ex:HealthcareOrganization ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:anonymizationDuty, ex:analyzeAnonymizedData .
```

---

## References

- GDPR Recital 26 — Anonymization
- HIPAA Safe Harbor De-identification
- IDS Policy Patterns — Anonymization
- Article 29 Working Party Opinion on Anonymization Techniques
