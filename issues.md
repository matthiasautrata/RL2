# RL2 Issues Log

Single consolidated tracker for RL2 ontology, semantics, protocol, and tooling.

**Consolidated:** 2026-07-24 — merged from the former `critique.md` (three-part external review), `fix.md` (multi-role remediation plan), and the prior `issues.md`. Those three source documents are superseded by this file.

---

## How to use this file

Each issue has an ID, a status, a severity, the source(s) it came from, the files it touches, and a north-star tag. Work proceeds top-down within each priority band. When an issue is resolved, move its entry to **§ Resolved** with the decision and rationale (see ACT-1/ACT-2 for the format).

**North star.** RL2 aims to be an ODRL successor built for the reality that *nobody authors policies by hand any more*. Its two governing quality attributes are therefore:

- **Generatable** — a model generating a policy should have exactly one correct RDF shape to emit for any given normative proposition. No authoring-convenience variation.
- **Verifiable** — every construct must have deterministic, mechanized semantics (Dafny→Go) so a policy can be checked, and two policies compared, structurally.

Issues are tagged **[GEN]** (affects generatability / canonical form), **[VER]** (affects verifiability / formal semantics), or **[COV]** (vocabulary/coverage completeness) to show which attribute they serve. Many serve more than one.

**Legend.** Status: `Open` · `In progress` · `Decision needed` · `Resolved` · `Deferred`. Severity: `S1` (blocks the north star / core soundness) · `S2` (significant gap) · `S3` (polish / hygiene).

---

## Corrections to the source reviews

Grounding the reviews against the current files surfaced several stale or incorrect claims. Recorded here so we don't act on them:

- **"`RL2_Semantics.md` returns empty / no formal semantics exists."** (critique 1) — Artifact of a web fetch. The document is ~1600 lines and defines denotational + operational semantics.
- **"Conflict resolution `resolveDecision` is undefined."** (fix §4.2, §13 Modeler) — It is defined at `RL2_Semantics.md:1240` (parameterized by strategy + priorities, with explicit ambiguity error on unbroken ties).
- **"Power exercise semantics missing."** (fix §13 Modeler) — Power denotation and `ExercisePower` state transition are defined at `RL2_Semantics.md:738`.
- **"Promise→Duty generation cut off mid-definition."** (fix §13) — The remedial generation rule exists at `RL2_Semantics.md:1007`. What is genuinely open is `restoreAction` (see SEM-1).
- **"Technology stack undecided (Why3 vs Dafny vs Go)."** (fix §2, §12, P0.4) — Decided: **Dafny → Go**, committed (`de473f5`) and recorded in `backlog.md`. The entire fix §12 deliberation is historical.
- **"Prohibition can be expressed two ways (`prohibitedAction` vs `dutyAction NotDelete`)."** (critique 3) — There is no `dutyAction`/`NotDelete` idiom in core. `rl2:prohibitedAction` is already `rdfs:subPropertyOf rl2:action` (`rl2.ttl:309`). The real question (CANON-3) is class modeling, not two competing idioms.
- **"Counterparty can appear at multiple container levels."** (critique 3) — `rl2:counterparty` has domain `rl2:Norm` only; containers have no counterparty property, so container-level inheritance is not even expressible. The real question (CANON-4) is redundancy among `counterparty` / `claimHolder` / `claimAgainst` / `subject`.

---

## Priority bands (work order)

**Band 0 — Canonical form (the generatability thesis).** CANON-1..5. Establishes the "exactly one shape per proposition" invariant that everything downstream depends on. Do first: later coverage work should be authored in canonical form from the start.

**Band 1 — Formal-semantics soundness (verifiability).** SEM-1..8. Closes the gaps that block Dafny mechanization and the S1/S4/S6 proofs.

**Band 2 — Hohfeld & Promise completeness (defensibility).** HOHF-1..5, PROM-1..8. Makes the theoretical claims true, not just asserted.

**Band 3 — Expressiveness coverage.** EXPR-1..6. Recurrence, quorum, temporal arithmetic, collections, delegation, revocation.

**Band 3.5 — Use-case corpus quality.** VALID-1..2. Systemic modeling defects and non-parseable drafts surfaced by the new `tools/validate.py` SHACL harness.

**Band 4 — Implementation.** IMPL-1..3. Dafny kernel, proofs, Go extraction.

**Band 5 — Documentation hygiene.** DOC-1..7. Version normalization, dedup, navigation.

