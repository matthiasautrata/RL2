# Design Note: Canonical Form (Band 0, v0.6)

**Status:** ✅ Implemented in v0.6 (2026-07-24) · **Date:** 2026-07-24
**Issues:** CANON-1..5 (see `issues.md` → § Resolved) · **Version:** RL2 0.6

This note specifies the concrete changes for the canonical-form band. It was the
"draft the plan first" deliverable and has since been applied in full. Retained as
the design-rationale record. **Sub-decisions settled:** (1) broaden `rl2:object`
to `Norm ∪ Promise` — **yes**; (2) unify on `subject`/`counterparty`, remove
`claimHolder`/`claimAgainst` — **yes**; (3) derive the Prohibition's correlative
Claim in semantics — **yes**; (4) tolerant-ingestion aliases — **no** (clean v0.6
break, no backward-compatibility baggage).

---

## The invariant we are buying (CANON-5)

> **For any normative proposition RL2 can express, there is exactly one valid RDF shape that expresses it.** Two graphs that differ structurally must differ semantically; where they don't, one shape is canonical and SHACL (or IR normalization) rejects or rewrites the rest.

Why this is the foundation for the north star:

- **Generatable.** A model emitting a policy never has to choose among equivalent encodings — there is one target shape. Prompting and fine-tuning both get dramatically easier when the output is canonical.
- **Verifiable.** Semantic equivalence reduces to graph isomorphism after normalization. No bespoke normalizer full of edge cases (the place ODRL bugs live).

**Action:** add a short "Canonical Form" section to `RL2_Architecture.md` stating the invariant, and a design rule to `AGENTS.md`. CANON-1..4 are the concrete instances; every future construct is checked against the invariant.

Grounding correction: RL2 is already *closer* to this than the reviews implied — condition composition is defined, `prohibitedAction ⊑ action`, roles are Norm-scoped. The work is finishing the job, not starting it.

---

## CANON-1 — Condition placement: normalize, don't multiply

**Current state (grounded).** `rl2:condition` attaches to a Norm or a Policy (two levels; Set/Offer/Agreement are Policy subclasses). Composition is *already defined* as conjunction — `RL2_Semantics.md:112`, `:810–838`:

```
NormActive(n, P, Env) = PolicyApplicable(P, Env) ∧ ⟦n.condition⟧(Env) = true
n.effectiveCondition   = And(P.condition, n.condition)
```

So there is no "undefined merge operator" (contra critique 3). The only residual canonical-form hazard: for a **single-norm policy**, a condition can go on the policy *or* the norm with identical effect — an ODRL-assigner-style redundancy.

**Proposed resolution (no ontology change).**
1. Keep both attachment points — they have genuinely different scope (policy-condition gates all norms; norm-condition gates one).
2. Declare the **canonical authoring rule**: place a condition at the *narrowest* level that carries its scope. A condition scoping exactly one norm belongs on that norm.
3. Enforce canonicality at **compile time, not in SHACL**: IR normalization pushes every policy condition down into each norm's `effectiveCondition` via the existing `And()`. The IR therefore carries conditions *only on norms* — one shape. (This is a SEM-4 IR obligation; recorded there.)

**Files:** `RL2_Architecture.md` (canonical-form section + IR normalization rule), `AGENTS.md` (authoring rule). No `rl2.ttl` / SHACL change.

---

## CANON-2 — Split `promiseContent` into three typed properties

**The problem, confirmed in the wild.** `rl2:promiseContent` ranges over `owl:unionOf (Action Duty Condition)`. The two promise use cases already encode content *incompatibly*:

- `data-stewardship.md`: `rl2:promiseContent ex:DataStewardshipCommitment` (a named individual).
- `data-freshness-promise.md`: `rl2:promiseContent [ a rl2:PromiseContent ; rl2:action …; rl2:object …; rl2:recurrence … ]` — instantiates the *union class* directly and invents `rl2:recurrence`.

Two authors, two shapes, for structurally similar promises. This is exactly the polymorphism the invariant forbids. An Action-promise (Tun-sollen, "I will do X") and a state-promise (Sein-sollen, "X will hold") are **not** semantically equivalent, yet the union lets a generator pick either.

**Proposed ontology change (`rl2.ttl`).** Retire the union; introduce three properties with disjoint semantics:

