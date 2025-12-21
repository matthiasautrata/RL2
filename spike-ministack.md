# MiniStack Spike Specification

**Purpose:** Evaluate Dafny vs Stainless for RL2 verified kernel  
**Scope:** Minimal stack machine exercising key verification properties  
**Effort:** ~4 hours per implementation  
**Date:** 2025-12-20

---

## Overview

Implement a trivial stack VM in all three:
1. **Dafny** → extract to Go
2. **Stainless** → native Scala/JVM
3. **Why3/WhyML** → extract to OCaml

Compare: proof ergonomics, code clarity, output quality, tooling.

This is NOT the RL2 kernel. This is a decision spike.

---

## Abstract Syntax

### Values

```
Value ::= VBool(b: bool)
        | VInt(i: int)
```

Two types. Enough to exercise type checking in operations.

### Instructions

```
Instr ::= Push(v: Value)
        | Dup
        | Drop
        | Swap
        | Eq
        | Lte
        | And
        | Or
        | Not
        | IfElse(thn: List<Instr>, els: List<Instr>)
```

10 instructions. Minimal but complete for testing.

### Machine State

```
VM = {
    stack: List<Value>,
    fuel: nat
}
```

`fuel` bounds execution. Decreases on every step. Machine halts when fuel = 0.

### Result Type

```
Result<A> = Ok(value: A) | Err(msg: string)
```

Operations return `Result<VM>`. Errors for: underflow, type mismatch, fuel exhaustion.

---

## Operational Semantics

### Notation

- `s` = stack (list, head is top)
- `s[0]` = top of stack
- `s[1]` = second element
- `a :: s` = push `a` onto `s`
- `fuel'` = `fuel - 1`

### Step Function

```
step : (VM, Instr) → Result<VM>
```

**Precondition:** `vm.fuel > 0`

| Instruction | Precondition | Effect |
|-------------|--------------|--------|
| `Push(v)` | — | `stack' = v :: stack` |
| `Dup` | `|stack| >= 1` | `stack' = stack[0] :: stack` |
| `Drop` | `|stack| >= 1` | `stack' = tail(stack)` |
| `Swap` | `|stack| >= 2` | `stack' = stack[1] :: stack[0] :: tail(tail(stack))` |
| `Eq` | `|stack| >= 2`, same type | `stack' = VBool(stack[0] == stack[1]) :: tail(tail(stack))` |
| `Lte` | `|stack| >= 2`, both `VInt` | `stack' = VBool(stack[1] <= stack[0]) :: tail(tail(stack))` |
| `And` | `|stack| >= 2`, both `VBool` | `stack' = VBool(b0 && b1) :: tail(tail(stack))` |
| `Or` | `|stack| >= 2`, both `VBool` | `stack' = VBool(b0 \|\| b1) :: tail(tail(stack))` |
| `Not` | `|stack| >= 1`, `VBool` | `stack' = VBool(!b) :: tail(stack)` |
| `IfElse(t,e)` | `|stack| >= 1`, `VBool` | pop bool; run `t` if true, else `e` |

**All steps:** `fuel' = fuel - 1`

### Run Function

```
run : (VM, List<Instr>) → Result<VM>

run(vm, []) = Ok(vm)
run(vm, i :: rest) = 
    match step(vm, i) with
    | Err(e) → Err(e)
    | Ok(vm') → run(vm', rest)
```

---

## Properties to Verify

### P1: Termination

Every step decreases fuel.

```
∀ vm, i, vm' :
    step(vm, i) = Ok(vm') ⟹ vm'.fuel < vm.fuel
```

### P2: Determinism

Step is a function (same inputs → same outputs).

```
∀ vm, i :
    step(vm, i) = step(vm, i)
```

(Trivially true if step is implemented as a function, not a relation. The verification should confirm no hidden nondeterminism.)

### P3: Stack Bounds

Each instruction changes stack size by at most +1.

```
∀ vm, i, vm' :
    step(vm, i) = Ok(vm') ⟹ |vm'.stack| <= |vm.stack| + 1
```

### P4: Type Safety

Well-typed programs don't get stuck (they return Ok or a type error, never undefined behavior).

```
∀ vm, i :
    vm.fuel > 0 ⟹ step(vm, i) ∈ { Ok(_), Err("underflow"), Err("type:*") }
```

No crashes, panics, or undefined states.

### P5: Fuel Exhaustion

Zero fuel always fails.

```
∀ vm, i :
    vm.fuel = 0 ⟹ step(vm, i) = Err("fuel exhausted")
```

---

## Test Cases

### T1: Basic Arithmetic Comparison

```
program: [Push(3), Push(5), Lte]
initial: { stack: [], fuel: 10 }
expected: Ok({ stack: [VBool(true)], fuel: 7 })
```

### T2: Boolean Logic

