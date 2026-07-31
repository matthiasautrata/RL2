# Use Case 45: Negated Condition

**Pattern:** Unless / except clause  
**Vocabulary Demonstrated:** `not` operator  
**Category:** Vocabulary Completeness  
**Status:** DRAFT

---

## Business Context

Policies often include exceptions using negation:

- "Permitted UNLESS revoked"
- "Allowed EXCEPT during maintenance"
- "Access granted IF NOT on blocklist"

Negation inverts a condition's truth value.

## Scenario

A system permits access unless the user is on a suspension list:

> "Users may access the platform UNLESS their account is suspended."

## Policy Intent

> "Access is PERMITTED if NOT(account is suspended)."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Operator | Logical NOT |
| Input | Single condition |
| Output | Inverted truth value |
| Use case | Exceptions, blocklists |

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Access Platform                          │
│  ─────────────────────────────────────────────────  │
│  Subject: User                                       │
│  Action: access                                      │
│  Object: Platform                                    │
│  Condition:                                          │
│    NOT(accountStatus = Suspended)                    │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

```
Given condition C

not(C) evaluates to:
  - TRUE if C is FALSE
  - FALSE if C is TRUE

Request: User with accountStatus = Active
  - accountStatus = Suspended? FALSE
  - not(FALSE) = TRUE → PERMIT

Request: User with accountStatus = Suspended
  - accountStatus = Suspended? TRUE
  - not(TRUE) = FALSE → DENY
```

## Common Negation Patterns

| Pattern | Expression |
|---------|------------|
| Blocklist | `not(user isAnyOf blocklist)` |
| Maintenance window | `not(currentTime between start and end)` |
| Revocation check | `not(privilege.revoked = true)` |
| Exception | `not(exceptionCondition)` |

## Combining NOT with Other Operators

```turtle
@prefix account: <https://example.org/profile/account#> .

# Access if NOT(suspended) AND NOT(terminated)
ex:combinedAccess a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Platform ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:LogicalConstraint ;
            rl2:constraintOperator rl2:not ;
            rl2:operand [
                a rl2:AtomicConstraint ;
                rl2:leftOperand account:accountStatusOperand ;
                rl2:constraintOperator rl2:eq ;
                rl2:rightOperandRef account:Suspended
            ]
        ] ;
        rl2:operand [
            a rl2:LogicalConstraint ;
            rl2:constraintOperator rl2:not ;
            rl2:operand [
                a rl2:AtomicConstraint ;
                rl2:leftOperand account:accountStatusOperand ;
                rl2:constraintOperator rl2:eq ;
                rl2:rightOperandRef account:Terminated
            ]
        ]
    ] .
```

## NOT Cardinality

Unlike `and`/`or`/`xone` which take multiple operands, `not` takes exactly one:

| Operator | Operand Count |
|----------|---------------|
| `and` | 2+ |
| `or` | 2+ |
| `xone` | 2+ |
| `not` | Exactly 1 |

## Alternative: neq Operator

Simple inequality can use `neq` instead of `not`:

```turtle
@prefix account: <https://example.org/profile/account#> .

# These two privileges are equivalent for simple cases.

# Using NOT(status = Suspended)
ex:accessViaNot a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Platform ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:not ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand account:accountStatusOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef account:Suspended
        ]
    ] .

# Using status != Suspended (simpler)
ex:accessViaNeq a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Platform ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand account:accountStatusOperand ;
        rl2:constraintOperator rl2:neq ;
        rl2:rightOperandRef account:Suspended
    ] .
```

Use `not` when negating complex conditions; use `neq` for simple inequality.

## Profile Requirements

```turtle
@prefix account: <https://example.org/profile/account#> .

account:accountStatusOperand a rl2:LeftOperand ;
    rl2:resolutionPath "agent.accountStatus" .

account:Active a account:AccountStatus .
account:Suspended a account:AccountStatus .
account:Terminated a account:AccountStatus .
```

---

## RL2 Model

The canonical form: access is permitted unless the account is suspended.

```turtle
@prefix account: <https://example.org/profile/account#> .

ex:platformAccess a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Platform ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:not ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand account:accountStatusOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef account:Suspended
        ]
    ] .
```

---

## References

- ODRL Vocabulary — Logical operators
- Boolean logic in policy languages
- Exception handling patterns
