---
title: "RL2 Formal Semantics"
subtitle: "Deterministic Policy Meaning over Requests and World Snapshots"
version: "0.7"
status: "Draft"
date: 2026-08-01
abstract: |
  RL2 is a policy language that extends and clarifies ODRL 2.2. It combines conduct norms, promises, and constraint algebra in deterministic evaluation semantics over a canonical policy universe, request, and immutable world snapshot.
---

## Introduction

Digital policy frameworks often lack formal normative foundations. ODRL 2.2 provides an expressive
information model and vocabulary but leaves important evaluator choices open, allowing independent
implementations to disagree about the result of the same policy.

RL2 (“Rights Language 2”) addresses these limitations with explicit conduct norms, typed
conditions, temporal Duty semantics, and evidence-derived status. RDF is the interchange
representation; evaluation is defined over the canonical abstract syntax produced during
ingestion.

This document defines the formal semantics. `RL2_Model.md` defines the evaluation interface;
`../docs/RL2_Architecture.md` provides an informative overview.

---

## Abstract Syntax

We define RL2’s abstract syntax using a typed algebraic grammar, enriched with commentary explaining intuition and use.

### Core Syntactic Categories

Let:

* **A** = set of agents
* **X** = set of actions
* **S** = set of assets
* **V** = set of values
* **T** = time domain
* **Env** = evaluation environment
* **W** = immutable WorldSnapshot
* **⊥** = an absent optional syntax field; missing evaluated data is represented by
  `Err(Missing(ErrorKey), note)` in the Result and Truth Algebra below

We define RL2 expressions as:

#### Norms

```
Norm ::=
    Privilege(Agent, Action, Asset, Condition,
              prerequisiteDuties: finite set of Duty)
  | AchievementDuty(Agent subject, Agent? counterparty, Action, Asset, Condition,
                    postCondition: Condition?, dutyWindow: DutyWindow?)
  | MaintenanceDuty(Agent subject, Agent? counterparty, Asset, Condition,
                    invariant: Condition, dutyWindow: DutyWindow?)
  | Prohibition(Agent, Action, Asset, Condition)
```

`Condition` in both Duty forms is the ordinary applicability guard. Duty satisfaction is
structural: an Achievement Duty requires action evidence and may additionally require a
`postCondition`; a Maintenance Duty requires its `invariant` throughout its `dutyWindow` and has
no action. The two forms are mutually exclusive in canonical RDF; no separate mode field exists.

`Privilege.prerequisiteDuties` is projected from zero or more `rl2:prerequisiteDuty` values.
The set is conjunctive: every applicable member must be Fulfilled before the Privilege can
contribute a permit. An attached Duty is referenced by one or more Privileges and is not also a
top-level Policy clause. Sharing one Duty node shares its one status result across those
Privileges. A top-level Duty is independent and never gates an access decision.

```
DutyWindow = [startInclusive: Time, endExclusive: Time)
```

The window is finite when present. Absence means unbounded; it is not a second RDF spelling for an
interval with omitted endpoints.

#### Promises

```
Promise ::= Promise(Agent promisor, Agent promisee, Asset? object, PromiseContent)

PromiseContent ::=
    PromisedAction(Action)          -- action commitment; object is Promise.object
  | PromisedState(Condition)        -- state commitment; from rl2:promisedState
```

`PromiseContent` maps one-to-one to `rl2:promisedAction` and `rl2:promisedState`. A well-formed
Promise carries exactly one.

#### Conditions

```
Condition ::=
      AtomicConstraint(leftOperand, operator,
                       rightOperand : Literal | IRI | RuntimeReference | ValueSet,
                       targetNorm : StateTarget?)
    | And(Condition{2,})
    | Or(Condition{2,})
    | Xone(Condition{2,})
    | Not(Condition)
```

Notes:
- `And`, `Or`, and `Xone` take at least two conditions, matching
  `AndOrXoneOperandCardinalityShape`
- `leftOperand` is drawn from profile-defined operands; core defines `currentDateTime`,
  `obligationStateOperand`, and `promiseStateOperand`
- Time-based conditions use `AtomicConstraint` with `leftOperand = currentDateTime` (e.g., `currentDateTime lte deadline`)
- Dynamic value resolution on the left side uses `LeftOperand` with `resolutionPath`
- Dynamic value resolution on the right side uses `RuntimeReference` (e.g., `currentAgent`)
- Set comparisons use one inline `ValueSet`; asset collections are not value sets
- The stable RDF property `rl2:targetNorm` is interpreted as the tagged `StateTarget` defined
  below, preserving whether it references a Duty or a Promise. It is required for the two status
  operands and forbidden for every other left operand.

#### Policies

```
Clause ::= Norm | Promise      -- mirrors rl2:Clause; only an Offer admits a Promise clause
PolicyKind ::= Set | Offer | Agreement

Policy ::= Policy {
  kind      : PolicyKind,
  grantor   : Agent?,       -- required for Agreement; optional for Offer; absent for Set
  grantee   : Agent?,       -- required for Agreement; optional for Offer; absent for Set
  condition : Condition?,   -- optional policy-level activation condition
  clauses   : Clause+,      -- non-empty, matching PolicyShape
  meta      : Metadata
}
```

Set, Offer, and Agreement are pairwise disjoint concrete policy kinds. A Set contains only Norms
and has no grantor or grantee. An Offer may identify the proposed parties and is the only kind that
admits Promises. An Agreement identifies exactly one grantor and grantee and contains only Norms.

Conditions on Policies and clauses are optional in RDF. Normalization maps an
absent condition to the constant `True` and avoids manufacturing a unary `And`:

```
effectiveCondition(P, clause) =
    case (P.condition, clause.condition) of
        (None, None)       → True
        (Some(p), None)    → p
        (None, Some(c))    → c
        (Some(p), Some(c)) → And(p, c)
```

The canonical AST therefore contains a total condition for every clause while
preserving the logical-operator arities enforced by SHACL.

The Duties reachable from a Policy are:

```
independentDuties(P) = { d : Duty | d ∈ P.clauses }
attachedDuties(P)    = ⋃ { n.prerequisiteDuties | n : Privilege ∈ P.clauses }
allDuties(P)         = independentDuties(P) ∪ attachedDuties(P)
```

SHACL rejects a Duty that occurs in both sets. An attached Duty's policy provenance is the set of
Policies containing Privileges that reference it; one `obligate(d,P)` atom is derived per such
Policy when at least one matching owner makes the Duty applicable.

---

## Type System

The type system ensures well-formed policies.

### Typing Judgements

We use:

```
Γ ⊢ e : τ
```

### Types

```
τ ::= Agent | Action | Asset | Condition | Time | Boolean | Norm | Promise | DutyWindow
    | WorldSnapshot | EvaluationConfiguration | EvaluationResult
```

### Key Typing Rules

Privilege:

```
Γ ⊢ a : Agent     Γ ⊢ x : Action     Γ ⊢ s : Asset     Γ ⊢ c : Condition
Γ ⊢ ds : finite set of Duty
--------------------------------------------------------------------------------
       Γ ⊢ Privilege(a, x, s, c, ds) : Norm
```

Duty:

```
Γ ⊢ a : Agent     Γ ⊢ b : Agent?      Γ ⊢ x : Action     Γ ⊢ s : Asset
Γ ⊢ c : Condition Γ ⊢ pc : Condition? Γ ⊢ w : DutyWindow?
--------------------------------------------------------------------------------
        Γ ⊢ AchievementDuty(a, b, x, s, c, pc, w) : Norm

Γ ⊢ a : Agent     Γ ⊢ b : Agent?      Γ ⊢ s : Asset      Γ ⊢ c : Condition
Γ ⊢ i : Condition Γ ⊢ w : DutyWindow?
--------------------------------------------------------------------------
        Γ ⊢ MaintenanceDuty(a, b, s, c, i, w) : Norm
```

Prohibition:

```
Γ ⊢ a : Agent     Γ ⊢ x : Action     Γ ⊢ s : Asset
Γ ⊢ c : Condition
--------------------------------------------------------------------------
   Γ ⊢ Prohibition(a, x, s, c) : Norm
```

Promise:

```
Γ ⊢ p : Agent   Γ ⊢ q : Agent   Γ ⊢ s : Asset?   Γ ⊢ content : PromiseContent
--------------------------------------------------------------------------------
       Γ ⊢ Promise(p, q, s?, content) : Promise
```

Condition types follow typical logical typing rules.

---

## Semantic Domains

We define semantic domains to interpret expressions.

### Agents

```
⟦Agent⟧ ⊆ A
```

### Actions

```
⟦Action⟧ ⊆ X
```

### Values

`Value` includes typed scalar values, `VURI(IRI)`, and finite `VSet(Value)` values. A `ValueSet`
projects to `VSet` after semantic duplicate removal and canonical member ordering. Its members
must be homogeneous when used by a comparison operator.

### World Snapshot

The evaluator reads one finite, immutable `WorldSnapshot W`; it has no mutable semantic state:

```text
W = (evaluationTime : Time,
     facts          : Set<AttributedFact>,
     evidence       : Set<Evidence>)
```

`AttributedFact`, `Evidence`, their scopes, identity rules, intervals, attribution, conflict
handling, and selection rules are defined normatively in `RL2_Model.md` §4. In summary:

- fact lookup is by canonical `(FactScope, Path)` and evaluation-time validity;
- equal asserted values agree, while distinct values for a single-valued key yield `Conflict`;
- action evidence is selected by explicit actor, action, object, and interval fields;
- occurrence time, not arrival order or a storage sequence, determines temporal eligibility;
- no event log or stored Duty or Promise state is part of `W`.

`state.Clock` is an authored path spelling for `W.evaluationTime`. Other declared paths resolve
through `W.facts`. Duty and Promise statuses are derived from policy content and `W.evidence`.

