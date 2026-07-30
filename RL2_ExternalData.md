---
title: "RL2 External Data Integration"
subtitle: "Source Binding, Interaction Modes, and the Pure-Evaluator Boundary"
version: "0.1"
status: "Draft"
date: 2026-07-29
---

# RL2 External Data Integration

This document specifies how RL2 policies obtain data they do not carry themselves — HR
directories, asset catalogs, identity providers, and other systems referenced (implicitly or
explicitly) via `rl2:resolutionFunction` and `lookupExternal`. It closes **SEM-13**: those two
mechanisms were declared in `RL2_Semantics.md` (§Helper Function Specifications) and
`RL2_Architecture.md` (§Runtime Functions, `resolve`) but never given a binding — no standard
way for a policy to declare what it needs, for an evaluator to satisfy that need, or for either
side to be tested. This is also the highest-risk area for the totality guarantee: the
extension warning at `RL2_Semantics.md` §Path Resolution Constraints already flags unbounded
external queries as a threat to polynomial-time/termination, and this document is what makes
that warning actionable rather than just cautionary.

**Scope.** This document defines the `Source`/`SourceBinding` types, the normative
out-of-band baseline, the hybrid/in-band extension and the constraints it must obey, and the
testing story (mock sources). It does not redefine `ContextManifest`, `resolve`, or `Env` —
those are `RL2_Architecture.md` and `RL2_IR.md` artifacts; this document specifies what fills
the gap *inside* them: how an `OperandSpec` becomes an actual value.

---

## 1. Where This Fits

Recall the pipeline (`RL2_Architecture.md` §Runtime Functions, `RL2_IR.md` §6):

```
compile(U)  →  CompiledUniverse, ContextManifest
                    │
lookup(CompiledUniverse.targetIndex, target)  →  ClauseRef*
                    │
manifest(ContextManifest, ClauseRef*)  →  OperandSpec*      -- WHAT is needed
                    │
resolve(OperandSpec*, Request, Sources)  →  (Context, Missing*)   -- HOW it is obtained (this document)
                    │
Env = mkEnv(Request, Σ, Context)
                    │
evalIR(CompiledUniverse, Request, Σ, Ctx, strategy)   -- reads Env, never calls out (RL2_IR.md §6)
```

`resolve` is the seam this document fills. Everything to its left (`lookup`, `manifest`) and
below (`evalIR`) is already specified. `resolve`'s *contract* — best-effort, transparent,
idempotent — was already stated in `RL2_Architecture.md`; what was missing is what `Sources`
*is* and what an evaluator is and is not allowed to do while implementing it.

**The pure evaluator never calls out.** `RL2_IR.md` §6 establishes that condition evaluation
reads a fully populated `Env` and never blocks on I/O. External interaction — whatever form it
takes — happens entirely in `resolve`, *before* `Env` is constructed and `evalIR` begins.
This document specifies that resolution boundary; it does not extend the guarantees of
`evalIR` to external systems.

---

## 2. Normative Baseline: Out-of-Band Resolution

**For the specified evaluator core, out-of-band is the only normative interaction mode.** The requester
supplies every operand value the applicable policies require, as `rl2p:ContextAssertion`s
(`RL2_Protocol.md` §Context), before `resolve` runs. `resolve`'s job in this mode is not to
*fetch* anything — it is to **project** the supplied assertions onto the required
`OperandSpec*`:

```
resolveOutOfBand : (OperandSpec*, ContextAssertion*) → (Context, Missing*)

resolveOutOfBand(specs, assertions) =
    let found   = { (spec, v) | spec ∈ specs, a ∈ assertions,
                                 a.contextSubject/contextProperty matches spec,
                                 v = a.contextValue | a.contextValueRef }
    let missing = { spec | spec ∈ specs, spec.required = true, spec ∉ dom(found) }
    in (Context(found), missing)
```