```turtle
# REMOVE:
#   rl2:PromiseContent (owl:unionOf ...)   and   rl2:promiseContent

rl2:promisedAction a owl:ObjectProperty ;
    rdfs:domain rl2:Promise ; rdfs:range rl2:Action ;
    rdfs:label "Promised Action" ;
    rdfs:comment """Tun-sollen: the promisor commits to performing this action
    (on rl2:object). Fulfilled when the promisor has performed it.""" .

rl2:promisedState a owl:ObjectProperty ;
    rdfs:domain rl2:Promise ; rdfs:range rl2:Condition ;
    rdfs:label "Promised State" ;
    rdfs:comment """Sein-sollen: the promisor commits to a state of affairs holding.
    Fulfilled when the condition evaluates true; violated when it fails
    (or its deadline passes unmet).""" .

rl2:promisedDuty a owl:ObjectProperty ;
    rdfs:domain rl2:Promise ; rdfs:range rl2:Duty ;
    rdfs:label "Promised Duty" ;
    rdfs:comment """Suretyship: the promisor commits to seeing that this Duty is
    fulfilled. The promisor does NOT thereby become the Duty's rl2:subject.
    Fulfilled when the Duty's ObligationState reaches Fulfilled.""" .
```

Broaden `rl2:object` so an action-promise can name its asset:

```turtle
rl2:object  rdfs:domain [ owl:unionOf (rl2:Norm rl2:Promise) ] .   # was rl2:Norm
```

**SHACL (`rl2-shacl.ttl`).** Replace the `sh:xone` over `promiseContent` in `PromiseShape` with an exactly-one over the three new properties:

```turtle
rl2:PromiseShape a sh:NodeShape ;
    sh:targetClass rl2:Promise ;
    sh:property [ sh:path rl2:promisor ; sh:minCount 1 ; sh:class rl2:Agent ] ;
    sh:property [ sh:path rl2:promisee ; sh:minCount 1 ; sh:class rl2:Agent ] ;
    sh:xone (
        [ sh:property [ sh:path rl2:promisedAction ; sh:minCount 1 ; sh:maxCount 1 ] ]
        [ sh:property [ sh:path rl2:promisedState  ; sh:minCount 1 ; sh:maxCount 1 ] ]
        [ sh:property [ sh:path rl2:promisedDuty   ; sh:minCount 1 ; sh:maxCount 1 ] ]
    ) ;
    sh:message "A Promise must have exactly one of promisedAction, promisedState, or promisedDuty." .
```

**Semantics (`RL2_Semantics.md`).** `contentHolds` becomes a clean dispatch on which property is present — and reuses the `performed()` helper from ACT-2, so no new machinery:

```
contentHolds(p, Σ) =
    performed(promisor(p), promisedAction(p), object(p), Σ)   if p has promisedAction
    ⟦ promisedState(p) ⟧(Env) = true                          if p has promisedState
    ObligationState(promisedDuty(p), Σ) = Fulfilled           if p has promisedDuty
```

This also gives `promisedDuty` real semantics — resolving the "what does it mean to promise a Duty" gap (PROM-5) — and makes `restoreAction` (SEM-1) total: retry the action / re-assert the state / fulfill the duty, respectively.

**Migration impact.** Small and clarifying:
- `data-freshness-promise.md` → `rl2:promisedAction datacontract:refreshData ; rl2:object ex:CustomerDataset`. (The invented `rl2:recurrence` is dropped; recurrence is EXPR-1, handled separately.)
- `data-stewardship.md` → `rl2:promisedState ex:DataStewardshipCommitment` if it's a condition, or `promisedAction`/`promisedDuty` per its real intent (needs a look at the full file).
- `RL2_Semantics.md:64,67,165,215,539–579,896,916` grammar/typing/`contentHolds` updated. `RL2_Primer.md`, `RL2_Vocabulary.md` prose updated.

---

## CANON-3 — Prohibition: keep the class, pin the semantics

**Decision:** keep `rl2:Prohibition` (ergonomic for generators and authors; already the *only* negative-duty idiom — there is no `dutyAction NotDelete` form, contra critique 3). The gap is purely semantic: its place in the Hohfeld square is unstated.

