# Use Case 7: Ethics Board Approval

**Pattern:** Multi-party workflow with identity binding
**Identity Check:** `eventBeneficiaryOperand = currentAgent`
**Category:** Research governance, IRB compliance

## Scenario

A researcher must obtain ethics board approval before accessing sensitive research data. The approval is granted to a specific researcher, not transferable.

## Policy Intent

> "If the ethics board approved YOUR request, YOU may access."

## Key Characteristics

- Named individual approval
- Non-transferable grant
- Audit trail for compliance
- Common in IRB/ethics workflows

## Profile-Declared Operands

This use case requires a research governance profile that declares operands for accessing approval event properties. All context access goes through the canonical path mechanism.

```turtle
@prefix research: <https://example.org/profile/research#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Profile-declared operand for the beneficiary of an approval event
# The approval event payload contains a 'beneficiary' field indicating
# the agent for whom approval was granted
research:eventBeneficiaryOperand a rl2:LeftOperand ;
    rdfs:label "Event Beneficiary" ;
    rdfs:comment """Resolves to the agent who is the beneficiary of an approval event.
    This is the researcher for whom ethics approval was granted.""" ;
    rl2:resolutionPath "state.Events.EthicsApprovalEvent.beneficiary" ;
    rdfs:range rl2:Agent .

# Profile-declared operand for approval expiration
research:approvalExpirationOperand a rl2:LeftOperand ;
    rdfs:label "Approval Expiration" ;
    rdfs:comment "Resolves to the expiration timestamp of the approval." ;
    rl2:resolutionPath "state.Events.EthicsApprovalEvent.expirationDate" ;
    rdfs:range xsd:dateTime .

# Profile-declared operand for current datetime
research:currentDateTimeOperand a rl2:LeftOperand ;
    rdfs:label "Current DateTime" ;
    rdfs:comment "Resolves to the current evaluation timestamp." ;
    rl2:resolutionPath "context.now" ;
    rdfs:range xsd:dateTime .

# Actions
research:access a rl2:Action ;
    rdfs:label "Access" ;
    rdfs:comment "Access to research datasets." .
```

## RL2 Model (Unified State Approach)

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix research: <https://example.org/profile/research#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:EthicsApprovalEvent a rl2:Event ;
    rl2:approver ex:EthicsBoard ;
    rdfs:comment "Approval from ethics board for specific researcher" .

ex:sensitiveDataAccess a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action research:access ;
    rl2:object ex:SensitiveDataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check 1: Has approval event occurred?
            a rl2:EventConstraint ;
            rl2:expectsEvent ex:EthicsApprovalEvent
        ] ;
        rl2:operand [
            # Check 2: Was approval for me (current agent)?
            # Uses profile-declared operand with explicit resolution path
            a rl2:AtomicConstraint ;
            rl2:leftOperand research:eventBeneficiaryOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ] ;
        rl2:operand [
            # Check 3: Is approval still valid?
            # Uses profile-declared operand comparing current time to expiration
            a rl2:AtomicConstraint ;
            rl2:leftOperand research:currentDateTimeOperand ;
            rl2:constraintOperator rl2:lt ;
            rl2:rightOperandRef research:approvalExpirationOperand
        ]
    ] .
```

## Resolution Semantics

When evaluating the identity binding condition:

1. `research:eventBeneficiaryOperand` has `rl2:resolutionPath "state.Events.EthicsApprovalEvent.beneficiary"`
2. `resolve(research:eventBeneficiaryOperand, Env, ⊥)` calls `deref("state.Events.EthicsApprovalEvent.beneficiary", Env)`
3. This navigates: `Env.Σ.Events[EthicsApprovalEvent].beneficiary` → returns the approved researcher (most recent matching EthicsApprovalEvent)
4. `rl2:currentAgent` resolves to `Env.Agent`
5. Constraint holds if these are equal

## Evaluation

| Scenario | Approval For | Request By | Result |
|----------|--------------|------------|--------|
| Approved researcher | Alice | Alice | PERMIT |
| Colleague sharing | Alice | Bob | DENY |
| Expired approval | Alice (2024) | Alice | DENY |

## Multi-Approval Variant

For N-of-M approval (e.g., 2 of 3 committee members), the profile would declare a function-based operand:

```turtle
research:approvalCountOperand a rl2:LeftOperand ;
    rdfs:label "Approval Count" ;
    rdfs:comment "Counts approvals for the current agent from committee members." ;
    rl2:resolutionFunction "countApprovalsForAgent" ;
    rdfs:range xsd:integer .
```

Policy usage:
```turtle
ex:multiApprovalAccess a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action research:access ;
    rl2:object ex:SensitiveDataset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand research:approvalCountOperand ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperand 2
    ] .
```

The `countApprovalsForAgent` function is implementation-specific but its interface is declared in the profile.

## Why Profile-Declared Operands?

Previous versions introduced `rl2:eventBeneficiary` as an ad-hoc property. This:
- Polluted the RL2 Core ontology
- Had no formal grounding in `resolve`/`deref`
- Could not be validated by SHACL
- Created maintenance burden

With profile-declared operands:
- The research governance profile owns `research:eventBeneficiaryOperand`
- Resolution path is explicit and auditable
- SHACL can verify usage constraints
- Different profiles can use different field names for the same concept

## Comparison

- **Paper-based:** Manual verification, error-prone
- **XACML:** Complex attribute matching, no event model
- **RL2:** `EventConstraint` + profile-declared operand with resolution path + temporal bounds
