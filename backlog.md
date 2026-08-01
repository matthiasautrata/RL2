# RL2 Backlog

Successor to the 2026-08-01 review/decision record (`fix-fable.md`, now deleted). Every design
decision from that cycle is executed in the normative artifacts and traceable through the commit
history `0ca83bd..6165f47`; this file carries only **remaining work** and **standing records**.
Working discipline: discuss → decide → sub-agent executes a closed task spec → coordinator checks
diffs → commit. Gate: `uv run tools/validate.py` stays `FAIL 0` and warning-free.

## 1. Executable conformance (highest priority — everything else's acceptance criterion)

- Machine-readable vector format per `spec/RL2_Compilation.md` §7 interchange schemas:
  `(module | universe, Request, WorldSnapshot, EvaluationConfiguration)` → expected
  `(decision, determining SourceRefs, Duty/Promise statuses, causes, diagnostics)`.
- Publish the four JSON Schema files (Request, WorldSnapshot, EvaluationConfiguration,
  EvaluationResult) — field tables are normative in `RL2_Compilation.md` §7; the schema files
  ship here.
- Convert the four `conformance/vectors/*.md` files and ~15 highest-value use cases to vectors.
- Negative compiler vectors: at least one per diagnostic code in `RL2_Compilation.md` §6.1.
- Missing positive vectors identified during review: complementary Privilege/Prohibition pair
  under a missing operand; inapplicable prerequisite Duty (vacuous pass vs status-condition
  `False`); `permit + indeterminate` resolution under each strategy; the four exception-pattern
  forms; profile version negotiation and digest mismatch; relative-window resolution incl.
  missing anchor; sentinel-population norm with missing population fact.
- F-01 vectors (sentinel Duty binding, `rl2:consequentDuty`): positive — a Privilege's
  `consequentDuty` fires on grant and the envelope carries the *bound* obligate atom
  (`bind(d, requestAgent, requestAsset)`), never the sentinel-bearing template; bound
  prerequisite-gating positive and negative — a sentinel-carrying `prerequisiteDuty` template is
  gated via `dutyStatus(bind(d, requestAgent, requestAsset))`, both fulfilled and unmet; a
  consequent Duty with an `Unknown` condition of its own — confirms the decision outcome is
  unaffected by a consequent Duty's condition value (only the Privilege's own `accessResult.truth
  = True` gates firing); `UnboundStatusTarget` negative compile vector — an
  `rl2:obligationStateOperand` targeting a Duty whose `rl2:subject`/`rl2:object` is a sentinel.
- Translation runner comparing normalized ODRL fixtures to expected modules.
- Reference harness (`tools/evaluate.py` or similar); two independent evaluators before any
  interoperability claim.
- `tools/validate.py` hardening: remove the `...`-means-placeholder fence skip; make the
  injected prefix `PREAMBLE` opt-in (or add a strict second parse pass); parse the SHACL report
  graph rather than counting rendered severity strings; validate the shapes graph itself.

## 2. ODRL migration profile ("ODRL ±" execution)

- Author the migration-profile document: the supported ODRL 2.2 fragment, term-by-term
  compatibility matrix, each row carrying its three-test verdict (demand / determinism /
  runtime-independence) and a fixture.
- Consequence mapping rule: `odrl:remedy`/`consequence` → Duty with applicability condition
  `obligationStateOperand(targetNorm) = Violated` (profile-dependent disposition; the machinery
  already exists in core).
- New migration fixtures: `odrl:xone`; `odrl:inheritFrom` (multiple parents, missing parent,
  cycle); `ConflictingCompactValue`.
- Reclassifications: ODRL `invalid` conflict → `clarified` (whole-policy void vs request-scoped
  Indeterminate); Set-rule assigner preservation caveat; `rightOperandReference` → pre-resolve
  into an attributed snapshot fact or reject.
- Refinement compile-down rule in the transpiler (component-scoped refinements → rule-level
  conditions; not an RL2 authoring form).
- Crosswalk to the W3C ODRL Formal Semantics draft (Behaviour ↔ `defaultDecision`; state
  taxonomy; report model) and to XACML combining algorithms — expand mapping §8/§11.

## 3. Shipped profiles (the ODRL + layer)

1. **Remedies/Contracts** — expression-only (decided): vocabulary + the §2 consequence shape;
   document the assembler's violation-evidence obligation in `RL2_ExternalData.md`.
   Violation-evidence *vocabulary* deferred until cross-party interop is live.
2. **Privacy/Consent** — align with pod/Solid practice (Esteves et al. as reference); rewrite
   4–6 data-governance use cases onto `spec/profiles/rl2-privacy-profile.ttl` (it currently has
   zero conformance coverage).
3. **AI Vocabulary** — adopt the W3C draft actions; align `no-ml-training.md` /
   `derived-data-restriction.md` action names.