---

## Band 0 — Canonical Form (Generatability)

> **✅ Implemented in v0.6 (2026-07-24).** CANON-1..5 applied across `rl2.ttl`,
> `rl2-shacl.ttl`, `RL2_Semantics.md`, `RL2_Architecture.md`, `persona.md`,
> `RL2_Vocabulary.md`, `RL2_Primer.md`, `CLAUDE.md`, and the affected use cases.
> Ontology bumped to 0.6. See § Resolved → CANON (v0.6). Residual follow-ups are
> tracked in Band 1 (CANON-1's IR-normalization enforcement → SEM-4; the
> `promisedState` remedial-action default → SEM-1). Details retained below.

> Governing principle (adopted from critique 3): **for any normative proposition the language can express, there is exactly one valid RDF shape that expresses it.** Two graphs that differ structurally must differ semantically. Where they don't, one shape is canonical and SHACL rejects the rest. This is the single most important property for machine generation and structural equivalence checking.

### CANON-1 — Condition placement & composition semantics
**Status:** Resolved (v0.6) — composition confirmed as conjunction & documented; IR-normalization enforcement → SEM-4 · **Severity:** S1 · **Source:** critique 3 · **Tags:** [GEN][VER]
**Files:** `rl2.ttl` (`rl2:condition` domain = union(Norm, Policy)), `RL2_Semantics.md`, `rl2-shacl.ttl`

`rl2:condition` may attach to a Norm **or** a Policy (two levels — not four; Set/Offer/Agreement are Policy subclasses). The semantics define that ODRL-style `inheritFrom` is *not* supported (`RL2_Semantics.md:1428`), but they do **not** define how a Policy-level condition composes with a Norm-level condition. Is it conjunction? Override? Precedence? Undefined composition means every evaluator resolves it differently — ODRL's assigner problem in new clothes.

**Options:** (a) Pure conjunction, no override: policy-condition AND norm-condition, specified as a total function in Semantics and enforced by SHACL. (b) Single canonical location per condition *kind* — activation conditions only on Policy, content conditions only on Norm. (c) Norm-only: forbid Policy-level conditions entirely, require explicit per-norm conditions.
**Recommendation:** (a) — least disruptive, preserves existing use cases, needs only a formal merge definition + a note. Decide before Band 2 coverage work.

### CANON-2 — `promiseContent` polymorphism → split properties
**Status:** Resolved (v0.6) · **Severity:** S1 · **Source:** critique 1 & 3 · **Tags:** [GEN][VER]
**Files:** `rl2.ttl:122` (`rl2:PromiseContent` = union(Action, Duty, Condition)), `rl2-shacl.ttl`, use case 8, 11

One property `rl2:promiseContent` ranges over three structurally different things. An Action-promise ("I will delete") and a Condition-promise ("data will be deleted") differ in Tun-sollen vs Sein-sollen terms — they are *not* semantically equivalent, yet the language lets a generator emit either for the "same" intent, and forces the evaluator to understand all three. The Duty-referencing case needed a special caveat in the ontology precisely because the polymorphism created ambiguity.

**Recommendation:** Replace with three distinct properties, each with clean non-overlapping semantics: `rl2:promisedAction` (Tun-sollen), `rl2:promisedState` (Sein-sollen), `rl2:promisedDuty` (suretyship — see PROM-5). Retire `rl2:PromiseContent`. Breaking change → v0.6. Resolves half of PROM-5 as a side effect.

### CANON-3 — Prohibition vs Duty-to-refrain
**Status:** Resolved (v0.6) — class kept; duty-to-refrain + derived correlative Claim specified · **Severity:** S2 · **Source:** critique 1 §2.2 & critique 3 · **Tags:** [GEN][COV]
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

---

## Band 1 — Formal Semantics (Verifiability)

### SEM-1 — `restoreAction` / remedial-action specification
**Status:** Open · **Severity:** S1 · **Source:** fix §4.2.1, P1.2 · **Tags:** [VER]
**Files:** `RL2_Semantics.md:1007-1031`, `rl2.ttl`

The Promise→Duty remedial rule exists but `restoreAction(content)` is "implementation-defined" with no guidance — a hole in an otherwise-deterministic pipeline. Add an explicit `rl2:remedialAction` property so remediation is declared on the norm/promise rather than invented by the evaluator. Define the default mapping: Action-promise → retry the action; Duty → the duty's action; State-promise → requires explicit `rl2:remedialAction` (no default). Interacts with CANON-2 (the split makes the mapping total).

