# S2-C4 Review Record

**Status:** Resolved and executed 2026-07-31

**Reviewed:** 2026-07-31

## Controlling disposition

This file preserves the review that prompted the final S2-C4 tightening. Its option rankings are
review input, not the controlling decision. The executed disposition is:

- adopted: D1/D2 with locality limited to top-level Norm clauses and attached prerequisite
  Duties; D6, D7, D12, D13(a), and D14;
- retained from the closed contract: explicit identity maps, generated Claims, rejection of
  unsupported Promise operands, and status reporting for all reachable Duties;
- clarified: an Offer condition is proposed Agreement applicability, never offer validity or
  acceptance authorization;
- deferred to their named workstreams: general Claim derivation (Hohfeld/canonicality), diagnostic
  unification (S2-M1), and an Acceptance conformance class (S2-T1).

The Promise habitat is same-Offer and transformation-local: a Promise and dependent terms are
sibling Offer clauses, materialization rewrites the dependency, and only the Agreement is
operative. Cross-policy Promise references are invalid. This fourth option supersedes the fork in
§4.

**Reviews:** `s2-c4-follow-up.md` against `spec/RL2_Semantics.md` §Pure Offer Acceptance,
`spec/RL2_Model.md` §7–8, `spec/rl2.ttl`, `spec/rl2-shacl.ttl`, and the 52-case corpus

**Relation to the package:** `s2-c4-follow-up.md` remains the delegated brief. It instructs that
"questions that would change a rule return to the senior reviewer before editing normative files."
Fourteen such questions exist. This document states them, ranks the options, and reissues the work
order so the mechanical portion can start on the parts that no open question touches.

---

## 1. Verdict

The S2-C4 transformation is sound in its core move: a pure, total, snapshot-independent
`materialize` with explicit identity allocation and typed rejection is the right shape, and
crystallizing action→Achievement / state→Maintenance is the right mapping onto the S2-C2 Duty
algebra. Nothing below asks to reopen that.

What is not yet closed is the *boundary* of the transformation. Three of its rules — what counts
as "local", what the Agreement inherits from the Offer, and which of the Offer's outputs are
minted versus derived — are stated with terms that are not defined anywhere (`structurally
contained`, `structurally conforming`) or that quietly contradict a sibling rule. A mechanical
sweep executed against them will encode the contradictions into four use cases and the vector
ledger, where they become much more expensive to remove.

Separately, the sweep's own premise deserves a challenge. Task B assumes use cases 8 and 11 are
Promise scenarios that need re-encoding. Under the current SHACL, a Promise has exactly one
validated home — an Offer — and an Offer contributes no atoms to `Out`. Within a single policy a
Promise therefore cannot influence any decision. Whether it may do so *across* policies is
unstated, and the answer determines whether roughly one page of core vocabulary is live or dead
(§4). That question is prior to rewriting either use case.

---

## 2. Package audit

### A. Terminology sweep — substantively complete

Every prohibited token is clean in the active tree except:

| Site | Finding |
|---|---|
| `docs/RL2_References.md:444,446` | Indexes `RL2_IR.md` and `RL2_ODRL_Comparison.md` as current documents. The first moved to `future/reference-implementation/`; the second is now `spec/RL2_ODRL_Mapping.md`. Stale index, mechanical fix. |
| `spec/RL2_Semantics.md` §State Scope, Identity and Concurrency | Carries its non-core notice and its Offer/Agreement tier table is already S2-C4-aligned, but the versioned-snapshot / CAS / commit-validity subsections still cite `RL2_IR.md §7–§9` and `Σ.ObligationState` in live normative text. `section-disposition.md:38` dispositions them to future work. Until that extraction happens, the sweep's token list can never go clean. |
| `docs/RL2_Vocabulary.md:~1290–1400` | Documents `rl2p:` protocol terms in an active informative document without a non-core notice. |
| `docs/RL2_Primer.md:918` | `No obligations until accepted`. The sweep string is lower-case and would miss this if run literally. It is also not obviously wrong — see D11 before replacing it. |

