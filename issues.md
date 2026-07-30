# RL2 Issues Log

Single consolidated tracker for RL2 ontology, semantics, protocol, and tooling.

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

## How to use this file

Each issue has an ID, a status, a severity, the source(s) it came from, the files it touches, and a north-star tag. Work proceeds top-down within each priority band. When an issue is resolved, move its entry to **§ Resolved** with the decision and rationale (see ACT-1/ACT-2 for the format).

**North star.** RL2 aims to be an ODRL successor built for the reality that *nobody authors policies by hand any more*. Its two governing quality attributes are therefore:

- **Generatable** — a model generating a policy should have exactly one correct RDF shape to emit for any given normative proposition. No authoring-convenience variation.
- **Verifiable** — every construct must have deterministic, precisely specified semantics (an interpreter design, not a black box) so a policy can be checked, and two policies compared, structurally. As of **SCOPE-1** (2026-07-29), "verifiable" means *specified precisely enough to test*, not mechanically proved — the project stops at design, not a mechanized proof or an implementation.

Issues are tagged **[GEN]** (affects generatability / canonical form), **[VER]** (affects verifiability / formal semantics), or **[COV]** (vocabulary/coverage completeness) to show which attribute they serve. Many serve more than one.

**Legend.** Status: `Open` · `In progress` · `Decision needed` · `Resolved` · `Deferred`. Severity: `S1` (blocks the north star / core soundness) · `S2` (significant gap) · `S3` (polish / hygiene).

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

## Priority bands (work order)

**Band 0 — Canonical form (the generatability thesis).** CANON-1..5. Establishes the "exactly one shape per proposition" invariant that everything downstream depends on. Do first: later coverage work should be authored in canonical form from the start.

**Band 1 — Formal-semantics soundness (verifiability).** SEM-1..14. Closes the gaps that block a precise, testable specification and the S1/S4/S6 documented properties, including `mostSpecific` (SEM-9), guard predicates (SEM-10), `nullRequest` for PromisedState (SEM-11), the stale Dafny example (SEM-12, now moot post-SCOPE-1 — see Resolved), external-data binding (SEM-13), and the closed-world stance (SEM-14).

**Band 1.5 — Protocol SHACL & cross-document consistency.** CONS-1..6. SHACL/protocol-level bugs and doc-vs-ontology mismatches surfaced by the fix.md/fix2.md sweep — distinct from Band 3.5's use-case-corpus scope.

**Band 2 — Hohfeld & Promise completeness (defensibility).** HOHF-1..5, PROM-1..8. Makes the theoretical claims true, not just asserted.

**Band 3 — Expressiveness coverage.** EXPR-1..8. Recurrence, quorum, temporal arithmetic (EXPR-1/2/3 decided 2026-07-25 — all profile-level/excluded, no core impact), collections, delegation, revocation (EXPR-4/5/6 still open, confirmed independent of Band 1 IR work), and implies/iff + ODRL relation/partOf coverage (EXPR-7/8, both deferrable).

**Band 3.5 — Use-case corpus quality.** VALID-1..4. Systemic modeling defects and non-parseable drafts surfaced by the new `tools/validate.py` SHACL harness; spec-doc examples brought up to the same validation standard; VALID-4 flags that the corpus doesn't yet exercise conflict resolution, the IR-compilation path, or external data.

**Band 4 — Implementation.** **Permanently out of scope as of SCOPE-1 (2026-07-29)** — see Resolved. IMPL-1..3 (Dafny kernel, proofs, Go extraction) are closed out-of-scope, not deferred: the project's scope stops at a reviewed docs+spec+semantics+IR design, with no committed implementation or mechanized-proof track.

**Band 5 — Documentation hygiene.** DOC-1..11. Version normalization, dedup, navigation, and (new) fixing three concrete stale/incorrect cross-references (DOC-9/10/11).

**Band 6 — AI-generation tooling.** LLM-1. Prompt templates, few-shot examples, and a validation harness for NL→RL2 generation — not yet started.

**Current sequencing decision (2026-07-25, scope narrowed 2026-07-29 by SCOPE-1).** Goal right now is to *finish the ontology/spec/semantics* — documentation plus a thoroughly reviewed IR design — not to build or prove an implementation. Agreed order: **PROM-1 → SEM-1/2/3 → SEM-4 → SEM-5 → SEM-6/7/8 → HOHF-1/2 → HOHF-4 → PROM-2..8 → DOC-2/4/5/6.** Band 4 (IMPL-1..3, Dafny/Go coding) and OPEN-1/2/3 are **permanently out of scope** per SCOPE-1 — not deferred pending later resourcing, but dropped from the project's goals entirely. Each item is discussed and decided before its file(s) are touched; ontology edits (`rl2.ttl`/`rl2p.ttl`/`*-shacl.ttl`) require explicit sign-off per AGENTS.md §7. **PROM-1 resolved 2026-07-25 — interim milestone. SEM-4 (IR definition) resolved 2026-07-25 — `RL2_IR.md` authored; next is SEM-5 (target matching), then SEM-1/2/3.** The new **SEM-9..14** and **CONS-1..6** (2026-07-25, merged from fix.md/fix2.md) slot into the same agreed order as sharpenings of SEM-4/SEM-5 work — no resequencing needed; they surface as that work is picked up, not before.

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
- **S8a / SEM-8** — `rl2:after` and opaque `resolutionFunction` explicitly scoped **outside the verified core** (annotated in rl2.ttl; kernel MUST NOT depend on them); path/condition/collection/universe bounds recast as **conformance parameters** (`MaxPathDepth`, `MaxConditionDepth`, `MaxCollectionSize`, `MaxPolicyUniverse`) — MUST-enforce, not `MAY`. Updated `RL2_Semantics.md`, `RL2_Vocabulary.md`.
- **O3** — new profile-declaration machinery: `rl2:Profile` + `rl2:profileVersion` (SemVer) + `rl2:requiresProfile`; **fail-closed unknown-profile rule** and **same-major SemVer negotiation** specified in `RL2_Semantics.md §Profile Resolution` and `profiles/README.md`; structural `ProfileShape`/`RequiresProfileShape` SHACL added. **Namespace move off `rl2.example` stays deferred** (OPEN-1/2, pre-publication) as agreed.
- **I2 / I3** (ratified) — recorded in `RL2_IR.md §2`: typed-AST evaluator first (bytecode only on a shown benchmark/portability need); runtime stays solver-free (entailment/closure at ingestion). **Superseded 2026-07-29 (SCOPE-1):** bytecode dropped outright (no benchmark gate) — see SCOPE-1 in § Resolved.
- **C1 residual / C3 / C4 / V1** — C1: `PromiseNotConcreteNormShape` makes Promise≠Norm testable at the *concrete-subclass* level without regressing the `targetNorm` RDFS crutch (full `owl:disjointWith` deferred to C5). C3: `sh:maxCount 1` on all singular norm fields (subject/action/object/counterparty/affectsNorm/exposedTo/immuneFrom/promisor/promisee) — this surfaced and fixed a latent IRI-reuse bug (`ex:accessPrivilege` defined twice in `compliance-attestation.md`). C4: `ContextAssertion` value/ref exclusivity via `sh:xone`. V1: exempted `rl2p:requirementFulfilled` from the operand-recommendation warning, then cleared the two remaining example-operand advisories (`workPeriodOperand`, `processorComplianceAssertionOperand`) → **warning-free gate reaches a true 52/52**.

