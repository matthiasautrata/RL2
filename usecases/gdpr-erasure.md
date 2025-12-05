# Use Case 9: GDPR Right to Erasure

**Pattern:** Data subject rights with identity verification
**Identity Check:** Attribute matching (`dataSubject = currentAgent`)
**Category:** Privacy, GDPR Article 17

## Scenario

A data subject exercises their right to erasure ("right to be forgotten"). Only the data subject themselves can request deletion of their own data.

## Policy Intent

> "If YOU are the data subject, YOU may request deletion."

## Key Characteristics

- Personal data rights
- Identity verification critical
- Cannot request erasure of others' data
- GDPR Article 17 compliance

## RL2 Model (Unified State Approach)

```turtle
ex:erasureRequest a rl2:Duty ;
    rl2:subject ex:DataController ;
    rl2:action ex:delete ;
    rl2:object ex:PersonalData ;
    rl2:condition [
        # Duty triggered when data subject requests
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:dataSubjectId ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .

ex:exerciseErasureRight a rl2:Privilege ;
    rl2:subject ex:DataSubject ;
    rl2:action ex:requestErasure ;
    rl2:object ex:PersonalData ;
    rl2:condition [
        # Only the data subject can request erasure of their data
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:dataOwner ;  # Attribute of PersonalData
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .
```

Note: This use case uses attribute matching rather than duty state querying. The identity check ensures the data owner attribute matches the requesting agent.

## Evaluation

| Scenario | Data Owner | Request By | Result |
|----------|------------|------------|--------|
| Own data | Alice | Alice | PERMIT |
| Others' data | Alice | Bob | DENY |
| Controller override | Alice | Controller | Special handling |

## GDPR Article 17 Mapping

| GDPR Requirement | RL2 Mechanism |
|------------------|---------------|
| Art. 17(1): Right to erasure | `ex:exerciseErasureRight` Privilege |
| Art. 17(2): Controller obligation | `ex:erasureRequest` Duty |
| Identity verification | Attribute matching via AtomicConstraint |
| Exemptions (Art. 17(3)) | Additional conditions on Privilege |

## Related Rights

Similar pattern applies to:
- **Article 15:** Right of access
- **Article 16:** Right to rectification
- **Article 20:** Right to data portability

All require identity binding: only the data subject can exercise rights over their own data.

## Comparison

- **Manual processes:** Paper forms, identity verification
- **GDPR-specific tools:** Purpose-built, not generalizable
- **RL2:** Generic rights framework using `currentAgent` for identity binding
