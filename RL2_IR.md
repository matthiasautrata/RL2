---
title: "RL2 Intermediate Representation"
subtitle: "Compilation Target, Construct Correspondence, and Equivalence Obligation"
version: "0.8"
status: "Draft"
date: 2026-07-29
---

# RL2 Intermediate Representation

This document defines the RL2 **intermediate representation (IR)** — the target of
`compile : PolicyUniverse → (CompiledUniverse, ContextManifest)` — and the equivalence obligation that ties IR evaluation back to
the denotational semantics. It closes the "IR = TBD" gap in **RL2_Architecture.md** and
supplies the object every downstream reasoning step (differential testing, review, a future
implementation) works against.

This is a **design specification**: it fixes the datatypes, the evaluation rules, the
construct correspondence, and the theorem statements. Datatype/function definitions below use
Dafny-like algebraic-datatype notation purely as precise pseudocode — the project's current
scope is specification, not a mechanized proof or a committed implementation language (see
**SCOPE-1**, `issues.md`). For the formal semantics this IR refines, see **RL2_Semantics.md**;
for the architectural pipeline, **RL2_Architecture.md**; **research/design-forth-ir.md**
records the earlier stack-VM design this document superseded (SCOPE-1, 2026-07-29) and is
retained for historical rationale only.

---

## 1. Purpose and Scope

`compile : PolicyUniverse → (CompiledUniverse, ContextManifest)` was left undefined, which blocked the evaluator
design and the compile-time-canonicalization story (SEM-4). This document defines the IR so
that:

- **SEM-5** (target matching) has a concrete `targetIndex` to specify an algorithm over;
- a future implementation has a concrete compilation target and a set of documented
  correctness properties to differentially test against;
- the "one canonical RDF shape per proposition" invariant (Band 0, CANON) has a place to be
  *enforced* — normalization is the compiler's job, not a runtime guess.

**I1/SEM-4 (WP-5).** `targetIndex` and conflict strategy are lifted to **universe scope**
(§4): a request may match clauses drawn from several policies at once, and RL2_Semantics.md's
`Out`/`Eval` already operate over a `PolicyUniverse`, not a single `Policy` — so the compiled
form must mirror that shape. `conflictStrategy` is not stored in compiled data at all; it is
supplied to `evalIR` at evaluation time, per S7's "evaluator configuration, not policy
vocabulary" ruling (RL2_Semantics.md §Normative Derivation, §Big-Step Semantics).

**In scope:** the IR datatypes (the normalized AST — there is no separate compiled
representation, see §5), the eval-time interaction model, the state/effect model, the
construct correspondence table, and the equivalence obligation split into named lemmas.

**Out of scope:** mechanized proof and implementation (SCOPE-1 — the project stops at
specification); the target-matching *algorithm* itself (SEM-5, which consumes the
`targetIndex` defined here).

---

## 2. Pipeline

RL2 compilation is a single lowering, named in ordinary compiler terms:

```
  Turtle (surface syntax)
        │  compile — normalize + index      (Band 0 canonical form makes this near-mechanical)
        ▼
  Normalized AST                            (norms + promises as structured data;
                                              conditions are AST nodes, evaluated in place)
        │  interpret — evalIR walks this AST directly, calling evalCondition (§5) for guards
        ▼
  (Decision, DutySet, seq<Effect>)
```

**There is no compiled bytecode, no stack machine, and no second lowering pass (SCOPE-1,
2026-07-29).** An earlier design lowered conditions to a small stack VM (retained as history in
research/design-forth-ir.md); that split added a second representation, a second correctness
proof, and a second implementation surface for no behavioral gain the direct interpreter
doesn't already provide, so it was dropped. **Both the deontic layer** (which clauses match,
which win, what the decision is) **and conditions** are evaluated by one recursive interpreter
over one AST. This is the central simplification of the RL2 IR, and everything below follows
from it.

Two orthogonal structural commitments frame the rest of this document:

- **Derive-then-resolve (I/O logic).** Evaluation is two phases: a *monotone* derivation that
  collects a normative envelope, then a *non-monotone* resolution that applies conflict
  strategy and priority (§7, §9; RL2_Semantics.md §Normative Derivation).
- **Functional core + effect shell.** The interpreter is a pure total function that returns a
  decision plus a list of *effect descriptions*; a separate shell applies them to state (§7).

One ratified implementation stance follows from these (recorded here so downstream work does
not relitigate it):

- **I3 — runtime stays solver-free; entailment/closure happen at ingestion.** No OWL reasoner,
  SAT/SMT solver, or fixpoint search runs during evaluation. All entailment and bounded
  closure — subsumption/`includedIn*` (§8), materialization (§6), hierarchy expansion — are
  computed **once at ingestion/compile time** and frozen into static indices; `evalIR` only
  reads pre-materialized values. This is what keeps the interpreter a pure total function.

**Evaluation order (I1/SEM-4 closure).** Not an open question: §5's Kleene logic fixes it.
Short-circuit and error-observability are determined by the three-valued algebra
(`False kAnd Unknown = False`, etc.), not by the order the interpreter happens to visit
operands in — a property pinned by the interpreter-correctness lemma (§9b).

```
   ┌───────────────────────────────── interpreter (pure) ────────────────────────────────┐
   │  evalIR : (CompiledUniverse, Request, Σ, Ctx, Strategy) → (Decision, DutySet, seq<Effect>) │
   │      ① derive  →  ② resolve  →  emit (Decision, DutySet) + effect descriptions        │
   └───────────────────────────────────────────────────────────────────────────────────────┘
                                        │ seq<Effect>
                                        ▼
                    shell (trivial):  Σ' = applyEffects(Σ, effects)
```

---

## 3. Construct Correspondence Table

The equivalence obligation (§9) is proven by **structural induction over the language
constructs**, and this table *is* the induction skeleton. Every construct lines up across
three columns — **syntax** (canonical RDF), **semantics** (`RL2_Semantics.md` denotation),
**AST constructor**. One row is one case of the induction. A construct present in one column
but missing from another is a proof hole: this is exactly the shape of the PROM-1 defect (a
`Norm`-only clause range with no `Promise` correspondent), which is why building this table is
also a corpus audit.