This is a **pure, total, O(|specs| · |assertions|) function** — no network calls, no timeouts,
no partial failure beyond "not supplied." It is what makes `Manifest Sufficiency`
(`RL2_Architecture.md` §Composition Invariants: "if all required operands are provided,
evaluation does not return `Indeterminate` due to missing context") a property the evaluator
can actually guarantee, rather than an aspiration undermined by live external calls that can
fail independently of what the requester supplied.

**This is what `RL2_Architecture.md`'s `Iterative` interaction mode is for.** If `resolve`
reports non-empty `Missing*`, the evaluator returns `NeedContext(Missing*)`; the requester
supplies the missing assertions (querying whatever source it needs to, on its own time, outside
the evaluation) and resubmits. The evaluator itself never becomes a client of HR systems,
directories, or asset catalogs in this mode — it only ever reads what it was given.

**Why this is the baseline, not an option among equals.** The totality, determinism, and
structural bounds specified for `evalIR` assume that resolution completes before evaluation
begins. Out-of-band resolution satisfies that assumption by construction. XACML's PIP
(Policy Information Point) pattern — the evaluator calling out
mid-decision — is the cautionary counter-example: it makes decision latency and availability
depend on arbitrary external systems, and a PIP outage becomes a silent authorization failure
mode. RL2's evaluator is designed specifically to avoid that failure mode; out-of-band resolution
is what preserves it up to the evaluator boundary.

---

## 3. Source Binding (the gap this document closes)

`RL2_Architecture.md`'s `resolve : (OperandSpec*, Request, Sources) → (Context, Missing*)`
already names `Sources` as an input but leaves its shape unspecified. This is the actual
SEM-13 gap: `rl2:resolutionFunction "lookupDepartment"` is a **name**, declared in the policy
graph — nothing in the graph says what system answers to that name, how to reach it, or under
what bounds. That binding is deliberately **not** part of the policy graph (a policy must not
encode "call this specific HTTP endpoint" — that is deployment configuration, not normative
content, exactly the same separation `RL2_Semantics.md` and `RL2_Architecture.md` already draw
between conflict-resolution *strategy* — semantics vocabulary — and *choice* — evaluator
configuration).

```
SourceBinding = SourceBinding(
  function      : string,        -- matches rl2:resolutionFunction's declared name
  source        : SourceId,      -- e.g. "HR_API", "AssetCatalog" — opaque evaluator-local id
  complexity    : Complexity,    -- O1 | OLogN   (RL2_Semantics.md §Path Resolution Constraints, item 8)
  timeoutMillis : nat,
  onFailure     : FailurePolicy  -- ToBottom | ToMissing  (see §4)
)

SourceRegistry = map<string, SourceBinding>    -- resolutionFunction name → binding; evaluator-local state,
                                                -- NOT part of the policy graph — mirrors the
                                                -- supported-profile registry (RL2_Semantics.md §Profile
                                                -- Resolution O3), which is evaluator state for the same reason
```

A `SourceRegistry` entry is what `invokeFunction(op.resolutionFunction, Env)`
(`RL2_Semantics.md` §Helper Function Specifications) resolves to at the evaluator layer: given
`op.resolutionFunction = "lookupDepartment"`, the evaluator looks up `"lookupDepartment"` in its
`SourceRegistry`, and the resulting `SourceBinding` says which system to call, under what
complexity/timeout bound, and what to do on failure. An unregistered `resolutionFunction` name
is a load-time rejection (**fail-closed**, mirroring the unknown-profile rule in
`RL2_Semantics.md` §Profile Resolution O3) — not a runtime `⊥`, so a missing binding is caught
before any request is evaluated, not discovered mid-decision.

**Profile-defined source schemas.** A profile that declares `resolutionFunction` operands
(e.g. `department → rl2:resolutionFunction "lookupDepartment"`, `RL2_Semantics.md` §Helper
Function Specifications) SHOULD ship a companion `SourceBinding` table as **deployment
documentation**, not as RDF: the profile's normative content is the operand's existence, type,
and range (SHACL-checkable); the binding — which concrete system answers it — is inherently
per-deployment and does not belong in a shared, versioned vocabulary. A profile document
lists the expected shape (name, arity, expected `Complexity`) so deployments can register a
conforming binding.

---

## 4. Hybrid/In-Band Extension (non-normative, opt-in)

**In-band resolution — the evaluator calling a `SourceBinding`'s system live during
`resolve` — is an explicitly non-core extension**, never a substitute for out-of-band
resolution and never something a policy can require. It exists for deployments that accept the
trade-off for convenience (no `NeedContext` round trip) and are willing to give up the evaluator's
totality guarantee over that portion of `resolve`.

**Constraints (mandatory wherever in-band is used at all):**

- **Declared, not implicit.** Only `OperandSpec`s whose `resolutionFunction` has a registered
  `SourceBinding` with a live source may resolve in-band; everything else stays out-of-band.
  `ContextManifest`'s `required : true/false` (`RL2_Architecture.md` §ContextManifest) governs
  what a missing in-band result does: `required = true` and resolution fails →
  `Indeterminate` (never a silent `Deny` or `Permit`); `required = false` → the operand is
  simply absent from `Context`, same as an unsupplied out-of-band assertion.
- **Bounded complexity.** `O(1)` or `O(log n)` per invocation, no iteration over external
  graphs, no unbounded joins — the same bound `RL2_Semantics.md` §Path Resolution Constraints
  already states for `resolutionFunction` in general, now attached to each binding explicitly
  via `SourceBinding.complexity` rather than left as a general admonition.
- **Timeout + fail-to-⊥, not fail-to-block.** `SourceBinding.timeoutMillis` bounds every call;
  a timeout, error, or malformed response is a **resolution failure**, handled per
  `onFailure`:
  - `ToBottom` — the operand resolves to `⊥` (Unknown), which S2's Kleene algebra then
    propagates normally (a condition depending on it becomes `Unknown`, not silently `False`).
  - `ToMissing` — the operand is reported in `Missing*`, identical to an out-of-band gap; if
    `required = true`, this surfaces as `NeedContext`/`Indeterminate` exactly as in §2, letting
    the requester supply the value out-of-band instead of retrying the live call.

  Either policy keeps `resolve` **total**: it always returns, never blocks indefinitely on an
  unresponsive source. `ToMissing` is the recommended default — it degrades to the out-of-band
  path uniformly, so a deployment can disable in-band resolution entirely (empty
  `SourceRegistry` of live bindings) without changing any policy's observable behavior, only
  its latency.
- **Snapshot-consistency is unaffected.** All in-band calls happen during `resolve`, before
  `Env` exists and before `evalIR` starts (§1). `RL2_IR.md` §6's snapshot-consistency invariant
  ("every read in a single evaluation observes Σ as of entry") is about `Σ`, not about
  `Sources`; a `SourceBinding` call and `Env` construction are the same "context materialization"
  step (`RL2_Architecture.md` §Evaluation Pipeline, ① Context Materialization) — nothing reads
  a live source *during* the pure evaluator's run.

**What in-band resolution does not get:** the evaluator equivalence obligation
(`RL2_IR.md` §9) covers `evalIR`, not `resolve`. An in-band `SourceBinding` is, like
`resolutionFunction`/`lookupExternal` generally, **outside the specified evaluator core**
(`RL2_Semantics.md` §Path Resolution Constraints, S8a) — using it is a deployment choice that
must be documented, not a claim that the deployment inherits the same guarantees as
path-based, out-of-band resolution.

---

## 5. Testing: Mock Sources

A `SourceRegistry` entry's `source : SourceId` is intentionally opaque to the evaluator core —
this is what makes substitution for testing mechanical rather than invasive. A **mock
registry** binds the same `resolutionFunction` names to fixed, deterministic responses instead
of live systems:

```
MockSource = MockSource(function: string, canned: map<Request, Value>)
```

This supplies deterministic fixtures for a future implementation. No RL2 compiler or
differential test suite currently exists. A policy that uses `resolutionFunction`
operands should be tested against a `MockSource` registry that pins expected
inputs/outputs, so a test run never depends on a live external system's availability or
current data. A `MockSource` is also how `required: true` operand handling (both the
`ToBottom` and `ToMissing` failure paths, §4) gets exercised deterministically — a mock can be
configured to "fail" (timeout or return malformed data) on command, which a live source cannot
reliably do on a schedule a test suite controls.

**Recommendation:** every profile that declares `resolutionFunction` operands SHOULD ship a
`MockSource` fixture set alongside its `SourceBinding` documentation (§3), so a consuming
deployment's test suite has a ready-made substitute before it wires up the real system.

---

## 6. Interaction Modes, Reconciled

`RL2_Architecture.md` §Interaction Modes lists `Single-shot`, `Iterative`, and `Pre-flight` as
TBD-normative-status. This document resolves that:

| Mode | Status | Relies on |
|------|--------|-----------|
| **Single-shot** (all context supplied upfront) | **Normative baseline**, always available | §2 out-of-band `resolve` |
| **Iterative** (`NeedContext` round trip) | **Normative**, always available | §2 out-of-band `resolve`; the requester's own follow-up query to whatever source it needs is out of RL2's scope |
| **Pre-flight** (`manifest` called before a full request) | **Normative**, always available | `manifest` alone (`RL2_Architecture.md` §manifest) — does not touch `resolve`/`Sources` at all |
| **Hybrid/in-band** (evaluator calls a live `SourceBinding`) | **Optional extension**, opt-in per deployment | §4; never required, never assumed by policy authors |

Single-shot, Iterative, and Pre-flight are all realizable purely through out-of-band
resolution and were never actually blocked on `Sources`/`SourceBinding` being defined — only
Hybrid was. That is why this document scopes the open design question narrowly to Hybrid
rather than reopening all four modes.

---

## 7. Handoffs

- **Specification surface.** `resolveOutOfBand` (§2) is small and total enough to be specified
  alongside `evalIR` with the same precision, unlike in-band resolution, which stays outside
  that surface by design (§4). Implementation is out of scope for this project (SCOPE-1,
  `issues.md`).
- **Profile authors.** Any profile declaring `resolutionFunction` operands should publish a
  `SourceBinding` shape table (§3) and a `MockSource` fixture set (§5) as part of the profile's
  deployment documentation — not inside `rl2.ttl`/profile ontology files, which stay
  binding-free per the separation stated in §3.
- **RL2_Architecture.md.** §Interaction Modes' "TBD: Specify which modes are normative vs
  optional" is resolved by §6 above; that TBD line should be updated to point here.
- **RL2_Semantics.md.** §Path Resolution Constraints' S8a extension warning is unchanged in
  substance; this document is the promised elaboration of "such extensions MUST document their
  determinism and complexity characteristics" (§3's `SourceBinding.complexity`/`timeoutMillis`/
  `onFailure` are exactly that documentation, formalized).

---

## References

- **RL2_Architecture.md** — `resolve`, `ContextManifest`, `Sources`, Composition Invariants,
  Interaction Modes.
- **RL2_Semantics.md** — §Helper Function Specifications (`resolve`, `resolutionFunction`,
  `lookupExternal`), §Path Resolution Constraints (S8a extension warning), §Profile Resolution
  (O3 — the analogous evaluator-local registry pattern this document reuses for
  `SourceRegistry`).
- **RL2_IR.md** — §6 Eval-time Interaction (pure context resolution and
  snapshot-consistency), §10 Compiler Trust Model (the future conformance-testing strategy
  followed by this document's §5).
- **RL2_Protocol.md** — §Context (`rl2p:ContextAssertion`, the out-of-band supply mechanism).