**Proposed additions (semantics + doc, minimal ontology).**
1. State in `RL2_Semantics.md` and `RL2_Vocabulary.md`: a `Prohibition(s, x, o)` is a **duty to refrain**; its Hohfeldian correlative is a **Claim** held by `rl2:counterparty(prohibition)` that `s` not perform `x` on `o`. When no counterparty is named, the correlative claim is held by the policy grantor.
2. Prohibition violation already uses the subsumption-aware `performed()` (ACT-2) — confirm and cross-link.
3. No new property required; `rl2:counterparty` (domain Norm) already applies to Prohibition. Optionally document derivation of the correlative Claim rather than forcing authors to assert it.

**SHACL:** none needed (no competing encoding exists to forbid). This issue is a semantics/doc fix, not a shape change.

---

## CANON-4 — Unify normative roles on `subject` / `counterparty`

**The redundancy.** Four role properties overlap: `rl2:subject`, `rl2:counterparty` (Norm-scoped) and `rl2:claimHolder`, `rl2:claimAgainst` (Claim-scoped). A Duty↔Claim pair can name "who is owed" twice, two different ways.

**Proposed canonical rule.** `subject`/`counterparty` are authoritative on **every** norm, including Claim:
- On a Claim: `rl2:subject` = the right-holder (was `claimHolder`); `rl2:counterparty` = the duty-bearer (was `claimAgainst`).
- **Deprecate and remove** `rl2:claimHolder` and `rl2:claimAgainst` in v0.6. Four role properties → two, uniform across all norm types. Correlative alignment (Duty.subject = Claim.counterparty, Duty.counterparty = Claim.subject) becomes a single checkable rule.

**Ontology (`rl2.ttl`).** Remove `rl2:claimHolder`, `rl2:claimAgainst`. **SHACL (`rl2-shacl.ttl`).** Rewrite `ClaimShape`:

```turtle
rl2:ClaimShape a sh:NodeShape ;
    sh:targetClass rl2:Claim ;
    sh:property [ sh:path rl2:subject ; sh:minCount 1 ; sh:class rl2:Agent ;
        sh:message "A Claim's subject is the right-holder." ] ;
    sh:property [ sh:path rl2:counterparty ; sh:minCount 1 ; sh:class rl2:Agent ;
        sh:message "A Claim's counterparty is the duty-bearer." ] .
```

**Migration impact (grepped).** `claimHolder`/`claimAgainst` appear in `usecases/{claim-counterclaim, no-claim-inference, pass-through-terms}.md`, plus `RL2_Primer.md`, `RL2_Vocabulary.md`, `claude.md`. All mechanical renames. Optional courtesy: an ingestion alias (`claimHolder → subject`) with a diagnostic, mirroring the ACT-1 tolerant-ingestion stance.

**Sub-decision:** this is the most invasive rename. Alternative (less clean): keep `claimHolder`/`claimAgainst` as the canonical Claim roles and *forbid* `counterparty` on Claim. I recommend unifying on subject/counterparty (fewer properties, uniform), but it touches more files.

---

## Version bump

As part of this batch: `rl2.ttl` header `owl:versionInfo "0.5" → "0.6"`, `owl:versionIRI …/0.5 → …/0.6`. Prose-wide version normalization (DOC-1) is deferred to the end so it captures every doc at once.

---

## Sub-decisions I need before applying

1. **CANON-2 object placement.** Broaden `rl2:object` domain to `union(Norm, Promise)` so an action-promise names its asset (recommended), *or* keep object out of promises and require action-promises to reference a fully-specified structure? → **Recommend: broaden `rl2:object`.**
2. **CANON-4 role unification.** Remove `claimHolder`/`claimAgainst` in favor of `subject`/`counterparty` (recommended, more files), or keep Claim-specific roles and forbid `counterparty` on Claim (fewer files, less uniform)? → **Recommend: unify.**
3. **CANON-3 correlative Claim.** Auto-*derive* the Prohibition's correlative Claim in semantics (author writes only the Prohibition), or require authors to assert both? → **Recommend: derive; document.**
4. **Ingestion aliases.** Provide tolerant-ingestion transpilation for the retired `promiseContent` / `claimHolder` / `claimAgainst` (diagnostic + rewrite), consistent with ACT-1, or hard-break at v0.6? → **Recommend: provide aliases** (cheap, and helps any future ODRL→RL2 transpiler).

Once these four are settled I'll implement CANON-1..5 as one v0.6 changeset, migrate the affected use cases, and run `shacl validate` against them.