**Clause is the base element — not Norm.** An Offer exists for its promises, so the base
cases include both `Norm` leaves *and* `Promise` leaves.

### 3.1 Clauses (norms and promises)

| Syntax (canonical RDF) | Semantics (§ref) | AST ctor |
|---|---|---|
| `rl2:Privilege [subject; action; object; condition?]` | Norm Denotations §684; `permit(a,x,s)` §1227 | `NormEntry(Privilege(a,x,s), effCond)` |
| `rl2:Duty [subject; action; object; condition?]` | §684; Duty SM §960–§1004; `obligate(d)` §1229 | `NormEntry(Duty(a,x,s), effCond)` |
| `rl2:Prohibition [subject; prohibitedAction; object; condition?]` | §684; `forbid(a,x,s)` §1228 | `NormEntry(Prohibition(a,x,s), effCond)` |
| `rl2:Claim [subject; counterparty; correlativeTo]` | Claim Denotation §748 | `NormEntry(Claim(subj,cpty,corr), …)` |
| `rl2:Power / Liability / Immunity [subject; affectsNorm/exposedTo/immuneFrom]` | §767 / §793 / §805 | `NormEntry(Power/Liability/Immunity(a,n), …)` |
| `rl2:Promise [promisor; promisee; promisedAction ∘ object]` | Promise SM §923–§1035; Crystallization §1036 | `PromiseEntry(p, q, PromisedAction(x,o), effCond)` |
| `rl2:Promise [promisor; promisee; promisedState]` | §923–§1035; §1036 | `PromiseEntry(p, q, PromisedState(c), effCond)` |
| `rl2:Promise [promisor; promisee; promisedDuty]` | §923–§1035; §1036 | `PromiseEntry(p, q, PromisedDuty(d), effCond)` |

> **Correspondence note.** The semantics uses non-empty `clauses : Clause+`, where
> `Clause ::= Norm | Promise` (`RL2_Semantics.md` §Policies), matching `PolicyShape` and the
> ontology. Type-filtered comprehensions in `Out`/`Eval` exclude Promise clauses from norm
> matching; promises participate through their own lifecycle and crystallization rules.

### 3.2 Conditions (base and inductive cases)

| Syntax (canonical RDF) | Semantics (§ref) | AST ctor |
|---|---|---|
| `rl2:AtomicConstraint [leftOperand; operator ∈ {eq,neq,lt,lte,gt,gte}; rightOperand \| rightOperandRef; targetNorm?]` | ⟦AtomicConstraint⟧ §288 | `Atomic(left, op, right, StateTargetRef?)` |
| `rl2:AtomicConstraint [leftOperand; operator ∈ {isA,isAnyOf,isAllOf,isNoneOf}; rightOperand \| rightOperandRef; targetNorm?]` | ⟦AtomicConstraint⟧ §288 | `Atomic(left, op, right, StateTargetRef?)` |
| `rl2:LogicalConstraint [and (…operands)]` | ⟦And⟧ §301 | `And(seq<Cond>)` |
| `rl2:LogicalConstraint [or (…operands)]` | ⟦Or⟧ §302 | `Or(seq<Cond>)` |
| `rl2:LogicalConstraint [xone (…operands)]` | ⟦Xone⟧ §304 | `Xone(seq<Cond>)` — reduced directly per the Kleene rule (§5), **not** a chained binary XOR |
| `rl2:LogicalConstraint [not operand]` | ⟦Not⟧ §303 | `Not(Cond)` |
| `rl2:EventConstraint [expectsEvent]` | ⟦EventConstraint⟧ §311 | `EventCond(ev)` — reads `Σ.Events`, evaluated by the same interpreter (§5) alongside pure conditions |

`AtomicConstraint` and each leaf clause are the **base cases**; `LogicalConstraint` and
conditional/nested clauses are the **inductive cases**. `EventConstraint` and any
`targetNorm`-parameterized state query read Σ via the subsumption-aware `performed(...)` helper
(§320); every other condition reads only `Env`. Both are cases of one `evalCondition` function
(§5) — there is no separate pure-vs-stateful evaluator split.

**`rightOperandRef` (I1/SEM-4).** When an `AtomicConstraint` carries `rightOperandRef` (a
`RuntimeReference`, e.g. `currentAgent` — RL2_Semantics.md §Conditions) rather than a literal
`rightOperand`, the right side is dynamic and must be read from `Env` like the left side.
`resolve` (§6) is not left-side-only: `evalCondition` resolves both sides from `Env` in that
case, in place of resolving the left side and treating the right as a literal. Which form
applies is a static, compile-time-visible choice (`rightOperand` vs `rightOperandRef` are
mutually exclusive per `AtomicConstraintShape`) — it adds no branching to the interpreter
itself beyond a field check.

### 3.3 Reading the table backwards

Right-to-left, the table is the **IR → source inverse map**: every AST node carries the
identity of the RDF construct it came from. Error reporting ("policy X, clause Y") is
therefore a table lookup, not a separate mechanism.

---

## 4. AST (the normalized policy)

The IR is structured data, mirroring the ontology's `rl2:Clause` split. `resolveDecision` and
clause matching pattern-match directly on these datatypes; conditions embedded in them are
interpreted in place by `evalCondition` (§5) — nothing is lowered to a second representation.

Compilation targets a `CompiledUniverse`, not a single compiled policy, mirroring
RL2_Semantics.md's `Out`/`Eval`, which already take a `PolicyUniverse U` (I1/SEM-4 — a request
can match clauses drawn from several policies at once, so `targetIndex` and
`subsumptionIndex` must span the whole compiled universe, not one policy's clauses):