**Deferred out of WP-1 (as agreed):** namespace move off `rl2.example` (OPEN-1/2); full `owl:disjointWith(Norm, Promise)` → C5/WP-2 (removes the entailment crutch). Original decision text retained below for traceability.

Each needed `AGENTS.md` §7 sign-off before ontology/SHACL edits (granted 2026-07-26).

- **S1** — restate the monotonicity theorem over `U ⊆ U'` for a **fixed immutable environment** (the false `Env ⊆ Env' ⇒ Out ⊆ Out'` is disproved by `Not(EventConstraint)`, `neq`, `isNoneOf`, upper time bounds); drop all proof/perf steps that relied on env-monotonicity; decide set-vs-bag for `Out`. *(new)*
- **C2** — decide `promiseStateOperand`: define one typed core operand + resolver branch, **or** remove every core reference and mark it profile-only/non-portable. Relates **PROM-4** (`promisorOperand` symmetry). *(new)*
- **C6a / SEM-3 / HOHF-1** — declare "six positive Hohfeldian positions + Prohibition; absence positions (No-Claim, Disability) derived/non-reified"; remove Power→Permit / Immunity→Deny decision mappings. *(sharpens SEM-3, HOHF-1, C6; CONS-4 already fixed the Vocabulary mapping)*
- **C7 / EXPR-4** — decide whether `AssetCollection` is itself a target `Asset` (declare the subclass) or compiles to member-matching; bind membership to the evaluation snapshot; define direct-vs-transitive closure. *(sharpens EXPR-4)*
- **S8a / SEM-8** — remove `rl2:after` and opaque `resolutionFunction`s from the *verified core* until precise bounded semantics exist; make depth/size/path/fuel bounds **conformance parameters**, not `MAY`. *(sharpens SEM-8)*
- **O3 / OPEN-1/2 / R1b** — profile-declaration property + "reject unknown required profile" rule + version negotiation + move off the `rl2.example` namespace before publication; add profile-specific SHACL. *(sharpens OPEN-1/2, §14)*
- **I2 / I3** (ratify only) — record "typed-AST evaluator first; bytecode only if a benchmark/portability need is shown" and "runtime stays solver-free; entailment/closure at ingestion". *(ratifies SEM-4 / §8.3)*
- **C1 residual / C3 / C4** (small) — add Promise≠Norm `sh:not` testability; node-shape `sh:maxCount 1` on remaining singular fields; `ContextAssertion` value/ref exclusivity via `sh:xone`. *(folds C1/C3/C4 residue; CONS-1/6 did the rest)*

### WP-2 — Result/error algebra + canonical AST (Class-3 roots)

**Depends on:** WP-1 · **Status:** ✅ Resolved 2026-07-26 (§7 sign-off; two forks decided by the user: C5 = AST-level disjointness keeping the RDF crutch, C6b = Claim derived from one Duty) · The two foundations everything downstream needs.

**Done this pass (validated: corpus `PASS 52 · WARN-ONLY 0 · FAIL 0 · SKIP 1`; `--strict` exits 0; all touched spec docs FAIL 0). No fix.md divergences — S2/C5/C6b match fix.md verbatim.**

- **S2** — total result/truth algebra defined in `RL2_Semantics.md §Result and Truth Algebra`: `EvalValue<T> = Ok | Missing | Invalid | Conflict` for `resolve`, `Truth = True | False | Unknown` for conditions; `apply` lifts operand errors to `Unknown`; And/Or/Not/Xone specified as **Kleene** strong three-valued (short-circuit fixed by the algebra, not evaluation order). A matched norm with `Unknown` condition contributes **`Indeterminate`** to the envelope (never silently inactive); `resolveDecision` takes the `indeterminate` set and returns `Indeterminate` when it could flip the verdict (a firm `Deny` is still conclusive). `Indeterminate → Deny` is an enforcement-adapter policy, not the semantic result. Wired through `RL2_IR.md` (`VBottom` **is** `Unknown`; Kleene opcodes; §9b correctness lemma pinned to the `Truth↔Value` correspondence) and `RL2_Architecture.md` (resolved the "incomplete context" TBD). All condition denotations normalized `= true → = True`.
- **C5** — canonical-form invariant **scoped to the normalized AST projection**, not raw RDF (`RL2_Architecture.md §Canonical Form` rewritten; `RL2_IR.md §10` corrected). Withdrew the false "two structurally-different graphs must differ semantically / equivalence reduces to graph comparison with no normalizer" claim. Specified the `π : RDF → AST` projection (entailment regime, `omitted condition → True`, cardinality expansion, blank-node elimination via stable IDs, operand ordering/dedup, annotation stripping, derived correlatives, unsupported-extension rejection). **Norm≠Promise disjointness is a canonical-AST axiom** — documented as `owl:disjointWith` at the semantic/AST layer while the RDF `targetNorm` crutch (PROM-7) is kept below π (chosen fork: zero fence churn); no raw `owl:disjointWith` triple added, so no latent RDF inconsistency.
- **C6b** — `Claim` is a **derived projection of exactly one Duty**: `ClaimShape` now requires exactly one `correlativeTo` → `rl2:Duty`, forbids authored `action`/`object`/`condition` on the Claim (`sh:maxCount 0`), and adds a SPARQL party-role-alignment check (`Duty.subject = Claim.counterparty`, `Duty.counterparty = Claim.subject`). `RL2_Semantics.md §Claim Denotation and Content Derivation` rewritten: content derived from the Duty, claim `Held`/`Indeterminate`/`Inactive` on the Duty condition's `Truth` (S2-consistent). rl2.ttl `Claim`/`correlativeTo` comments updated; `RL2_Vocabulary.md` Claim entry + example updated. **Per the user's mid-pass guidance, the shape was kept strict and the one non-conforming example fixed** (scaffolded the Vocabulary `bobClaim` fence with an in-fence aligned `ex:aliceDuty`); all existing corpus Claims already conformed.

**Deferred to later WPs (unchanged):** full guard-predicate/remedy semantics (F2/SEM-10) → WP-4; the S2 fixtures for missing/wrong-type/multi-valued/conflicting operands can land with WP-5 (E1) test work.

- **S2** — define a total result/truth algebra (`EvalValue<T> = Ok | Missing | Invalid | Conflict`; `Truth = True | False | Unknown`), specify `And/Or/Not/Xone` over it (incl. short-circuit/error observability), and the normative promotion `condition-error → Indeterminate` (deny is an enforcement-adapter mapping, not the semantic result). Use the same algebra in Semantics, IR, Protocol, and the Go API. *(new; blocks E1, I1, P2)*
- **C5** — specify the normative `RDF → canonical AST` projection: entailment regime, semantic defaults (omitted condition → `True`), cardinality expansion, blank-node handling, operand ordering/dedup, annotation stripping, unsupported-extension rejection, stable IDs; scope canonicality to the *normalized projection*, not raw RDF graphs; drop the "graph comparison proves semantic equivalence" claim. *(new; blocks C6b, I1, O2c)*
- **C6b** — Claim content: make it a required derived projection of a Duty (derive action/object/condition) **or** define its content directly; validate type-pairing and party-role alignment; make correlatives derived *or* authored, not both. *(depends on C5; sharpens CANON-4)*