### SEM-2 — `targetNorm` lacks parametricity
**Status:** Open · **Severity:** S2 · **Source:** critique 1 §1.2 · **Tags:** [VER][COV]
**Files:** `rl2.ttl:251`, `RL2_Semantics.md`

`rl2:targetNorm` hard-references a specific Norm IRI, so state predicates (`obligationStateOperand`, `dutyPerformerOperand`) can only ask about *one enumerated* norm. You cannot express "if **any** duty is violated" or "if **all** duties in this policy are fulfilled." Needs a quantified target (e.g. a target-set selector, or a collection operand) so duty-state conditions compose.

### SEM-3 — No-Claim / Disability inference rules
**Status:** Open · **Severity:** S2 · **Source:** critique 1 §2.1, critique 2 · **Tags:** [VER][COV]
**Files:** `RL2_Semantics.md`, `RL2_Vocabulary.md`

The Vocabulary says No-Claim and Disability are "inferrable" from the absence of a Claim/Power, but no inference rule is written anywhere. Either (a) state the rules formally (closed-world absence predicates: `NoClaim(a,b,x) := ¬∃ Claim(...)`), or (b) drop the "inferrable" language and scope them out explicitly. Use case `no-claim-inference.md` exists and should drive this.

### SEM-4 — IR definition
**Status:** Open · **Severity:** S1 (blocks IMPL) · **Source:** fix P0.1 · **Tags:** [VER]
**Files:** new (`RL2_IR.md`), `RL2_Architecture.md`, `design-forth-ir.md`

`compile : Policy* → IR` leaves IR as TBD; blocks evaluator implementation and the "compile-time canonicalization" story. `design-forth-ir.md` proposes a stack-based IR — evaluate whether to adopt it, or define a flattened-norm-list IR. Must carry an equivalence obligation (IR eval ≡ RDF eval). Strongly synergistic with Band 0: canonical form makes the compile step a normalization, not a guess.

### SEM-5 — Target matching algorithm
**Status:** Open · **Severity:** S1 (blocks IMPL) · **Source:** fix P0.2 · **Tags:** [VER]
**Files:** `RL2_Architecture.md` (§TargetIndex)

Four matching modes are listed (direct, classification, sub-asset, subsumption) but the algorithm and precedence are unspecified — implementations will disagree on whether `tag:sensitive` matches `doc:report.pdf`. Specify the algorithm with strict precedence and closed-world defaults.

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

### PROM-1 — Promise-in-Agreement restriction undefended & unenforced
**Status:** Decision needed · **Severity:** S2 · **Source:** critique 2 · **Tags:** [GEN][COV]
**Files:** `RL2_Primer.md`, `RL2_Architecture.md`, `rl2-shacl.ttl`

The lifecycle Set/Offer(contain Promise) → Agreement(contains only derived Duties/Claims) is theoretically right — a promise is "contractualized" on acceptance, so keeping it alongside its generated Duty creates a dual-source problem. But the restriction is (a) never justified in prose, (b) not enforced by SHACL, and (c) at odds with the casual author who reaches for `rl2:Promise` inside an Agreement. Pick one: enforce via SHACL (`sh:not` Promise in Agreement) *with* documented rationale, or allow and define resolution identically to Offer-contained promises (in which case, why restrict?).

### PROM-2 — Framework agreements / Power-to-promise
**Status:** Open · **Severity:** S3 · **Source:** critique 2 · **Tags:** [COV]
**Files:** `RL2_Primer.md`, `usecases/*`

"A master agreement under which A may make future binding promises to B" is properly modeled as a **Power** (in A) + **Liability** (in B) inside the Agreement, plus Promises made *outside* it. RL2 can express this but never explains the Power↔Promise connection. Document it; add a use case.

### PROM-3 — Conditional promise in an accepted agreement
**Status:** Open · **Severity:** S3 · **Source:** critique 2 · **Tags:** [GEN]
**Files:** `RL2_Semantics.md`, `RL2_Primer.md`