```dafny
datatype CompiledUniverse = CompiledUniverse(
  policies         : seq<CompiledPolicy>,
  targetIndex      : map<Target, set<ClauseRef>>,   // Target → clause refs, ACROSS policies (SEM-5 consumes)
  subsumptionIndex : map<Action, set<Action>> )      // includedIn* downward closure — STATIC (§8), one
                                                       // hierarchy per generation (SEM-6), so it is shared
                                                       // by every policy in the universe, not per-policy

datatype ClauseRef = ClauseRef(policy: nat, clause: nat)  // indices into policies[policy].clauses[clause]

datatype StateTargetRef = NormTargetRef(source: ClauseRef)
                        | PromiseTargetRef(source: ClauseRef)
    // compilation tags rl2:targetNorm with the referenced clause kind. NormTargetRef MUST
    // reference NormEntry; PromiseTargetRef MUST reference PromiseEntry. The compiler rejects
    // a wrong-kind target before evaluation.

datatype CompiledPolicy = CompiledPolicy(
  policyId : IRI,                                  // source rl2:Policy — provenance (mirrors S7's
                                                     // per-atom provenance requirement on the Out side)
  clauses  : seq<Clause>,
  kind     : PolicyKind )                           // Offer | Agreement | Set | Privacy | Assertion

datatype Clause = NormEntry(norm: Norm, effCond: Condition)
                | PromiseEntry(promisor: Agent, promisee: Agent,
                               content: PromiseContent, effCond: Condition)

datatype PromiseContent = PromisedAction(action: Action, object: Asset)
                        | PromisedState(cond: Condition)
                        | PromisedDuty(duty: Norm)      // the referenced Duty (suretyship)
```

Notes:

- **`effCond` carries the CANON-1 push-down.** The compiler computes
  `effCond = effectiveCondition(policy, clause)` (RL2_Semantics.md §Policies):
  no conditions becomes `True`, one condition is retained directly, and two
  conditions become `And(policyCondition, clauseCondition)`. The evaluator never
  re-derives policy-level activation. This is a *normalization*, and its
  decision-preservation is part of the equivalence obligation (§9a).
- **No `matchesAction` field.** Action/purpose matching is *eval-time* (§8): the request's
  chosen value is unknown at compile time. The compiler precomputes the `subsumptionIndex`;
  the match is a membership test at eval-time.
- **`kind` encodes the Offer/Agreement well-formedness split.** Only `kind = Offer` admits a
  `PromiseEntry` clause; `Agreement`, `Set`, `Privacy`, `Assertion` reject it. This mirrors
  the SHACL constraints added in PROM-1 (`AgreementShape` etc. carry `sh:not [ sh:class
  rl2:Promise ]`). The compiler rejects a Promise in a non-Offer at compile time — the IR
  cannot represent an ill-formed policy.
- **No `conflictStrategy` field anywhere in compiled data (I1/SEM-4).** S7 established that
  conflict-resolution strategy is evaluator configuration, not something a policy or the
  universe authors — so it is not compiled at all. It is supplied directly to `evalIR` as a
  parameter (§7), exactly mirroring `Eval`'s `strategy` parameter in RL2_Semantics.md
  §Big-Step Semantics.
- **`policyId` restores per-clause provenance.** `Out`'s atoms carry `(atom-kind, n, P)` — the
  producing policy `P` (RL2_Semantics.md S7) — so the compiled form must be able to answer
  "which policy did this clause come from" too; `ClauseRef.policy` indexes into
  `CompiledUniverse.policies`, and `CompiledPolicy.policyId` is that policy's source IRI.

---

## 5. Condition Interpretation

Conditions are evaluated by `evalCondition`, a small, pure, total, recursive function over the
`Condition` AST (§3.2/§4) — no compiled representation, no stack machine, no opcode set
(SCOPE-1, 2026-07-29: see §2). Its result type realizes the semantics' **causal-error algebra**
(S2, RL2_Semantics.md §Result and Truth Algebra) directly: there is no flat `VBottom` sentinel
folded into `Value`. A resolution or comparison failure is instead carried as an `EvalError`,
lifted to `Unknown` by `evalAtomic`/`kleeneFold` below, and attached to the enclosing
`ConditionResult.causes` — never silently dropped and never conflated with a data value. The
tree-walk that consumes a condition result (§7 derivation) treats `Unknown` as `Indeterminate`
at the norm level, carrying `causes` forward into the `indeterminate` atom's payload — never as
inactive, and never as a plain `False`.

```dafny
datatype Value =
    VBool(bool)
  | VInt(int)
  | VDecimal(unscaled: int, scale: nat)              // exact fixed-point (no float rounding)
  | VString(string)
  | VLangString(string, lang: string)                // rdf:langString
  | VDateTime(epochSeconds: int, tzOffsetMinutes: int) // xsd:dateTimeStamp — tz offset MANDATORY (S4)
  | VDuration(seconds: int)                          // xsd:duration, normalized to seconds
  | VURI(string)
  | VSet(seq<Value>)                                 // collections — operand of isAnyOf/isAllOf/isNoneOf
                                                       // no VBottom (S2): Missing/Invalid/Conflict are
                                                       // carried by EvalValue/EvalError, not by Value

datatype ValueType = TBool | TInt | TDecimal | TString | TLangString
                   | TDateTime | TDuration | TURI | TSet

function valueType(v: Value): ValueType
{
  match v
    case VBool(_)       => TBool
    case VInt(_)        => TInt
    case VDecimal(_, _) => TDecimal
    case VString(_)     => TString
    case VLangString(_,_) => TLangString
    case VDateTime(_,_) => TDateTime
    case VDuration(_)   => TDuration
    case VURI(_)        => TURI
    case VSet(_)        => TSet
}
```

```dafny
datatype ErrorSite = SiteLeftOperand(op: LeftOperand)
                   | SiteRuntimeRef(ref: RuntimeReference)
                   | SitePath(path: Path)
                   | SiteComparison(operator: ComparisonOperator,
                                    leftType: ValueType, rightType: ValueType)

datatype ErrorKey = ErrorKey(site: ErrorSite, target: Option<StateTargetRef>)

datatype EvalError = Missing(key: ErrorKey)   // operand or target resolved to absent
                   | Invalid(key: ErrorKey)   // malformed lexical value or incompatible datatype
                   | Conflict(key: ErrorKey)  // resolution produced more than one value

datatype EvalValue<T> = Ok(value: T) | Err(error: EvalError, note: Option<string>)
    // note is diagnostic text only; it cannot affect EvalError/set identity

datatype Truth = True | False | Unknown

datatype ConditionResult = ConditionResult(truth: Truth, causes: set<EvalError>)
```

**Canonical error identity (S2).** `set<EvalError>` now has the required equality directly:
`EvalError` contains only `(constructor, ErrorKey)`, while free text is carried by
`EvalValue.Err.note`. `SiteComparison` includes both operand types, so mismatch categories do
not collapse merely because they use the same operator. No custom hashing or tie-break is needed.

