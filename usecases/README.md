# RL2 Use Cases

This folder contains use cases demonstrating RL2's capabilities, particularly duty state preconditions using the **Unified State Approach** (explicit AtomicConstraints rather than a specialized DutyConstraint class).

## Use Case Index

### Core Patterns (1-10)

| # | Name | Pattern | Identity Check | File |
|---|------|---------|----------------|------|
| 1 | Pay-to-Play | Tun-sollen | `dutyPerformer = currentAgent` | [pay-to-play.md](pay-to-play.md) |
| 2 | Team License | Sein-sollen | (none) | [team-license.md](team-license.md) |
| 3 | Break Glass (Liability) | Event + Identity | `operationalAgent = currentAgent` | [break-glass.md](break-glass.md) |
| 4 | Fire Alarm Evacuation | Event, decoupled | (none) | [fire-alarm.md](fire-alarm.md) |
| 5 | Wire Transfer (Two-Man Rule) | Separation of Duty | `dutyPerformer ≠ currentAgent` | [wire-transfer-sod.md](wire-transfer-sod.md) |
| 6 | Check Signing (Dynamic SoD) | Separation of Duty | `dutyPerformer ≠ currentAgent` | [check-signing-sod.md](check-signing-sod.md) |
| 7 | Ethics Board Approval | Multi-party workflow | `operationalAgent = currentAgent` | [ethics-approval.md](ethics-approval.md) |
| 8 | Data Stewardship Promise | Promise fulfillment | `promisor = currentAgent` | [data-stewardship.md](data-stewardship.md) |
| 9 | GDPR Right to Erasure | Data subject rights | attribute matching | [gdpr-erasure.md](gdpr-erasure.md) |
| 10 | Audit Trail Requirement | Compliance | (none) | [audit-trail.md](audit-trail.md) |

### Data Contracts & SLAs (11-13)

| # | Name | Pattern | Domain | File |
|---|------|---------|--------|------|
| 11 | Data Freshness Promise | Promise + violation | Data Contracts | [data-freshness-promise.md](data-freshness-promise.md) |
| 12 | Schema Evolution Lock | Event + temporal duty | Data Contracts | [schema-evolution.md](schema-evolution.md) |
| 13 | Quality Circuit Breaker | State transition | Data Contracts | [quality-circuit-breaker.md](quality-circuit-breaker.md) |

### Financial Entitlements (14-15)

| # | Name | Pattern | Domain | File |
|---|------|---------|--------|------|
| 14 | Step-Up Authentication | Condition + obligation | Access Control | [step-up-auth.md](step-up-auth.md) |
| 15 | Chinese Wall (Embargo) | Event-based expiry | Conflict of Interest | [chinese-wall.md](chinese-wall.md) |

### Software Licensing (16-17)

| # | Name | Pattern | Domain | File |
|---|------|---------|--------|------|
| 16 | Concurrent Seat Licensing | Global state | Licensing | [concurrent-seats.md](concurrent-seats.md) |
| 17 | Trial Period Expiration | Temporal state transition | Licensing | [trial-period.md](trial-period.md) |

## Design Approach: Unified State

RL2 uses **explicit AtomicConstraints** to query duty state, rather than a specialized `DutyConstraint` class with a "magic" `SubjectScope` enum.

### Why This Approach?

1. **De-Magicing:** Identity binding is an explicit logical proposition (`performer = agent`), not a hidden enum interpretation
2. **Regularity:** Norm state is just another queryable property of Σ, like `dateTime`
3. **Parsimony:** No new classes or enumerations needed
4. **Expressiveness:** Supports patterns impossible with a fixed enum (e.g., specific agent)
5. **Decidability:** All logic is explicit in the policy graph

### Key LeftOperands

| LeftOperand | Queries | Returns |
|-------------|---------|---------|
| `rl2:obligationStateOperand` | `Σ.ObligationState(targetNorm)` | Pending, Active, Fulfilled, Violated |
| `rl2:dutyPerformerOperand` | `Σ.DutyPerformer(targetNorm)` | Agent who fulfilled, or ⊥ |

### Identity Binding Patterns

| Pattern | Equivalent To | Implementation |
|---------|---------------|----------------|
| "By anyone" | AnySubject | Check `obligationState = Fulfilled` only |
| "By me" | SameSubject | Add `dutyPerformer = currentAgent` |
| "By someone else" | DifferentSubject | Add `dutyPerformer ≠ currentAgent` |
| "By Bob specifically" | (impossible before) | Add `dutyPerformer = ex:Bob` |

## Theoretical Foundation

### Deontic Logic: Tun-sollen vs. Sein-sollen

| German Term | English | RL2 Implementation |
|-------------|---------|-------------------|
| *Tun-sollen* | Ought-to-do | `obligationState = Fulfilled` AND `dutyPerformer = currentAgent` |
| *Sein-sollen* | Ought-to-be | `obligationState = Fulfilled` (only) |

RL2 operationalizes this classical distinction from normative philosophy through explicit constraint composition.

### Comparison with Other Standards

| Standard | Agency/State Handling | RL2 Advantage |
|----------|----------------------|---------------|
| **ODRL** | Implied via nesting (SameSubject assumed) | Explicit `eq`/`neq` constraints |
| **XACML** | Manual attribute matching, verbose | Same verbosity, but with semantic clarity |
| **UCON** | System vs. user attributes | Unified model via LeftOperands |
| **RBAC/NIST** | Separation of Duty as separate concept | Natural via `neq` operator |

### The Verbosity Trade-off

The explicit approach is more verbose (3 objects vs. 1), but:

- Every piece of logic is explicit in the graph
- No hidden evaluator semantics
- Formally decidable by static analysis
- This is the correct trade-off for a rigorous normative language

## Canonical Pattern

### Duty State as Precondition (Tun-sollen)

```turtle
ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Resource ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check 1: Is the duty fulfilled?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:obligationStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand rl2:Fulfilled
        ] ;
        rl2:operand [
            # Check 2: Did I fulfill it?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:dutyPerformerOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

## RL2 vs ODRL: When Each Applies

| Capability | ODRL 2.2 | RL2 |
|------------|----------|-----|
| Static permissions | Excellent | Supported |
| Static prohibitions | Excellent | Supported |
| Purpose constraints | Native (`odrl:purpose`) | Profile operand |
| Spatial constraints | Native | Profile operand |
| **Provider obligations** | Awkward | Native (Promise) |
| **Event-based conditions** | Not supported | EventConstraint |
| **State transitions** | Not supported | NormState machine |
| **Identity binding** | Implied (SameSubject) | Explicit constraints |
| **Temporal monitoring** | Limited | `currentDateTime` constraints |
| **Violation detection** | Not supported | State tracking |

**Guidance:** Use cases 11-17 demonstrate patterns that require RL2's operational semantics. Static access control (purpose, geofencing) can be modeled in either, but RL2 provides a unified approach.

## Note on Use Case Files

The individual use case files (pay-to-play.md, etc.) have been updated to use the **Unified State Approach** (explicit constraint pattern) as defined in the v0.4 implementation. They demonstrate the rigorous, explicit modeling of identity binding and state preconditions.
