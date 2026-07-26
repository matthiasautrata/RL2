# RL2 IR Design: Stack-Based Kernel

**Status:** Design rationale — refined and narrowed by **RL2_IR.md** (2026-07-25, SEM-4)  
**Date:** 2025-12-20  
**Alternative to:** Undefined IR in RL2_Architecture.md

> **Note (SEM-4, 2026-07-25).** The adopted IR (**RL2_IR.md**) takes the stack VM from this
> document but **scopes it to pure condition evaluation only**. In particular the
> `EMIT-PERMIT` / `EMIT-FORBID` / `EMIT-OBLIGATION` opcodes proposed below are **dropped**:
> emission is *derivation* (collecting a normative envelope under I/O logic), a set operation
> in the structured AST layer, not a stack effect. `resolveDecision` and clause matching live
> in the outer AST (tree-walk over `Clause = Norm ⊔ Promise`), and state changes are emitted
> as effect descriptions applied by a shell. This file is retained as design rationale for the
> Layer 0/1 stack machine; read **RL2_IR.md** for the normative IR design.

---

## Core Insight

When you need a minimal, verifiable, portable execution model, you end up reinventing Forth. The pattern recurs:

| System | Era | Stack-based? |
|--------|-----|--------------|
| PostScript | 1982 | Yes (Forth derivative) |
| JVM bytecode | 1995 | Yes |
| Bitcoin Script | 2009 | Yes (explicitly Forth-like) |
| WebAssembly | 2017 | Yes |
| Ethereum EVM | 2015 | Yes |

Stack machines are the natural target when you need **provable bounds and minimal TCB**.

---

## Why It Fits RL2

The derivation phase is concatenative by nature:

```
Push norms → Evaluate conditions (pure) → Filter → Produce envelope
```

A condition tree:

```turtle
ex:cond a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:and ;
    rl2:operand [ rl2:leftOperand ex:purpose ; rl2:constraintOperator rl2:eq ; rl2:rightOperand "research" ] ;
    rl2:operand [ rl2:leftOperand rl2:currentDateTime ; rl2:constraintOperator rl2:lte ; rl2:rightOperand "2025-12-31"^^xsd:date ] .
```

Compiles to:

```forth
: COND-17 ( env -- flag )
    "context.purpose" RESOLVE   "research" S=
    "state.Clock" RESOLVE       2025-12-31 DATE<=
    AND ;
```

Fifty lines of stack manipulation. No hidden state. Trivially auditable.

---

## Layered Verification Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Layer 2: RL2 Word Definitions                           │
│                                                         │
│   : PURPOSE-RESEARCH? "context.purpose" RESOLVE         │
│                       "research" S= ;                   │
│                                                         │
│   Verified by: stack-effect checking + property tests   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 1: RL2-Specific Primitives                        │
│                                                         │
│   RESOLVE  EMIT-PERMIT  EMIT-FORBID  MATCHES-EVENT?     │
│                                                         │
│   Verified by: Dafny requires/ensures                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 0: Forth VM Core                                  │
│                                                         │
│   DUP DROP SWAP AND OR NOT = < > IF THEN CALL           │
│                                                         │
│   Verified by: Dafny, extracted to Go                   │
│   Properties: termination, determinism, memory safety   │
└─────────────────────────────────────────────────────────┘
```

**Trust boundary**: Layer 0 + Layer 1 primitives. ~800-1000 lines of Dafny.

---

## Compilation Pipeline

```
            Compile-Time                          Runtime
            ────────────                          ───────
Policy.ttl ──→ [Compiler] ──→ RL2 Bytecode ──→ [Stack VM] ──→ NormativeAtoms
                   │                                │
                   └── ContextManifest              └── Env (path resolution)
                   └── TargetIndex
