# Use Case 8: Data Stewardship Promise

**Pattern:** Promise fulfillment as precondition (Tun-sollen)
**Identity Check:** `promisor = currentAgent`
**Category:** Data governance, trust frameworks

## Scenario

A researcher must make (and keep) a data stewardship promise before accessing sensitive data. The promise is a voluntary commitment, not an imposed duty.

## Policy Intent

> "If YOU promised to be a good steward, YOU may access."

## Key Characteristics

- Voluntary commitment (Promise, not Duty)
- Personal accountability
- Trust-based access control
- Promise Theory integration

## RL2 Model (Unified State Approach)

```turtle
ex:stewardshipPromise a rl2:Promise ;
    rl2:promisor ex:Researcher ;
    rl2:promisee ex:DataOwner ;
    rl2:promiseContent ex:DataStewardshipCommitment ;
    rl2:promiseState rl2:PromisePending .

ex:dataAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:SensitiveData ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check 1: Is the promise fulfilled?
            a rl2:Condition ;
            rl2:requires ex:stewardshipPromise
        ] ;
        rl2:operand [
            # Check 2: Am I the promisor?
            a rl2:AtomicConstraint ;
            rl2:leftOperand ex:promisorId ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

Note: For promises, the identity check compares the promisor attribute against the current agent, similar to duty performer tracking.

## Promise vs. Duty

| Aspect | Promise | Duty |
|--------|---------|------|
| Origin | Voluntary | Imposed |
| Counterparty | Specific promisee | May be abstract |
| Lifecycle | PromisePending → PromiseFulfilled | Pending → Active → Fulfilled |
| Semantics | Cooperative commitment | Normative obligation |

## Evaluation

| Scenario | Promise By | Promise State | Request By | Result |
|----------|------------|---------------|------------|--------|
| Committed | Alice | Fulfilled | Alice | PERMIT |
| Not yet committed | Alice | Pending | Alice | DENY |
| Wrong person | Alice | Fulfilled | Bob | DENY |

## Promise Theory Context

From Burgess & Bergstra: Promises are **autonomous** commitments. Unlike duties (imposed externally), promises reflect the promisor's voluntary intention.

RL2 distinguishes these normatively while allowing both to serve as preconditions.

## Comparison

- **ODRL:** No promise concept; would use duty
- **Smart Contracts:** Promises as executable code
- **RL2:** Native Promise class with lifecycle tracking + identity binding