### WP-3 — State identity/scope + event model (Class-3 roots)

**Depends on:** WP-2 · **Status:** ✅ Resolved — all 3 steps done. **Step 3a (S6) ✅ Resolved 2026-07-26**; **Step 3b (S5) ✅ Resolved 2026-07-26**; **Step 3c (F3/P3) ✅ Resolved 2026-07-29**.

Dependency order S6 → S5 → F3/P3 (matches fix.md's own note).

- **S6 — ✅ Resolved 2026-07-26 (Step 3a; §7 sign-off; fork decided: event kinds = individuals + `eventKindIncludedIn`, not classes).** Validated corpus `PASS 52 · WARN-ONLY 0 · FAIL 0 · SKIP 1`. Done:
  - **Append-only witness log.** `RL2_Semantics.md` Σ redesigned: `Events : EventLog` is the authoritative append-only log with an `EventRecord (id, eventSequence, eventTime, kind, operationalAgent, eventAction, eventObject, case, provenance)`. `Σ.Performed` (Boolean) and `Σ.DutyPerformer` (map) **removed as stored fields** — both are now **derived views** over `Σ.Events` (new §Witness Derivation). `processEvent` **appends** every witness event (incl. `ActionPerformed`) with a fresh `eventSequence`; nothing sets a Boolean. D-FULFILL no longer stores the performer.
  - **Deterministic tie-breaking.** Event selection is `maxByⁱ` over the **total** `(eventTime, eventSequence)` lexicographic order — kills the old `maxBy(eventTime)` tie nondeterminism. `DutyPerformer(d,Σ)` reads the performer from the highest-sequence witnessing event.
  - **One event-kind subsumption model.** New `rl2:eventKindIncludedIn` (transitive, individual-level — the `rl2:includedIn` counterpart for events); `typeMatches` uses `eventKindIncludedIn*`, no `rdfs:subClassOf`, no OWL class reasoning (I3).
  - **Ontology/SHACL/Vocab.** rl2.ttl: `eventSequence`, `eventAction`, `eventObject`, `eventKindIncludedIn` + Event class comment. rl2-shacl.ttl `EventShape`: optional `maxCount 1` guards for the new fields (lenient — kind templates carry none, zero corpus churn). `RL2_Vocabulary.md` Event entry + property table updated.
- **S5 — ✅ Resolved 2026-07-26 (Step 3b; §7 sign-off; design settled in discussion — the 7-tuple collapses to a two-tier class/instance model bounded at the Offer).** Validated corpus `PASS 52 · WARN-ONLY 0 · FAIL 0 · SKIP 1`, `--strict` exits 0; Semantics per-fence FAIL 0; GlobalLeftOperandShape negative-tested (fires). Done:
  - **Two scope tiers, no more — class/instance (OO analogy).** `RL2_Semantics.md` new §State Scope, Identity, and Concurrency: **Offer = class** (immutable template, stateless, accepted many times); **Agreement = instance** (one per acceptance); `materialize()` = the constructor. **Instance variables (default, ~all cases)** = per-Agreement state, already delivered by `materialize()`'s fresh-IRI-per-clause (Σ stays bare-IRI-keyed; zero new machinery, zero corpus churn). **Class variables (rare, explicit)** = state shared across all live Agreements of one Offer, read via the new `global.*` root. **The Offer is the ceiling** — no tenant/cross-Offer tier (explicit non-goal). This is the shared-strong-state vs case-local distinction fix.md asked for.
  - **Shared limits are derived, not stored.** `activeAgreements(Offer, Σ) = { A | A prov:wasDerivedFrom Offer ∧ active(A,Σ) }` (the `wasDerivedFrom` link already exists from PROM-7 materialize; `active()` lifecycle → WP-4). A concurrent-seat limit is the read-only aggregate `|activeAgreements(Offer)|` resolved into ResolvedContext — **no shared-counter algebra**. A genuinely *accumulating* pooled counter is **outside the verified core** (profile + external resolver, same status as an aggregating `resolutionFunction`, S8a).
  - **Versioned snapshot + CAS.** `Snapshot = (Σ, version)`, `evalIR`/`Out` pure over it; `commit(Snapshot_v, effects)` = compare-and-swap on `version`. Admission against `global.*` **MUST** commit serializably; case-local **MAY** use snapshot isolation. Mechanism (locks/storage/retry) outside verified core (I4). Kills the two-evaluators-both-admit race.
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
  - **`mostSpecific` (SEM-9) fully defined** — lexicographic `(actionDepth, atomCount, priority)`; folded into `SpecificOverridesGeneral`. See SEM-9 (now Resolved) for the definition.
  - **Empty/tied/incomparable sets given a complete result.** `mostSpecific` returns `Empty | Unique(n) | Tied(ns)` instead of a bare norm. A single specificity metric applied uniformly to `Privilege` and `Prohibition` eliminates *incomparability* by construction (one total order over one triple type); `Tied` (genuine ties) resolves to `Indeterminate` — an explicit, auditable ambiguity, never a silent pick. `Empty` falls through to `baseDecision`.
  - **ODRL `Invalid` strategy added** — a fourth `resolveDecision` strategy alongside `ProhibitOverrides`/`PermitOverrides`/`SpecificOverridesGeneral`: a genuine Permission/Prohibition conflict (`privileges ≠ ∅ ∧ prohibitions ≠ ∅`) is `Indeterminate` unconditionally, never adjudicated by priority — matching ODRL's strictest conflict-strategy semantics (surface the conflict, don't resolve it).
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

