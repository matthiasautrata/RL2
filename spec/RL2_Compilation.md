# RL2 Compilation Contract

**Version:** 0.7

## Status

This document is normative. It specifies the second of three phases between authored RDF and
`Eval`: compilation from a validated RDF dataset to a `CompiledPolicyModule`. It does not restate
`RL2_Semantics.md`'s evaluation semantics or `RL2_Model.md`'s abstract input/output types; it
specifies the contract that produces a `CompiledPolicyModule` and the diagnostics, schemas, and
soundness guarantee that go with it.

## 1. Scope and Pipeline

RL2 policy meaning is produced by three ordered phases:

```text
RDF dataset (policies + declared profiles)
   |  (1) SHACL: graph-structural well-formedness         -> Violation | ok
   v
   |  (2) compile: profile resolution, projection, link,   -> CompileDiagnostics | CompiledPolicyModule
   |      type, cycle, and bound checks (total, deterministic)
   v
CompiledPolicyModule (typed, flat, closed)
   |  (3) Eval(module, Request, WorldSnapshot, EvaluationConfiguration) -> EvaluationResult
```

Phase (3) is `RL2_Semantics.md`'s `Eval`. Phases (1) and (2) are this document's subject, captured
as one total function:

```text
compile(
    RDFDataset,
    ProfileModules,
    CompileConfiguration
) -> CompiledPolicyModule | CompileDiagnostics
```

`RDFDataset` is the candidate policy graph together with the RDF of every profile it declares.
`ProfileModules` are the already-compiled profile modules `compile` may consult while resolving
profile-defined vocabulary (see §9). `CompileConfiguration` carries compiler-side choices that must
be explicit and reproducible — supported profile versions, declared conformance bounds, and no
other implicit environment. `compile` performs SHACL validation as its first internal stage; a
dataset that fails SHACL never reaches projection, and a SHACL report is not itself a
`CompileDiagnostic` (§6).

**Design principle: authoring forms compile down; `Eval`'s kernel never grows.** Ergonomics belong
to expansion — refinements into conditions, recurrence into finite windows, profile vocabulary into
typed operand bindings, ODRL conveniences into canonical RL2 — not to the evaluation kernel.
Semantics and proof obligations are carried by the kernel alone; every authoring convenience is
correct by construction of its expansion into that kernel. Compilation is where this discipline is
enforced: `compile` is the only place new authoring surface may be added, and it is required to
terminate in the same closed `CompiledPolicyModule` shape regardless of the authoring form it
started from.

`compile` does not choose an internal intermediate representation for an implementation. It fixes
the *interchange* shape of its output (§5) and the diagnostics an implementation must be able to
reproduce (§6); an implementation is free to compile through any internal plan, index, or bytecode
so long as its `CompiledPolicyModule` and diagnostics match another conforming compiler's for the
same input (§8).

## 2. Check Ownership

Every validation check is normatively owned by exactly one phase. A check has no meaning if
performed twice with different outcomes, and no check may be silently skipped by both phases.

### 2.1 Phase (1) — SHACL

SHACL keeps only checks that are graph-structural: expressible against the RDF graph alone, without
a type system, a closure over collections or class hierarchies, or knowledge of declared profiles
beyond the well-formedness of the declaration itself. The current shapes in `rl2-shacl.ttl` and
their ownership:

