# Use Case 14: Step-Up Authentication

**Pattern:** Condition + Remediation Obligation
**Identity Check:** `currentAgent` authentication level
**Category:** Financial Entitlements, Access Control

## Scenario

Access to "High Risk" documents requires MFA. If the user session is only "Password" authenticated, deny access unless they upgrade their authentication. Upon successful MFA, access is granted.

## Policy Intent

> "High-risk resources require MFA. Password-only sessions must step up to proceed."

## Key Characteristics

- Conditional access based on authentication level
- Remediation path (not just deny, but "deny with instructions")
- State change on successful authentication upgrade
- Session-level evaluation

## Why RL2?

RL2 models the **Condition** (`authLevel >= MFA`) and, if false, can return a `Deny` with a specific **Obligation** (perform MFA). Once the obligation is fulfilled, the state changes and the condition becomes true, enabling `Permit`.

ODRL can express "MFA required" but cannot model:
- The remediation path
- The state change upon authentication upgrade
- The obligation to perform a specific authentication action

## Profile-Declared Operands

```turtle
@prefix auth: <https://example.org/profile/auth#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

auth:authLevelOperand a rl2:LeftOperand ;
    rdfs:label "Authentication Level" ;
    rdfs:comment "Current session authentication level." ;
    rl2:resolutionPath "context.session.authenticationLevel" ;
    rdfs:range auth:AuthLevel .

auth:sessionMfaCompletedOperand a rl2:LeftOperand ;
    rdfs:label "MFA Completed" ;
    rdfs:comment "Whether MFA was completed in this session." ;
    rl2:resolutionPath "context.session.mfaCompleted" ;
    rdfs:range xsd:boolean .

auth:requestedResourceRiskLevelOperand a rl2:LeftOperand ;
    rdfs:label "Requested Resource Risk Level" ;
    rdfs:comment "Risk level of the resource being accessed in the current request." ;
    rl2:resolutionPath "request.resource.riskLevel" ;
    rdfs:range auth:RiskLevel .

# Authentication levels (ordered)
auth:PasswordOnly a auth:AuthLevel ; auth:levelValue 1 .
auth:MFA a auth:AuthLevel ; auth:levelValue 2 .
auth:HardwareToken a auth:AuthLevel ; auth:levelValue 3 .

# Risk levels
auth:LowRisk a auth:RiskLevel .
auth:HighRisk a auth:RiskLevel .

# Actions
auth:read a rl2:Action ;
    rdfs:label "Read" ;
    rdfs:comment "Read access to resources." .

auth:performMFA a rl2:Action ;
    rdfs:label "Perform MFA" ;
    rdfs:comment "Complete multi-factor authentication." .
```

## RL2 Model

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix auth: <https://example.org/profile/auth#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# High-risk document access with MFA requirement
ex:highRiskDocumentAccess a rl2:Privilege ;
    rl2:subject ex:Employee ;
    rl2:action auth:read ;
    rl2:object ex:HighRiskDocument ;
    rl2:condition [
        # MFA must be completed in this session
        a rl2:AtomicConstraint ;
        rl2:leftOperand auth:sessionMfaCompletedOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand true
    ] .

# Step-up duty: When accessing high-risk resource without MFA, must authenticate
# Note: Uses profile-declared operand for resource risk level instead of
# attempting to match on request action/object types
ex:stepUpAuthDuty a rl2:Duty ;
    rl2:subject ex:Employee ;
    rl2:action auth:performMFA ;
    rl2:object ex:AuthenticationSystem ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Requested resource is high-risk
            a rl2:AtomicConstraint ;
            rl2:leftOperand auth:requestedResourceRiskLevelOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef auth:HighRisk
        ] ;
        rl2:operand [
            # But MFA not yet completed
            a rl2:AtomicConstraint ;
            rl2:leftOperand auth:sessionMfaCompletedOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand false
        ]
    ] .
```

## Evaluation Flow

```
Access Request for High-Risk Document
                │
                ▼
       ┌────────────────────┐
       │ session.mfaCompleted │
       │       == true?      │
       └──────────┬──────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
        true             false
         │                 │
         ▼                 ▼
      PERMIT           DENY +
                       Duty: performMFA
                           │
                           ▼
                     User completes MFA
                           │
                           ▼
                  session.mfaCompleted = true
                           │
                           ▼
                       Re-evaluate
                           │
                           ▼
                        PERMIT
```

## Evaluation

| Scenario | Auth Level | MFA Completed | Result |
|----------|------------|---------------|--------|
| MFA session | MFA | true | PERMIT |
| Password session | Password | false | DENY + Step-up duty |
| After step-up | Password→MFA | true | PERMIT |

## Response Structure

When access is denied with a remediation path, the response includes:

```json
{
  "decision": "DENY",
  "obligations": [
    {
      "action": "performMFA",
      "target": "AuthenticationSystem",
      "reason": "High-risk resource requires MFA"
    }
  ],
  "remediation": {
    "type": "STEP_UP_AUTH",
    "requiredLevel": "MFA",
    "currentLevel": "Password"
  }
}
```

## Key Insight

Step-up authentication demonstrates the difference between:
- **Hard deny**: "You cannot access this" (no path forward)
- **Conditional deny**: "You cannot access this *yet*" (clear remediation)

RL2's obligation model makes the remediation path explicit and actionable.

## Comparison

| Aspect | ODRL | XACML | RL2 |
|--------|------|-------|-----|
| Condition expression | Limited | Full | Full |
| Remediation obligation | Not standard | Obligations element | Native Duty |
| State change tracking | Not supported | External | Built-in |
| Session context | Not built-in | Custom attributes | Profile operand |

## PNF Considerations

This use case requires:
- Session state access (`session.mfaCompleted`)
- Conditional evaluation (boolean check)
- Duty triggering on denial

All propositional. No transitive closure needed.