- **E1 / SEM-13 — ✅ Resolved 2026-07-29 (new `RL2_ExternalData.md`; `RL2_Architecture.md` TBDs closed, no ontology change).** Authored `RL2_ExternalData.md` specifying the source-binding step between a `ContextManifest`/`OperandSpec` entry and an actual external data source — the gap between `resolve`'s declared signature and `Sources` being otherwise unspecified. Done:
  - **Out-of-band resolution fixed as the normative baseline.** `resolveOutOfBand : (OperandSpec*, ContextAssertion*) → (Context, Missing*)` — a pure, total, O(|specs|·|assertions|) projection of already-supplied `rl2p:ContextAssertion`s (`RL2_Protocol.md` §Context) onto required operands. No network calls, no timeouts; preserves totality/determinism/fuel-boundedness by construction. Missing `required` operands surface as `Missing*` → `NeedContext`/`Indeterminate`, never a silent decision.
  - **`SourceBinding`/`SourceRegistry` defined** — the formalization of `Sources`: `SourceBinding(function, source, complexity: O1|OLogN, timeoutMillis, onFailure: ToBottom|ToMissing)`, keyed by `resolutionFunction` name. Kept outside the RDF graph as evaluator/deployment configuration, mirroring how S7 scoped `conflictStrategy` as evaluator config rather than policy vocabulary (I1/SEM-4 above) and how O3 scopes the supported-profile registry. An unregistered `resolutionFunction` name is a load-time (fail-closed) rejection, not a runtime `⊥`.
  - **Hybrid/in-band fixed as an explicitly non-core, opt-in extension**, never a policy requirement: bounded complexity (O(1)/O(log n) per call, per the existing S8a constraint), mandatory timeout, and a `ToBottom`/`ToMissing` fail policy that keeps `resolve` total. `ToMissing` degrades uniformly to the out-of-band path, so in-band can be disabled deployment-wide with zero policy-visible behavior change.
  - **Mock sources for testing** — `MockSource(function, canned: map<Request,Value>)`, substituted per `resolutionFunction` name for differential testing, mirroring `RL2_IR.md` §10's tested-not-verified compiler-trust model.
  - **Profile-defined source schemas** — profiles declaring `resolutionFunction` operands SHOULD ship a `SourceBinding` shape table + `MockSource` fixtures as deployment documentation, kept out of `rl2.ttl`/profile ontology files.
  - **`RL2_Architecture.md`'s two TBD interaction-mode tables and two Open Design Questions rows closed**, all pointing at `RL2_ExternalData.md`: §Runtime Functions `resolve`'s "Interaction modes (TBD)" table now marks out-of-band normative-baseline vs in-band/hybrid optional-extension; §Interaction Modes' "TBD: Specify which modes are normative vs optional" resolved (Single-shot/Iterative/Pre-flight are all realizable via out-of-band alone and are all normative); "Context resolution mode" and "Incomplete context behavior" rows in Open Design Questions marked Decided. "Pre-flight API" and "NeedContext protocol" rows are untouched (still TBD — out of this item's scope).
  - Touched: RL2_ExternalData.md (new), RL2_Architecture.md (§Runtime Functions `resolve`, §Interaction Modes, §Open Design Questions), issues.md.
- **I1 / SEM-4 — ✅ Resolved 2026-07-29 (`RL2_IR.md`-only, no ontology change).** All seven defects were `RL2_IR.md`-internal gaps against an already-permissive ontology/semantics (`isA`/`isAnyOf`/`isAllOf`/`isNoneOf` are already `rl2:ComparisonOperator` individuals in `rl2.ttl`; `mkEnv(R,Σ,Ctx)` and `Eval(U,R,Σ,Ctx,strategy)` were already the canonical RL2_Semantics.md signatures) — no `rl2.ttl`/`rl2-shacl.ttl` edit and no §7 sign-off gate applies. Done:
  - **Real `Xone`.** `IXor` (parity on chained folds, wrong for ≥3 operands) replaced by N-ary `IXone(n: nat)`, reducing directly per the existing Kleene rule — a type-level fix, the semantic rule itself is unchanged.
  - **`isA`/`isAnyOf`/`isAllOf`/`isNoneOf` opcodes added** (`IIsA`/`IIsAnyOf`/`IIsAllOf`/`IIsNoneOf`), lowering the already-ontology-defined operators that previously had no bytecode target.
  - **`Value` extended**: `VDecimal` (exact fixed-point), `VLangString`, `VDuration`, `VSet` (collections — operand type for the new `isAnyOf`/`isAllOf`/`isNoneOf`), and `VDate`→`VDateTime` (mandatory `tzOffsetMinutes`, matching S4/WP-4's `xsd:dateTimeStamp` decision; `IDateLte`→`IDateTimeLte`).
  - **`rightOperandRef` bytecode lowering fixed** — §3.2's lowering row now emits `RESOLVE right` (not `PUSH right`) when the AtomicConstraint carries a dynamic `rightOperandRef` rather than a literal; `IResolve` clarified as usable on either operand position.
  - **AST↔bytecode boundary / evaluation order — closed with a clarifying note, no new machinery.** Already resolved by I2 (typed-AST is normative; bytecode is an optional lowering) and by §5's existing Kleene-logic invariants (short-circuit/error-observability fixed by the algebra, not evaluation order).
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
- **T1 / VALID-4** — convert the 52 narrative use cases into golden `input/AST-digest/state/context/envelope/decision/effects/next-state` vectors + negative vectors + the coverage matrix (§11), for differential testing against the specified `evalCondition`/`evalIR` design (RL2_IR.md §10) — not for a mechanized proof. *(sharpens VALID-4)*
- **D1** — W3C-style conformance classes + stable requirement IDs + RFC 2119 boilerplate, once the semantic decisions are closed. *(new; Band 5)*
- **A1 / LLM-1** — the strict parse→validate→type-check→normalize→compile ingestion pipeline with unknown-term/heuristic-repair rejection + adversarial-input tests. *(sharpens LLM-1, §7)*
- **R1b** — separate privacy-profile category classes from runtime individuals; add profile SHACL; narrow the GDPR legal claims. *(new; §14)*
- **D2** (dependent) — final editorial consolidation per the source hierarchy; generate vocabulary/cardinality/namespace tables rather than hand-maintaining them. *(extends Band 5 DOC-2)*

---

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

## Band 1 — Formal Semantics (Verifiability)

### SEM-1 — `restoreAction` / remedial-action specification

**Status:** Open · **Severity:** S1 · **Source:** fix §4.2.1, P1.2 · **Tags:** [VER]
**Files:** `RL2_Semantics.md:1007-1031`, `rl2.ttl`

The Promise→Duty remedial rule exists but `restoreAction(content)` is "implementation-defined" with no guidance — a hole in an otherwise-deterministic pipeline. Add an explicit `rl2:remedialAction` property so remediation is declared on the norm/promise rather than invented by the evaluator. Define the default mapping: Action-promise → retry the action; Duty → the duty's action; State-promise → requires explicit `rl2:remedialAction` (no default). Interacts with CANON-2 (the split makes the mapping total). **PROM-1 handoff (2026-07-25):** crystallization of a `promisedState` promise produces a *state-maintenance Duty* whose fulfillment is the promised condition; SEM-1 owns the ObligationState-transition wiring for such condition-fulfilled duties (how Active→Fulfilled/Violated advances, and `restoreAction` on breach). The crystallization *target* is fixed by PROM-1; only this behavioral wiring is open here. **Narrowed (WP-4/S4, 2026-07-29):** the ObligationState-transition half of the handoff is now resolved — `rl2:dutyMode` (`Achievement`/`Maintenance`) plus the Duty Fulfillment/Violation (Maintenance) rules in `RL2_Semantics.md` fully specify how a crystallized `PromisedState` duty's Active→Fulfilled/Violated transitions advance (violate on first counterexample, fulfill only when a recognized monitoring window closes clean). **Still open:** `restoreAction`/`rl2:remedialAction` itself — the total mapping and ontology property described below.

**Sharpened (fix.md Task 2, fix2.md N4, 2026-07-25 sweep):** `restoreAction(content)` must be specified as a *total* function: `promisedAction` → re-execute the action; `promisedDuty` → fulfill the referenced duty; `promisedState` → require the explicit `rl2:remedialAction` annotation, and when it's absent return an explicit "needs annotation" sentinel — not ⊥ — so the function stays total. **Confirmed still missing from the ontology:** `rl2:remedialAction` is referenced in prose at `RL2_Semantics.md:1118` but is not declared anywhere in `rl2.ttl` (fix2.md N4). When this is implemented, add `rl2:remedialAction` to `rl2.ttl` with domain `rl2:Promise` and an appropriate range, plus a SHACL shape.

### SEM-2 — `targetNorm` lacks parametricity

**Status:** Open · **Severity:** S2 · **Source:** critique 1 §1.2 · **Tags:** [VER] [COV]
**Files:** `rl2.ttl:251`, `RL2_Semantics.md`

`rl2:targetNorm` hard-references a specific Norm IRI, so state predicates (`obligationStateOperand`, `dutyPerformerOperand`) can only ask about *one enumerated* norm. You cannot express "if **any** duty is violated" or "if **all** duties in this policy are fulfilled." Needs a quantified target (e.g. a target-set selector, or a collection operand) so duty-state conditions compose. **Scope note (2026-07-25):** EXPR-2 (quorum) is now decided as excluded-from-core, so this quantification only needs to cover any/all duty-*state* queries over a set of norms — not counting/aggregation. Keep the quantified-target design (SEM-4/5) to that narrower scope.

### SEM-3 — No-Claim / Disability inference rules

**Status:** Open · **Severity:** S2 · **Source:** critique 1 §2.1, critique 2 · **Tags:** [VER] [COV]
**Files:** `RL2_Semantics.md`, `RL2_Vocabulary.md`

The Vocabulary says No-Claim and Disability are "inferrable" from the absence of a Claim/Power, but no inference rule is written anywhere. Either (a) state the rules formally (closed-world absence predicates: `NoClaim(a,b,x) := ¬∃ Claim(...)`), or (b) drop the "inferrable" language and scope them out explicitly. Use case `no-claim-inference.md` exists and should drive this.

### SEM-4 — IR definition

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S1 (blocks IMPL) · **Source:** fix P0.1 · **Tags:** [VER]
**Files:** `RL2_IR.md` (new), `RL2_Architecture.md`, `research/design-forth-ir.md`

`compile : Policy* → IR` left IR as TBD; blocked evaluator implementation and the "compile-time canonicalization" story. **Resolved** by authoring `RL2_IR.md`, a design spec (datatypes + opcode table + correspondence table + equivalence statements; no Dafny proofs — those are IMPL). Decisions:

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

`deref` grammar + security requirements are stated but there are no test vectors (valid paths, traversal-attack rejects, boundary cases). Needed to validate the sandbox in the Dafny/Go kernel.

### SEM-8 — Confirm/complete `resolveDecision`, Power exercise, remedial chains

**Status:** Open · **Severity:** S2 · **Tags:** [VER]
**Files:** `RL2_Semantics.md:738,795,1240`

These are *defined* (contra fix.md) but under-exercised: verify totality of `resolveDecision` for every norm-type pairing, confirm Power `ExercisePower` updates Σ consistently, and complete the violation→remedial-norm chains (`:795`). Turn into proof obligations for IMPL-2.

**Narrowed (WP-4/S7, 2026-07-29):** the `resolveDecision` totality sub-item is closed for `SpecificOverridesGeneral` — see **SEM-9**, now resolved, which also fixed `Out`/`deriveNorms` to carry full norm+source-policy provenance instead of projected `(a,x,s)` atoms. **Still open:** Power `ExercisePower` state-update verification and the violation→remedial-norm chain completeness — untouched by this step.

**Further narrowed (WP-4/F2, 2026-07-29):** see **SEM-10**, now resolved, which fixed Liability's guard pattern (was an unlinked existential inconsistent with `LiabilityShape`'s required `exposedTo`; now derives from the specific linked Power) and tightened the Sanctions-and-Remedies rule to use that same bound Power instance on both sides. **Still open, unchanged:** Power `ExercisePower` state-update verification and the violation→remedial-norm chain completeness beyond that notational fix.