### Environments

```
Env = (Universe, Request?, Agent, Asset, Snapshot, Configuration)
```

A named six-field record (not a bare product), used for evaluating matching and operand paths.

- `Universe` — the immutable canonical PolicyUniverse and its finite term-inclusion indexes
- `Request?` — the core request being evaluated, when one exists; absent when `Env` is built for
  status derivation (`mkStatusEnv`, §Declarative Duty and Promise status), which has no access
  Request
- `Agent`   — the requesting agent (`Request.requestingAgent`; what `rl2:currentAgent` resolves to)
- `Asset`   — the requested asset
- `Snapshot` — the immutable `WorldSnapshot`
- `Configuration` — profiles, bounds, trust parameters, and conflict strategy

When `Request` is absent, every `request.*` path resolves to
`Invalid({ site: Path(path), target: None })` (§`requestField`), consistent with the status
environment's rule that `request.*` is invalid outside an access Request.

The fields do not correspond one-to-one with the canonical path roots (`request.*`, `agent.*`,
`asset.*`, `state.*`, `context.*`, `global.*`); several roots are backed by `Snapshot`, and two
fields back no root at all:

| Path root  | Backing `Env` field(s) |
|------------|-------------------------|
| `request.*` | `Request` — the three core Request fields only (§`deref`) |
| `agent.*`   | `Snapshot` — facts under `AgentScope(Agent)`; `Agent` supplies the scope identity, not the data |
| `asset.*`   | `Snapshot` — facts under `AssetScope(Asset)`; `Asset` supplies the scope identity, not the data |
| `state.*`   | `Snapshot` — `state.Clock` is `Snapshot.evaluationTime`; other `state.*` paths are `StateScope` facts |
| `context.*` | `Snapshot` — `EvaluationScope` facts |
| `global.*`  | `Snapshot` — `GlobalScope` facts |

`Universe` backs no path root: it supplies the policy graph and term-inclusion indexes used by
matching, action-ancestor lookups, and status derivation. `Configuration` backs no path root: it
supplies the profile, bound, trust, and conflict-strategy parameters consulted during resolution.

`context.*` and `global.*` are scoped fact paths within `Snapshot`; they are not separate live
objects. `Env` contains no callback, source adapter, or mutable record.

---

## Denotational Semantics

Denotational semantics gives timeless meaning to norms and conditions.

### Result and Truth Algebra

Operand resolution and condition evaluation are **partial** — an operand may be missing,
wrong-typed, multi-valued, or fail to resolve. RL2 makes this total with typed carriers shared
throughout the normative semantics. Serialization of structured causes is an interchange-profile
question; the semantic value is defined here.

```
StateTarget  = NormTarget(Norm) | PromiseTarget(Promise)

ErrorSite    = LeftOperand | RuntimeReference | Path
             | SnapshotSite(String) | ConfigurationSite(String) | EvidenceSelector
             | StatusSite(StateTarget)
             | ComparisonSite(Operator, ValueType, ValueType)
ErrorKey     = { site : ErrorSite, target : StateTarget? }

EvalError    = Missing(ErrorKey) | Invalid(ErrorKey) | Conflict(ErrorKey)
             -- the canonical, comparable cause carried by ConditionResult

EvalValue<T> = Ok(T) | Err(EvalError, String?)
             -- the optional String is diagnostic text, not part of EvalError identity

Truth        = True | False | Unknown   -- no payload: causal attribution lives in ConditionResult
```

**Canonical error identity.** `EvalError` is the identity-bearing value: equality is structural
on `(constructor, ErrorKey)`. Diagnostic text lives only on `EvalValue.Err` and therefore cannot
change set membership. `ComparisonSite` includes both operand types, so two distinct mismatch
classes do not collapse merely because they use the same operator. This makes union over
`causes` commutative, associative, and idempotent without implementation-specific hashing.

`resolve : LeftOperand × Env × StateTarget? → EvalValue<Value>`. **Comparison lifts errors to
`Unknown`:** `apply(operator, l, r, Env)` is called, and its `True`/`False` result trusted, only when
both sides are `Ok` and type-compatible; any `Err` on either side — or a type mismatch between
two `Ok` values — yields `Unknown`, carrying the canonical `EvalError` as its cause.

**Condition evaluation carries causal attribution, not every error observed.** A condition
denotes a pair of its Kleene truth value and the *finite set of errors that actually
determined that truth value* — never the set of every error encountered anywhere in its
subtree:

```
ConditionResult = { truth : Truth, causes : Set<EvalError> }
```

Rules (instantiated by And/Or/Xone/Not below):
- An atomic resolution or comparison error produces `{ truth: Unknown, causes: {error} }`.
- `Not` preserves `causes` unchanged; only `truth` is negated.
- `And`, `Or`, and `Xone` first compute their Kleene truth value from the children's `truth`
  fields alone.
- If that truth value is `Unknown`, `causes` is the union of the `causes` of every child whose
  `truth` is `Unknown`.
- If the truth value is conclusively `True` or `False`, `causes` is **empty**: an error masked
  by a conclusive branch elsewhere in the same connective did not cause the result and must
  not be reported as if it did — there is no "winning error" to arbitrate.
- `causes` is a finite set under canonical error identity; ordering matters only when
  serializing diagnostics. An implementation MAY additionally keep every error encountered,
  causal or not, in a separate `observedErrors` side-channel for debugging — that channel is
  never attached to an `indeterminate` atom's payload (below), whose `causes` must explain
  *why that verdict* is unknown, nothing broader.

**Logical connectives are Kleene strong three-valued logic** — an error is *unobservable* when it
cannot change the outcome (short-circuit is therefore **specified**, not left implicit):

```
And:  True∧x = x ;  False∧x = False ;  Unknown∧False = False ;  Unknown∧(True|Unknown) = Unknown
Or:   False∨x = x ;  True∨x = True ;   Unknown∨True  = True  ;  Unknown∨(False|Unknown) = Unknown
Not:  ¬True = False ; ¬False = True ;  ¬Unknown = Unknown
Xone(c₁..cₙ): if any cᵢ = Unknown → Unknown; else True iff exactly one is True, else False
```

**Normative promotion.** A norm whose condition denotes `Unknown` is **not** silently inactive:
it contributes **`Indeterminate`** to the normative envelope. Mapping `Indeterminate → Deny` is an
**enforcement-adapter** policy (fail-closed at the PEP), *not* the semantic result — the evaluator
reports `Indeterminate` rather than silently choosing. The result retains the causal diagnostics.

We write, for the two kinds of denotation:

```
⟦ e ⟧      : Env → Value            -- terms (operands, right-values)
⟦ c ⟧      : Env → ConditionResult  -- conditions: truth plus the causal error set
```

Where only the truth value is needed (norm/policy activation checks, operational-semantics
guards), we read `⟦c⟧(Env).truth`; the full pair is consumed where causal attribution matters
(`deriveNorms`'s `indeterminate` atom, §Normative Derivation).

### Conditions

Atomic constraints (result is a `ConditionResult`, lifting operand and type errors to
`Unknown` with the responsible error attached as `causes`):

```
⟦ AtomicConstraint(op, operator, value, targetNorm?) ⟧(Env) : ConditionResult =
     let leftEV  = resolve(op, Env, targetNorm)          -- : EvalValue<Value>
     let rightEV = case value of
         RuntimeRef(r) → resolveRuntime(r, Env)           -- : EvalValue<Value>
         IRIRef(u)     → Ok(VURI(u))
         Literal(v)    → Ok(v)
         ValueSet(vs)  → Ok(VSet(canonicalMembers(vs)))
     in case (leftEV, rightEV) of
         (Ok(l), Ok(r)) | typeCompatible(operator, l, r) →
             { truth: apply(operator, l, r, Env), causes: ∅ }
         (Ok(l), Ok(r)) →
             { truth: Unknown, causes: { mkTypeMismatch(operator, targetNorm, l, r) } }
         _ →
             { truth: Unknown, causes: nonOk(leftEV) ∪ nonOk(rightEV) }

nonOk(Ok(_)) = ∅
nonOk(Err(e, _)) = { e }

typeCompatible(operator, l, r) =
    case operator of
        eq | neq            → sameDomain(l, r)
        lt | lte | gt | gte → ordered(l) ∧ ordered(r) ∧ sameDomain(l, r)
        isA                  → isURI(l) ∧ isURI(r)
        isAnyOf              → isSet(r) ∧ compatibleValueSet(l, r)
        isAllOf              → isSet(l) ∧ isSet(r) ∧ compatibleSets(l, r)
        isNoneOf             → isSet(r) ∧ compatibleValueSet(l, r)

sameDomain(l, r) = valueType(l) = valueType(r)
ordered(v)       = valueType(v) ∈ {Int, Decimal, DateTime, Duration}
isURI(VURI(_))   = true;   isURI(_) = false
isSet(VSet(_))   = true;   isSet(_) = false

homogeneous(VSet(xs)) = ∀x,y ∈ xs : sameDomain(x,y)
compatibleSets(VSet(xs), VSet(ys)) =
    homogeneous(VSet(xs)) ∧ homogeneous(VSet(ys)) ∧
    (xs = [] ∨ ys = [] ∨ sameDomain(head(xs), head(ys)))
compatibleValueSet(VSet(xs), s : VSet) = compatibleSets(VSet(xs), s)
compatibleValueSet(v, VSet(ys)) = ¬isSet(v) ∧ homogeneous(VSet(ys)) ∧
                                  (ys = [] ∨ sameDomain(v, head(ys)))

    -- A profile may extend `ordered` only by declaring a total comparator for the new domain.
    -- No case admitted here can make `apply` get stuck. The `isA` right URI is verified as a
    -- class/subsumption-index key during compilation; `typeCompatible` checks its value shape.

mkTypeMismatch(operator, targetNorm, l, r) =
    Invalid({ site: ComparisonSite(operator, valueType(l), valueType(r)),
              target: targetNorm })
```

The RDF property remains named `rl2:targetNorm`, but its semantic value is the tagged
`StateTarget`: `NormTarget` for Duty-state queries and `PromiseTarget` for Promise-state queries.
The right operand may be a literal value or a runtime reference (e.g.,
`currentAgent`). If either operand is `Missing`/`Invalid`/`Conflict`, or the two resolved values
are not type-compatible for `operator`, the result is `Unknown` carrying that error as its
cause — the constraint never silently reads as `False`.

Logical conditions (Kleene strong three-valued, with `causes` masked whenever the connective
reaches a conclusive verdict — see Result and Truth Algebra):

```
foldK(kleeneOp, rs) =
    let t = kleeneOp([ r.truth | r ← rs ])
    in { truth: t,
         causes: if t ∈ {True, False} then ∅
                 else ⋃ { r.causes | r ∈ rs, r.truth = Unknown } }

⟦ And(cs)  ⟧(Env) = foldK(kAnd,  [ ⟦cᵢ⟧(Env) | cᵢ ← cs ])
⟦ Or(cs)   ⟧(Env) = foldK(kOr,   [ ⟦cᵢ⟧(Env) | cᵢ ← cs ])
⟦ Xone(cs) ⟧(Env) = foldK(kXone, [ ⟦cᵢ⟧(Env) | cᵢ ← cs ])
⟦ Not(c)   ⟧(Env) = let r = ⟦c⟧(Env) in { truth: ¬ᴷ r.truth, causes: r.causes }
```

`cs` is the `Condition{2,}` operand sequence (§Abstract Syntax, at least two conditions per
`AndOrXoneOperandCardinalityShape`); `kAnd`/`kOr`/`kXone` are the Kleene truth tables above,
applied to the full list of child truths at once — `kXone` in particular is "exactly one
`True`, else `Unknown` if any child is `Unknown`," not a chained binary XOR (chaining would
compute parity past two operands, the wrong answer).