| Shape | Structural obligation owned |
|---|---|
| `rl2:PolicyShape` | A Policy has at least one clause; at most one grantor/grantee/condition. |
| `rl2:PolicyKindShape` | A Policy is exactly one of Set, Offer, or Agreement. |
| `rl2:ClauseKindShape` | A Clause is exactly one of the admitted Norm or Promise forms. |
| `rl2:NormKindShape` | A Norm is exactly one of Privilege, Prohibition, or Duty. |
| `rl2:AgreementShape` | An Agreement has exactly one grantor and grantee and no Promise content. |
| `rl2:SetShape` | A Set carries neither grantor, grantee, nor Promise content. |
| `rl2:PrivilegeShape` | A Privilege has exactly one subject, action, and object. |
| `rl2:PrerequisiteDutyShape` | A `prerequisiteDuty` target is a Duty; cardinality on the gating edge. |
| `rl2:DutyShape` | A Duty has exactly one subject and object and one of the two admitted forms. |
| `rl2:DutyWindowShape`, `rl2:DutyWindowStartEndpointShape`, `rl2:DutyWindowEndEndpointShape` | A DutyWindow has one endpoint form per side (absolute or relative), never both. |
| `rl2:ProhibitionShape` | A Prohibition has exactly one subject, action, and object. |
| `rl2:PromiseShape` | A Promise has exactly one of `action`/`invariant`, required `counterparty`, optional `object`. |
| `rl2:AtomicConstraintShape` | An AtomicConstraint has one leftOperand, one operator that is a `rl2:ComparisonOperator` individual, and exactly one right-operand representation. |
| `rl2:ConditionKindShape` | A Condition is exactly one of AtomicConstraint or LogicalConstraint. |
| `rl2:ValueSetShape` | A ValueSet member is an IRI or literal. |
| `rl2:StatusTargetOnlyShape` | `targetNorm` occurs only alongside `obligationStateOperand`. |
| `rl2:NormStateConstraintShape` | Structural shape of a status-query AtomicConstraint. |
| `rl2:InvariantOperandRestrictionShape` | No `obligationStateOperand` occurs anywhere inside an `rl2:invariant` condition tree (the 0.7 restriction of Maintenance invariants to fact and clock operands; graph-reachability check, owned here). |
| `rl2:PromiseTargetLocalityShape` | A `targetNorm` referencing a Promise is Offer-local. |
| `rl2:LogicalConstraintShape`, `rl2:NotOperandCardinalityShape`, `rl2:AndOrXoneOperandCardinalityShape` | Logical operator is one of the fixed four; `not` has one operand, `and`/`or`/`xone` at least two. |
| `rl2:AssetCollectionShape`, `rl2:AgentCollectionShape` | Collection membership triples are well-typed. |
| `rl2:AccessPriorityShape` | `rl2:priority` is present at most once and integer-typed. |
| `rl2:LeftOperandShape`, `rl2:OperandResolutionPathShape`, `rl2:AtomicConstraintLeftOperandShape` | A LeftOperand carries at most one `resolutionPath`; core operand individuals are well-formed. |
| `rl2:RuntimeReferenceShape` | The only core `RuntimeReference` individual is `rl2:currentAgent`. |
| `rl2:ProfileShape`, `rl2:RequiresProfileShape` | A declared Profile has one SemVer `profileVersion`; `requiresProfile` targets a declared Profile. |
| `rl2:ProfileOperatorShape` | A `rl2:ProfileOperator` declares exactly one `leftParamType` and one `rightParamType` (§9). |
| `rl2:ClauseIriRecommendationShape`, `rl2:PrerequisiteDutyIriRecommendationShape`, `rl2:PolicyIriRecommendationShape` | `sh:Warning`-only IRI recommendation for clause, prerequisite-Duty, and Policy positions (§3). |

SHACL does not decide operator/datatype compatibility, duration classification, path validity,
profile resolution, dependency cycles, declared bounds, or the closed-property rule. A shape that
would require any of those is not added to `rl2-shacl.ttl`; the corresponding check is added to §2.2
instead. `rl2:OperandRangeTypeShape` — an earlier `sh:Warning` syntactic datatype-IRI comparison —
does not exist in the shapes graph; its job is the hard `②` type-checking stage below.

### 2.2 Phase (2) — compile

The compiler owns every check that needs the type system, a transitive closure, cross-graph
knowledge, or a runtime-independent decision about supported vocabulary. Compilation proceeds in
named, ordered stages; each stage's diagnostics are drawn from the registry in §6:

| Stage | Owns |
|---|---|
| `profileResolution` | Declared-profile version negotiation against `CompileConfiguration`; loading each required `ProfileModule`; rejecting an unsupported or undeclared profile. |
| `projection` | Mapping validated RDF to the canonical AST; applying the closed-world property rule (§4); rejecting unknown core properties and undeclared non-core properties; annotation retention into the source map. |
| `link` | Resolving every `LeftOperand`, `RuntimeReference`, and operator reference to its declaration (core or profile); computing action-inclusion, collection-membership, and type/subclass closures. |
| `type` | Operand/operator compatibility (ordered comparison, set operators, `isA` against a finite class model); duration-component classification; float-literal rejection; resolution-path admissibility. |
| `cycle` | Rejecting a self-reference or cycle in the finite `targetNorm` status-dependency graph. |
| `bounds` | Rejecting a policy universe that would exceed a declared conformance bound (§2.3). |

Both phases are conformance requirements. Published policy RDF is required to pass phase (1);
a conforming evaluator accepts only phase (2)'s output — it never re-derives phase (1) or phase
(2) checks from raw RDF, and it never accepts a `CompiledPolicyModule` that did not come from a
`compile` that reports success.

### 2.3 Bounds are authoring-time, not input-time

The `bounds` stage rejects a policy universe whose own declared structure — clause count, condition
or path depth, collection size — exceeds a compile-configured limit; this is a property of the
authored policy and is therefore decided once, at compile time, never re-checked per request.
`MaxSnapshotFacts` and `MaxSnapshotEvidence` (`RL2_Semantics.md` §Complexity and Constraints) bound
the `WorldSnapshot` supplied to a particular evaluation instead; they are properties of runtime
input and are checked by `validateSnapshot` inside `Eval`, not by `compile`. A `CompiledPolicyModule`
therefore carries its own declared authoring bounds (§5) but never a snapshot's fact or evidence
count, which is not yet known at compile time.

