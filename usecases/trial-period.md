# Use Case 17: Trial Period Expiration

**Pattern:** State Transition on temporal boundary
**Identity Check:** License holder
**Category:** Software Licensing, Feature Gating

## Scenario

Software works with full features for 14 days. On day 15, it automatically reverts to "Read Only" mode. The `Execute` privilege deactivates, leaving only the `Read` privilege active.

## Policy Intent

> "Full access for 14-day trial. After expiration, read-only access only."

## Key Characteristics

- **State Transition** based on time
- Privilege degradation (full → limited)
- Automatic enforcement (no human intervention)
- Clear temporal boundary

## Why RL2?

Day 15 triggers a `StateTransition` that deactivates the `Execute` privilege, leaving only the `Read` privilege active.

ODRL can express "valid until date X" but cannot model:
- Partial capability degradation
- The transition from one access level to another
- Multiple privileges with different temporal bounds

## Profile-Declared Operands

```turtle
@prefix licensing: <https://example.org/profile/licensing#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

licensing:trialStartDateOperand a rl2:LeftOperand ;
    rdfs:label "Trial Start Date" ;
    rdfs:comment "Date when the trial period began." ;
    rl2:resolutionPath "license.trialStartDate" ;
    rdfs:range xsd:dateTime .

licensing:trialDaysRemainingOperand a rl2:LeftOperand ;
    rdfs:label "Trial Days Remaining" ;
    rdfs:comment "Days remaining in trial period." ;
    rl2:resolutionPath "license.trialDaysRemaining" ;
    rdfs:range xsd:integer .

licensing:licenseTypeOperand a rl2:LeftOperand ;
    rdfs:label "License Type" ;
    rdfs:comment "Current license type (trial, basic, pro)." ;
    rl2:resolutionPath "license.type" ;
    rdfs:range licensing:LicenseType .

# License types
licensing:Trial a licensing:LicenseType .
licensing:Expired a licensing:LicenseType .
licensing:Paid a licensing:LicenseType .
```

## RL2 Model

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix licensing: <https://example.org/profile/licensing#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Full access during active trial
ex:trialFullAccess a rl2:Privilege ;
    rl2:subject ex:TrialUser ;
    rl2:action ex:execute ;
    rl2:object ex:Application ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand licensing:trialDaysRemainingOperand ;
        rl2:constraintOperator rl2:gt ;
        rl2:rightOperand 0
    ] .

# Read-only access always available (trial or expired)
ex:readOnlyAccess a rl2:Privilege ;
    rl2:subject ex:TrialUser ;
    rl2:action ex:read ;
    rl2:object ex:Application .

# Prohibition: No execute after trial expires
ex:expiredTrialProhibition a rl2:Prohibition ;
    rl2:priority 100 ;
    rl2:subject ex:TrialUser ;
    rl2:action ex:execute ;
    rl2:object ex:Application ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand licensing:trialDaysRemainingOperand ;
        rl2:constraintOperator rl2:lteq ;
        rl2:rightOperand 0
    ] .

# Paid users always have full access
ex:paidFullAccess a rl2:Privilege ;
    rl2:priority 200 ;
    rl2:subject ex:PaidUser ;
    rl2:action ex:execute ;
    rl2:object ex:Application .
```

## State Transitions

```
License State Machine:

                     14 days elapse
    ┌────────────┐ ─────────────────▶ ┌─────────────┐
    │   TRIAL    │                    │   EXPIRED   │
    │            │                    │             │
    │ read: OK   │                    │ read: OK    │
    │ execute: OK│                    │ execute: NO │
    └────────────┘                    └──────┬──────┘
                                             │
                                             │ purchase
                                             ▼
                                      ┌─────────────┐
                                      │    PAID     │
                                      │             │
                                      │ read: OK    │
                                      │ execute: OK │
                                      └─────────────┘
```

## Evaluation

| Scenario | Days Remaining | Action | Result |
|----------|----------------|--------|--------|
| Day 1 | 13 | execute | PERMIT |
| Day 14 | 0 | execute | PERMIT (last day) |
| Day 15 | -1 | execute | DENY |
| Day 15 | -1 | read | PERMIT |
| After purchase | N/A (Paid) | execute | PERMIT |

## Feature-Level Granularity

For more granular feature gating:

```turtle
# Premium features: trial only for 7 days
ex:premiumFeaturesTrial a rl2:Privilege ;
    rl2:subject ex:TrialUser ;
    rl2:action ex:usePremiumFeature ;
    rl2:object ex:Application ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand licensing:trialDaysRemainingOperand ;
            rl2:constraintOperator rl2:gt ;
            rl2:rightOperand 7  # Only first 7 days
        ]
    ] .

# Basic features: full 14 days
ex:basicFeaturesTrial a rl2:Privilege ;
    rl2:subject ex:TrialUser ;
    rl2:action ex:useBasicFeature ;
    rl2:object ex:Application ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand licensing:trialDaysRemainingOperand ;
        rl2:constraintOperator rl2:gt ;
        rl2:rightOperand 0
    ] .
```

## Upgrade Path with Duty

```turtle
# Duty: Prompt for upgrade when trial expires
ex:upgradePromptDuty a rl2:Duty ;
    rl2:subject ex:Application ;
    rl2:action ex:showUpgradePrompt ;
    rl2:object ex:TrialUser ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand licensing:trialDaysRemainingOperand ;
        rl2:constraintOperator rl2:lteq ;
        rl2:rightOperand 0
    ] .
```

## Comparison

| Aspect | ODRL | RL2 |
|--------|------|-----|
| Time-limited permission | `odrl:dateTime` constraint | Temporal operand |
| Feature degradation | Multiple separate policies | Condition-based privilege |
| State representation | Not modeled | Explicit in Σ |
| Upgrade path | Not expressible | Duty on condition |

## PNF Considerations

This use case is straightforward:
- Temporal comparison (`daysRemaining > 0`)
- Simple propositional logic
- No transitive closure needed

The complexity is in **state derivation** (calculating `daysRemaining` from `trialStartDate`), which happens before PNF evaluation, not within it.

## Implementation Note

The `trialDaysRemaining` operand abstracts the calculation:

```
trialDaysRemaining = 14 - (now - trialStartDate).days
```

This calculation is performed by the resolution function, not by the policy evaluator. PNF sees a simple integer comparison.