---

### Helper Function Specifications

The condition semantics rely on several helper functions. For a testable evaluator, these must be precisely specified.

#### resolve : LeftOperand × Env × StateTarget? → EvalValue\<Value\>

The function `resolve(leftOperand, Env, targetNorm?)` maps a left operand to an
`EvalValue<Value>`: `Ok(v)` on success and `Err(error,note)` on failure. Although the RDF
property keeps its stable name `rl2:targetNorm`, the semantic parameter is a `StateTarget?` and
therefore preserves whether the referenced clause is a Norm or a Promise.

Resolution is closed over the policy, Request, snapshot, and configuration. There is no
function-based or external-lookup fallback inside `Eval`.

```
resolve : LeftOperand × Env × StateTarget? → EvalValue<Value>

failure(kind, site, target, note) =
    Err(kind({ site: site, target: target }), Some(note))

resolve(op, Env, targetNorm) =
    case op of
        -- Core derived-status operands
        obligationStateOperand →
            case targetNorm of
                Some(NormTarget(d : Duty)) →
                    resolveDutyStatus(d, Env.Universe, Env.Snapshot, Env.Configuration)
                None → failure(Missing, op, None, "obligationStateOperand requires a targetNorm")
                _    → failure(Invalid, op, targetNorm, "obligationStateOperand requires a Duty target")
        promiseStateOperand →
            case targetNorm of
                Some(PromiseTarget(p)) →
                    resolvePromiseStatus(p, Env.Universe, Env.Snapshot, Env.Configuration)
                None → failure(Missing, op, None, "promiseStateOperand requires a targetNorm")
                _    → failure(Invalid, op, targetNorm, "promiseStateOperand requires a Promise target")
        -- Profile-declared snapshot operands
        _ | op.resolutionPath ≠ ⊥ →
            deref(op.resolutionPath, op, Env)

        _ → failure(Missing, op, targetNorm, "operand has no core or snapshot binding")
```

Where:
* `obligationStateOperand` accepts `NormTarget(d : Duty)` and queries the derived Duty status
* `promiseStateOperand` accepts `PromiseTarget(p)` and queries the derived Promise status
* `op.resolutionPath` — path expression declared on the operand via `rl2:resolutionPath`
* `Err(Missing(key),note)` indicates the operand could not be resolved — never fatal,
  always lifted to `Unknown` at the condition level; a present target of the wrong variant is
  `Err(Invalid(key),note)` instead

All policy-visible contextual data uses declared `rl2:LeftOperand` instances. Core status
operands use the fixed branches above, `currentDateTime` uses its fixed `state.Clock` path, and
profile operands use explicit snapshot paths. This provides:

- Type safety (operands can declare expected ranges)
- Validation (SHACL can verify operand usage)
- Specifiability (one finite lookup algorithm)
- Auditability (all data access points are declared)

RL2 Core defines the following left operand instances:

* `currentDateTime` → `WorldSnapshot.evaluationTime`
* `obligationStateOperand` → derived Duty status (requires a Duty-valued `targetNorm`)
* `promiseStateOperand` → derived Promise status (requires a Promise-valued `targetNorm`)

Profiles define domain-specific left operands with resolution paths, such as:
* `purpose` → `rl2:resolutionPath "context.purpose"`
* `dataOwner` → `rl2:resolutionPath "asset.dataOwner"`
* `department` → `rl2:resolutionPath "agent.department"`

#### Runtime References

Runtime references resolve to values at evaluation time. These are used in `rightOperandRef` for dynamic comparisons.

```
resolveRuntime : RuntimeReference × Env → EvalValue<Value>

resolveRuntime(ref, Env) =
    case ref of
        currentAgent → Ok(Env.Agent)
        _            → failure(Missing, ref, None, "unrecognized runtime reference")
```

The `currentAgent` reference resolves to `Env.Agent`, the requesting agent. Other IRI-valued
right operands are ordinary `VURI` constants and do not invoke `resolveRuntime`.

#### Profile Resolution

A policy may declare vocabulary dependencies with `rl2:requiresProfile` (each value an `rl2:Profile` carrying an `rl2:profileVersion`). Before evaluation, the loader runs profile resolution against the evaluator's **supported-profile registry** — a set of `(profileIRI, supportedVersion)` pairs that is evaluator state, not part of the policy graph.

**Unknown-profile rule (fail-closed).** For each `requiresProfile P`, the loader MUST find a supported entry whose IRI equals `P`'s IRI and whose version is *compatible*. If any required profile is unsupported or only supported at an incompatible version, the policy is **rejected at load time** — never evaluated with a partially-understood vocabulary, and never silently accepted by ignoring the requirement:

```
loadOK(Policy, Registry) =
    ∀ P ∈ requiredProfiles(Policy) :
        ∃ (iri, supV) ∈ Registry :
            iri = P.iri ∧ compatible(supV, P.profileVersion)
    -- otherwise: reject(Policy) at ingestion (a load error, not ⊥ at eval time)
```

**Version negotiation (SemVer, same-major).** The referenced Profile's declared version is the **minimum required**:

```
compatible(supV, reqV) =
    supV.MAJOR = reqV.MAJOR ∧ (supV.MINOR, supV.PATCH) ≥ (reqV.MINOR, reqV.PATCH)
```

A major-version mismatch is always incompatible (breaking changes); a higher supported minor/patch is compatible (additive changes). This mirrors the SHACL `ProfileShape`/`RequiresProfileShape` structural checks, which only verify the declarations are well-formed — the compatibility decision itself is a runtime check because the registry is not in the graph.

#### deref : Path × LeftOperand × Env → EvalValue\<Value\>

`deref` interprets a declared path as a key into the normalized snapshot. It never traverses a
host-language object or invokes a connector.

```text
Path       ::= Root '.' Segment ('.' Segment)*
Root       ::= 'agent' | 'asset' | 'context' | 'state' | 'request' | 'global'
Segment    ::= Identifier
Identifier ::= [a-zA-Z_][a-zA-Z0-9_]*
```

A path exceeding `MaxPathDepth`, using another root, containing an empty segment, or containing
`*`, `/`, `\\`, `%`, `..`, or an escape sequence is rejected during canonical projection. Paths
are data keys, not filesystem or language-level member expressions.

The only canonical `request.*` paths are `request.requestingAgent`,
`request.requestedAction`, and `request.requestedAsset`. Any other `request.*` path is rejected
during canonical projection.

```text
deref(path, op, Env) =
    case path of
        "request.requestingAgent" → requestField(Env.Request, requestingAgent, path)
        "request.requestedAction" → requestField(Env.Request, requestedAction, path)
        "request.requestedAsset"  → requestField(Env.Request, requestedAsset, path)
        "request." + _            → failure(Invalid, path, None,
                                             "unsupported core Request field")
        "state.Clock"             → Ok(Env.Snapshot.evaluationTime)
        _ →
            case factKey(path, Env.Agent, Env.Asset) of
                Err(e,note) → Err(e,note)
                Ok(key) → resolveFact(key, declaredType(op), declaringProfile(op),
                                      Env.Snapshot, Env.Configuration)
```

`requestField(None,_,path)` returns `Invalid({ site: Path(path), target: None })`; a request path therefore cannot
silently read a Duty or Promise status environment. `factKey` is total over canonical fact paths
when the required scope is present:

```text
factKey("agent."   + rest, a, _)       = Ok(AgentScope(a), canonicalPath)
factKey("asset."   + rest, _, Some(s)) = Ok(AssetScope(s), canonicalPath)
factKey("asset."   + rest, _, None)    = failure(Missing, canonicalPath, None,
                                                  "status content has no asset scope")
factKey("context." + rest, _, _)       = Ok(EvaluationScope, canonicalPath)
factKey("state."   + rest, _, _)       = Ok(StateScope, canonicalPath)
factKey("global."  + rest, _, _)       = Ok(GlobalScope, canonicalPath)
```