4. **Commercial/Market-Data** — `Quantity(Numeric, Unit)` value type (same-unit comparison
   only, no conversion — decided); metering patterns via `request.parameters`; first
   `rl2:ProfileOperator` exercises.

## 4. Infrastructure

- w3id.org registration PR for `https://w3id.org/rl2#` (namespace already swapped in-repo).
- Regenerate/re-check `docs/RL2_Vocabulary.md` after each ontology change (standing sub-agent
  task-spec line: every batch touching `rl2.ttl` updates the Vocabulary doc).

## 5. Implementation track

- Go reference evaluator + ODRL importer (reconciled estimate: 6–10 person-months to a credible
  reference implementation with executable conformance).
- Lean 4 model of the kernel; differential random testing Go ↔ Lean (Cedar precedent,
  arXiv:2407.01688). Proof order: compile-soundness theorem (`RL2_Compilation.md` §8) →
  evaluator determinism/totality → verified RDF compiler last (largest trusted boundary).
  Mechanized proofs: +6–12 person-months, do not gate conformance.
- Benchmarks before any scale claim: policy count, clauses/policy, condition depth, hierarchy
  size, snapshot facts, evidence, conflicting atoms; compare OVAL/OPA/Cedar on the shared
  authorization subset.

## 6. Deferred, with reopen triggers

| Item | Trigger to reopen |
|---|---|
| Fact-vs-fact comparison (right operand is authored; dynamic-right needs widened RuntimeReference or stays assembler doctrine) | Commercial profile metering scenarios |
| Recurrence (bounded period+count, compile-time expansion to finite windows) | A real recurring-obligation contract |
| Maintenance boundary algorithm (lift the P8 fact/clock-only invariant restriction via recursive boundary collection) | An invariant genuinely needing status operands |
| Evidence-existence operand (event-triggered activation, Cimmino P4d) | Migration demand |
| `rl2:enforcementMode` metadata (regimentation vs sanction, eval-ignored) | PEP integration work |
| Policy containment / conflict detection tooling (SMT over the 3-valued condition language; authoring-time, no solver in Eval) | Negotiation or change-impact requirements |
| Assembly contract → normative | A deployment exercises `assemble()` |
| RDFC-1.0 source-RDF digests | Cross-party identity over raw RDF re-ingestion |
| Violation-evidence vocabulary for the Remedies profile | Cross-party remedy interop |

## 7. Do not relitigate

Settled during the 2026-08-01 review cycle (rationale in commit messages and the spec):

- `rl2:priority` never applied to Promises/Duties — its domain is Privilege ∪ Prohibition by
  design; crystallized Duties have nothing to inherit.
- Set/Offer/Agreement stay distinct classes; operativity is structural (Promise ∉ Norm), not a
  mutable status property. Promise ≠ Duty deontically: directive-in-force vs
  commissive-contingent-on-acceptance, binding different parties.
- Atomic vs Logical constraint classes stay separate (structural arity checking).
- `neq`/`isNoneOf` are authoring preference over `not(eq)`/`not(isAnyOf)`, **not** a projection
  rewrite: truth values agree, but causes differ (`ComparisonSite` embeds the operator).
- Independent-Duty `obligate` atoms are action-local (derive only for requests matching the
  Duty's own action); an unmet prerequisite yields `NotApplicable` (no atom), not implicit Deny.
- Never widen an `rdfs:range` (to `owl:unionOf` or otherwise); domains widen only via the
  in-file `owl:unionOf` precedent; structure sharing across classes goes through SHACL.
- Full Boolean canonicalization rejected (exponential; Salas 2026); the narrowed one-encoding-
  per-primitive-relation claim plus enumerated local rules is the standing position.
- The three-test rule (demand / determinism / runtime-independence) governs every future
  vocabulary question; `odrl:implies` stays rejected; `includedIn` stays core.
- F-01 (sentinel Duty subject/object with no instance binding): resolved via new
  `rl2:consequentDuty` (Privilege → Duty, non-gating, the post-use/companion counterpart to
  `rl2:prerequisiteDuty`) plus a universal `bind(d, a, o)` substitution applied at exactly four
  request-context sites — prerequisite gating, attached-duty reporting, `consequentDuty` emission,
  and independent-clause atom emission. Envelope atoms and `dutyStatus` queries are always
  concrete and sentinel-free;
  `dutyStatus` itself stays defined on concrete duties only (a bound occurrence recorded in an
  `EvaluationResult` is concrete and re-evaluable). Sentinels remain legal in Duty templates but
  are `SentinelMisuse` on a Promise (a Promise crystallizes at materialization with no binding
  source). ODRL `odrl:duty` from a Permission is `clarified`, not `normalized`: a
  `TranslationConfiguration` must declare per profile/policy whether it means
  `prerequisiteDuty` or `consequentDuty`; an undeclared interpretation is
  `MissingTranslationInterpretation`.