```
program: [Push(true), Push(false), And]
initial: { stack: [], fuel: 10 }
expected: Ok({ stack: [VBool(false)], fuel: 7 })
```

### T3: Stack Manipulation

```
program: [Push(1), Push(2), Swap, Drop]
initial: { stack: [], fuel: 10 }
expected: Ok({ stack: [VInt(2)], fuel: 6 })
```

### T4: Conditional

```
program: [Push(true), IfElse([Push(1)], [Push(2)])]
initial: { stack: [], fuel: 10 }
expected: Ok({ stack: [VInt(1)], fuel: 7 })
```

### T5: Type Error

```
program: [Push(1), Push(true), And]
initial: { stack: [], fuel: 10 }
expected: Err("type: And expects bool bool")
```

### T6: Underflow

```
program: [Drop]
initial: { stack: [], fuel: 10 }
expected: Err("underflow: Drop requires 1 element")
```

### T7: Fuel Exhaustion

```
program: [Push(1), Push(2), Push(3)]
initial: { stack: [], fuel: 2 }
expected: Err("fuel exhausted")
```

### T8: Equality (Same Type)

```
program: [Push(5), Push(5), Eq]
initial: { stack: [], fuel: 10 }
expected: Ok({ stack: [VBool(true)], fuel: 7 })
```

### T9: Equality (Different Types)

```
program: [Push(1), Push(true), Eq]
initial: { stack: [], fuel: 10 }
expected: Err("type: Eq requires same types")
```

### T10: Compound Expression

Compute: `(3 <= 5) AND (NOT false)`

```
program: [
    Push(3),
    Push(5),
    Lte,           // stack: [true]
    Push(false),
    Not,           // stack: [true, true]
    And            // stack: [true]
]
initial: { stack: [], fuel: 20 }
expected: Ok({ stack: [VBool(true)], fuel: 14 })
```

---

## Deliverables

### Dafny Implementation

1. `ministack.dfy` — VM implementation with verification annotations
2. `ministack_test.dfy` — Test cases as lemmas/assertions
3. `make go` — Extract to Go
4. `ministack-go/` — Generated Go code

### Stainless Implementation

1. `MiniStack.scala` — VM implementation with Stainless annotations
2. `MiniStackTest.scala` — Test cases
3. `sbt compile` — Verify and compile
4. `target/` — JVM bytecode

### Why3/WhyML Implementation

1. `MiniStack.mlw` — VM implementation with Why3 contracts
2. Test module included in same file
3. `make verify` — Prove with Alt-Ergo/Z3/CVC4
4. `make extract` — Extract to OCaml

---

## Evaluation Criteria

Score 1-5 for each:

| Criterion | Dafny | Stainless | WhyML | Notes |
|-----------|-------|-----------|-------|-------|
| **Code clarity** | | | | Can you read it cold in 5 min? |
| **Proof annotations** | | | | How much ceremony for P1-P5? |
| **Error messages** | | | | When proof fails, debuggable? |
| **IDE experience** | | | | Autocomplete, inline errors? |
| **Build friction** | | | | Setup, dependencies, compile time? |
| **Output quality** | | | | Is extracted code idiomatic? |
| **Prover flexibility** | | | | Multiple provers, fallback options? |
| **Ecosystem fit** | | | | Libraries, community, docs? |

### Decision Rubric

| Outcome | Recommendation |
|---------|----------------|
| Dafny wins clearly | Use Dafny → Go |
| Stainless wins clearly | Use Stainless, JVM deployment |
| WhyML wins clearly | Use Why3 → OCaml |
| Tie, Go preferred | Use Dafny |
| Tie, JVM acceptable | Use Stainless (no extraction) |
| Tie, OCaml acceptable | Use WhyML |
| All three unacceptable | Go + property testing (sacrifice formal guarantees) |

---

## Timeline

| Task | Effort |
|------|--------|
| Dafny setup + implementation | 2 hours |
| Dafny proofs + extraction | 2 hours |
| Stainless setup + implementation | 2 hours |
| Stainless proofs | 2 hours |
| WhyML setup + implementation | 2 hours |
| WhyML proofs + extraction | 2 hours |
| Comparison writeup | 1 hour |
| **Total** | ~1.5 days |

---

## Notes

- This spike is deliberately trivial. If verification is hard here, it will be harder on the real kernel.
- The RL2 kernel will add: `RESOLVE`, `EMIT-*`, strings, dates, URIs. But the core VM structure is the same.
- Focus on proof ergonomics, not performance. We're choosing a verification tool, not a runtime.

---

## References

- [Dafny Documentation](https://dafny.org/dafny/)
- [Dafny Go Backend](https://dafny.org/dafny/Compilation/Go)
- [Stainless Documentation](https://epfl-lara.github.io/stainless/)
- [design-forth-ir.md](design-forth-ir.md) — Full RL2 kernel design