```

**The compiler** (offline, can be complex) produces bytecode.  
**The VM** (runtime, must be fast/correct) executes it.

---

## Scope: RL2 Subset vs Full FORTH

We need ~30% of FORTH's surface. That 30% is exactly the verifiable subset.

| Full FORTH Feature | RL2 Needs? | Rationale |
|--------------------|------------|-----------|
| Stack ops (DUP, DROP, SWAP, etc.) | **Yes** | Core evaluation |
| Arithmetic (+, -, *, /) | Minimal | Counting, limits |
| Comparisons (=, <, >, etc.) | **Yes** | Condition evaluation |
| Logic (AND, OR, NOT) | **Yes** | Condition composition |
| Conditionals (IF/THEN/ELSE) | **Yes** | Branching |
| Word definitions (:, ;) | **Yes** | Compiled policies |
| CREATE/DOES> metaprogramming | **No** | Not needed |
| Memory allocation (ALLOT, HERE) | **No** | Fixed structures only |
| I/O (EMIT, KEY, TYPE) | **No** | No interactive I/O |
| Floating point | **No** | Integers/dates suffice |
| String manipulation | Minimal | S= comparison only |
| File access | **No** | Offline compilation |
| Interactive REPL | **No** | Batch execution |
| Variables/Constants | Minimal | Env access via RESOLVE |

This minimal subset is what makes verification tractable.

---

## Primitive Set (~45 opcodes)

> **Note (SEM-4).** In the adopted design (**RL2_IR.md**) the `EMIT-PERMIT` / `EMIT-FORBID` /
> `EMIT-OBLIGATION` words in the table below are **removed** — emission is *derivation* in the
> AST layer, not a stack effect — leaving ~30 pure opcodes. The Dafny `Instr` sketch further
> down likewise predates that decision (its `IEmitPermit` / `IEmitForbid` cases are dropped).
> The remaining primitives (stack / compare / logic / control / `RESOLVE`) are unchanged.

| Category | Words |
|----------|-------|
| Stack | DUP DROP SWAP OVER ROT |
| Compare | = <> < <= > >= |
| Logic | AND OR NOT XOR |
| Control | IF ELSE THEN |
| Types | S= DATE<= URI= |
| RL2 | RESOLVE MATCHES-EVENT? EMIT-PERMIT EMIT-FORBID EMIT-OBLIGATION |

~500-800 lines of implementation. **You can read the entire TCB.**

---

## Dafny Core Sketch

```dafny
datatype Value = 
  | VBool(b: bool)
  | VInt(i: int) 
  | VString(s: string)
  | VDate(d: int)  // days since epoch
  | VURI(u: string)
  | VBottom        // ⊥

datatype Instr =
  | IDup | IDrop | ISwap | IOver | IRot
  | IAnd | IOr | INot
  | IEq | INeq | ILt | ILte | IGt | IGte
  | ILitBool(b: bool) | ILitInt(i: int) | ILitString(s: string)
  | IResolve        // ( path -- value )
  | IEmitPermit     // ( agent action asset -- )
  | IEmitForbid     // ( agent action asset -- )
  | IIf(thn: seq<Instr>, els: seq<Instr>)
  | ICall(word: nat)  // index into dictionary

datatype VM = VM(
  stack: seq<Value>,
  env: Env,
  output: seq<Atom>,
  fuel: nat          // bounded execution
)

function method Step(vm: VM, i: Instr): Result<VM>
  requires vm.fuel > 0
  ensures r.Ok? ==> r.value.fuel < vm.fuel  // progress
  ensures r.Ok? ==> |r.value.stack| <= |vm.stack| + 1  // bounded growth
{
  match i
  case IAnd => 
    if |vm.stack| < 2 then Err("underflow")
    else match (vm.stack[|vm.stack|-2], vm.stack[|vm.stack|-1])
      case (VBool(a), VBool(b)) => 
        Ok(vm.(stack := vm.stack[..|vm.stack|-2] + [VBool(a && b)],
               fuel := vm.fuel - 1))
      case _ => Err("type: AND expects bool bool")
  // ... ~40 more cases
}
```

Key invariants in `ensures` clauses:
- **Termination**: `fuel` decreases
- **Memory safety**: stack bounded
- **Determinism**: `Step` is a function, not a relation

---

## RESOLVE: The Escape Hatch

Where semantic complexity lives:

```dafny
function method Resolve(vm: VM, path: string): Result<Value>
  requires ValidPath(path)  // grammar check
  requires PathRootAllowed(path, vm.env)  // sandboxing
  ensures r.Ok? ==> ValueMatchesPathType(r.value, path)
{
  var segments := SplitPath(path);
  var root := match segments[0]
    case "agent" => vm.env.agent
    case "asset" => vm.env.asset
    case "state" => vm.env.state
    case "context" => vm.env.context
    case "request" => vm.env.request
    case _ => return Err("invalid root");
  
  FoldNavigate(root, segments[1..])
}
```

Preconditions enforce security constraints from RL2_Semantics.md §deref.

---

## Stack Effects as Types (Layer 2 Verification)

Words verified by stack-effect annotations:

```forth
\ Stack effect: ( -- flag )
: PURPOSE-RESEARCH?
    "context.purpose" RESOLVE   \ ( -- value )
    "research" S= ;             \ ( value -- flag )