"If audit findings > X, I promise to remediate within 30 days," placed in an Agreement — is it a conditional Duty or a Promise-that-generates-a-Duty? The architecture implies the former; resolve explicitly (falls out of PROM-1's decision + CANON-2).

### PROM-4 — No `promisorOperand` in core
**Status:** Open · **Severity:** S2 · **Source:** critique 1 §3.2, critique 2 · **Tags:** [VER][COV]
**Files:** `rl2.ttl` (cf. `dutyPerformerOperand:267`), use case 8

Duty identity-binding is core-supported (`dutyPerformerOperand`); promise identity-binding is delegated to a profile operand (use case 8's `governance:promisorOperand`). If Promise is first-class, add a core `rl2:promisorOperand` for symmetry.

### PROM-5 — "Promise references a Duty" = suretyship, unspecified
**Status:** Open · **Severity:** S2 · **Source:** critique 1 §3.2, critique 2 · **Tags:** [VER][COV]
**Files:** `rl2.ttl:122`, `RL2_Semantics.md`

Promising to fulfill *someone else's* Duty (without becoming its dutyHolder) is a real legal concept — guarantee/suretyship — with no analysis. CANON-2's `rl2:promisedDuty` names it; this issue is to give it semantics (what state/obligation the suretyship promise creates for the promisor).

### PROM-6 — Promise-as-Generator mechanism
**Status:** Open · **Severity:** S2 · **Source:** critique 1 §3.2 · **Tags:** [VER]
**Files:** `RL2_Semantics.md:1007`, `RL2_Protocol.md`

"When the world deviates from a Promise's invariant, generate a remedial Duty" — but what triggers the check (continuous? event-driven?), who defines "deviation," and how does it interact with SEM-1 `restoreAction`? Specify the trigger and detection model.

### PROM-7 — `PromiseState` vs `RequirementStatus` dual state machines
**Status:** Open · **Severity:** S2 · **Source:** critique 1 §3.2, critique 2 · **Tags:** [VER]
**Files:** `rl2.ttl:535`, `rl2p.ttl`, `RL2_Protocol.md`

A Promise carries `promiseState` (Pending/Fulfilled/Violated, no Active) while the Protocol wraps it in a `Requirement` whose `requirementStatus` *does* include Active. "Pending at the Promise level, Active at the Requirement level" is never reconciled. Define the projection between the two (analogous to how `projectObligationState` collapses Active→Pending for promises).

### PROM-8 — Departure from Promise Theory autonomy, unacknowledged
**Status:** Open · **Severity:** S3 · **Source:** critique 1 §3.2 · **Tags:** [COV]
**Files:** `RL2_Primer.md`, `RL2_References.md`

Burgess's Promise Theory assesses a promise from the *promisee's* observation — no central truth. RL2 tracks promise state centrally in Σ (a contract-law model). This may be the right engineering choice, but the philosophical departure should be stated, not silent.

---

## Band 3 — Expressiveness Coverage

### EXPR-1 — Recurrent / periodic duties
**Status:** Open · **Severity:** S2 · **Source:** fix §4.2.2, backlog · **Tags:** [COV]
"Every quarter," "annually." Options: `rl2:DutyTemplate` + recurrence + event-triggered instantiation, or a recurrence profile. Decide core vs profile.

### EXPR-2 — Quorum / k-of-n approvals
**Status:** Open · **Severity:** S2 · **Source:** fix §4.2.3, backlog · **Tags:** [COV]
Cannot express "any 2 of 5 approvers." Add a quorum constraint (min approvers + approver pool). Interacts with SEM-2 (quantified operands).

### EXPR-3 — Native temporal arithmetic
**Status:** Deferred · **Severity:** S3 · **Source:** backlog, critique 1 · **Tags:** [COV]
Relative time ("30 days after event") needs profile operands like `daysSinceEvent`. Native `xsd:duration` arithmetic (`currentDateTime − eventTime < P30D`) deferred to keep the kernel small. Revisit if recurrence (EXPR-1) forces it.

### EXPR-4 — AssetCollection dynamic membership
**Status:** Open · **Severity:** S3 · **Source:** fix §8.2 (+HOHF-5) · **Tags:** [COV]
Only `rl2:member` enumeration. Add `rl2:selectionCriteria` (a Condition) for "all assets with tag:PII." Watch canonical-form: enumeration vs criteria must not become two ways to say the same set.

### EXPR-5 — Delegation model
**Status:** Open · **Severity:** S3 · **Source:** fix §8.2 · **Tags:** [COV]
"Alice grants Bob power to act on her behalf." Likely expressible today via Power/Liability — check before adding `rl2:delegatedTo`. May be a documentation issue, not a vocabulary gap.

### EXPR-6 — Revocation vocabulary
**Status:** Open · **Severity:** S3 · **Source:** fix §8.2 · **Tags:** [COV]
Power-to-revoke exists but there is no explicit revocation event. Consider `rl2:RevocationEvent` in the protocol layer. Use cases `approval-revocation.md`, `immunity-from-termination.md` should drive this.

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
**Status:** Partially resolved · **Severity:** S3 · **Source:** validation harness · **Tags:** [COV]
**Files:** `RL2_Semantics.md` ✅, `RL2_Primer.md` ✅, `RL2_Vocabulary.md` ✅, `RL2_Protocol.md` ⏳

The same "every example validates or is empty" standard applies to the spec docs, not
just the use cases. The harness gained a **`--per-fence`** mode for this: each
```turtle``` fence is validated as its own graph (ontology merged in), because a
reference doc's fences are *independent* illustrations — a shared example IRI reused
across sections must not merge into one graph (whole-file mode would force false
cardinality conflicts). Use cases keep whole-file mode (their fences build on each
other). Run: `uv run tools/validate.py --per-fence <doc>.md`.

**Done:** Semantics, Primer, Vocabulary all pass per-fence. Fixes were of two kinds:
(1) demote genuine narration fragments (state-machine transition triples, bare
predicate snippets) to plain code fences; (2) complete labeled examples so each is
valid standalone (define the Power/Duty/Promise/Policy an example references; use
`xsd:anyURI` literals for `policyGeneration`, not IRIs).

**Remaining — `RL2_Protocol.md`.** 9 fences still fail per-fence
(`fence@189, 311, 320, 356, 553, 703, 738, 762, 805`). They develop a shared
loan-access / data-contract scenario, so each fence references entities defined only
in *other* fences (`ex:request1`, `ex:req1/req2`, `ex:loanAccessPolicy`,
`ex:managerApprovalDuty`, `ex:dataQualityPromise`, `ex:dataContract`, `ex:case1`,
`ex:eval1`, `ex:fulfillment1/2`). Under `rdfs` inference the referenced IRIs get typed
via property ranges (e.g. `evaluatedRequest` range `Request`), so the shapes then
demand their required fields. Note whole-file mode is *not* a fallback here: it has
genuine merge conflicts (`ex:eval1` is defined twice with two decisions/explanations;
a Request ends up with two requestors) — confirming per-fence is the correct model.

**Fix (same recipe as Primer/Vocabulary):** make each of the 9 fences self-contained —
define the source norm/promise (typed), its source Policy (with ≥1 clause), the
referenced Request (action/asset/agent/time), and, for `requirementFulfilled`
assertions, the performer. Then `uv run tools/validate.py --per-fence RL2_Protocol.md`
should report all fences OK.

---

## Band 4 — Implementation

### IMPL-1 — Dafny core modules
**Status:** Open · **Severity:** S1 · **Source:** backlog Phase 1, fix §12 · **Tags:** [VER]
Translate `RL2_Semantics.md` to Dafny. Blocked on SEM-4 (IR) and SEM-5 (target matching). Toolchain decided (Dafny→Go).

### IMPL-2 — Discharge proofs S1 / S4 / S6
**Status:** Open · **Severity:** S1 · **Source:** backlog, fix · **Tags:** [VER]
S1 Determinism, S4 Duty-state consistency, S6 Totality. Fold SEM-8's obligations in. These substantiate the "formally verified" claim.

### IMPL-3 — Go extraction, CLI, property tests
**Status:** Open · **Severity:** S2 · **Source:** backlog · **Tags:** [VER]
`rl2-eval --policy p.ttl --request r.json`; property-based tests; validate against use cases 1–17.

---

## Band 5 — Documentation Hygiene

- **DOC-1** — ✅ Resolved (v0.6). Spec-suite docs normalized to `version: "0.6"` / `date: 2026-07-24` (Semantics, Architecture, Vocabulary, Primer, Protocol, References, README banner). RDF artifacts keep truthful `owl:versionInfo`: `rl2.ttl` 0.6 (changed), `rl2p.ttl` 0.5 (unchanged); Vocabulary footer notes the split. `RL2_ODRL_Comparison.md` retains its own doc version (1.0). `S3`.
- **DOC-2** — `RL2_Vocabulary.md` vs `rl2.ttl` duplication (~800 lines). Keep TTL authoritative; Vocabulary as gloss. `S3`.
- **DOC-3** — Remove redundant AI-config pointer files `codex.md`, `gemini.md` (4-line pointers; Codex retired per global policy), and reconcile `claude.md` with `persona.md`. `S3`.
- **DOC-4** — Merge `RL2_ODRL_Comparison.md` into `RL2_Primer.md` as a comparison section (+ an ODRL→RL2 migration guide). `S3`.
- **DOC-5** — Add a document-navigation map ("I want to… → read…") to `README.md`. `S3`.
- **DOC-6** — Terminology consistency: `ObligationState` (not DutyState), `Norm` (not Rule), clarify Requirement-wraps-Duty. `S3`.
- **DOC-7** — Reconcile `backlog.md` with this log (overlap: recurrence, temporal arithmetic, toolchain, namespace). Keep backlog for forward *work items*; this file owns *issues*. `S3`.

---

## Resolved

### ACT-1 — Action ontological status & hierarchy mechanism
**Resolved.** Actions are named **individuals** of `rl2:Action`; hierarchies use `rl2:includedIn` (transitive object property), not `rdfs:subClassOf`. No punning; subsumption is bounded graph reachability (`ASK { ?req rl2:includedIn* ?pol }`), not OWL reasoning; ODRL-compatible. Optional SKOS alignment kept out of core. Applied to `rl2.ttl`, `RL2_Semantics.md`, `RL2_Vocabulary.md`, `CLAUDE.md`, and affected use cases. Ingestion is tolerant: legacy `rdfs:subClassOf` between Action individuals is transpiled with a diagnostic.

### ACT-2 — Action subsumption asymmetry (request matching vs duty fulfillment)
**Resolved.** Subsumption applies **uniformly** across norm types via a read-time helper `performed(a,x,s,Σ) := ∃x′ : Σ.Performed(a,x′,s) ∧ (x′ = x ∨ x′ ⊑ x)`. `Σ.Performed` stays an exact log; the helper adds subsumption at query time. Decisive case: performing `fineTune` must violate a prohibition on `trainModel` when `fineTune includedIn trainModel`; the same logic extends to duty fulfillment. All `Σ.Performed(...)` checks in `RL2_Semantics.md` replaced with `performed(...)`. Profiles needing exact-match should define the action at the exact level.

### CANON (v0.6) — Canonical-form band
**Resolved 2026-07-24 (ontology → 0.6).** Adopted the invariant *exactly one valid RDF shape per normative proposition* and applied it:

- **CANON-5 / CANON-1.** Invariant documented in `RL2_Architecture.md` §Canonical Form and `persona.md` §11. Condition composition confirmed as conjunction (`n.effectiveCondition = And(P.condition, n.condition)`, already in semantics); canonical rule = author at narrowest scope; policy conditions pushed down during IR normalization (enforcement is an IR obligation → **SEM-4**).
- **CANON-2.** Retired the polymorphic `rl2:promiseContent` / `rl2:PromiseContent` union. Added three disjoint properties: `rl2:promisedAction` (Tun-sollen), `rl2:promisedState` (Sein-sollen), `rl2:promisedDuty` (suretyship). `rl2:object` domain broadened to `Norm ∪ Promise`. `PromiseShape` now requires exactly one via `sh:xone`. Semantics `contentHolds`/`deadline`/`linkedDuty`/remedial rules rewritten over the tagged union (`contentHolds` reuses the ACT-2 `performed()` helper); `restoreAction`/`objectOf` made total (PromisedState remedial default → **SEM-1**). `promisedDuty` now has real semantics, resolving most of **PROM-5**. Migrated use cases 8 (`promisedAction`) and 11 (`promisedState`, dropping the invented `rl2:recurrence` → **EXPR-1**).
- **CANON-3.** `rl2:Prohibition` kept as the sole negative-duty form; semantics now state it is a duty-to-refrain whose correlative **Claim** is held by its `counterparty` (or the grantor), derived not authored.
- **CANON-4.** Unified normative roles on `rl2:subject` (right-holder) / `rl2:counterparty` (duty-bearer); **removed** `rl2:claimHolder` / `rl2:claimAgainst`. `ClaimShape` and all references migrated (Primer, Vocabulary, CLAUDE.md, use cases claim-counterclaim / no-claim-inference / pass-through-terms).

No backward-compatibility aliases (clean break, per decision). `rl2.ttl` and `rl2-shacl.ttl` parse clean; no residual references outside explanatory comments.
