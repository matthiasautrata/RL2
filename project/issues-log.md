# RL2 Issues — Log (Archive)

Completed work and historical record for RL2, split out of `issues.md` on
2026-07-30 to keep the active tracker small. Holds: the full changelog, resolved
band entries (with their decisions + rationale), the deep-sweep **WP-0…WP-5**
roadmap, and the § Resolved decisions (SCOPE-1, ACT-1/2, CANON v0.6). SCOPE-2 supersedes the
former runtime-protocol/IR boundary; see `../spec/RL2_Scope.md`. The active
backlog lives in [issues.md](issues.md); cross-references like "SEM-9 (Resolved)",
"WP-4/S7", or "C6b" resolve to this file.

---

## Changelog

**Updated: 2026-07-31 (S2-C3 resolved).** Added one canonical prerequisite-Duty relation,
made prerequisite failure local to its owning Privilege, removed all global Duty flags from
access resolution, and moved concurrent/post-use requirement packaging outside core.

**Updated: 2026-07-31 (S2-C2 resolved).** Replaced the contradictory Duty lifecycle model with
two canonical structural forms and pure status functions: Achievement (`action`, optional
`postCondition`) and Maintenance (`invariant`), each with an optional finite half-open
`dutyWindow`. Removed authored `dutyMode`; kept `condition` solely for applicability.

**Updated: 2026-07-31 (S2-C1 resolved).** Adopted the immutable `WorldSnapshot` and pure
evaluation boundary, integrated it into the normative model and semantics, added nine component
vectors, and aligned protected ontology/SHACL annotations without changing vocabulary or
constraints. S2-C2 is the next core decision.

**Updated: 2026-07-31 (SCOPE-2).** RL2 narrowed its normative center to the policy language and a
pure evaluation contract over a request and immutable world snapshot. ODRL migration and semantic
conformance are first-class deliverables. Case lifecycle, event sourcing, persistence,
re-evaluation workflows, distributed commit, and a prescribed IR moved to `future/`. The active
execution order and former-stopper dispositions are in `issues.md`; the controlled repository
transition is in `reorganization-plan.md`.

**Updated:** 2026-07-30 (integration sweep merged) — a fresh external review (`fix.md`, dated
2026-07-29) was merged and the source files (`fix.md`, `fix-codex-original.md`) deleted, same
disposition as every prior sweep. Its findings live in the new **§ Remediation Roadmap —
integration sweep (2026-07-29)**: **Class 1 (E1–E16)** — E1/E3–E11/E13/E14 applied in commit
`ae0026b`, E2/E12/E15/E16 deferred (with reasons); **Class 2 (D1–D25)** and **Class 3
(C3-1…C3-8)** cross-referenced to the WP/band entries they sharpen or re-open. The headline: the
execution model is endorsed, but WP-2…WP-5's locally-sound definitions aren't yet *integrated*
into one deterministic evaluator — integration-follow-up notes were added to the WP-2/3/4/5
status lines, and §7's dependency-ordered work order is now the authoritative next sequence.

**Updated:** 2026-07-29 — SCOPE-1 terminology and the active execution-model entries were
aligned with the direct normalized-AST design. Verified-kernel, Forth/bytecode, Dafny/Go, and
already-tested wording is retained only where an entry explicitly records superseded history.

**Consolidated:** 2026-07-24 — merged from the former `critique.md` (three-part external review), `fix.md` (multi-role remediation plan), and the prior `issues.md`. Those three source documents are superseded by this file.

**Updated:** 2026-07-25 — merged `backlog.md` into this file. The open design decisions (namespace, owl:imports, ODRL transpiler) are now § Open Decisions below. The backlog's work items and success criteria were already tracked as IMPL-1..3 and the S1/S4/S6 proof obligations. `backlog.md` is deleted. Review findings and the full remediation roadmap live in `fix.md` (cross-referenced from issues where relevant).

**Updated:** 2026-07-25 (later same day) — merged the fresh `fix.md` (full spec audit + engineering analysis + remediation roadmap) and `fix2.md` (independent quality-sweep corroborating, sharpening, and extending `fix.md`) into this file. Every actionable finding from both is now tracked below: new entries **SEM-9..14**, **CONS-1..6** (new Band 1.5), **EXPR-7/8**, **VALID-4**, **DOC-9..11**, **LLM-1** (new Band 6), **OPEN-4**; plus amendments folded into the existing **SEM-1**, **SEM-4**, **PROM-7**, **IMPL-1**, **DOC-3**, **DOC-4**, **DOC-6** entries. `fix.md` and `fix2.md` are superseded by this file (same disposition as `backlog.md`/`critique.md` above).

**Updated:** 2026-07-25 (docs-only cleanup pass) — worked down the mechanical/editorial findings that touch only Markdown docs (no ontology/SHACL files, no design decisions): **DOC-3, DOC-6, DOC-9, DOC-10, DOC-11, SEM-12, CONS-4, CONS-5** resolved; **DOC-4** partially resolved (staleness disclaimer added to `RL2_ODRL_Comparison.md`; the actual merge into `RL2_Primer.md` stays open). Remaining findings in Band 1.5 (CONS-1/2/3/6) touch `rl2-shacl.ttl`/`rl2p-shacl.ttl`/`RL2_IR.md` and were deliberately deferred pending explicit discussion per `AGENTS.md` §7.

**Updated:** 2026-07-25 (SHACL/IR tightening pass, discussed and approved per `AGENTS.md` §7) — **CONS-6** (`sh:maxCount 1` on Atomic/Logical/Event constraint shapes in `rl2-shacl.ttl`) and **CONS-3** (`source: Clause` added to `CrystallizePromise` in `RL2_IR.md`) resolved; then **CONS-1** (`sh:or` over fulfillment-evidence properties in `rl2p-shacl.ttl`) and **CONS-2** (documented, not SHACL-rejected, the intentional Active-on-Promise-Requirement projection, cross-referenced into `rl2p.ttl`/`rl2p-shacl.ttl`; closes PROM-7's reconciliation sub-task) resolved. All of Band 1.5 is now resolved except PROM-7's separate `targetNorm` range-widening sub-task. Full corpus revalidated clean after each change: `PASS 0 · WARN-ONLY 51 · FAIL 0 · SKIP 1`.

**Updated:** 2026-07-25 (PROM-7 closed, discussed and approved per `AGENTS.md` §7) — **PROM-7** fully resolved: `rl2:targetNorm` widened to admit `rl2:Promise` (enforced via `sh:or` in `rl2-shacl.ttl`'s `AtomicConstraintShape`, deliberately *not* via `rdfs:range owl:unionOf` — that broke `RL2_Primer.md`/`RL2_Vocabulary.md`'s reliance on RDFS range-entailment auto-typing, see PROM-7 for the full root-cause note); new `materialize(Offer, Acceptance) → Agreement` function defined in `RL2_Semantics.md` §Materialization (fresh IRIs for every Agreement clause, `targetNorm` rewriting, `prov:wasDerivedFrom` provenance — borrowing PROV-O by term, first such use on individuals rather than the ontology header); `RL2_IR.md` §7.2 cross-references `materialize` as a pre-compilation step outside `evalIR`/`applyEffects`. New corpus example **Use Case 52** (`usecases/sla-credit-clause.md`). Full corpus revalidated clean: `usecases/*.md` → `PASS 0 · WARN-ONLY 52 · FAIL 0 · SKIP 1`; `RL2_Primer.md`/`RL2_Protocol.md`/`RL2_Vocabulary.md` (`--per-fence`) → `PASS 0 · WARN-ONLY 3 · FAIL 0 · SKIP 0`.

**Updated:** 2026-07-26 (fresh `fix.md` sweep merged) — a new quality sweep (`fix.md`, 13 findings against the post-PROM-7 state) is merged and the source file deleted, same disposition as prior sweeps. Four of its findings reconfirm existing open entries with no new tracking needed: **DOC-4** (ODRL-Comparison body still stale), **SEM-1** (`rl2:remedialAction` still undeclared), **VALID-4** (no IR-compilation use case), **DOC-2** (Vocabulary/TTL duplication). Two new entries need ontology/SHACL sign-off per `AGENTS.md` §7 and are tracked **Open, not yet actioned**: **CANON-6** (dead vocabulary `rl2:requires`/`rl2:ConditionOrEvent`/`rl2:NormOrEvent`), **CONS-7** (`OperandRangeTypeShape` never fires). Five doc-only mechanical items were fixed immediately in this pass: **DOC-12** (stale `CLAUDE.md`/`fix.md` rows in `AGENTS.md`'s Key Files table, plus a stale `fix.md §6.2` cross-reference now pointing at `research/verification-toolchain-comparison.md`), **DOC-14** (`design-forth-ir.md`/`design-canonical-form.md` moved to `research/`, inbound references in `RL2_IR.md`/`issues.md` updated), **DOC-15** (`RL2_Primer.md` frontmatter's editorial `audience`/`prerequisites` fields dropped; `version`/`status`/`date` kept — full frontmatter removal as fix.md's action line literally suggested would have undone DOC-1's cross-doc version/date normalization, so this pass kept the useful fields and cut only the editorial ones). fix.md's **O1** (claimed `materialize()` missing from `RL2_Semantics.md`'s TOC) is recorded as **DOC-13, not applicable**: verified the document has no Table-of-Contents section at all (unlike Primer/Protocol/Vocabulary/References) — nothing to add an entry to. Two observational notes (Σ state-category split, Protocol/Core enum coupling) needed no tracking — both already-accepted designs, not open questions.

