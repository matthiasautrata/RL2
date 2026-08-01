# RL2 0.7 — Consolidated Proposals

Consolidation of three independent reviews — `fix.md`, `fix-gpt.md`, `fix-agy.md` — cross-checked
against the corpus. No input was taken as authoritative: every claim adopted here was re-verified
against the spec files, and input claims that failed verification are listed with rationale in §5.
Validation baseline at consolidation time: `uv run tools/validate.py` → PASS 46 · FAIL 0.

Structure: §1 proposals sorted by value, each with origin, adjudication, recommendation, and
caveats · §2 corpus and editorial repairs · §3 complications that need real algorithms ·
§4 consolidated answers to the modeling questions · §5 input claims rejected or corrected ·
§6 work order · §7 merged references.

Origin tags: **[O]** = fix.md · **[G]** = fix-gpt.md · **[A]** = fix-agy.md.

---

## 1. Proposals, sorted by value

Value ordering rationale: an item ranks higher the more it (a) blocks the spec's own stated claims
(determinism, SHACL-then-never-fail, ODRL upgrade path), (b) unblocks other items, and (c) was
independently found by multiple reviews. Items 1–5 are release stoppers; 6–15 are semantic
correctness; the rest is structure and hygiene (§2).

### P1 · Specify the end-to-end compilation contract (SHACL → typed module → Eval)

**Origin:** [O] F8+§10.1 and [G] C3-1, independently converging on the same architecture; [A]
endorses the AST-interpreter direction. The strongest agreement across all three reviews.

**Problem.** The property the project wants — *a SHACL-valid policy plus a passing request cannot
fail* — is false today, structurally, not incidentally:

- `rl2:OperandRangeTypeShape` is `sh:severity sh:Warning` (`spec/rl2-shacl.ttl:446-463`), and
  warnings do not break conformance (`tools/README.md:27-29`). It is also a syntactic datatype-IRI
  comparison, so `xsd:dateTime` vs `xsd:dateTimeStamp` and `xsd:integer` vs `xsd:decimal` trip it
  spuriously — which is presumably why it was demoted.
- Operator/type compatibility is unchecked entirely: ordered comparison on an IRI, `isAllOf`
  against a scalar, `isA` without a finite class model [G].
- Condition cycles, status-dependency cycles, invalid Duty windows, path validity, and bounds are
  checked after SHACL, if anywhere; shapes are open, so unknown properties survive silently [G].
- Request, WorldSnapshot, EvaluationConfiguration, and EvaluationResult have no normative
  interchange schema [G].

A policy can therefore validate cleanly and be *guaranteed* to evaluate `Unknown` on every request.

**Recommendation.** Three ordered phases, with phase ② the new normative artifact:

```text
RDF dataset
   │  ① SHACL: structural well-formedness            → Violation | ok
   ▼
   │  ② compile: projection + link + type/effect +   → CompileErrors | CompiledPolicyModule
   │     cycle + bound checks (total, deterministic)
   ▼
CompiledPolicyModule (typed, flat, closed)
   │  ③ Eval(module, Request, Snapshot, Config)      → EvaluationResult
```

with the soundness theorem stated normatively:

> If `compile(G, profiles, cfg) = Ok(m)`, then for every schema-valid Request, Snapshot, and
> Configuration, `Eval(m, …)` contains no `Invalid(ComparisonSite(…))` cause. A compiled policy
> never fails for reasons of its own; it can only be indeterminate because the world is.

Residual `Missing`/`Conflict` causes remain — correctly, as properties of the data.

**Design principle (owner-endorsed 2026-08-01): authoring forms compile down; `Eval`'s kernel
never grows.** Ergonomics live in expansion (refinements → conditions, recurrence → finite
windows, profiles → vocabulary bindings, transpiler → ODRL conveniences); semantics and proofs
live on the kernel only. This is the macro discipline of Rust/Elixir applied to a policy
language, and it is simultaneously the verification strategy — the mechanized model covers the
kernel, and every convenience is correct by construction of its expansion. State it in
`RL2_Scope.md` when P1 lands.

Module shape (merging [O]'s flat-AST and [G]'s CompiledPolicyModule, which agree on everything
material): flat arrays with integer indices, no blank-node identity, bytewise-diffable; every
condition node carries its resolved `ValueType`; every operand its resolved
`(scope, canonicalPath, declaredType, profile)` tuple; action-inclusion and type closures
materialized as index arrays; Duty forms pre-discriminated; profile digests, source map, and
declared bounds embedded. Serialize as canonical JSON or deterministic CBOR. Each compile stage
owns named stable diagnostics. Core-namespace properties are closed; extension properties require
a declared supported profile; annotations survive only in the source map [G].

**Caveats.**
- Both reviews independently reject a stack/bytecode IR as the *normative* target ([G] explicitly:
  it obscures algebraic types, provenance, and proof structure — fine as a private backend, as OPA
  lowers its IR to Wasm). Do not litigate this again.
- SHACL keeps only structural obligations after this change; delete or fully demote
  `OperandRangeTypeShape` rather than half-trusting it.
- If a stable digest of *source RDF* is wanted, RDFC-1.0 is the tool, but it needs resource limits
  (adversarial blank-node graphs are expensive — see §3.5).

**Effort:** the largest single work item; ~2–3 person-months for the compile contract, schemas, and
diagnostics ([G]'s estimate; [O]'s 3–4 weeks covered a narrower typing pass).

### P2 · Population subjects and classification-based targeting — DECIDED 2026-08-01

**Origin:** [O] G1/G2 (language-level fix) and [G] C2-6 (assembly-boundary fix). These look like
competing answers; adjudication below concludes they are complementary and both are needed.

**Decisions (owner-confirmed):**
1. **Both mechanisms**: `rl2:AgentCollection` (closed enumerated groups, direct `rl2:member`,
   mirroring `AssetCollection`) AND unbound subjects/objects for attribute-defined populations.
   Matching unifies into one rule with a per-axis declared preorder (absorbs [O] O1).
2. **Unbound form = sentinel individuals** `rl2:anyAgent` / `rl2:anyAsset` — SHACL keeps
   `minCount 1`, so an unbound norm is always an explicit authoring act, never a forgotten
   property silently becoming a universal grant (the fail-closed property matters doubly for
   AI-generated policies). One canonical form per proposition holds.
3. **Assembly contract is informative in 0.7** — documented
   `assemble(Catalogue, SelectionRule, Bindings) → PolicyUniverse | AssemblyErrors` with
   identity/digest/provenance requirements pinned; normative once a deployment exercises it.

**Problem.** `subjectMatches(a, requested) = a = requested` (`spec/RL2_Semantics.md:909-910`) with
`sh:minCount 1 ; sh:maxCount 1 ; sh:class rl2:Agent` (`spec/rl2-shacl.ttl:102,144,197`): every norm
names exactly one concrete Agent. Same on the object axis: a concrete Asset or an AssetCollection
with *direct* members. Consequences, verified in the corpus:

