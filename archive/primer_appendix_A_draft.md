
---

## Appendix A: ODRL Mapping Reference

This appendix provides detailed mapping tables for translating ODRL 2.2 policies to RL2. For transpilation patterns and worked examples, see **usecases/**.

### A.1 Structural Mapping

| ODRL Concept | RL2 Equivalent | Notes |
|:-------------|:---------------|:------|
| Policy | `rl2:Policy` | Direct mapping |
| Rule | `rl2:Norm` | "Rule" is syntactic; "Norm" is semantic |
| Permission | `rl2:Privilege` | Hohfeldian term for "permission" |
| Prohibition | `rl2:Prohibition` | Direct mapping |
| Duty | `rl2:Duty` | Direct mapping |
| Asset | `rl2:Asset` | Direct mapping |
| Party | `rl2:Agent` | Direct mapping |
| Action | `rl2:Action` | Direct mapping |
| Constraint | `rl2:Condition` | RL2 distinguishes AtomicConstraint, LogicalConstraint, EventConstraint |

### A.2 Property Mapping

| ODRL Property | RL2 Property | Semantics |
|:--------------|:-------------|:----------|
| `assignee` | `rl2:subject` | Agent bearing the norm |
| `assigner` | `rl2:counterparty` | Agent to whom duty is owed |
| `target` | `rl2:object` | Asset acted upon |
| `action` | `rl2:action` | Operation being regulated |
| `constraint` | `rl2:condition` | Activation requirements |
| `refinement` | `rl2:condition` | Nested conditions on assets/actions |
| `relation` | `rl2:refines` | Links Asset to Collection |
| `consequence` | State-triggered Duty | Duty conditioned on violation state |
| `remedy` | State-triggered Duty | Duty conditioned on prohibition violation |

### A.3 Operator Mapping

| ODRL Operator | RL2 Operator | Type |
|:--------------|:-------------|:-----|
| `eq`, `neq` | `rl2:eq`, `rl2:neq` | Comparison |
| `lt`, `lte`, `gt`, `gte` | `rl2:lt`, `rl2:lte`, `rl2:gt`, `rl2:gte` | Comparison |
| `isA` | `rl2:isA` | Semantic |
| `isAnyOf`, `isAllOf` | `rl2:isAnyOf`, `rl2:isAllOf` | Set |
| `isNoneOf` | `rl2:isNoneOf` | Set |
| `and`, `or`, `xone` | `rl2:and`, `rl2:or`, `rl2:xone` | Logical |

### A.4 Key Transpilation Patterns

#### Permission-Bound Duties

ODRL embeds duties inside permissions to imply "you can do X if you do Y." RL2 decouples these:

1. Extract the duty as a standalone norm
2. Add a condition to the privilege checking duty state
3. Make identity binding explicit (ODRL implies SameSubject)

See **usecases/pay-to-play.md** for the complete pattern.

#### Inheritance (`inheritFrom`)

RL2 performs compile-time flattening:
- Recursively resolve parent policies
- Union all clauses
- Output self-contained policy with no external dependencies

#### Consequences and Remedies

RL2 models these as state-triggered duties:
- The remedial duty has `rl2:obligationState rl2:Pending`
- Its condition checks `rl2:obligationStateOperand eq rl2:Violated` on the original duty

See **usecases/quality-circuit-breaker.md** for violation chains.

### A.5 ODRL Ambiguities Resolved by RL2

| Ambiguity | ODRL Behavior | RL2 Resolution |
|:----------|:--------------|:---------------|
| Party roles | `assigner`/`assignee` overloaded | Split into normative (subject/counterparty) and functional (grantor/grantee) roles |
| Duty semantics | Conflates obligation and condition | Duty = norm with lifecycle; Condition = logic gate |
| Identity binding | Implicit SameSubject assumption | Explicit via `dutyPerformerOperand` constraint |
| Evaluation | Underspecified | Formal operational semantics in RL2_Semantics.md |

### A.6 RL2 Extensions Beyond ODRL

| Capability | ODRL 2.2 | RL2 |
|:-----------|:---------|:----|
| Event-based conditions | Not supported | `rl2:EventConstraint` |
| Duty lifecycle tracking | Implicit | Explicit state machine (Pending→Active→Fulfilled/Violated) |
| Identity binding patterns | Implied | Explicit `dutyPerformerOperand` with `eq`/`neq` |
| Promises | Not supported | First-class `rl2:Promise` |
| Hohfeldian relations | Partial (Permission, Prohibition, Duty) | Full (adds Claim, Power, Liability, Immunity) |
| Violation detection | Not supported | State tracking with `rl2:Violated` |

---

*End of Appendix A*
