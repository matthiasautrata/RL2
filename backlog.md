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
  (`occurrenceOf(d, Env)`), never the sentinel-bearing template; bound
  prerequisite-gating positive and negative — a sentinel-carrying `prerequisiteDuty` template is
  gated via `dutyStatus(bind(d, requestAgent, requestAsset))`, both fulfilled and unmet; a
  consequent Duty with an `Unknown` condition of its own — confirms the decision outcome is
  unaffected by a consequent Duty's condition value (only the Privilege's own `accessResult.truth
  = True` gates firing); `UnboundStatusTarget` negative compile vector — an
  `rl2:obligationStateOperand` targeting a Duty whose `rl2:subject`/`rl2:object` is a sentinel.
- R-01/R-02/R-03 vectors (status-map and occurrence model, `spec/RL2_Semantics.md` §Duty Template
  Binding and Eval composition): a template Duty (prerequisite, consequent, or independent) reached
  via the widened `allDuties(P)` receives **no** entry in `dutyStatuses` under its own identity —
  only `concrete(d)` Duties do; a bound occurrence produced by `occurrenceOf` at a consequent-duty
  or independent-clause site contributes a `dutyStatuses` entry keyed by its `occurrenceId`,
  disjoint from the concrete-Duty key space (`boundOccurrenceStatuses`). TWO-IDENTICAL-READS — same
  agent, same asset, two distinct `Request.id` values against the same template, with Evidence
  carrying `dischargeOf` naming only the first occurrence's `occurrenceId` — the first occurrence is
  `Known(Fulfilled)` and the second stays `Known(Pending)`, confirming per-grant discharge does not
  leak across `Request.id` values. Per-member fallback — two grants of the same template to the same
  agent/asset with no `Request.id` on either request coalesce onto one `occurrenceId`, so evidence
  discharging the first grant also discharges the second. Consequent-duty trigger condition
  consumed — an `occurrenceOf`-produced occurrence carries `condition := None` (the Privilege's own
  `accessResult` already decided applicability at grant time), so a later `dutyStatus`
  re-evaluation of that recorded occurrence cannot re-decide firing eligibility, only fulfillment.
  Occurrence window resolved at grant time — an occurrence's `window` is `resolveWindow`'s output
  computed once against the granting evaluation's own snapshot, so a later evaluation supplying a
  different snapshot does not re-anchor a relative window to the new snapshot's clock.
- F-05 materialization vectors — action Promise with postCondition crystallizes into an
  Achievement Duty carrying it (positive); state Promise with postCondition rejected by
  `PromiseShape` (negative).
- Translation runner comparing normalized ODRL fixtures to expected modules.
- Reference harness (`tools/evaluate.py` or similar); two independent evaluators before any
  interoperability claim.
- `tools/validate.py` hardening: remove the `...`-means-placeholder fence skip; make the
  injected prefix `PREAMBLE` opt-in (or add a strict second parse pass); parse the SHACL report
  graph rather than counting rendered severity strings; validate the shapes graph itself.