\ Stack effect: ( -- flag )  
: TIME-VALID?
    "state.Clock" RESOLVE       \ ( -- date )
    2025-12-31 DATE<= ;         \ ( date -- flag )

\ Stack effect: ( -- )
: LOAN-POLICY
    PURPOSE-RESEARCH?           \ ( -- flag )
    TIME-VALID?                 \ ( -- flag flag )
    AND IF                      \ ( flag flag -- )
        ex:Alice ex:access ex:LoanPortfolio EMIT-PERMIT
    THEN ;
```

A simple checker verifies:
1. Stack doesn't underflow
2. Types match at each step
3. Words compose correctly

Decidable and fast. No SMT solver needed—just propagation.

---

## What This Solves

| Problem from fix.md | How Forth/Dafny Solves It |
|---------------------|---------------------------|
| IR undefined | IR = Forth bytecode (simple, portable) |
| Technology stack friction | Dafny → Go extraction |
| Verification timeline | Tiny verified core (~1000 lines) |
| Operational deployment | Go is cloud-native |
| Auditability | Can read entire VM source |

---

## Work Breakdown

**Phase 1: VM Core (2-3 weeks)**
- Dafny datatype definitions
- ~45 primitive implementations
- Proof of termination, determinism, memory safety
- Extract to Go, test

**Phase 2: RL2 Primitives (1-2 weeks)**
- RESOLVE with path validation
- EMIT-PERMIT, EMIT-FORBID, EMIT-OBLIGATION
- MATCHES-EVENT?
- Verify security properties

**Phase 3: Compiler (2-3 weeks)**
- Turtle → bytecode (tested, not verified)
- Stack-effect checker for words
- ContextManifest / TargetIndex generation

**Phase 4: Validation (1-2 weeks)**
- Run all 17 complete use cases
- Property-based testing on compiled output
- Performance benchmarks

**Total: 6-10 weeks** to working evaluator.

---

## Alternatives Considered

**Minimal Lisp kernel**: S-expressions instead of stack. Pros: familiar to more people, homoiconic. Cons: requires environment/closure semantics, GC concerns, harder to bound memory. Stack machines are simpler to verify.

**Direct AST interpreter**: No IR, evaluate RDF directly. Cons: No compilation benefit, harder to optimize, larger trusted surface.

**WASM as IR**: Use WebAssembly. Pros: existing tooling, portable. Cons: overkill for RL2's needs, larger spec surface, verification story unclear.

---

## Verification Landscape

Existing work and the gap we'd fill:

| Approach | Exists? | Limitation |
|----------|---------|------------|
| FORTH in Go | Yes (several) | Not verified |
| Verified FORTH in Coq/Isabelle | Some research | Extracts to OCaml/Haskell, not Go |
| Verified stack VM (EVM, Bitcoin Script) | Yes | C/Rust, testing not proofs |
| Verified FORTH in Dafny → Go | **No** | **This is the opportunity** |

The intersection of "needs verified stack VM" + "needs Go deployment" is small. Blockchain projects went with C/Rust for performance, accepted testing over verification. Academic verification extracts to functional languages.

### Dafny → Go Extraction Maturity

Dafny's Go backend is relatively recent (2021+, maturing). Recommended: small spike before committing.

```dafny
// spike.dfy - minimal test
datatype Value = VInt(i: int) | VBool(b: bool)

function method TestAnd(a: Value, b: Value): Result<Value>
  ensures r.Ok? ==> r.value.VBool?
{
  match (a, b)
  case (VBool(x), VBool(y)) => Ok(VBool(x && y))
  case _ => Err("type error")
}
```

Extract to Go, verify idiomatic output, benchmark. If clean, path is clear.

---

## Open Questions

1. **Bytecode serialization format**: Binary? Text? JSON array of opcodes?
2. **Dictionary structure**: How are compiled words indexed and looked up?
3. **Error reporting**: How do VM errors map back to source policies?
4. **Debugging**: Stack traces, breakpoints, step-through execution?

---

## References

- [Moving Forth](https://www.bradrodriguez.com/papers/moving1.htm) - Classic Forth implementation guide
- [Dafny Reference Manual](https://dafny.org/dafny/DafnyRef/DafnyRef)
- [Bitcoin Script](https://en.bitcoin.it/wiki/Script) - Minimal stack language for verification
- RL2_Semantics.md §deref, §Complexity and Constraints