## 3. Canonical Projection and Identity

Projection produces one deterministic canonical node table from the validated graph:

- **Authored IRI first.** A node with an authored IRI is identified by that IRI in the canonical
  node table.
- **Module-scoped identity otherwise.** A node without an authored IRI (a blank node) is assigned a
  deterministic, projection-order-derived module-local identity. This identity is stable for a
  fixed input graph and canonical projection algorithm, but it is not a portable IRI: it does not
  survive being copied into another module, and it is not suitable for cross-compile citation.
- **SourceRef anchors on the node table.** Every emitted diagnostic, every entry in the source map,
  and every determining node named in an `EvaluationResult` cites a node-table entry — an authored
  IRI when one exists, a module-scoped identity otherwise. A missing authored IRI degrades
  capability (no stable cross-compile reference is possible for that node) but never validity: a
  module with blank-node clause positions still compiles and evaluates.
- **Cross-compile references require an IRI.** A relation that crosses module boundaries by
  construction — `rl2:acceptedUnder`, provenance properties, and any other reference from outside
  the authoring graph — MUST target an authored IRI. A module-scoped identity cannot be dereferenced
  by a party that does not hold this exact compiled module.
- **The SHACL warning is deliberate design, not an oversight.** `rl2:ClauseIriRecommendationShape`,
  `rl2:PrerequisiteDutyIriRecommendationShape`, and `rl2:PolicyIriRecommendationShape` (§2.1) issue a
  `sh:Warning` — not a violation — when a clause position, a `prerequisiteDuty` target, or a Policy
  node is a blank node. Authors are known to ignore a silent recommendation (this is the documented
  experience with ODRL 2.2's `odrl:uid`); a validation-visible warning is used instead of silent
  guidance, without making an IRI mandatory. Condition substructure is deliberately not targeted:
  requiring stable identity all the way into constraint trees would defeat the purpose of a
  lightweight authoring form.
- **RDFC-1.0 is not adopted for this identity scheme.** A stable digest of the *source RDF graph*
  (as opposed to the compiled module) is a separable concern addressable later with RDFC-1.0
  canonical labeling, which needs its own resource bounds against adversarial blank-node graphs.
  Adopting node-table identity now does not foreclose adding RDFC-1.0 digests later.

## 4. The Closed-World Property Rule

The RL2 core namespace (`https://w3id.org/rl2#`) is closed under projection: an `rl2:`-prefixed
property that projection encounters and does not recognize is a compile error (`UnknownCoreProperty`,
§6) — the misspelling and hallucination catcher for machine-generated RDF. A property outside the
core namespace is valid on an RL2 node only when a declared, supported profile defines it;
otherwise it is rejected with a stable diagnostic (`UndeclaredTerm`, §6). This is fail-closed by
design: a well-formed-looking but undeclared property must fail loudly rather than be silently
ignored or silently accepted.

Triples whose subject is not itself part of the projected RL2 graph (an external resource merely
mentioned in passing) are outside the projection entirely and are not subject to this rule.

The allowlist for non-core properties is **property-level**, not namespace-level: two properties in
the same external namespace can have different treatment, because their semantic weight differs.

| Category | Properties | Treatment |
|---|---|---|
| Semantic core inputs | `rdf:type`, `rdfs:subClassOf`; `rdfs:range` on `rl2:LeftOperand` individuals only | Read by phase (2) — `rdf:type`/`rdfs:subClassOf` feed the type/class closure (link stage); `rdfs:range` on an operand is read only until that operand declares `rl2:valueType` (see the transition rule below). |
| Annotation allowlist | `rdfs:label`, `rdfs:comment`, `rdfs:seeAlso`; `dcterms:title`, `dcterms:description`, `dcterms:creator`, `dcterms:created`, `dcterms:modified`, `dcterms:identifier` (a `dc11:` equivalent is normalized to `dcterms:` at projection); `skos:prefLabel`, `skos:altLabel`, `skos:note`, `skos:definition`, `skos:example`; `prov:wasDerivedFrom`, `prov:wasAttributedTo`, `prov:generatedAtTime` | Retained in the source map; semantically ignored by evaluation. `materialize()` (`RL2_Semantics.md` §Pure Offer Acceptance) writes `prov:wasDerivedFrom` on materialized nodes. |
| Named rejections | `owl:sameAs` on an RL2 node; `skos:broader`, `skos:narrower` on an RL2 node | Rejected with a dedicated diagnostic. `owl:sameAs` would let identity be asserted around matching and determinism rather than through it (`IdentityAssertionRejected`). Hierarchy is expressed only through `rl2:includedIn` or `rdfs:subClassOf`; SKOS broader/narrower is never a hierarchy source for core matching (`HierarchyAssertionRejected`). |
| Extensible | Any additional annotation-only term | A `ProfileModule` may declare further terms as annotation-only, with the same source-map-only treatment as the built-in annotation allowlist. |

**The `rl2:valueType` transition.** Operand typing is normatively carried by `rl2:valueType`
(`rl2.ttl`), not by `rdfs:range` on the operand individual. An operand used in a policy without a
declared `rl2:valueType` is a compile error (`MissingValueType`, §6). `rdfs:range` on a `LeftOperand`
individual is tolerated documentation only once `rl2:valueType` is present, and is read as the
semantic core input above only for a corpus that has not yet migrated. This document does not
change `rdfs:range` on any existing property; the transition is entirely about which property
compile reads for operand typing, not about retracting or reassigning any `rdfs:range` triple.

## 5. CompiledPolicyModule

`CompiledPolicyModule` is the abstract flat, typed, closed output of `compile`. Its structure is
normative; its representation choices are fixed to keep the module bytewise-diffable and free of
node-table indirection at the point of use:

- **Flat arrays, integer indices.** Clauses, conditions, operands, and profile references are
  stored as flat arrays; cross-references inside the module are integer indices into those arrays,
  not blank-node or IRI references. There is no residual blank-node identity inside a compiled
  module — the node table (§3) is retained only in the source map, not in the evaluated structure.
- **Resolved condition and operand types.** Every condition node carries its resolved comparison
  behavior (the closed operator identity, §9); every operand carries its resolved
  `(scope, canonicalPath, declaredType, profile)` tuple, eliminating repeated path parsing or
  profile lookup at evaluation time.
- **Materialized closures.** Action-inclusion (`rl2:includedIn`) and type/subclass closures are
  precomputed into index arrays rather than left as graph traversals.
- **Pre-discriminated Duty forms.** A Duty or Promise's form (Achievement or Maintenance) is
  resolved once, at compile time, into a discriminated representation; `Eval` does not re-derive it
  from the presence or absence of `rl2:action`/`rl2:invariant`.
- **Embedded compile-time artifacts.** Declared authoring bounds (§2.3), profile digests (§9), and
  the source map (§3) travel with the module.

### 5.1 Canonical serialization

The one normative serialization of `CompiledPolicyModule` is canonical JSON:

- object keys are sorted in a fixed, documented order (byte order on the UTF-8 key);
- every `Numeric` value (RL2's exact-decimal number domain) is serialized as a JSON **string**, not
  a JSON number — a JSON number is an IEEE 754 double, which does not preserve exact-decimal
  semantics for values RL2 treats as exact;
- the module digest is the SHA-256 hash of the canonical JSON bytes (UTF-8, no trailing
  whitespace, keys sorted as above);
- CBOR or protocol-buffer encodings of the same abstract structure are permitted as a private,
  non-normative transport, provided a canonical-JSON round trip through them is lossless; only the
  canonical JSON encoding participates in digest computation and cross-implementation conformance
  comparison.

Two conforming compilers given the same `RDFDataset`, `ProfileModules`, and `CompileConfiguration`
MUST produce byte-identical canonical JSON (and therefore identical digests) — this is the
projection-determinism half of §8's soundness statement.

## 6. Compile Diagnostics

A `CompileDiagnostic` is:

```text
CompileDiagnostic = (
    code     : DiagnosticCode,
    stage    : Stage,
    severity : Severity,
    site     : SourceRef,
    detail   : String?
)

Stage ::= parse | SHACL | profileResolution | projection | link | type | cycle | bounds
```

`site` cites the canonical node table (§3). Diagnostics are collected within one stage — a stage
does not stop at its first diagnostic — but compilation stops at the first stage that produces any
diagnostic; a later stage's checks are not run against a graph a prior stage already rejected.
`CompileDiagnostics` reports the ordered stage at which compilation stopped and every diagnostic
collected in that stage, in canonical order (stable sort by `(stage, code, site)`).

**Conformance requirement.** Two conforming compilers given the same input MUST report the same
`(code, site)` set in the same canonical order. This is what makes negative conformance vectors
portable: a vector states the expected diagnostic set, not an implementation's internal error
text. Diagnostic codes are versioned spec surface — adding one is a spec change, not an
implementation detail.

Phase (1) reports through standard SHACL validation reports; it does not use this taxonomy. Phase
(1) and phase (2) diagnostics are never merged into one collection — a caller distinguishes "not
SHACL-conformant" from "SHACL-conformant but rejected by compile."

### 6.1 Initial diagnostic code registry

| Code | Stage | Meaning |
|---|---|---|
| `UnknownCoreProperty` | `projection` | An `rl2:`-prefixed property was encountered that the core vocabulary does not define. |
| `UndeclaredTerm` | `projection` | A non-core property was used without a declared, supported profile defining it. |
| `UnknownOperator` | `link` | `rl2:constraintOperator` names an individual that is not a core comparison/logical operator and not a declared `rl2:ProfileOperator`. |
| `OperandTypeMismatch` | `type` | An operator was applied to operand types its declared signature does not admit (e.g. ordered comparison on a non-ordered type, a set operator against a scalar). |
| `MissingValueType` | `type` | An operand is used in a policy without a declared `rl2:valueType`. |
| `InvalidResolutionPath` | `type` | A `resolutionPath` is not a well-formed canonical path, or its root is not an admitted canonical root. |
| `UnsupportedLiteralDatatype` | `type` | A right-operand literal uses a datatype RL2 does not admit for comparison (e.g. a bare float where exact-decimal `Numeric` is required). |
| `MixedDurationComponents` | `type` | A duration-shaped value mixes calendar and exact-time components RL2 does not allow to combine. |
| `StatusDependencyCycle` | `cycle` | The finite `targetNorm` status-dependency graph contains a self-reference or cycle. |
| `WindowMalformed` | `type` | Both of a `DutyWindow`'s endpoints are Absolute and start is not before end. (Endpoint-form exclusivity per side is phase (1)'s `DutyWindow*Shape`s; a window with a Relative endpoint is ordering-checked at resolution time, where a degenerate resolved interval is a data-origin `Invalid`.) |
| `SentinelMisuse` | `type` | `rl2:anyAgent`/`rl2:anyAsset` appears as a collection member, or as the subject or object of a `rl2:Promise`. (A Duty MAY carry a sentinel — it is a template, bound per `RL2_Semantics.md` §Duty Template Binding; a Promise crystallizes at materialization and has no binding source, so sentinels there are prohibited outright. Sentinel misuse in a Request field is rejected by the `Request` interchange schema, §7, not by `compile`.) |
| `UnboundStatusTarget` | `link` | An `rl2:obligationStateOperand` targets (via `rl2:targetNorm`) a Duty whose `rl2:subject` or `rl2:object` is a sentinel. A template Duty has no standalone status (`RL2_Semantics.md` §Duty Template Binding); `site` is the operand's `ErrorSite`. |
| `BoundExceeded` | `bounds` | A declared authoring bound (§2.3) was exceeded by the compiled structure. |
| `UnsupportedProfile` | `profileResolution` | A required profile or profile version is not supported by `CompileConfiguration`. |
| `ProfileDigestMismatch` | `profileResolution` | A `ProfileModule` supplied for compilation does not match the digest its declaration expects. |
| `IdentityAssertionRejected` | `projection` | `owl:sameAs` was asserted on an RL2 node (§4). |
| `HierarchyAssertionRejected` | `projection` | `skos:broader`/`skos:narrower` was asserted on an RL2 node (§4). |
| `UnresolvedReference` | `link` | A structurally admissible reference (e.g. `prerequisiteDuty`, `targetNorm`) does not resolve to a node in scope. |

This registry is extensible in later spec revisions; it is not extensible per-deployment — a
private diagnostic code is not a conforming `CompileDiagnostic`.

The ODRL importer's fourteen migration diagnostics (`RL2_ODRL_Mapping.md` §2) are a separate,
pre-compile family: they describe `translate`'s partial function from ODRL to canonical RL2, not
`compile`'s function from canonical RL2 to a `CompiledPolicyModule`. A translated policy that
produces no `translate` diagnostic still passes through phases (1) and (2) like any other
canonical RL2 graph and may still receive `CompileDiagnostic`s of its own.

## 7. Interchange Schemas

`Request`, `WorldSnapshot`, `EvaluationConfiguration`, and `EvaluationResult` — defined abstractly
in `RL2_Model.md` §§3, 4, 5, 6 — get published JSON Schemas under this document's canonical-JSON
conventions (§5.1: sorted keys, `Numeric` as string), versioned with the spec. Conformance vectors
and a PDP-style API consume the same schemas; this document does not introduce a second wire
format for the same abstract values.

| Interchange schema | Serializes | Notable fields beyond the abstract type |
|---|---|---|
| `Request` | `RL2_Model.md` §3 | `parameters` as a canonical-JSON object keyed by name; `Numeric` parameter values as strings. |
| `WorldSnapshot` | `RL2_Model.md` §4 | `facts` and `evidence` as canonical-JSON arrays in a fixed sort order (by `id`), so two structurally equal snapshots serialize identically. |
| `EvaluationConfiguration` | `RL2_Model.md` §5 | Declared conformance bounds and supported-profile versions as explicit fields, not an open map — an unrecognized configuration field is a schema validation failure, not silently ignored input. |
| `EvaluationResult` | `RL2_Model.md` §6 | Replay-anchoring fields added at the interchange layer, listed below. These fields are additive to the abstract `EvaluationResult` value; they do not change its meaning, only what a caller retains alongside it. |

**`EvaluationResult` as a replay-anchored audit record.** The interchange schema carries, in
addition to `decision`, `normativeEnvelope`, `dutyStatuses`, `promiseStatuses`, and `diagnostics`:

- the determining `SourceRef`s (§3) for the atoms that produced `decision`, not only the full
  envelope;
- the compiled module's digest (§5.1);
- the `WorldSnapshot`'s canonical digest (computed the same way, over its interchange serialization);
- `evaluationTime` (echoed, not re-derived, from the snapshot used);
- an echo of the `EvaluationConfiguration` actually applied.

Every field is chosen so that a result is independently re-derivable from retained artifacts alone
— the compiled module (by digest), the snapshot (by digest), and the configuration — without
needing the evaluator's internal state. This is what makes an `EvaluationResult` a replayable audit
record rather than a transient response value.

## 8. Soundness and Determinism

**Theorem (compile soundness).** If `compile(G, profiles, cfg) = Ok(m)`, then for every
schema-valid `Request`, `WorldSnapshot`, and `EvaluationConfiguration`, `Eval(m, …)` contains no
**policy-origin** cause: no `Invalid(ComparisonSite(…))` and no cause whose site names a defect in
`m`'s own structure. A compiled module never fails for reasons of its own; it can only be
indeterminate because the supplied world is. Residual `Missing`/`Conflict` causes remain —
correctly, as properties of the data, never eliminated by compilation.

**Companions.**

- *Projection determinism*: two conforming compilers given the same `(G, profiles, cfg)` produce a
  byte-identical `CompiledPolicyModule` (§5.1), hence the same digest.
- *Evaluation determinism*: two conforming evaluators given the same `(m, R, W, C)` produce a
  byte-identical canonical `EvaluationResult` (§7).

These are normative obligations now; a mechanized (e.g. Lean) proof is future work and does not
gate conformance.

**Scope: core operators only.** The evaluation-determinism obligation above is stated over modules
whose atomic constraints use the ten core comparison operators (§Denotational Semantics,
`RL2_Semantics.md`). A module that uses a `rl2:ProfileOperator` (§9.1) is deterministic *relative to*
that profile's own normative denotation — the theorem's guarantee still holds conditional on the
denotation being a pure total function, exactly as required — but cross-implementation agreement on
the operator's actual output is a separate, per-profile conformance claim, checked by that profile's
vector suite, not part of core STRICT conformance (§10).

### 8.1 Site partition

`RL2_Semantics.md`'s `ErrorSite` grammar is:

```text
ErrorSite ::= LeftOperand
            | RuntimeReference
            | Path
            | SnapshotSite(String)
            | ConfigurationSite(String)
            | EvidenceSelector
            | StatusSite(StateTarget)
            | ComparisonSite(Operator, ValueType, ValueType)
```

Every constructor is assigned to exactly one side of the soundness theorem:

| `ErrorSite` constructor | Origin | Rationale |
|---|---|---|
| `ComparisonSite(Operator, ValueType, ValueType)` | Policy | Operand and operator types are resolved statically by the `type` stage (§2.2); a successfully compiled module's comparisons are type-checked before `Eval` ever runs. |
| `LeftOperand` | Policy | Operand declaration and binding (core or profile) is checked by the `link` stage; an unresolved operand is `UnresolvedReference` or `MissingValueType` at compile time, not at evaluation time. |
| `RuntimeReference` | Policy | The closed `RuntimeReference` vocabulary (core: `rl2:currentAgent` only) is checked by SHACL and by the `link` stage; a module cannot compile with an unresolvable reference. |
| `Path` | Policy | Path syntax and root admissibility (`InvalidResolutionPath`) are checked by the `type` stage; a compiled module's paths are structurally admissible before evaluation. |
| `ConfigurationSite(String)` — the status-dependency-cycle case | Policy | A self-reference or cycle in the `targetNorm` status-dependency graph is now rejected by the compiler's `cycle` stage (`StatusDependencyCycle`, §2.2); a successfully compiled module contains no such cycle, so `Eval` cannot encounter it. |
| `SnapshotSite(String)` | Data | Depends on the `WorldSnapshot` supplied to a particular evaluation — missing, invalid, or conflicting facts are properties of runtime input `compile` never inspects. |
| `EvidenceSelector` | Data | Depends on `WorldSnapshot.evidence` and the configured `admissibleEvidence` rule, both runtime inputs. |
| `StatusSite(StateTarget)` | Data | Duty/Promise status depends on snapshot facts and evidence at evaluation time, not on module structure. |
| `ConfigurationSite(String)` — every other case (unsupported strategy, an unsupported or missing profile/version, an absent or non-total fact- or evidence-admissibility rule, an absent or non-positive conformance bound) | Data | These describe `EvaluationConfiguration`, a runtime input independent of the compiled module; `compile` validates its own `CompileConfiguration` (§1) but does not — and cannot — foresee the `EvaluationConfiguration` a later, separate evaluation call will supply. |

`ConfigurationSite` is therefore the one constructor whose instances split across the partition,
because it names two different objects in the current design: a compile-time configuration
concern that has now moved into `compile`'s own `cycle` stage, and a run-time configuration concern
that remains `Eval`'s. The site name is unchanged; the owning phase for each case is what this
table fixes.

## 9. Profile Compilation

Profiles are authored as RDF in any serialization (Turtle, JSON-LD, or another RDF syntax); the
graph is the normative artifact, and the corpus uses Turtle. A profile compiles into a canonical
JSON `ProfileModule` under the same digest discipline as a policy module (§5.1) — one pipeline,
not a separate one for profiles. A policy's required-profile declaration names a profile digest
(directly or via a supported version), and `profileResolution` (§2.2) rejects a mismatch
(`ProfileDigestMismatch`) or an unsupported profile (`UnsupportedProfile`).

**Inline operand declarations remain legal.** A `LeftOperand` declared directly in the policy graph
— typed with `rl2:valueType` and given a `rl2:resolutionPath` — is a self-contained micro-profile;
`rl2:requiresProfile` is required only for a term the policy graph does not itself declare. The
closed-world property rule (§4) still applies: an undeclared non-core term is rejected regardless
of whether a full profile or an inline declaration was the missing piece.

### 9.1 Plug-in operators (D8a)

A profile may declare a comparison operator of its own — a **`rl2:ProfileOperator`** — rather than
being limited to the ten core comparison operators. `rl2:ProfileOperator` is `rdfs:subClassOf
rl2:ComparisonOperator` (the class every core comparison operator individual, e.g. `rl2:eq`, is
already typed as; confirmed by inspection of `rl2.ttl` rather than introduced by this document), so
a profile operator individual is usable anywhere `rl2:constraintOperator` admits a
`rl2:ComparisonOperator`, including `rl2:AtomicConstraintShape` (§2.1).

Each `rl2:ProfileOperator` individual declares a typed binary signature:

```text
rl2:leftParamType  : the value type (a datatype IRI or profile value class) admitted as the
                     operator's left-hand operand type
rl2:rightParamType : the value type admitted as the operator's right-hand operand type
```

Neither property declares an `rdfs:range` (the same rationale as `rl2:valueType`, §4: their values
are heterogeneous — datatype IRIs and classes both occur — so no single class is the range).
`rl2:ProfileOperatorShape` (§2.1) requires exactly one of each on every `rl2:ProfileOperator`
individual.

The declaration is part of the profile's digest — a profile operator's identity, like a core
operator's, is fixed by what compiled it, not by an out-of-band implementation registry. A plug-in
operator's implementation is required to be **pure, total over its declared domain, and free of
I/O**, matching every other part of the evaluation kernel; conformance for a profile's plug-in
operators is established the same way as core conformance — by that profile's own vectors, checked
against `OperandTypeMismatch` and `UnknownOperator` at the `link`/`type` stages when a
policy misuses the declared signature.

**Normative denotation requirement.** Declaring a `rl2:ProfileOperator` is not by itself enough to
make a profile conforming. The declaration pins the operator's *identity* (name, digest, parameter
types); it does not pin its *behavior*, so two evaluators can compile the same profile digest and
still disagree on what the operator returns. A conforming profile MUST therefore also supply, in
the profile's own normative document, a **denotation**: a definition of the operator as a pure
**total** function over its declared `leftParamType`/`rightParamType` pair, in the same register as
`apply` (`RL2_Semantics.md`, `apply : Operator × Value × Value × Env → Boolean`) defines the ten core
comparison operators — every input pair in the declared domain maps to `True`, `False`, or a typed
`EvalError`; no partiality, and no discretion left to the host implementation. A
`rl2:ProfileOperator` declaration without such a denotation makes the profile non-conforming. The
profile MUST also ship conformance vectors exercising each declared operator, both positive
(operator returns `True`) and negative (operator returns `False`, and, where the denotation admits
one, the `EvalError` case).