- "Any researcher may read X" is inexpressible. `conformance/usecases/ethics-approval.md` writes
  `rl2:subject ex:Researcher`, sends the request from Alice, and expects `Permit` — which
  contradicts `subjectMatches`; the use case or the semantics is wrong (verified this sweep;
  [G] §7's "no additional structural failure" missed it).
- The spec's own escape hatch — *"role-based authorization uses an explicit condition over a
  profile-defined agent fact"* (`RL2_Semantics.md:955`) — cannot work: matching fails before any
  condition is evaluated.
- "This Set applies to any asset classified `home-loan-data`" is inexpressible, though the
  classification exists as a snapshot fact and the privacy profile declares the operand for it.
  This is Immuta's entire deployment model and blocks the three-Set scenario in §4.2.
- RL2 is currently *less* expressive than ODRL 2.2 here (`odrl:PartyCollection`,
  source-based `odrl:AssetCollection`), which undercuts the upgrade-path claim.

**Recommendation — both mechanisms, different jobs:**

1. **Language level** [O]: (a) `rl2:AgentCollection` mirroring `AssetCollection` with direct
   `rl2:member`, extending `subjectMatches` to the exact rule `objectMatches` already uses; and
   (b) distinguished `rl2:anyAgent` / `rl2:anyAsset` individuals for which matching is `true`,
   so the population is defined by conditions over `agent.*` / `asset.*` facts. (a) covers closed
   enumerated groups; (b) covers attribute-defined populations; neither subsumes the other.
2. **Assembly level** [G]: a pure, documented preprocessing contract
   `assemble(CatalogueSnapshot, SelectionRule, OfferBindings) → PolicyUniverse | AssemblyErrors`
   for *catalog-driven selection of which policies enter the universe* — tag-selected Sets,
   data-product governance. Informative in 0.7 is acceptable, but it must pin selected-policy
   identity/digests, tag interpretation, duplicate-clause identity, and provenance. Discovery
   stays outside `Eval`.

Adjudication: (2) alone cannot express "any agent with clearance ≥ 3" — assembly selects policies,
it cannot quantify over requesters; (1) alone does not answer how three tag-matched Sets get into
the universe deterministically. They compose: unbound norms make the policy *meaning* right,
assembly makes the policy *selection* reproducible.

**Caveats.**
- Indexing degrades: with equality matching, candidate selection is a hash lookup on
  `(subject, action, object)`; unbound norms need a separate always-scanned bucket. State this in
  `docs/RL2_Architecture.md §7` and design the extension so bound norms keep the fast path [O].
- Fold [O] O1 in here: today the three request axes have three unrelated matching disciplines
  (subject exact; object equality ∨ direct member; action equality ∨ transitive `includedIn`).
  Define one `matches(declared, requested, ⊑axis)` with a per-axis declared preorder, and put the
  transitivity policy in one table with its rationale — the asymmetry (actions transitive, assets
  not) is defensible but currently buried in a paragraph (`RL2_Semantics.md:935`).
- A missing population-defining fact must yield `Indeterminate`, not silent `Permit`; the existing
  Kleene machinery gives this for free, but add a vector proving it.

### P3 · Make the conformance suite executable

**Origin:** [O] E3 and [G] C3-3, in full agreement. [G] adds tooling-hardening detail.

**Problem.** `conformance/vectors/README.md:11` says "Each executable vector…", but all four vector
files are prose tables; `tools/validate.py` runs SHACL only; migration fixtures pair ODRL input
with expected RL2 output but nothing translates or compares. The central claim — independent
evaluators agree — is unfalsifiable. Two implementations could pass everything in `conformance/`
and disagree on every request.

**Recommendation.**
1. Machine-readable vector format (JSON/YAML): universe (or compiled module), request, snapshot,
   configuration, expected compile result, expected envelope, expected Duty/Promise statuses,
   expected decision, expected diagnostics. Convert the 4 vector files and the ~15 highest-value
   use cases.
2. Negative compiler vectors for every rejected and non-canonical form [G].
3. A translation runner comparing normalized ODRL fixtures to expected modules [G].
4. Two independent evaluator implementations before any interoperability claim [G].
5. Harden `tools/validate.py`: stop silently skipping any fence containing `...`
   (`validate.py:95-107`); make the injected prefix `PREAMBLE` opt-in or add a second strict parse
   pass, so publication examples that omit `@prefix` are caught [O][G]; parse the SHACL report
   graph instead of counting rendered severity strings; validate the shapes graph itself; pin
   `rdflib`/`pyshacl` versions [G].
6. Immediately: change "Each executable vector" to "Each vector" until a runner exists [G].

**Caveat.** A vector format with no runner still has value — it makes expected results unambiguous
and diffable — so don't gate the format on the evaluator. But P1 should land first or in parallel:
vectors are most useful stated against the compiled module, not raw RDF.

### P4 · An executable profile contract (ProfileModule)

**Origin:** [G] C3-2, the strongest finding unique to one review; [O] O5/O6 corroborate from the
corpus side.

**Problem.**
- `declaringProfile(op)` is consumed by `deref` (`spec/RL2_Semantics.md:615`) but **no RDF property
  binds an operand to a profile** — verified: the term appears nowhere in any Turtle file. The
  privacy profile declares 16 operands with no membership link; namespace ownership is not
  sufficient (the ODRL Profile Best Practices explicitly separates profile identity from
  namespaces).
- 32 use cases declare custom LeftOperands; **zero** declare `rl2:requiresProfile`. The fail-closed
  profile mechanism has no coverage at all [G][O].
- `docs/RL2_ExternalData.md §3` promises profile-declared cardinality and allowed operators; the
  profile vocabulary has no properties or shapes for either. `RL2_ODRL_Mapping.md §7` invokes a
  "profile operator" disposition nothing supports [O].
- `admissibleFact`/`admissibleEvidence` are "total pure predicates" with no portable
  representation: two implementations can claim the same profile IRI+version and run different
  predicates [G].
- Operand typing rides on `rdfs:range` applied to *individuals*, which entails every LeftOperand is
  an `rdf:Property` — an accidental commitment [G]. (Project history corroborates: the
  `rdfs:range` widening trap has bitten twice, per the repo's own issue log.)
- The same-major SemVer compatibility rule is wrong under major version 0: SemVer says anything may
  change in 0.y.z, so `0.1.0` and `0.9.0` must not be treated compatible [G].

**Recommendation.** Adopt the ODRL 2.2 profile mechanism and the W3C Profile Best Practices in
spirit, not verbatim: ODRL already establishes that a profile is an identified artifact distinct
from its namespaces, that policies declare the profiles they depend on, and — in its conformance
clauses — that **a conforming processor must understand the profiles a policy declares or refuse
to process it**. RL2's fail-closed load-time rejection is the right half of this; the missing half
is making "understand" checkable. Concretely:

1. Define a finite `ProfileModule` manifest: profile IRI + version + canonical digest; member
   terms; per-operand `rl2:valueType` (replacing `rdfs:range` on operand individuals),
   cardinality, allowed operators, resolution path; admissibility rules in a declared portable
   form; finite hierarchy data. Require every policy using non-core terms to declare the profile.
   Same IRI+version must mean same digest. For 0.y.z, require exact-minor or a profile-declared
   compatibility range.
2. Make profile understanding an explicit **evaluator conformance requirement**, mirroring ODRL's
   processor-conformance language: a conforming evaluator rejects at load time any policy
   requiring a profile it does not support, and when it claims support for a profile it must pass
   that profile's conformance vectors (P3 format) — profile vectors, not prose, are what makes
   "two implementations support privacy-1.x" mean the same thing.
3. **Adopt the operator/function extension point.** Deployment experience with ODRL 2.2 evaluators
   (including the project owner's own) shows the working pattern is precisely profile-as-linkage:
   the profile binds operands *and operators* to plug-in functions loaded at runtime. RL2 should
   standardize this rather than forbid it, with the constraints that preserve its guarantees: a
   profile-declared operator has a declared typed signature `(ValueType, ValueType) → Bool`
   evaluated under the same three-valued discipline; the bound function must be pure, total on its
   declared types, and free of snapshot traversal beyond declared resolution paths; the binding is
   part of the module's digest, so same IRI+version+digest ⇒ same function. Plug-in loading is
   then a conforming *implementation technique*, and the profile's conformance vectors are what
   keep independently implemented plug-ins semantically aligned. This resolves the mapping's
   dangling "profile operator" disposition ([O] O5) in favour of specifying it — `odrl:hasPart`/
   `isPartOf` become expressible as profile operators over the finite membership indexes.
4. Exercise the mechanism: rewrite 4–6 data-governance use cases onto the privacy profile and add
   version-negotiation and digest-mismatch vectors [O].

**Caveat.** The extension point is where RL2's determinism claim is most exposed: an arbitrary
plug-in is an escape hatch from the semantics. The constraints above (typed signature, purity, no
I/O, digest-bound identity, mandatory per-profile vectors) are load-bearing, not hygiene — without
them, "conforming evaluator" degrades to "same policy, whatever functions happen to be installed."
The compile stage (P1) must verify signature compatibility exactly as it does for core operators,
and a profile operator over unbounded computation should be rejected at module admission, which is
one more reason bounds belong in the normative set (§2.1).

### P5 · ODRL 2.2 coverage position — DECIDED 2026-08-01: "ODRL ±"

**Origin:** [O] §6.1, [G] C3-4, [A] — all three flag the remedy/consequence gap; [G] frames the
release decision most sharply. **Decided with the project owner; record below is normative for
subsequent sweeps.**

**Strategic frame (owner-stated).** RL2's purpose is twofold: candidate spec work toward an
eventual ODRL 3, *and* a practical, verified engine deployable in real contract/permission
practice now — dataspaces, data services, market-data contracts, secured pods — covering what is
actually needed from ODRL 2.2, filling its holes, and unlikely to break outright when ODRL 3
arrives. Consequences for prioritization: the compile contract (P1), executable vectors (P3), and
the verified-evaluator path (§5 formalization note) are the assurance artifacts that make internal
adoption defensible; forward-compatibility means tracking the W3C Formal Semantics draft
(crosswalk + P11 Behaviour) and keeping core small rather than chasing vocabulary breadth.

**The decision rule — three tests.** A construct earns its place by passing all three; *which*
test it fails determines where it lands:

1. **Demand**: written into real contracts (IDSA/dataspace agreements, market-data licensing,
   data-service terms, pod/consent policies) — not merely proposed.
2. **Determinism**: exact, total, three-valued semantics as a pure function of
   (policy, request, snapshot). Fails even in principle → **eliminated** (the ODRL−).
3. **Runtime independence**: evaluating it needs nothing beyond `Eval`. Demanded and deterministic
   but operationally heavy → **shipped profile**, not core (the ODRL+).

**The three layers.**

*Core (sharpened ODRL−):* Set/Offer/Agreement; the three norm classes; conditions;
`rl2:includedIn` action subsumption — **retained deliberately**: real vocabularies are
hierarchical (the W3C AI vocab, market-data action families), the closure is finite and
precomputed, and a Prohibition on a broad action catching an unanticipated narrow one is a safety
property, with the discipline that inclusion stays a curated profile-declared DAG, never inferred
from `rdfs:subClassOf`; collections including the P2 population extensions (demand-confirmed:
subscriber classes, pod user groups); priority + conflict strategies; windows; Duty status.
*Eliminated:* `odrl:implies` (hidden permissions — the archetype of the fuzz being removed;
distinct from `includedIn`, which stays), `andSequence`, ordered/sequence constraints, `Ticket`,
general `rightOperandReference` (pre-resolve into attributed snapshot facts).

*Shipped profiles (ODRL+):*
1. **Remedies/Contracts — expression only (decided).** `remedy`/`consequence` map to a Duty whose
   applicability condition is `obligationStateOperand(targetNorm: D) = Violated`. Core and
   evaluator untouched — the remedy Duty surfaces as Pending→Active in the status map once
   violation is derivable. *Operating* remedies (issuing credits, terminating, feeding violation
   events forward) stays behind the enforcement boundary, where it already was. Honest cost to
   document in `RL2_ExternalData.md`: the snapshot assembler must supply the non-performance
   evidence for `Violated` to be derivable. A standardized violation-evidence vocabulary is
   **deferred** (owner decision) — revisit when interop between independent parties is live.
2. **Privacy/Consent** — exists; align with pod/Solid practice (Esteves et al. as reference).
3. **AI Vocabulary** — adopt the W3C draft actions.
4. **Commercial/Market-Data** — `Quantity(Decimal, Unit)` value type with unit-equality in
   `sameDomain` (this resolves the previously open `odrl:unit` question: demand-confirmed by
   market-data practice — fees per user, device counts, currency — but profile-scoped, not core);
   metering via P13 `request.parameters`.

*Migration transpiler:* `odrl:refinement` is **compiled down** (decided) — component-scoped
refinements canonicalize into rule-level conditions during ODRL→RL2 translation; the refinement
form does not exist in RL2 authoring. This makes the transpiler the home of ODRL's authoring
conveniences generally: accepted on input, normalized away, never round-tripped.

*Multi-party depth (decided):* per-norm subject + counterparty suffices for 0.7 (covers
exchange/vendor/subscriber patterns when each obligation names its pair); assignment chains,
beneficiary-distinct-from-counterparty, and delegation go to `future/` normative instruments.

**Publication claim** (scoped to the migration profile, per [G]):

> RL2 defines a deterministic, bounded core for request evaluation, Duty interpretation, and
> Offer materialization, plus a specified ODRL 2.2 migration profile. It does not replace every
> ODRL 2.2 processing mode.

**Remaining execution items** (unchanged from the reviews):
1. Specific reclassifications [G]: ODRL `invalid` voids the whole policy while RL2 returns a
   request-scoped `Indeterminate` — mark `clarified`, not exact, unless equivalence is proved for
   the supported fragment. A Set rule's discarded assigner: do not claim full preservation where
   issuer interpretation depends on it.
2. Publish the full term-by-term compatibility matrix with a fixture per row ([G] §6 has the
   skeleton), each row carrying its three-test verdict; plus migration fixtures for `xone`,
   `inheritFrom` (multiple parents, missing parent, cycle), `ConflictingCompactValue` — none
   currently exist [O].
3. Add the crosswalk to the W3C ODRL Formal Semantics draft and its report model — including the
   open/closed **Behaviour** parameter (→ P11) — and stop implying Request/State-of-World is novel
   to RL2; the draft has both [G].

### P6 · Fix the normative-text type errors (mechanical batch)

**Origin:** [O] F1–F5, F9 (all verified with line numbers); [G] §5.1–5.2, C2-4. Unique to these
two; no overlap conflicts. All can land immediately, independent of everything else.

1. `Promise` typing rule (`RL2_Semantics.md:221-224`) omits the `object` field declared in the
   grammar at `:81` and has no result type. [O F1]
2. `Invalid(OperandSite(path))` at `:619`: `OperandSite` is not an `ErrorSite` constructor
   (`:311-315`) and the value is not wrapped in the required `ErrorKey` record. Use
   `Invalid({site: Path(path), target: None})`. [O F2]
3. `mkStatusEnv` (`:679`) passes `None` into the non-optional `Env.Request` (`:278`). Make the
   field `Request?` and state that `request.*` resolves `Invalid` when absent. [O F3]
4. The claim that `Env` fields "correspond one-to-one with the canonical path roots" (`:281-283`)
   is false — `Snapshot` backs three roots, `Universe`/`Configuration` back none. Replace with an
   explicit root→field table. [O F4]
5. `promiseStatus` (`:792-793`) emits `StatusSite(PromiseTarget(p))` where `p` is the *promisor
   Agent*, not the Promise — ill-typed and pointing at the wrong node. Bind the Promise. [O F5]
6. Two incompatible error representations are normative simultaneously: `RL2_Model.md:177-189` and
   all four vector files use bare `Err(Missing(key))` while `RL2_Semantics.md:316-319` requires
   the `{site, target}` record. Standardize on the record. [O F9]
7. `Resource` is used in `Evidence.object`/`EvidenceSelector.object` (`RL2_Model.md:109,209`) but
   is not a defined type. Use `Asset` or define the relation. [G]
8. A status-dependency cycle is reported as `Invalid(ConfigurationSite("statusDependency"))`
   (`RL2_Semantics.md:814`) — it is a policy-compilation defect, not a configuration defect. Add a
   `PolicySite`/`CompileSite` (folds naturally into P1's stage-owned diagnostics). [G C2-4]
9. `RL2_Semantics.md:1279` justifies atom distinctness "because `n` is unique per policy" — SHACL
   permits one Norm as a clause of multiple Policies, and distinctness already follows from `P`
   being part of the atom key. Fix the justification (the conclusion stands). [G, nuanced]
10. `rl2.ttl` section numbering jumps 4 → 6 → 6a. [O F10][G §5.3]

### P7 · Repair the value-type algebra — DECIDED 2026-08-01

**Origin:** [O] F6/F7, unique but verified; corroborated by the corpus. **Decided with the
project owner:**

1. **Single exact `Numeric`** replaces Int/Decimal: exact decimal semantics, integer and decimal
   literals unify, `sameDomain` stays plain type equality. `xsd:float`/`xsd:double` are rejected
   in core — policy literals fail at compile (`UnsupportedDatatype` diagnostic); float-typed
   snapshot facts resolve `Invalid`.
2. **`xsd:duration` splits** into `xsd:dayTimeDuration` and `xsd:yearMonthDuration` — two
   disjoint, totally ordered value types. Pure literals are auto-classified at compile/transpile
   (`PT6H` → dayTime, `P1Y2M` → yearMonth); mixed literals (`P1Y3D`) are a compile error. Bare
   `xsd:duration` disappears from `ordered`.
3. **`Quantity(Numeric, Unit)`** lives in the Commercial/Market-Data profile, not core:
   comparison requires identical units (compile error when statically known, `Unknown`
   otherwise); **no conversion** in 0.7 — exact-scale conversion deferred, currency conversion
   excluded permanently (rates are world data, not units). Implemented when the profile lands
   (P4/P5), not before.

Note: `rl2:OperandRangeTypeShape`'s syntactic integer-vs-decimal warning becomes over-strict
under (1); it is superseded by the P1 typing pass and is not patched in the interim.

Original findings for the record:

1. **`ordered(Duration)` is unsound** (`RL2_Semantics.md:422`): `xsd:duration` is only partially
   ordered (`P1M` vs `P30D` is indeterminate in XSD), so `lt/lte/gt/gte` over it is not total —
   breaking Proof Obligations 1 and 2. Live in the corpus:
   `conformance/usecases/data-freshness-promise.md` compares `xsd:duration` values. Restrict to
   `xsd:dayTimeDuration` and `xsd:yearMonthDuration` as two separate value types that do not
   `sameDomain` with each other.
2. **No numeric tower**: `sameDomain(l,r) = valueType(l) = valueType(r)` (`:421`) makes
   `"1"^^xsd:integer` vs `"0.999"^^xsd:decimal` a type mismatch → `Unknown`. (The Primer's SLA
   example is type-consistent — verified during the mechanical sweep — so the exposure is
   integer-typed *snapshot facts* supplied by assemblers, and ODRL imports carrying integer
   literals against decimal-ranged operands.) Collapse Int/Decimal into one exact `Numeric` type
   (what Cedar and Rego effectively do) or define explicit promotion in `typeCompatible`; then
   make `RL2_ODRL_Mapping.md §7`'s "exact after datatype normalization" true.

Both decisions feed the P1 typing pass; land the decisions before freezing the module format.

### P8 · Complete the windowed-Maintenance boundary algorithm — DECIDED 2026-08-01: option (b)

**Decision:** 0.7 Maintenance invariants admit fact and clock operands only; a status operand
inside an invariant is a compile rejection. Status operands in *applicability conditions* remain
allowed (that is what `sla-credit-clause` uses; verified no corpus invariant contains one). The
recursive boundary-collection algorithm (§3.3) is the documented lift if a need appears.

**Origin:** [G] C3-5. This *corrects* [O], whose claim that `elapsed` was "not pinned down" was
overstated — the spec does define a finite cell partition (`RL2_Semantics.md:737-743`, verified).
The real defect is that the partition's boundary list is **incomplete**.

**Problem.** The stated boundaries are fact-validity intervals, the Duty window, and literal time
comparisons. If a Maintenance invariant contains `obligationStateOperand` or
`promiseStateOperand`, truth also changes at: evidence occurrence times feeding the referenced
status; the referenced Duty's/Promise's own window boundaries; and boundaries of *recursively*
referenced statuses. An implementation using only the listed boundaries evaluates representatives
of cells that are not truth-invariant → wrong, and differently wrong per implementation → the
determinism obligation fails precisely where it matters.

**Recommendation.** Either (a) define a recursive boundary-collection function over the compiled
condition/status-dependency DAG (acyclicity is already guaranteed by the cycle check) and prove
one-representative-per-open-cell sufficiency, or (b) — the bounded 0.7 option — restrict
Maintenance invariants to fact and clock operands, deferring status operands inside Maintenance
content. [G] offers both; take (b) for 0.7 and (a) as the lift, unless a use case already needs
(a). Add vectors for nested status references at exact start/evidence/end instants either way.
Algorithm sketch in §3.3.

### P9 · Narrow the canonical-form claim; canonicalize the enumerated duplicates

**Origin:** [G] C2-1 (the sharper analysis) merged with [O] R3/§9.3 (the concrete exception
patterns and their `Unknown` divergence).

**Problem.** The project invariant "exactly one valid RDF shape per normative proposition" is
false today and unachievable in general: policy/clause condition placement, `prerequisiteDuty` vs
status-condition gating, `neq` vs `not(eq)`, `isNoneOf` vs `not(isAnyOf)`, and arbitrary Boolean
identities all yield equivalent policies — and full logical normalization is exponential (Salas et
al. make the cost explicit, ref §7). Worse, the *exception* encodings are not even equivalent:
"everywhere except X" as `not(loc eq X)` vs Privilege+Prohibition behaves differently when the
operand is `Unknown` (one `indeterminate` atom vs `permit`+`indeterminate`, strategy-dependent),
and nothing documents this or covers it with a vector.

**Recommendation.**
1. Replace the invariant [G]: *every primitive relation has one admitted structural encoding;
   canonical projection removes RDF-level, lexical, ordering, and enumerated local syntactic
   alternatives; RL2 does not normalize arbitrary semantically equivalent Boolean policies.*
2. Enumerate the local normalization rules: `prerequisiteDuty` is the sole canonical form for
   ordinary pre-duty gating (status operands reserved for genuinely cross-norm conditions);
   atomic complements (`neq`, `isNoneOf`) canonical over `not` around their positive
   counterparts; policy-level conditions retained as factoring, acknowledged as not semantic
   uniqueness. [G]
3. Add a normative "Exception patterns" subsection with the four worked forms (single-clause
   `not`-condition; Privilege+Prohibition pair; priority-based break-glass; `defaultDecision`-based
   once P11 lands), their three-valued truth tables, the two distinct *meanings* ("no permit
   there" → `NotApplicable` vs "explicit prohibition there" → `Deny`) [G §8.3], and a vector each
   for the missing-operand case — including `permit + indeterminate` resolution under each
   strategy, which no vector currently exercises. [O]

### P10 · Regularize Duty gating — DECIDED 2026-08-01 (all three items)

**Origin:** [O] G5/G6 + R2; interacts with P9's canonicalization choice.

1. **Allow a Duty to be both a policy clause and a prerequisite.** `rl2:PrerequisiteDutyShape`
   (`spec/rl2-shacl.ttl:124-128`) forbids the combination outright, yet the natural governance
   pattern — a standing obligation that also gates access — is exactly that, and the semantics
   already handles it with no changes (the Duty emits its `obligate` atom and independently gates
   via `prerequisiteResult`; single derived status reported once). Delete the
   inverse-`rl2:clause` `sh:maxCount 0` constraint and state the combined reading.
2. **Policy-level `rl2:prerequisiteDuty`**, folded into `effectiveCondition` like the policy-level
   condition, so "every Privilege in this Agreement is gated by the attestation Duty" needs one
   assertion, not one per Privilege.
3. **Document the divergence** between `prerequisiteResult` and the status-condition encoding on an
   *inapplicable* Duty (vacuous pass vs `False`) and add the vector — `duty-attachment.md` D5 does
   not cover it. This divergence is why P9 rule 2 must name `prerequisiteDuty` canonical.

### P11 · Add `defaultDecision` to EvaluationConfiguration — DECIDED 2026-08-01

**Origin:** [O] G4; [G] independently requires the Behaviour crosswalk; [A]'s "default behavior in
policy engines is deny" answer implicitly assumes it exists.

The ODRL Formal Semantics draft takes an open/closed **Behaviour** parameter; XACML has it as
`deny-unless-permit`/`permit-unless-deny` combining algorithms. RL2 pushes the choice onto the PEP,
which is defensible but leaves "never except in this case" needing an explicit broad Prohibition
and makes the FS correspondence inexact. Add
`defaultDecision : Permit | Deny | NotApplicable` (default `NotApplicable`), applied only when the
envelope contains no atom. Three lines of semantics; record the FS and XACML correspondences in the
mapping. With it, RL2's three strategies + priority + defaultDecision cover all XACML combining
algorithms except the order-dependent ones RL2 correctly rejects [O].

### P12 · Relative Duty deadlines — DECIDED 2026-08-01 (incl. recurrence stance)

**Origin:** [O] G3; independently identified as an ODRL gap by Cimmino & Fornara (P4b) and by the
Fornara et al. deadline work already in RL2's bibliography.

"Delete within two weeks of receipt" — the canonical obligation in the literature — is
inexpressible: `rl2:DutyWindow` takes absolute instants only. The corpus works around it by
precomputing expiry into snapshot facts (`deletion-after-use.md`, `data-retention-limit.md`),
which moves policy meaning into the snapshot assembler and defeats replay-based audit. Add
`WindowEndpoint ::= Absolute(DateTime) | Relative(LeftOperand, Duration)`, resolved once via
`resolveFact`; `Missing` → window unresolved → `IndeterminateStatus`, an already-defined outcome.
Closed, small, and it removes the largest single migration objection after consequences (P5.2).

**Adjacent gap — recurrence.** A recurring commitment — "the data will be ready at 8am every
Monday" — has no home either: `rl2:DutyWindow` is one half-open interval, so the materialized
Duty from such a Promise can express only a single occurrence. Full recurrence (RRULE-style) in
core would drag in calendar semantics and threaten the boundary-finiteness argument (P8/§3.3);
for 0.7, state the limitation and the deployment pattern (the snapshot assembler instantiates the
current period's window, or a profile-defined operand carries the schedule), and treat a bounded
recurrence form — a fixed period and count, expanding at compile time to finitely many windows —
as the candidate extension. Expansion at compile keeps `Eval` untouched and the cell-partition
proof intact.

### P13 · Request parameters — DECIDED 2026-08-01

**Origin:** [O] O4; corroborated by [G] §5.6 (multi-level-approval binds approval to "project P"
that the Request cannot carry) and by both metering use cases whose prose invents Request fields
that don't exist.

`request.*` exposes only agent/action/asset. Real requests carry parameters — count, columns,
format, purpose — currently laundered through `context.*` facts, splitting one logical input
across two inputs with different lifecycles. Add `request.parameters.<name>`: a typed map on the
Request, resolved through the same `resolveFact` discipline, `Attribution = Request`. Purity is
unaffected. Makes `purpose`/`count`/`format` — among ODRL's most-used operands — expressible
without snapshot contortions, and fixes both metering use cases properly.

### P14 · Snapshot semantics decisions — DECIDED 2026-08-01

**Origin:** [G] C2-3 (unique) + [O] E4 + [G] 10.3 (convergent).

1. **Poisoning rule — DECIDED: strict + trusted assembler.** `resolveFact` keeps its fail-closed
   rule (`Invalid` if any candidate for a key is inadmissible). The threat model is stated
   normatively: the WorldSnapshot is the output of a trusted assembler; mixed-trust filtering is
   the assembler's job, before the snapshot exists. This matches the intended deployment shape
   (the assembler is the integration layer).
2. **Dependency manifest + fetch loop** ([O] E4 and [G] 10.3 are two halves of one feature):
   compile-time, the module exports `RequiredInputs` (fact keys with type/cardinality/trust,
   evidence selectors, time requirements) so the assembler can prefetch; runtime, a structured
   `Missing` cause set *is a fetch plan* — evaluate, fetch exactly the missing keys, re-evaluate.
   Specify both; `RL2_ExternalData.md §6` currently gestures at the loop without defining it. This
   is a genuinely distinctive capability of the attributed-error design — neither Rego's
   `http.send` nor XACML PIP callbacks can offer it.
3. **Freshness**: `validDuring` handles expiry, but "fact must be no older than 5 min" is
   inexpressible; expose assertion time as a resolvable path or profile operand. [O]

### P15 · Materialization identity and Promise/Duty structure

**Origin:** [G] C2-2 (identity — unique) + [O] O2 + [A] (unification — convergent, different
strengths).

1. **Source identity** [G]: `SourceRef` claims stable canonical identity including blank nodes, but
   its construction is undefined — parser-local blank-node labels are not stable across
   ingestions. Derive identities from the compiled module's canonical node table (P1), or require
   named clause IRIs; use RDFC-1.0 only if identity must survive independent RDF-level ingestion
   (with resource limits, §3.5). Enumerate `copyMetadata` explicitly. Include profile digests in
   the materialization result.
2. **Share structure between Promise and Duty; keep the class disjointness — DECIDED
   2026-08-01 (adopt as specified below).** All three reviews
   see the duplication (parallel status lattice, parallel state operand, the documented
   `promiseStateOperand`→`obligationStateOperand` rewrite in `sla-credit-clause.md`). [A] proposes
   eliminating `Promise` entirely (a Duty inside an Offer is non-operative); **rejected on
   semantic grounds, per the project owner's clarification**: Duty and Promise are different
   speech acts binding different parties. A Duty in a Set is a *directive in force* — "every
   employee must …" — binding its subjects unconditionally, with no acceptance involved. A
   Promise in an Offer is a *commissive contingent on acceptance* — "the data will be ready at
   8am every Monday" — binding the **offeror**, and only once accepted. An Offer legitimately
   contains both: proposed Duties that will bind the *acceptor*, and Promises that commit the
   *offeror*; duty-in-offer-non-operative erases exactly the "what you must do" vs "what I commit
   to" distinction. The disjointness is therefore load-bearing twice over — deontically (above)
   and structurally (`derive`'s type filter, Offers non-operative by construction). The absent
   `Active` state in the Promise lattice is a consequence of the speech act, not a coincidence: a
   Promise is never in force. Adopt [O]'s version, which preserves all of this while removing the
   duplication: `Promise = { proposed : Duty }` — `rl2:Promise` stays outside `rl2:Norm`, the
   nested node reuses `rl2:action`/`rl2:invariant`, the promisor/promisee ↔ subject/counterparty
   correspondence becomes the single documented binding-direction flip at materialization,
   `PromiseState` collapses into `ObligationState` minus `Active`, one state operand survives.
   Removes roughly a third of the Promise-specific text with no semantic loss — the distinction
   lives in the class and the binding direction, not in the record layout.

---

## 2. Structural, corpus, and editorial repairs

### 2.1 Structure ([O] unless noted)

- **Unify the Duty constructor — DECIDED 2026-08-01**:
  `DutyBody ::= Achieve(Action, Condition?) | Maintain(Condition)` — one constructor, two-case
  matches, and "form is structural" becomes a projection fact instead of a running proof
  obligation. Formal grammar only; the RDF surface (`rl2:action` xor `rl2:invariant`) is
  unchanged, so no policy is affected. Land before freezing the P1 module format, which encodes
  it.
- **One action property**: `rl2:prohibitedAction` duplicates `rl2:action` (modality is already
  carried by the class; `actionMatches` treats them identically), held apart only by a SHACL
  message. Unify on `rl2:action`, or document why import fidelity requires the split.
- **Bounds normative and complete** (+[G] C2-5): the complexity section is non-normative yet
  requires bound enforcement. Move bounds into a normative section; split into authoring bounds
  (rejected at compile) vs input bounds (rejected at snapshot admission) with stated failure
  modes; add the missing ones — clauses per policy, condition nodes, hierarchy edges/depth,
  status-dependency edges, module bytes (`MaxPolicyUniverse` does not bound `m` in the stated
  formula). Also [G]: label the selected-set monotonicity result narrowly — it holds because
  `deriveNorms` ignores the selected subset, and is not a policy-composition theorem.
- **Deduplicate the scope lists**: `RL2_Scope.md` owns out-of-scope normatively;
  `RL2_Architecture.md §7` and `future/README.md` link to it. Same for the related-work list
  duplicated between `RL2_ODRL_Mapping.md §12` and the bibliography.
- **State the Hohfeld/UFO-L boundary** [G C2-7]: cite the UFO-L grounding work (ref §7) and answer
  it — counterparty recovers the useful correlative; powers/immunities/strong permission are
  deliberately out of core; the future normative-instrument transformation is the recovery path;
  core must not imply a Prohibition makes the prohibited act normatively ineffective. A scoped
  limitation, not restored vocabulary.

### 2.2 Corpus (merged [O] U1–U10 + [G] §5, deduplicated)

| File | Defect | Fix |
|---|---|---|
| `ethics-approval.md` | Expects `Permit` for Alice under `rl2:subject ex:Researcher` — contradicts `subjectMatches` | Blocked on P2; interim: make the requester `ex:Researcher` or mark as depending on the extension |
| `owner-access.md`, `role-hierarchy.md` | Hardcoded subject + condition doing the real work; role-titled case pins one agent | P2; `role-hierarchy.md` additionally puts agent instance data in the policy graph — move `ex:AliceRole` to an `agent.role` snapshot fact; `isA` closes over the class hierarchy only |
| `pass-through-terms.md` | Action-bearing Achievement Duty called "the maintenance duty" [O][G] | True `rl2:invariant` Maintenance, or fix the prose |
| `audit-trail.md` | Prose says "prerequisite Duty", Turtle uses independent Duty + status condition — different decision semantics; evidence selector also can't link the record to "this order" [G] | Normalize per P9/P10; give each order a distinct record Asset or a linking profile fact |
| `usage-metering.md`, `volume-limit.md` | Prose invents Request fields (`requestedQueries`, `requestedRecords`) | P13, then use `request.parameters.*` |
| `multi-level-approval.md` [G] | "Approval bound to project P" but policy reads one global boolean; Request has no project field | Context-scoped fact keyed to P, or model P as the Asset; P13 helps |
| `data-freshness-promise.md` | `xsd:duration` ordering (P7); also supplies an unrelated `inspect` request without stating its decision [G] | `xsd:dayTimeDuration`; state `NotApplicable` or drop the request |
| `policy-versioning.md` [G] | Tests universe selection, not version negotiation | Rename |
| `quality-circuit-breaker.md`, `schema-evolution.md`, `step-up-auth.md` [G] | "Duty is active" conflates status map with `obligate` atoms the Duty doesn't emit for this request | Wording |
| `concurrent-seats.md`, `quality-circuit-breaker.md`, `trial-period.md`, `chinese-wall.md` [O] | Complementary Privilege/Prohibition condition pairs both go `Unknown` when the operand is missing — two indeterminate atoms, strategy-dependent outcome, no vector | Vector per P9.3 |
| `check-signing.md`, `pay-to-play.md`, `team-license.md`, `wire-transfer-sod.md`, `data-stewardship.md` [G] | Status conditions used for ordinary prerequisite gating | Normalize to `prerequisiteDuty` per P9 |
| `vectors/*` | Bare-key error form (P6.6); prose-only (P3) | Rewrite |
| `migration/` | No fixtures for `xone`, `inheritFrom`, `ConflictingCompactValue`, `InheritanceCycle` | Add (P5.4) |

Missing use cases/vectors worth adding ([G] §7, condensed): data product with three ports and one
port-scoped extra Duty; tag-selected Sets + Offer assembly; default/exception patterns with all
three outcomes; cross-policy conflicts at different priorities; every compile error; profile
mismatch/digest mismatch; strict-vs-filtered inadmissible duplicates; blank-node identity in
materialization; nested temporal status dependencies; Achievement/Maintenance boundary instants.

### 2.3 Editorial ([G] §5 + [O], residue)

`--shapes-only` doesn't do what its name implies (no meta-validation) — rename or implement;
replace "total semantics" with "total on compiled, bounded inputs"; regenerate
`docs/RL2_Vocabulary.md` after ontology changes; fix Primer §4's false claim that role membership
"is expressed as typed profile conditions" (P2); fix Primer §6.2's decimal SLA example (P7); align
`no-ml-training.md`/`derived-data-restriction.md` action names with the W3C ODRL AI Vocabulary
draft and consider it as the second RL2 profile [O].

---

## 3. Complications that need real algorithms

Explicitly requested; these are the places where "add a feature" hides a hard sub-problem.

### 3.1 Policy equivalence and containment

Wanted for negotiation (is an Acceptance within an Offer?), regression ("did this edit deny
anything previously permitted?"), and dedup. Two viable routes, different costs:

- **Normalization** (Salas et al. 2026, ref §7): rewrite to a normal form, compare syntactically.
  Complete for the fragment it covers but **worst-case exponential** in condition size — their
  result, and the reason P9 abandons global canonicality. Usable as a fast path for small
  conditions only.
- **Symbolic checking**: RL2's condition language is finite, typed, quantifier-free — decidable by
  SMT. The subtlety is three-valued logic: encode each condition as a *pair* of classical
  predicates (`isTrue`, `isFalse`; unknown = neither), because `p ⊑ p'` must be checked per truth
  value — a policy pair can agree on True/False and diverge on Unknown, which is observable
  through `Indeterminate`. Containment of a whole policy additionally quantifies over the
  snapshot: model each resolvable path as an uninterpreted typed variable plus a per-path
  three-state tag (present/missing/conflicted). Duty *status* operands make containment recursive
  through the status DAG — bounded because the DAG is acyclic (P1's cycle check), but each status
  reference expands into its window/evidence conditions. Cedar's symbolic compiler is the working
  precedent. All of this is authoring-time tooling; none of it enters `Eval`, so the no-solver
  constraint holds.

### 3.2 Static conflict detection

"Find requests where a Privilege and a Prohibition both fire" is the SMT query
`∃ request, snapshot : isTrue(cond_i) ∧ isTrue(cond_j) ∧ matches_i ∧ matches_j` per
(Privilege, Prohibition) pair — O(n²) pairs, pruned hard by the matching indexes (only pairs with
intersecting subject/action/object cones can conflict; with P2's unbound norms the cone
intersection test weakens, which is another cost of unbound norms to name). Under three-valued
semantics there are *three* conflict classes to report: definite (both True), potential (one or
both Unknown-reachable), and masked (resolved by priority/strategy — report as informational,
since a strategy change unmasks them). The NXDG 2025 paper (ref §7) argues explanation and repair,
not just detection, is the differentiator; RL2's attributed atoms make the explanation part nearly
free. Temporal conflicts (windows that overlap only sometimes) add interval reasoning — the
sort-stratified work (ref §7) is the pointer.

### 3.3 Maintenance boundary collection (P8 option (a))

```text
boundaries(cond, W, U) =
    ⋃ over atoms a in cond:
        fact-validity endpoints of every key a can resolve      (existing)
      ∪ literal time comparison points in a                     (existing)
      ∪ if a is a status operand on target t:
            window endpoints of t
          ∪ occurrence times of evidence selectable for t
          ∪ boundaries(applicability(t), W, U)
          ∪ if t is Maintenance: boundaries(invariant(t), W, U)   -- recursion, DAG-bounded
```

Obligation to prove: within any open cell of the induced partition, every atom's value — including
derived statuses — is constant, so one representative suffices; singleton cells at each boundary
where inclusivity can flip truth. Termination from status-DAG acyclicity; size bounded by
`MaxSnapshotEvidence × dependency-depth`, which is why the bound belongs in the normative set
(§2.1). If this proof resists, take P8 option (b) for 0.7.

### 3.4 Unbound-norm evaluation cost (P2)

Equality matching admits hash-lookup candidate selection; unbound norms are scanned always. Keep
bound norms on the fast path, put unbound norms in a dedicated bucket, and note that a universe
dominated by unbound norms degrades to O(|U|) per request — acceptable, but say it, and let the
assembly contract (P2.2) keep governance universes small.

### 3.5 RDFC-1.0 poisoning

If source-RDF digests are adopted (P15.1), RDF Dataset Canonicalization must run with resource
limits: adversarial blank-node graphs have super-polynomial canonicalization cost. The compiled
module's node table avoids the issue entirely, which is one more reason to prefer it as the
identity root.

### 3.6 Profile compatibility under SemVer 0.x

Same-major matching is vacuous while every profile is 0.y.z (P4). Exact-minor or declared ranges;
revisit when profiles reach 1.0.

---

## 4. The modeling questions, consolidated

**4.1 Data contract with per-port promises/duties.** Expressible now: product as AssetCollection,
ports as direct members; product-level norms match port requests via membership; port-level norms
add via `Out`'s union; per-port Promises bind through `objectBindings` at acceptance. Two gaps:
no product→port inheritance beyond one membership level (conservative and fine — [G]); and a
port-level prerequisite cannot gate a product-level Privilege without duplication until P10 lands.
With P10 (both halves), a data contract is one Agreement: product Privileges, a policy-level
attestation prerequisite, port-scoped Privileges with their own extra prerequisites. Add the
one-product/three-ports use case.

**4.2 Three tag-matched Sets activating with an Offer.** Three answers, one per layer:
(i) evaluation-time composition of caller-selected Sets already works — `Out` unions, priorities
resolve, atoms stay attributed; (ii) an Offer does not and *should not* absorb Set duties at
materialization — an Agreement must be self-contained, and Set duties still apply at evaluation
via (i); state this explicitly in the Primer and mapping, and add optional `rl2:acceptedUnder`
(policy IRIs + digests) on the Acceptance for auditability [O]; (iii) tag-driven *selection* is the
genuine gap — blocked on P2 (unbound objects for "applies to anything classified X") plus the
assembly contract (deterministic, digest-pinned universe construction). If the attestation must
*gate* use rather than merely oblige, the assembled/authored form must use `prerequisiteDuty` —
an independent Duty in the universe never changes an access decision [G][O], which is exactly the
trap the current corpus falls into (§2.2).

**4.3 "Everywhere except X" / "never except C".** Keep two meanings distinct [G]: *no permit
there* (single Privilege, `location neq X`; excluded place → `NotApplicable`; closed PEP denies)
vs *explicit prohibition there* (Privilege + scoped Prohibition; → `Deny`; survives an open PEP).
Canonical operator: `neq`, not `not(eq)` (P9). "Never except C": narrow Privilege + closed
enforcement where absence suffices; broad Prohibition + higher-priority conditional Privilege
(break-glass, matching the existing use case) where an explicit denial must appear in the result —
with P11, the first form becomes `defaultDecision: Deny` + one conditional Privilege. In all
forms: a missing exception fact must yield `Indeterminate`, never a silent grant; the truth tables
and vectors are P9.3.

---

## 5. Input claims rejected or corrected

Recorded so the next sweep doesn't relitigate them.

1. **[A] "Missing priority on Promises is a modeling error" — rejected.** Verified:
   `rl2:priority`'s domain is `owl:unionOf (rl2:Privilege rl2:Prohibition)`
   (`spec/rl2.ttl:52-54`), not `rl2:Norm` as claimed. Duties never carry priority — priority
   exists only for permit/forbid resolution — so a Promise crystallizing into a Duty has nothing
   to inherit. A proposed Privilege in an Offer can carry priority and it copies through. No
   defect.
2. **[A] "Merge Set/Offer/Agreement into one Policy class with a status property" — rejected.**
   Operativity in RL2 is structural (Promise ∉ Norm), which is what keeps `Eval` pure and
   materialization a function. A mutable `status` property reintroduces exactly the recorded-state
   design RL2 deliberately diverges from (Cimmino & Fornara Proposal 3) and the divergence is
   right. P15.2 captures the legitimate kernel (structure sharing) without this cost.
3. **[A] "Unify AtomicConstraint and LogicalConstraint" — rejected.** The split is what lets SHACL
   and the P1 typing pass check arity and operand types structurally; a single class with
   operator-dependent cardinality moves those checks from structure into validation logic. Low
   value, real cost.
4. **[O] "`elapsed` is not pinned down" — corrected.** The spec defines the finite cell partition
   (`RL2_Semantics.md:737-743`). The actual defect is the incomplete boundary list → P8.
5. **[G] "no additional structural failure was found" in the use cases — corrected.**
   `ethics-approval.md` expects a result the normative matching rule cannot produce (verified;
   P2/§2.2).
6. **[A] §Extra-questions answers — superseded.** The "everywhere except" answer omits the
   `Unknown`-divergence between encodings, and "activating Sets with an Offer" via "a Set
   condition verifying presence of a materialized Agreement" inverts the actual dependency; §4
   replaces both.
7. **Effort estimates reconciled.** [O] ≈ 4–5 person-months for evaluator+importer; [G] ≈ 6–10
   including schemas, differential oracle, and hardening, with mechanized proofs +6–12. [G]'s
   breakdown is the more complete accounting; adopt 6–10 pm for a credible reference
   implementation with executable conformance, proofs extra. Both agree a production PDP with real
   enforcement integrations is a separate follow-on of comparable size.

On formalization, the reviews agree in substance: no normative proof assistant ([G], and
`RL2_Scope.md` already says so); Lean 4 is the strongest fit for the mechanized model, with
Cedar's Dafny→Lean migration and Lean-as-differential-oracle as the working precedent [O][G];
Dafny remains the shortest path *if* SMT-automated verification with generated Go is prioritized
over an induction-heavy metatheory [G] — but the metatheory here (structural induction over the
AST, totality, determinism) is exactly where Dafny's automation stops helping, which is why Cedar
left. Order of proof value: P1's compile-soundness theorem first (small, and it is the theorem the
design story rests on), evaluator determinism/totality second, verified RDF compiler last (largest
trusted boundary). Go for production, differentially tested against the Lean model; Rust only if
embedding (Wasm/data-plane) becomes a requirement; WhyML/OCaml/Scala add nothing here beyond a
pleasant reference interpreter.

---

## 6. Work order

1. **P6 + §2.3** — mechanical corrections; ~~land now~~ **done, committed 0ca83bd**.
2. **P5.1** — ~~decide the ODRL publication position~~ **decided: "ODRL ±" three-layer structure
   with the three-test rule; see P5.** Execution (matrix, fixtures, crosswalk) remains.
3. **P7, P15.2, §2.1 Duty constructor** — value-type and structure decisions that the module
   format will freeze.
4. **P1 + P4** — compile contract and ProfileModule (the core work; P4 is a P1 stage).
5. **P2** — population/targeting extension + assembly contract (parallel to 4).
6. **P3** — vector format immediately after the module format stabilizes; runner with the
   reference evaluator.
7. **P8–P14** — semantic decisions, each small once 4–5 exist; vectors alongside (§2.2).
8. **Reference evaluator + differential oracle**, then benchmarks (policy count, condition
   depth, hierarchy size, snapshot facts, evidence, conflicting atoms; compare OVAL/OPA/Cedar on
   the shared subset [G]).
9. **Mechanized proofs** — only after the module and vectors freeze.

---

## 7. References (merged from all three reviews, deduplicated)

★ = not yet in `docs/RL2_References.md`, incorporate. ★★ = highest-value for the next sweep.

### W3C and ODRL primary sources

1. [ODRL Information Model 2.2](https://www.w3.org/TR/odrl-model/), W3C Recommendation, 2018 —
   including its profile mechanism and processor-conformance clauses, which P4 adopts in spirit.
2. [ODRL Vocabulary & Expression 2.2](https://www.w3.org/TR/odrl-vocab/), W3C Recommendation, 2018.
3. Fornara, Rodríguez-Doncel, Esteves, Steyskal, Smith.
   [ODRL Formal Semantics](https://w3c.github.io/odrl/formal-semantics/), W3C ODRL CG Editor's
   Draft — cited but unused; source of the Behaviour parameter (P11), the state taxonomy, and the
   report model (P5.5). Its conflict-resolution section is unwritten; RL2's resolver is a
   candidate contribution back.
4. [ODRL V2.2 Profile Best Practices](https://www.w3.org/community/reports/odrl/CG-FINAL-profile-bp-20240808.html),
   CG Final Report, 2024 — profile identity vs namespaces, term collections, publication practice;
   with ref 1's profile clauses, the model P4 adopts in spirit.
5. ★ W3C ODRL CG. [ODRL Profile: AI Vocabulary](https://w3c.github.io/odrl/ai-vocab/), first
   draft 2026-05-27 — align AI-related use cases; obvious second RL2 profile.
   ([announcement](https://lists.w3.org/Archives/Public/public-odrl/2026May/0008.html))
6. Rodríguez-Doncel, Roman.
   [Towards Conformance in ODRL 3.0](https://ceur-ws.org/Vol-3977/OPAL2025-8.pdf), OPAL 2025 —
   requirement/use-case/test traceability; grounds P3.
7. ★ Slabbinck et al.
   [Interoperable Interpretation and Evaluation of ODRL Policies](https://raw.githubusercontent.com/woutslabbinck/papers/main/2025/Interoperable-Interpretation-and-Evaluation-of-ODRL-Policies.pdf)
   — Compliance Report Model and executable test-suite precedent.
8. [ODRL CG implementation list](https://www.w3.org/community/odrl/implementations).

### ODRL critique, semantics, and extension proposals

9. ★★ Cimmino, Fornara.
   [Improving ODRL 2.2: current limitations and theoretical solutions](https://ceur-ws.org/Vol-3977/OPAL2025-6.pdf),
   OPAL 2025 — six ODRL 3.0 proposals; both authors are FS editors, making this the de-facto ODRL 3
   requirements statement. RL2 disposition per proposal: P1 covered (better, via typed operands);
   P2/P3/P5 deliberately divergent (state the rationale in Scope); P4 partially covered — the
   deadline (P12 here), unknown-assignee (P2 here), event-activation, and
   regimentation-vs-sanction gaps remain (consider an eval-ignored `rl2:enforcementMode`); P6
   (templates/variables) is the deep gap behind P2.
10. ★ Bonatti, Fornara, Harth.
    [Towards a Formal Semantics of ODRL 2.2](https://ceur-ws.org/Vol-3977/OPAL2025-4.pdf),
    OPAL 2025 — competing model-theoretic formalization; state the contrast (RL2: total,
    three-valued, explicit snapshot).
11. ★ Salas, Pareti, Yumuşak, Gheisari, Ibáñez, Konstantinidis.
    [Evaluation and Comparison Semantics for ODRL](https://arxiv.org/abs/2509.05139), 2025 —
    policy comparison via query containment; the containment relation RL2 lacks (§3.1).
12. ★ Salas, Pareti, Konstantinidis.
    [ODRL Policy Comparison Through Normalisation](https://arxiv.org/abs/2603.12926), 2026 —
    exponential normalization cost; grounds P9's narrowed canonicality claim.
13. ★★ Salas et al.
    [A Formally Grounded ODRL Evaluator: Implementation and Comparison (OVAL)](https://arxiv.org/abs/2607.15987),
    2026 — implemented evaluator with benchmarks; the most important comparison target for the
    next sweep.
14. ★ Cimmino, Cano-Benito, García-Castro. "Open Digital Rights Enforcement framework (ODRE)."
    *Computers & Security* 150 (2025) 104282.
    [doi:10.1016/j.cose.2024.104282](https://doi.org/10.1016/j.cose.2024.104282)
    ([arXiv](https://arxiv.org/abs/2409.17602)) — descriptive→enforceable; contrast with the pure
    boundary.
15. ★ Mustafa et al.
    [What Does ODRL Mean? A Cross-Level Ontological Grounding](https://arxiv.org/abs/2606.24344)
    — UFO-L/Hohfeld grounding; grounds §2.1's scoped-limitation statement.
16. ★ Kebede, Sileno, van Engers. "A Critical Reflection on ODRL." *AICOL XI–XII*, Springer 2021.
17. ★ De Vos, Kirrane, Padget, Satoh. "ODRL policy modelling and compliance checking."
    *RuleML+RR 2019* — the solver-based approach RL2 rejects; cite when stating why.
18. ★ Cimmino, Cano-Benito, García-Castro.
    [Practical challenges of ODRL and potential courses of action](https://doi.org/10.1145/3543873.3587628),
    WWW '23 Companion.
19. ★ Roshankish, Fornara. "How to Formalize Different Types of Norms in Multi-agent Systems."
    *SN Computer Science* 5 (2024) 749 — norm taxonomy behind ref 9's Proposal 4; relevant to P12.
20. ★ Esteves, Pandit, Rodríguez-Doncel. "ODRL Profile for Expressing Consent through Granular
    Access Control Policies in Solid." *IEEE EuroS&PW 2021* — best real ODRL privacy profile;
    benchmark for P4/O6.
21. ★ [Semantic Conflict Resolution for Access and Usage Control](https://ceur-ws.org/Vol-4064/NXDG25-paper4.pdf),
    NXDG 2025 — conflict explanation/repair; grounds §3.2.
22. ★ [Sort-Stratified Semantics for Temporal Conflict Detection in ODRL Policies](https://arxiv.org/pdf/2606.23442)
    — temporal conflict detection; grounds §3.2's interval reasoning note.
23. Pucella, Weissman. [A Formal Foundation for ODRL](https://arxiv.org/abs/cs/0601085) — cited.
24. Steyskal, Polleres. "Towards a Formal Semantics for ODRL Policies." *RuleML 2015* — cited.
25. Fornara, Colombetti — obligations semantics; Fornara, Roshankish, Colombetti
    ([arXiv:2105.00200](https://arxiv.org/abs/2105.00200)) — time-constrained norm monitoring;
    both cited; the latter is the direct source for P12's deadline model.

### Policy engines and data governance

26. [OPA/Rego policy language](https://www.openpolicyagent.org/docs/policy-language) — cited; also
    ★ [external data](https://www.openpolicyagent.org/docs/external-data),
    ★ [IR](https://www.openpolicyagent.org/docs/ir) /
    [Wasm](https://www.openpolicyagent.org/docs/wasm) (typed-plan-then-backend precedent for P1),
    ★ [performance guidance](https://www.openpolicyagent.org/docs/policy-performance).
27. Cutler et al. [Cedar (OOPSLA 2024)](https://doi.org/10.1145/3649835) — cited; plus
    ★ [authorization semantics](https://docs.cedarpolicy.com/auth/authorization.html),
    ★ [validation](https://docs.cedarpolicy.com/policies/validation.html) (validation-soundness —
    the direct precedent for P1's theorem),
    ★ [schema](https://docs.cedarpolicy.com/schema/schema.html) and
    [level validation](https://docs.cedarpolicy.com/policies/level-validation.html) (bounded entity
    slicing ≈ RequiredInputs, P14.2),
    ★ [AVP concepts](https://docs.aws.amazon.com/verifiedpermissions/latest/userguide/terminology.html).
28. ★★ [How We Built Cedar: A Verification-Guided Approach](https://arxiv.org/abs/2407.01688),
    2024 — the Dafny→Lean 4 migration and differential-random-testing method; the direct answer to
    the Dafny question. See also the
    [Amazon Science account](https://www.amazon.science/blog/how-we-built-cedar-with-automated-reasoning-and-differential-testing)
    and [lean-lang.org case study](https://lean-lang.org/use-cases/cedar/);
    [cedar-policy repos](https://github.com/cedar-policy).
29. OASIS. XACML 3.0, 2013 — cited; the eight combining algorithms are the completeness benchmark
    for P11.
30. ★ [Immuta policy model](https://documentation.immuta.com/2026.1/governance/author-policies-for-data-access-control/authoring-policies-in-secure)
    — tag-targeted global policies; the deployment pattern P2 unblocks.
31. ★ IDSA.
    [Rulebook — Technical Agreements](https://docs.internationaldataspaces.org/ids-knowledgebase/idsa-rulebook/idsa-rulebook/4_technical_agreements)
    — largest production ODRL deployment; source of the consequence requirement (P5.2). Also
    ★ [SIMPL open architecture](https://simpl-programme.ec.europa.eu/book-page/simpl-open-architecture).

### Verification, canonicalization, foundations

32. [Dafny](https://dafny.org/latest/Installation) /
    [reference manual](https://dafny.org/dafny/DafnyRef/DafnyRef) — Go target exists; trusted-code
    limits at the extern boundary.
33. [Lean 4](https://lean-lang.org/lean4/doc) —
    [compilation pipeline](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/).
34. [Why3](https://why3.org/) — considered and not recommended (§5, formalization note).
35. ★ [RDF Dataset Canonicalization 1.0](https://www.w3.org/TR/rdf-canon/) — identity/digests with
    poisoning caveat (§3.5).
36. [SHACL](https://www.w3.org/TR/shacl/) — severity semantics behind P1's warning-gap finding.
37. ★ [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) — §7 major-zero rule
    (§3.6).
38. Makinson, van der Torre. "Input/Output Logics." *JPL* 29 (2000) — cited.
39. Kleene. *Introduction to Metamathematics*, 1952 — cited.