```dafny
function evalCondition(c: Condition, env: Env, Σ: State): ConditionResult
  decreases c            // structural recursion over a finite acyclic AST — always terminates
{
  match c
    case Atomic(left, op, right, target) =>
      evalAtomic(op, target, resolve(left, env, target), resolveOperand(right, env))
                                                                    // §3.2's rightOperandRef case;
                                                                    // targetNorm now reaches resolve
    case And(cs)        => kleeneFold(kAnd,  [evalCondition(c, env, Σ) | c ← cs])
    case Or(cs)         => kleeneFold(kOr,   [evalCondition(c, env, Σ) | c ← cs])
    case Xone(cs)       => kleeneFold(kXone, [evalCondition(c, env, Σ) | c ← cs])  // "exactly one true,"
                                                                    // reduced directly, not a chained XOR
    case Not(c)         => let r := evalCondition(c, env, Σ) in ConditionResult(kleeneNot(r.truth), r.causes)
    case EventCond(ev)  => evalEventConstraint(ev, Σ)                  // queries Σ.Events; RL2_Semantics.md §311
}

function evalAtomic(op: ComparisonOperator, target: Option<StateTargetRef>,
                     leftEV: EvalValue<Value>, rightEV: EvalValue<Value>): ConditionResult
{
  match (leftEV, rightEV)
    case (Ok(l), Ok(r)) =>
      if typeCompatible(op, l, r) then ConditionResult(boolToTruth(applyOp(op, l, r)), {})
      else ConditionResult(Unknown, {mkTypeMismatch(op, target, l, r)})
    case _ =>
      ConditionResult(Unknown, nonOk(leftEV) + nonOk(rightEV))
}

function nonOk(ev: EvalValue<Value>): set<EvalError>
{
  match ev
    case Ok(_)  => {}
    case Err(e, _) => {e}
}

function mkTypeMismatch(op: ComparisonOperator, target: Option<StateTargetRef>,
                       l: Value, r: Value): EvalError
{
  Invalid(ErrorKey(SiteComparison(op, valueType(l), valueType(r)), target))
}

function evalEventConstraint(ev: EventPattern, Σ: State): ConditionResult
{
  if exists e :: e in Σ.Events && matches(e, ev)
  then ConditionResult(True, {})
  else ConditionResult(False, {})
}

function boolToTruth(b: bool): Truth { if b then True else False }

function kleeneFold(kleeneOp: seq<Truth> -> Truth, rs: seq<ConditionResult>): ConditionResult
{
  var t := kleeneOp([r.truth | r ← rs]);
  ConditionResult(t, if t == True || t == False then {}
                     else ⋃ { r.causes | r ∈ rs, r.truth == Unknown })
                     // a conclusive And/Or/Xone masks every Unknown child: an error that could
                     // not have changed the outcome is not a cause (S2)
}
```

**Kleene three-valued logic (S2).** `kAnd`/`kOr`/`kXone`/`kleeneNot` implement strong
three-valued logic over the full list of child truths at once (not a chained binary reduction):
`False kAnd Unknown = False`, `True kOr Unknown = True`, `kleeneNot(Unknown) = Unknown`, and
`kXone` is `Unknown` if any operand is `Unknown` — otherwise "exactly one `True`" over the
fully-evaluated operands, computed directly rather than as a chained binary XOR (which would
compute *parity*, the wrong answer past two operands). Short-circuit is therefore fixed by the
algebra, not by evaluation order — masking is what makes `kleeneFold`'s causes-emptying rule
above well-defined — so which errors are observable is determined, not incidental; this is the
interpreter-correctness lemma's (§9b) short-circuit claim.

**`applyOp` is a pure, already-type-checked comparator** — `applyOp : ComparisonOperator ×
Value × Value → bool` — mirroring RL2_Semantics.md's `apply : Operator × Value × Value →
Boolean`. `evalAtomic` calls it only after `typeCompatible(op, l, r)` holds; a domain mismatch
is caught by `typeCompatible` and surfaced as `Invalid` before `applyOp` ever runs. It covers
the ontology's comparison operators, including `isA`/`isAnyOf`/`isAllOf`/`isNoneOf`
(`rl2:ComparisonOperator` individuals in `rl2.ttl`: `isA` = "Type/class membership check,"
`isAnyOf` = "Value is any of a specified set," `isAllOf` = "Value satisfies all of a specified
set," `isNoneOf` = "Value is none of a specified set"). `isA` reuses the static subsumption
index (§8, "the same index mechanism serves any subsumable dimension") for hierarchical
`leftOperand` domains, falling back to equality for flat ones; `isAnyOf` tests `left ∩ rightSet
≠ ∅` (or scalar `left ∈ rightSet`); `isAllOf` tests `rightSet ⊆ left`'s value-set; `isNoneOf`
tests `left ∩ rightSet = ∅`. `typeCompatible`/`mkTypeMismatch` are specified in
RL2_Semantics.md's Helper Function Specifications and are not redefined here.

**`VDateTime` carries `tzOffsetMinutes` explicitly** (S4, WP-4's `xsd:dateTimeStamp` decision
mandating a tz offset for `currentDateTime` comparisons), so a comparison can never silently
assume UTC. **`VSet`** is the operand type `isAnyOf`/`isAllOf`/`isNoneOf` evaluate over — the
ontology already permits authoring these conditions; `applyOp` is where they are given meaning.

The properties below are documented directly from `evalCondition`'s definition above — not
proof obligations for a separate machine, since there is no separate machine:

- **Termination:** `Condition` is a finite acyclic tree, and `evalCondition` recurses strictly
  on structurally smaller subterms, so it always terminates.
- **Determinism:** `evalCondition` is a function, not a relation — the same `(c, env, Σ)`
  always yields the same `ConditionResult`.
- **Type safety:** `evalAtomic` routes ill-typed or unresolved operands to `Unknown` (with the
  responsible `EvalError` attached as a cause) rather than getting stuck; there is no stack to
  underflow and no "stuck state" to define in the first place.

The single exported meaning is `evalCondition(c, env, Σ) : ConditionResult`, a `(Truth, causes)`
pair. Its correctness statement is §9b.

---

## 6. Eval-time Interaction (reads)

All interaction with the outside world is **front-loaded and read-only**, so the interpreter
stays pure.

- **`resolve` is the sole external-read primitive.** It reads from a fully-populated `Env`; it
  never blocks on I/O. Its precondition is the `deref` grammar and sandbox of
  RL2_Semantics.md §Path Resolution Constraints (valid path, allowed root); the helper
  contract is §Helper Function Specifications.

```dafny
datatype Env = Env(request: Request, agent: AgentView, asset: AssetView,
                   state: StateView, context: ContextView)   // all pre-materialized values