**Instruction defect:** the token list is case-sensitive as written. Re-run with `rg -i`.

### B. Offer use-case sweep — one of four done

| # | File | State | Required |
|---:|---|---|---|
| 52 | `sla-credit-clause.md` | Canonical, complete | No structural change. It is also the exhibit for D3. |
| 26 | `legal-review-gate.md` | Pre-SCOPE-2 throughout | Wholesale rewrite. Details below. |
| 8 | `data-stewardship.md` | Pre-SCOPE-2 | Blocked on §4 |
| 11 | `data-freshness-promise.md` | Pre-SCOPE-2 | Blocked on §4 |
| 50 | `runtime-evaluation.md` | `rl2p:`-based; disposition says *Future workflow* | Relocate, do not sweep |

`legal-review-gate.md` defects, in order of severity:

1. `ex:vendorAccessPrivilege` is a clause of both the Offer and the Agreement. This violates
   decision 8 and the freshness/injectivity rule directly, in the one file whose subject *is*
   Offer→Agreement.
2. The document models acceptance as a lifecycle with a Draft/Offer/Accepted/Rejected state
   machine. `materialize` is a pure function, not a transition system.
3. Agreement *formation* is conditioned on an `rl2:Event` with `rl2:approver`. This conflates a
   pre-evaluation transformation with an `Eval`-time applicability condition. Under SCOPE-2 the
   legal-review precondition is not a policy condition at all: it is a precondition on the
   acceptor's decision to issue an `Acceptance`, which sits outside `Eval` entirely.
4. No `Acceptance` value is shown.
5. `Status: DRAFT`.

The consequence of (3) is that most of this use case's business intent leaves the core. What
remains in core is an Offer, an Acceptance, and the resulting Agreement. If a policy must still
gate on the approval, that is an ordinary applicability condition on an Agreement Privilege over
approval *evidence* — which is what use cases 7 and 31 already demonstrate. Recommend rewriting it
to exactly that shape and relocating the review-workflow narrative to `future/protocol/`.