`request.*` has exactly the three fields in the core Request. Additional request metadata must be
a declared `context.*` fact or belong to an interchange profile; an evaluator cannot invent a
fourth implicit Request field.

The `global` root contains caller-supplied aggregate facts in `GlobalScope`. Computing a seat
count, active-Agreement set, or other aggregate happens during snapshot assembly. `Eval` applies
the same fact-resolution rules as for any other root.

#### Declarative Duty and Promise status

Status is a result over immutable inputs, not a stored-state transition:

```
DutyStatus    ::= Pending | Active | Fulfilled | Violated
PromiseStatus ::= Pending | Fulfilled | Violated

StatusResult<S> ::= Known(S)
                  | IndeterminateStatus(causes : finite non-empty Set<EvalError>)
```

`IndeterminateStatus` is not an ontology state. It preserves errors that prevent the evaluator
from selecting one of the existing state individuals. Policy RDF contains no asserted Duty or
Promise status; every status is derived from the evaluation inputs.

One Duty node denotes one occurrence. A present `dutyWindow` is the finite half-open interval
`[startInclusive, endExclusive)`; absence is unbounded. The following predicates fix every
boundary:

```
before(d, now) = d.window ≠ None ∧ now < d.window.startInclusive
inside(d, t)   = d.window = None ∨
                 d.window.startInclusive ≤ t < d.window.endExclusive
closed(d, now) = d.window ≠ None ∧ now ≥ d.window.endExclusive
```

At the start instant the Duty is assessable. Evidence at the end instant is outside the window;
at that same instant a still-unsatisfied Achievement Duty is Violated. There is no implicit
recurrence or terminal-state reset. A repeated period requires another canonical Duty node.

`at(W,t)` is `W` with `evaluationTime = t`. It does not mutate the supplied snapshot. Status
conditions use a request-free environment whose agent and asset scopes are fixed by the Duty or
Promise content; `request.*` is invalid in a postcondition, invariant, or promised state. The
normal fact-validity and evidence-eligibility rules therefore define a historical slice from the
same finite semantic input:

```
mkStatusEnv(U, a, s?, W, C) = (U, None, a, s?, W, C)
evalAt(c, t, U, a, s?, W, C) = ⟦c⟧(mkStatusEnv(U,a,s?,at(W,t),C))
```

For an Achievement Duty, evidence is selected by the Duty subject, an action equal to or narrower
than the required action, the Duty object, and the Duty window.
The selector adds no ambient storage-order condition. If `postCondition` is absent, each
selected evidence item is a qualifying witness. If present, it is evaluated at that item's occurrence
time; later unrelated state cannot retroactively make an action successful:

```
achievementCandidates(d, U, W, C) =
    selectEvidence(actionSelector(d.subject, d.action, d.object, d.window, U), W, C)

qualifies(d, e, U, W, C) =
    case d.postCondition of
        None     → { truth: True, causes: ∅ }
        Some(pc) → evalAt(pc, e.occurredAt, U, d.subject, Some(d.object), W, C)
```

`actionSelector(a,x,s,w,U)` selects evidence whose actor is `a`, whose object is `s`, whose action
is equal to or included in `x` under `U.actionAncestors`, and whose occurrence time is inside `w`
(or unrestricted when `w=None`). `selectEvidence` then applies the snapshot's attribution rules
from `RL2_Model.md` §4.3.

`achievementStatus` is total:

```
achievementStatus(d, U, W, C) =
    if before(d, W.evaluationTime) then Known(Pending)
    else case achievementCandidates(d, U, W, C) of
        Err(e) → IndeterminateStatus({e})
        Ok(es) →
            let qs = [ qualifies(d,e,U,W,C) | e ∈ es ] in
            if ∃q ∈ qs : q.truth = True then Known(Fulfilled)
            else if ∃q ∈ qs : q.truth = Unknown then
                IndeterminateStatus(⋃ { q.causes | q ∈ qs, q.truth = Unknown })
            else if closed(d, W.evaluationTime) then Known(Violated)
            else Known(Active)
```

No matching action evidence is `Ok(∅)`, not `Missing`: it means the Achievement has not yet been
fulfilled. Relevant malformed, inadmissible, or conflicting evidence remains an error.

For a windowed Maintenance Duty, `elapsed(d,now)` is the set of instants inside its window no
later than `now`. `throughout` applies the existing three-valued condition semantics to every
such instant:

```
throughout(i, d, U, W, C) =
    let rs = { evalAt(i,t,U,d.subject,Some(d.object),W,C) |
               t ∈ elapsed(d,W.evaluationTime) } in
    if ∃r ∈ rs : r.truth = False then { truth: False, causes: ∅ }
    else if ∀r ∈ rs : r.truth = True then { truth: True, causes: ∅ }
    else { truth: Unknown,
           causes: ⋃ { r.causes | r ∈ rs, r.truth = Unknown } }
```

This is not an instruction to sample a continuous clock. Over a finite snapshot and bounded
condition tree, truth changes only at the finite boundaries contributed by fact-validity
intervals, the Duty window, and literal time comparisons. A conforming
implementation partitions the elapsed window into truth-invariant finite cells at those
boundaries, retaining singleton boundary cells when equality or inclusivity can change truth, and
evaluates one representative per cell. An uncovered cell resolves the relevant fact as `Missing`
and therefore yields `Unknown`.

```
maintenanceStatus(d, U, W, C) =
    if before(d, W.evaluationTime) then Known(Pending)
    else if d.window = None then
        case evalAt(d.invariant,W.evaluationTime,U,d.subject,Some(d.object),W,C) of
            { truth: True, _ }       → Known(Active)
            { truth: False, _ }      → Known(Violated)
            { truth: Unknown, causes } → IndeterminateStatus(causes)
    else let r = throughout(d.invariant, d, U, W, C) in
            if r.truth = False then Known(Violated)
            else if r.truth = Unknown then IndeterminateStatus(r.causes)
            else if closed(d, W.evaluationTime) then Known(Fulfilled)
            else Known(Active)

dutyApplicabilityResult(d, U, W, C) =
    case d.condition of
        None    → { truth: True, causes: ∅ }
        Some(c) → ⟦c⟧(mkStatusEnv(U,d.subject,Some(d.object),W,C))

dutyStatus(d, U, W, C) =
    if before(d, W.evaluationTime) then Known(Pending)
    else case dutyApplicabilityResult(d,U,W,C) of
        { truth: False, _ }          → Known(Pending)
        { truth: Unknown, causes }   → IndeterminateStatus(causes)
        { truth: True, _ } → case d of
            AchievementDuty(_) → achievementStatus(d,U,W,C)
            MaintenanceDuty(_) → maintenanceStatus(d,U,W,C)
```

A false applicability guard therefore denotes a Duty that is not currently required and remains
`Pending`; it is not a fulfilled Duty. A profile that needs a one-way trigger must provide a
snapshot fact whose validity records that the trigger remains established. Missing or conflicting
applicability data produces `IndeterminateStatus`.

A Maintenance Duty without a finite window is an ongoing snapshot requirement: it is Active when
the invariant is true now, Violated when false now, and cannot be Fulfilled. It makes no claim
about an interval with an unspecified start. For a windowed Maintenance Duty, complete coverage
is required; merely observing the invariant as true at `evaluationTime` is insufficient.

Promise status is derived without a Promise state machine:

```
promiseStatus(pr, U, W, C) =
    let Promise(p,q,s?,content) = pr in
    case content of
        PromisedAction(x) →
            case s? of
                None → IndeterminateStatus({
                    Missing({ site: StatusSite(PromiseTarget(pr)),
                              target: Some(PromiseTarget(pr)) }) })
                Some(s) → case selectEvidence(actionSelector(p,x,s,None,U), W, C) of
                    Err(e)    → IndeterminateStatus({e})
                    Ok(∅)     → Known(Pending)
                    Ok(_)     → Known(Fulfilled)

        PromisedState(c) →
            case ⟦c⟧(mkStatusEnv(U,p,s?,W,C)) of
                { truth: True,  _ }      → Known(Fulfilled)
                { truth: False, _ }      → Known(Violated)
                { truth: Unknown, causes } → IndeterminateStatus(causes)

```

`mkStatusEnv` admits `agent.*`, `asset.*`, `state.*`, `context.*`, and `global.*`, binding agent and
asset to the Promise content rather than an access Request. A status condition that uses
`request.*` is invalid because status derivation has no access Request.
`PromisedAction` has no Duty window: it may be fulfilled by evidence but does not become Violated
solely through elapsed time. Acceptance can crystallize it into a bounded Duty.

Status dependencies induced by `targetNorm` must be acyclic. Canonical projection rejects a
self-reference or cycle with `Invalid(ConfigurationSite("statusDependency"))`; memoized structural
evaluation then terminates and gives each referenced Duty or Promise one result.

```
statusDiagnostics(statuses) =
    ⋃ { es | IndeterminateStatus(es) ∈ range(statuses) }
```

The core status operands expose a `Known` state as an ordinary value. When status is
indeterminate, the atomic operand reports one stable status-site error; the complete underlying
causes remain in `EvaluationResult.diagnostics` through `statusDiagnostics`.

```
resolveDutyStatus(d,U,W,C) =
    case dutyStatus(d,U,W,C) of
        Known(s) → Ok(s)
        IndeterminateStatus(_) →
            Err(Invalid({ site: StatusSite(NormTarget(d)),
                          target: Some(NormTarget(d)) }),
                Some("Duty status is indeterminate"))

resolvePromiseStatus(p,U,W,C) =
    case promiseStatus(p,U,W,C) of
        Known(s) → Ok(s)
        IndeterminateStatus(_) →
            Err(Invalid({ site: StatusSite(PromiseTarget(p)),
                          target: Some(PromiseTarget(p)) }),
                Some("Promise status is indeterminate"))
```