```

- **`context: ContextView` is populated from `Ctx`.** `Env` is built by
  `mkEnv(R, Σ, Ctx) : Env` (RL2_Semantics.md §839), matching the denotational `mkEnv` exactly
  — `evalIR` threads `Ctx` through the same way it threads `R` and `Σ` (§7.1; I1/SEM-4 fixes a
  prior mismatch where `evalIR`'s signature and its internal `mkEnv` call omitted `Ctx` even
  though §9's equivalence obligation already stated it as a top-level parameter).

- **ContextManifest.** The compiler statically extracts, from every condition tree, the exact
  set of paths the clause will resolve:
  `ContextManifest : ClauseRef → set<OperandSpec>`. At
  runtime the host pre-materializes precisely those paths into `Env` before evaluation; a
  `RESOLVE` of an un-manifested path is a hard reject. Interaction is thus **bounded and
  declared** — no surprise fetch mid-evaluation.
- **Σ / event queries are one case among `evalCondition`'s others (§5).** `EventConstraint`
  and `targetNorm`-parameterized state operands interrogate Σ/history via
  `evalEventConstraint(...)`; there is no longer a purity boundary to route around, since
  `evalCondition(c, env, Σ)` already takes `Σ` alongside `env` for every case.
- **`StateTargetRef` preserves the target kind.** The RDF property remains `rl2:targetNorm`,
  but compilation emits `NormTargetRef` or `PromiseTargetRef`. Duty operands accept only the
  former and Promise operands only the latter; a missing target becomes `Missing`, while a
  present wrong-kind target is rejected during compilation (and is `Invalid` defensively at an
  evaluator boundary).

**Snapshot-consistency invariant.** Every read in a single evaluation observes Σ as of entry;
all effects (§7) apply atomically afterward. There is no intra-evaluation read-after-write.
This invariant is what permits effects to live *outside* the semantics of the language. It
holds for RL2 today: a decision evaluates against a fixed Σ snapshot, `Out` is a set-builder
over that snapshot, and `resolveDecision` is set-based rather than a stateful fold. A future
construct that had to observe another clause's effect *within the same evaluation* would
violate it and force a revisit — so it is stated, not assumed.

---

## 7. State and Effects (writes)

The denotational `Eval` already returns state as a *value* — `(Decision, State, DutySet)`
(RL2_Semantics.md §Evaluation Function Signature). The IR keeps that shape and only refactors
the returned `State` into a list of **effect descriptions**:

```dafny
evalIR : (CompiledUniverse, Request, Σ, Ctx, Strategy) → (Decision, DutySet, seq<Effect>)   // PURE, total
```

`CompiledUniverse` (§4) replaces the earlier single-policy `CompiledPolicy` as `evalIR`'s
input (I1/SEM-4 — a request evaluates against the whole compiled universe, not one policy).
`Ctx` and `Strategy` are explicit parameters, matching the denotational `Eval`'s signature
(RL2_Semantics.md §Big-Step Semantics) exactly: `Ctx` was previously dropped between §9's
equivalence obligation and this signature; `Strategy` was previously smuggled in as a
`CompiledPolicy` field, which S7 already rejected as policy vocabulary.

- **`(Decision, DutySet)` is the outward result: a verdict plus possible future duties.** The
  verdict is yes/no/indeterminate (`Permit | Deny | PermitWithObligations | NotApplicable |
  Indeterminate`); `DutySet` is the duties the request will owe. `PermitWithObligations` is
  the "yes, and you will owe these" case. For an **Offer**, the future duties simply *are* the
  crystallized duties (below).
- **`seq<Effect>` replaces the returned `State`.** Effects are *data*, not actions. Σ,
  Cases, and history are immutable values threaded through `evalIR` as plain function
  arguments and results. "Mutation" is a shell computing `Σ' = applyEffects(Σ, fx)`.

The attributed envelope and `ConditionResult.causes` are internal semantic values, not yet an
additional `evalIR` return field. Their structured Protocol projection remains C3-6/D10; until
then the outward decision may be `Indeterminate`, but causal detail is retained only inside the
evaluation/audit implementation.

```dafny
datatype Effect =
  | TransitionDuty(duty: Norm, from: DutyState, to: DutyState)   // Duty SM; SEM-1 restoreAction wiring
  | CrystallizePromise(promisor: Agent, promisee: Agent,         // PROM-1 §1036 — orientation-carrying
                       content: PromiseContent, source: Clause)  // CONS-3 — audit trail to originating Promise
  | GenerateRemedialDuty(source: Clause, remedy: Norm)           // PROM-6 §1082 (Remedial Generation)
  | CreateCase(case: CaseRef, generation: GenId)                 // Protocol; SEM-6 generation binding
  | ExercisePower(power: Norm, target: Norm)                     // Power exercise; SEM-8
  | AppendHistory(event: Event)
```

**Effects unify a large part of Bands 1–2.** Crystallization (PROM-1), remedial generation
(PROM-6), duty-state transitions and `restoreAction` (SEM-1), Case/generation binding
(SEM-6), and Power exercise (SEM-8) are all *effect kinds* in one closed algebra. `evalIR`
enumerates the legal effect vocabulary; the Duty/Promise state machines define which
transitions are legal; the shell just applies them.

### 7.1 Derive-then-resolve

Inside `evalIR`, the deontic computation is the I/O-logic two-phase (RL2_Semantics.md
§Normative Derivation):

```
IRAtom ::= permit(source: ClauseRef, privilege: Norm)
         | forbid(source: ClauseRef, prohibition: Norm)
         | obligate(source: ClauseRef, duty: Norm)
         | indeterminate(source: ClauseRef, norm: Norm, causes: set<EvalError>)
```