### SEM-9 — `mostSpecific` undefined in `SpecificOverridesGeneral`

**Status:** ✅ Resolved 2026-07-29 (WP-4/S7) · **Severity:** S1 · **Source:** fix.md §3.1/Task 3, fix2.md E1 · **Tags:** [VER]
**Files:** `RL2_Semantics.md` §Conflict Resolution (`mostSpecific`, `SpecificOverridesGeneral`)

`resolveDecision`'s `SpecificOverridesGeneral` strategy calls `mostSpecific(privileges ∪ prohibitions)`, but `mostSpecific` is never defined — so `resolveDecision` is not actually total until this is closed. **Sharpened (fix2.md):** the gap is subtler than "undefined": specificity may mean different things for a Privilege (action subsumption depth) vs a Prohibition (condition complexity), and a single ordering over the *union* of both assumes a common specificity metric that may not exist. **Recommendation:** define `mostSpecific` as a lexicographic ordering — (1) action subsumption depth (deeper = more specific), (2) condition count (more conditions = more specific), (3) policy priority as tiebreaker — and document this explicitly as a design choice, not a theorem.

**Resolved (WP-4/S7, 2026-07-29):** adopted the recommendation as-is — `specificity(n) = (actionDepth(n.action), atomCount(n.condition), n.priority)`, lexicographic. `actionDepth(x) = |{y | x ⊑ y, y ≠ x}|` (static ancestor count under `rl2:includedIn*`, the direction-dual of the compiler's descendant-oriented `subsumptionIndex`); `atomCount` flattens `AtomicConstraint`/`EventConstraint` leaves through `And`/`Or`/`Xone`/`Not`. A single metric applied uniformly across `Privilege` and `Prohibition` eliminates the incomparability fix2.md flagged by construction — every norm gets a well-defined triple under one total order, so only genuine ties remain. `mostSpecific` returns `Empty | Unique(n) | Tied(ns)`, not a bare norm, so `resolveDecision` no longer has to guess: `Empty` falls through to `baseDecision`, `Tied` surfaces as `Indeterminate` (an explicit ambiguity, never an implicit default) — closing the "empty/tied/incomparable" completeness gap from **S7** in the same edit.

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

### SEM-11 — `nullRequest` semantics for `PromisedState` condition evaluation

**Status:** Open · **Severity:** S2 · **Source:** fix.md §3.6/Task 5, fix2.md E3 · **Tags:** [VER]
**Files:** `RL2_Semantics.md:560-562` (`contentHolds`/`mkEnv(nullRequest, Σ, emptyContext)`)

`contentHolds` for `PromisedState` evaluates `⟦c⟧(mkEnv(nullRequest, Σ, emptyContext))` — but `nullRequest` is undefined, and the denotational semantics for conditions otherwise assume a real Request `R = (a_req, x_req, s_req)`. How `agent.*`/`asset.*` resolutionPaths behave under a null request is unspecified. **Narrowed (fix2.md):** `PromisedAction` and `PromisedDuty` don't use `Env` at all (they query Σ directly via `performed()`/`ObligationState`) — only `PromisedState` does. This supports fix.md's option (b) over defining a `nullRequest` sentinel. **Recommendation (adopted):** restrict `PromisedState` conditions to `state.*`/`context.*` resolutionPath roots only, since `agent.*`/`asset.*` are meaningless without a request; add a SHACL constraint enforcing this restriction.

### SEM-12 — Stale Dafny example in `RL2_Semantics.md`

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S3 · **Source:** fix.md §3.7/§4.4(6)/Task 9, fix2.md E4 · **Tags:** [VER]
**Files:** `RL2_Semantics.md` (Dafny Example, Mechanization section)

The Dafny abstract-syntax example included `Temporal(start, end)` and `Context(path, cmp, val)` Condition variants that don't exist in the current abstract syntax: `TemporalConstraint` was removed in favor of `AtomicConstraint` + `currentDateTime`, and `Context` was replaced by `AtomicConstraint` + `resolutionPath`. It also omitted `Xone` even though it's present in the abstract syntax, and `EvalCondition`'s match fell through to `// ...` (non-exhaustive, would not compile). **Fixed:** removed `Temporal`/`Context`, added `Xone(operands: seq<Condition>)`, and made `EvalCondition` exhaustive (`Xone` case counts true operands via a set comprehension and requires exactly one).

**Superseded note (SCOPE-1, 2026-07-29):** the "Dafny Example" and "Mechanization"/"Target Platforms" sections this issue fixed were later removed from `RL2_Semantics.md` entirely, along with the rest of the Dafny/Go mechanization track. `evalCondition`'s pseudocode now lives in `RL2_IR.md` §5 instead.

### SEM-13 — External data integration lacks a binding specification

**Status:** ✅ Resolved 2026-07-29 (WP-5/E1 — see full Done-block there) · **Severity:** S2 · **Source:** fix.md §6.4/Task 11, fix2.md E10 · **Tags:** [VER]
**Files:** `RL2_Architecture.md` (ContextManifest, `resolve`), `RL2_Semantics.md:364-366` (`resolutionFunction` "implementation-specific"), `RL2_ExternalData.md` (new)

`rl2:resolutionFunction` and `lookupExternal` are declared but not bound: no standard way for a policy to declare what external data it needs, for an evaluator to call external services, or to test/verify a policy that uses external data. This is the highest-risk area for the totality guarantee — the extension warning at `RL2_Semantics.md:1574` already flags unbounded external queries as a threat to polynomial-time/termination. The ContextManifest pattern (compiler extracts `RESOLVE` paths from condition trees → host pre-materializes them into `Env` before evaluation → `RESOLVE` of an un-manifested path is a hard reject) is the right shape, but the source-binding step between a manifest entry and an actual data source is unspecified.

**Recommended resolution (fix.md and fix2.md converge on this):** write `RL2_ExternalData.md` specifying — (1) **out-of-band** (requester supplies all context as `rl2p:ContextAssertion`s before evaluation) as the *normative baseline* for the verified kernel, preserving totality/determinism/fuel-boundedness; (2) **hybrid/in-band** as a documented *extension only*, with source bindings declared in the ContextManifest (`required: true/false`), bounded complexity (O(1) or O(log n) per call), a timeout + fail-to-⊥ policy, and mock sources for testing; (3) **profile-defined source schemas** binding `resolutionFunction` names to concrete implementations (e.g. `privacy:dataOwnerOperand` → `source: HR_API, query: getUserByIRI`). Precedents: OPA's bundle API (atomic policy+data delivery; also track OPA's evolving `rego.v1`/bundle patterns as design input), Cedar's Entity Store (pre-loaded typed entities — the out-of-band pattern). Forbid pure in-band for the verified kernel; it breaks totality (XACML's PIP pattern is the cautionary example). Blocks IMPL-1 confidence.