#### apply : Operator × Value × Value × Env → Boolean

The function `apply(op, left, right, Env)` applies a comparison operator to two **already-resolved,
already type-compatible** values — the `AtomicConstraint` denotation (§Conditions) is the only
caller, and it calls `apply` only after `typeCompatible(operator, left, right)` holds; a
domain mismatch is caught there and surfaced as `Invalid`, never passed into `apply`:

```
apply : Operator × Value × Value × Env → Boolean

apply(op, left, right, Env) =
    case op of
        eq       → left = right
        neq      → left ≠ right
        lt       → left < right
        lte      → left ≤ right
        gt       → left > right
        gte      → left ≥ right
        isA      → instanceOf(left, right, Env.Universe)
        isAnyOf  → valuesOf(left) ∩ elements(right) ≠ ∅
        isAllOf  → elements(right) ⊆ elements(left)
        isNoneOf → valuesOf(left) ∩ elements(right) = ∅

valuesOf(VSet(xs)) = set(xs)
valuesOf(v)         = {v}       -- admitted only for scalar v by typeCompatible
elements(VSet(xs))  = set(xs)   -- called only after typeCompatible established VSet

instanceOf(VURI(u), VURI(c), U) =
    ∃t : (u rdf:type t) ∈ U ∧ (t = c ∨ t rdfs:subClassOf+ c in U)
```

Canonical projection computes the finite `rdf:type`/`rdfs:subClassOf` closure used by `isA`.
Profiles that use `isA` must supply the relevant classes and hierarchy in the policy universe.

---

## Denotational Semantics for Norms

Norms are evaluated in the context of a **Request** `R = (a_req, x_req, s_req)` specifying the requesting agent, requested action, and target asset. The denotation takes both the request and an environment constructed from it.

### Environment Construction

Given a PolicyUniverse `U`, Request `R = (a_req, x_req, s_req)`, WorldSnapshot `W`, and
EvaluationConfiguration `C`:

```
mkEnv(U, R, W, C) = (U, R, a_req, s_req, W, C)
                    -- (Universe, Request, Agent, Asset, Snapshot, Configuration)
```

The environment retains the full Request so `request.*` paths resolve. All other dynamic values
come from `W`; `U` supplies canonical action and collection indexes; `C` supplies profiles,
declared bounds, trust parameters, and the combining strategy.

### Request Matching

A norm applies to a request only if the norm's subject, action, and object match the request:

```
matchesRequest(n, Env) =
    let R = Env.Request in
    subjectMatches(n.subject, R.requestingAgent, Env) ∧
    objectMatches(n.object, R.requestedAsset, Env.Universe) ∧
    actionMatches(n, R.requestedAction, Env.Universe)

subjectMatches(a, requested, Env) =
    a = requested

objectMatches(s, requested, U) =
    s = requested ∨ requested ∈ members(s,U)

actionMatches(AchievementDuty(_,_,x,_,_,_,_), requested, U) =
    x = requested ∨ includedInAction(requested,x,U)
actionMatches(Privilege(_,x,_,_,_), requested, U) =
    x = requested ∨ includedInAction(requested,x,U)
actionMatches(Prohibition(_,x,_,_), requested, U) =
    x = requested ∨ includedInAction(requested,x,U)
actionMatches(MaintenanceDuty(_), _, _) = true
```

Where:
- `includedInAction(x_req, x, U)` tests the finite canonical action-inclusion index
- `members(s, U)` returns the **direct** `rl2:member` individuals of `s` in the canonical policy
  universe when `s` is an `AssetCollection` (empty otherwise)

A Maintenance Duty has no requested action to match. The `true` action component above makes an
independent Maintenance Duty a candidate on its subject and object only. An attached Duty is
reached through its owning Privilege and therefore uses the Privilege's request match; its own
subject and object still determine performance evidence, not access matching.

`AssetCollection ⊑ Asset`, so a norm may target a collection directly and a collection may itself
be a member of another collection. Core `members(s,U)` is not transitively closed: membership in
a nested sub-collection does not match the outer collection. Membership is read from the fixed
canonical PolicyUniverse.

Action subsumption is defined by the transitive closure of `rl2:includedIn`:

```
x' ⊑ᵁ x  :=  includedInAction(x', x, U)
```

Canonical projection computes the finite transitive closure of `rl2:includedIn` in `U`. Usage of
`rdfs:subClassOf` for action refinement is non-normative in RL2.

Action subsumption applies uniformly across request matching and Achievement evidence selection.
There is no stored `Performed` Boolean; `achievementCandidates` derives performance from the
immutable evidence set.

**RDF grounding**: Actions are individuals of `rl2:Action`. Action subsumption (`x' ⊑ x`)
follows the transitive closure of `rl2:includedIn`; `members(s)` is the set of direct `rl2:member`
links when `s` is an `rl2:AssetCollection`. A conduct norm's subject matches the requesting Agent
exactly. Role-based authorization uses an explicit condition over a profile-defined agent fact.

Policy and clause conditions are combined by `effectiveCondition`. During derivation, `True`
activates a matching clause, `False` leaves it inactive, and `Unknown` produces an attributed
`indeterminate` atom. A Duty's own applicability guard also gates its derived status as specified
above; its action and optional postcondition, or its invariant, determine status once that guard
is true. The policy universe is an immutable caller-supplied input; discovery and version selection
occur before `Eval`.

---

## Pure Offer Acceptance (Offer → Agreement)

An **Offer** may contain voluntary Promises together with Norms that are restated as terms of the
proposed Agreement. A Promise is not an operative Norm before acceptance. Acceptance is a pure,
one-time policy transformation; it is not an
event consumed by `Eval`, a state transition, or an instruction to persist anything.

The transformation operates on the validated normalized Offer and explicit acceptance
parameters:

```text
SourceRef  = stable canonical identity of one Promise clause or policy-local Norm
PromiseRef = SourceRef restricted to Promise clauses

Acceptance = (
    agreementId   : IRI,
    grantor        : Agent,
    grantee        : Agent,
    primaryIds     : total map SourceRef  → IRI,
    objectBindings : partial map PromiseRef → Asset,
    dutyWindows    : partial map PromiseRef → DutyWindow
)

MaterializationResult =
      Materialized(agreement : Agreement, sourceMap : map SourceRef → IRI)
    | Rejected(errors : non-empty finite set of MaterializationError)

MaterializationError ::=
      InvalidOffer(site, reason : InvalidOfferReason)
    | PartyMismatch(promiseRef)
    | InvalidIdentityAllocation(id)
    | MissingPromiseObject(promiseRef)
    | InvalidDutyWindow(promiseRef)
    | DanglingInternalReference(site, targetId)

InvalidOfferReason ::=
      WrongPolicyKind | EmptyClauseSet | ConflictingObjectBinding
    | InvalidAcceptanceDomain | NonLocalPromiseTarget
    | InvalidOutputShape | StatusDependencyCycle
```

`primaryIds` assigns the output Norm identifier for every materialized source: the crystallized
Duty for a Promise and the copied Norm for a policy-local Norm. Locality is structural and narrow:

```text
localNorms(O) =
    { n : Norm | n ∈ O.clauses }
    ∪ { d : Duty | ∃ n : Privilege ∈ O.clauses : d ∈ n.prerequisiteDuties }
```

The second set contains the non-clause Duties owned through `prerequisiteDuty`; their attachment
placement is preserved rather than promoted to Agreement clauses. `targetNorm` is a reference,
not an ownership relation. Its target is rewritten only when independently present in
`localNorms(O)` or among the Promise clauses of `O`; otherwise it remains external and is not
copied. Canonical RDF projection preserves this distinction.

Define `sourceIris(O)` as every IRI occurring as an RDF term in the canonical projection of `O`;
blank nodes contribute no IRI. `agreementId` and all `primaryIds` values MUST be pairwise distinct,
and the resulting set of allocated IRIs MUST be disjoint from `sourceIris(O)`. Identifier allocation is therefore
explicit input, not a nondeterministic `fresh IRI` operation. How a caller allocates globally
unique IRIs is outside the transformation. `ref(x)` denotes the `SourceRef` assigned to source
Promise or local Norm `x` by the normalized projection; materialization depends only on its stable
identity and equality, not on its concrete encoding.

`objectBindings` may supply an object for either an action or state Promise when the Offer leaves
the catalogue target open. A conflicting authored and supplied object is `InvalidOffer`; an
identical binding is accepted but has no effect. `dutyWindows` supplies an optional finite
performance interval for the Duty created from a Promise. It does not alter a copied Norm clause.

An Offer-level `condition` denotes the applicability guard proposed for the resulting Agreement;
it does not determine whether or when an Acceptance may be issued. Offer validity, withdrawal,
and acceptance authorization are outside this pure transformation. Materialization therefore
rewrites and copies `O.condition` as the Agreement-level applicability guard.

### Validation

`materialize(O,A)` collects all applicable errors and returns `Rejected(errors)` without a partial
Agreement when any error exists. A value is **structurally conforming** when it inhabits the typed
abstract syntax in this document and its RDF projection satisfies the applicable core SHACL
shapes. The input is valid only when:

1. `O` is a structurally conforming `Offer` with a non-empty finite clause set;
2. any `grantor` or `grantee` authored on `O` equals the corresponding value in `A`;
3. each Promise's `(promisor,promisee)` is either `(A.grantor,A.grantee)` or
   `(A.grantee,A.grantor)`—orientation may differ, but acceptance cannot bind an absent third
   party;
