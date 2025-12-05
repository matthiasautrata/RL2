# Use Case 9: GDPR Right to Erasure

**Pattern:** Data subject rights with identity verification
**Identity Check:** `dataOwnerOperand = currentAgent`
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

## Profile-Declared Operands

This use case requires a privacy profile that declares operands for accessing data ownership attributes. All context access goes through the canonical path mechanism.

```turtle
@prefix privacy: <https://example.org/profile/privacy#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Profile-declared operand for the data owner (data subject) of personal data
privacy:dataOwnerOperand a rl2:LeftOperand ;
    rdfs:label "Data Owner" ;
    rdfs:comment """Resolves to the agent who is the data subject (owner) of the
    personal data asset. Used for GDPR rights enforcement.""" ;
    rl2:resolutionPath "asset.dataOwner" ;
    rdfs:range rl2:Agent .

# Profile-declared operand for processing purpose
privacy:purposeOperand a rl2:LeftOperand ;
    rdfs:label "Purpose" ;
    rdfs:comment """Resolves to the declared purpose of the data processing request.
    Equivalent to ODRL's odrl:purpose but as a declared, resolvable operand.""" ;
    rl2:resolutionPath "context.purpose" ;
    rdfs:range privacy:Purpose .

# Profile-declared operand for consent status
privacy:consentStatusOperand a rl2:LeftOperand ;
    rdfs:label "Consent Status" ;
    rdfs:comment "Resolves to whether valid consent exists for processing." ;
    rl2:resolutionPath "asset.consentRecord.status" ;
    rdfs:range privacy:ConsentStatus .
```

## RL2 Model (Unified State Approach)

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix privacy: <https://example.org/profile/privacy#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Duty on data controller when erasure is requested
ex:erasureRequest a rl2:Duty ;
    rl2:subject ex:DataController ;
    rl2:action ex:delete ;
    rl2:object ex:PersonalData ;
    rl2:condition [
        # Duty triggered when data subject (asset owner) requests
        a rl2:AtomicConstraint ;
        rl2:leftOperand privacy:dataOwnerOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .

# Privilege for data subject to exercise erasure right
ex:exerciseErasureRight a rl2:Privilege ;
    rl2:subject ex:DataSubject ;
    rl2:action ex:requestErasure ;
    rl2:object ex:PersonalData ;
    rl2:condition [
        # Only the data subject can request erasure of their data
        # Uses profile-declared operand with explicit resolution path
        a rl2:AtomicConstraint ;
        rl2:leftOperand privacy:dataOwnerOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .
```

## Resolution Semantics

When evaluating the identity binding condition:

1. `privacy:dataOwnerOperand` has `rl2:resolutionPath "asset.dataOwner"`
2. `resolve(privacy:dataOwnerOperand, Env, ⊥)` calls `deref("asset.dataOwner", Env)`
3. This navigates: `Env.Asset.dataOwner` → returns the data subject IRI
4. `rl2:currentAgent` resolves to `Env.Agent`
5. Constraint holds if these are equal

This is pure attribute matching (not duty state querying). The identity check ensures the data owner attribute matches the requesting agent.

## Evaluation

| Scenario | Data Owner | Request By | Result |
|----------|------------|------------|--------|
| Own data | Alice | Alice | PERMIT |
| Others' data | Alice | Bob | DENY |
| Controller override | Alice | Controller | Special handling via exemptions |

## GDPR Article 17 Mapping

| GDPR Requirement | RL2 Mechanism |
|------------------|---------------|
| Art. 17(1): Right to erasure | `ex:exerciseErasureRight` Privilege |
| Art. 17(2): Controller obligation | `ex:erasureRequest` Duty |
| Identity verification | Profile-declared `privacy:dataOwnerOperand` |
| Exemptions (Art. 17(3)) | Additional conditions on Privilege |

## Related Rights (Same Pattern)

The same profile-declared operand pattern applies to other GDPR data subject rights:

### Article 15: Right of Access

```turtle
ex:exerciseAccessRight a rl2:Privilege ;
    rl2:subject ex:DataSubject ;
    rl2:action ex:requestAccess ;
    rl2:object ex:PersonalData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand privacy:dataOwnerOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .
```

### Article 16: Right to Rectification

```turtle
ex:exerciseRectificationRight a rl2:Privilege ;
    rl2:subject ex:DataSubject ;
    rl2:action ex:requestRectification ;
    rl2:object ex:PersonalData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand privacy:dataOwnerOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .
```

### Article 20: Right to Data Portability

```turtle
ex:exercisePortabilityRight a rl2:Privilege ;
    rl2:subject ex:DataSubject ;
    rl2:action ex:requestPortability ;
    rl2:object ex:PersonalData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand privacy:dataOwnerOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .
```

All require identity binding: only the data subject can exercise rights over their own data.

## Why Profile-Declared Operands?

Previous versions introduced ad-hoc properties like `ex:dataSubjectId` and `ex:dataOwner` directly in policies. This:
- Created domain-specific vocabulary outside the profile system
- Had no connection to the formal `resolve`/`deref` machinery
- Could not be validated or type-checked
- Duplicated concepts across different policies

With profile-declared operands:
- The privacy profile defines `privacy:dataOwnerOperand` once
- All GDPR-related policies reuse the same operand
- Resolution path `"asset.dataOwner"` is explicit
- SHACL can enforce that the operand is used with appropriate operators
- The operand can be swapped for different implementations (different asset schemas)

## Purpose as a Profile-Declared Operand

Note that `privacy:purposeOperand` shows how ODRL's built-in `odrl:purpose` becomes just another profile-declared operand in RL2:

```turtle
# Instead of magic ODRL vocabulary:
#   odrl:purpose "research"

# RL2 uses a declared, resolvable operand:
rl2:condition [
    a rl2:AtomicConstraint ;
    rl2:leftOperand privacy:purposeOperand ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperand privacy:Research
] .
```

This generalizes: **all contextual data access is uniform**, whether it's purpose, jurisdiction, consent status, or data ownership.

## Comparison

- **Manual processes:** Paper forms, identity verification
- **GDPR-specific tools:** Purpose-built, not generalizable
- **ODRL:** `odrl:purpose` as magic vocabulary, no formal resolution
- **RL2:** Profile-declared operands with explicit resolution paths
