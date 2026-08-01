# ODRL 2.2 Migration to RL2

**RL2 version:** 0.7

## 1. Purpose

This document defines deterministic translation from supported ODRL 2.2 policy expressions to
canonical RL2. Translation is a partial function:

```text
translate(ODRLPolicy, TranslationConfiguration)
    -> CanonicalRL2Policy | Rejected(diagnostics)
```

An importer does not treat arbitrary ODRL RDF as native RL2 and does not guess when ODRL permits
materially different interpretations. The source model is the [ODRL Information Model
2.2](https://www.w3.org/TR/odrl-model/) and its [Vocabulary and Expression
2.2](https://www.w3.org/TR/odrl-vocab/).

## 2. Dispositions

Each source construct has one disposition:

| Disposition | Meaning |
|---|---|
| `exact` | The canonical RL2 result preserves the relevant ODRL behavior. |
| `normalized` | A deterministic structural rewrite preserves behavior. |
| `clarified` | Translation requires a declared interpretation that ODRL does not fix. |
| `profile-dependent` | Translation requires an identified RL2 profile. |
| `rejected` | Core RL2 has no safe deterministic interpretation. |
| `metadata-only` | The term is preserved outside evaluation or reported as ignored metadata. |

Translation diagnostics are stable identifiers. At minimum, an importer distinguishes:

```text
UnsupportedPolicyType
UnsupportedRuleRelation
UnsupportedPartyFunction
UnsupportedConstraintOperand
UnsupportedOperator
UnsupportedOrderedConstraint
UnsupportedFailureRelation
MissingTranslationInterpretation
ConflictingCompactValue
UnresolvedInheritedPolicy
InheritanceCycle
UnsupportedProfile
NonCanonicalSource
```

## 3. Canonicalization

An ODRL expression is normalized before term mapping:

1. Every Policy, Rule, Constraint, Asset, and Party that requires identity is assigned its
   normalized source identity from `odrl:uid` or RDF identity.
2. Compact Policy values shared at Policy level are copied to each Rule that lacks that value.
   A conflicting Rule-local and Policy-level value yields `ConflictingCompactValue`.
3. Repeated Permissions, Prohibitions, Duties, targets, actions, or parties are atomized into
   singular canonical clauses where the ODRL Information Model permits expansion.
4. Multiple constraints applying to one component are conjoined in one canonical `And` tree.
5. `odrl:inheritFrom` is resolved and flattened before RL2 projection. Missing parents and cycles
   are rejected. The resulting policy contains no inheritance edge.
6. Vocabulary aliases and RDF lexical forms are normalized to their semantic values.

Atomization preserves the identity of a shared ODRL Duty. If several Permissions refer to the
same Duty, their RL2 Privileges refer to the same prerequisite Duty rather than copied Duties.

## 4. Policy Mapping

| ODRL source | RL2 result | Disposition | Rule |
|---|---|---|---|
| `odrl:Policy` or `odrl:Set` | `rl2:Set` | normalized | Translate all supported Rules; a Set is operative when supplied to `Eval`. |
| `odrl:Offer` | `rl2:Offer` | clarified | Translate proposed Rules. The Offer contributes no normative atoms before explicit RL2 materialization. Translation never infers acceptance. |
| `odrl:Agreement` | `rl2:Agreement` | normalized | `odrl:assigner` maps to `rl2:grantor`; `odrl:assignee` maps to `rl2:grantee`. Both parties are required. |
| `odrl:Assertion` | profile or `rl2:Set` | profile-dependent | The profile must state whether the assertion is operative policy or attributed snapshot evidence. |
| `odrl:Privacy` | `rl2:Set`, `rl2:Agreement`, or profile policy | profile-dependent | The legal and party interpretation must be supplied by a privacy profile. |
| `odrl:Request` | RL2 `Request` plus optional snapshot facts | clarified | A request is an evaluation input, not a policy container. |
| `odrl:Ticket` | none | rejected | Core RL2 does not define bearer-token or ticket semantics. |
| `odrl:profile` | `rl2:requiresProfile` | clarified | `TranslationConfiguration` maps the ODRL profile IRI to an RL2 profile and minimum version. |
| `odrl:conflict` | evaluation strategy | clarified | See §8. |
| `odrl:inheritFrom` | flattened policy | normalized | See §3; no inheritance edge survives. |
| `odrl:uid` and descriptive metadata | RDF identity and metadata | metadata-only | Metadata does not change evaluation unless a profile says otherwise. |

## 5. Rule Mapping

| ODRL source | Canonical RL2 | Disposition |
|---|---|---|
| `odrl:Permission` | `rl2:Privilege` | normalized |
| `odrl:Prohibition` | `rl2:Prohibition` | normalized |
| action-bearing `odrl:Duty` | Achievement `rl2:Duty` | clarified |
| `odrl:duty` from Permission | `rl2:prerequisiteDuty` | normalized |
| `odrl:obligation` from Policy | independent `rl2:Duty` clause | normalized |
| `odrl:remedy` from Prohibition | none | rejected |
| `odrl:consequence` from Duty | none | rejected |
| `odrl:failure` | none | rejected |

The common fields map as follows:

| ODRL field | RL2 field | Rule |
|---|---|---|
| `odrl:target` | `rl2:object` | Exactly one target after atomization. |
| `odrl:action` | `rl2:action` or `rl2:prohibitedAction` | The action is an `rl2:Action`. |
| Rule `odrl:assignee` | `rl2:subject` | The party whose requested conduct or performance is governed. |
| Rule `odrl:assigner` | Offer or Agreement `rl2:grantor`; Set provenance metadata | A Rule-local assigner must agree with the containing policy after normalization. A Set has no operative grantor field. |
| Duty beneficiary | `rl2:counterparty` | Defaults to the Permission assigner only when the ODRL functional-role inheritance rule applies unambiguously. |
| `odrl:constraint` | `rl2:condition` | Only constraints governing Rule applicability map directly. |

ODRL Duty fulfillment depends on application state and action performance. RL2 makes this
interpretation explicit. An imported action-bearing Duty is an Achievement Duty whose qualifying
evidence must identify its subject, action, and object. A translation profile may additionally
map source constraints to `postCondition` or `dutyWindow`. An importer does not infer those roles
from vocabulary names alone.

ODRL has no native Maintenance Duty. A source rule maps to `rl2:invariant` only under a declared
profile interpretation establishing that it requires a state to hold rather than an action to
occur.

## 6. Parties, Assets, and Actions

| ODRL source | RL2 result | Disposition |
|---|---|---|
| `odrl:Party` | `rl2:Agent` | normalized |
| `odrl:PartyCollection` | profile-defined agent-set fact or expansion | profile-dependent |
| `odrl:Asset` | `rl2:Asset` | normalized |
| `odrl:AssetCollection` with explicit members | `rl2:AssetCollection` and direct `rl2:member` | normalized |
| Collection `odrl:source` | profile resolver input | profile-dependent |
| `odrl:Action` | `rl2:Action` | normalized |
| `odrl:includedIn` | `rl2:includedIn` | exact |
| `odrl:implies` | none | rejected |

ODRL functions other than the core assigner/assignee roles—including attributing, consenting,
compensating, informing, and tracking parties—require a profile mapping to explicit RL2 parties,
conditions, or evidence selectors. They are not copied as uninterpreted evaluator inputs.

Because ODRL identifies a profile by IRI but RL2 requires a minimum compatible version,
`TranslationConfiguration` must supply that version and the profile's term mappings. An absent or
unsupported mapping yields `UnsupportedProfile`.

## 7. Constraints

An ODRL Constraint maps to one `rl2:AtomicConstraint` only when its left operand, value type,
operator, and resolution rule are supported by the selected profile.

| ODRL operator or form | RL2 result | Disposition |
|---|---|---|
| `eq`, `neq`, `lt`, `lteq`, `gt`, `gteq` | corresponding comparison operator | exact after datatype normalization |
| `isAnyOf`, `isAllOf`, `isNoneOf` | corresponding set operator | exact when a finite right operand maps to an inline `rl2:ValueSet` |
| `isA` | `rl2:isA` | profile-dependent; hierarchy and closure must be finite and declared |
| `hasPart`, `isPartOf` | profile operator | profile-dependent |
| `odrl:and` | `rl2:and` | normalized |
| `odrl:or` | `rl2:or` | normalized |
| `odrl:xone` | `rl2:xone` | normalized |
| `odrl:andSequence` | none | rejected; RL2 conditions have no evaluation-order semantics |
| `odrl:rightOperandReference` | `rl2:rightOperandRef` | clarified; the referenced runtime value must have a declared RL2 resolution rule |
| action, asset, or party `odrl:refinement` | component condition | profile-dependent |
| `odrl:unit`, datatype, or status annotations | typed RL2 value or metadata | clarified |

Several ODRL Common Vocabulary operands—such as purpose, spatial location, count, elapsed time,
and industry—are not magic core variables in RL2. A profile declares their value type and
`rl2:resolutionPath` into the immutable `WorldSnapshot`.

## 8. Conflict Strategy

ODRL defines `perm`, `prohibit`, and `invalid`, with `invalid` as its default when `odrl:conflict`
is absent. RL2 makes the strategy an explicit `EvaluationConfiguration` input:

| ODRL term | RL2 strategy |
|---|---|
| `odrl:perm` | `PermitOverrides` |
| `odrl:prohibit` | `ProhibitOverrides` |
| `odrl:invalid` or absent | `Invalid` |

This mapping preserves ODRL conflict behavior only when translated norms have equal RL2 priority.
ODRL has no corresponding numeric priority in its Core Model. A translation that introduces
priorities is therefore profile-dependent and must state how priority interacts with the source
conflict strategy.

If several translated policies declare incompatible ODRL conflict strategies, translation of the
combined PolicyUniverse is rejected unless `TranslationConfiguration` supplies and records one
explicit combining interpretation.

## 9. Offer and Agreement

An ODRL Offer maps to an RL2 Offer, but translation does not make it operative and does not infer
that any party accepted it. A caller that possesses explicit acceptance information may invoke:

```text
materialize(Offer, Acceptance) -> Agreement | Rejected(errors)
```

RL2 materialization assigns Agreement-local identifiers, preserves local references, and turns
action and state Promises into beneficiary-bearing Duties. Existing ODRL Permission,
Prohibition, and Duty rules are copied as proposed terms. An already accepted ODRL Agreement maps
directly to an RL2 Agreement and does not pass through materialization.

Assignment, delegation, amendment, revocation, and termination are not Offer acceptance. Core RL2
does not translate an ODRL action name such as `grantUse` or `nextPolicy` into an automatic policy
transformation.

## 10. Preservation and Rejection

For an `exact` or `normalized` mapping, evaluating the canonical RL2 result preserves the supported
ODRL permission/prohibition/duty outcome under the declared Request, snapshot interpretation, and
conflict strategy. For a `clarified` mapping, preservation is relative to the interpretation
recorded in `TranslationConfiguration`.

Translation fails rather than silently weakening a policy when it encounters:

- an unsupported Rule relation, Party function, failure relation, or logical operator;
- a profile term without supported semantics;
- an unresolved or cyclic inherited policy;
- an ODRL Duty whose applicability, fulfillment, deadline, or consequence cannot be assigned one
  canonical RL2 meaning; or
- compact values whose expansion conflicts with Rule-local values.

## 11. Why RL2 Adds Semantics

RL2 retains ODRL's Permission, Prohibition, Duty, Set, Offer, Agreement, Action, Asset, Party,
constraint, profile, action-inclusion, and conflict concepts. It adds four explicit elements
needed for reproducible evaluation:

1. a canonical RDF-to-AST projection;
2. a Request and immutable WorldSnapshot contract;
3. total condition and Duty-status semantics with attributed indeterminacy; and
4. an explained result containing the determining normative envelope.

Canonical RDF shapes, explicit validation, typed conditions, and total evaluation semantics also
make RL2 suitable for machine generation and independent interpretation. The claim is not that an
LLM should evaluate policy by prose reasoning; generated policy is accepted only after canonical
projection and validation.

## 12. Related Work

RL2 follows a substantial body of work on ODRL formalization and evaluation. Relevant starting
points include:

- the [ODRL Formal Semantics](https://w3c.github.io/odrl/formal-semantics/) work;
- Steyskal and Polleres, *Towards a Formal Semantics for ODRL Policies*;
- Pucella and Weissman, *A Formal Foundation for ODRL*;
- Fornara and Colombetti's work on operational semantics for ODRL;
- Makinson and van der Torre, *Input/Output Logics*; and
- the [ODRL Profile Best Practices](https://www.w3.org/community/reports/odrl/CG-FINAL-profile-bp-20240808.html).

The bibliography in `../docs/RL2_References.md` supplies full citations. These works motivate the
need for explicit interpretation but do not substitute for RL2 conformance vectors.