The constructors are kind-restricted: `permit` accepts only a Privilege, `forbid` only a
Prohibition, and `obligate` only a Duty. `indeterminate` accepts exactly those three kinds.
`source.policy` plus `CompiledPolicy.policyId` supplies the source-policy provenance carried as
`P` by the denotational atom; `source.clause` identifies the producing clause.

```
evalIR(CU, R, Σ, Ctx, strategy) =
    let env      = mkEnv(R, Σ, Ctx)
    -- ① DERIVATION (monotone): collect the pre-resolution envelope, across ALL policies
    let envelope = ⋃ { derive(ref, clauseAt(CU, ref), env)
                       | ref ∈ clauseRefs(CU) }                              -- Out
    -- ② effect collection (still monotone): duty transitions, crystallization on acceptance, …
    let effects  = deriveEffects(envelope, CU, Σ, env)
    -- ③ RESOLUTION (non-monotone): strategy + priority over the collected envelope
    let Σ'       = applyEffects(Σ, effects)
    let decision = resolveDecision(envelope, Σ', strategy)
    in (decision, duties(envelope, Σ'), effects)

duties(envelope, Σ') = { d ∈ obligated(envelope) | Σ'.ObligationState(d) ∈ {Pending, Active} }

derive(ref, clause, env) =
    case clause of
        NormEntry(n, effCond) | n : Privilege ∧ matches(n, env.request) →
            let r = evalCondition(effCond, env, env.state) in
            if r.truth = True then { permit(ref, n) }
            else if r.truth = Unknown then { indeterminate(ref, n, r.causes) }
            else ∅
        NormEntry(n, effCond) | n : Prohibition ∧ matches(n, env.request) →
            let r = evalCondition(effCond, env, env.state) in
            if r.truth = True then { forbid(ref, n) }
            else if r.truth = Unknown then { indeterminate(ref, n, r.causes) }
            else ∅
        NormEntry(d, effCond) | d : Duty ∧ matches(d, env.request) →
            let r = evalCondition(effCond, env, env.state) in
            if r.truth = True then { obligate(ref, d) }
            else if r.truth = Unknown then { indeterminate(ref, d, r.causes) }
            else ∅
        _ → ∅   -- nonmatching access norms and non-access clauses have separate denotations/lifecycles

obligated(envelope) = { d | obligate(ref, d) ∈ envelope }
```

`derive` is the complete monotone per-clause decision fold; it consumes the compiled `effCond`
and retains the `ClauseRef` needed for provenance. Promise, Claim, Power, Liability, and Immunity
processing remains in their dedicated lifecycle/effect rules rather than being coerced through
request matching. `resolveDecision` is where priority, strategy, and Unknown outcome sensitivity
act. Because derivation is monotone and order-independent, the outer normalization theorem (§9a)
inherits order-independence for free.

**`duties(envelope, Σ')` reads the post-transition state**, mirroring the identical fix on the
denotational side (RL2_Semantics.md §Derivation vs Resolution): the outward `DutySet` reports
duties that are still `Pending`/`Active` *after* `applyEffects` has run, not a stale
pre-transition snapshot. `obligated(envelope) = { d | obligate(ref, d) ∈ envelope }` is the raw
per-envelope obligated-clause set `dutyFx` also draws from (below); it takes no state, since
`dutyFx` runs before `Σ'` exists.

**`deriveEffects` (I4).** Each effect kind is produced by a function keyed on the entity it
transitions, not on the clause that happened to mention it — this is what makes effect
conflicts unrepresentable rather than something `applyEffects` must arbitrate:

```dafny
deriveEffects(envelope, CU, Σ, env) : seq<Effect> =
    dutyFx(envelope, Σ) ++ promiseFx(envelope) ++ remedialFx(envelope)
      ++ caseFx(envelope) ++ powerFx(envelope) ++ historyFx(envelope)
    -- each sub-sequence canonically ordered by ClauseRef (policy index, then clause index) —
    -- derivation's Decision is order-independent (§7.1 above) regardless, but AppendHistory's
    -- literal order feeds the replay/audit log (WP-3 witness events), so evalIR fixes one

dutyFx(envelope, Σ) =
    [ e | d ∈ obligated(envelope), e = transitionEffect(d, Σ), e ≠ None ]

transitionEffect(d, Σ) : Effect? =
    case Σ.ObligationState(d) of
        Pending → Some(TransitionDuty(d, Pending, Active))
                  -- membership in obligated(envelope) already proves compiled effCond = True
        Active  → if performed(d.subject, d.action, d.object, Σ)
                  then Some(TransitionDuty(d, Active, Fulfilled))
                  else if timeout(d.condition, Σ) then Some(TransitionDuty(d, Active, Violated))
                  else None
        _       → None   -- Fulfilled/Violated terminal (D-FULFILL/D-VIOLATE, RL2_Semantics.md §Duty
                          -- Activation/Fulfillment/Violation)
```