**Doctrine note (non-normative).** When the profile-specific judgment is request-independent — e.g.
"these two parties are in the same jurisdiction group" — prefer precomputing it as a typed,
attributed `WorldSnapshot` fact at assembly time rather than declaring an operator for it. Reserve a
`rl2:ProfileOperator` for genuine per-request value-pair comparisons that cannot be tabulated at
assembly time.

```turtle
@prefix rl2:     <https://w3id.org/rl2#> .
@prefix privacy: <https://w3id.org/rl2/profiles/privacy#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .

privacy:sameJurisdictionGroup a rl2:ProfileOperator ;
    rdfs:label "Same jurisdiction group" ;
    rdfs:comment "Compares two Jurisdiction values for group membership rather than identity." ;
    rl2:leftParamType privacy:Jurisdiction ;
    rl2:rightParamType privacy:Jurisdiction .
```

This declaration alone is not conforming; the privacy profile's own normative text is where
`sameJurisdictionGroup`'s total-function denotation (and its conformance vectors) must live.

## 10. Conformance

A conforming compiler:

1. accepts exactly the RDF datasets a conforming SHACL processor operating under the validation
   regime below accepts against `rl2-shacl.ttl`, and rejects every other dataset with a SHACL
   validation report, never a `CompileDiagnostic`;