**Updated:** 2026-07-26 (later same day — CANON-6/CONS-7 sign-off obtained and actioned) — the two ontology/SHACL items deferred in the pass above were discussed, approved by explicit sign-off, and resolved. **CANON-6**: removed `rl2:requires`, `rl2:ConditionOrEvent`, `rl2:NormOrEvent` from `rl2.ttl` (domains inlined to `owl:unionOf`); stripped references from `RL2_Vocabulary.md`/`RL2_Semantics.md`; rewrote the `RL2_Primer.md` illustrative example as a single `AtomicConstraint` (not `And`, per the entry's noted deviation — the original had nothing to conjoin). **CONS-7**: extended `OperandRangeTypeShape` in `rl2-shacl.ttl` with a SPARQL `UNION` branch checking literal right-operand `datatype()` against the leftOperand's declared `rdfs:range`, correcting fix.md's premise that the shape was fully dead (the IRI branch was already structurally live on several use cases, just quietly passing). Verified with a synthetic mismatch graph that the new branch fires correctly, then re-ran the full corpus and all affected docs per-fence: identical clean baseline throughout (`PASS 0 · WARN-ONLY 52 · FAIL 0 · SKIP 1` whole-file; per-fence docs all `FAIL 0`) — no regressions, both items now fully resolved.

**Updated:** 2026-07-26 (later same day — DOC-4 resolved, `RL2_ODRL_Comparison.md` overhauled) — the user supplied a new quantitative ontology comparison (RL2 vs. ODRL 2.2/PROV-O/DCAT 3/ORG/FOAF: raw metrics, complexity dimensions, understandability, utility-by-use-case) and decided the comparison doc should remain **standalone** rather than merge into `RL2_Primer.md` (reversing DOC-4's prior plan) — the doc needs room for motivation/use-cases/justification the Primer can't spare. Added the new section, then did a full accuracy pass rather than just applying the new content: fixed all four staleness items flagged in the doc's 2026-07-25 notice (Dafny→Go toolchain, nonexistent media profile, Duty/crystallization model, and — on inspection — found the "time-ordered Event Log" claim was actually already correct, not stale, so corrected the notice itself rather than the doc), and fact-checked the new metrics against the repo directly: caught and fixed an inaccurate "RL2 full" combined-suite row that had silently repeated the "RL2 core" row instead of rolling in `rl2p.ttl`'s classes/properties/enums. Doc version bumped 1.0→1.1. `DOC-4` closed.

**Updated:** 2026-07-26 (deep review sweep — the current `fix.md`) — a substantially deeper external review (`fix.md`, ~60 findings across semantics, ontology, IR, protocol, ODRL compatibility, external data, proofs, and docs — S1–S8, C1–C8, O1–O5, I1–I4, P1–P4, E1, D1–D5, F1–F3, R1a/b, L1/L2, A1, T1, V1, X1) supersedes the shallow 13-finding 2026-07-26 sweep merged above. Rather than fold all ~60 findings into individual band entries at once, its analysis and dependency-ordered execution plan are captured as the new **§ Remediation Roadmap (deep sweep)** below. That roadmap groups the findings into nine work packages **WP-0 … WP-8**, ordered by *semantic dependency* (following the review's own closing recommendation — drive by dependency, not by the Class 1/2/3 effort tiers), cross-references each to the band entry it sharpens or the resolved decision it must respect, and is the authoritative execution order going forward — it supersedes the 2026-07-25 "Current sequencing decision" line for ordering. **`issues.md` is the source of truth**; `fix.md` and its saved copy `fix-codex-original.md` are **interim artifacts** kept only long enough to cross-check that the roadmap and bands captured every actionable finding, then removed — work is driven from this file, not from the fix docs. The per-issue bands below remain the tracker of record for individual findings.

---

## S2-C1 — Pure evaluation contract and immutable WorldSnapshot

**Resolved:** 2026-07-31 · **Scope:** core model, semantics, conformance, and protected
ontology/SHACL annotations · **Tags:** [VER] [GEN]

### Decision

- `WorldSnapshot` is immutable and contains one evaluation time, scoped attributed facts, and
  attributed evidence. It contains no mutable Case, append log, stored Duty/Promise status, or
  evaluator callback.
- Fact lookup uses canonical `(FactScope, Path)`, half-open validity intervals, fixed type and
  admissibility checks, equal-value collapse, and `Conflict` for distinct eligible values where a
  single value is required.
- Evidence selectors match kind, actor, action, object, interval, and payload constraints. Latest
  projection uses occurrence time. Unequal values tied at the latest occurrence time conflict;
  identifiers and arrival order never select a winner.
- Duplicate identifiers collapse only when their normalized records are equal. Unequal reuse of
  one identifier invalidates the snapshot and makes `Eval` return `Indeterminate` before policy
  evaluation.
- Profile trust and admissibility are total finite predicates over attribution and explicit
  configuration. Live lookup, credential verification, connector I/O, arrival order, and Case
  membership are outside core `Eval`.
- `Eval` is a pure, total function of PolicyUniverse, Request, WorldSnapshot, and configuration.
  It validates its configuration and snapshot, derives one provenance-carrying normative
  envelope, and invokes the sole public `resolveDecision(envelope, snapshot, strategy)` form.
- A derived Duty has a status for both definite and indeterminate condition results. Unsupported
  strategies are errors; the evaluator does not silently choose a default.

### Integration

- `spec/RL2_Model.md` defines the Request, immutable snapshot, attributed facts and evidence,
  validity, identity, scope, trust/admissibility, and result boundaries.
- `spec/RL2_Semantics.md` threads the PolicyUniverse through `Env`, defines configuration and
  snapshot validation, expands event selectors over evidence, and derives the normative envelope
  without live resolution.
- `conformance/vectors/snapshot-resolution.md` supplies nine hand-derivable component vectors for
  agreement, conflict, scope/validity, duplicate identity, latest projection, future evidence,
  and invalid evidence.
- `spec/rl2.ttl` and `spec/rl2-shacl.ttl` received comment/annotation alignment only. No IRI,
  class/property axiom, range, or SHACL constraint changed.

### Validation

- Full 52-use-case corpus: `PASS 52 · WARN 0 · FAIL 0`.
- Core ontology and shapes parse and validate independently.
- A separate reader pass checked the model, semantics, and vectors for stale stateful signatures,
  incomplete result paths, and ambiguous tie behavior; the resulting integration corrections were
  applied before closure.

### Deferred boundaries

S2-C1 does not decide declarative Achievement/Maintenance Duty and Promise status (`S2-C2`), Duty
attachment and decision interaction (`S2-C3`), or role matching (`D3`). Those remain explicit
follow-on decisions rather than implicit behavior in the snapshot contract.

---

## S2-C2 — Declarative Duty and Promise status

**Resolved:** 2026-07-31 · **Scope:** core ontology, SHACL, model, semantics, vocabulary, and
conformance · **Tags:** [VER] [GEN]

### Decision

- `rl2:condition` has one meaning: policy or norm applicability.
- An Achievement Duty has exactly one `rl2:action`, may have one `rl2:postCondition`, and has no
  `rl2:invariant`. A qualifying action witness fulfills it; the postcondition, when present, is
  evaluated at the witness occurrence time.
- A Maintenance Duty has exactly one `rl2:invariant` and has no action or postcondition. A
  counterexample violates it; fulfillment requires complete fact/evidence coverage of a closed
  finite interval.
- Either form may have one `rl2:dutyWindow`, represented as the half-open interval
  `[startInclusive,endExclusive)`. Evidence at the end instant is outside. An unbounded
  Achievement can be fulfilled but not time out; an unbounded Maintenance Duty cannot be
  fulfilled. It is an ongoing snapshot requirement, not an interval with an unspecified start.
- Duty form is derived from content. The former `DutyMode`, `Achievement`, `Maintenance`, and
  `dutyMode` vocabulary is removed rather than retained as redundant authored state.
- One Duty node denotes one occurrence. Recurrence, scheduling, persistence, and reset are not
  evaluator semantics.
- `dutyStatus` and `promiseStatus` return `StatusResult`; causal errors produce
  `IndeterminateStatus`, not a fifth ontology state. S2-C3 subsequently confines Duty-status
  decision sensitivity to a Privilege that owns the Duty as a prerequisite.
- `EvaluationResult` carries separate immutable Duty- and Promise-status maps. Promise status does
  not affect access resolution, but its causal errors remain observable in diagnostics.
- Status environments bind the Duty/Promise agent and optional asset directly. They do not invent
  a null Request; `request.*` is invalid during status evaluation. This closes SEM-11.
- A promised state is a snapshot assessment and may change on a later snapshot. Only an accepted
  Maintenance Duty with a finite window represents completion of a maintenance period. The exact
  acceptance transformation remains S2-C4.

### Boundary

S2-C2 does not decide how Duties attach to access grants or whether they are prerequisite,
concurrent, post-use, or independent (`S2-C3`). It also does not complete Promise-to-Duty
materialization or suretyship (`S2-C4`).

### Validation

- Core ontology and shapes parsed successfully (`505` ontology triples; `571` shape triples).
- Full use-case corpus: `PASS 52 · WARN 0 · FAIL 0`.
- `conformance/vectors/duty-status.md` records Achievement boundaries, Maintenance coverage,
  Promise projection, and resolver outcome-sensitivity.

---

## S2-C3 — Duty attachment and decision interaction

**Resolved:** 2026-07-31 · **Scope:** core ontology, SHACL, model, semantics, ODRL mapping,
architecture, Primer, and conformance · **Tags:** [VER] [GEN] [COV]

### Decision

- `rl2:prerequisiteDuty` is the only core Duty-to-Privilege attachment. It corresponds to
  `odrl:duty` on an ODRL Permission.
- A prerequisite Duty is referenced by one or more Privileges and is not also a top-level Policy
  clause. Multiple prerequisites on one Privilege are conjunctive; one shared Duty has one status
  result and can be fulfilled once for every owner. An independent Duty remains a
  top-level Policy clause and has no access-decision effect.
- A prerequisite with a false applicability condition is not required. When applicable, only
  `Known(Fulfilled)` satisfies it. Pending, Active, or Violated disables only the owning
  Privilege; an outcome-sensitive status error makes that Privilege indeterminate.
- Duty atoms and statuses remain observable in `EvaluationResult`, but the access resolver reads
  only Privilege and Prohibition atoms. The public signature is consequently
  `resolveDecision(envelope,strategy)`; the former global active/violated-Duty flags are removed.
- Core `Decision` is `Permit | Deny | NotApplicable | Indeterminate`. Concurrent and post-use
  attachment, scheduling, Requirements, and `PermitWithObligations` are companion-protocol
  concerns. Core may express the underlying independent Achievement or Maintenance Duty but does
  not claim that evaluating a request creates it.

### Rationale and migration

ODRL 2.2 already specifies Permission `duty` as a precondition, permits one Duty to be shared by
several Permissions and fulfilled once, and specifies Policy `obligation` as an
independent Duty. RL2 preserves that distinction rather than adding a four-value phase field.
This closes the concrete C3-4 defect: a violated unrelated Duty can no longer deny an arbitrary
request. It also avoids embedding scheduling and enforcement protocol into the language core.

The ODRL translation is structural: Permission `duty` becomes `prerequisiteDuty`; Policy
`obligation` becomes an independent `clause`. `consequence` and `remedy` remain separate migration
decisions rather than being guessed as phases.

### Validation

- `conformance/vectors/duty-attachment.md` records prerequisite, independence, locality, and
  conflict outcomes.
- Protected vocabulary/SHACL changes add the relation and reject dual-role or ownerless
  prerequisite Duties while permitting ODRL-compatible sharing.
- Core ontology and shapes parse independently (`510` ontology triples; `593` shape triples).
- Full use-case corpus: `PASS 52 · WARN 0 · FAIL 0`.
- Per-fence validation of the eight touched specification, explanatory, and vector documents:
  `PASS 3 · WARN 0 · FAIL 0 · SKIP 5` (the skipped documents contain no Turtle fences).

---

## S2-C4 — pure Offer acceptance and materialization

**Resolved:** 2026-07-31 · **Scope:** model, semantics, ontology annotations, architecture,
Primer, ODRL mapping, use cases, and conformance · **Tags:** [VER] [GEN] [COV]

### Decision

- `materialize(Offer,Acceptance)` is a pure total function returning either one complete
  Agreement plus a source-clause map or a canonical non-empty set of materialization errors.
- Acceptance is a semantic value, not an event. It supplies the Agreement identifier, grantor,
  grantee, injective output identifiers, optional missing-object bindings, and optional
  per-Promise Duty windows. There is no implicit fresh-name operation.
- A promised action becomes an Achievement Duty; a promised state becomes a Maintenance Duty.
  The generated Duty has `subject=promisor` and `counterparty=promisee`; its one generated Claim
  has the reverse roles and an authored Claim→Duty `correlativeTo` link.
- General `promisedDuty` suretyship is rejected with `UnsupportedPromiseContent`. Its Promise
  status remains defined, but neither current Duty form can represent the accepted second-order
  obligation without inventing an action or changing Maintenance semantics.
- All policy-local Norms, including non-clause attached Duties, receive Agreement-local identity
  while retaining their placement. Internal Norm references are rewritten; external references
  remain external.
  Core `promiseStateOperand` queries become Duty `obligationStateOperand` queries; Promise-specific
  queries with no Duty equivalent are rejected.
- An Offer is not operative: its clauses contribute no atoms to `Out` before acceptance. Status
  functions may still report Promise and referenced Duty statuses for inspection.
- Materialization reads no WorldSnapshot, emits no effect, and specifies no messaging,
  persistence, Case, Requirement, or remedial-generation behavior.

### Rationale

Making identity allocation part of Acceptance preserves determinism while keeping global IRI
allocation outside the language. Rejection of unsupported suretyship preserves the S2-C2 Duty
algebra and totality; silent approximation would assign a materially different obligation.
Suppressing Offer atoms closes the pre-acceptance authorization hole in which a proposed
Privilege could otherwise contribute a permit.

### Conformance

- `conformance/vectors/offer-materialization.md` defines positive, negative, determinism, and
  locality vectors.
- `conformance/usecases/sla-credit-clause.md` is the canonical promised-state example and no
  longer invents an Achievement action for maintenance content.
- Core ontology and shapes parse independently (`510` ontology triples; `593` shape triples).
- Full use-case corpus: `PASS 52 · WARN 0 · FAIL 0`.
- Per-fence validation of the nine touched specification, explanatory, use-case, and vector
  documents: `PASS 3 · WARN 0 · FAIL 0 · SKIP 6` (the skipped files contain no Turtle fences).

### Post-review tightening

The follow-up review found boundary ambiguities without reopening the transformation's core
shape. The final disposition was:

- `localNorms(O)` is exactly the Offer's top-level Norm clauses plus prerequisite Duties attached
  to its top-level Privileges. Other Norm-valued properties are references, not ownership.
- Promise-valued targets are transformation-local sibling references within one Offer. A
  cross-policy Promise query is structurally invalid.
- An Offer-level condition is proposed Agreement applicability; offer validity and authorization
  to accept remain outside core.
- Object binding is uniform for action and state Promises. Accepted Duty windows must be valid
  finite intervals and otherwise yield `InvalidDutyWindow`.
- Explicit identity maps, generated Claims, unsupported-operand rejection, and status reporting
  over every reachable Duty were retained. General Claim derivation remains a separate
  Hohfeld/canonicality question; diagnostic unification and an Acceptance conformance class remain
  with S2-M1 and S2-T1 respectively.
- Use cases 8, 11, and 26 were rewritten to the pure Offer→Acceptance→Agreement pattern. Use Case
  50 was preserved under `future/protocol/usecases/` rather than kept as core conformance.

PROM-4 is resolved: `rl2:promisorOperand` exists in core. Materialization intentionally rejects
it because an Agreement has no Promise and core defines no corresponding authored-Norm-subject
operand.

Final validation: core parse `510/595` ontology/shape triples; active corpus `PASS 51 · WARN 0 ·
FAIL 0 · SKIP 1`; relocated future scenario `PASS 1`; touched active-document fences `PASS 7 ·
WARN 0 · FAIL 0 · SKIP 6`. A negative cross-policy Promise fixture produced the required
`PromiseTargetLocalityShape` violation, while an object-less action Promise Offer passed. The
validation harness now treats pyshacl textual `Validation Failure` results as failures rather than
miscounting them as zero violations. The local Markdown-link check found zero broken links.

---

## Corrections to the source reviews

Grounding the reviews against the current files surfaced several stale or incorrect claims. Recorded here so we don't act on them:

- **"`RL2_Semantics.md` returns empty / no formal semantics exists."** (critique 1) — Artifact of a web fetch. The document is ~1600 lines and defines denotational + operational semantics.
- **"Conflict resolution `resolveDecision` is undefined."** (fix §4.2, §13 Modeler) — It is defined at `RL2_Semantics.md:1240` (parameterized by strategy + priorities, with explicit ambiguity error on unbroken ties).
- **"Power exercise semantics missing."** (fix §13 Modeler) — Power denotation and `ExercisePower` state transition are defined at `RL2_Semantics.md:738`.
- **"Promise→Duty generation cut off mid-definition."** (fix §13) — The remedial generation rule exists at `RL2_Semantics.md:1007`. What is genuinely open is `restoreAction` (see SEM-1).
- **"Technology stack undecided (Why3 vs Dafny vs Go)."** (fix §2, §12, P0.4) — Decided: **Dafny → Go**, committed (`de473f5`). The entire fix §12 deliberation is historical. **Superseded 2026-07-29 (SCOPE-1):** the Dafny→Go mechanization plan itself was later dropped — the project stops at specification, with no implementation track at all.
- **"Prohibition can be expressed two ways (`prohibitedAction` vs `dutyAction NotDelete`)."** (critique 3) — There is no `dutyAction`/`NotDelete` idiom in core. `rl2:prohibitedAction` is already `rdfs:subPropertyOf rl2:action` (`rl2.ttl:309`). The real question (CANON-3) is class modeling, not two competing idioms.
- **"Counterparty can appear at multiple container levels."** (critique 3) — `rl2:counterparty` has domain `rl2:Norm` only; containers have no counterparty property, so container-level inheritance is not even expressible. The real question (CANON-4) is redundancy among `counterparty` / `claimHolder` / `claimAgainst` / `subject`.

---


## Remediation Roadmap — deep sweep (2026-07-26)

Source: the current `fix.md` / `fix-codex-original.md` (~60 findings; both are interim scratch, to be cross-checked against this file and then deleted). This roadmap is the **execution order**; the bands below remain the **per-issue tracker**. The review classified findings by *remediation effort* (Class 1 mechanical, Class 2 bounded decision, Class 3 architectural stopper), but its own closing advice — adopted here — is to **drive by semantic dependency, not by class number**: take the cheap independent Class-1 wins immediately, front-load the foundational Class-2 decisions that bound the redesign, then work the Class-3 stoppers in dependency order, with the remaining Class-2 volume work and dependent Class-1 editorial consolidation trailing.

**Dependency spine** (Class-3 roots and what they unblock):

```text
WP-2  S2 result/error algebra ─┬─ E1 external context (WP-5)
                              ├─ I1 IR type system   (WP-5)
                              └─ P2 replay diagnostics (WP-6)
WP-2  C5 canonical AST ────────┬─ C6b Claim/correlative
                              ├─ I1 source/IR correspondence (WP-5)
                              └─ O2c lossless ODRL import     (WP-7)
WP-3  S6 events + S5 scoped state ─┬─ S4 temporal lifecycle (WP-4)
                                  ├─ I4 effect application  (WP-5)
                                  └─ P1/P3/P4 protocol      (WP-6)
WP-4  S7 conflict/provenance ──────┬─ ODRL conflict compat (WP-7)
                                  └─ final decision + duty attachment
```

**Reconciliations — where `fix.md` re-opens an already-made decision** (do not act blindly):

- **C1** (`targetNorm` RDFS range makes a targeted Promise a Norm). Already handled deliberately: **PROM-7/PROM-1** kept `rdfs:range rl2:Norm` on purpose (it is the RDFS range-entailment *auto-typing crutch* the terse-fence corpus depends on) and did the real widening in SHACL via `sh:or (Norm Promise)`. fix.md's "remove the range" recommendation would regress `RL2_Primer.md`/`RL2_Vocabulary.md`. **Residual actually open:** add disjointness / `sh:not` making the Promise≠Norm distinction *testable*, and decide the `StatefulClause`-vs-explicit-typing question as part of **C5** (canonical AST) — where the entailment crutch goes away anyway. Folded into WP-1/WP-2, not a fresh C1.
- **I2/I3** (typed-AST-first; runtime solver-free). Largely **already the adopted stance** — `RL2_IR.md`/SEM-4 chose a hybrid (deontic tree-walk + condition bytecode) and §8.3 already keeps entailment/closure at ingestion. WP-1 ratifies + records the "measure before committing to bytecode" caveat, not a redesign. **Superseded 2026-07-29 (SCOPE-1):** the bytecode lowering was dropped outright rather than benchmarked — `RL2_IR.md` now specifies a single-lowering AST with direct interpretation (`evalCondition`), no condition bytecode at all.
- **E1** ≈ **SEM-13**, already specified in detail (ContextManifest, out-of-band baseline, in-band as extension). WP-5 *executes* SEM-13, it is not a new finding.
- **C3/C4** partly resolved: **CONS-6** capped constraint-shape multiplicity; **CONS-1** collapsed fulfillment-evidence to `sh:or`. Residual = node-shape `sh:maxCount 1` on subject/action/object/promisor/claim-party/etc. (C3) and the `rl2p:ContextAssertion` `contextValue`/`contextValueRef` exclusivity (C4) — small, folded into WP-1.
- Several **D-items** are done (DOC-*); **D3/D4/D5** (claim-downgrade, reversed determinism formulas, stale refs) are genuinely open and sit in WP-0/WP-8.

---

### WP-0 — Immediate Class-1 corrections (independent, parallel-safe)

**Depends on:** nothing · **Status:** ✅ Resolved 2026-07-26 · Cheap, mechanical/editorial fixes that make currently-false claims true; no new semantic decision.

**Done this pass** (full corpus + per-fence spec/profile docs revalidated clean throughout — `PASS 0 · WARN-ONLY 52 · FAIL 0 · SKIP 1` whole-file; per-fence docs all `FAIL 0`):

- **V1** — `tools/validate.py` now renames the warning-only glyph from `✓` to `⚠`, reports SHACL conformance (`no sh:Violation`) separately from the warning-free project gate, and adds a `--strict` flag (warning-only files → exit 1) for release/conformance CI. The summary now reads e.g. `SHACL conformance: 52/52 · warning-free gate: 0/52`, surfacing the baseline warning honestly. **Deferred (needs `AGENTS.md` §7 sign-off):** exempting the core `rl2p:requirementFulfilled` operand from `OperandResolutionRecommendationShape` in `rl2p-shacl.ttl` so the warning-free gate can reach 52/52 — a SHACL edit, folded into WP-1's C1/C3/C4 SHACL bundle.
- **O4 / C6a(wording)** — `RL2_ODRL_Comparison.md`: "Hohfeldian octagon (8 positions)" → "seven modeled positions: six positive Hohfeldian positions + Prohibition; No-Right/Disability derived"; two more "octagon" mentions reworded; the "ODRL lacks formal semantics" claim (contradicted by the doc's own W3C-CG citation) softened to "specifies processing descriptively in prose … a non-normative Formal Semantics draft exists"; the "automated compliance/audit ✓" row downgraded to "Partial" with the missing audit machinery named. `RL2_Primer.md:363` "eight fundamental legal concepts" → the accurate six-plus-Prohibition framing.
- **O2a** — `RL2_Primer.md` ODRL-mapping table: nonexistent `rl2:refines` replaced with "*(no RL2-core equivalent)*".
- **C8** — `RL2_Architecture.md` "`rl2:Promise`, in a Set/Offer" → "in an Offer" (matches SHACL).
- **D3** — "semantic superset" downgraded to a design goal in `README.md`, `RL2_Primer.md`, `FAQ/RL2_FAQ.md` (each now noting the compatibility inventory is open work); the `RL2 ≈ LTL_F + Deontic + …` characterization in `RL2_Architecture.md` recast as a "guarded finite-state transition system" with LTL as an explicit *design goal, not yet proved*, plus the expressive-comparison table row.
- **D4** — `RL2_Architecture.md` determinism formulas replaced: the false converse (`evaluate(…,ctx₁)=evaluate(…,ctx₂) ⟹ ctx₁=ctx₂`) removed, restated as same-input determinism; the compile-injectivity relabeled as the (separate) canonicalization property.
- **D5** — `RL2_IR.md` "51-use-case corpus" → "52".
- **O5** — new "Prior Art and Related ODRL Work" section in `RL2_ODRL_Comparison.md` (disposition table over ODRL Formal Semantics, atomization, FORCE, evaluator test suite, ODRL-PAP/Rego, consistency checking, temporal & data-space/VC profiles, with stable links); References renumbered.
- **R1a** — `profiles/README.md`: added missing `@prefix xsd:`; the illustrative Privilege fence made self-contained (subject/action/object + a defined operand) so it validates per-fence; "Why3/Lean" → "Dafny→Go"; the "MUST go through declared operands" overstatement softened to a recommendation (matching the SHACL warning-not-violation reality).
- **S3** — `RL2_Semantics.md` `Env` redefined from the 4-tuple `Agent × Asset × State × ExternalContext` to a named five-field record `(Request, Agent, Asset, Σ, Context)` matching the `deref` roots one-to-one; `mkEnv` now retains the full `Request` so `request.*` paths resolve; `rl2:currentAgent = Request.requestingAgent` stated. (Prior grep confirmed no stray `requestor` usage.)

**Judgment call left for a later pass:** D5's "remove volatile line-count/KB metrics" was *not* applied — the user's recent DOC-4 work deliberately added a Quantitative Comparison section, so stripping incidental line counts now would conflict; revisit alongside that section.

Original item list retained below for reference.

- **V1** — validation reporting: report `sh:conforms` separately from the project gate, rename warning-only "clean/conformant" success, fix-or-exempt the `OperandResolutionRecommendationShape` operand warning, add a fail-on-warning CI mode. Touches `tools/validate.py` + Band 3.5 baseline note. *(new)*
- **S3** — one named `Env` record with `request/agent/asset/state/context`; align every signature; state `rl2:currentAgent = rl2p:requestingAgent`. *(new; mechanical alignment)*
- **C8** — Architecture "Promise may occur in Set" → Offer only (matches SHACL). *(new, small)*
- **O4 / C6a(wording)** — ODRL comparison factual errors: "octagon"/eight→**six positive Hohfeldian positions + Prohibition**; acknowledge ODRL's published formal-semantics work; drop the "SHACL+enum = audit" overstatement. *(new; distinct from DOC-4's already-done metrics work)*
- **O2a / O5** — remove the nonexistent `odrl:relation → rl2:refines` mapping (`RL2_Primer.md:1487`); add the prior-art / disposition appendix with stable citations. *(new)*
- **X1** — recast §12 product comparison as coverage / missing / intended-boundary. *(new)*
- **R1a** — repair profile-example prefixes and per-fence-validate them; remove stale Why3/Lean toolchain prose from `profiles/README.md`. *(new; overlaps §14)*
- **D3 / D4 / D5** — downgrade "full/total/polynomial/canonical/semantic superset" to design goals/proof obligations; replace the two reversed determinism formulas (`RL2_Architecture.md:595-596`) and the unproven `LTL_F + Deontic + Finite Obligation Automata` claim; fix stale section refs, 51→52, remove line/KB metrics, normalize terminology. *(extends Band 5 DOC)*

### WP-1 — Foundational Class-2 decisions (bound the redesign)

**Depends on:** WP-0 (mechanical Env/terminology cleanup helps) · **Status:** ✅ Resolved 2026-07-26 (§7 sign-off granted for all six protected-file items) · Bounded decisions with a recommended resolution; they set the boundary conditions the Class-3 stoppers build on.

**Done this pass (validated: corpus `PASS 52 · WARN-ONLY 0 · FAIL 0 · SKIP 1`, warning-free gate 52/52; all touched spec docs FAIL 0):**

- **S1** — `RL2_Semantics.md` §Monotonicity restated over `U ⊆ U'` for a **fixed immutable environment**; the false `Env ⊆ Env' ⇒ Out ⊆ Out'` is now explicitly retracted with the anti-monotone witnesses (`Not`, `neq`, `isNoneOf`, upper time bounds). `Out` declared a **set** (dedup by canonical identity; codomain `℘(NormativeAtoms)`). Order-independence of derivation kept as the real property. Swept the false "adding facts never removes conclusions" claim out of `RL2_Architecture.md:88` and `RL2_References.md` too.
- **C2 / PROM-4** — chose **option A**: defined `rl2:promiseStateOperand` and `rl2:promisorOperand` as **core operands** (rl2.ttl) with dedicated resolver branches (`PromiseState(targetNorm,Σ)` / `Σ.Promises[targetNorm].promisor`) in `RL2_Semantics.md §resolve`, symmetric with the two Norm-state operands; added `rl2:PromiseStateConstraintShape` (Promise-valued targetNorm required) and exempted both from `OperandResolutionRecommendationShape`; documented in `RL2_Vocabulary.md`. Profiles may still declare their own resolutionPath operands.
- **C6a / SEM-3 / HOHF-1** — `RL2_Semantics.md §Hohfeldian Correlatives` now states "six positive positions + Prohibition; No-Claim/Disability derived, non-reified"; removed the last `Power→Permit` / `Immunity→Deny` decision mappings (`RL2_Protocol.md`, `RL2_Architecture.md`) → Power = `Effect(ExercisePower)`, Immunity = precondition blocking ExercisePower.
- **C7 / EXPR-4** — `rl2:AssetCollection rdfs:subClassOf rl2:Asset` (a collection is itself a valid target and can nest); membership bound to the **evaluation snapshot**; **direct membership only** in core (transitive flattening = profile/derived). Updated rl2.ttl (`AssetCollection`, `member`), `RL2_Semantics.md §Request Matching`, `RL2_Vocabulary.md`.
- **S8a / SEM-8** — `rl2:after` and opaque `resolutionFunction` explicitly scoped **outside the specified evaluator core** (annotated in rl2.ttl; `evalIR` MUST NOT depend on them); path/condition/collection/universe bounds recast as **conformance parameters** (`MaxPathDepth`, `MaxConditionDepth`, `MaxCollectionSize`, `MaxPolicyUniverse`) — MUST-enforce, not `MAY`. Updated `RL2_Semantics.md`, `RL2_Vocabulary.md`.
- **O3** — new profile-declaration machinery: `rl2:Profile` + `rl2:profileVersion` (SemVer) + `rl2:requiresProfile`; **fail-closed unknown-profile rule** and **same-major SemVer negotiation** specified in `RL2_Semantics.md §Profile Resolution` and `profiles/README.md`; structural `ProfileShape`/`RequiresProfileShape` SHACL added. **Namespace move off `rl2.example` stays deferred** (OPEN-1/2, pre-publication) as agreed.
- **I2 / I3** (ratified) — recorded in `RL2_IR.md §2`: typed-AST evaluator first (bytecode only on a shown benchmark/portability need); runtime stays solver-free (entailment/closure at ingestion). **Superseded 2026-07-29 (SCOPE-1):** bytecode dropped outright (no benchmark gate) — see SCOPE-1 in § Resolved.
- **C1 residual / C3 / C4 / V1** — C1: `PromiseNotConcreteNormShape` makes Promise≠Norm testable at the *concrete-subclass* level without regressing the `targetNorm` RDFS crutch (full `owl:disjointWith` deferred to C5). C3: `sh:maxCount 1` on all singular norm fields (subject/action/object/counterparty/affectsNorm/exposedTo/immuneFrom/promisor/promisee) — this surfaced and fixed a latent IRI-reuse bug (`ex:accessPrivilege` defined twice in `compliance-attestation.md`). C4: `ContextAssertion` value/ref exclusivity via `sh:xone`. V1: exempted `rl2p:requirementFulfilled` from the operand-recommendation warning, then cleared the two remaining example-operand advisories (`workPeriodOperand`, `processorComplianceAssertionOperand`) → **warning-free gate reaches a true 52/52**.

**Deferred out of WP-1 (as agreed):** namespace move off `rl2.example` (OPEN-1/2); full `owl:disjointWith(Norm, Promise)` → C5/WP-2 (removes the entailment crutch). Original decision text retained below for traceability.

Each needed `AGENTS.md` §7 sign-off before ontology/SHACL edits (granted 2026-07-26).

- **S1** — restate the monotonicity theorem over `U ⊆ U'` for a **fixed immutable environment** (the false `Env ⊆ Env' ⇒ Out ⊆ Out'` is disproved by `Not(EventConstraint)`, `neq`, `isNoneOf`, upper time bounds); drop all proof/perf steps that relied on env-monotonicity; decide set-vs-bag for `Out`. *(new)*
- **C2** — decide `promiseStateOperand`: define one typed core operand + resolver branch, **or** remove every core reference and mark it profile-only/non-portable. Relates **PROM-4** (`promisorOperand` symmetry). *(new)*
- **C6a / SEM-3 / HOHF-1** — declare "six positive Hohfeldian positions + Prohibition; absence positions (No-Claim, Disability) derived/non-reified"; remove Power→Permit / Immunity→Deny decision mappings. *(sharpens SEM-3, HOHF-1, C6; CONS-4 already fixed the Vocabulary mapping)*
- **C7 / EXPR-4** — decide whether `AssetCollection` is itself a target `Asset` (declare the subclass) or compiles to member-matching; bind membership to the evaluation snapshot; define direct-vs-transitive closure. *(sharpens EXPR-4)*
- **S8a / SEM-8** — remove `rl2:after` and opaque `resolutionFunction`s from the *specified evaluator core* until precise bounded semantics exist; make depth/size/path bounds **conformance parameters**, not `MAY`. *(sharpens SEM-8)*
- **O3 / OPEN-1/2 / R1b** — profile-declaration property + "reject unknown required profile" rule + version negotiation + move off the `rl2.example` namespace before publication; add profile-specific SHACL. *(sharpens OPEN-1/2, §14)*
- **I2 / I3** (ratify only) — record "typed-AST evaluator first; bytecode only if a benchmark/portability need is shown" and "runtime stays solver-free; entailment/closure at ingestion". *(ratifies SEM-4 / §8.3)*
- **C1 residual / C3 / C4** (small) — add Promise≠Norm `sh:not` testability; node-shape `sh:maxCount 1` on remaining singular fields; `ContextAssertion` value/ref exclusivity via `sh:xone`. *(folds C1/C3/C4 residue; CONS-1/6 did the rest)*

### WP-2 — Result/error algebra + canonical AST (Class-3 roots)

**Depends on:** WP-1 · **Status:** ✅ Resolved 2026-07-26 (§7 sign-off; two forks decided by the user: C5 = AST-level disjointness keeping the RDF crutch, C6b = Claim derived from one Duty) · The two foundations everything downstream needs.

> **Integration follow-up (fix.md 2026-07-29):** **C3-1** finds S2's algebra not yet threaded through `resolve`/`apply`/`Out`/IR; **C3-8** finds the C5 projection still incomplete on entailment/blank-node/dedup/fresh-IDs; **C3-5** finds materialization/crystallization can't execute as specified. **C3-1 ✅ resolved 2026-07-31** (below); C3-5/C3-8 remain open — see § Remediation Roadmap — integration sweep (2026-07-29) in `issues.md`.

**C3-1 — ✅ Resolved 2026-07-31.** Threaded S2's causal-error algebra through every place it was still bypassed, and consolidated the duplicated `Out`/`deriveNorms` vs. Big-Step `Eval` formalizations the review flagged as two competing definitions of the same computation:

- **`Value`/`EvalValue`/`ConditionResult` unified.** `RL2_Semantics.md`'s `resolve`/`resolveRuntime`/`deref`/`apply` are typed through `EvalValue<Value>`; `RL2_IR.md §5` mirrors them without `VBottom`. `EvalValue<T> = Ok | Err(EvalError,note)`, `EvalError = Missing | Invalid | Conflict`, and `ConditionResult(truth,causes)` are concrete datatypes. The Atomic interpreter now passes its state target into `resolve` instead of dropping it.
- **Canonical causal-error channel.** `ConditionResult.causes` contains only determining errors under the Kleene masking rules. `EvalError` contains the structural `(constructor,ErrorKey)` identity; optional diagnostic text is outside that identity on `EvalValue.Err`, so native set equality is commutative/associative/idempotent without custom hashing. Comparison-error keys include both operand types. `StateTarget`/`StateTargetRef` tags Norm versus Promise targets, closing the Promise-valued `rl2:targetNorm` type hole.
- **Typed derivation closes the Unknown-collapse bug.** `deriveNorms` folds `effectiveCondition(P,n)` and emits attributed Unknown atoms only for request-matched Privilege, Prohibition, and Duty clauses; Promise and the other Hohfeldian positions remain in their own denotations/lifecycles. `RL2_IR.md` now defines the corresponding `IRAtom` algebra and the complete `derive(ClauseRef,Clause,env)` cases over compiled `effCond`, rather than citing an undefined provenance-free helper.
- **One outcome-sensitive resolver.** C3-1 originally consolidated resolution behind
  `resolveDecision(envelope,Σ',strategy)` with access maxima plus active/violated-Duty flags.
  S2-C3 supersedes only the Duty portion: prerequisite status is now interpreted locally while
  deriving its owning Privilege, independent Duties have no access effect, and the public resolver
  is `resolveDecision(envelope,strategy)`. The finite choice fold and `O(n³)` access-summary bound
  remain unchanged.
- **Duty `Violated` classification moved off the stale pre-transition atom.** `Out`'s envelope no longer emits `violated(d,P)` (it read free `Σ` and went stale the instant `updateDutyStates` ran). Both `Eval` and `evalIR` now bind `Σ' = updateDutyStates(...)`/`applyEffects(...)` before resolution, and `resolveDecision`'s internal partition classifies attributed duties (`obligate(d,P) ∈ envelope`) as Active/Violated by reading `Σ'.ObligationState(d)` directly. `duties(envelope, Σ')` (both docs) is defined as `{ d | obligate(d,P) ∈ envelope, Σ'.ObligationState(d) ∈ {Pending, Active} }` — the returned `DutySet` reflects post-transition state, not a stale snapshot. `RL2_IR.md`'s `dutyFx` needed a companion `obligated(envelope) = { d | obligate(d,P) ∈ envelope }` (no Σ filter) for the pre-`Σ'` transition-effect computation, since the two uses of the old ambiguous `duties(envelope)` name meant genuinely different sets.
- **`RL2_Architecture.md`** pipeline diagram's derivation step now lists `indeterminate(n, P, causes)` alongside `{permit, forbid, obligate}`.
- **Protocol boundary kept explicit.** The internal envelope retains causes, while the current Protocol carries only the `Indeterminate` decision. Structured causal projection is not claimed as C3-1 work; it remains C3-6/D10.
- Unblocks **E2**, **D1**, and **D2** (below).

Touched: RL2_Semantics.md, RL2_IR.md, RL2_Architecture.md, issues.md.

**Done this pass (validated: corpus `PASS 52 · WARN-ONLY 0 · FAIL 0 · SKIP 1`; `--strict` exits 0; all touched spec docs FAIL 0). The finite-summary resolver was additionally checked against exhaustive Unknown truth assignments over 2,916 bounded priority/specificity/duty models.**

- **S2** — total result/truth algebra defined in `RL2_Semantics.md §Result and Truth Algebra`: `EvalValue<T> = Ok | Err(EvalError,note)` for operand resolution and `ConditionResult(Truth,causes)` for conditions; `apply` lifts operand errors to `Unknown`; And/Or/Not/Xone use Kleene strong three-valued logic with causal masking. A matched access norm with `Unknown` effective condition contributes an attributed `indeterminate(norm,policy,causes)` atom. `resolveDecision` returns `Indeterminate` exactly when activating such an atom can change the priority-and-strategy result; no verdict is declared conclusive merely because it is Deny. `Indeterminate → Deny` remains an enforcement-adapter policy. `RL2_IR.md` mirrors the algebra directly without `VBottom` or an opcode layer.
- **C5** — canonical-form invariant **scoped to the normalized AST projection**, not raw RDF (`RL2_Architecture.md §Canonical Form` rewritten; `RL2_IR.md §10` corrected). Withdrew the false "two structurally-different graphs must differ semantically / equivalence reduces to graph comparison with no normalizer" claim. Specified the `π : RDF → AST` projection (entailment regime, `omitted condition → True`, cardinality expansion, blank-node elimination via stable IDs, operand ordering/dedup, annotation stripping, derived correlatives, unsupported-extension rejection). **Norm≠Promise disjointness is a canonical-AST axiom** — documented as `owl:disjointWith` at the semantic/AST layer while the RDF `targetNorm` crutch (PROM-7) is kept below π (chosen fork: zero fence churn); no raw `owl:disjointWith` triple added, so no latent RDF inconsistency.
- **C6b** — `Claim` is a **derived projection of exactly one Duty**: `ClaimShape` now requires exactly one `correlativeTo` → `rl2:Duty`, forbids authored `action`/`object`/`condition` on the Claim (`sh:maxCount 0`), and adds a SPARQL party-role-alignment check (`Duty.subject = Claim.counterparty`, `Duty.counterparty = Claim.subject`). `RL2_Semantics.md §Claim Denotation and Content Derivation` rewritten: content derived from the Duty, claim `Held`/`Indeterminate`/`Inactive` on the Duty condition's `Truth` (S2-consistent). rl2.ttl `Claim`/`correlativeTo` comments updated; `RL2_Vocabulary.md` Claim entry + example updated. **Per the user's mid-pass guidance, the shape was kept strict and the one non-conforming example fixed** (scaffolded the Vocabulary `bobClaim` fence with an in-fence aligned `ex:aliceDuty`); all existing corpus Claims already conformed.

**Deferred to later WPs (unchanged):** full guard-predicate/remedy semantics (F2/SEM-10) → WP-4; the S2 fixtures for missing/wrong-type/multi-valued/conflicting operands can land with WP-5 (E1) test work.

- **S2 (original work item; now resolved above)** — define a total result/truth algebra, Kleene connectives with causal masking, and `condition-error → attributed Unknown`; use the same internal algebra in Semantics and IR. Structured Protocol projection was later separated as C3-6/D10, and the Go implementation track was dropped by SCOPE-1.
- **C5** — specify the normative `RDF → canonical AST` projection: entailment regime, semantic defaults (omitted condition → `True`), cardinality expansion, blank-node handling, operand ordering/dedup, annotation stripping, unsupported-extension rejection, stable IDs; scope canonicality to the *normalized projection*, not raw RDF graphs; drop the "graph comparison proves semantic equivalence" claim. *(new; blocks C6b, I1, O2c)*
- **C6b** — Claim content: make it a required derived projection of a Duty (derive action/object/condition) **or** define its content directly; validate type-pairing and party-role alignment; make correlatives derived *or* authored, not both. *(depends on C5; sharpens CANON-4)*

### WP-3 — State identity/scope + event model (Class-3 roots)

**Depends on:** WP-2 · **Status:** ✅ Resolved — all 3 steps done. **Step 3a (S6) ✅ Resolved 2026-07-26**; **Step 3b (S5) ✅ Resolved 2026-07-26**; **Step 3c (F3/P3) ✅ Resolved 2026-07-29**.

> **Integration follow-up (fix.md 2026-07-29):** **C3-3** finds `EventSet` still picks an arbitrary element (order-dependent sequence), `TimeAdvanced`/`MetadataChanged` mutate scalars without appending (not replayable), and witness derivation still ignores subject/Case-scope/activation-window (D4). See § Remediation Roadmap — integration sweep (2026-07-29).

Dependency order S6 → S5 → F3/P3 (matches fix.md's own note).

- **S6 — ✅ Resolved 2026-07-26 (Step 3a; §7 sign-off; fork decided: event kinds = individuals + `eventKindIncludedIn`, not classes).** Validated corpus `PASS 52 · WARN-ONLY 0 · FAIL 0 · SKIP 1`. Done:
  - **Append-only witness log.** `RL2_Semantics.md` Σ redesigned: `Events : EventLog` is the authoritative append-only log with an `EventRecord (id, eventSequence, eventTime, kind, operationalAgent, eventAction, eventObject, case, provenance)`. `Σ.Performed` (Boolean) and `Σ.DutyPerformer` (map) **removed as stored fields** — both are now **derived views** over `Σ.Events` (new §Witness Derivation). `processEvent` **appends** every witness event (incl. `ActionPerformed`) with a fresh `eventSequence`; nothing sets a Boolean. D-FULFILL no longer stores the performer.
  - **Deterministic tie-breaking.** Event selection is `maxByⁱ` over the **total** `(eventTime, eventSequence)` lexicographic order — kills the old `maxBy(eventTime)` tie nondeterminism. `DutyPerformer(d,Σ)` reads the performer from the highest-sequence witnessing event.
  - **One event-kind subsumption model.** New `rl2:eventKindIncludedIn` (transitive, individual-level — the `rl2:includedIn` counterpart for events); `typeMatches` uses `eventKindIncludedIn*`, no `rdfs:subClassOf`, no OWL class reasoning (I3).
  - **Ontology/SHACL/Vocab.** rl2.ttl: `eventSequence`, `eventAction`, `eventObject`, `eventKindIncludedIn` + Event class comment. rl2-shacl.ttl `EventShape`: optional `maxCount 1` guards for the new fields (lenient — kind templates carry none, zero corpus churn). `RL2_Vocabulary.md` Event entry + property table updated.
- **S5 — ✅ Resolved 2026-07-26 (Step 3b; §7 sign-off; design settled in discussion — the 7-tuple collapses to a two-tier class/instance model bounded at the Offer).** Validated corpus `PASS 52 · WARN-ONLY 0 · FAIL 0 · SKIP 1`, `--strict` exits 0; Semantics per-fence FAIL 0; GlobalLeftOperandShape negative-tested (fires). Done:
  - **Two scope tiers, no more — class/instance (OO analogy).** `RL2_Semantics.md` new §State Scope, Identity, and Concurrency: **Offer = class** (immutable template, stateless, accepted many times); **Agreement = instance** (one per acceptance); `materialize()` = the constructor. **Instance variables (default, ~all cases)** = per-Agreement state, already delivered by `materialize()`'s fresh-IRI-per-clause (Σ stays bare-IRI-keyed; zero new machinery, zero corpus churn). **Class variables (rare, explicit)** = state shared across all live Agreements of one Offer, read via the new `global.*` root. **The Offer is the ceiling** — no tenant/cross-Offer tier (explicit non-goal). This is the shared-strong-state vs case-local distinction fix.md asked for.
  - **Shared limits are derived, not stored.** `activeAgreements(Offer, Σ) = { A | A prov:wasDerivedFrom Offer ∧ active(A,Σ) }` (the `wasDerivedFrom` link already exists from PROM-7 materialize; `active()` lifecycle → WP-4). A concurrent-seat limit is the read-only aggregate `|activeAgreements(Offer)|` resolved into ResolvedContext — **no shared-counter algebra**. A genuinely *accumulating* pooled counter is **outside the specified evaluator core** (profile + external resolver, same status as an aggregating `resolutionFunction`, S8a).
  - **Versioned snapshot + CAS.** `Snapshot = (Σ, version)`, `evalIR`/`Out` pure over it; `commit(Snapshot_v, effects)` = compare-and-swap on `version`. Admission against `global.*` **MUST** commit serializably; case-local **MAY** use snapshot isolation. Mechanism (locks/storage/retry) is outside the specified evaluator core (I4). Kills the two-evaluators-both-admit race.
  - **Event dup/late-arrival (S6 follow-through).** `processEvent` now idempotent on `e.id` (at-least-once transport safe); late arrivals appended with next `eventSequence`, sort by `(eventTime, eventSequence)`, and **never retroactively change a decision committed against an earlier snapshot version** (replay-stable).
  - **`global.*` operand surface.** Core (rl2.ttl) adds `global.*` to the canonical resolutionPath roots + core deref case (`Env.Context.global`, resolver-injected); rl2-shacl `ResolutionPathRootShape` accepts `global`. Profile (rl2p.ttl) adds `rl2p:GlobalLeftOperand ⊑ rl2:LeftOperand` (Offer-tier, read-only aggregate, outside-core for mutable pools); rl2p-shacl `GlobalLeftOperandShape` requires a `^global\.` path.
  - **Example aligned (fix example, not shape).** `usecases/concurrent-seats.md` (UC16) re-pointed from the ad-hoc `state.License.*` path to `rl2p:GlobalLeftOperand` + `global.*`; reframed as the class-variable/Offer-scope case, contrasted with per-Agreement instance scope (usage-metering.md); Scaling section ties to the CAS/versioned-snapshot rule.
  - Touched: rl2.ttl, rl2p.ttl, rl2-shacl.ttl, rl2p-shacl.ttl, RL2_Semantics.md, usecases/concurrent-seats.md, issues.md.
- **F3 / P3(state) — ✅ Resolved 2026-07-29 (Step 3c; §7 sign-off; design settled via AskUserQuestion — "Explicit state machine + formal projections", i.e. keep `ObligationState`/`PromiseState` as the authoritative stored transition-rule state machines and redefine every other status representation as a *projection* over them, rather than converting to full event-sourced derivation).** Validated corpus `PASS 52 · WARN-ONLY 0 · FAIL 0 · SKIP 1`, `--strict` exits 0; `RL2_Semantics.md` per-fence FAIL 0. Done:
  - **`requirementStatus` as a formal projection (closes F3's duplication gap).** `RL2_Semantics.md` new §Requirement Status Derivation (F3/P3): `RequirementRecord` **no longer carries a stored status field** — `requirementStatus(req, Σ, Env)` is defined as `projectRequirementFromPromise`/`projectObligationState` reads over the *tracked* norm's live `ObligationState`/`PromiseState`, plus a `promiseEffective(p, Env)` guard (mirrors the existing `PolicyApplicable`/`NormActive` pattern) for standalone Promises reached via `rl2:clauseOf`. Same shape as the pre-existing `PromiseState → ObligationState` projection (S6/S3 precedent) — no new mutable store, monotonicity preserved.
  - **`trackedDuty` field (remedial-generation correctness fix).** `RequirementRecord` gained `trackedDuty: Duty?`, distinct from `sourceNorm` (which stays the original imposing Duty/Promise for provenance). The Promise→Duty Generation (Remedial Generation) transition rule now sets `trackedDuty = d` (the newly generated remedial Duty) when a Promise is violated, so `requirementStatus` reads the *remedial* Duty's live state, not the now-permanently-Violated original Promise — this was required to make the rule's own worked example (`ex:remedialReq` showing `requirementStatus rl2:Active` after the source Promise is Violated) actually consistent with the projection formula. `trackedDuty` is Σ-internal only (not RDF-round-tripped, same status as other Σ fields).
  - **`caseStatus` projection — scoped to the duty-fulfillment component.** New §Case Status Derivation defines `Requirements(c,Σ)` (active requirements attached to a Case via its evaluation history), `allFulfilled`/`anyViolated` over their (already-projected) `requirementStatus`, and `pendingOutcome(c,Σ,Env) ∈ {Approved, Denied, CasePending}`. **`Expired`/`Revoked` stay stored/exogenous** — full `CaseEvents` event-sourcing of the *entire* `rl2p:caseStatus` lifecycle (P1) is explicitly deferred to WP-6, since issues.md's own Step-3c scope only names `obligationState`/`promiseState`/`requirementStatus`, not a full Case-lifecycle redesign; this is a narrower, more defensible read of the AskUserQuestion answer than inventing new revocation/expiration semantics beyond what WP-3 asked for.
  - **P3 SHACL checks.** `rl2p-shacl.ttl`: (1) hard `sh:Violation` SPARQL constraint on `RequirementShape` — `sourceNorm` must be a `rl2:clause` of `sourcePolicy` (structural invariant, no severity override, same pattern as `ClaimShape`'s C6b check); (2) new `rl2p:RequirementCaseLinkageShape` (`sh:Warning`, `sh:SPARQLTarget` over Active-status Requirements) — should be reachable via some Case's `evaluationHistory → activeRequirements` (same "should-have" pattern as the pre-existing `RequirementFulfillmentAuditShape`). The hard check required one corpus fix: `usecases/runtime-evaluation.md`'s "Universal Requirement" block was missing `ex:dataUsePolicy rl2:clause ex:someDuty, ex:somePromise` — added. The new Warning check surfaced 3 previously-unlinked illustrative Requirements in the `usecases/*.md` corpus (`claim-counterclaim.md`'s `ex:freshnessRequirement`, `runtime-evaluation.md`'s `ex:dutyReq`/`ex:promiseReq`); each got a minimal `Request`/`EvaluationResult`/`Case` wrapper added so the strict `usecases/*.md` gate stays `WARN-ONLY 0`.
  - **Spec-doc per-fence warnings (accepted, not chased).** The same Warning check also fires on 4 *isolated* single-Requirement illustrations in the reference docs — `RL2_Semantics.md:1444` (`ex:remedialReq`), `RL2_Protocol.md:189,347` (`ex:req1`, shown twice), `RL2_Vocabulary.md:1236` (`ex:paymentReq`) — where a self-contained formal-notation example intentionally omits the surrounding Case/EvaluationResult ceremony. These are the same character as the pre-existing, already-accepted `OperandResolutionRecommendationShape` per-fence warnings in `RL2_Protocol.md`/`RL2_Vocabulary.md` (present before this step; `--per-fence` on spec docs was never a warning-free gate, unlike the strict `usecases/*.md` corpus gate). Left as-is rather than padding formal examples with boilerplate wrapper triples.
  - **`RL2_Protocol.md`.** Both "State Mapping Note" callouts (Requirement Lifecycle, Case State Transitions) rewritten to state that `requirementStatus`/`caseStatus` are not independently asserted, pointing at the new Semantics §§ instead of describing an informal mapping.
  - Touched: RL2_Semantics.md, RL2_Protocol.md, rl2p-shacl.ttl, usecases/runtime-evaluation.md, usecases/claim-counterclaim.md, issues.md.

### WP-4 — Temporal lifecycle + conflict/provenance

**Depends on:** WP-3 · **Status:** ✅ Resolved 2026-07-29 — **S4 (Step 4a)**, **S7 (Step 4b)**, **F2 (Step 4c)** all done (S7/SEM-8 partial — see narrowing below; the two sub-items noted there are tracked, not blocking).

> **Integration follow-up (fix.md 2026-07-29):** **C3-2** finds the Maintenance-duty premises jointly unsatisfiable when one `c` serves as guard, invariant, and deadline source (and Achievement can stay Pending forever if first seen post-deadline); **C3-4** elevates S7's explicitly-deferred "attach duties to their grant" to a stopper (an unrelated violated Duty currently denies any request). See § Remediation Roadmap — integration sweep (2026-07-29).

> **Superseded by S2-C2 (2026-07-31):** the S4 design below is retained as historical rationale,
> but its authored `dutyMode`, extracted deadlines, and stored transition rules are no longer
> active specification. S2-C2 replaces them with structural Duty forms, explicit `dutyWindow`,
> and snapshot-derived status. S2-C3 subsequently resolves S7 with `prerequisiteDuty` plus
> independent Duties and removes global Duty effects from access resolution.

- **S4 — ✅ Resolved 2026-07-29 (Step 4a; §7 sign-off; design authored directly by the user after prior-art review of Allen's Interval Algebra and OWL-Time — both rejected: OWL-Time distinguishes instants/intervals but has no deontic transition rule and is a heavier dependency than needed; full 13-relation Allen typing is unneeded scope when only `By`/`During`-style lifecycle semantics are required).** Done:
  - **`rl2:DutyMode` (Achievement/Maintenance).** New enum `rl2:DutyMode` (`rl2:Achievement`/`rl2:Maintenance`) + `rl2:dutyMode` (domain `rl2:Duty`) in `rl2.ttl`, mirroring the `ObligationState`/`PromiseState` pattern; `rl2:DutyModeShape` in `rl2-shacl.ttl`. Optional — absent `rl2:dutyMode` defaults to Achievement (the discipline every Duty followed before this distinction existed; zero corpus churn). Crystallization derives it from Promise content shape (`promisedAction`/`promisedDuty` → Achievement, `promisedState` → Maintenance) rather than requiring it be authored on the source Promise.
  - **Sound, partial `extractDeadline`.** `RL2_Semantics.md` `extractDeadline` no longer synthesizes a bound via `min`/`max` over arbitrary `And`/`Or` structure. It recognizes exactly one canonical upper-bound leaf (`currentDateTime lt|lte t`, static `t`) reachable through a top-level conjunction and returns `None` otherwise (`Or`, `Not`, `Xone`, ambiguous multi-bound `And`, dynamic `t`). A temporal comparison inside a general `Condition` is not automatically a temporal window; the raw condition language remains valid for activation/guards (`⟦c⟧`), but `deadlinePassed` only consumes this proven-safe fragment. This is the fix for the previously-unsound extractor, not a new named temporal constructor — see note below on the original phrasing.
  - **`lt`/`lte` strictness preserved.** New `TimeBound = Bound(t, inclusive)` + `expired(bound, now)` replaces the single collapsed `Σ.Clock > t` check, so `lt t` (expires at `now ≥ t`) and `lte t` (expires at `now > t`) are distinguished.
  - **Achievement/Maintenance ObligationState lifecycle.** `RL2_Semantics.md` splits the former single Duty Fulfillment/Violation pair into four rules gated on `dutyMode`: **Achievement** keeps the original `performed()`-before-deadline discipline; **Maintenance** (new) violates on the first witnessed `⟦c⟧(Env) = False` while active, and fulfills only when a recognized monitoring window (`extractDeadline`) closes with `⟦c⟧(Env) = True` — with no recognized end bound it stays Active rather than being declared fulfilled by omission. `Unknown(_)` advances neither rule (S2 discipline).
  - **`xsd:dateTimeStamp` requirement.** `rl2:currentDateTime rdfs:range xsd:dateTimeStamp` added (bare `xsd:dateTime` lacks a timezone offset and so no total ordering); activates the existing dormant `rl2:OperandRangeTypeShape` warning for `currentDateTime` comparisons for the first time. 19 corpus literals retyped `^^xsd:dateTime` → `^^xsd:dateTimeStamp` (`rl2.ttl` doc comment, `RL2_Primer.md` ×13, `RL2_Vocabulary.md` ×1, `usecases/policy-versioning.md` ×2, `usecases/time-window-access.md` ×3) to keep the warning-free gate clean; unrelated `xsd:dateTime` literals (`imposedTime`, the foreign ODRL Temporal Profile example) were left untouched.
  - **Crystallization table/prose updated** (`RL2_Semantics.md`): the `PromisedState` row's ObligationState-wiring gap is closed; **SEM-1** is narrowed to just `restoreAction`/`rl2:remedialAction` (unaffected by this change, still open).
  - **On the original "`During`/`Before`/`By`/interval" phrasing:** the adopted design does not introduce new named `Condition` constructors. `dutyMode` supplies the deontic *lifecycle* distinction those names gestured at (Achievement ≈ "By" — fulfilled once before a bound; Maintenance ≈ "During" — must hold throughout a window) while temporal *bounds* stay expressed through the existing `AtomicConstraint`/`currentDateTime` fragment, now soundly extracted. Richer interval relations (the rest of Allen's 13) remain a possible future profile, not core vocabulary.
  - Touched: rl2.ttl, rl2-shacl.ttl, RL2_Semantics.md, RL2_Primer.md, RL2_Vocabulary.md, usecases/policy-versioning.md, usecases/time-window-access.md, issues.md (SEM-1 narrowed).
  - **Not covered by this step (separate, still open):** SEM-11's `nullRequest`/`PromisedState`-resolutionPath-restriction recommendation (adopted but not yet executed); guard predicates and the Promise↔Duty↔Requirement status-projection phrasing now folds into the already-resolved `requirementStatus` projection (WP-3 Step 3c, F3/P3) plus this step's `dutyMode`-aware lifecycle — no separate projection work identified as outstanding.
- **S7 / SEM-9 / SEM-8 — ✅ Resolved 2026-07-29 (Step 4b; semantics-only, no ontology change).** `rl2:priority`/the strategy names were already ontology-external ("evaluator configuration, not policy vocabulary" — `RL2_Semantics.md`), so this closed entirely within `RL2_Semantics.md`; no `rl2.ttl`/`rl2-shacl.ttl` edit and no §7 sign-off gate applies. Done:
  - **Specificity fully defined, corrected 2026-07-31** — conflict resolution first selects the maximal declared-priority stratum (default 0) across Privilege and Prohibition. Within that stratum, the resolver summary stores each effect kind's maximal lexicographic `(actionDepth, atomCount)` key; priority is not counted twice.
  - **Empty/tied/incomparable sets given a complete result.** Missing maxima represent an empty effect kind; comparing the two maxima gives a total result. A same-effect tie is conclusive, while equal opposite-effect maxima are `Indeterminate`.
  - **ODRL `Invalid` strategy added and priority-ordered** — a fourth strategy alongside `ProhibitOverrides`/`PermitOverrides`/`SpecificOverridesGeneral`: a Privilege/Prohibition conflict in the maximal-priority stratum is `Indeterminate`. Lower-priority candidates have already been defeated, matching D1's priority-before-strategy rule.
  - **Source-policy/source-clause provenance retained on every normative atom.** `Out`/`deriveNorms` previously projected matched norms down to bare `permit(a,x,s)`/`forbid(a,x,s)` tuples, losing both the clause object (so `.priority`/`.condition` were unavailable to `resolveDecision` downstream — a real type mismatch with the Big-Step `Eval`, which operates on full clause objects) and the source `Policy`. Atoms are now `permit(n, P)`/`forbid(n, P)`/`obligate(d, P)`/`violated(d, P)`, carrying the full norm object and its policy; also fixed an incidental bug where `matches(_, R)` ignored the norm being matched.
  - Touched: RL2_Semantics.md, issues.md (SEM-9 resolved, SEM-8 narrowed).
  - **Not covered by this step (separate, still open):** **"attach duties to their grant"** — RL2's Duty is a freestanding top-level clause with no link to a specific Privilege whose win/loss in `resolveDecision` gates it, unlike ODRL's permission-nested `duty`. Whether RL2 should add such a link (a new ontology property, e.g. Privilege → attached Duty) or deliberately keep Duties independent (current behavior) is a real modeling decision, not a documentation gap — it needs the same kind of explicit design sign-off S4's `dutyMode` got, and mainly matters for **WP-7's ODRL import/export** (`O2b/EXPR-8`, blocked on this). Deferred to when WP-7 is picked up, or to an explicit design request. Power `ExercisePower` state-update verification and the remedial-norm chain (SEM-8's other two sub-items) are also untouched.
- **F2 / SEM-10 — ✅ Resolved 2026-07-29 (Step 4c; semantics-only, no ontology change).** `rl2:condition`'s domain already covers every `Norm` subclass and `PowerShape`/`ImmunityShape` already permit it — the grammar was under-specified, not the ontology — so this closed entirely within `RL2_Semantics.md`; no `rl2.ttl`/`rl2-shacl.ttl` edit and no §7 sign-off gate applies. Full detail under **SEM-10** (now Resolved). Done:
  - **`powerCondition`/`immunityCondition` dropped as named predicates (CANON-5).** Abstract syntax gained the `Condition?` field they were missing (`Power(Agent, Norm, Condition?)`, `Immunity(Agent, Power, Condition?)`); both denotations now use the direct three-way `Truth` pattern (S2) on that field, same shape as Privilege/Duty/Prohibition.
  - **Liability's guard pattern fixed, not just renamed.** The old unlinked existential (`∃ Power(h, n) where subject(n) = a`) was inconsistent with `LiabilityShape`'s required `rl2:exposedTo` link. Liability now carries `exposedTo` as its typed (`Power`, not generic `Norm`) second constructor field and derives its `Truth` from that specific Power — mirroring the Claim/Duty derivation pattern (C6b). Sanctions-and-Remedies rule tightened to reference the same bound Power instance on both sides.
  - **Claim `Right` dropped (drive-by).** Undefined anywhere, absent from `ClaimShape`, already superseded in practice by `correlativeTo: Duty` (used 3-ary at `RL2_Semantics.md:1435`, `RL2_IR.md:118,348`). Grammar and denotations now consistently use `Claim(Agent subject, Agent counterparty, Duty correlativeTo)`; the Prohibition↔Claim derivation rule's undefined `¬x@o` shorthand and `correlatesTo`/`correlativeTo` name mismatch fixed alongside it.
  - **Materialization/acceptance:** confirmed already fully specified (§Materialization, §Remedial Generation Rule, §Acceptance) — no gap, no new work needed.
  - Touched: RL2_Semantics.md, issues.md (SEM-10 resolved, SEM-8 further narrowed).
  - **Not covered by this step (separate, still open — SEM-8):** Power `ExercisePower` state-update verification and the violation→remedial-norm chain completeness.

### WP-5 — External data + execution model

**Depends on:** WP-2 (S2), WP-3 · **Status:** ✅ Resolved 2026-07-29 (both I1/SEM-4 and E1/SEM-13 and I4 sub-items closed; see each below)

> **Integration follow-up (fix.md 2026-07-29):** **C3-7** finds `resolveOutOfBand` doesn't handle duplicate/conflicting/stale/wrong-subject assertions and live SourceBinding calls lack a source snapshot/version (no coherent cut); **D14/D15/D16** sharpen SourceBinding keying and the `VDuration`/`VSet` value types; **D20/D21** re-open the I4 effect-merge/`validateCommit` idempotence via stable effect IDs. See § Remediation Roadmap — integration sweep (2026-07-29).

- **E1 / SEM-13 — ✅ Resolved 2026-07-29 (new `RL2_ExternalData.md`; `RL2_Architecture.md` TBDs closed, no ontology change).** Authored `RL2_ExternalData.md` specifying the source-binding step between a `ContextManifest`/`OperandSpec` entry and an actual external data source — the gap between `resolve`'s declared signature and `Sources` being otherwise unspecified. Done:
  - **Out-of-band resolution fixed as the normative baseline.** `resolveOutOfBand : (OperandSpec*, ContextAssertion*) → (Context, Missing*)` — a pure, total, O(|specs|·|assertions|) projection of already-supplied `rl2p:ContextAssertion`s (`RL2_Protocol.md` §Context) onto required operands. No network calls, no timeouts; satisfies the evaluator's totality/determinism assumptions by construction. Missing `required` operands surface as `Missing*` → `NeedContext`/`Indeterminate`, never a silent decision.
  - **`SourceBinding`/`SourceRegistry` defined** — the formalization of `Sources`: `SourceBinding(function, source, complexity: O1|OLogN, timeoutMillis, onFailure: ToBottom|ToMissing)`, keyed by `resolutionFunction` name. Kept outside the RDF graph as evaluator/deployment configuration, mirroring how S7 scoped `conflictStrategy` as evaluator config rather than policy vocabulary (I1/SEM-4 above) and how O3 scopes the supported-profile registry. An unregistered `resolutionFunction` name is a load-time (fail-closed) rejection, not a runtime `⊥`.
  - **Hybrid/in-band fixed as an explicitly non-core, opt-in extension**, never a policy requirement: bounded complexity (O(1)/O(log n) per call, per the existing S8a constraint), mandatory timeout, and a `ToBottom`/`ToMissing` fail policy that keeps `resolve` total. `ToMissing` degrades uniformly to the out-of-band path, so in-band can be disabled deployment-wide with zero policy-visible behavior change.
  - **Mock sources for future implementation testing** — `MockSource(function, canned: map<Request,Value>)`, substituted per `resolutionFunction` name to make external-data conformance tests deterministic.
  - **Profile-defined source schemas** — profiles declaring `resolutionFunction` operands SHOULD ship a `SourceBinding` shape table + `MockSource` fixtures as deployment documentation, kept out of `rl2.ttl`/profile ontology files.
  - **`RL2_Architecture.md`'s two TBD interaction-mode tables and two Open Design Questions rows closed**, all pointing at `RL2_ExternalData.md`: §Runtime Functions `resolve`'s "Interaction modes (TBD)" table now marks out-of-band normative-baseline vs in-band/hybrid optional-extension; §Interaction Modes' "TBD: Specify which modes are normative vs optional" resolved (Single-shot/Iterative/Pre-flight are all realizable via out-of-band alone and are all normative); "Context resolution mode" and "Incomplete context behavior" rows in Open Design Questions marked Decided. "Pre-flight API" and "NeedContext protocol" rows are untouched (still TBD — out of this item's scope).
  - Touched: RL2_ExternalData.md (new), RL2_Architecture.md (§Runtime Functions `resolve`, §Interaction Modes, §Open Design Questions), issues.md.
- **I1 / SEM-4 — ✅ Resolved 2026-07-29 (`RL2_IR.md`-only, no ontology change).** All seven defects were `RL2_IR.md`-internal gaps against an already-permissive ontology/semantics (`isA`/`isAnyOf`/`isAllOf`/`isNoneOf` are already `rl2:ComparisonOperator` individuals in `rl2.ttl`; `mkEnv(R,Σ,Ctx)` and `Eval(U,R,Σ,Ctx,strategy)` were already the canonical RL2_Semantics.md signatures) — no `rl2.ttl`/`rl2-shacl.ttl` edit and no §7 sign-off gate applies. Done:
  - **Real `Xone`.** `IXor` (parity on chained folds, wrong for ≥3 operands) replaced by N-ary `IXone(n: nat)`, reducing directly per the existing Kleene rule — a type-level fix, the semantic rule itself is unchanged.
  - **`isA`/`isAnyOf`/`isAllOf`/`isNoneOf` opcodes added** (`IIsA`/`IIsAnyOf`/`IIsAllOf`/`IIsNoneOf`), lowering the already-ontology-defined operators that previously had no bytecode target.
  - **`Value` extended**: `VDecimal` (exact fixed-point), `VLangString`, `VDuration`, `VSet` (collections — operand type for the new `isAnyOf`/`isAllOf`/`isNoneOf`), and `VDate`→`VDateTime` (mandatory `tzOffsetMinutes`, matching S4/WP-4's `xsd:dateTimeStamp` decision; `IDateLte`→`IDateTimeLte`).
  - **`rightOperandRef` handling fixed** — the direct AST resolver distinguishes dynamic
    resource references from literal `rightOperand` values and resolves either operand
    position through the same typed environment.
  - **Evaluation order clarified.** The direct AST interpreter follows the existing
    Kleene-logic invariants; short-circuit and error observability are fixed by the algebra,
    not by an obsolete bytecode evaluation order.
  - **`Ctx` added to `evalIR`'s signature** (`evalIR : (CompiledUniverse, Request, Σ, Ctx, Strategy) → …`), threaded through `mkEnv(R, Σ, Ctx)` — fixes a real mismatch against §9's equivalence obligation, which already stated `Eval(U, R, Σ, Ctx)`.
  - **`conflictStrategy`/`targetIndex` lifted to cross-policy scope.** `CompiledPolicy` (a per-`Policy*` struct with its own `conflictStrategy` field) replaced by `CompiledUniverse(policies: seq<CompiledPolicy>, targetIndex, subsumptionIndex)`, mirroring `PolicyUniverse`/`Out`/`Eval` in RL2_Semantics.md; `targetIndex` now maps `Target → set<ClauseRef>` spanning all policies (`ClauseRef = (policy, clause)`); `CompiledPolicy` keeps only `policyId` (provenance, echoing S7's atom-provenance fix)/`clauses`/`kind`. `conflictStrategy` is no longer stored anywhere — it is supplied to `evalIR` as an explicit parameter, per S7's "evaluator configuration, not policy vocabulary" ruling.
  - **Drive-by fix in RL2_Semantics.md:** `Eval`'s Big-Step Semantics definition referenced `P.conflictStrategy` with `P` out of scope (a residue of S7's fix, which had already correctly parameterized the *other* `Eval` definition in §Normative Derivation but missed this one) — both `Eval` signatures now take `strategy` as an explicit parameter, consistent with each other and with `evalIR`.
  - Touched: RL2_IR.md (v0.6→0.7), RL2_Semantics.md (§Big-Step Semantics signature + call site), issues.md.
- **I4 — ✅ Resolved 2026-07-29 (`RL2_IR.md` + `RL2_Semantics.md`, no ontology change).** Done:
  - **`deriveEffects` made concrete** (`RL2_IR.md` §7.1) — previously an unspecified placeholder call. `TransitionDuty` effects are now keyed **by duty**, computed via `transitionEffect(d, Σ, env)`, a direct restatement of `updateOneDuty`'s case dispatch (RL2_Semantics.md `updateDutyStates`) as an effect-returning total function of `(Σ.ObligationState(d), env)`.
  - **Effect-conflict resolution answered as "precluded by construction," not a runtime strategy** — since `transitionEffect` is keyed by duty and total, `duties(envelope)` being a set means at most one `TransitionDuty` per duty per round; `CrystallizePromise`/`GenerateRemedialDuty`/`CreateCase` are keyed by originating clause, so distinct clauses can't collide either. `applyEffects` (§7.3) is therefore a commutative/idempotent merge, not an arbitrator — mirroring how S7 eliminated per-clause `conflictStrategy` rather than adjudicating between clauses. `ExercisePower` is the one effect kind left open, deferred to SEM-8 (not claimed here).
  - **Commit-time validation formalized** (`RL2_IR.md` §7.3 `validateCommit`; `RL2_Semantics.md` §Versioned snapshot and commit) — a commit at version `v` is valid only if the applied `fx` equals `evalIR`'s fresh recomputation against `Snapshot_v`, not a caller-supplied `fx` accepted on trust. This closes the gap the CAS version-check alone leaves (a stale/memoized `fx` could coincidentally carry a still-current `v`). Makes retries free to leave outside the proof: unchanged-`v` retries recompute the same `fx` (determinism) and no-op; retries after `v` moved fail CAS and force re-evaluation.
  - **§9c (Effect-soundness lemma) extended** with the conflict-freedom and commit-validity sub-lemmas above, alongside the existing made-vs-demanded orientation sub-lemma.
  - Touched: RL2_IR.md (§7.1, §7.3, §9c), RL2_Semantics.md (§Versioned snapshot and commit), issues.md.


## Band 0 — Canonical Form (Generatability)

> **✅ Implemented in v0.6 (2026-07-24).** CANON-1..5 applied across `rl2.ttl`,
> `rl2-shacl.ttl`, `RL2_Semantics.md`, `RL2_Architecture.md`, `AGENTS.md`,
> `RL2_Vocabulary.md`, `RL2_Primer.md`, `CLAUDE.md`, and the affected use cases.
> Ontology bumped to 0.6. See § Resolved → CANON (v0.6). Residual follow-ups are
> tracked in Band 1 (CANON-1's IR-normalization enforcement → SEM-4; the
> `promisedState` remedial-action default → SEM-1). Details retained below.
>
> Governing principle (adopted from critique 3): **for any normative proposition the language can express, there is exactly one valid RDF shape that expresses it.** Two graphs that differ structurally must differ semantically. Where they don't, one shape is canonical and SHACL rejects the rest. This is the single most important property for machine generation and structural equivalence checking.

### CANON-1 — Condition placement & composition semantics

**Status:** Resolved (v0.6) — composition confirmed as conjunction & documented; IR-normalization enforcement → SEM-4 · **Severity:** S1 · **Source:** critique 3 · **Tags:** [GEN] [VER]
**Files:** `rl2.ttl` (`rl2:condition` domain = union(Norm, Policy)), `RL2_Semantics.md`, `rl2-shacl.ttl`

`rl2:condition` may attach to a Norm **or** a Policy (two levels — not four; Set/Offer/Agreement are Policy subclasses). The semantics define that ODRL-style `inheritFrom` is *not* supported (`RL2_Semantics.md:1428`), but they do **not** define how a Policy-level condition composes with a Norm-level condition. Is it conjunction? Override? Precedence? Undefined composition means every evaluator resolves it differently — ODRL's assigner problem in new clothes.

**Options:** (a) Pure conjunction, no override: policy-condition AND norm-condition, specified as a total function in Semantics and enforced by SHACL. (b) Single canonical location per condition *kind* — activation conditions only on Policy, content conditions only on Norm. (c) Norm-only: forbid Policy-level conditions entirely, require explicit per-norm conditions.
**Recommendation:** (a) — least disruptive, preserves existing use cases, needs only a formal merge definition + a note. Decide before Band 2 coverage work.

### CANON-2 — `promiseContent` polymorphism → split properties

**Status:** Resolved (v0.6) · **Severity:** S1 · **Source:** critique 1 & 3 · **Tags:** [GEN] [VER]
**Files:** `rl2.ttl:122` (`rl2:PromiseContent` = union(Action, Duty, Condition)), `rl2-shacl.ttl`, use case 8, 11

One property `rl2:promiseContent` ranges over three structurally different things. An Action-promise ("I will delete") and a Condition-promise ("data will be deleted") differ in Tun-sollen vs Sein-sollen terms — they are *not* semantically equivalent, yet the language lets a generator emit either for the "same" intent, and forces the evaluator to understand all three. The Duty-referencing case needed a special caveat in the ontology precisely because the polymorphism created ambiguity.

**Recommendation:** Replace with three distinct properties, each with clean non-overlapping semantics: `rl2:promisedAction` (Tun-sollen), `rl2:promisedState` (Sein-sollen), `rl2:promisedDuty` (suretyship — see PROM-5). Retire `rl2:PromiseContent`. Breaking change → v0.6. Resolves half of PROM-5 as a side effect.

### CANON-3 — Prohibition vs Duty-to-refrain

**Status:** Resolved (v0.6) — class kept; duty-to-refrain + derived correlative Claim specified · **Severity:** S2 · **Source:** critique 1 §2.2 & critique 3 · **Tags:** [GEN] [COV]
**Files:** `rl2.ttl:35` (`rl2:Prohibition`), `RL2_Semantics.md`

Strict Hohfeld: a prohibition *is* a duty to refrain, correlating with a claim. RL2 models Prohibition as a sibling class of Duty with `prohibitedAction` (⊑ `action`). This is a defensible pragmatic choice, but two things are unresolved: (1) does a Prohibition induce a correlative Claim, and in whom? Prohibition has no counterparty story. (2) Is the class distinction the *only* way to express a negative duty (good for canonical form), or can a `not`-wrapped condition on a Duty express the same thing (bad)?

**Options:** (a) Keep Prohibition as the sole canonical negative-duty form; document its Hohfeldian status (duty-to-refrain) and specify its correlative Claim; SHACL-forbid any alternative encoding. (b) Eliminate the class, model as Duty + negated action. **Recommendation:** (a) — Prohibition is ergonomic for generators and authors; the fix is to *pin down its semantics*, not remove it.

### CANON-4 — Counterparty / claim-role redundancy

**Status:** Resolved (v0.6) — unified on subject/counterparty; claimHolder/claimAgainst removed · **Severity:** S2 · **Source:** critique 3 · **Tags:** [GEN]
**Files:** `rl2.ttl:71-79,157`

Four overlapping role properties: `rl2:subject`, `rl2:counterparty` (Norm-level), `rl2:claimHolder`, `rl2:claimAgainst` (Claim-level). A Duty↔Claim correlative pair can express "who is owed" via `counterparty` on the Duty *and* via `claimHolder`/`claimAgainst` on the Claim. Need a canonical rule: which role property is authoritative on which norm type, and how correlative roles must line up. Enforce with SHACL.

### CANON-5 — Adopt & document the canonical-form invariant

**Status:** Resolved (v0.6) · **Severity:** S1 · **Source:** critique 3 (synthesis) · **Tags:** [GEN]
**Files:** `persona.md`, `RL2_Architecture.md`, `rl2-shacl.ttl`

Make the "exactly one shape" principle an explicit, stated design tenet (not folklore), and back it with SHACL wherever a canonical choice is made (CANON-1..4, and any future construct). Add a short "Canonical Form" section to Architecture and a design rule to persona.md. This is the umbrella issue that CANON-1..4 instantiate.

### CANON-6 — Remove dead vocabulary: `rl2:requires`, `rl2:ConditionOrEvent`, `rl2:NormOrEvent`

**Status:** ✅ Resolved (2026-07-26, `AGENTS.md` §7 sign-off obtained) · **Severity:** S3 · **Source:** fix.md (2026-07-26 sweep) · **Tags:** [CANON]
**Files:** `rl2.ttl`, `RL2_Semantics.md`, `RL2_Vocabulary.md`, `RL2_Primer.md`

`rl2:requires` has declared prose semantics (`RL2_Semantics.md:318`: "`c1 requires c2` means that whenever `c1` is considered, `c2` must also hold") but no `Requires` constructor in the abstract syntax and no IR lowering — dead vocabulary, equivalent to `And(c1, c2)` evaluated as a unit. Its range class `rl2:ConditionOrEvent` exists solely to serve as `requires`'s range and dies with it. `rl2:NormOrEvent` is a separate named union class existing only as the domain of `rl2:approver`/`rl2:operationalAgent`; the same effect is achievable with inline `owl:unionOf` domains on those two properties, without a named intermediary. The only corpus use of `requires` is illustrative (`RL2_Primer.md:569`, `ex:stewardshipPromise`); no use case exercised it, so removal needed no use-case migration.

**Action taken:** removed `rl2:requires`, `rl2:ConditionOrEvent`, and `rl2:NormOrEvent` from `rl2.ttl`; `approver`/`operationalAgent` domains now use inline `[ owl:unionOf (rl2:Norm rl2:Event) ]`. Removed the corresponding sections/rows from `RL2_Vocabulary.md` (Union Classes section, Condition Properties table row, Role Properties domain column updated to `Norm ∪ Event`) and the "`rl2:requires` semantics" paragraph from `RL2_Semantics.md`. **Deviation from the literal fix.md action:** the Primer example (originally line 569) was rewritten as a single `AtomicConstraint`, not a `LogicalConstraint` `And` — the original example had only one condition to conjoin, and `And` requires 2+ operands (per CONS-6), so a bare `AtomicConstraint` is the correct minimal replacement. A leftover stale sentence referencing `requires`/`ConditionOrEvent` at old line 767 was also removed. Net reduction: 3 vocabulary terms, no expressiveness lost. **Verified:** exhaustive grep confirms zero remaining references across all `.ttl`/`.md` files; `uv run tools/validate.py` and `--per-fence` on `RL2_Primer.md`/`RL2_Vocabulary.md`/`RL2_Semantics.md` all show FAIL 0, matching the pre-change baseline (PASS 0 · WARN-ONLY 52 · FAIL 0 · SKIP 1 whole-file; per-fence docs all WARN-ONLY 1 · FAIL 0).

---


## Band 1 — Formal Semantics — resolved entries

### SEM-4 — IR definition

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S1 (blocks IMPL) · **Source:** fix P0.1 · **Tags:** [VER]
**Files:** `RL2_IR.md` (new), `RL2_Architecture.md`, `research/design-forth-ir.md`

`compile : Policy* → IR` left IR as TBD; blocked evaluator implementation and the "compile-time canonicalization" story. **Resolved** by authoring `RL2_IR.md`, a design spec (datatypes + opcode table + correspondence table + equivalence statements; no Dafny proofs — those are IMPL). Decisions:

**Current status after SCOPE-1 (2026-07-29):** the two-lowering/bytecode design described
below is historical. The active `RL2_IR.md` specifies one lowering, Turtle → normalized AST,
interpreted directly by `evalCondition`/`evalIR`. There is no committed implementation or
mechanized-proof track.

- **Hybrid, two-lowering IR** (standard compiler terms): `Turtle (syntax) → normalized AST (outer IR) → condition bytecode (inner IR)`. Only *conditions* lower to a stack machine; the deontic layer stays a tree-walk over the AST. Adopts `research/design-forth-ir.md`'s stack VM but **scopes it to pure condition eval** and **drops the `EMIT-*` opcodes** (emission is I/O-logic derivation, a set op in the AST layer, not a stack effect).
- **`Clause` (Norm ⊔ Promise) is the AST base element**, mirroring PROM-1's `rl2:Clause`. Promises (made *and* demanded) and their three contents are first-class; centering on Norm would repeat the PROM-1 oversight. Offer-vs-Agreement well-formedness (only Offer admits a Promise clause) is compiled in via `CompiledPolicy.kind`.
- **Derive-then-resolve** (I/O logic): monotone derivation collects a normative envelope; non-monotone `resolveDecision` applies conflict/priority after.
- **Functional core + effect shell:** kernel is a pure `evalIR : (IR,Request,Σ) → (Decision, DutySet, seq<Effect>)` — `(Decision,DutySet)` = verdict + future duties; `seq<Effect>` refactors the denotational `Eval`'s returned `State`. `CrystallizePromise`/`GenerateRemedialDuty`/`TransitionDuty`/`CreateCase`/`ExercisePower` are one closed effect algebra (unifies PROM-1/PROM-6/SEM-1/SEM-6/SEM-8). Two recorded invariants: snapshot-consistency (enables effects-outside-semantics) and effect-coherence (a real proof obligation).
- **Subsumption is eval-time:** compiler builds a static `subsumptionIndex` (`includedIn*` closure); the request-time match is membership. Limitations inherit ACT-1/2 + EXPR-2 (bounded reachability, no counting).
- **Correspondence table is the proof spine** (syntax ↔ semantics §ref ↔ AST ctor + bytecode lowering); its rows are the induction cases; empty cell = proof hole (the PROM-1 shape); read backwards it is the IR→source error-report map.
- **Compiler tested, not verified** (Cedar-style differential testing on the 51 use cases + generated policies), backed by CANON making `Turtle→AST` near-mechanical; condition-compiler is a later verification stretch goal. Precedents: evm-dafny (inner VM), Cedar-spec (test strategy) — `research/verification-toolchain-comparison.md`.
- **Equivalence obligation** split into (a) normalization theorem (outer), (b) VM-correctness lemma (inner, `EvalBytecode(lower c,env)=⟦c⟧`), (c) effect-soundness lemma (incl. made-vs-demanded crystallization orientation + effect coherence).

**Handoffs:** SEM-5 consumes `CompiledPolicy.targetIndex` (owns the matching algorithm/precedence); SEM-1 owns `PromisedState` maintenance-duty ObligationState wiring; PROM-5 owns `PromisedDuty` suretyship remedy; effect kinds map to PROM-6/SEM-6/SEM-8. **Follow-up (done 2026-07-25):** aligned RL2_Semantics.md abstract syntax to `Policy.clauses : Clause*` (added `Clause ::= Norm | Promise`), matching the ontology and RL2_IR.md. No semantic change — the type-filtered comprehensions in `Out`/`Eval` already exclude Promise clauses from norm matching.

**Follow-up (fix2.md E9, 2026-07-25 sweep):** the snapshot-consistency invariant (`RL2_IR.md:247-253` — "every read in a single evaluation observes Σ as of entry; all effects apply atomically afterward") is currently stated as a design note ("so it is stated, not assumed") rather than enforced, and it "holds for RL2 today" only because `Out` is a set-builder over a fixed snapshot and `resolveDecision` is set-based — a future construct observing another clause's effect within the same evaluation would silently violate it. Action (belongs to IMPL-1/2, tracked here since it's a spec-level obligation first): add a Dafny precondition to the `evalIR` spec — `requires ∀ c ∈ CP.clauses, the evaluation of c does not depend on effects produced by evaluating any other clause` — so this becomes a verified precondition, not an assumption. Related: **CONS-3** (the `CrystallizePromise` effect in this same effect algebra needs a source-Promise reference for the audit trail).

**Follow-up (WP-5/I1, 2026-07-29):** the concrete type-system gaps left after this initial `RL2_IR.md` authoring — parity-not-Xone, missing `isA`/`isAnyOf`/`isAllOf`/`isNoneOf`, an untyped/tz-less `Value`, unhandled `rightOperandRef`, missing `Ctx` in `evalIR`, and a per-policy `conflictStrategy`/`targetIndex` that didn't scope to the policy universe — are resolved; see **I1 / SEM-4** under **WP-5** for the full list. `CompiledPolicy.targetIndex` above is now `CompiledUniverse.targetIndex` (`map<Target, set<ClauseRef>>`, spanning all policies).

### SEM-9 — `mostSpecific` undefined in `SpecificOverridesGeneral`

**Status:** ✅ Resolved 2026-07-29 (WP-4/S7) · **Severity:** S1 · **Source:** fix.md §3.1/Task 3, fix2.md E1 · **Tags:** [VER]
**Files:** `RL2_Semantics.md` §Conflict Resolution (`mostSpecific`, `SpecificOverridesGeneral`)

`resolveDecision`'s `SpecificOverridesGeneral` strategy calls `mostSpecific(privileges ∪ prohibitions)`, but `mostSpecific` is never defined — so `resolveDecision` is not actually total until this is closed. **Sharpened (fix2.md):** the gap is subtler than "undefined": specificity may mean different things for a Privilege (action subsumption depth) vs a Prohibition (condition complexity), and a single ordering over the *union* of both assumes a common specificity metric that may not exist. **Recommendation:** define `mostSpecific` as a lexicographic ordering — (1) action subsumption depth (deeper = more specific), (2) condition count (more conditions = more specific), (3) policy priority as tiebreaker — and document this explicitly as a design choice, not a theorem.

**Resolved (WP-4/S7, 2026-07-29; corrected by C3-1 review and S2-C3 on 2026-07-31):** priority is a separate first-stage filter, not the third component of specificity. The resolver summary selects the maximal declared-priority stratum (default 0) across Privilege and Prohibition and retains each kind's maximal `specificity(n,P) = (actionDepth(n.action), guardAtomCount(P,n))`. `actionDepth` is static ancestor count under `rl2:includedIn*`; `guardAtomCount` includes policy and norm conditions and, for a Privilege, each prerequisite Fulfilled test plus its applicability condition. Missing maxima represent an empty side; one larger maximum wins; equal opposite-effect maxima are `Indeterminate`. This total summary replaces the former undefined `mostSpecific` call without allowing priority to be ignored by non-specificity strategies, counted twice, or made blind to prerequisite guards.

### SEM-10 — Undefined guard predicates `claimCondition`/`powerCondition`/`immunityCondition`

**Status:** ✅ Resolved 2026-07-29 (WP-4/F2) · **Severity:** S1 · **Source:** fix.md §3.3/Task 4, fix2.md E2 · **Tags:** [VER]
**Files:** `RL2_Semantics.md` §Claim/Power/Liability/Immunity Denotation, §Sanctions and Remedies, Abstract Syntax (`Norm`)

Three condition guard predicates gate the `Claim`, `Power`, and `Immunity` denotations, but their reduction rules (how they evaluate to true/false given an environment) are never given anywhere in the spec. SEM-8 already flags these as "under-exercised" (see above). The obvious canonical reading is that each is an alias for `⟦n.condition⟧(Env) = true` — if so, the three distinct names should be dropped per CANON-5 (exactly one canonical shape). **Additional finding (fix2.md):** the `Liability` denotation (`:801`) uses a *different* guard pattern — `∃ Power(h, n) where subject(n) = a`, an existential quantification over the norm universe, not a condition evaluation — suggesting confusion about whether these predicates are condition-gated or structurally-derived. **Action:** (a) if all are condition-evaluation aliases, use `⟦n.condition⟧(Env) = true` uniformly and drop the three distinct names; (b) if some have genuinely distinct semantics (e.g. Liability's existential), define each explicitly and document why the guard patterns differ.

**Resolved (WP-4/F2, 2026-07-29, semantics-only, no ontology change):** re-derived from the actual current text rather than the stale line numbers above (which predate WP-3/WP-4 edits). `claimCondition` turned out not to exist at all — C6b (already resolved, pre-dating this step) had already replaced it with derivation from the correlative Duty's own condition, so nothing to fix there beyond a drive-by grammar cleanup (below). That left `powerCondition`/`immunityCondition` and the Liability existential as the real gap, and it is option (b): they are genuinely distinct, not all aliases.
- **Root cause:** the abstract syntax `Power(Agent, Norm)` / `Immunity(Agent, Norm)` / `Liability(Agent, Norm)` had no `Condition` field at all to alias — yet `rl2:condition`'s domain (`owl:unionOf(rl2:Norm, rl2:Policy)`) already permits it on every `Norm` subclass, Power/Immunity included, and `PowerShape`/`ImmunityShape` already allow it (no `maxCount 0` the way `ClaimShape` forbids it on `Claim`). The grammar was simply under-specified relative to what the ontology already supports — not an ontology gap, a documentation gap.
- **Power / Immunity — condition-evaluation aliases, per option (a), now typed.** Abstract syntax extended to `Power(Agent, Norm affectsNorm, Condition?)` and `Immunity(Agent, Power immuneFrom, Condition?)`. Both denotations now use the direct three-way `Truth` pattern (S2) on that field — the same shape as Privilege/Duty/Prohibition — so `powerCondition`/`immunityCondition` are dropped as named predicates rather than defined (CANON-5). Power's condition gates the Power itself, independent of `affectsNorm`'s own condition; Immunity's condition gates the immunity independently of `immuneFrom`'s (e.g. "immune from termination during the first 90 days" holds on its own schedule).
- **Liability — genuinely distinct, per option (b), now correctly linked.** Liability has no condition of its own; it is a **structurally derived** view of a *specific* Power — mirroring the Claim/Duty derivation pattern (C6b) — inheriting that Power's `Truth` (`PowerActive → LiabilityActive`, `Indeterminate → Indeterminate`, else `LiabilityInactive`). The old `∃ Power(h, n) where subject(n) = a` was not just unmotivated but **architecturally inconsistent** with `LiabilityShape`, which already requires exactly one `rl2:exposedTo` link to a specific `rl2:Power` — the unlinked existential could bind a Liability to any Power sharing its target, not the one it's actually `exposedTo`. Fixed by adding `exposedTo` as Liability's second constructor field (typed `Power`, not generic `Norm`) and denoting against that specific instance. The Sanctions-and-Remedies inference rule was tightened to match (`P` is now the same bound Power instance on both sides, not a re-mentioned `sanction` term).
- **Claim `Right` (F2, drive-by):** the abstract syntax's `Claim(Agent, Agent, Right)` third field `Right` was undefined anywhere in the document, absent from `ClaimShape`, and already superseded in practice by `correlativeTo: Duty` (used 3-ary with that exact field at `RL2_Semantics.md:1435` and in `RL2_IR.md:118,348` — `Claim [subject; counterparty; correlativeTo]`). Grammar now reads `Claim(Agent subject, Agent counterparty, Duty correlativeTo)`, matching what was already in use; `Claim`/`ClaimContent` denotations updated to bind `D` directly from the constructor instead of a same-named lookup. Also fixed the Prohibition↔Claim correlative-derivation rule (§Hohfeldian Correlatives), which used an undefined 3rd-arg shorthand `¬x@o` and a `correlatesTo`/`correlativeTo` name mismatch — now `Claim(h, s, Duty(s, ¬x, o, c))`, consistent with the "Prohibition **is** a duty to refrain" identity the same section already asserts.
- **Materialization/acceptance:** already fully specified independently (§Materialization, §Promise→Duty Generation/Remedial Generation Rule, §Acceptance/crystallization) — no gap found there; F2's mention of this scope is satisfied by pre-existing text, not new work.
- Touched: RL2_Semantics.md, issues.md (SEM-10 resolved).
- **Not covered by this step (separate, still open — SEM-8):** Power `ExercisePower` state-update verification and the violation→remedial-norm chain completeness beyond the Sanctions-rule notation fix above.

### SEM-12 — Stale Dafny example in `RL2_Semantics.md`

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S3 · **Source:** fix.md §3.7/§4.4(6)/Task 9, fix2.md E4 · **Tags:** [VER]
**Files:** `RL2_Semantics.md` (Dafny Example, Mechanization section)

The Dafny abstract-syntax example included `Temporal(start, end)` and `Context(path, cmp, val)` Condition variants that don't exist in the current abstract syntax: `TemporalConstraint` was removed in favor of `AtomicConstraint` + `currentDateTime`, and `Context` was replaced by `AtomicConstraint` + `resolutionPath`. It also omitted `Xone` even though it's present in the abstract syntax, and `EvalCondition`'s match fell through to `// ...` (non-exhaustive, would not compile). **Fixed:** removed `Temporal`/`Context`, added `Xone(operands: seq<Condition>)`, and made `EvalCondition` exhaustive (`Xone` case counts true operands via a set comprehension and requires exactly one).

**Superseded note (SCOPE-1, 2026-07-29):** the "Dafny Example" and "Mechanization"/"Target Platforms" sections this issue fixed were later removed from `RL2_Semantics.md` entirely, along with the rest of the Dafny/Go mechanization track. `evalCondition`'s pseudocode now lives in `RL2_IR.md` §5 instead.

### SEM-13 — External data integration lacks a binding specification

**Status:** ✅ Resolved 2026-07-29 (WP-5/E1 — see full Done-block there) · **Severity:** S2 · **Source:** fix.md §6.4/Task 11, fix2.md E10 · **Tags:** [VER]
**Files:** `RL2_Architecture.md` (ContextManifest, `resolve`), `RL2_Semantics.md:364-366` (`resolutionFunction` "implementation-specific"), `RL2_ExternalData.md` (new)

`rl2:resolutionFunction` and `lookupExternal` are declared but not bound: no standard way for a policy to declare what external data it needs, for an evaluator to call external services, or to test/verify a policy that uses external data. This is the highest-risk area for the totality guarantee — the extension warning at `RL2_Semantics.md:1574` already flags unbounded external queries as a threat to polynomial-time/termination. The ContextManifest pattern (compiler extracts `RESOLVE` paths from condition trees → host pre-materializes them into `Env` before evaluation → `RESOLVE` of an un-manifested path is a hard reject) is the right shape, but the source-binding step between a manifest entry and an actual data source is unspecified.

**Resolution:** `RL2_ExternalData.md` specifies (1) out-of-band context supply as the
normative baseline, preserving the specified evaluator's totality and determinism assumptions;
(2) hybrid/in-band resolution as a bounded extension with timeout and explicit failure
handling; and (3) deployment-local source bindings plus deterministic mock fixtures. Live
external resolution remains outside the specified evaluator core.


## Band 1.5 — Protocol SHACL & Cross-Document Consistency (CONS)

> Surfaced by the fix.md/fix2.md 2026-07-25 review sweep — concrete SHACL over/under-constraint bugs and vocabulary/ontology mismatches found by manual cross-reference, distinct from the pySHACL-harness use-case defects in Band 3.5.

### CONS-1 — `RequirementFulfillmentAuditShape` requires both action and event evidence

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S2 · **Source:** fix2.md N1 · **Tags:** [VER]
**Files:** `rl2p-shacl.ttl:178-205`

The shape required `sh:minCount 1` on `fulfilledByAction` **and** `fulfilledByEvent` **and** `fulfillmentEvidence` for fulfilled requirements (three independent property shapes, each triggering its own warning) — but a requirement may legitimately be fulfilled by an action *or* an event, not necessarily both (e.g. a `PromisedState`-derived requirement is fulfilled by a state condition holding in Σ, with no discrete action). **Fixed:** collapsed the three property shapes into one `sh:or` (at least one of the three required). Severity was already `sh:Warning` at the node level. Validated against the full corpus: clean, `PASS 0 · WARN-ONLY 51 · FAIL 0 · SKIP 1`, no change in per-file warning counts (including `fulfillment-evidence.md`, which exercises this shape).

### CONS-2 — Protocol SHACL allows `Active` for Promise-derived Requirements (semantically impossible)

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S2 · **Source:** fix2.md N2 · **Tags:** [VER] · **Related:** PROM-7
**Files:** `rl2p-shacl.ttl:148-152` (`RequirementShape` `sh:in`), `rl2p.ttl:163-168`, `rl2.ttl:535-563`

`RequirementShape`'s `requirementStatus` `sh:in` list is the full `ObligationState` enum (`Pending`, `Active`, `Fulfilled`, `Violated`) — but `PromiseState` admits no `Active` (`rl2.ttl:558`). A Promise-backed Requirement can therefore be assigned `requirementStatus = rl2:Active` and pass validation. **Resolved as option (b), not (a):** `RL2_Semantics.md`'s "Promise and duty states vs protocol requirement status" section (and `RL2_Protocol.md:277`'s cross-reference to it) already document this as the *intended* protocol-level projection — a pending promise that is effective now surfaces as `Active` at the Requirement layer while its semantic `PromiseState` stays `Pending`. Checked for consistency: `usecases/runtime-evaluation.md`'s `ex:promiseReq` example (`sourceNorm = ex:somePromise`, `requirementStatus = rl2:Active`) already relies on exactly this reading; `claim-counterclaim.md` and `fulfillment-evidence.md`'s `Active`/`Fulfilled` usages are all Duty-sourced, not Promise-sourced, so unaffected. `RL2_IR.md`'s effect algebra doesn't model `rl2p:Requirement`/`requirementStatus` at all (it operates on Duty/Promise state directly via `TransitionDuty`/`CrystallizePromise`) — the projection is a protocol layer computation above the specified evaluator core, so no IR change was needed or made. **Action taken:** rather than adding a SPARQL rejection rule (which would contradict this documented design), added cross-referencing comments to `rl2p:requirementStatus` in `rl2p.ttl` and to `RequirementShape`'s `requirementStatus` property in `rl2p-shacl.ttl`, so the ontology/SHACL files are self-explanatory without requiring a jump to `RL2_Semantics.md`. This also satisfies **PROM-7**'s "land the reconciliation, not just a semantics-doc note" ask — the reconciliation already existed in the docs; it's now wired up from the ontology side too. Validated against the full corpus: clean, `PASS 0 · WARN-ONLY 51 · FAIL 0 · SKIP 1`.

### CONS-3 — `CrystallizePromise` effect lacks source-Promise reference

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S3 · **Source:** fix2.md N3 · **Tags:** [VER] · **Related:** SEM-4
**Files:** `RL2_IR.md:277-285` (Effect algebra)

`CrystallizePromise(promisor, promisee, content)` carried no reference to the originating `Promise` individual (its IRI or a clause index) — the audit trail from a crystallized Duty back to its source Promise was lost unless the application layer reconstructed it manually from `(promisor, promisee, content)`. **Fixed:** added `source: Clause` to the constructor, mirroring the existing convention already used by `GenerateRemedialDuty(source: Clause, remedy: Norm)` in the same effect algebra — no new `ClauseRef` type introduced since `Clause` already exists and serves the purpose directly.

### CONS-4 — `rl2p:PermitStateChange`/`DenyStateChange` referenced but undefined; also conceptually wrong

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S3 · **Source:** fix.md §4.4(1), fix2.md E5 · **Tags:** [COV]
**Files:** `RL2_Vocabulary.md` (Hohfeldian Mapping table), `rl2p.ttl` (Decision individuals: `Permit`, `PermitWithObligations`, `Deny`, `Indeterminate`, `NotApplicable` only)

The Vocabulary mapped Power→`rl2p:PermitStateChange` and Immunity→`rl2p:DenyStateChange`, neither of which `rl2p.ttl` defines — and the mapping was conceptually wrong: Power/Immunity are about altering normative relations, not access decisions, so they don't belong in the Decision enum. **Fixed:** Power now maps to `Effect (ExercisePower)` referencing the `RL2_IR.md` effect algebra; Immunity is documented as not an effect or Decision at all, but a precondition blocking `ExercisePower` (`ImmunityActive(a,n) → ¬canExercise(Power(h,n))`, `RL2_Semantics.md:807-821`). No `BlockPower` effect exists in `RL2_IR.md`, so that speculative name from fix2.md was not used.

### CONS-5 — `rl2p:requirementFulfilled` mis-categorized in the Vocabulary's Property Reference

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S3 · **Source:** fix.md §4.4(2), fix2.md E6 · **Tags:** [COV]
**Files:** `RL2_Vocabulary.md`, `rl2p.ttl:256-258`

`rl2p:requirementFulfilled` is a `rl2:LeftOperand` individual (an operand, not an OWL property) but was listed in the Protocol Property Reference table. **Fixed:** moved it to a new "Protocol Left Operands" subsection.

### CONS-6 — Missing `sh:maxCount 1` on Atomic/Logical/Event constraint shapes

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S3 · **Source:** fix.md §4.4(4), fix2.md E7 · **Tags:** [GEN]
**Files:** `rl2-shacl.ttl` (`AtomicConstraintShape` ~195-218, `LogicalConstraintShape` ~246-249, `EventConstraintShape` ~290-292)

`AtomicConstraintShape` has `sh:minCount 1` but no `sh:maxCount 1` on `leftOperand` and `constraintOperator` (`rightOperand`/`rightOperandRef` is already `sh:xone`-guarded). `LogicalConstraintShape`'s `constraintOperator` and `EventConstraintShape`'s `expectsEvent` have the same gap — a `LogicalConstraint` with two `constraintOperator` values, or an `EventConstraint` with two `expectsEvent` values, is ill-formed but currently passes SHACL. A canonical-form (CANON-5) gap: multiplicity should be pinned down exactly. **Fixed:** added `sh:maxCount 1` to `leftOperand` and `constraintOperator` in `AtomicConstraintShape`, `constraintOperator` in `LogicalConstraintShape`, and `expectsEvent` in `EventConstraintShape` (`LogicalConstraintShape`'s `operand` intentionally left uncapped — `and`/`or`/`xone` need 2+ operands). Validated against the full 51-use-case corpus (`uv run tools/validate.py`): clean, `PASS 0 · WARN-ONLY 51 · FAIL 0 · SKIP 1`, confirming no existing use case relied on the now-forbidden multiplicity.

**Checked and closed as not-a-gap (fix2.md E8):** fix.md's note that `Set`/`Privacy`/`Assertion` lack dedicated SHACL shapes beyond `PolicyShape` is **not** an issue — `Offer` intentionally inherits the permissive `PolicyShape`; the other subclasses each already have a shape that forbids Promise clauses (`AgreementShape` additionally requires `grantor`/`grantee`). The inheritance design is documented in `rl2-shacl.ttl:30-34`'s header comments. No action needed; recorded here so it isn't re-raised as an open gap.

### CONS-7 — `OperandRangeTypeShape` never fires (dead SHACL weight)

**Status:** ✅ Resolved (2026-07-26, `AGENTS.md` §7 sign-off obtained) · **Severity:** S3 · **Source:** fix.md (2026-07-26 sweep) · **Tags:** [CONS]
**Files:** `rl2-shacl.ttl`

WARNING-level shape checking that `rightOperand` IRI values match the `rdfs:range` of the left operand, gated on `isIRI(?right)`. The majority of right operands in the corpus are literals (`"research"`, `"99.9"^^xsd:decimal`, `"2025-01-01"^^xsd:dateTime`), which the shape never inspects. Across the full 52-use-case corpus this shape has never produced a warning — all 52 warnings on record are `OperandResolutionRecommendationShape`. **Correction to fix.md's premise:** the shape was not fully dead — several use cases (`break-glass.md`, `chinese-wall.md`, `gdpr-erasure.md`, `step-up-auth.md`, and others) declare class-typed (`rdfs:range rl2:Agent`, etc.) operands with IRI right-operands, so the original IRI branch is structurally live; it simply passes quietly because that part of the corpus happens to be well-typed. Only the literal-operand path (the majority case) was uncovered.

**Action taken:** extended the shape's `sh:sparql` with a `UNION` branch covering literal right-operands, using SPARQL `datatype(?right) != ?expected` against the leftOperand's declared `rdfs:range` (guarded by `isLiteral(?right) && isIRI(?expected)` so it only applies when the range is itself an XSD datatype IRI). The original IRI branch is unchanged. **Verified:** a synthetic test graph (leftOperand `rdfs:range xsd:boolean`, rightOperand `"not-a-bool"^^xsd:string`) confirmed the new branch correctly fires with the shape's warning message. Re-running the full 52-use-case corpus (`uv run tools/validate.py`) shows the identical baseline (PASS 0 · WARN-ONLY 52 · FAIL 0 · SKIP 1) — confirming the corpus itself is genuinely well-typed on literal operands too (a clean pass, not a silently-broken check), while the shape retains real protective value going forward.

---


## Promise Theory (PROM) — resolved entries

### PROM-1 — Promise-in-Agreement restriction & crystallization

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S2 · **Source:** critique 2 · **Tags:** [GEN] [COV]
**Files:** `rl2.ttl`, `rl2-shacl.ttl`, `RL2_Semantics.md`, `RL2_Primer.md`, `RL2_Architecture.md`, `RL2_Vocabulary.md`, `RL2_Protocol.md`

**Root cause found.** The Norm-only assumption was a systemic ontology oversight, not a deliberate restriction: `rl2:clause` range, `rl2:clauseOf` domain, and `PolicyShape`'s `sh:class rl2:Norm` all excluded `rl2:Promise` (a separate top-level class). Promise-in-policy examples only validated because RDFS range-entailment on `rl2:clause` *silently retyped the Promise as a Norm* to satisfy the SHACL `sh:class` — i.e. the corpus was passing by asserting a falsehood at inference time.

**Decision (committed).** Enforceability requires correlatives; a Promise creates none; so an executed Agreement's enforceable content is Duties/Claims only, and a Promise there is inert goodwill (a verification liability). Offers are the home of Promises; **acceptance crystallizes each Promise into a Duty + correlative Claim** (the act of contracting), so crystallization is core, not deferred.

**Implemented:**

- Added `rl2:Clause` superclass (`Norm` ⊔ `Promise`); retargeted `rl2:clause` range / `rl2:clauseOf` domain to it. A *named* superclass (not an anonymous `owl:unionOf`) so RDFS auto-types clause referents as `rl2:Clause` — preserving simple-fence validation with zero churn — while subclass entailment only propagates upward, so a Promise is never coerced into a Norm.
- SHACL: `PolicyShape` clause → `sh:class rl2:Clause` (permissive base; Offer inherits it). `AgreementShape`/`SetShape`/`PrivacyPolicyClauseShape`/`AssertionClauseShape` each add `sh:not [ sh:class rl2:Promise ]`. Only Offer admits a Promise clause. Verified: Promise-in-Offer conforms; Promise-in-Agreement fails.
- Crystallization defined in `RL2_Semantics.md` as a total function; each Duty inherits the promise content's already-defined fulfillment criterion (`rl2.ttl:promisedAction/State/Duty`). `promisedAction` fully closed; `promisedState`/`promisedDuty` crystallization *targets* fixed, behavioral wiring handed to SEM-1 / PROM-5 (below).
- Docs (Primer, Architecture) document the Offer=promises / Agreement=duties model; corpus examples that put a Promise in an Agreement (Vocabulary, Semantics, Protocol) re-typed to `rl2:Offer`.
- `rl2:targetNorm` range intentionally left as `rl2:Norm` — widening it for standalone promise-state queries was deferred to PROM-7 (now resolved: widened via SHACL `sh:or`, not `rdfs:range`, since a union range would have regressed fences that relied on targetNorm range-coercion for typing — see PROM-7 for the full root-cause note).
- Non-binding recitals: use `rl2:Assertion`, not a Promise clause.

### PROM-3 — Conditional promise in an accepted agreement

**Status:** ✅ Resolved 2026-07-25 (by PROM-1) · **Severity:** S3 · **Source:** critique 2 · **Tags:** [GEN]
**Files:** `RL2_Semantics.md`, `RL2_Primer.md`

"If audit findings > X, I promise to remediate within 30 days," placed in an Agreement — is it a conditional Duty or a Promise-that-generates-a-Duty? **Resolved by the container-determines-semantics rule (PROM-1 + CANON-2):** an Agreement contains no Promises — every promise crystallizes into a Duty + correlative Claim on acceptance — so in an Agreement this is unambiguously a **conditional Duty** (the condition is the duty's activation guard). The Promise-with-a-condition form exists only in an **Offer**, where it crystallizes to the conditional Duty on acceptance. The container type (Offer vs Agreement) fixes the reading; no ambiguity remains.

### PROM-7 — `PromiseState` vs `RequirementStatus` dual state machines

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S2 · **Source:** critique 1 §3.2, critique 2 · **Tags:** [VER]
**Files:** `rl2.ttl:535`, `rl2p.ttl`, `RL2_Protocol.md`, `rl2-shacl.ttl`, `RL2_Semantics.md`, `RL2_IR.md`, `usecases/sla-credit-clause.md`

A Promise carries `promiseState` (Pending/Fulfilled/Violated, no Active) while the Protocol wraps it in a `Requirement` whose `requirementStatus` *does* include Active. "Pending at the Promise level, Active at the Requirement level" is never reconciled. Define the projection between the two (analogous to how `projectObligationState` collapses Active→Pending for promises). **Narrowed by PROM-1 (2026-07-25):** since an executed Agreement contains no Promises (they crystallize to Duties), this reconciliation now concerns only *standalone* promises we choose to runtime-track (e.g. `data-freshness-promise`), never the agreement case. This issue also owns the `rl2:targetNorm` range widening (to `Norm ⊔ Promise`) needed to let a promise-state operand query a standalone promise's state.

**Reconciliation resolved via CONS-2 (2026-07-25):** the projection was already defined in `RL2_Semantics.md` ("Promise and duty states vs protocol requirement status") and cross-referenced from `RL2_Protocol.md:277`; what was missing was wiring from the ontology/SHACL side. `rl2p.ttl`'s `requirementStatus` property and `rl2p-shacl.ttl`'s `RequirementShape` now both carry comments cross-referencing the projection rule, so `requirementStatus = Active` on a Promise-sourced Requirement is documented as intentional at every layer, not just in prose.

**`targetNorm` widening resolved 2026-07-25 — via a `materialize(Offer, Acceptance) → Agreement` design, discussed and approved per `AGENTS.md` §7:**

- **Where the widening is enforced:** `rl2-shacl.ttl`'s `AtomicConstraintShape.targetNorm` now uses `sh:or ( [ sh:class rl2:Norm ] [ sh:class rl2:Promise ] )` in place of the old `sh:class rl2:Norm`, so an Offer-stage clause may target a sibling Promise directly (see `usecases/sla-credit-clause.md`). `NormStateConstraintShape` (the shape specific to `obligationStateOperand`/`dutyPerformerOperand`) was deliberately left Norm-only — those two operands are Duty-state-specific; a Promise-valued target belongs to a `promiseStateOperand` instead (already demonstrated pre-session by `usecases/data-freshness-promise.md`).
- **Why `rl2:targetNorm`'s `rdfs:range` was *not* widened to `owl:unionOf(Norm, Promise)`:** tried this first and it broke `RL2_Primer.md`/`RL2_Vocabulary.md` corpus validation (10 violations each). Root cause: `pyshacl`'s `inference="rdfs"` silently auto-types many terse example values (e.g. `ex:paymentDuty` in `RL2_Primer.md:783`, never explicitly declared `a rl2:Duty` in that fence) via RDFS range-entailment (rdfs3) from `targetNorm`'s single-class range — this is a pre-existing, previously-undocumented crutch the corpus depends on. Plain RDFS entailment cannot auto-type through an `owl:unionOf` blank node (that needs full OWL reasoning, which `pyshacl`'s `rdfs` inference option doesn't do), so widening the range broke every example relying on it. Fix: `rdfs:range` stays the single class `rl2:Norm` (preserves the entailment crutch for the dominant Norm-targeting case); the SHACL `sh:or` above is the real, enforced widening and correctly admits any *explicitly*-typed `rl2:Promise` value. Documented in `rl2:targetNorm`'s `rdfs:comment` in `rl2.ttl` so this doesn't get "fixed" back into a regression later.
- **`materialize(Offer, Acceptance) → Agreement`** — new function defined in `RL2_Semantics.md` §Materialization, immediately after §Crystallization: a one-time, document-level, pre-compilation step (not an IR `Effect` — `RL2_IR.md` §7.2 now cross-references this explicitly, since `evalIR`/`applyEffects` only ever mutate Σ, never a policy's own AST, which the `targetNorm` rewrite requires). It (1) mints a fresh Agreement IRI; (2) crystallizes each Promise clause into a **freshly-minted** Duty + correlative Claim; (3) copies each restated Norm clause under a **freshly-minted** IRI too (not merely for symmetry — `Σ`'s `ObligationState`/`DutyPerformer`/`Requirements` maps are keyed by bare IRI with no Case/Agreement dimension, so reusing any clause IRI across multiple Agreements formed from the same catalog Offer would let two customers' fulfillment states collide); (4) rewrites every `targetNorm` reference through the resulting crystallization/restatement map, so an executed Agreement's `targetNorm` usage is always Norm-valued — consistent with "no Promise survives materialization" (PROM-1); (5) records provenance as `Agreement prov:wasDerivedFrom Offer`, borrowing the PROV-O term by reference (no `owl:imports`, matching how `rl2.ttl` already borrows `dc:` at the ontology-header level) rather than minting a bespoke `rl2:materializedFrom` property — chosen for the richer machinery available if agent/time provenance is ever wanted (`prov:wasGeneratedBy`/`prov:Activity`/`prov:atTime`). This is the corpus's first use of an external vocabulary term on individuals rather than just the ontology document header — deliberate, not a precedent for importing further vocabularies without the same discussion.
- **New corpus example:** `usecases/sla-credit-clause.md` (Use Case 52) — an SLA Offer with a Promise (uptime) and a sibling Duty (service credit) whose condition targets the Promise pre-acceptance, then shows `materialize` producing an Agreement where the same condition has been rewritten to target the crystallized Duty. Explicitly contrasts with `usecases/legal-review-gate.md`, whose Offer→Agreement clause-IRI reuse is safe only because that Offer is accepted exactly once (not a catalog Offer accepted by many customers).
- Full corpus revalidated clean after every step of this fix, including the range-widening revert: `usecases/*.md` (whole-file) → `PASS 0 · WARN-ONLY 52 · FAIL 0 · SKIP 1`; `RL2_Primer.md`/`RL2_Protocol.md`/`RL2_Vocabulary.md` (`--per-fence`) → `PASS 0 · WARN-ONLY 3 · FAIL 0 · SKIP 0`.


## Band 3.5 — Use-Case Corpus Quality — resolved entries

### VALID-1 — Systemic use-case modeling defects ✅ RESOLVED (2026-07-24)

**Status:** Resolved · **Severity:** S2 · **Source:** validation harness · **Tags:** [COV]
**Files:** `usecases/*`

The corpus was never validated before. All recurring defects are now swept and every
use case conforms:

- **State-enum as `rightOperand`.** `rl2:rightOperand rl2:X` (IRI where a literal is

  required) → `rl2:rightOperandRef`. Also applied to IRI-valued right operands in
  chinese-wall, compliance-attestation, no-claim-inference, step-up-auth.

- **Non-canonical `resolutionPath` roots.** Mapped every path to a canonical root

  (`agent`/`asset`/`state`/`context`/`request`) — e.g. `license.*` → `state.License.*`,
  `session.*` → `context.session.*`, `event.schemaChange.*` →
  `state.Events.SchemaChangeEvent.*`, `party.*` → `agent.*`.

- **Nonexistent operators.** `rl2:gteq`/`rl2:lteq` → `rl2:gte`/`rl2:lte`.
- **Prohibition using `rl2:action`** → `rl2:prohibitedAction` (chinese-wall,

  concurrent-seats, quality-circuit-breaker, schema-evolution, trial-period).

- **Incomplete `rl2p:Requirement`/`Case`/`EvaluationResult`** — completed all required

  fields (`sourceNorm` typed, `sourcePolicy`, `imposedTime`, `requirementStatus`;
  `evaluatedRequest`/`evaluationTime`; Case scaffolding) in runtime-evaluation,
  claim-counterclaim; fixed wrong property names (`request`→`evaluatedRequest`,
  `evaluatedAt`→`evaluationTime`) and RDF-list-as-range mis-typing (use repeated
  values, not `( )`).

- **Missing required norm props** — added `subject` to a `Power`, `object` to a `Duty`,

  completed a bare `Privilege`, unwrapped a single-operand `and`.

- **Set membership** now uses the canonical `AssetCollection` + `member` referenced by

  `rightOperandRef` (geo-restriction, multi-certification), never an inline RDF list.

### VALID-2 — Draft use cases contain non-parseable pseudo-Turtle ✅ RESOLVED (2026-07-24)

**Status:** Resolved · **Severity:** S3 · **Source:** validation harness · **Tags:** [COV]
**Files:** was ~11 `usecases/*.md`

All draft use cases are now self-contained and complete: subjectless `rl2:condition [...]`
fragments were promoted to full norms, `...`/`…` elisions removed, and foreign-vocabulary
illustrations (ODRL `tpl:`/`pav:`/`odrl:`) moved out of `turtle`-tagged fences into plain
code fences. A real ontology bug was also fixed: `rl2:EventPathTypeShape`'s SPARQL used
`\.` (invalid SPARQL string escape), which crashed validation for **any** policy using a
`state.Events.*` resolution path — now double-escaped to `\\.`.

### VALID-3 — Spec-doc examples should validate too

**Status:** Resolved · **Severity:** S3 · **Source:** validation harness · **Tags:** [COV]
**Files:** `RL2_Semantics.md` ✅, `RL2_Primer.md` ✅, `RL2_Vocabulary.md` ✅, `RL2_Protocol.md` ✅

The same "every example validates or is empty" standard applies to the spec docs, not
just the use cases. The harness gained a **`--per-fence`** mode for this: each
```turtle``` fence is validated as its own graph (ontology merged in), because a
reference doc's fences are *independent* illustrations — a shared example IRI reused
across sections must not merge into one graph (whole-file mode would force false
cardinality conflicts). Use cases keep whole-file mode (their fences build on each
other). Run: `uv run tools/validate.py --per-fence <doc>.md`.

All four spec docs now pass per-fence (0 fail). Fixes were of three kinds:
(1) demote genuine narration fragments (state-machine transition triples, bare
predicate snippets) to plain code fences; (2) complete labeled examples so each is
valid standalone (define the Power/Duty/Promise/Policy an example references; use
`xsd:anyURI` literals for `policyGeneration`, not IRIs); (3) a real ontology bug in
`rl2p.ttl` — `rl2p:fulfillmentEvidence` had `rdfs:domain rl2p:Requirement`, but the
"Fulfillment as Context" pattern legitimately uses it on `rl2p:ContextAssertion` too.
A second `rdfs:domain` declaration doesn't union domains, it conjuncts them (RDFS
requires membership in *all* declared domains simultaneously) — the fix was to remove
the domain restriction entirely rather than work around it in the docs.

`RL2_Protocol.md`'s 9 originally-failing fences (its shared loan-access /
data-contract worked example, where each fence references entities defined only in
*other* fences) were made self-contained per the same recipe used for
Primer/Vocabulary: define the source norm/promise (typed), its source Policy (with
≥1 clause), the referenced Request (action/asset/agent/time), the Case
(initialRequest/caseCreated/caseStatus), and, for `requirementFulfilled` assertions,
the performer. Confirmed no regressions: Semantics/Primer/Vocabulary still pass
per-fence, and all 51 use cases still pass whole-file.

### VALID-5 — DeepSeek use-case pass: accuracy check + marker removal ✅ RESOLVED (2026-07-26)

**Status:** Resolved · **Severity:** S2 · **Source:** user-directed audit · **Tags:** [COV]
**Files:** `usecases/*` (all 52), `usecases/README.md`

An external model (DeepSeek) was asked to work through the use-case corpus and mark
its edits with an `editedby: Deepseek` frontmatter line. Every one of the 52 marked
files was checked against the pre-edit git version and, where needed, fixed:

- **22 files** had only a placeholder `## RL2 Model` (`*To be added after pattern
  documentation is approved.*` / `# Placeholder for RL2 implementation`) — 5 had been
  emptied back to that placeholder, 17 had never gotten past `Status: DRAFT`. Wrote
  real, self-contained Turtle for all 22, matching each file's own Normative
  Structure/Profile Requirements sections and established corpus idioms (`Privilege`/
  `Duty`/`Prohibition` gated by `AtomicConstraint` or `EventConstraint`, wrapped in an
  `Agreement`/`Set`/`Policy`). One drafting slip caught before validation: typed a
  fulfillment-evidence IRI as `a rl2p:Evidence`, a class that doesn't exist in
  `rl2p.ttl`/`rl2p-shacl.ttl` — fixed by using the bare-untyped-IRI idiom
  `RL2_Protocol.md` already establishes for `rl2p:fulfillmentEvidence` targets.
- **6 files** (`claim-counterclaim`, `purpose-restriction`, `approval-revocation`,
  `power-to-grant`, `internal-use-only`, `derived-data-restriction`) had real
  DeepSeek-authored Turtle beyond the marker line. All validated correctly against
  `rl2-shacl.ttl`/`rl2p-shacl.ttl`; `claim-counterclaim.md` had one editorial defect
  (a sentence duplicated both before and after the code fence from how the edit moved
  content out of "Protocol Representation" into "RL2 Model") — removed the duplicate.
- **28 files** carried only the marker line with no content change — confirmed each
  still had a complete, already-valid `RL2 Model` section.

All 52 `editedby: Deepseek` frontmatter lines then removed. Full corpus revalidated
clean after every step: `usecases/*.md` (whole-file) → `PASS 0 · WARN-ONLY 52 · FAIL 0
· SKIP 1`. `usecases/README.md`'s "52 complete, 0 draft" claim, previously aspirational,
is now actually true — no placeholder or DRAFT-only `RL2 Model` sections remain
anywhere in the corpus (individual files' own `**Status:** DRAFT` frontmatter field
was left untouched — that field is editorially stale across the corpus and tracking
its accuracy is a separate, not-yet-scoped cleanup from the RL2-Model completeness
checked here).

---


## Band 4 — Implementation

**Permanently out of scope as of SCOPE-1 (2026-07-29).** See § Open Decisions → SCOPE-1 for the
full rationale. IMPL-1..3 are closed below with their history preserved, not deleted, since
they record real prior decisions (the Dafny→Go toolchain choice, the de-risking-spike design)
that a future implementation effort could still pick back up.

### IMPL-1 — Dafny core modules

**Status:** ✅ Resolved — out of scope (SCOPE-1, 2026-07-29) · **Severity:** S1 · **Source:** backlog Phase 1, fix §12 · **Tags:** [VER]
Translate `RL2_Semantics.md` to Dafny. Blocked on SEM-4 (IR) and SEM-5 (target matching). Toolchain decided (Dafny→Go).

**De-risking spike required first (fix.md Task 12/§6.2, confirmed by fix2.md §6):** before full commitment, replicate a minimal evm-dafny-style proof (3-4 opcodes — DUP, DROP, ADD, IF) in Dafny 4.11 (pin this version to avoid nightly churn), extract to Go, and confirm the generated Go compiles and runs correctly. A 2-3 day spike, using [Consensys/evm-dafny](https://github.com/Consensys/evm-dafny) as the architectural reference — a verified stack VM in Dafny with the same shape RL2 needs. fix2.md notes that `RL2_IR.md`'s design of keeping deontic logic in the AST tree-walk and only conditions in the bytecode VM shrinks the verification surface to ~30 opcodes of pure boolean evaluation, more tractable than the original ~45-opcode `design-forth-ir.md` estimate. If the spike succeeds, proceed with Dafny→Go as planned. If it fails (Go extraction issues, proof friction), fall back to **Creusot** (verify Rust directly — eliminates the extraction gap entirely, but is pre-1.0 and lacks a `--enforce-determinism` equivalent).

**Closed 2026-07-29 (SCOPE-1):** the stack-bytecode IR this spike targeted no longer exists (RL2_IR.md now specifies a direct AST interpreter, `evalCondition`), and the project no longer has an implementation track for any IR representation. This entry's content is retained as a historical record of the toolchain evaluation, not an active plan.

### IMPL-2 — Discharge proofs S1 / S4 / S6

**Status:** ✅ Resolved — out of scope (SCOPE-1, 2026-07-29) · **Severity:** S1 · **Source:** backlog, fix · **Tags:** [VER]
S1 Determinism, S4 Duty-state consistency, S6 Totality. Fold SEM-8's obligations in. These substantiate the "formally verified" claim.

**Closed 2026-07-29 (SCOPE-1):** S1/S4/S6 remain documented design properties
(`RL2_Semantics.md` § Proof Obligations, `RL2_IR.md` §5/§9), but are no longer proof
obligations for a mechanized evaluator — there is none. A future implementation should be
checked with semantic conformance and differential tests (`RL2_IR.md` §10).

### IMPL-3 — Go extraction, CLI, property tests

**Status:** ✅ Resolved — out of scope (SCOPE-1, 2026-07-29) · **Severity:** S2 · **Source:** backlog · **Tags:** [VER]
`rl2-eval --policy p.ttl --request r.json`; property-based tests; validate against use cases 1–17.

**Closed 2026-07-29 (SCOPE-1):** no reference implementation is planned; this entry described the last stage of a track the project no longer pursues.

---


## Band 5 — Documentation Hygiene — resolved entries

- **DOC-1** — ✅ Resolved (v0.6). Spec-suite docs normalized to `version: "0.6"` / `date: 2026-07-24` (Semantics, Architecture, Vocabulary, Primer, Protocol, References, README banner). RDF artifacts keep truthful `owl:versionInfo`: `rl2.ttl` 0.6 (changed), `rl2p.ttl` 0.5 (unchanged); Vocabulary footer notes the split. `RL2_ODRL_Comparison.md` retains its own doc version (now 1.1, see DOC-4). `S3`.
- **DOC-3** — ✅ Resolved (2026-07-25). `codex.md`/`gemini.md`/`persona.md` were already gone; found and removed a byte-identical duplicate `claude.md` (redundant with `CLAUDE.md`). Fixed the stale `persona.md` references in `design-canonical-form.md:25,46` → `AGENTS.md`. `S3`.
- **DOC-4** — ✅ **Resolved (2026-07-26).** Decision reversed on the "merge into `RL2_Primer.md`" plan: the user determined `RL2_ODRL_Comparison.md` should stay a **standalone** document — the motivation/use-case/justification content it needs to carry doesn't fit the Primer. All previously-flagged staleness fixed in place instead of via merge: §3.2 now names Dafny→Go (not Why3/Coq/Lean); §1.1 no longer cites the nonexistent `rl2-media-profile.ttl`; §2.2's Σ.Events description corrected to "typed, temporally-ordered index" (matching `RL2_Semantics.md`, and confirming this specific claim was actually already accurate, not stale); §2.1 rewritten to reflect PROM-1's crystallization model (Promise → Duty + correlative Claim on Offer→Agreement acceptance). Also added a new **Quantitative Comparison** section (ontology metrics vs. ODRL 2.2/PROV-O/DCAT 3/ORG/FOAF) and fact-checked every RL2-specific figure against the current repo: found and corrected an inaccurate "RL2 full" row (undercounted classes/properties/enums and overstated size — `rl2p.ttl`'s 7 classes/26 objProps/12 dataProps/2 enums weren't rolled into the combined-suite total). `S2`→resolved.
- **DOC-6** — ✅ Resolved (2026-07-25). `FAQ/RL2_FAQ.md:23` "Rights & Licenses 2" → "Rights Language 2"; `FAQ/RL2_FAQ.md:111-118`'s pre-CANON-2 `ProviderPromise`/`ConsumerPromise`/`ThirdPartyPromise` terms replaced with a description of the unified `rl2:Promise` class + `promisedAction`/`promisedState`/`promisedDuty`. Same stale terminology also found and fixed in `RL2_References.md:329` (Tun-Sollen glossary entry). Remaining terminology consistency (`ObligationState` not DutyState, `Norm` not Rule, Requirement-wraps-Duty clarity) not yet audited beyond these two files — reopen if found elsewhere. `S3`.
- **DOC-7** — ✅ Resolved (2026-07-25). `backlog.md` merged into this log. Open design decisions are now § Open Decisions (OPEN-1..3). Work items and success criteria were already tracked as IMPL-1..3 and S1/S4/S6. `backlog.md` deleted. `S3`.
- **DOC-9** — ✅ Resolved (2026-07-25), then superseded by SCOPE-1 (2026-07-29).
  The FAQ now describes the active direct-AST specification and no committed implementation
  backend. The earlier Forth-IR → Dafny → Go wording recorded by this item is historical. `S2`.
- **DOC-10** — ✅ Resolved (2026-07-25). `RL2_References.md:446` now cites `RL2_ODRL_Comparison.md` (was the nonexistent `RL2_ODRL_Coverage.md`). `S3`.
- **DOC-11** — ✅ Resolved (2026-07-25). `RL2_Semantics.md:1684`'s dangling reference to `RL2_ResearchPlan.md` replaced with pointers to `RL2_IR.md` (compilation target) and `issues.md` Band 4 (phased implementation plan) — the artifacts that actually carry this content now. `S3`.
- **DOC-12** — ✅ Resolved (2026-07-26). `AGENTS.md` §12 Key Files table listed a `CLAUDE.md` row (file removed per DOC-3) and a `fix.md` row (a transient scratch file, not a persistent repo artifact); both rows removed. Also fixed a stale `fix.md §6.2` cross-reference in `AGENTS.md` §2 to point at `research/verification-toolchain-comparison.md`, which is where that toolchain-comparison content actually lives now. `S3`.
- **DOC-13** — Not applicable (checked 2026-07-26). fix.md claimed the `materialize()` section (added for PROM-7) was missing from `RL2_Semantics.md`'s table of contents. Verified: `RL2_Semantics.md` has no Table-of-Contents section at all — unlike `RL2_Primer.md`/`RL2_Protocol.md`/`RL2_Vocabulary.md`/`RL2_References.md`, which all have one. Nothing to add an entry to; adding a full TOC to a 1749-line, 30-heading document is a separate, larger undertaking than what fix.md described, and out of scope for this pass. `S3`.
- **DOC-14** — ✅ Resolved (2026-07-26). `design-forth-ir.md` and `design-canonical-form.md` (both historical/superseded design-rationale docs per their own top-of-file disclaimers) moved from repo root to `research/`, alongside `verification-toolchain-comparison.md`. Inbound references updated: `RL2_IR.md` (5 mentions) and `issues.md` (SEM-4 entry) now say `research/design-forth-ir.md`. Root now holds only active, authoritative documents. `S3`.
- **DOC-15** — ✅ Resolved (2026-07-26). `RL2_Primer.md`'s YAML frontmatter had two editorial fields (`audience`, `prerequisites`) alongside the normative `title`/`subtitle`/`version`/`status`/`date` fields. fix.md's action line suggested dropping the frontmatter entirely, but `version`/`date` are load-bearing for DOC-1's cross-doc version normalization — removing them would have regressed that. Kept `title`/`subtitle`/`version`/`status`/`date`, dropped only `audience`/`prerequisites`; the markdown `## Table of Contents` (unaffected) remains the one place readers navigate section structure. `S3`.

---

## Resolved

### SCOPE-1 — Drop the stack/Forth IR and the Dafny/Go mechanization track; scope stops at specification

**Resolved 2026-07-29.** RL2's IR collapses from a two-lowering pipeline
(`Turtle → normalized AST → condition bytecode`, the latter a Forth-style stack VM with ~30
opcodes) to a **single lowering**: `Turtle → normalized AST`, with conditions evaluated by
direct recursive interpretation (`evalCondition`, RL2_IR.md §5) over the same AST. There is no
compiled bytecode, no stack machine, no opcode set, and no second equivalence obligation for a
VM layer — `evalCondition(c, env, Σ)` unifies what were previously two evaluation surfaces
(pure conditions taking only `Env`, `EventConstraint` handled separately as an "AST-layer"
case reading Σ) into one function taking both.

Separately, and independently motivated: RL2 **drops the planned Dafny→Go mechanization
track** (formerly IMPL-1..3, Band 4) entirely. The project's scope stops at a **thoroughly
reviewed docs + spec + semantics + IR design** — not a mechanized proof, not a reference
implementation. Confidence in the design comes from differential testing against the
denotational reference (the Cedar-spec model, RL2_IR.md §10), not from a proof assistant.

**Why:** the stack-VM layer existed to give the deontic tree-walk a "pure, verifiable" core to
call into — a purity boundary that only mattered if something downstream (Dafny) needed a
small, syntax-directed, side-effect-free evaluator to verify. Once mechanized verification is
out of scope, that boundary has no job left to do: it added a second representation, a second
correctness lemma (VM-correctness, §9b), and an artificial split between pure and
Σ-reading condition evaluation, for no behavioral difference in what policies can express or
how they're evaluated. Dropping both the VM and the proof track at once is simpler than
dropping either alone, since the VM's main raison d'être *was* being a Dafny verification
target.

**What changed:**
- **`RL2_IR.md`** — §2 (pipeline diagram, now single-lowering), §3.2 (dropped the bytecode
  lowering table column), §5 (replaced the `Value`/`Instr`/`VM` datatypes and opcode set with
  `evalCondition(c, env, Σ): Value`, a direct pure recursive function over `Condition`), §6-§9
  (interpreter framing; §9b restated as the "interpreter-correctness lemma"), §10 (compiler
  trust model rewritten around differential testing only, no "verified kernel"/evm-dafny
  precedent), §11 (implementation handoffs replaced with an out-of-scope note), References.
- **`RL2_Architecture.md`** — IR structure description, Open Design Questions table, "Gaps
  addressed" mechanization-path bullet, Design Goals (#3 reworded from "Mechanizable" to
  "Specifiable"), "Normative implementation" paragraph replaced with a scope statement.
- **`RL2_Semantics.md`** — "Proof scope and normative artifact" rewritten (no more
  "reference evaluator written in Dafny and extracted to Go" as the normative artifact); the
  "Mechanization"/"Target Platforms"/"Dafny Example" sections removed (the Dafny Example was
  already stale per SEM-12 and is now moot); "Proof Obligations" reframed as documented design
  properties, not obligations for a verified implementation.
- **`AGENTS.md`** — §1 drops "formal verification" from RL2's description; §2 Project Phase's
  "Next: Dafny/Go implementation" plan replaced with this scope decision; §8's "Dafny
  encodability" formal property renamed "Specifiability."
- **`FAQ/RL2_FAQ.md`, `RL2_ODRL_Comparison.md` §3.2, `RL2_ExternalData.md` §7,
  `profiles/README.md`** — Forth-bytecode/Dafny→Go mentions reworded to describe the direct
  AST interpreter and the specification-only scope.
- **`issues.md`** (this file) — Band 4 (IMPL-1..3) closed out-of-scope rather than deferred;
  WP-8's `S8b`/`IMPL-2` and `L1`/`L2`/`IMPL-1` sub-items struck; the "Verifiable" north-star
  bullet and the Priority-bands/sequencing-decision prose updated to reflect the narrowed
  scope.
- **`research/design-forth-ir.md`, `research/verification-toolchain-comparison.md`** — marked
  superseded; retained for historical rationale only, not as active design input.

**Not affected:** the ontology (`rl2.ttl`, `rl2p.ttl`, `rl2-shacl.ttl`, `rl2p-shacl.ttl`) — this
is a pure IR/scope decision, no `.ttl` file changed. The Kleene three-valued logic (S2), the
derive-then-resolve two-phase evaluation (I/O logic), the effect algebra (§7), and all
Band 0-3/5-6 ontology and semantics work are unaffected — this decision is scoped entirely to
*how conditions are evaluated* and *what the project commits to building*, not *what RL2
means*.

### ACT-1 — Action ontological status & hierarchy mechanism

**Resolved.** Actions are named **individuals** of `rl2:Action`; hierarchies use `rl2:includedIn` (transitive object property), not `rdfs:subClassOf`. No punning; subsumption is bounded graph reachability (`ASK { ?req rl2:includedIn* ?pol }`), not OWL reasoning; ODRL-compatible. Optional SKOS alignment kept out of core. Applied to `rl2.ttl`, `RL2_Semantics.md`, `RL2_Vocabulary.md`, `CLAUDE.md`, and affected use cases. Ingestion is tolerant: legacy `rdfs:subClassOf` between Action individuals is transpiled with a diagnostic.

### ACT-2 — Action subsumption asymmetry (request matching vs duty fulfillment)

**Resolved.** Subsumption applies **uniformly** across norm types via a read-time helper `performed(a,x,s,Σ) := ∃x′ : Σ.Performed(a,x′,s) ∧ (x′ = x ∨ x′ ⊑ x)`. `Σ.Performed` stays an exact log; the helper adds subsumption at query time. Decisive case: performing `fineTune` must violate a prohibition on `trainModel` when `fineTune includedIn trainModel`; the same logic extends to duty fulfillment. All `Σ.Performed(...)` checks in `RL2_Semantics.md` replaced with `performed(...)`. Profiles needing exact-match should define the action at the exact level.

### CANON (v0.6) — Canonical-form band

**Resolved 2026-07-24 (ontology → 0.6).** Adopted the invariant *exactly one valid RDF shape per normative proposition* and applied it:

- **CANON-5 / CANON-1.** Invariant documented in `RL2_Architecture.md` §Canonical Form and `AGENTS.md` §6. Condition composition confirmed as conjunction (`n.effectiveCondition = And(P.condition, n.condition)`, already in semantics); canonical rule = author at narrowest scope; policy conditions pushed down during IR normalization (enforcement is an IR obligation → **SEM-4**).
- **CANON-2.** Retired the polymorphic `rl2:promiseContent` / `rl2:PromiseContent` union. Added three disjoint properties: `rl2:promisedAction` (Tun-sollen), `rl2:promisedState` (Sein-sollen), `rl2:promisedDuty` (suretyship). `rl2:object` domain broadened to `Norm ∪ Promise`. `PromiseShape` now requires exactly one via `sh:xone`. Semantics `contentHolds`/`deadline`/`linkedDuty`/remedial rules rewritten over the tagged union (`contentHolds` reuses the ACT-2 `performed()` helper); `restoreAction`/`objectOf` made total (PromisedState remedial default → **SEM-1**). `promisedDuty` now has real semantics, resolving most of **PROM-5**. Migrated use cases 8 (`promisedAction`) and 11 (`promisedState`, dropping the invented `rl2:recurrence` → **EXPR-1**).
- **CANON-3.** `rl2:Prohibition` kept as the sole negative-duty form; semantics now state it is a duty-to-refrain whose correlative **Claim** is held by its `counterparty` (or the grantor), derived not authored.
- **CANON-4.** Unified normative roles on `rl2:subject` (right-holder) / `rl2:counterparty` (duty-bearer); **removed** `rl2:claimHolder` / `rl2:claimAgainst`. `ClaimShape` and all references migrated (Primer, Vocabulary, CLAUDE.md, use cases claim-counterclaim / no-claim-inference / pass-through-terms).

No backward-compatibility aliases (clean break, per decision). `rl2.ttl` and `rl2-shacl.ttl` parse clean; no residual references outside explanatory comments.
