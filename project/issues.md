# RL2 Issues — Active

Active tracker for the RL2 language, semantics, ODRL migration, conformance, and documentation:
open decisions and the current remediation backlog. **Completed work, resolved
entries, and the full changelog live in [issues-log.md](issues-log.md).**

> **Convention.** When an issue is resolved, move its entry (decision + rationale)
> to `issues-log.md`; if open work still references it, leave a one-line pointer in
> its band here. New review sweeps append to the log's changelog.

**Latest (2026-07-31): SCOPE-2 supersedes the former protocol/IR-centered execution order.**
The governing boundary is `../spec/RL2_Scope.md`; progress and file dispositions are maintained
in `reorganization-plan.md`. The older priority bands and integration-sweep tables below remain
useful evidence, but their old §7 sequence is no longer authoritative.

---

## How to use this file

Each issue has an ID, a status, a severity, the source(s) it came from, the files it touches, and a north-star tag. Work proceeds top-down within each priority band. On resolution, move the entry to `issues-log.md` (see that file's ACT-1/ACT-2 for the format).

**North star.** RL2 aims to be an ODRL successor built for the reality that *nobody authors policies by hand any more*. Its two governing quality attributes are therefore:

- **Generatable** — a model generating a policy should have exactly one correct RDF shape to emit for any given normative proposition. No authoring-convenience variation.
- **Verifiable** — every construct must have deterministic, precisely specified, bounded semantics
  so independent evaluators can be tested against the same observable results. SCOPE-2 requires a
  specification precise enough to implement and verify, but no normative IR, implementation, or
  mechanized proof.

Issues are tagged **[GEN]** (affects generatability / canonical form), **[VER]** (affects verifiability / formal semantics), or **[COV]** (vocabulary/coverage completeness) to show which attribute they serve. Many serve more than one.

**Legend.** Status: `Open` · `In progress` · `Decision needed` · `Resolved` · `Deferred`. Severity: `S1` (blocks the north star / core soundness) · `S2` (significant gap) · `S3` (polish / hygiene).

---

## SCOPE-2 Active Workstreams — authoritative order

| ID | Workstream | Status | Consumes or replaces |
|---|---|---|---|
| S2-R1 | Repository and documentation reorganization | In progress | SCOPE-1 file hierarchy; ROADMAP-D2 |
| S2-C1 | Pure evaluation contract and immutable `WorldSnapshot` | ✅ Resolved 2026-07-31 — immutable snapshot contract, pure `Eval` integration, component vectors, and protected annotation alignment; see [issues-log.md](issues-log.md) | Stateful `Σ`, C3-3 core fragment, C3-7 snapshot fragment |
| S2-C2 | Declarative Duty and Promise status semantics | ✅ Resolved 2026-07-31 — structural Achievement/Maintenance forms, finite DutyWindow, pure status derivation | C3-2; transition-oriented WP-4/S4 |
| S2-C3 | Duty attachment and decision interaction | ✅ Resolved 2026-07-31 — one canonical prerequisite relation; independent Duties have no access effect; protocol phases excluded from core | C3-4; WP-4/S7 |
| S2-C4 | Pure Offer→Agreement transformation | ✅ Resolved 2026-07-31 — explicit Acceptance value and identity allocation; action/state crystallization; typed rejection; complete reference rewriting; Offers non-operative before acceptance | C3-5 without runtime effects or persistence |
| S2-C5 | Canonical RDF→AST projection | Open | C3-8; normative portions of the former IR |
| S2-M1 | ODRL 2.2 disposition and translation matrix | Open | OPEN-3; WP-7 |
| S2-T1 | Structural and semantic conformance suite | In progress | VALID-4; revised golden vectors; 52-use-case migration |
| S2-D1 | Reader-document consolidation and generated vocabulary checks | Open | DOC-2; ROADMAP-D2 |

Order within the core is: **S2-R1 → S2-C1 → S2-C2 → S2-C3/S2-C4 → S2-C5/S2-M1 →
S2-T1 → S2-D1**. Conformance cases and migration fixtures are added continuously as each semantic
decision lands.

### SCOPE-2 disposition of former stoppers

| Former item | SCOPE-2 disposition |
|---|---|
| C3-1 result/error algebra | Retained core foundation; resolved work stands |
| C3-2 temporal duty model | Reframed as declarative status over snapshot evidence (`S2-C2`) |
| C3-3 event log | Event storage/order/replay moves to future protocol; evidence identity and selection remain in `S2-C1` |
| C3-4 duty attachment | Retained core (`S2-C3`) |
| C3-5 materialization | Retained only as a pure policy transformation (`S2-C4`) |
| C3-6 protocol projection | Future companion protocol; no longer a core blocker |
| C3-7 resolved context | Immutable snapshot/error contract remains core; trust workflow and live source calls move outside core |
| C3-8 canonical projection | Retained core (`S2-C5`) |
| WP-6 Case/replay protocol | Future companion protocol |
| IR effects, CAS, retry, commit validation | Future reference implementation/protocol |

Items moved out of core are deferred by scope, not considered semantically resolved. Their detailed
findings remain below until they are moved to a future-work tracker.

Resolved S2-C1 through S2-C4 decisions and validation records are archived in
[issues-log.md](issues-log.md). **S2-C5 is next.**

---

## Open Decisions

Forward-looking design decisions deferred until publication or spec stability.

### OPEN-1 — Namespace URI

**Status:** Deferred · **Severity:** S3
**Current:** `https://rl2.example/ontology#`
**Options:** `https://w3id.org/rl2/` (persistent) or institutional.
Decide before publication.

### OPEN-2 — ODRL owl:imports

**Status:** Deferred · **Severity:** S3
Add `owl:imports <http://www.w3.org/ns/odrl/2/>` before publication. Depends on OPEN-1 (namespace decision).

### OPEN-3 — ODRL→RL2 transpiler

**Status:** Open · **Severity:** S2 · **Tags:** [COV]
Create an ODRL 2.2 → RL2 transpiler (flatten `inheritFrom`, map `odrl:Permission`→`rl2:Privilege`, etc.). Needed for migration path and to demonstrate RL2 as a true ODRL successor. Cross-ref: `fix.md` Task 13. Blocked on spec stability (Bands 1-3).

### OPEN-4 — Track W3C ODRL Workshop outcomes for alignment

**Status:** Open · **Severity:** S3 · **Source:** fix.md §1.1, fix2.md §7
The W3C Workshop on the Future of ODRL (20-21 July 2026, London; co-chaired by Iannella, Fornara, Rodríguez-Doncel) covered gaps in the ODRL Information Model, formal semantics, policy evaluation engines, constraint modeling, and conformance/testing mechanisms — all areas RL2 addresses. No V3.0 requirements document or use-case catalog existed at review time; outcomes weren't yet published. Action: once published, check RL2's direction against the workshop's requirements/use-case output. Strategic opportunity to position RL2 as a workshop-informed ODRL 3.0 candidate contribution.

---


---

## Priority bands (work order)

**Band 0 — Canonical form (the generatability thesis).** CANON-1..5. Establishes the "exactly one shape per proposition" invariant that everything downstream depends on. Do first: later coverage work should be authored in canonical form from the start.

**Band 1 — Formal-semantics soundness (verifiability).** SEM-1..14. Closes the gaps that block a precise, testable specification and the S1/S4/S6 documented properties, including remedial relations (SEM-1), target quantification (SEM-2), target matching (SEM-5), external-data binding (SEM-13), and the closed-world stance (SEM-14). SEM-9–12 are resolved or superseded.

**Band 1.5 — Protocol SHACL & cross-document consistency.** CONS-1..6. SHACL/protocol-level bugs and doc-vs-ontology mismatches surfaced by the fix.md/fix2.md sweep — distinct from Band 3.5's use-case-corpus scope.

**Band 2 — Hohfeld & Promise completeness (defensibility).** HOHF-1..5, PROM-1..8. Makes the theoretical claims true, not just asserted.

**Band 3 — Expressiveness coverage.** EXPR-1..8. Recurrence, quorum, temporal arithmetic (EXPR-1/2/3 decided 2026-07-25 — all profile-level/excluded, no core impact), collections, delegation, revocation (EXPR-4/5/6 still open, confirmed independent of Band 1 IR work), and implies/iff + ODRL relation/partOf coverage (EXPR-7/8, both deferrable).

**Band 3.5 — Use-case corpus quality.** VALID-1..4. Systemic modeling defects and non-parseable drafts surfaced by the new `tools/validate.py` SHACL harness; spec-doc examples brought up to the same validation standard; VALID-4 flags that the corpus doesn't yet exercise conflict resolution, the IR-compilation path, or external data.

**Band 4 — Implementation.** **Permanently out of scope as of SCOPE-1 (2026-07-29)** — see Resolved. IMPL-1..3 (Dafny kernel, proofs, Go extraction) are closed out-of-scope, not deferred: the project's scope stops at a reviewed docs+spec+semantics+IR design, with no committed implementation or mechanized-proof track.

**Band 5 — Documentation hygiene.** DOC-1..11. Version normalization, dedup, navigation, and (new) fixing three concrete stale/incorrect cross-references (DOC-9/10/11).

**Band 6 — AI-generation tooling.** LLM-1. Prompt templates, few-shot examples, and a validation harness for NL→RL2 generation — not yet started.

**Current sequencing decision (2026-07-25, scope narrowed 2026-07-29 by SCOPE-1).** Goal right now is to *finish the ontology/spec/semantics* — documentation plus a thoroughly reviewed IR design — not to build or prove an implementation. Agreed order: **PROM-1 → SEM-1/2/3 → SEM-4 → SEM-5 → SEM-6/7/8 → HOHF-1/2 → HOHF-4 → PROM-2..8 → DOC-2/4/5/6.** Band 4 (IMPL-1..3, Dafny/Go coding) and OPEN-1/2/3 are **permanently out of scope** per SCOPE-1 — not deferred pending later resourcing, but dropped from the project's goals entirely. Each item is discussed and decided before its file(s) are touched; ontology edits (`rl2.ttl`/`rl2p.ttl`/`*-shacl.ttl`) require explicit sign-off per AGENTS.md §7. **PROM-1 resolved 2026-07-25 — interim milestone. SEM-4 (IR definition) resolved 2026-07-25 — `RL2_IR.md` authored; next is SEM-5 (target matching), then SEM-1/2/3.** The new **SEM-9..14** and **CONS-1..6** (2026-07-25, merged from fix.md/fix2.md) slot into the same agreed order as sharpenings of SEM-4/SEM-5 work — no resequencing needed; they surface as that work is picked up, not before.

---


## Remediation Roadmap — deep sweep (2026-07-26) — open WPs

> **WP-0…WP-5 are ✅ resolved**; their full Done-blocks, the dependency-spine intro,
> and the reconciliations note are in [issues-log.md](issues-log.md). The integration
> follow-ups that re-open WP-2…WP-5 on the *integration* dimension are tracked in
> § Remediation Roadmap — integration sweep below. Open WPs:

### WP-6 — Protocol projection + replay

**Depends on:** WP-3, WP-4 · **Status:** Open

- **P1** — CaseEvents append-only log (id, sequence, time, actor, prev-version, payload); derive `caseStatus`; persistence/concurrency stated outside SHACL. *(new)*
- **P2** — replayable `EvaluationResult`: policy generation, evaluator/spec/profile versions, combining config, input/context digest, external-source versions, state-snapshot version, structured result/error code; disambiguate `matchedPolicies` (evaluated vs applicable vs decision-contributing). *(new; consumes S2's algebra)*
- **P3** — validate Requirement→sourceNorm∈sourcePolicy and active-requirement→evaluated-case linkage/provenance. *(new; consumes WP-3's authoritative model)*
- **P4** — enforcement phases (pre / concurrent / post) instead of one `PermitWithObligations`; blocking-vs-ongoing requirements; transformation/advice output; token issue/expiry/revocation. *(new)*

### WP-7 — ODRL behavioral compatibility

**Depends on:** WP-2 (C5), WP-4 (S7), WP-6 (P4) · **Status:** Open · The largest *volume* but regular work with a known decision rule.

- **O1 / OPEN-3** — generate a term-by-term compatibility inventory from the W3C ODRL ontology; assign each of the five dispositions (lossless core / lossless profile / bounded expansion / rejected-with-diagnostic / intentionally-unsupported); back with golden import tests. *(sharpens OPEN-3)*
- **O2b / O2c / EXPR-8** — field/operator/profile-term mappings (`hasPart`/`isPartOf`/`andSequence`/`consequence`/`remedy`/`inheritFrom`/collections/refinements); lossless import behavior — **blocked on S4/S6/S7/P4** for before-action duties, remedies, ordered constraints, and conflict. *(sharpens OPEN-3, EXPR-8)*

### WP-8 — Proofs, tests, toolchain, closeout

**Depends on:** WP-2 … WP-7 as noted · **Status:** Open · The trailing Class-2 volume + dependent Class-1 consolidation.

- ~~**S8b / IMPL-2**~~ and ~~**L1 / L2 / IMPL-1**~~ — **struck, out of scope (SCOPE-1, 2026-07-29).** These sharpened the stateful-trace/totality proofs and the Dafny→Go de-risking spike, both part of the dropped mechanization track; see Resolved (IMPL-1/2/3).
- **T1 / VALID-4** — convert the 52 narrative use cases into golden `input/AST-digest/state/context/envelope/decision/effects/next-state` vectors + negative vectors + the coverage matrix (§11), as semantic conformance vectors for a future `evalCondition`/`evalIR` implementation (RL2_IR.md §10). *(sharpens VALID-4)*
- **D1** — W3C-style conformance classes + stable requirement IDs + RFC 2119 boilerplate, once the semantic decisions are closed. *(new; Band 5)*
- **A1 / LLM-1** — the strict parse→validate→type-check→normalize→compile ingestion pipeline with unknown-term/heuristic-repair rejection + adversarial-input tests. *(sharpens LLM-1, §7)*
- **R1b** — separate privacy-profile category classes from runtime individuals; add profile SHACL; narrow the GDPR legal claims. *(new; §14)*
- **ROADMAP-D2** (dependent) — final editorial consolidation per the source hierarchy; generate vocabulary/cardinality/namespace tables rather than hand-maintaining them. *(extends Band 5 DOC-2; distinct from the Class-2 finding D2 below)*

---


## Remediation Roadmap — integration sweep (2026-07-29)

Source: a fresh external review saved as `fix.md` / `fix-codex-original.md` (both scratch, deleted after this merge — same disposition as every prior sweep). It re-reviews the post-SCOPE-1, post-WP-5 state and **endorses the execution model** (direct normalized-AST; no Forth IR / Datalog / OWL reasoner / proof assistant needed). Its headline is that the remaining problem is **integration**: the WP-2…WP-5 result-algebra, event-log, duty-lifecycle, materialization, and external-data definitions are each locally sound but coexist with older, incompatible signatures, so the documents do not yet pin down *one* deterministic evaluator. Findings are classified by *remediation effort* (Class 1 editorial, Class 2 bounded-decision, Class 3 integration stopper); per the review's own §7 — adopted here — drive by **dependency**, not class number: decide the semantic roots (C3-1/C3-2/C3-4/C3-5) first.

This section is the **execution tracker** for the sweep; individual findings cross-reference the WP/band entry they sharpen or re-open. Class 1 was applied in commit `ae0026b` (2026-07-30) except three deferred items noted below (E2 resolved 2026-07-31 with C3-1).

### Class 1 — editorial (E1–E16)

| ID | Finding | Disposition |
|---|---|---|
| E1 | Grammar cardinalities disagree with SHACL (And/Or/Xone ≥2, Policy clauses ≥1, absent condition → `True`) | ✅ `ae0026b` |
| E2 | Typed result algebra coexists with `Value ∪ {⊥}`/Boolean signatures | ✅ resolved 2026-07-31 — landed with **C3-1**; see issues-log.md (WP-2 entry) |
| E3 | `global` path root excluded by normative grammar + sandbox list | ✅ `ae0026b` |
| E4 | Historical `dutyMode`/state-map mismatch | ✅ superseded by S2-C2: no mode field or authoritative state map |
| E5 | Duplicate headings / duplicate normative algorithms | ✅ `ae0026b` |
| E6 | Architecture vs IR disagree on `TargetIndex` + evaluator signatures | ✅ `ae0026b` (Architecture uses IR datatypes + full `evalIR` sig) |
| E7 | `RL2_ExternalData.md` still cites verified kernel / `IResolve` / VM / fuel | ✅ `ae0026b` (pure-evaluator boundary) |
| E8 | ODRL comparison says derivation is monotone in facts | ✅ `ae0026b` (fixed-environment/policy-universe statement) |
| E9 | ODRL comparison's ontological-status claim ("ontology in the stronger sense") | ✅ `ae0026b` (both described as RDF/OWL models) |
| E10 | Comparison claims differential testing has occurred | ✅ `ae0026b` ("planned conformance testing") |
| E11 | Vocabulary tables drifted from TTL/SHACL | ✅ `ae0026b` (current-state repair; auto-generation stays **ROADMAP-D2**) |
| E12 | `rl2p.ttl` says `performer` populates `Σ.DutyPerformer` (contradicts derived-witness model) | ⏸ deferred — protected ontology comment, needs **AGENTS.md §7** sign-off (Vocabulary prose already corrected) |
| E13 | `issues.md` active-text Dafny/verified-core/Forth references | ✅ `ae0026b` (historical-only) |
| E14 | Semantics refers to a "Go API" | ✅ `ae0026b` (implementation-neutral) |
| E15 | `xsd:dateTime` vs `xsd:dateTimeStamp` used inconsistently | ⏸ deferred — needs the datatype decision before coordinated TTL/SHACL/IR/prose edit (relates the WP-4 `dateTimeStamp` work) |
| E16 | Example namespace + inconsistent version metadata | ⏸ deferred — **OPEN-1** namespace/publication + a release-version table |

### Class 2 — bounded decisions (D1–D25)

Each has a sound recommended resolution in `fix.md` §3 (Class 2 table). Disposition against the existing tracker:

| ID | Topic | Disposition |
|---|---|---|
| D1 | Priority before strategy; keep ODRL `invalid` distinct | ✅ resolved 2026-07-31 — maximal-priority stratum now precedes every strategy; `Invalid` surfaces a conflict within that stratum; see **WP-4/S7** and C3-1 addendum in issues-log.md |
| D2 | `Unknown` atoms lose type/provenance in the envelope | ✅ resolved 2026-07-31 — landed with **C3-1**; `indeterminate(norm,policy,causes)` atom now in `Out`; see issues-log.md (WP-2 entry) |
| D3 | `roles(agent)` undefined in role expansion | Open (new) — add a bounded role-membership relation + closure, or drop role matching from core; relates **SEM-5** |
| D4 | Witness selection ignores duty subject + lifecycle interval | Open — folds into **C3-3** |
| D5 | `latestEvaluation` ordered by timestamp only | Open — add a stable result/event sequence; folds **WP-6/P2** |
| D6 | Empty Requirement set approves any non-Deny | Open — approve only a definite Permit/PermitWithObligations; folds **WP-6/P4** |
| D7 | Requirement/Case status called derived but asserted in RDF | Partly done **WP-3/3c** (requirementStatus projection); residual snapshot/version → **WP-6/P3** |
| D8 | Claims tracked as runtime Requirements | Open — reconcile with **WP-2/C6b** (Claim = derived view of one Duty; don't materialize a Requirement from it) |
| D9 | `NeedContext` absent from protocol ontology | Open — folds **WP-6** |
| D10 | EvaluationResult records too little for replay | = **WP-6/P2** |
| D11 | ContextManifest declares too little (type/cardinality/binding/issuer/freshness) | Open — part of **C3-7** |
| D12 | ContextAssertion permits untrusted requester assertions | Part of **C3-7** |
| D13 | External values lack a snapshot identity | Part of **C3-7** |
| D14 | SourceBinding keyed by an unqualified string | Residual on **WP-5/E1** — key by profile IRI + version + function signature |
| D15 | `VDuration(seconds)` can't represent general `xsd:duration` | Residual on **WP-5/I1** — preserve XSD value; split year-month/day-time |
| D16 | `VSet` neither canonical nor a set | Residual on **WP-5/I1** — typed equality, dedup, canonical order |
| D17 | Raw-RDF "exactly one shape" stronger than SHACL/RDF allow | ✅ addressed **WP-2/C5** (scoped to the AST projection, not raw graphs) |
| D18 | `compile` injectivity too strong (identifiers/metadata survive) | ✅ addressed **WP-0/D4 + WP-2/C5** (semantic-core projection vs identity/provenance) |
| D19 | Complexity bounds omit event scans/closure/sort/effects/AST size | Open — folds **WP-8** |
| D20 | Effect "commutative/idempotent merge" false for ordered append + retries | Re-opens **WP-5/I4** — needs stable effect IDs + set-dedup, append in canonical order inside one version-checked commit |
| D21 | `validateCommit` recomputes an unbound `U`; retry at unchanged version not auto no-op | Re-opens **WP-5/I4** — validate a *named* compiled generation + effect IDs (CAS + dedup, not recomputation alone) |
| D22 | Power exercise writes nonexistent `Σ.ActiveNorms` | Open — **SEM-8** (define as a versioned policy-generation change, or drop executable Power this release) |
| D23 | `nullRequest` undefined for PromisedState | ✅ resolved by S2-C2 status environments with explicit agent/asset scopes |
| D24 | No rule converts ContextAssertion fulfillment → authoritative event | Part of **C3-7** / **WP-6** |
| D25 | Case expiration/re-certification mixes terminal override + re-Pending | Open — folds **WP-6** |

### Class 3 — integration stoppers (C3-1…C3-8)

The review's core claim: WP-2…WP-5 each closed a definition in isolation, but the older signatures they were meant to replace still coexist, so the pipeline isn't yet one deterministic evaluator. Each stopper **re-opens the integration dimension** of an already-"Resolved" WP (or sharpens an open one); the local work stands, the wiring does not. These are recorded as `fix.md` states them — verification against the current text belongs to the pass that picks each up (some are partly pre-empted, e.g. C3-8 vs the C5 AST-projection scoping, C3-6 vs WP-3/3c's requirementStatus projection).

| ID | Integration gap | Re-opens |
|---|---|---|
| C3-1 | ✅ **Resolved 2026-07-31** — one causal-error algebra and one `Out`-based evaluator; canonical `EvalError` identity; typed attributed Unknown atoms; maximal access priority before strategy; exact polynomial finite-summary outcome sensitivity. S2-C3 subsequently narrowed the public resolver to `resolveDecision(envelope,strategy)` because Duty status is interpreted locally during prerequisite derivation, not globally during access resolution. Structured Protocol projection remains C3-6/D10. | **WP-2/S2** — unblocked E2, D1, D2 |
| C3-2 | ✅ **Resolved 2026-07-31 as S2-C2** — applicability, Achievement qualification, Maintenance invariant, and finite interval are separate canonical fields; status is snapshot-derived and total | **WP-4/S4** |
| C3-3 | `EventSet(E)` picks an arbitrary `e` (sequence depends on iteration order); `TimeAdvanced`/`MetadataChanged` mutate scalars but aren't appended (not idempotent/replayable, clock can go backward); witness derivation ignores subject/Case scope/activation window (D4) | **WP-3/S6+S5** |
| C3-4 | ✅ **Resolved by S2-C3 (2026-07-31)** — `prerequisiteDuty` gates only its owning Privilege; independent Duty status is excluded from access resolution; concurrent/post-use workflow is outside core | **WP-4/S7** |
| C3-5 | ✅ **Resolved by S2-C4 (2026-07-31)** — materialization is a pre-evaluation pure transformation, not an IR/runtime effect; PromisedState produces a valid Maintenance Duty; unsupported suretyship rejects; Claims are authored Claim→Duty; complete internal reference rewriting is defined | **WP-2** materialization + **PROM-7** |
| C3-6 | Case history called append-only but RDF exposes unordered `evaluationHistory` + mutable `caseStatus`; EvaluationResult lacks replay identity; Approved can't represent a Permit with ongoing post-use obligations | = **WP-6** (P1/P2/P3/P4), still open |
| C3-7 | `resolveOutOfBand` doesn't handle duplicate/conflicting/ill-typed/stale/wrong-subject assertions; any requester can assert access; live SourceBinding calls omit a source snapshot/version so the Context isn't a coherent cut | **WP-5/E1** (+ D11–D14, D24) |
| C3-8 | Canonical `project(Graph,Profiles)` still doesn't fully fix entailment regime, blank-node/clause identity, list/dedup, literal normalization, unknown-term behavior, or deterministic fresh IDs | **WP-2/C5** |

### ODRL 2.2 completeness (§4) and coverage gaps (§4.3)

- **Superset claim** — `fix.md §4.1` reiterates that "semantic superset" stays unproven without a term-by-term disposition + behavioral import rules; already tracked as **OPEN-3** / **WP-7 (O1/O2b/O2c)** and the "design goal, not proven" downgrade (WP-0/D3). fix.md adds a concrete artifact shape (per ODRL term: disposition `native|normalized|profile|rejected|metadata-only` · AST mapping · preservation rule · diagnostic · positive/negative/golden fixture) and a minimum coverage list (seven Policy subclasses incl. Request/Ticket, Asset/Party collections, `source`/`partOf`/refinements, all logical+relational operators, `includedIn`/`implies`, compact→atomic expansion, inheritance, remedies/consequences/failure chains, conflict `invalid` default, multi-profile + unknown-profile rejection). Fold into **WP-7**.
- **Prior-art sweep is stale** — the W3C Workshop on the Future of ODRL (20–21 July 2026) has 20 public contributions not yet indexed: Bonatti/Fornara/Harth *Open Issues in ODRL 2.2 Semantics* (duty-actor quantification, one-time-vs-per-use, future duties — overlaps **C3-2/C3-4**), Cimmino/Fornara *Policy Templates & Variables*, Salas et al. *Evaluation and Comparison Semantics for ODRL*, Salas/Pareti *Policy Comparison Through Normalisation* (compare directly with the C5 canonical AST), Termont et al. *Towards ODRL 3.0* (competing candidate — needs section-by-section disposition), HSBC *Beyond Permit and Prohibit*, DPV/data-space/VC contributions. Extends **OPEN-4**.
- **Typical-use-case gaps (§4.3)** — recurring/periodic duties, per-use vs one-time fulfillment, any/all/each-actor + quorum, delegation/revocation with executable semantics, policy templates/typed variables, negotiation/comparison, transformations/advice (masking/redaction/minimization), cross-policy fulfillment scope, credential/trust freshness, static consistency/redundancy/unreachable/shadowing diagnostics, bounded remedy/consequence chains, complete Power exercise, native temporal intervals/recurrence. Most already sit in EXPR-1..8 / SEM-8 / WP-7; fix.md's contribution is requiring each to carry an explicit `core | profile | import-only | out-of-scope` disposition rather than being left implicit.

### Work order (§7) — superseded by SCOPE-2

Historical SCOPE-1 sequence retained to explain the integration findings. It no longer controls
current work; use **SCOPE-2 Active Workstreams — authoritative order** above.

1. **Decide the semantic roots:** C3-1 → C3-2/S2-C2 → C3-4/S2-C3 → C3-5/S2-C4 are resolved. Continue with **S2-C5 canonical projection**.
2. **Unify state:** C3-3 (event log) → C3-6 (protocol projection) → C3-7 (resolved context).
3. **Complete ingestion:** C3-8 (canonical projection) + the ODRL compatibility matrix (WP-7).
4. Apply the bounded **Class 2** decisions against that model.
5. **Class 1** cleanup continuously where independent (E2 ✅ landed with C3-1), then the final generated-table pass (**ROADMAP-D2**, still open).
6. Build the **8 golden conformance vectors** (Achievement duty · Maintenance duty · unknown operand · priority-conflict Permit/Prohibit · unrelated violated Duty · Offer materialization · trusted external assertion · Case replay), each as `source graph + request + initial state/events + resolved context → canonical AST → decision + determining atoms + requirements + effects → next state + protocol projection`. Until these evaluate unambiguously by hand from one normative algorithm, totality/replay/canonicality/superset claims stay unproven. Consumes **T1/VALID-4** (WP-8).

---


## Band 0 — Canonical Form (Generatability)

> ✅ **All resolved (v0.6, 2026-07-24).** CANON-1…CANON-6 — full entries in [issues-log.md](issues-log.md).

---

## Band 1 — Formal Semantics (Verifiability)


> **Resolved here → [issues-log.md](issues-log.md):** SEM-4, SEM-9, SEM-10, SEM-12, SEM-13.

### SEM-1 — `restoreAction` / remedial-action specification

**Status:** Open · **Severity:** S1 · **Source:** fix §4.2.1, P1.2 · **Tags:** [VER]
**Files:** `RL2_Semantics.md:1007-1031`, `rl2.ttl`

The future Promise→Duty remedial rule refers to `restoreAction(content)` without a total mapping.
S2-C2 now supplies the underlying declarative Duty status semantics; this issue is limited to
whether remediation is an authored policy relation at all, and, if retained, how a violated
Promise identifies a canonical remedial action. Do not infer an action from an arbitrary
`promisedState` invariant. The core evaluator does not generate or persist remedial Duties.

**Sharpened (fix.md Task 2, fix2.md N4, 2026-07-25 sweep):** `restoreAction(content)` must be specified as a *total* function: `promisedAction` → re-execute the action; `promisedDuty` → fulfill the referenced duty; `promisedState` → require the explicit `rl2:remedialAction` annotation, and when it's absent return an explicit "needs annotation" sentinel — not ⊥ — so the function stays total. **Confirmed still missing from the ontology:** `rl2:remedialAction` is referenced in prose at `RL2_Semantics.md:1118` but is not declared anywhere in `rl2.ttl` (fix2.md N4). When this is implemented, add `rl2:remedialAction` to `rl2.ttl` with domain `rl2:Promise` and an appropriate range, plus a SHACL shape.

### SEM-2 — `targetNorm` lacks parametricity

**Status:** Open · **Severity:** S2 · **Source:** critique 1 §1.2 · **Tags:** [VER] [COV]
**Files:** `rl2.ttl:251`, `RL2_Semantics.md`

`rl2:targetNorm` hard-references a specific Norm IRI, so state predicates (`obligationStateOperand`, `dutyPerformerOperand`) can only ask about *one enumerated* norm. You cannot express "if **any** duty is violated" or "if **all** duties in this policy are fulfilled." Needs a quantified target (e.g. a target-set selector, or a collection operand) so duty-state conditions compose. **Scope note (2026-07-25):** EXPR-2 (quorum) is now decided as excluded-from-core, so this quantification only needs to cover any/all duty-*state* queries over a set of norms — not counting/aggregation. Keep the quantified-target design (SEM-4/5) to that narrower scope.

### SEM-3 — No-Claim / Disability inference rules

**Status:** Open · **Severity:** S2 · **Source:** critique 1 §2.1, critique 2 · **Tags:** [VER] [COV]
**Files:** `RL2_Semantics.md`, `RL2_Vocabulary.md`

The Vocabulary says No-Claim and Disability are "inferrable" from the absence of a Claim/Power, but no inference rule is written anywhere. Either (a) state the rules formally (closed-world absence predicates: `NoClaim(a,b,x) := ¬∃ Claim(...)`), or (b) drop the "inferrable" language and scope them out explicitly. Use case `no-claim-inference.md` exists and should drive this.

### SEM-5 — Target matching algorithm

**Status:** Open · **Severity:** S1 (blocks IMPL) · **Source:** fix P0.2 · **Tags:** [VER]
**Files:** `RL2_Architecture.md` (§TargetIndex)

Four matching modes are listed (direct, classification, sub-asset, subsumption) but the algorithm and precedence are unspecified — implementations will disagree on whether `tag:sensitive` matches `doc:report.pdf`. Specify the algorithm with strict precedence and closed-world defaults. **SEM-4 handoff (2026-07-25):** `RL2_IR.md` fixes the index *shape* — `CompiledPolicy.targetIndex : map<Target, set<int>>` (Target → clause indices) — and defines eval-time subsumption matching via a static `subsumptionIndex` (`includedIn*` closure, bounded reachability per ACT-1/2, no counting per EXPR-2). SEM-5 owns the *algorithm* and precedence over that shape.

### SEM-6 — Policy-generation migration protocol

**Status:** Open · **Severity:** S2 · **Source:** fix §3.2.3, P2.1 · **Tags:** [VER]
**Files:** `RL2_Protocol.md`, `RL2_Semantics.md`

A Case is bound to the generation in force at creation. What happens to in-flight Cases when policy advances to gen N+1 — grandfather, force-upgrade, or hybrid (security-critical force)? Undefined means security patches may silently not apply to open Cases. Specify.

### SEM-7 — Path-resolution security test vectors

**Status:** Open · **Severity:** S2 · **Source:** fix P0.3, §7.2 · **Tags:** [VER]
**Files:** new (`security/path_resolution_test_vectors.json`), `RL2_Semantics.md` (`deref`)

`deref` grammar + security requirements are stated but there are no test vectors (valid
paths, traversal-attack rejects, boundary cases). Needed to validate any future evaluator
against the specified sandbox.

### SEM-8 — Confirm/complete `resolveDecision`, Power exercise, remedial chains

**Status:** Open · **Severity:** S2 · **Tags:** [VER]
**Files:** `RL2_Semantics.md:738,795,1240`

These are *defined* (contra fix.md) but under-exercised: verify totality of `resolveDecision` for every norm-type pairing, confirm Power `ExercisePower` updates Σ consistently, and complete the violation→remedial-norm chains (`:795`). Turn into proof obligations for IMPL-2.

**Narrowed (WP-4/S7, 2026-07-29):** the `resolveDecision` totality sub-item is closed for `SpecificOverridesGeneral` — see **SEM-9**, now resolved, which also fixed `Out`/`deriveNorms` to carry full norm+source-policy provenance instead of projected `(a,x,s)` atoms. **Still open:** Power `ExercisePower` state-update verification and the violation→remedial-norm chain completeness — untouched by this step.

**Further narrowed (WP-4/F2, 2026-07-29):** see **SEM-10**, now resolved, which fixed Liability's guard pattern (was an unlinked existential inconsistent with `LiabilityShape`'s required `exposedTo`; now derives from the specific linked Power) and tightened the Sanctions-and-Remedies rule to use that same bound Power instance on both sides. **Still open, unchanged:** Power `ExercisePower` state-update verification and the violation→remedial-norm chain completeness beyond that notational fix.

### SEM-14 — Document the closed-world evaluation stance as a deliberate design choice

**Status:** Open · **Severity:** S3 · **Source:** fix.md §3.4 · **Tags:** [VER]
**Files:** `RL2_Architecture.md:196` (already states "Not omniscient — Σ contains only facts explicitly asserted")

The scoped closed-world assumption (Σ contains only explicitly-asserted facts; the evaluator has no access to external state unless provided) is correct for a verifiable evaluator, but creates a tension with ODRL's open-world RDF semantics that isn't currently called out as intentional. **Action:** state explicitly that this is a deliberate design choice (not an oversight), and specify how an open-world profile would work if one is ever needed (e.g. "absent fact → Indeterminate, not Deny").

---


## Band 1.5 — Protocol SHACL & Cross-Document Consistency (CONS)

> ✅ **All resolved (2026-07-25/26).** CONS-1…CONS-7 — full entries in [issues-log.md](issues-log.md).

---

## Band 2 — Hohfeld & Promise Completeness (Defensibility)

### HOHF-1 — `correlativeTo` cannot express Immunity↔Disability / Privilege↔No-Claim

**Status:** Open · **Severity:** S2 · **Source:** critique 1 §2.4 · **Tags:** [COV]
**Files:** `rl2.ttl:61`

`rl2:correlativeTo` has domain/range `rl2:Norm`. Disability and No-Claim are not modeled as classes (by design — they're absences), so the symmetric correlative can never be completed for the Immunity/Disability and Privilege/No-Claim pairs. Either accept this asymmetry explicitly in the ontology comment, or model the absence-positions as first-class-but-derived (ties to SEM-3).

### HOHF-2 — Jural opposites not modeled

**Status:** Open · **Severity:** S3 · **Source:** critique 1 §2.3 · **Tags:** [COV]
**Files:** `rl2.ttl`, `RL2_Semantics.md`

RL2 models correlatives (horizontal pairs) but not jural opposites (Privilege⊥Duty, Power⊥Disability, Immunity⊥Liability). These are currently implicit in the evaluator's conflict detection. Decide whether to make the opposition relation explicit (enables reasoning *about* positions) or document it as an evaluator-level concern.

### HOHF-3 — Prohibition's place in the Hohfeld square

**Status:** Open · **Severity:** S2 · **Tags:** [COV]
**Note:** Merged with **CANON-3** — the correlative-Claim question is the same issue. Track there.

### HOHF-4 — Advanced-vocabulary use cases are draft-only

**Status:** Open · **Severity:** S2 · **Source:** critique 1 §1.2 · **Tags:** [COV]
**Files:** `usecases/*` (claim-*, power-*, immunity-*, liability-*)

Claim, Power, Immunity, Liability are specified but not stress-tested — their use cases are placeholder Turtle. 17 of 51 use cases are complete. Completing the Hohfeld cases (in canonical form, post-Band-0) is what validates the vocabulary actually works.

### HOHF-5 — AssetCollection dynamic membership

**Status:** Open · **Severity:** S3 · **Source:** fix §8.2 · **Tags:** [COV]
**Note:** Duplicate of **EXPR-4**. Track there.

---

## Promise Theory (PROM)


> **Resolved here → [issues-log.md](issues-log.md):** PROM-1, PROM-3, PROM-4, PROM-5, PROM-7.

### PROM-2 — Framework agreements / Power-to-promise

**Status:** Open · **Severity:** S3 · **Source:** critique 2 · **Tags:** [COV]
**Files:** `RL2_Primer.md`, `usecases/*`

"A master agreement under which A may make future binding promises to B" is properly modeled as a **Power** (in A) + **Liability** (in B) inside the Agreement, plus Promises made *outside* it. RL2 can express this but never explains the Power↔Promise connection. Document it; add a use case.

### PROM-6 — Promise-as-Generator mechanism

**Status:** Open · **Severity:** S2 · **Source:** critique 1 §3.2 · **Tags:** [VER]
**Files:** `RL2_Semantics.md:1007`, `RL2_Protocol.md`

"When the world deviates from a Promise's invariant, generate a remedial Duty" — but what triggers the check (continuous? event-driven?), who defines "deviation," and how does it interact with SEM-1 `restoreAction`? Specify the trigger and detection model.

### PROM-8 — Departure from Promise Theory autonomy, unacknowledged

**Status:** Open · **Severity:** S3 · **Source:** critique 1 §3.2 · **Tags:** [COV]
**Files:** `RL2_Primer.md`, `RL2_References.md`

Burgess's Promise Theory assesses a promise from the *promisee's* observation — no central truth. RL2 tracks promise state centrally in Σ (a contract-law model). This may be the right engineering choice, but the philosophical departure should be stated, not silent.

---

## Band 3 — Expressiveness Coverage

### EXPR-1 — Recurrent / periodic duties

**Status:** Decided (2026-07-25) — profile-level, not core · **Severity:** S3 · **Source:** fix §4.2.2, backlog · **Tags:** [COV]
"Every quarter," "annually." Ratified fix.md's recommendation: `rl2:DutyTemplate` + recurrence + event-triggered instantiation lives in a **profile**, not core — same pattern as `ethics-approval.md`'s N-of-M operand. Core vocabulary is unaffected; no SEM-4/5 IR impact. **Remaining work:** author the actual profile pattern/use case (not yet written) when a concrete recurring-duty use case demands it.

### EXPR-2 — Quorum / k-of-n approvals

**Status:** Decided (2026-07-25) — excluded from core, documented limitation · **Severity:** S3 · **Source:** fix §4.2.3, backlog · **Tags:** [COV]
Cannot express "any 2 of 5 approvers" in the specified core, and this is now an explicit,
permanent design decision rather than an open gap. The `ethics-approval.md`
"Multi-Approval Variant" pattern (`rl2:resolutionFunction "countApprovalsForAgent"`) remains
the sanctioned workaround, but it is an opaque host function outside `evalIR`'s guarantees.
**Consequence for SEM-2:** its "quantified `targetNorm`" scope is narrowed to any/all
duty-state queries ("if any duty is violated"); it does not need counting or aggregation.

### EXPR-3 — Native temporal arithmetic

**Status:** Decided (2026-07-25) — remains deferred · **Severity:** S3 · **Source:** backlog, critique 1 · **Tags:** [COV]
Relative time ("30 days after event") needs profile operands like `daysSinceEvent`. Native `xsd:duration` arithmetic (`currentDateTime − eventTime < P30D`) stays out of the core kernel. The "revisit if EXPR-1 forces it" trigger no longer applies — EXPR-1 is confirmed profile-level, so no core recurrence machinery will create pressure to add native duration arithmetic. Treat as closed unless a new use case demands it.

### EXPR-4 — AssetCollection dynamic membership

**Status:** Open (reviewed 2026-07-25 — independent of SEM-4/5, no urgency) · **Severity:** S3 · **Source:** fix §8.2 (+HOHF-5) · **Tags:** [COV]
Only `rl2:member` enumeration. Add `rl2:selectionCriteria` (a Condition) for "all assets with tag:PII." Watch canonical-form: enumeration vs criteria must not become two ways to say the same set.

### EXPR-5 — Delegation model

**Status:** Open (reviewed 2026-07-25 — independent of SEM-4/5, no urgency) · **Severity:** S3 · **Source:** fix §8.2 · **Tags:** [COV]
"Alice grants Bob power to act on her behalf." Likely expressible today via Power/Liability — check before adding `rl2:delegatedTo`. May be a documentation issue, not a vocabulary gap.

### EXPR-6 — Revocation vocabulary

**Status:** Open (reviewed 2026-07-25 — independent of SEM-4/5, no urgency) · **Severity:** S3 · **Source:** fix §8.2 · **Tags:** [COV]
Power-to-revoke exists but there is no explicit revocation event. Consider `rl2:RevocationEvent` in the protocol layer. Use cases `approval-revocation.md`, `immunity-from-termination.md` should drive this.

### EXPR-7 — Logical implication/equivalence (`implies`, `iff`) absent

**Status:** Open · **Severity:** S3 · **Source:** fix.md §2.4(1) · **Tags:** [COV]
**Files:** `rl2.ttl` (`rl2:LogicalOperator`: `and`/`or`/`xone`/`not` only)

`A ⟹ B` and `A ⟺ B` can't be expressed as first-class logical operators today. **Recommendation:** desugar at IR-compilation time (`A ⟹ B ≡ ¬A ∨ B`) rather than adding new core operators — preserves canonical form by avoiding two ways to express the same proposition. No core ontology change needed; note as an IR-compiler (SEM-4/`RL2_IR.md`) normalization rule.

### EXPR-8 — ODRL `relation`/`partOf`/`refinement` not covered in RL2 core

**Status:** Open · **Severity:** S3 · **Source:** fix.md §2.1 (coverage table) · **Tags:** [COV]
**Files:** `rl2.ttl`

ODRL's asset relation properties (`relation`, `partOf`, `hasPolicy`) and `refinement` (constraining an action or collection) have no RL2-core equivalent. Action refinement is partially covered via `rl2:includedIn` hierarchies; collection refinement would need `rl2:selectionCriteria` (tracked as **EXPR-4**); `relation`/`partOf` would need a profile. Minor gap — defer to a profile unless a use case demands core support.

---

## Band 3.5 — Use-Case Corpus Quality (surfaced by validation)

> **Tooling now exists.** `tools/validate.py` (pySHACL via `uv`, PEP-723) validates
> the embedded-Turtle use cases against `rl2.ttl` + `rl2-shacl.ttl`. First-ever
> machine-check baseline (2026-07-24): **PASS 0 · WARN-ONLY 17 · FAIL 34 · SKIP 1.**
> After the CANON migration and the state-enum `rightOperandRef` sweep, the corpus
> stood at **WARN-ONLY 24 · FAIL 27 · SKIP 1**. After the full corpus repair
> (2026-07-24) every use case validates: **WARN-ONLY 51 · FAIL 0 · SKIP 1** (the
> skip is `usecases/README.md`, the catalog index, which has no Turtle). The lone
> remaining warning class is the advisory `OperandResolutionRecommendationShape`.
> Run: `uv run tools/validate.py`.


> **Resolved here → [issues-log.md](issues-log.md):** VALID-1, VALID-2, VALID-3, VALID-5.

### VALID-4 — Corpus lacks executable decision, effect, and external-data vectors

**Status:** Open · **Severity:** S3 · **Source:** fix.md §2.5 · **Tags:** [COV]
**Files:** `usecases/*`

No golden vector tests `ProhibitOverrides` vs `PermitOverrides` vs
`SpecificOverridesGeneral` on the same scenario; none covers expected effects/next-state or
mocked external-data resolution. (ODRL migration coverage is tracked separately as
**OPEN-3**.) **Action:** add policy/request/state/context/decision/effects/next-state vectors
against the active direct-AST semantics.


---

## Band 4 — Implementation

> ✅ **Permanently out of scope (SCOPE-1, 2026-07-29).** IMPL-1/2/3 closed with their
> history (Dafny→Go choice, de-risking-spike design) preserved in [issues-log.md](issues-log.md).

---

## Band 5 — Documentation Hygiene

- **DOC-2** — `RL2_Vocabulary.md` vs `rl2.ttl` duplication (~800 lines). Keep TTL authoritative; Vocabulary as gloss. `S3`.
- **DOC-5** — Add a document-navigation map ("I want to… → read…") to `README.md`. `S3`.

> **Resolved here → [issues-log.md](issues-log.md):** DOC-1, DOC-3, DOC-4, DOC-6, DOC-7, DOC-9, DOC-10, DOC-11, DOC-12, DOC-13, DOC-14, DOC-15.

---

## Band 6 — AI-Generation Tooling

### LLM-1 — No LLM-generation prompt templates, few-shot examples, or validation harness

**Status:** Open · **Severity:** S3 · **Source:** fix.md §7.2/Task 15 · **Tags:** [COV]
**Files:** new `examples/llm-generation/` (proposed)

The canonical-form invariant makes RL2 well-suited for LLM generation (graph isomorphism substitutes for a semantic theorem prover when comparing generated vs gold-standard policies — fix.md §7.1), but no concrete artifacts demonstrate this: no prompt-engineering guide for NL→RL2 generation, no NL→RL2 evaluation harness/benchmark, no few-shot examples formatted for LLM consumption. **Action:** create `examples/llm-generation/` with prompt templates, few-shot examples, and a validation harness checking LLM output against SHACL + canonical-form rules.


---

## Resolved

> Moved to [issues-log.md](issues-log.md): **SCOPE-1** (drop stack-IR + Dafny/Go), **ACT-1**,
> **ACT-2**, **CANON (v0.6)**, and every resolved band entry. That file also carries the
> full changelog and the deep-sweep WP-0…WP-5 detail.