- F-10 regime fixtures — imports ignored, named graphs ignored, relative-IRI rejection,
  warning-does-not-reject, canonical report-projection comparison across two SHACL engines.

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
| Assembly contract → normative | A deployment exercises `assemble()`, at which point the informative `SelectedPolicyUniverse` manifest (`docs/RL2_ExternalData.md` §6) also becomes normative |
| Port churn under a live agreement (product terms extending to later-created ports; amendment/lifecycle) | A deployed data product creates ports under an existing Agreement |
| RDFC-1.0 source-RDF digests | Cross-party identity over raw RDF re-ingestion |
| Violation-evidence vocabulary for the Remedies profile | Cross-party remedy interop |
| Declarative operator DSL with a normative interpreter (machine-checkable profile-operator semantics, replacing prose denotations) | A profile requires machine-verified operator semantics (e.g. the Lean-verified evaluator track) |
| Full per-operand data contract (value schema, cardinality, owner, provenance fields beyond `Attribution`, freshness semantics beyond `maxAge`, trust-policy digest, completeness scope) plus a normative, versioned `RequiredInputs` companion (F-13) | Cross-party snapshot exchange or a second independent assembler implementation |

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
  `rl2:prerequisiteDuty`). The regression review (`fix-codex.md` R-01..R-03) correctly called this
  cycle's original "resolved" claim premature: a single `bind(d, a, o)` substitution at all four
  request-context sites left template Duties reachable by `dutyStatus` unbound (R-01), gave a bound
  Duty no per-grant occurrence identity (R-02), and gave Duty conditions incompatible request/status
  evaluation scopes (R-03). The completed model instead splits the four sites into two mechanisms:
  **prerequisite gating** and **attached-duty reporting** keep unchanged, pure `bind(d, a, o)`
  substitution, with a `request.*` path in these request-free contexts yielding an attributed
  `Missing`; **`consequentDuty` emission** and **independent-clause atom emission** use
  `occurrenceOf(d, Env)` instead, which additionally consumes the Duty's `condition` (evaluated once,
  in the request environment), resolves `window` to `Absolute` or `None` via `resolveWindow` at grant
  time (never an unresolved `Relative` window — a `resolveWindow` failure yields an indeterminate
  atom, not a broken occurrence), and assigns an `occurrenceId` — `(sourceIdentity(d), Request.id)`
  when the request carries one (PER-GRANT), else `(sourceIdentity(d), agent, asset)` (PER-MEMBER
  fallback, coalescing repeated grants). `dutyStatuses` (`RL2_Model.md` §6) is restricted to
  `concrete(d)` Duties under their own identity — a template contributes no entry there — plus a
  lazily-computed entry per bound occurrence, keyed by `occurrenceId` (from `occurrenceOf`) or by
  `BoundIdentity` (from a bound prerequisite at gating); the two key spaces are disjoint by
  construction (`RL2_Semantics.md`'s `boundOccurrenceStatuses`). `Evidence.dischargeOf`
  (`RL2_Model.md` §4.3) correlates evidence to a specific PER-GRANT occurrence; PER-MEMBER
  occurrences and authored concrete Duties are unaffected. Envelope atoms and `dutyStatus` queries
  are always concrete and sentinel-free; a bound occurrence recorded in an `EvaluationResult` is
  concrete and re-evaluable, and re-identifiable by its recorded key. Sentinels remain legal in Duty
  templates but are `SentinelMisuse` on a Promise (a Promise crystallizes at materialization with no
  binding source). ODRL `odrl:duty` from a Permission is `clarified`, not `normalized`: a
  `TranslationConfiguration` must declare per profile/policy whether it means
  `prerequisiteDuty` or `consequentDuty`; an undeclared interpretation is
  `MissingTranslationInterpretation`.
- F-03 (plug-in `rl2:ProfileOperator` semantics unconstrained): operators stay (D8), quarantined —
  the declaring profile must ship a total-function denotation (same register as core `apply`) plus
  positive/negative conformance vectors, or the profile is non-conforming; STRICT core conformance
  (`spec/RL2_Compilation.md` §8, §10) excludes profile operators entirely; a request-independent
  profile judgment should be precomputed as a `WorldSnapshot` fact rather than declared as an
  operator.
- F-10 (validation regime pinned, `spec/RL2_Compilation.md` §10.1): single merged default graph as
  phase (1)/projection input, named graphs ignored, `owl:imports` not followed, no network/file
  fetching beyond supplied inputs; base IRI is an explicit caller-supplied `compile` input, a
  remaining relative IRI rejects; NO RDFS/OWL entailment before or during validation; SHACL Core +
  SHACL-SPARQL only, Advanced Features (rules, functions) inactive; `sh:Violation` rejects,
  `sh:Warning` never rejects but must be reported; canonical report projection is
  `(source shape IRI, focus node, result path, severity)`, deduplicated and sorted, messages
  excluded.
- F-06/F-07 (Offer bundling / output-port boundary): no `materializeBundle` and no overloading
  `rl2:Offer`/`requiresProfile` to carry a bundle of tagged `Set` policies —
  `materialize(Offer, Acceptance)` stays single-Offer. Concrete-at-acceptance data products (Level
  1) are expressed with one Promise per named output port plus a product-wide prerequisite
  attestation Duty (see `conformance/usecases/data-product-offer.md`). Per-request policy-universe
  selection (e.g. tag-based, per port/asset) is the assembler's job, kept replayable via the
  informative `SelectedPolicyUniverse` manifest (`docs/RL2_ExternalData.md` §6), not a kernel
  concept.
- F-13 (external-data admissibility language unpinned): trust verification (signatures, provenance
  chains, trust anchors, connector authentication) is pre-`Eval`, performed by the trusted
  assembler before `WorldSnapshot` exists; `Eval` never does cryptographic or chain-of-trust
  verification. `EvaluationConfiguration` carries admissibility as a closed, finite three-kind
  record (`allowedSources`, `maxAge` per left-operand resolution path; `evidenceSigners` per
  Duty-evidence scope) — not a predicate language, not profile-extensible — with a canonical JSON
  form covered by the configuration echo/digest in `EvaluationResult`. A fact or evidence item
  failing the filter is treated exactly as absent, yielding the ordinary attributed `Missing`
  (never a distinct error kind, never a silent skip). The full per-operand data contract and a
  normative `RequiredInputs` companion stay deferred (§6).
- R-04/R-05 (admissibility completion and closure complexity, `fix-codex.md`): `evidenceSigners` is
  keyed by the owning Duty's own stable identity (`sourceIdentity(d)`), not by `EvidenceSelector`
  shape, so a bound occurrence inherits its template's entry unchanged regardless of who requested
  it. A configured constraint (`allowedSources`, `maxAge`, or `evidenceSigners`) whose candidate
  lacks the attribution field it reads fails that filter, deterministically and conservatively in
  both directions. The "visible in causes" claim for admissibility filtering is qualified, not
  retracted: a filtered fact surfaces as an ordinary attributed `Missing`; filtered-to-empty evidence
  is a definite status (typically `Pending`) with no distinct cause of its own; an over-restrictive
  `evidenceSigners` entry is visible only by comparing two evaluations' configuration digests side by
  side, never by inspecting one evaluation's causes. Separately, the Complexity Analysis section's
  closure-construction claim (O(`n_hier`) space *and* O(1) membership for the same representation)
  was not simultaneously achievable and is corrected: `n_closure` (reachable pairs, up to `V²`) names
  the materialized closure's actual size, and the section now states the materialized-vs-compact
  space/lookup-cost trade-off explicitly instead of asserting both sides of it at once.