`data-stewardship.md` and `data-freshness-promise.md` share one defect that §4 must settle first:
both declare profile operands (`governance:promiseStateOperand`, `governance:promisorOperand`,
`datacontract:promiseStateOperand`) with `resolutionPath "state.Promises.<x>.state|.promisor"`.
These duplicate the now-existing core `rl2:promiseStateOperand` / `rl2:promisorOperand` — two RDF
shapes for one proposition, a canonical-form violation — *and* they re-admit mutable Promise state
as a snapshot fact, which `RL2_Model.md` §7 forbids ("an asserted `rl2:promiseState` is never
authoritative input"). Use case 8 additionally authors `rl2:promiseState rl2:Pending` and omits
`targetNorm` altogether, so its Privilege never references the Promise node it is nominally about.

### C. Conformance vectors — complete against the listed rules, five gaps

`conformance/vectors/offer-materialization.md` covers all ten items the package enumerates
(M1–M8, R1–R11, P1–P5). Missing:

- the error-suppression rule ("a primary error on a Promise suppresses derivative output-shape and
  rewrite errors") has no vector;
- a supplied `dutyWindow` that is not a valid interval (D14);
- an attached Duty that is also referenced from outside the Offer (D1);
- a copied Norm that is neither top-level nor an attached Duty (D2);
- R9's stated cause is wrong (D7).

Also, M5 (attached-Duty copy with reference rewriting) and M8 (Offer non-operation) have no worked
graph anywhere in the corpus. Both qualify under the package's "add examples only when they test a
distinct listed rule."

### D. Validation and handoff — no open questions

`--core-only`, `--shapes-only`, and `--per-fence` all exist in `tools/validate.py`; the flag
combination in the package is valid. Purely mechanical.

---

## 3. Defects in the closed contract

Severity uses the project legend: **S1** blocks core soundness · **S2** significant gap ·
**S3** hygiene. Tags follow `issues.md`.

### D1 — `localNorms(O)` contradicts the external-reference rule · S1 · [GEN][VER]

**Statement.** `localNorms(O)` is defined as "the least finite set containing every Norm clause of
`O` and every Norm structurally contained from that set through `prerequisiteDuty`,
`correlativeTo`, `affectsNorm`, `exposedTo`, or `immuneFrom`." Two lines earlier: "Norm references
outside the normalized Offer boundary remain external and are not copied."

**Why these conflict.** Four of the five closure properties are *reference* properties, not
ownership. `affectsNorm`, `exposedTo`, and `immuneFrom` exist precisely to point at norms in other
policies — that is what a Power over someone else's Agreement clause *is*. `correlativeTo` is
`owl:SymmetricProperty`, so the closure walks in both directions. Taken literally, the closure
copies and renames external norms; taken as the boundary rule says, it must not. The only thing
separating the two readings is "structurally contained", which is defined nowhere.

**Consequence (D2, folded).** Materialization also has no placement rule for the class of nodes the
closure creates. The output rule says "only mapped top-level Norms become Agreement clauses; copied
attached Duties remain attached." A Claim reached via `correlativeTo` is neither. It lands in the
Agreement as a Norm that is not a clause and not attached — invisible to `Out`, which iterates
clauses, and invisible to `AgreementShape`, which does not constrain it. Dead nodes by
construction.

**Options.**

| | Approach | Assessment |
|---|---|---|
| a | Close only over `prerequisiteDuty`. All other Norm-valued properties are pure references: never copied, rewritten only when their target is independently local. | **Recommended.** Minimal. `prerequisiteDuty` is the only property the ontology treats as ownership, and `PrerequisiteDutyShape` already guarantees an attached Duty is not a clause of any policy — so the "not owned elsewhere" test is derivable and need not be stated. Eliminates D2 entirely: every copied Norm is either a top-level clause or an attached Duty. |
| b | Keep the current closure, add the side condition "and is not a clause of another policy". | Preserves an ill-founded notion of containment and still admits Claims and Powers reached by reference. Also needs a placement rule for D2. |
| c | Define locality by RDF containment (blank-node nesting). | Rejected. Ties semantics to a serialization accident and contradicts "canonical projection is normative; raw RDF graph identity is not semantic identity." |

**Cost of (a).** One paragraph in §Pure Offer Acceptance; the vector M5 wording narrows from "any
attached Norm" to "attached prerequisite Duty". No IRI or SHACL change.

### D2 — Placement of copied non-clause, non-attached Norms · S1 · [VER]

Folded into D1. Disappears under D1(a); requires an explicit rule under D1(b).

### D3 — Correlative Claims are generated asymmetrically · S1 · [GEN]

**Statement.** `claimIds : total map PromiseRef → IRI` gives every crystallized Duty an explicit
correlative Claim. Copied Duties get none, even when they carry a `counterparty`.

**Evidence.** `sla-credit-clause.md`: `ex:uptimeDuty` (from a Promise) receives `ex:uptimeClaim`;
`ex:creditDuty_A1` (copied) has `rl2:counterparty ex:Customer` and no Claim. Two Duties of
identical normative shape, in one Agreement, with different graph shapes. `AGENTS.md` §6: "Two
graphs that differ structurally must differ semantically."

**Sharper form.** `ClaimShape` forbids a Claim from authoring `action`, `object`, `condition`,
`postCondition`, `invariant`, or `dutyWindow`, requires exactly one `correlativeTo` to a Duty, and
requires its two party roles to mirror that Duty's. A Claim node therefore carries **zero**
information not derivable from its Duty. Minting one is declaring what can be derived.

**Options.**

| | Approach | Assessment |
|---|---|---|
| a | Derive Claims; never mint them. Drop `claimIds`. §Hohfeldian Correlatives already defines Duty↔Claim; make the correlative a derived normative atom for every Duty with a `counterparty`. | **Recommended for materialization.** Removes one Acceptance field, one error surface, and the asymmetry. Note it raises the wider question of whether *authored* Claims are also redundant — four use cases author Claim IRIs as policy clauses (`claim-counterclaim`, `pass-through-terms`, `data-sovereignty`, `sla-credit-clause`). That wider question belongs to CANON-3/HOHF-3, not here; scope this decision to materialization output. |
| b | Mint a Claim for every counterparty-bearing Duty in the Agreement — widen `claimIds`' domain to `PromiseClauses(O) ∪ {local Duties with a counterparty}`. | Restores symmetry, keeps Claim IRIs addressable, grows the Acceptance value and the caller's enumeration burden. Choose this only if authored Claim IRIs must remain referenceable from outside. |
| c | Keep as is. | Rejected. The stated justification — that a crystallized Duty needs an explicit Claim so the promisee relation is not lost — is false: `counterparty` already carries it. |

**Corpus note.** `correlativeTo` is `owl:SymmetricProperty`, so each direction entails the other.
`data-sovereignty.md` authors *both* (`:auditDuty correlativeTo :auditClaim` at 170 and
`:auditClaim correlativeTo :auditDuty` at 176) while `sla-credit-clause.md` authors only
Claim→Duty. Both validate. That is two RDF shapes for one proposition, plus a redundant triple — a
separate canonical-form defect worth one SHACL constraint (author Claim→Duty only) regardless of
how D3 resolves.

### D4 — The Offer's `rl2:condition` is inert, then silently becomes operative · S1 · [GEN][VER]

**Statement.** `materialize` sets the Agreement's `condition = rewrite(O.condition)`.

**Why this is wrong.** An Offer contributes no atoms to `Out`, so `rl2:condition` on an Offer gates
nothing and has no evaluation meaning before acceptance. An author writing it means "this offer is
open for acceptance until X". After the copy, the identical structure means "these clauses apply
when X". Those are different propositions with different lifetimes: an offer-validity window must
not become the Agreement's applicability guard, or every Agreement silently expires when its
catalogue entry closed.

The corpus does not yet exercise this — no use case puts `rl2:condition` on an `rl2:Offer` — so the
fix is cheap now and expensive after the migration wave.

**Options.**

| | Approach | Assessment |
|---|---|---|
| a | Forbid `rl2:condition` on an `rl2:Offer` in SHACL; drop the copy rule. Terms that gate the Agreement are authored on clauses. | **Recommended.** One SHACL constraint, one deleted rule, no new IRI. Makes the inert-then-operative path structurally impossible rather than documented. |
| b | Drop the copy; let the Acceptance supply an optional `agreementCondition`. | Adds an Acceptance field for a capability no use case has asked for. Consider only if (a) proves too restrictive. |
| c | Split the vocabulary: `rl2:condition` for applicability, `rl2:offerValidity` for offer-open windows, copy neither. | Adds an IRI to name a distinction (a) removes structurally. Reserve for the case where offer validity must be machine-checkable. |
| d | Keep the copy, document the conflation. | Rejected. Leaves a latent contract bug in a normative rule. |

**Note.** (a) requires one new SHACL constraint. The package states "the fixed S2-C4 contract
requires no new IRI or constraint," so this is explicitly a rule change and yours to approve.

### D5 — Identity allocation declares what could be derived · S2 · [GEN]

**Statement.** `primaryIds` and `claimIds` are *total* maps keyed by `SourceRef`. To construct
them, a caller must independently compute `localNorms(O)` — including attached Duties reached
through the closure. The caller must therefore implement part of the transformation before it can
invoke the transformation.

Three rejection classes exist only to police this input: `InvalidIdentityAllocation` (R5),
`InvalidAcceptanceDomain` (R11), and the domain-totality half of validation item 4.

**Options.**

| | Approach | Assessment |
|---|---|---|
| a | Derived naming: `outputIri(n) = mint(A.agreementId, ref(n))` for one specified total injective `mint`. | Cleanest. Purity and determinism preserved; injectivity by construction; freshness follows from `agreementId` freshness, which the caller already guarantees. Eliminates both maps, `InvalidIdentityAllocation`, R5, R11, and D6. **Cost:** depends on a canonical encoding of `ref(n)`, which S2-C4 deliberately deferred to S2-C5. Creates a sequencing dependency. |
| b | Derived by default, explicit partial override map. Unmapped sources get `mint(...)`. | **Recommended.** Removes the enumeration burden and the domain-totality error class while preserving caller control where it matters (stable IRIs for Agreement clauses that outside policies will reference). Same S2-C5 dependency as (a), but degrades gracefully: if `mint` is not settled, the override map still works. |
| c | Keep totally explicit. | Defensible only if every caller is a generator that already holds the normalized AST. State that assumption if you keep it — it is currently unstated and it is load-bearing. |

### D6 — Freshness is stated over IRIs; the domain is `SourceRef` · S2 · [VER]

**Statement.** "all `primaryIds` values, and all `claimIds` values MUST be pairwise distinct and
MUST NOT reuse an identifier of the source Offer or one of its local sources." That comparison
needs a function `iri(SourceRef)`. The same paragraph disclaims any dependence on `ref`'s concrete
encoding.

It is also unsound for blank nodes. Attached prerequisite Duties and condition nodes are routinely
blank in this corpus; a blank source has no identifier to collide with, and copying a blank node to
an allocated IRI changes the canonical projection — a fact the rule does not acknowledge.

**Options.** (a) Restate as: *the set of allocated output IRIs is disjoint from the set of IRIs
occurring in the normalized Offer* — precise, needs no `ref` encoding, well-defined for blank
sources. (b) Require every local Norm to be IRI-named; too strong an authoring constraint. (c) Moot
under D5(a).

**Recommendation:** adopt (a) now regardless of how D5 resolves.

### D7 — `StatusDependencyCycle` is mis-attributed · S3 · [VER]

Vector R9 reads "Rewriting creates a status dependency cycle." Rewriting is an injective renaming
composed with one operand substitution; it cannot create a cycle in the reference graph. Any
post-rewrite cycle was present in the Offer.

The check is still worth having, for a reason the spec does not give: Offers are never evaluated,
so `validateConfiguration`'s cycle check never runs on them, and materialization is the first point
at which the defect can surface. The error is already correctly typed as `InvalidOffer`.

**Action:** reword R9 to "the Offer's reference graph contains a status-dependency cycle" and add
the one-sentence rationale to §Validation item 7. Also note the redundancy with
`validateConfiguration` — the same property, two diagnostic vocabularies (see D9).

### D8 — Rejecting `promisorOperand` is a symptom of a missing operand · S2 · [GEN][COV]

**Statement.** `promisorOperand` reads *static policy content*: the agent bound by the Promise.
After crystallization that agent is the Duty's `subject`. The rewrite is unavailable only because
core has no operand that reads a targeted Norm's authored subject — `dutyPerformerOperand` is a
different thing, projecting the actual performer from evidence.

So `UnsupportedPromiseReference(site, p, promisorOperand)` is correct today, but the cause is a
vocabulary gap, and its effect is that an Offer legitimately asking "am I the promisor?" cannot be
materialized at all.

**Options.**

| | Approach | Assessment |
|---|---|---|
| a | Add core `rl2:normSubjectOperand` reading the targeted Norm's authored `subject`; rewrite `promisorOperand@Promise(p) → normSubjectOperand@Duty(p)`. | Makes the core rewrite total and removes one rejection class. Note the follow-on: `promisorOperand` then becomes *derivable* (promisor = subject of the crystallized Duty), so one operand over both Norm and Promise targets could replace two — a canonical-form win. Requires ontology sign-off per `AGENTS.md` §7. |
| b | Keep the rejection; document the authoring rule ("do not query a promisor in a clause you intend to materialize"). | **Recommended for now.** Zero cost, and D8 is downstream of §4: if Promise-state operands turn out to be unreachable from any decision, (a) buys nothing. Revisit after §4. |
| c | Profile-defined rewrite hook. | Rejected. Adds a transformation extension point to core for one operand. |

**Tracker hygiene.** `issues.md` PROM-4 still reads "No `promisorOperand` in core." It exists at
`rl2.ttl:356`. Close it.

### D9 — Two disjoint error algebras · S3 · [VER]

`MaterializationError` is structurally parallel to `EvalError` — constructor plus site plus
referenced identifier, identity excluding prose, set-valued, all-or-nothing — and shares no types
with it. `InvalidOffer(site, reason)` mirrors `Invalid(Site)`.

**Options.** (a) One `Diagnostic(site, code, refs)` with per-phase code enumerations. (b) Leave
disjoint, document the parallelism. (c) Unify `Site` only.

**Recommendation:** (c) now, (a) as an explicit S2-M1 decision — ODRL import is about to introduce
a third diagnostic vocabulary, and three is the point at which this stops being tidiness.

### D10 — Materialization has no conformance clause · S2 · [VER]

`RL2_Model.md` §10 lists five conformance requirements. None covers `materialize`, although the
transformation is normative in two documents and has a vector ledger.

Note that a conforming *evaluator* need not implement `materialize` at all — it consumes
Agreements. That argues for a separate, optional **Acceptance conformance class** rather than a
sixth item in the core list.

**Recommendation:** add it as a separate claim in §10, alongside wire formats and storage models.

### D11 — The domain of the two status maps is unstated · S2 · [VER]

`EvaluationResult.dutyStatuses : finite map Duty → StatusResult` never says over which Duties.
`RL2_Model.md` §8 says an Offer's "Promise and referenced Duty statuses" may still be reported for
inspection.

Taken literally, a Duty clause of an unaccepted Offer gets a definite status. In
`sla-credit-clause.md`, `ex:creditDuty` is an unbounded Achievement Duty; before anyone accepts
anything, it reports `Active` — "must be fulfilled" — for a term of a proposal nobody has agreed
to. That honours the letter of decision 1 (no *atoms*) while contradicting its intent.

**Options.** (a) Restrict both maps to norms reachable from operative policies; report nothing for
Offer clauses. (b) Report Offer statuses with a tag — rejected, adds result metadata with policy
meaning. (c) Report *Promise* statuses for Offers and exclude Offer Duty clauses.

**Recommendation:** (c). Promise inspection is the reason the allowance exists, and a Promise has
no access effect in any case. State the domain explicitly in §6 either way — this is currently
implementation-defined by omission, which the Scope forbids.

### D12 — A cross-policy Promise query survives materialization and diverges · S1 · [VER]

**Statement.** `targetNorm` is a reference; nothing restricts it to the containing policy.
`AtomicConstraintShape` admits a Promise-valued target and `PromiseStateConstraintShape` requires
one for `promiseStateOperand`. So a `Set`'s Duty may condition on a Promise living inside an
`Offer`.

Materialization rewrites references *inside* the Offer only — external references are unchanged by
rule. After acceptance the external policy still queries the Promise while the Agreement queries
the crystallized Duty. Two status sources for one commitment, and they can disagree: `PromiseState`
has no `Active`, and a windowed Maintenance Duty can reach `Fulfilled` where a Promise never can.

If the source Offer is then withdrawn from the universe, the external `targetNorm` dangles.
Decision 10 stops a Promise surviving in an *Agreement*; it does not stop one surviving in the
*universe*.

**Options.** (a) Require a Promise-valued `targetNorm` to resolve within the same Offer (SHACL
SPARQL constraint). Then every Promise query is Offer-internal and every one is rewritten.
(b) Extend the rewrite across the universe — rejected: `materialize` takes no universe, and this
would destroy its locality. (c) Accept and document the divergence.

**Recommendation:** (a), and note that it interacts with §4 — under §4 option (ii) it must not be
adopted, because (ii) depends on exactly this cross-policy path.

### D13 — Object templating is available for state promises and denied for action promises · S3 · [GEN]

`PromiseShape` requires `rl2:object` for `promisedAction` but leaves it optional for
`promisedState`; `DutyShape` requires `object` on every Duty. So an object-less state promise
validates and is then unconditionally `MissingPromiseObject` at acceptance unless `objectBindings`
supplies one — while an object-less action promise cannot be authored at all.

The asymmetry has no stated reason. `objectBindings` exists to support a catalogue Offer accepted
per asset, which is a real requirement; if so, it should apply to both content forms.

**Options.** (a) Permit an omitted object on `promisedAction` too, making `objectBindings` uniform.
(b) Require `object` on `promisedState`, moving the error to authoring time — but this leaves
`objectBindings` with no motivating case, at which point it and two error classes
(`MissingPromiseObject`, `ConflictingObjectBinding`, R2, R3) should be deleted. (c) Status quo.

**Recommendation:** decide which of (a) or (b) reflects the intent, then apply it symmetrically.
Either is coherent; the present mixture is not.

### D14 — Supplied `DutyWindow` values are not validated · S2 · [VER]

Validation items 1–7 never require a supplied window to be a valid interval. Item 7 says rewriting
must produce a "structurally conforming Agreement", which is not defined as "passes
`rl2-shacl.ttl`" — and `materialize` is specified over the normalized AST, not over RDF, so the
`DutyWindowShape` SPARQL check is not obviously in scope.

**Recommendation:** state that item 7 means SHACL conformance of the projected Agreement graph, and
reuse `RL2_Model.md` §4.1(4)'s existing interval-validity definition rather than restating it. Add
the corresponding vector.

---

## 4. The prior question: where may a Promise live?

This is not a defect in S2-C4. It is a question S2-C4 makes unavoidable, and it must be settled
before use cases 8 and 11 are rewritten, because both exist to demonstrate "a Promise gates
access."

**The constraint set as it stands.** `AgreementShape`, `SetShape`, `PrivacyPolicyClauseShape`, and
`AssertionClauseShape` all forbid Promise clauses. Only `Offer` permits one. An Offer contributes
no atoms to `Out`. Therefore:

- Within a single policy, a Promise can never influence a decision.
- Across policies it can, only via the D12 path — which D12(a) would close.
- After materialization no Promise survives in the Agreement, so the operand is rewritten away.

**What is at stake.** If cross-policy Promise queries are disallowed, then
`rl2:promiseStateOperand`, `rl2:promisorOperand`, `PromiseStateConstraintShape`, the
`promiseStatuses` result map, and the Promise branch of `resolve` have no path to any decision.
That is a page of core vocabulary, two SHACL shapes, and a result field that exist only for
inspection.

Three of the four Promise-bearing use cases sidestep the question by placing the Promise in **no
policy container at all** (`data-stewardship`, `data-freshness-promise`) or in an untyped container
(`runtime-evaluation`). Free-floating Promises are arguably not in "the supplied policy universe",
which leaves `promiseStatus` undefined for them — the corpus is currently relying on a shape the
spec does not sanction.

**Options.**

| | Approach | Assessment |
|---|---|---|
| i | Allow Promise clauses in `Set` / `Agreement` as non-correlative commitments. | Rejected. Contradicts decision 10 and `AgreementShape`'s own rationale: an inert Promise in a binding policy is a verification liability. |
| ii | Allow cross-policy `promiseStateOperand` explicitly: an Offer's Promise is observable by operative policies. Rewrite use cases 8 and 11 with the Promise inside an Offer and the gating Privilege in a Set. | Least disruptive; keeps the vocabulary alive and the Promise Theory claim honest. **Requires D12 to be resolved as (c)**, and requires stating what happens to an external query when the Offer is accepted or withdrawn. The answer is uncomfortable: the external policy is fragile either way. |
| iii | Remove Promise-state operands from core. Promises become pre-acceptance content only. Use case 8 becomes a `prerequisiteDuty`; use case 11 becomes a Maintenance Duty in an Agreement. | **Most defensible minimal core**, and it is what the rest of S2-C1..C4 has been converging on: status from evidence, access from Duties. Cost is the Promise Theory positioning, which `docs/FAQ/RL2_Why_Promises.md` and PROM-8 already flag as philosophically strained (RL2 tracks promise state centrally; Burgess assesses from the promisee's observation). Worth costing before rejecting. |

**Recommendation:** decide between (ii) and (iii) before touching use cases 8 and 11. My reading is
that (iii) is the honest end state and (ii) is the one that preserves the most existing text; the
choice is a positioning decision, not a technical one, which is why it is yours.

---

## 5. Corrected work order

### Now — unblocked, no open question touches these

1. `docs/RL2_References.md:444,446` — repoint to `spec/RL2_ODRL_Mapping.md` and
   `future/reference-implementation/RL2_IR.md`, marking the latter non-core.
2. `docs/RL2_Vocabulary.md` — add a non-core notice to the `rl2p:` section.
3. `conformance/usecases/runtime-evaluation.md` — relocate per its *Future workflow* disposition
   rather than sweeping it.
4. Vector ledger: reword R9 (D7); add vectors for error suppression, invalid supplied window
   (D14), and the two locality cases (D1/D2) once D1 is decided.
5. `issues.md`: close PROM-4 as already implemented (D8).
6. Re-run the task-A token sweep case-insensitively.

### After D1, D3, D4 are decided

7. `spec/RL2_Semantics.md` §Pure Offer Acceptance — apply the decided locality rule, Claim rule,
   and condition rule. Update `RL2_Model.md` §8 to match.
8. `conformance/usecases/legal-review-gate.md` — full rewrite: Offer, explicit Acceptance,
   Agreement-local identifiers, approval as evidence on an Agreement Privilege, workflow narrative
   moved to `future/protocol/`, status normalized.
9. `sla-credit-clause.md` — no structural change, but add a Claim for `creditDuty_A1` or remove
   `uptimeClaim`, depending on D3.

### After §4 is decided

10. `data-stewardship.md` and `data-freshness-promise.md` — rewrite to the chosen Promise habitat;
    delete the duplicate profile operands and the authored `rl2:promiseState` regardless of which
    option wins.

### Deferred but scheduled

11. D5 (identity derivation) — decide with S2-C5, which supplies `ref`'s canonical encoding.
12. D9 (error algebras) — decide with S2-M1, before ODRL import adds a third vocabulary.
13. D10 (Acceptance conformance class) — with S2-T1.
14. `spec/RL2_Semantics.md` §State Scope — complete the extraction dispositioned at
    `section-disposition.md:38`. Out of this package, but the task-A token list cannot go clean
    until it happens.

---

## 6. Completion gate, restated

The package's gate stands, with two additions:

- every active Offer example either stays non-operative or shows a valid explicit Acceptance;
- no active document describes runtime crystallization;
- all touched Turtle fences pass independently;
- no delegated edit changes a fixed decision;
- **every term used in a normative rule is defined** — currently `structurally contained` and
  `structurally conforming` are not;
- **no two Norms of the same normative shape have different graph shapes in one materialized
  Agreement** (D3).