4. `primaryIds` has domain `PromiseClauses(O) ∪ localNorms(O)`, the optional maps have no other
   keys, and the identity map satisfies the freshness and injectivity rule;
5. every promised action or state has exactly one object after applying `objectBindings`;
6. every `dutyWindows[p]` satisfies
   `dutyWindows[p].startInclusive < dutyWindows[p].endExclusive`;
7. every Promise-valued `targetNorm` occurring in the Offer's policy condition, clause conditions,
   Promise content, or attached prerequisite Duties targets a Promise clause of that same Offer;
8. every reference to a clause of `O` has a corresponding `primaryIds` entry; and
9. rewriting produces an acyclic, structurally conforming Agreement.

A failure of item 6 yields `InvalidDutyWindow(ref(p))`; a failure of item 7 yields
`InvalidOffer(site, NonLocalPromiseTarget)`. `StatusDependencyCycle` reports a cycle already
present in the Offer's status-dependency graph: injective renaming and the typed Promise-to-Duty
operand rewrite cannot create one.

Materialization-error identity is the constructor plus its typed fields; explanatory prose is not
part of identity. Errors are enumerated by constructor, site, and referenced identifier, so
validation order cannot change the result. A primary error on a Promise (missing object, invalid
Duty window, or party mismatch) suppresses derivative output-shape and
rewrite errors caused solely by the absence of that Promise's generated Duty; independent errors
are still collected.

### Crystallization

For a Promise `p = Promise(promisor, promisee, object?, content)`, let `s` be its authored object
or accepted object binding, and let `w` be its accepted Duty window if one exists:

```text
crystallize(p,A) =
    case p.content of
        PromisedAction(x) →
            AchievementDuty(subject = p.promisor,
                            counterparty = Some(p.promisee),
                            action = x,
                            object = s,
                            condition = True,
                            postCondition = None,
                            dutyWindow = w)

        PromisedState(i) →
            MaintenanceDuty(subject = p.promisor,
                            counterparty = Some(p.promisee),
                            object = s,
                            condition = True,
                            invariant = i,
                            dutyWindow = w)

```

The Duty identifier is `A.primaryIds[ref(p)]`. The Promise beneficiary is retained as the Duty's
`counterparty`; no additional norm is generated.

A `PromisedAction` without an accepted window creates an unbounded Achievement Duty, which can
remain Pending. A `PromisedState` without a window creates an ongoing Maintenance Duty, which can
be Active or Violated but cannot become Fulfilled. A finite accepted window gives the resulting
Duty the status boundaries defined in §Declarative Duty and Promise status.

### Clause copying and reference rewriting

Let `sourceMap(x) = A.primaryIds[ref(x)]`. Each policy-local Norm is structurally copied under
`sourceMap(n)`. Immutable value expressions may be shared; Norm identity is never shared across
the Offer and Agreement. Only mapped top-level Norms become Agreement clauses; copied attached
Duties remain attached. All Norm-valued references inside the copied policy condition and
clauses are traversed recursively:

```text
rewriteRef(r) =
    if r is a Promise clause or policy-local Norm of O then sourceMap(r) else r

rewriteAtomic(a) =
    if a.targetNorm = PromiseTarget(p) then
        a[targetNorm  ↦ NormTarget(sourceMap(p)),
          leftOperand ↦ obligationStateOperand]
    else a[targetNorm ↦ rewriteRef(a.targetNorm)]
```

`rewriteRef` applies to `prerequisiteDuty` and Norm-valued `targetNorm`. A Promise-valued
`targetNorm` necessarily uses `promiseStateOperand` by the canonical syntax and has the rewrite
shown above. Conditions without `targetNorm` are copied structurally.

The result is:

```text
materialize(O,A) =
    if validateMaterialization(O,A) = errors ≠ ∅ then Rejected(errors)
    else Materialized(
        Agreement(id        = A.agreementId,
                  grantor   = A.grantor,
                  grantee   = A.grantee,
                  condition = rewrite(O.condition),
                  clauses   = copiedTopLevelNorms(O,A)
                              ∪ crystallizedDuties(O,A),
                  metadata  = copyMetadata(O)
                              ∪ { prov:wasDerivedFrom ↦ O.id }),
        sourceMap)
```

No Promise survives in the Agreement. `materialize` neither reads a `WorldSnapshot` nor emits an
effect; identical Offer and Acceptance values produce the same result. With indexed maps it is
linear in the size of the normalized Offer, including its condition trees and references.
`copyMetadata` preserves non-structural annotations and profile/version requirements; it excludes
the source identifier, policy kind, parties, condition, clauses, and any prior materialization
provenance because those fields are constructed explicitly above.

`Eval` derives statuses and normative atoms but does not create remedial norms, consume events,
or mutate policy or world state.

## Normative Derivation (I/O-Logic Foundation)

RL2's evaluation follows an **I/O logic** pattern (Makinson & van der Torre): derivation produces a normative envelope, then conflict resolution yields a final decision.

### Pre-Resolution Normative Envelope

The function `Out` computes the **unresolved set** of normative atoms from a policy universe and
environment (atoms are deduplicated by canonical identity — the `∪` below is set union, not
multiset sum). Access clauses use `accessResult`: it folds the policy and clause conditions and,
for a Privilege, its prerequisite Duties. Independent Duties use `effectiveCondition` directly.
Attached Duties use `attachedDutyResult`, which makes the Duty applicable only within the scope of
its owning Privilege. An `Unknown` result is attributed to the affected norm rather than silently
treated as inapplicable.

For a Duty `d`, convert its derived status into a condition-shaped result:

```
fulfilledResult(d, Env) =
    case dutyStatus(d, Env.Universe, Env.Snapshot, Env.Configuration) of
        Known(Fulfilled)       → { truth: True,    causes: ∅ }
        Known(Pending)         → { truth: False,   causes: ∅ }
        Known(Active)          → { truth: False,   causes: ∅ }
        Known(Violated)        → { truth: False,   causes: ∅ }
        IndeterminateStatus(E) → { truth: Unknown, causes: E }

dutyConditionResult(d, Env) =
    case d.condition of
        None    → { truth: True, causes: ∅ }
        Some(c) → ⟦c⟧(mkStatusEnv(Env.Universe,
                                      d.subject,
                                      Some(d.object),
                                      Env.Snapshot,
                                      Env.Configuration))

prerequisiteResult(d, Env) =
    foldK(kOr, [notResult(dutyConditionResult(d,Env)), fulfilledResult(d,Env)])
    -- not applicable OR fulfilled

notResult(r) = { truth: ¬ᴷ r.truth, causes: r.causes }

allResults(rs) =
    if rs = [] then { truth: True, causes: ∅ } else foldK(kAnd, rs)

anyResults(rs) =
    if rs = [] then { truth: False, causes: ∅ } else foldK(kOr, rs)

canonicalDutyOrder(ds) = sort ds by dutyId
canonicalPrivilegeOrder(ns) = sort ns by privilegeId

accessResult(P, n : Privilege, Env) =
    allResults([⟦effectiveCondition(P,n)⟧(Env)] ++
               [ prerequisiteResult(d,Env) |
                 d ∈ canonicalDutyOrder(n.prerequisiteDuties) ])

accessResult(P, n : Prohibition, Env) = ⟦effectiveCondition(P,n)⟧(Env)

ownerScopeResult(P, n, d, Env) =
    if ¬matchesRequest(n,Env) then { truth: False, causes: ∅ }
    else foldK(kAnd, [⟦effectiveCondition(P,n)⟧(Env), dutyConditionResult(d,Env)])

attachedDutyResult(P, d, Env) =
    anyResults([ ownerScopeResult(P,n,d,Env) |
                 n ∈ canonicalPrivilegeOrder({ n : Privilege ∈ P.clauses |
                                               d ∈ n.prerequisiteDuties }) ])
```

`allResults` gives an empty prerequisite set the identity value `True`; it does not construct an
authored zero-arity `And`. `prerequisiteResult` masks irrelevant errors in the usual Kleene way:
an inapplicable Duty is satisfied as a prerequisite regardless of its separately reported status,
and a conclusively Fulfilled Duty is sufficient even when its applicability guard is Unknown.
Pending, Active, and Violated all mean that an applicable prerequisite has not been met. They
make that Privilege inactive; they do not create a global Deny.

```
Out : (PolicySet S, Env) → ℘(NormativeAtoms), where S ⊆ Env.Universe

Out(S, Env) =
    ⋃ { deriveNorms(P, Env) | P ∈ S }

deriveNorms(P, Env) =
    if P : Offer then ∅
    else
        { permit(n, P)   | n : Privilege ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = True } ∪
        { forbid(n, P)   | n : Prohibition ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = True } ∪
        { obligate(d, P) | d ∈ independentDuties(P), matchesRequest(d, Env), ⟦effectiveCondition(P,d)⟧(Env).truth = True } ∪
        { obligate(d, P) | d ∈ attachedDuties(P), attachedDutyResult(P,d,Env).truth = True } ∪
        { indeterminate(n, P, accessResult(P,n,Env).causes)
                         | n : Privilege ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = Unknown } ∪
        { indeterminate(n, P, accessResult(P,n,Env).causes)
                         | n : Prohibition ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = Unknown } ∪
        { indeterminate(d, P, ⟦effectiveCondition(P,d)⟧(Env).causes)
                         | d ∈ independentDuties(P), matchesRequest(d, Env), ⟦effectiveCondition(P,d)⟧(Env).truth = Unknown } ∪
        { indeterminate(d, P, attachedDutyResult(P,d,Env).causes)
                         | d ∈ attachedDuties(P), attachedDutyResult(P,d,Env).truth = Unknown }
```

