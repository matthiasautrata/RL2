# RL2 External Data

**Version:** 0.7

## Status

This document is informative. The normative snapshot model is in `../spec/RL2_Model.md`.

## 1. Rule

Policy evaluation performs no external I/O:

```text
Eval(PolicyUniverse, Request, WorldSnapshot, EvaluationConfiguration)
    -> EvaluationResult
```

Every fact and item of evidence read by a policy is already present in the immutable
WorldSnapshot. Missing, invalid, and conflicting data is handled by the formal result algebra,
not by implementation-specific fallback behavior.

## 2. Snapshot Contents

The snapshot contains:

- `evaluationTime`, the instant used by temporal expressions;
- attributed facts, each with a canonical scoped key, typed value, and validity interval; and
- attributed evidence of an action, with its occurrence time, actor, action, and object.

Facts are scoped to the requesting agent, requested asset, evaluation context, state, or a global
namespace. Request identity fields are read directly from the Request. Performance evidence is
selected by explicit actor, action, object, interval, and profile criteria.

## 3. Profile-Declared Operands

A profile defines an operand's identity, value type (via `rl2:valueType`), cardinality, allowed
operators, and canonical `rl2:resolutionPath`. It may also require explicit issuer, source, profile
version, or freshness metadata.

A resolution path is a key in the semantic snapshot. It is not a host-language property path and
does not authorize a live lookup. Unknown operands and unsupported profile versions are errors.

For a single-valued fact key, equal eligible assertions agree and unequal values conflict. A
multi-valued operand uses one canonical set value. Profiles cannot replace these rules with an
implicit first, newest, or preferred-source choice.

### 3.1 Required Inputs Manifest

A compiled module (a `PolicyUniverse` plus the profiles it requires) may export a `RequiredInputs`
manifest: a finite, statically derivable list describing every fact key and evidence selector the
module can consult, so an assembler can prefetch before the first evaluation instead of discovering
dependencies one `Missing` at a time. This manifest is informative tooling support, not part of the
normative `Eval` signature — an assembler that omits it still works correctly via the re-evaluation
loop in §6, just with more round trips.

Each entry is derived from the compiled operand and clause declarations already present in the
module:

```text
RequiredInput = (
    key          : FactKey,                 -- scope + canonical path
    valueType    : ValueType,               -- declared via the operand's rl2:valueType
    cardinality  : SingleValued | SetValued,
    trust        : the Admissibility record's allowedSources/maxAge entry for this path, if any
)

RequiredEvidence = (
    selector     : EvidenceSelector shape (actor/action-set/object/interval as declared by the clause),
    trust        : the Admissibility record's evidenceSigners entry for this scope, if any
)

RequiredInputs = (
    facts    : finite set of RequiredInput,
    evidence : finite set of RequiredEvidence
)
```

`RequiredInputs` is finite because a `PolicyUniverse` is finite and every operand's resolution path
and every Duty/Promise evidence selector is fixed at compile time — no policy in RL2 constructs a
fact key or selector dynamically at evaluation time. The manifest is therefore exact for what a
given module *can* read; it is not a prediction of what a particular Request or snapshot state will
actually cause it to read (conditional branches mean not every listed key is consulted on every
evaluation).

## 4. Assembly Boundary

A deployment may assemble a snapshot using request attributes, database reads, verified
credentials, signed assertions, APIs, caches, or event stores. Credentials, connection failures,
timeouts, retries, and trust discovery are resolved before evaluation.

The assembler is responsible for producing a coherent snapshot. Snapshot validation rejects
invalid intervals and reuse of one identifier for unequal normalized records. Evidence after the
evaluation time is ineligible. Storage order and arrival order have no semantic effect.

## 5. Provenance and Trust

Trust verification is pre-`Eval`. Signature checking, provenance-chain validation, trust-anchor
evaluation, and connector authentication all happen in the trusted assembler, before a
`WorldSnapshot` exists; the snapshot it produces contains only already-admitted facts and
evidence, each carrying its attribution (`source`, `observedAt`, `issuer`) as an ordinary immutable
field. `Eval` never performs cryptographic or chain-of-trust verification of its own — the
evaluator consumes the assembler's attributed result and checks only the finite, declarative
`Admissibility` record (`RL2_Model.md` §4.4: `allowedSources` and `maxAge` per left-operand
resolution path, `evidenceSigners` per Duty-evidence scope) that `EvaluationConfiguration` supplies.
That record — not an open predicate language, and not a place for connector logic — is the only
trust mechanism `Eval` itself applies; an item outside it is filtered exactly as if absent, never
arbitrated.

`RL2_Model.md` §4.4 states the threat model this rests on: `WorldSnapshot` is the output of a
single trusted assembler, and mixed-trust filtering across sources happens there, before `Eval`
ever sees the snapshot — `Eval` checks attribution, it does not arbitrate trust.