### SEM-14 — Document the closed-world evaluation stance as a deliberate design choice

**Status:** Open · **Severity:** S3 · **Source:** fix.md §3.4 · **Tags:** [VER]
**Files:** `RL2_Architecture.md:196` (already states "Not omniscient — Σ contains only facts explicitly asserted")

The scoped closed-world assumption (Σ contains only explicitly-asserted facts; the evaluator has no access to external state unless provided) is correct for a verifiable evaluator, but creates a tension with ODRL's open-world RDF semantics that isn't currently called out as intentional. **Action:** state explicitly that this is a deliberate design choice (not an oversight), and specify how an open-world profile would work if one is ever needed (e.g. "absent fact → Indeterminate, not Deny").

---

## Band 1.5 — Protocol SHACL & Cross-Document Consistency (CONS)

> Surfaced by the fix.md/fix2.md 2026-07-25 review sweep — concrete SHACL over/under-constraint bugs and vocabulary/ontology mismatches found by manual cross-reference, distinct from the pySHACL-harness use-case defects in Band 3.5.

### CONS-1 — `RequirementFulfillmentAuditShape` requires both action and event evidence

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S2 · **Source:** fix2.md N1 · **Tags:** [VER]
**Files:** `rl2p-shacl.ttl:178-205`

The shape required `sh:minCount 1` on `fulfilledByAction` **and** `fulfilledByEvent` **and** `fulfillmentEvidence` for fulfilled requirements (three independent property shapes, each triggering its own warning) — but a requirement may legitimately be fulfilled by an action *or* an event, not necessarily both (e.g. a `PromisedState`-derived requirement is fulfilled by a state condition holding in Σ, with no discrete action). **Fixed:** collapsed the three property shapes into one `sh:or` (at least one of the three required). Severity was already `sh:Warning` at the node level. Validated against the full corpus: clean, `PASS 0 · WARN-ONLY 51 · FAIL 0 · SKIP 1`, no change in per-file warning counts (including `fulfillment-evidence.md`, which exercises this shape).

### CONS-2 — Protocol SHACL allows `Active` for Promise-derived Requirements (semantically impossible)

**Status:** ✅ Resolved 2026-07-25 · **Severity:** S2 · **Source:** fix2.md N2 · **Tags:** [VER] · **Related:** PROM-7
**Files:** `rl2p-shacl.ttl:148-152` (`RequirementShape` `sh:in`), `rl2p.ttl:163-168`, `rl2.ttl:535-563`