`deriveNorms` reads the Request, snapshot, and configuration only through `Env`; there is no free
mutable state or external-context argument.

An Offer is transformation input, not an operative access policy. Its clauses contribute no
normative atoms before acceptance, so proposed Privileges cannot grant access and proposed Duties
cannot affect an access decision. `derivePromiseStatuses` and `deriveDutyStatuses` may still
report the snapshot-derived status of clauses reachable from an Offer for inspection and
diagnostics. Normative effect begins only in the materialized Agreement.

`violated(d, P)` is **not** an `Out`/`deriveNorms` atom. Duty status is a separate derived value.
It is read while deriving a Privilege with prerequisites and is also returned for every Duty
reachable from the supplied policy universe. An implementation may memoize the pure status
function; evaluation performs no status transition. Duty atoms remain in the envelope for
normative reporting but resolution ignores them. In particular, an unrelated violated Duty can
never deny a request.

The type filters are normative. Promises are not request-matched access candidates and therefore
do not produce access-decision `indeterminate` atoms.

**Provenance.** A `NormativeAtom` wraps the full norm object (`n`/`d`, not a projected
`(a,x,s)` triple) together with its source policy `P`. Every atom therefore identifies the norm
and policy that produced it. Atom equality is structural: `(atom-kind,n,P)` for
definite atoms and `(indeterminate,n,P,causes)` for Unknown atoms. `causes` is itself a canonical
set, so its enumeration order cannot create a second atom. Two policies granting the same
`(a,x,s)` shape remain distinct atoms with independent provenance because atom equality includes
`P`: even the same Norm `n` — SHACL permits one Norm to be a clause of multiple Policies — still
yields one distinct atom per owning Policy. For an attached Duty, `P` contains at least one
Privilege that references it; the Duty itself is not in `P.clauses`. Resolution consumes this
attributed envelope.

### Monotonicity of Derivation

For one fixed immutable environment, `Out` is monotone in the selected subset of that
environment's policy universe:

```
For fixed Env and S ⊆ S' ⊆ Env.Universe,
Out(S, Env) ⊆ Out(S', Env)
```

Since `Out` is a union of per-clause contributions evaluated independently against the same
`Env`, selecting another policy can only add atoms. The result is independent of
clause-processing order.

This does not claim monotonicity when `Env.Universe` itself changes. A different universe may
change shared action hierarchies, collection membership, or status dependencies and is therefore
a different semantic input.

`Out` is not monotone in the environment: `not`, `neq`, `isNoneOf`, and upper bounds can change
from true to false when facts change, removing a derived atom. The environment is therefore one
immutable snapshot per evaluation. No optimization may assume that atoms survive a change of
snapshot.

Derivation does not use negation-as-failure over derived atoms. Conditions may still use
data-level negation and comparison over the fixed environment.

### Derivation vs Resolution

| Property | Out (Derivation) | Eval (Full) |
|----------|------------------|-------------|
| Monotone in selected policy set `S` (fixed `Env`) | Yes | No |
| Monotone in environment `Env` | No (conditions may be anti-monotone) | No |
| Deterministic | Yes | Yes |
| Conflict-handling | None (contradiction is data) | Strategy-based |
| Output | Set of atoms (dedup by canonical identity) | Single decision |

The `Eval` function composes snapshot validation, declarative status derivation, `Out`, and
access-conflict resolution. Status derivation precedes `Out` because Privilege prerequisites read
Duty status; it remains a pure interpretation of the same immutable inputs:

```
Eval(U, R, W, C) =
    let errors = validateConfiguration(U, C) ∪ validateSnapshot(W, C)
    in if errors ≠ ∅ then
        EvaluationResult(Indeterminate, ∅, ∅, ∅, errors)
    else
        let dutyStatuses = deriveDutyStatuses(U, W, C)     -- pure, memoizable support
        let promiseStatuses = derivePromiseStatuses(U, W, C)
        let Env = mkEnv(U, R, W, C)
        let envelope = Out(U, Env)
        let decision = resolveDecision(envelope, C.strategy)
        in EvaluationResult(decision,
                            envelope,
                            dutyStatuses,
                            promiseStatuses,
                            diagnosticsOf(envelope, dutyStatuses, promiseStatuses))
```

`deriveDutyStatuses` is total over every independent or attached Duty reachable from the policy
universe and returns an immutable map. This makes every prerequisite result defined even when
the Duty does not itself produce an envelope atom:

```text
deriveDutyStatuses(U, W, C) =
    { d ↦ dutyStatus(d,U,W,C) | P ∈ U, d ∈ allDuties(P) }

derivePromiseStatuses(U, W, C) =
    { p ↦ promiseStatus(p,U,W,C) | p is a Promise clause in U }
```

Input errors short-circuit policy derivation because no condition may read an invalid semantic
input.

```text
diagnosticsOf(envelope, dutyStatuses, promiseStatuses) =
    ⋃ { causes | indeterminate(_, _, causes) ∈ envelope }
    ∪ statusDiagnostics(dutyStatuses)
    ∪ statusDiagnostics(promiseStatuses)
```

`statusDiagnostics` is defined by the declarative status algebra above.

The **normative envelope** `Out(U, Env)` is the first-class intermediate result: it is visible
before resolution and retains policy and clause attribution for audit.

Resolution may eliminate norms via priority or strategy, breaking monotonicity. This is by design:
`permit(a,x,s) ∧ forbid(a,x,s)` is an explicit conflict, not an inconsistency in the derivation.
`resolveDecision` applies norm priorities and the configured strategy. It never applies an
unstated specificity heuristic.

For architectural context, see `../docs/RL2_Architecture.md` §3.

---

## Conflict Resolution

`resolveDecision(envelope, strategy)` retains each complete
access-norm `indeterminate(norm,policy,causes)` atom. It computes the finite set of resolver
summaries reachable when each Unknown access candidate is independently inactive or active, then
maps those summaries through the same priority/strategy decision function. Duty
`indeterminate` atoms remain in the envelope and diagnostics but do not enter access resolution.
A single reachable decision is conclusive; more than one yields `Indeterminate`. The summary
space is polynomial and does not enumerate the `2^|I|` truth assignments. Mapping
`Indeterminate → Deny` is an **enforcement-adapter** decision (a fail-closed PEP), **not** the
semantic verdict: `Eval` returns `Indeterminate` so the ambiguity is auditable.

When multiple access norms apply, RL2 uses two explicit mechanisms:

1. **Access-norm priority** (`rl2:priority`): Privileges and Prohibitions may declare an integer
   priority; higher access candidates override lower access candidates before strategy is applied.
   Duty priority is irrelevant to access resolution. A prerequisite is either satisfied or it
   prevents its owning Privilege from becoming a candidate.

2. **Evaluator-level strategy**: The evaluator is configured with a conflict resolution strategy (e.g., prohibit-overrides, permit-overrides). This is **evaluator configuration**, not policy vocabulary—analogous to XACML combining algorithms.

The `strategy` parameter is evaluator configuration. Policies express norms and priorities;
the strategy combines opposite effects at the same maximal priority. The three strategies are
`ProhibitOverrides`, `PermitOverrides`, and `Invalid`, corresponding to ODRL's `prohibit`, `perm`,
and `invalid` values.

`resolveDecision(envelope, strategy)` retains attributed Unknown Privilege and Prohibition atoms
and projects definite and possible
activations into the compact `ResolverSummary` consumed by `decisionOf`. Duty atoms are not
access candidates.

```
resolveDecision(envelope, strategy) =
    let known    = { a ∈ envelope | kind(a) ∈ {permit, forbid} }
    let unknowns = { indeterminate(n,P,E) ∈ envelope |
                     n : Privilege ∨ n : Prohibition }
    let initial  = summarizeChoices(known)
    let summaries = choiceFold(canonicalOrder(unknowns), initial)
    let decisions = { decisionOf(s, strategy) | s ∈ summaries }
    in if |decisions| = 1 then the element of decisions else Indeterminate

activate(indeterminate(n : Privilege,   P, _)) = permit(n, P)
activate(indeterminate(n : Prohibition, P, _)) = forbid(n, P)

priority(n) = n.priority if declared, otherwise 0

ResolverSummary =
    { topPriority    : Integer?,
      hasPrivilege  : Boolean,
      hasProhibition : Boolean }

emptySummary = { None, false, false }
summarizeChoices(atoms) =
    fold(extendSummaries, {emptySummary}, canonicalOrder(atoms))

extendSummaries(summaries, atom) =
    { addAtom(s, atom) | s ∈ summaries }

canonicalOrder(atoms) = sort atoms by (sourcePolicyId, sourceClauseId, atomKind)
addAtom(s, permit(n, P)) =
    addAccess(s, Privilege, priority(n))
addAtom(s, forbid(n, P)) =
    addAccess(s, Prohibition, priority(n))

addAccess(s, kind, p) =
    if s.topPriority = None ∨ p > s.topPriority then
        { topPriority: p,
          hasPrivilege: kind = Privilege,
          hasProhibition: kind = Prohibition }
    else if p < s.topPriority then s
    else if kind = Privilege then
        s[hasPrivilege ↦ true]
    else
        s[hasProhibition ↦ true]

choiceFold([], summaries) = summaries
choiceFold(i :: rest, summaries) =
    let active = { addAtom(s, activate(i)) | s ∈ summaries }
    let next = summaries ∪ active
    in choiceFold(rest, next)
    -- retaining s chooses condition Unknown=False; active chooses Unknown=True

baseDecision(s) =
    if ¬s.hasPrivilege then NotApplicable else Permit

decisionOf(s, strategy) =
    case strategy of
        ProhibitOverrides →
            if s.hasProhibition then Deny else baseDecision(s)

        PermitOverrides →
            if s.hasPrivilege then Permit
            else if s.hasProhibition then Deny
            else NotApplicable

        Invalid →  -- ODRL "invalid": a conflict in the maximal-priority stratum is surfaced
            if s.hasPrivilege ∧ s.hasProhibition then Indeterminate
            else if s.hasProhibition then Deny
            else baseDecision(s)
```

