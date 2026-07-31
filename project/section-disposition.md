# SCOPE-2 Section Disposition

**Status:** Initial audit complete; update rows when extraction or deletion lands.

**Rule:** A whole document may move before its mixed sections are rewritten, but no normative core
definition may be discarded merely because it currently appears in a protocol or IR document.

Disposition values: `core`, `rewrite-core`, `informative`, `future-protocol`,
`future-implementation`, and `historical/remove`.

## `spec/RL2_Semantics.md`

| Section | Disposition | Action |
|---|---|---|
| Abstract Syntax and Type System | core | Retain; replace transition/event syntax with evidence only where needed |
| Semantic Domains: Agents/Actions | core | Retain |
| Semantic Domains: mutable `Σ` and EventLog | rewrite-core | Replace reads with immutable `WorldSnapshot`; move storage/order/Case fields out |
| Environments | rewrite-core | Bind Request, requested agent/asset, snapshot, and facts explicitly |
| Result and Truth Algebra | core | Retain C3-1 causal errors and three-valued logic |
| Condition semantics | core | Retain; interpret EventConstraint over supplied evidence |
| `resolve`, runtime references, paths | rewrite-core | Resolve only supplied snapshot values; remove live fallback and shared-state semantics |
| Request matching and witness derivation | rewrite-core | Retain matching; define evidence identity/scoping without append order |
| Norm denotations | core | Retain |
| Hohfeldian correlatives and denotations | core | Retain; exclude mutation protocol |
| Sanctions and remedies | rewrite-core | Retain authored/derived policy meaning; exclude generated Requirement lifecycle |
| Policy applicability and norm activation | core/consolidate | Keep one pure definition; remove duplicated dynamic/operational forms |
| Small-Step Operational Semantics | future-protocol/implementation | Extract declarative status meaning, then remove from core |
| Requirement and Case status derivation | future-protocol | Remove from core |
| Duty Achievement/Maintenance transitions | rewrite-core | Replace with total `dutyStatus` over time/evidence |
| Promise transitions | rewrite-core | Replace with total `promiseStatus` |
| Crystallization/materialization | rewrite-core | Keep pure Offer→Agreement transformation only |
| Promise→Duty runtime generation | future-protocol | Core may retain only an authored or pure derived remedy relation |
| Event Processing | future-protocol | Remove append/idempotency/late-arrival rules from core |
| Normative envelope and derivation/resolution split | core | Retain as evaluator center |
| Big-Step Eval | rewrite-core | Return immutable EvaluationResult, not updated state/effects |
| Duty State Updates | rewrite-core | Replace with status calculation |
| Constraint algebra and composition | core/consolidate | Retain without duplicating primary rules |
| State scope, concurrency, CAS, commit | future-implementation/protocol | Keep only immutable-snapshot premise and Offer identity needed by transformation |
| Policy generations | split | Caller-selected PolicyUniverse is core; Case binding/lifecycle is future protocol |
| Compilation interoperability | rewrite-core | Retain canonical ingestion and ODRL translation contract |
| Protocol correspondence | future-protocol | Remove from core |
| Complexity and proof obligations | rewrite-core/informative | Bound pure snapshot evaluation; move IR/effect proof plan |

## `docs/RL2_Architecture.md`

**Progress:** Active document replaced with the concise SCOPE-2 architecture. The former full
document is preserved as `future/reference-implementation/RL2_Architecture_Scope1.md`; normative
canonical-projection details still require extraction under S2-C5.

| Section | Disposition | Action |
|---|---|---|
| Evaluation pipeline | informative/rewrite | Four-input pure evaluation; remove context-materialization and wrapping stages |
| Layer separation | informative | Retain with SCOPE-2 boundary |
| Derivation/resolution and strategies | core extraction | Normative definitions live in Semantics; retain rationale only here |
| Protocol wrapping/correspondence/state ownership | future-protocol | Remove from active Architecture |
| Functional model | future-implementation | Retain later as a possible evaluator architecture |
| Canonical form and RDF→AST projection | core extraction | Move normative rules to `spec/` |
| IR, ContextManifest, TargetIndex | future-implementation | Keep only semantic matching rules in core |
| Runtime lookup/manifest/resolve/evalIR APIs | future-implementation | Remove from language architecture |
| Request processing and interaction modes | future-protocol | Move |
| Composition invariants | split | Keep semantic determinism/equivalence; move API sufficiency claims |
| Open design questions | project tracker | Remove from reader document |
| Expressive characterization/prior work/goals | informative/rewrite | Retain conservative language claims |
| Enforcement boundary | informative/rewrite | Handoff is EvaluationResult, not Case |

## `future/reference-implementation/RL2_IR.md`

| Section | Disposition | Action |
|---|---|---|
| RDF→canonical AST pipeline | core extraction | Move normative projection to `spec/` |
| Construct correspondence | core extraction | Use as skeleton for projection and ODRL mapping |
| Normalized AST constructors | core extraction | Remove storage/index layout and numeric ClauseRef choices |
| Condition interpretation | consolidate | Semantics remains authoritative; keep code as reference only |
| Snapshot consistency | core extraction | Retain no-I/O immutable-input rule |
| Source resolution architecture | future-implementation | Retain here |
| State/effects/commit | future-implementation/protocol | Retain here, outside core |
| Derive-then-resolve | consolidate | Preserve normative meaning in Semantics; remove effect shell from core |
| Crystallization orientation | core extraction | Keep only pure transformation constraints |
| Subsumption | core extraction | Semantics is core; indexes are optional |
| Equivalence/testing/trust model | informative | Rewrite against pure Eval contract |

## `docs/RL2_ExternalData.md`

**Progress:** Active document replaced with snapshot-oriented guidance. The former SourceBinding,
ContextManifest, live-resolution, and interaction-mode design is preserved as
`future/reference-implementation/RL2_ExternalData_Scope1.md`.

| Section | Disposition | Action |
|---|---|---|
| Pure-evaluator boundary | core extraction | Eval consumes an immutable supplied snapshot and performs no I/O |
| Missing/invalid/conflicting value behavior | core extraction | Integrate with result/truth algebra |
| SourceBinding and function registry | future-implementation | Move |
| Hybrid/in-band resolution | future-implementation | Move |
| Mock sources/testing | informative future implementation | Retain as implementation guidance |
| Single-shot/iterative/pre-flight modes | future-protocol/API | Move |
| Handoffs | historical/remove | Delete after substantive rules are redistributed |

## `future/protocol/RL2_Protocol.md`

| Section | Disposition | Action |
|---|---|---|
| Minimal Request | core extraction | Abstract triple now in `spec/RL2_Model.md`; RDF interchange may remain future companion |
| EvaluationResult decisions | core extraction | Abstract result now in Model; serialization remains companion work |
| Context | core extraction/rewrite | Replace with generic WorldSnapshot facts/evidence |
| Fulfillment evidence meaning | core extraction/rewrite | Define evidence-to-duty relation without Requirement as truth source |
| Requirement lifecycle | future-protocol | Retain here |
| Case lifecycle and event sourcing | future-protocol | Retain here |
| Re-evaluation triggers | future-protocol | Retain here |
| Provenance/audit persistence | future-protocol | Retain here; core profiles may require attributed input values |
| Worked example | split | Preserve policy scenario; retain Case workflow here |
| Comparisons | informative/rewrite | Correct claims after split |

## Completion Rule

A row is complete only when:

1. the destination contains the necessary definition or rationale;
2. the source no longer makes a conflicting normative claim;
3. inbound references point to the destination;
4. affected Turtle fences and use cases validate;
5. `reorganization-plan.md` records the completed extraction.