`transitionEffect` is `updateOneDuty`'s case dispatch (RL2_Semantics.md `updateDutyStates`)
restated to *return* an effect instead of mutating Σ in place. Pending activation does not
re-evaluate the raw `d.condition`: presence in `obligated(envelope)` already proves the compiled
policy-plus-clause `effCond` was True against the input snapshot. The function is otherwise a
total function of `Σ.ObligationState(d)` and Σ, and `obligated(envelope)`
is a set, so at most one `TransitionDuty` effect is ever produced per duty per round. A
same-round `Fulfilled`-vs-`Violated` conflict on one duty (§7.3's original framing) is
therefore not a case `applyEffects` resolves at commit time; it is precluded at derivation time
by construction, the same way S7 eliminated per-clause `conflictStrategy` by making resolution
a single evaluator-supplied parameter rather than something clauses vote on. `promiseFx`,
`remedialFx`, `caseFx` similarly key each effect by its originating clause (`source: Clause`,
§7.2) — distinct clauses can never collide because they produce distinct `Effect` values, so
folding them into Σ is append, not arbitration. `powerFx` (`ExercisePower`) is the one
remaining open case: SEM-8's state-update verification for `ExercisePower` is explicitly
deferred (see issues.md), so this document does not claim its conflict-freedom — only that the
other five kinds are conflict-free by the argument above.

### 7.2 Crystallization carries orientation

**Acceptance of an Offer is the event that emits the crystallization effect set.** Each
`PromiseEntry` yields a `CrystallizePromise` effect; `applyEffects` realizes PROM-1's function

```
crystallize(Promise(p, q, κ)) = (D, C),   C = Claim(subject = q, counterparty = p, correlativeTo = D)
```

A promise **made** (promisor = offerer) and a promise **demanded** (promisor = acceptor) both
crystallize on acceptance but bind **opposite** parties. Carrying `promisor`/`promisee` on the
effect is what keeps the resulting `Duty` + correlative `Claim` correctly oriented — the
made-vs-demanded orientation is a named effect-soundness sub-lemma (§9c). The three content
forms map exactly as in RL2_Semantics.md §Crystallization (`PromisedAction` fully closed;
`PromisedState` maintenance-duty wiring → SEM-1; `PromisedDuty` suretyship remedy → PROM-5).

**`CrystallizePromise` is not the whole of Offer→Agreement (PROM-7).** This effect is
*runtime* bookkeeping inside an already-materialized Agreement's evaluation. The document-level
step that turns an Offer into that Agreement — minting fresh clause IRIs and rewriting
`targetNorm` references from Offer-stage Promises to their crystallized Duties — is
`materialize` (RL2_Semantics.md §Materialization), which runs once, before compilation. It
cannot be an `Effect`/`applyEffects` case: `CompiledUniverse` is immutable during `evalIR`, and
`applyEffects` only ever produces a new Σ, never a rewritten policy AST — exactly what
`targetNorm` rewriting requires.

### 7.3 Effect coherence

`applyEffects` folds `deriveEffects`'s output into Σ. Given §7.1's `transitionEffect`
construction, the fold has no conflicts left to arbitrate: each `TransitionDuty` is keyed by a
distinct duty, each `CrystallizePromise`/`GenerateRemedialDuty`/`CreateCase` by a distinct
source clause, so `applyEffects` is a commutative, idempotent merge into Σ, well-posed by
snapshot-consistency (§6 — all effects derive from the same Σ, so the update set is fixed).
`applyEffects`'s remaining proof obligation (§9c) is therefore reproduction, not arbitration:
that this merge yields exactly the Σ' the denotational `updateDutyStates`/operational rules
compute — not that it picks a winner among effects that were never actually in tension.

**Commit-time validation (I4).** `applyEffects` is pure and total over a fixed `(Σ, fx)`; the
part of "committing a transition" that is *not* pure — persistence, network delivery, retries —
sits entirely in the deployment shell (RL2_Semantics.md §Versioned snapshot and commit) and is
out of this document's proof surface. What the evaluator contract obligates the deployment to do is
re-derive, not merely re-apply: a commit against snapshot version `v` is valid only if the
`fx` being applied is the `fx` that `evalIR` computes fresh against `Snapshot_v`, not an `fx`
carried over from a possibly-stale prior evaluation:

```
validateCommit(CU, Snapshot_v, R, Ctx, strategy, fx_claimed) : bool =
    let (_, _, fx_expected) = evalIR(CU, R, Snapshot_v.Σ, Ctx, strategy)
    in fx_claimed = fx_expected
```

This closes the gap the CAS check alone does not: version-matching guarantees no *other*
committed transition slipped in between read and write, but does not by itself guarantee the
deployment is committing the effect set the pure evaluator actually computed for that version (e.g. a
retried request whose `fx` was memoized against an earlier, since-superseded evaluation attempt
could still carry a matching `v` by coincidence). Recomputing `fx_expected` at commit time —
rather than trusting a caller-supplied `fx` — makes `commit` idempotent under retry for free:
a retried commit at unchanged `v` recomputes the same `fx` (§9's determinism) and is a no-op;
a retry after `v` has moved fails the CAS check and forces re-evaluation against the new
snapshot, exactly as already specified.

---

## 8. Subsumption (compile-time index, eval-time match)

Action/purpose subsumption is **eval-time**, because the chosen action/purpose is a
request-time value. The compiler precomputes only the *static* structure:

- **Compile-time:** build `subsumptionIndex : map<Action, set<Action>>` as the `includedIn*`
  downward closure of the hierarchy — for each norm-action `y`, the set `{ x | x includedIn* y
  }`. The hierarchy is fixed within a generation (SEM-6), so the closure is static. Cycles are
  a compile-time reject.
- **Eval-time:** `matches(c, R) := R.action ∈ subsumptionIndex[c.action]` — a membership test
  against the request. The same index mechanism serves any subsumable dimension (action,
  purpose, target asset); each gets its own closure map.

**Well-defined limitations** carry over verbatim from the resolved action-hierarchy decisions
(ACT-1/ACT-2) and EXPR-2: subsumption is *bounded graph reachability* over `includedIn*` — no
OWL reasoning, no counting/aggregation quantifier. The `subsumptionIndex` is a materialized
cache of the reachability relation, so eval-time match `≡ ∃ path in includedIn*`; this is a
caching-correctness lemma inside §9a, not a new semantic gap.

---

## 9. Equivalence Obligation

The IR is correct iff it reproduces the denotational semantics. Top-level statement (with Σ
threaded functionally and refactored into effects):

```
For all policy universes U, requests R, states Σ, contexts Ctx, strategies strategy:

  Eval(U, R, Σ, Ctx, strategy) = (dec, Σ', duties)
    ≡
  let (CU, M) = compile(U)
  let (dec', duties', fx) = evalIR(CU, R, Σ, Ctx, strategy)
  in  dec = dec'  ∧  duties = duties'  ∧  Σ' = applyEffects(Σ, fx)
```

The proof is structural induction over the correspondence table (§3). It decomposes into three
named lemmas:

**(9a) Normalization theorem (outer IR).** `compile` is decision-preserving: pushing policy
conditions into `effCond`, precomputing `targetIndex`, and materializing `subsumptionIndex`
change *how* the answer is stored, not *what* is computed. `M` maps each source Policy/clause
identity to its `CompiledPolicy`/`ClauseRef`; applying `M` to every norm, source policy,
`StateTarget`, and `ErrorKey.target` in `Out(U,Env)` yields exactly the envelope collected by the
AST tree-walk over the returned `CompiledUniverse`. Derivation's monotonicity
and order-independence (§7.1) make this a fold-equivalence; the subsumption-index caching
lemma (§8) is a sub-case.

**(9b) Interpreter-correctness lemma.** For every source condition `c` and its compiled condition
`c'`, `evalCondition(c',env,Σ) = mapResult(M,⟦c⟧(env,Σ))`, where `mapResult` preserves `truth`
and maps only source clause targets in `causes` to their kind-tagged `StateTargetRef`. Both sides
otherwise share the same `{truth,causes}` algebra directly, so no `Truth`↔`Value`
mapping is needed: there is no `VBottom` sentinel on either side to reconcile. Together with the
properties of §5 (termination, determinism, type safety), this covers: Base case: `Atomic`
(including the `Missing/Invalid/Conflict → Unknown` lifting and its `causes` attribution) and
`EventCond` (§Result and Truth Algebra's event-constraint case, now just another case of the
same function). Inductive cases: `And`/`Or`/`Xone`/`Not` by the Kleene fold in §5 — the lemma
therefore also pins the short-circuit behavior and the causes-masking rule (an error masked by a
conclusive sibling branch is not a cause on either side of the equivalence). Because
`evalCondition` is a direct structural recursion over `Condition` with no intervening lowering
step, this proof is close to definitional — each case of the interpreter is read off the
corresponding denotational rule.

**(9c) Effect-soundness lemma.** `applyEffects(Σ, fx)` reproduces the `Σ'` that `Eval` computes
via `updateDutyStates` (§1259) and the operational rules (§Duty Activation/Fulfillment/
Violation, §Crystallization, §Remedial Generation). Three sub-lemmas:

- **Made-vs-demanded orientation:** for either promise orientation, `CrystallizePromise`
  yields a `Duty` bound to the promisor and a correlative `Claim` bound to the promisee
  (§7.2).
- **Effect coherence (I4):** `deriveEffects` keys `TransitionDuty` by duty (not by clause), so
  distinct duties/sources never produce colliding effects within one round — `applyEffects` is
  a commutative, idempotent merge, not an arbitration (§7.3). This is a determinism argument,
  not a runtime resolution strategy, mirroring how S7 removed per-clause `conflictStrategy`
  rather than adjudicating between clauses that declared different ones.
- **Commit validity (I4):** for a shell built on the versioned-snapshot/CAS protocol
  (RL2_Semantics.md §Versioned snapshot and commit), a committed transition at version `v` is
  sound only if its applied `fx` equals `evalIR`'s fresh recomputation against `Snapshot_v`
  (§7.3's `validateCommit`) — persistence, network, and retries stay outside this proof; only
  the equality obligation on `fx` is in scope.

The split keeps 9a/9c as structural refinements close to the denotational spec, and localizes
9b to a single pure function whose cases mirror the denotational rules directly. Section 10
defines how a future implementation is to test this correspondence; the current project stops
at the specification (SCOPE-1).

---

## 10. Compiler Trust Model

There is no separate verified kernel to trust and an untrusted shell around it (SCOPE-1): the
whole pipeline — `compile` and `evalIR` alike — is a **specified design**, not a
mechanized or implemented one. A future implementation is to be checked by:

- **Differential testing** against an independently executable reference on semantic
  conformance vectors derived from the 52-use-case corpus *and*
  on generated policies (the canonical-form thesis makes machine-generated policies the
  primary case, so they must be in the test set). This follows the **Cedar-spec** model —
  reference semantics kept separate from the production executable and reconciled by differential testing
  (`research/verification-toolchain-comparison.md` §Lean/Cedar, retained as a historical
  precedent for this methodology even though its toolchain recommendation is superseded).
- **CANON shrinks the surface that needs testing.** The canonical-form invariant is scoped to
  the **AST the projection produces**, not to raw RDF (C5, RL2_Architecture.md §Canonical
  Form): the RDF authoring layer admits exactly one authored shape per proposition
  (SHACL-enforced), and the projection `π : RDF → AST` normalizes entailment, defaults, blank
  nodes, operand ordering/dedup, annotations, and unsupported-extension rejection. Because that
  authored input is already SHACL-canonical, `π` is a **near-mechanical normalizer** — small
  and total — rather than an optimizing compiler, and it is `π` (not raw graph structure) that
  makes syntax → AST a *function* (one canonical AST per proposition), the precondition that
  makes §9's base cases well-formed. Semantic equivalence is decided over the AST, never by
  raw-graph isomorphism.

---

## 11. Handoffs and Deferred Items

- **SEM-5 (target matching).** Consumes `CompiledUniverse.targetIndex`. This document fixes the
  index *shape* (`map<Target, set<ClauseRef>>`); SEM-5 owns the *algorithm* and precedence
  (direct, classification, sub-asset, subsumption) and closed-world defaults.
- **SEM-1 / PROM-5.** `PromisedState` maintenance-duty ObligationState wiring (SEM-1) and
  `PromisedDuty` suretyship remedy (PROM-5) are the two behavioral wirings the crystallization
  *targets* (§7.2) hand off; the IR is well-defined regardless of how they resolve.
- **Implementation, out of scope entirely (SCOPE-1).** Building an actual evaluator (in any
  language), error-report surfacing, and step/debug tooling are not part of this project's
  current scope, which stops at specification. `research/design-forth-ir.md` records the
  earlier stack-VM design's take on these questions for historical reference only.

---

## References

- **RL2_Semantics.md** — denotational and operational semantics this IR refines (§Conditions,
  §Norm Denotations, §Crystallization, §Normative Derivation, §Big-Step Semantics).
- **RL2_Architecture.md** — evaluation pipeline and layer separation.
- **research/design-forth-ir.md** — earlier stack-VM design rationale, superseded by this
  document's direct-interpreter design (SCOPE-1, 2026-07-29); retained for historical record.
- **research/verification-toolchain-comparison.md** — earlier Dafny→Go mechanization
  comparison, superseded by SCOPE-1; retained for its Cedar-spec differential-testing
  precedent, cited in §10.
- Makinson & van der Torre, *Input/Output Logics* — the derive-then-resolve foundation.