The cases are exhaustive over the validated `Strategy` datatype. An unknown strategy is an
`Invalid(ConfigurationSite(strategy))` input error and never reaches `decisionOf`.

`addAtom` uses only priority comparison and Boolean accumulation, so definite summarization is
order-independent. `choiceFold` is exact for all joint Unknown access activations but deduplicates
after every step by summary equality. For `n` access atoms there are at most `4(n+1)` summaries:
one of four effect pairs for each possible top priority. The construction is polynomial and does
not enumerate the powerset of Unknown clauses.

Normative boundary consequences include:

- Under `PermitOverrides`, a definite Privilege plus an equal-priority Unknown Prohibition is
  `Permit`: either activation choice permits.
- Under `PermitOverrides`, a definite Prohibition plus an equal-priority Unknown Privilege is
  `Indeterminate`: the choices yield Deny and Permit.
- Under `Invalid`, a lower-priority definite Prohibition and two Unknown equal-higher-priority
  access atoms (one Privilege, one Prohibition) are `Indeterminate`.
  Activating either Unknown alone still yields Deny, but activating both creates a top-stratum
  conflict; retaining joint reachable summaries is therefore necessary.

`Indeterminate` here is the same value produced per norm in the denotations above. A fail-closed
enforcement adapter may map it to `Deny`, but that mapping is not part of `resolveDecision`.

Note: `NotApplicable` (no matching rule) is distinct from `Deny` (explicit prohibition). This allows policy composition where a higher-level policy can provide defaults.

### Duty Status Derivation

`deriveDutyStatuses` computes an immutable result map; it does not apply transitions or return a
new snapshot. The Achievement and Maintenance status functions include status indeterminacy and
the evidence interval for each attached Duty.

### Duty Attachment Boundary

Core has two Duty relationships only:

- a Duty linked from one or more Privileges with `rl2:prerequisiteDuty` is blocking for each owner when applicable; and
- a Duty linked directly from a Policy with `rl2:clause` is independent.

Concurrent and post-use obligations are not additional core attachment modes. Their substantive
requirements can still be stated as Achievement or Maintenance Duties with applicability,
postconditions, invariants, and optional windows. Core `Eval` returns `Permit` plus the complete
Duty-status map; it does not schedule, enforce, or claim that an ongoing obligation was imposed by
the act of evaluation.

### Note on Evaluation Complexity

One `Eval` call is a bounded computation over finite policy, fact, and evidence sets. It neither
waits for evidence nor processes an event stream. Multi-step workflows may call `Eval` again with
a later snapshot, but scheduling, persistence, and trace semantics are future companion work.

---

## Constraint Algebra Semantics

Conditions form a compositional three-valued algebra. Time values use the same comparison
operators as other ordered values.

Properties:

* Associativity, commutativity, idempotence for And/Or
* De Morgan laws
* Temporal and contextual comparisons are orthogonal to logical structure
* Dynamic operands resolved at evaluation time
* Path-based evaluation is deterministic (fully resolved from Env)

This ensures determinism of constraint evaluation.

---

## Evidence Semantics

Evidence influences a result only through the Duty and Promise status functions. `Eval` does not
append, reorder, or transform evidence. Matching and temporal selection are defined in
`RL2_Model.md` §4.3.

---

## Policy Composition Semantics

Policy universes compose by set union:

```
U1 ⊔ U2 = U1 ∪ U2
```

Each policy retains its own applicability conditions, parties, profile declarations, and clause
provenance. The combined envelope is `Out(U1 ∪ U2, Env)`; `resolveDecision` then applies maximal
clause priority and the configured ODRL-compatible strategy to conflicting access atoms.

ODRL `inheritFrom` input is normalized by a translator before evaluation; native RL2 policy
composition is explicit clause union. The supported translation cases and diagnostics are defined
in `RL2_ODRL_Mapping.md`.

---

## Interoperability

RL2 is a canonical target for supported ODRL 2.2 input. Translation is a partial, deterministic
function:

```text
translate(ODRLPolicy, TranslationConfiguration)
    -> CanonicalRL2Policy | Rejected(diagnostics)
```

`RL2_ODRL_Mapping.md` defines the supported structures, required interpretation parameters,
preservation guarantees, and rejection diagnostics. Translation does not guess among materially
different meanings.

## Concurrency Boundary

`Eval` reads one immutable `WorldSnapshot`; it neither reserves resources nor commits an action.
A decision based on a shared quota or capacity fact is therefore a decision about that snapshot,
not an atomic admission guarantee. Systems that require check-and-reserve behavior must ensure
snapshot freshness and atomic enforcement outside RL2.

## Complexity and Constraints

*This section is non-normative.*

RL2 evaluation is designed to be **polynomial-time** and **total** under the following constraints.

### Conformance Parameters

The core's termination and polynomial-time guarantees depend on a small set of **conformance parameters** — named finite bounds a conforming implementation **MUST** enforce. Only the *values* are implementation- or profile-declared; the existence of each bound is mandatory, not a `MAY`. An implementation that omits any of these bounds is out of core conformance.

| Parameter | Default | Bounds |
|-----------|---------|--------|
| `MaxPathDepth` | 10 segments | `deref` path length |
| `MaxConditionDepth` | 20 | condition tree nesting; evaluation work is linear in tree size |
| `MaxCollectionSize` | implementation-declared | policy-declared sets and collections |
| `MaxSnapshotFacts` | implementation-declared | `|WorldSnapshot.facts|` |
| `MaxSnapshotEvidence` | implementation-declared | `|WorldSnapshot.evidence|` |
| `MaxPolicyUniverse` | implementation-declared | `|U|` |

### Structural Constraints

1. **Finite policy universe**: U is a finite set of policies (`≤ MaxPolicyUniverse`)
2. **Bounded condition nesting**: Conditions have bounded depth (`≤ MaxConditionDepth`, default 20)
3. **Acyclic conditions**: No self-referential condition definitions
4. **Finite snapshot**: facts and evidence satisfy their declared bounds
5. **No recursive policy references**: Policies cannot invoke evaluation of other policies

### Path Resolution Constraints

6. **Bounded path depth**: `≤ MaxPathDepth` (default 10), enforced by grammar
7. **No live traversal**: ordinary paths are exact fact-key lookups, not graph pattern matching
8. **No evaluator callback**: source access and derived-value computation occur before snapshot
   assembly
9. **Deterministic selection**: action evidence is selected by explicit clause-derived fields

### Complexity Analysis

Given these constraints:

| Operation | Complexity |
|-----------|------------|
| Canonical fact resolution | O(F) without an optional key index |
| Evidence selection | O(E × h), where h is bounded action-hierarchy lookup work |
| Condition evaluation | O(n × F) without an optional fact index |
| Norm matching | O(\|U\| × m) where m = max clauses per policy |
| Conflict resolution | O(k²) for `k` access atoms |
| **Total `Eval`** | **O(\|U\| × m × (nF + Eh) + k²)** |

`F`, `E`, and `h` are bounded by the snapshot and hierarchy conformance parameters. The bound
includes Duty and Promise status derivation. Indexes may reduce lookup cost without changing
meaning.

### Totality Guarantees

Under these constraints, `Eval` is **total**: it terminates for all well-formed inputs. The function never:

- Loops infinitely (no recursive evaluation)
- Blocks on external resources (`Eval` performs no I/O; missing snapshot values produce `EvalError`)
- Diverges due to condition structure (bounded, acyclic)

Source fetching, credential verification, and connector execution are outside `Eval`. A deployment
completes them while constructing `WorldSnapshot`; their cost and termination are not included in
the evaluator bound.

---

## Proof scope and normative artifact

RL2 specifies the language, ODRL migration, and conformance, not an implementation or mechanized
proof. The normative artifacts are the core ontology and shapes, `RL2_Model.md`, this document,
`RL2_ODRL_Mapping.md`, and accepted conformance vectors.

Datatype and function definitions in this document use Dafny-like algebraic-datatype notation
purely as precise pseudocode. This is not a commitment to Dafny or any implementation language.

---

## Proof Obligations

The following are requirements on RL2 semantics:

1. **Determinism:** equal PolicyUniverse, Request, WorldSnapshot, and EvaluationConfiguration
   values produce equal EvaluationResults.
2. **Condition totality:** every well-formed condition produces `True`, `False`, or attributed
   `Unknown`; it neither throws nor silently drops an error.
3. **Projection determinism:** supported RDF input maps to one canonical AST; unsupported or
   ambiguous input produces a specified diagnostic.
4. **Status consistency:** a Duty or Promise receives one status for one semantic input; terminal
   outcomes cannot be simultaneously Fulfilled and Violated.
5. **Resolution completeness:** every finite attributed envelope, total Duty-status map, and
   supported configuration produces one Decision.
6. **Bounded totality:** `Eval` terminates for every well-formed input satisfying declared
   conformance bounds.

The semantic conformance vectors test these observable properties. A future reference evaluator
may add differential tests or mechanized proofs without changing the language contract.

For architecture and boundaries, see `../docs/RL2_Architecture.md`.

---

## References

See `../docs/RL2_References.md` for complete citations.

Related RL2 specifications:
- `rl2.ttl` — Core ontology (OWL)
- `rl2-shacl.ttl` — SHACL validation shapes
- `RL2_Model.md` — Request, WorldSnapshot, configuration, and result
- `RL2_ODRL_Mapping.md` — ODRL 2.2 translation and compatibility
- `../conformance/` — Structural and semantic conformance artifacts