`RequirementShape`'s `requirementStatus` `sh:in` list is the full `ObligationState` enum (`Pending`, `Active`, `Fulfilled`, `Violated`) — but `PromiseState` admits no `Active` (`rl2.ttl:558`). A Promise-backed Requirement can therefore be assigned `requirementStatus = rl2:Active` and pass validation. **Resolved as option (b), not (a):** `RL2_Semantics.md`'s "Promise and duty states vs protocol requirement status" section (and `RL2_Protocol.md:277`'s cross-reference to it) already document this as the *intended* protocol-level projection — a pending promise that is effective now surfaces as `Active` at the Requirement layer while its semantic `PromiseState` stays `Pending`. Checked for consistency: `usecases/runtime-evaluation.md`'s `ex:promiseReq` example (`sourceNorm = ex:somePromise`, `requirementStatus = rl2:Active`) already relies on exactly this reading; `claim-counterclaim.md` and `fulfillment-evidence.md`'s `Active`/`Fulfilled` usages are all Duty-sourced, not Promise-sourced, so unaffected. `RL2_IR.md`'s effect algebra doesn't model `rl2p:Requirement`/`requirementStatus` at all (it operates on Duty/Promise state directly via `TransitionDuty`/`CrystallizePromise`) — the projection is a protocol/shell-layer computation above the verified kernel, so no IR change was needed or made. **Action taken:** rather than adding a SPARQL rejection rule (which would contradict this documented design), added cross-referencing comments to `rl2p:requirementStatus` in `rl2p.ttl` and to `RequirementShape`'s `requirementStatus` property in `rl2p-shacl.ttl`, so the ontology/SHACL files are self-explanatory without requiring a jump to `RL2_Semantics.md`. This also satisfies **PROM-7**'s "land the reconciliation, not just a semantics-doc note" ask — the reconciliation already existed in the docs; it's now wired up from the ontology side too. Validated against the full corpus: clean, `PASS 0 · WARN-ONLY 51 · FAIL 0 · SKIP 1`.

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

### PROM-2 — Framework agreements / Power-to-promise

**Status:** Open · **Severity:** S3 · **Source:** critique 2 · **Tags:** [COV]
**Files:** `RL2_Primer.md`, `usecases/*`

"A master agreement under which A may make future binding promises to B" is properly modeled as a **Power** (in A) + **Liability** (in B) inside the Agreement, plus Promises made *outside* it. RL2 can express this but never explains the Power↔Promise connection. Document it; add a use case.

### PROM-3 — Conditional promise in an accepted agreement

**Status:** ✅ Resolved 2026-07-25 (by PROM-1) · **Severity:** S3 · **Source:** critique 2 · **Tags:** [GEN]
**Files:** `RL2_Semantics.md`, `RL2_Primer.md`

"If audit findings > X, I promise to remediate within 30 days," placed in an Agreement — is it a conditional Duty or a Promise-that-generates-a-Duty? **Resolved by the container-determines-semantics rule (PROM-1 + CANON-2):** an Agreement contains no Promises — every promise crystallizes into a Duty + correlative Claim on acceptance — so in an Agreement this is unambiguously a **conditional Duty** (the condition is the duty's activation guard). The Promise-with-a-condition form exists only in an **Offer**, where it crystallizes to the conditional Duty on acceptance. The container type (Offer vs Agreement) fixes the reading; no ambiguity remains.

### PROM-4 — No `promisorOperand` in core

**Status:** Open · **Severity:** S2 · **Source:** critique 1 §3.2, critique 2 · **Tags:** [VER] [COV]
**Files:** `rl2.ttl` (cf. `dutyPerformerOperand:267`), use case 8

Duty identity-binding is core-supported (`dutyPerformerOperand`); promise identity-binding is delegated to a profile operand (use case 8's `governance:promisorOperand`). If Promise is first-class, add a core `rl2:promisorOperand` for symmetry.

### PROM-5 — "Promise references a Duty" = suretyship, unspecified

**Status:** Open · **Severity:** S2 · **Source:** critique 1 §3.2, critique 2 · **Tags:** [VER] [COV]
**Files:** `rl2.ttl:122`, `RL2_Semantics.md`

Promising to fulfill *someone else's* Duty (without becoming its dutyHolder) is a real legal concept — guarantee/suretyship — with no analysis. CANON-2's `rl2:promisedDuty` names it; this issue is to give it semantics (what state/obligation the suretyship promise creates for the promisor). **PROM-1 handoff (2026-07-25):** crystallization maps a `promisedDuty` promise to a *second-order Duty* on the promisor, fulfilled when the referenced Duty reaches Fulfilled (target fixed by PROM-1). Open here: the remedy/liability the surety incurs when the referenced Duty is Violated — guarantee vs indemnity.

### PROM-6 — Promise-as-Generator mechanism

**Status:** Open · **Severity:** S2 · **Source:** critique 1 §3.2 · **Tags:** [VER]
**Files:** `RL2_Semantics.md:1007`, `RL2_Protocol.md`

"When the world deviates from a Promise's invariant, generate a remedial Duty" — but what triggers the check (continuous? event-driven?), who defines "deviation," and how does it interact with SEM-1 `restoreAction`? Specify the trigger and detection model.

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
Cannot express "any 2 of 5 approvers" in the verifiable core, and this is now an explicit, permanent design decision rather than an open gap — it ratifies what `RL2_Architecture.md`'s "Known Limitations" (`LTL_F + Deontic + Finite Obligation Automata` has no counting quantifier) already stated. The `ethics-approval.md` "Multi-Approval Variant" pattern (`rl2:resolutionFunction "countApprovalsForAgent"`) remains the sanctioned workaround, but it is an **opaque host function** — policies using it are *not* Dafny-verifiable, unlike core RL2 policies. **Consequence for SEM-2:** its "quantified `targetNorm`" scope is narrowed to any/all duty-*state* queries ("if any duty is violated") — it does **not** need to support counting/aggregation. This removes a structural risk that would otherwise have forced IR (SEM-4) rework. **Follow-up (low-priority doc task):** add a one-line caveat to `ethics-approval.md` and `RL2_Architecture.md` noting the opaque-function/unverified tradeoff explicitly.

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

### VALID-4 — Corpus doesn't exercise conflict resolution, the Forth-IR path, or external data

**Status:** Open · **Severity:** S3 · **Source:** fix.md §2.5 · **Tags:** [COV]
**Files:** `usecases/*`

No use case tests `ProhibitOverrides` vs `PermitOverrides` vs `SpecificOverridesGeneral` on the same scenario; none exercises the Forth-IR compilation path end-to-end; none demonstrates external data integration (the `resolve` function calling an external source). (ODRL migration coverage is tracked separately as **OPEN-3**.) **Action:** add targeted use cases once SEM-4/IR and SEM-13/external-data work stabilize enough to give them a fixed target to test against.

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

**Closed 2026-07-29 (SCOPE-1):** S1/S4/S6 remain documented design properties (RL2_Semantics.md § Proof Obligations, RL2_IR.md §5/§9), but are no longer proof obligations for a mechanized evaluator — there is none. Confidence comes from differential testing (RL2_IR.md §10), not mechanized proof.

### IMPL-3 — Go extraction, CLI, property tests

**Status:** ✅ Resolved — out of scope (SCOPE-1, 2026-07-29) · **Severity:** S2 · **Source:** backlog · **Tags:** [VER]
`rl2-eval --policy p.ttl --request r.json`; property-based tests; validate against use cases 1–17.

**Closed 2026-07-29 (SCOPE-1):** no reference implementation is planned; this entry described the last stage of a track the project no longer pursues.

---

## Band 5 — Documentation Hygiene

- **DOC-1** — ✅ Resolved (v0.6). Spec-suite docs normalized to `version: "0.6"` / `date: 2026-07-24` (Semantics, Architecture, Vocabulary, Primer, Protocol, References, README banner). RDF artifacts keep truthful `owl:versionInfo`: `rl2.ttl` 0.6 (changed), `rl2p.ttl` 0.5 (unchanged); Vocabulary footer notes the split. `RL2_ODRL_Comparison.md` retains its own doc version (now 1.1, see DOC-4). `S3`.
- **DOC-2** — `RL2_Vocabulary.md` vs `rl2.ttl` duplication (~800 lines). Keep TTL authoritative; Vocabulary as gloss. `S3`.
- **DOC-3** — ✅ Resolved (2026-07-25). `codex.md`/`gemini.md`/`persona.md` were already gone; found and removed a byte-identical duplicate `claude.md` (redundant with `CLAUDE.md`). Fixed the stale `persona.md` references in `design-canonical-form.md:25,46` → `AGENTS.md`. `S3`.
- **DOC-4** — ✅ **Resolved (2026-07-26).** Decision reversed on the "merge into `RL2_Primer.md`" plan: the user determined `RL2_ODRL_Comparison.md` should stay a **standalone** document — the motivation/use-case/justification content it needs to carry doesn't fit the Primer. All previously-flagged staleness fixed in place instead of via merge: §3.2 now names Dafny→Go (not Why3/Coq/Lean); §1.1 no longer cites the nonexistent `rl2-media-profile.ttl`; §2.2's Σ.Events description corrected to "typed, temporally-ordered index" (matching `RL2_Semantics.md`, and confirming this specific claim was actually already accurate, not stale); §2.1 rewritten to reflect PROM-1's crystallization model (Promise → Duty + correlative Claim on Offer→Agreement acceptance). Also added a new **Quantitative Comparison** section (ontology metrics vs. ODRL 2.2/PROV-O/DCAT 3/ORG/FOAF) and fact-checked every RL2-specific figure against the current repo: found and corrected an inaccurate "RL2 full" row (undercounted classes/properties/enums and overstated size — `rl2p.ttl`'s 7 classes/26 objProps/12 dataProps/2 enums weren't rolled into the combined-suite total). `S2`→resolved.
- **DOC-5** — Add a document-navigation map ("I want to… → read…") to `README.md`. `S3`.
- **DOC-6** — ✅ Resolved (2026-07-25). `FAQ/RL2_FAQ.md:23` "Rights & Licenses 2" → "Rights Language 2"; `FAQ/RL2_FAQ.md:111-118`'s pre-CANON-2 `ProviderPromise`/`ConsumerPromise`/`ThirdPartyPromise` terms replaced with a description of the unified `rl2:Promise` class + `promisedAction`/`promisedState`/`promisedDuty`. Same stale terminology also found and fixed in `RL2_References.md:329` (Tun-Sollen glossary entry). Remaining terminology consistency (`ObligationState` not DutyState, `Norm` not Rule, Requirement-wraps-Duty clarity) not yet audited beyond these two files — reopen if found elsewhere. `S3`.
- **DOC-7** — ✅ Resolved (2026-07-25). `backlog.md` merged into this log. Open design decisions are now § Open Decisions (OPEN-1..3). Work items and success criteria were already tracked as IMPL-1..3 and S1/S4/S6. `backlog.md` deleted. `S3`.
- **DOC-9** — ✅ Resolved (2026-07-25). Rewrote `FAQ/RL2_FAQ.md:183` (conflict-resolution bullet) and the "Is RL2 tied to a specific policy engine?" section (was lines 280-291) to describe the actual single Forth-IR → Dafny → Go pipeline; Rego/Cedar/Prolog/Datalog are now framed as conceivable future targets for that IR, not implemented/planned backends. `S2`.
- **DOC-10** — ✅ Resolved (2026-07-25). `RL2_References.md:446` now cites `RL2_ODRL_Comparison.md` (was the nonexistent `RL2_ODRL_Coverage.md`). `S3`.
- **DOC-11** — ✅ Resolved (2026-07-25). `RL2_Semantics.md:1684`'s dangling reference to `RL2_ResearchPlan.md` replaced with pointers to `RL2_IR.md` (compilation target) and `issues.md` Band 4 (phased implementation plan) — the artifacts that actually carry this content now. `S3`.
- **DOC-12** — ✅ Resolved (2026-07-26). `AGENTS.md` §12 Key Files table listed a `CLAUDE.md` row (file removed per DOC-3) and a `fix.md` row (a transient scratch file, not a persistent repo artifact); both rows removed. Also fixed a stale `fix.md §6.2` cross-reference in `AGENTS.md` §2 to point at `research/verification-toolchain-comparison.md`, which is where that toolchain-comparison content actually lives now. `S3`.
- **DOC-13** — Not applicable (checked 2026-07-26). fix.md claimed the `materialize()` section (added for PROM-7) was missing from `RL2_Semantics.md`'s table of contents. Verified: `RL2_Semantics.md` has no Table-of-Contents section at all — unlike `RL2_Primer.md`/`RL2_Protocol.md`/`RL2_Vocabulary.md`/`RL2_References.md`, which all have one. Nothing to add an entry to; adding a full TOC to a 1749-line, 30-heading document is a separate, larger undertaking than what fix.md described, and out of scope for this pass. `S3`.
- **DOC-14** — ✅ Resolved (2026-07-26). `design-forth-ir.md` and `design-canonical-form.md` (both historical/superseded design-rationale docs per their own top-of-file disclaimers) moved from repo root to `research/`, alongside `verification-toolchain-comparison.md`. Inbound references updated: `RL2_IR.md` (5 mentions) and `issues.md` (SEM-4 entry) now say `research/design-forth-ir.md`. Root now holds only active, authoritative documents. `S3`.
- **DOC-15** — ✅ Resolved (2026-07-26). `RL2_Primer.md`'s YAML frontmatter had two editorial fields (`audience`, `prerequisites`) alongside the normative `title`/`subtitle`/`version`/`status`/`date` fields. fix.md's action line suggested dropping the frontmatter entirely, but `version`/`date` are load-bearing for DOC-1's cross-doc version normalization — removing them would have regressed that. Kept `title`/`subtitle`/`version`/`status`/`date`, dropped only `audience`/`prerequisites`; the markdown `## Table of Contents` (unaffected) remains the one place readers navigate section structure. `S3`.

---

## Band 6 — AI-Generation Tooling

### LLM-1 — No LLM-generation prompt templates, few-shot examples, or validation harness

**Status:** Open · **Severity:** S3 · **Source:** fix.md §7.2/Task 15 · **Tags:** [COV]
**Files:** new `examples/llm-generation/` (proposed)

The canonical-form invariant makes RL2 well-suited for LLM generation (graph isomorphism substitutes for a semantic theorem prover when comparing generated vs gold-standard policies — fix.md §7.1), but no concrete artifacts demonstrate this: no prompt-engineering guide for NL→RL2 generation, no NL→RL2 evaluation harness/benchmark, no few-shot examples formatted for LLM consumption. **Action:** create `examples/llm-generation/` with prompt templates, few-shot examples, and a validation harness checking LLM output against SHACL + canonical-form rules.

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
