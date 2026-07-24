# Use Case 8: Data Stewardship Promise

**Pattern:** Promise fulfillment as precondition (Tun-sollen)
**Identity Check:** `promisorOperand = currentAgent`
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

## Profile-Declared Operands

This use case requires a profile that declares operands for accessing promise attributes. Like event performer binding, promise identity binding uses the canonical resolution path mechanism.

```turtle
@prefix governance: <https://example.org/profile/governance#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Profile-declared operand for the promisor of the stewardship promise
governance:promisorOperand a rl2:LeftOperand ;
    rdfs:label "Promisor" ;
    rdfs:comment """Resolves to the agent who made the stewardship promise.
    Used for identity binding to ensure the requester is the promisor.""" ;
    rl2:resolutionPath "state.Promises.stewardshipPromise.promisor" ;
    rdfs:range rl2:Agent .

# Profile-declared operand for promise state
governance:promiseStateOperand a rl2:LeftOperand ;
    rdfs:label "Promise State" ;
    rdfs:comment "Resolves to the current state of a promise." ;
    rl2:resolutionPath "state.Promises.stewardshipPromise.state" ;
    rdfs:range rl2:PromiseState .
```

## RL2 Model (Unified State Approach)

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix governance: <https://example.org/profile/governance#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:stewardshipPromise a rl2:Promise ;
    rl2:promisor ex:Researcher ;
    rl2:promisee ex:DataOwner ;
    rl2:promisedAction ex:steward ;      # Tun-sollen: commit to stewarding the data
    rl2:object ex:SensitiveData ;
    rl2:promiseState rl2:Pending .

ex:dataAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:SensitiveData ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check 1: Is the promise fulfilled?
            a rl2:AtomicConstraint ;
            rl2:leftOperand governance:promiseStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:Fulfilled   # state enum is an IRI → rightOperandRef
        ] ;
        rl2:operand [
            # Check 2: Am I the promisor?
            # Uses profile-declared operand with explicit resolution path
            a rl2:AtomicConstraint ;
            rl2:leftOperand governance:promisorOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

## Resolution Semantics

When evaluating the identity binding condition:

1. `governance:promisorOperand` has `rl2:resolutionPath "state.Promises.stewardshipPromise.promisor"`
2. `resolve(governance:promisorOperand, Env, ⊥)` calls `deref("state.Promises.stewardshipPromise.promisor", Env)`
3. This navigates: `Env.Σ.Promises["stewardshipPromise"].promisor` → returns the promisor agent
4. `rl2:currentAgent` resolves to `Env.Agent`
5. Constraint holds if these are equal (Tun-sollen identity binding)

## Promise vs. Duty

| Aspect | Promise | Duty |
|--------|---------|------|
| Origin | Voluntary | Imposed |
| Counterparty | Specific promisee | May be abstract |
| Lifecycle | Pending → Fulfilled (or Violated) | Pending → Active → Fulfilled (or Violated) |
| Semantics | Cooperative commitment | Normative obligation |
| Identity Binding | `promisorOperand = currentAgent` | `dutyPerformerOperand = currentAgent` |

## Evaluation

| Scenario | Promise By | Promise State | Request By | Result |
|----------|------------|---------------|------------|--------|
| Committed | Alice | Fulfilled | Alice | PERMIT |
| Not yet committed | Alice | Pending | Alice | DENY |
| Wrong person | Alice | Fulfilled | Bob | DENY |

## Why Profile-Declared Operands?

Previous versions used ad-hoc properties like `ex:promisorId`. This bypassed the formal `resolve`/`deref` machinery.

With profile-declared operands:
- The governance profile owns `governance:promisorOperand`
- Resolution path is explicit and auditable
- Pattern parallels duty performer binding (`rl2:dutyPerformerOperand`)
- SHACL can verify correct usage

## Promise Theory Context

From Burgess & Bergstra: Promises are **autonomous** commitments. Unlike duties (imposed externally), promises reflect the promisor's voluntary intention.

RL2 distinguishes these normatively while allowing both to serve as preconditions. The identity binding mechanism is consistent across both:
- Duties: `rl2:dutyPerformerOperand` (core operand querying Σ.DutyPerformer)
- Promises: `governance:promisorOperand` (profile operand querying Σ.Promises)

## Comparison

- **ODRL:** No promise concept; would use duty
- **Smart Contracts:** Promises as executable code
- **RL2:** Native Promise class with lifecycle tracking + profile-declared identity binding