**Freshness.** `Attribution.observedAt` (`RL2_Model.md` §4) records when the assembler obtained or
computed the fact's value, distinct from `validDuring`, which bounds when the value is asserted to
apply. `validDuring` expresses expiry ("this value is only asserted through time T"); it cannot
express "this value must have been observed within the last 5 minutes, regardless of what it
asserts." A profile that needs the latter declares a `context.*` or `global.*` operand whose
resolution path resolves to the relevant fact's `observedAt` (e.g. an operand with
`rl2:resolutionPath "global.quota.observedAt"`, paired with the fact operand it qualifies), and
states a `currentDateTime`-relative freshness condition over it using the ordinary constraint
machinery — the same way any other derived value is checked. RL2 Core does not add a distinct
"freshness" operator; `observedAt` is exposed as an ordinary resolvable `DateTime` value, checked
with `lte`/`gte` like any other.

## 6. Replayable universe selection (informative)

Some deployments do not bake every possible policy into one static `PolicyUniverse`. Instead a
trusted assembler chooses, per request, which `CompiledPolicyModule`s belong in the universe that
particular request is evaluated against — for example selecting by asset or port tag rather than by
authoring-time enumeration. `Eval` itself is unaffected: it still takes one fixed `PolicyUniverse`
(`RL2_Model.md` §3, `RL2_Semantics.md`) and has no notion of "selection." Making the selection step
itself replayable is therefore an assembly-side concern, informative here, not a change to `Eval`'s
signature.

A `SelectedPolicyUniverse` manifest records that assembler-side decision as a plain, replayable
record:

- **selected policy digests** — the `CompiledPolicyModule` digests (`RL2_Compilation.md` §5.1) that
  the assembler assembled into the `PolicyUniverse` for this evaluation;
- **selector identity and version** — which selection logic, and which version of it, made the
  choice;
- **selection inputs** — the inputs that drove the selection itself (e.g. the asset/port tags or
  request attributes consulted to choose modules), distinct from the `WorldSnapshot` facts `Eval`
  later consults;
- **selection time** — when the selection was made, distinct from the snapshot's `evaluationTime`.

An `EvaluationResult`'s interchange schema already carries the digest of the one compiled module it
ran against, alongside `evaluationTime` and the applied `EvaluationConfiguration`
(`RL2_Compilation.md` §7), so a result is independently re-derivable — it tells you *what* was
decided. The `SelectedPolicyUniverse` manifest is a distinct, complementary record: it tells you
*why these policies* were in the universe evaluated, i.e. how the assembler arrived at that set of
digests in the first place. An `EvaluationResult` MAY carry the manifest's digest as optional
interchange metadata alongside its existing replay-anchoring fields.

This section is informative only: `SelectedPolicyUniverse` has no SHACL shape and does not change
`Eval`'s signature or `EvaluationResult`'s normative fields. It becomes normative when the assembly
contract (`assemble()`, `backlog.md` §6) does.

## 7. Re-evaluation

An application may request missing inputs, refresh a snapshot, and evaluate again. Each call is a
separate evaluation over one immutable input. RL2 does not standardize subscription, polling,
retry, or event-delivery protocols. The following loop is the precise shape that re-evaluation
takes when driven by the causal errors `Eval` already produces:

1. **Evaluate.** Call `Eval` with the current (possibly partial) `WorldSnapshot`.
2. **Collect Missing keys.** Scan `EvaluationResult.diagnostics` (and any `Missing` causes carried
   inside `dutyStatuses`/`promiseStatuses` as `IndeterminateStatus` causes) for `Missing(ErrorKey)`
   values whose `site` is a `SnapshotSite(path)` or an `EvidenceSelector`. Collect the distinct set
   of `path`s and selectors — this set is exactly the input that, if supplied, could change the
   result; `Invalid` and `Conflict` causes are not re-fetch targets, since they mean admissible data
   was found and rejected or found in disagreement, not that data is absent.
3. **Fetch exactly those keys.** Query the underlying sources for the collected paths and evidence
   selectors only — not the full `RequiredInputs` manifest, which may be far larger than what this
   particular Request and prior snapshot actually left unresolved.
4. **Assemble a new snapshot.** Merge the fetched facts/evidence into a new immutable `WorldSnapshot`
   (assembly, including any mixed-trust filtering, per §4 and `RL2_Model.md` §4.4); this is a new
   value, not a mutation of the one just evaluated.
5. **Re-evaluate.** Call `Eval` again with the new snapshot. Go to step 2.

**Termination.** The loop terminates because the dependency set a module can ever ask about is
finite (§3.1's `RequiredInputs` bounds it) and each iteration either (a) resolves at least one
previously-`Missing` key, shrinking the `Missing` set for any key whose source produced an
answer, admissible or not — an admissible answer removes the `Missing` cause, an `Invalid` or
`Conflict` answer replaces it with a non-`Missing` cause that is not re-fetched, so it is also
removed from the set the loop collects in step 2 — or (b) leaves the `Missing` set unchanged,
which means the source has no further answer to give and the caller should stop rather than loop
forever on an unfulfillable dependency. Since the set collected in step 2 is a subset of the finite
`RequiredInputs` facts/evidence and is non-increasing, and case (a) strictly decreases it while case
(b) is a caller-visible fixed point, the loop reaches a fixed point in at most `|RequiredInputs|`
iterations that make progress.

Conformance vectors supply snapshots directly, making resolution behavior replayable without
requiring any particular external system.