2. for a dataset that passes phase (1), either returns a `CompiledPolicyModule` satisfying §5, or
   returns the `CompileDiagnostics` set required by §6 — never a partial or best-effort module;
3. produces byte-identical canonical JSON (§5.1) to any other conforming compiler given the same
   `(RDFDataset, ProfileModules, CompileConfiguration)`;
4. produces the same `(code, site)` diagnostic set, in the same canonical order, as any other
   conforming compiler given the same rejected input;
5. never emits a policy-origin cause (§8) from `Eval` when given its own successfully compiled
   module and schema-valid runtime inputs.

A conforming evaluator accepts only a `CompiledPolicyModule` — directly, or via the interchange
JSON Schema of §7 — as its policy-universe input; it does not accept raw policy RDF and does not
re-run phase (1) or phase (2) checks itself. A conforming interchange participant (a vector, a PDP
API, a replay tool) uses the JSON Schemas of §7 for `Request`, `WorldSnapshot`,
`EvaluationConfiguration`, and `EvaluationResult`, and the canonical serialization of §5.1 for
`CompiledPolicyModule` and `ProfileModule` digests.

**Profile operators are outside core conformance.** Clauses 3–5 above (byte-identical projection,
byte-identical diagnostics, byte-identical evaluation results — STRICT conformance) quantify over
policies whose atomic constraints use core comparison operators only. An implementation MAY claim
full core conformance, including STRICT conformance, without implementing any `rl2:ProfileOperator`
(§9.1). Conversely, "conforms to profile P" is a distinct claim: it requires implementing every
operator P declares, per P's own normative denotation (§9.1), and passing P's conformance vector
suite in full. Core conformance and profile conformance are independently checkable and neither
implies the other.

### 10.1 Validation regime

Clause 1 above ("a conforming SHACL processor operating under the validation regime below") is
fixed by this regime; a conforming compiler's phase (1) and its canonical projection (§3) MUST
operate under it, not against an implementation-specific dataset interpretation.

1. **Dataset scope.** The input to phase (1) and to canonical projection is the supplied RDF
   document or documents, parsed and merged into a single graph — the default graph. Named-graph
   semantics MUST NOT be consulted; a supplied dataset's non-default graphs MUST be ignored.
   `owl:imports` MUST NOT be followed. The compiler MUST perform no network or file fetching beyond
   the explicitly supplied inputs.
2. **Base IRI.** The base IRI, when an input uses relative IRIs, is an explicit caller-supplied
   input to `compile`, recorded alongside `RDFDataset`. Any relative IRI remaining after parsing
   MUST be rejected — canonical projection (§3) requires absolute IRIs.
3. **Entailment: none.** Phase (1) validation and phase (2) projection MUST operate on the asserted
   graph only; no RDFS or OWL entailment regime may be applied before or during validation. RL2's
   closed-world property rule (§4) and its SHACL shapes are the enforcement layer; entailment
   silently adding triples would bypass both.
4. **SHACL feature set.** SHACL Core plus SHACL-SPARQL (`sh:sparql` constraints), exactly — the
   shapes graph `spec/rl2-shacl.ttl` uses both. SHACL Advanced Features (rules, functions) are not
   used and MUST NOT be active during phase (1).
5. **Severity.** A validation result with severity `sh:Violation` MUST cause phase (1) rejection. A
   result with severity `sh:Warning` MUST NOT cause rejection but MUST be reported to the caller
   (RL2 deliberately ships `sh:Warning`-severity IRI-recommendation shapes, §2.1). The **canonical
   validation-report projection** is the set of tuples `(source shape IRI, focus node, result path
   if any, severity)`, deduplicated and sorted by that tuple order; two conforming implementations
   agree when they produce the same projected set for the same input. Message strings are
   informative only and are not part of the projection.

Positive and negative dataset fixtures exercising this regime — imports ignored, named graphs
ignored, relative-IRI rejection, warning-does-not-reject — ship with the conformance-vector suite
(`backlog.md` §1).
