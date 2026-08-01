# RL2 Primer

**Version:** 0.7

## 1. Why RL2

ODRL 2.2 provides a widely used RDF vocabulary for permissions, prohibitions, duties, parties,
assets, actions, and constraints. It deliberately leaves important parts of policy interpretation
to profiles and implementations. In particular, two systems can reasonably disagree about which
facts a constraint reads, when a Duty is fulfilled, or how several applicable policies combine.

RL2 is a candidate extension and clarification. It retains the recognizable ODRL policy model and
adds a deterministic evaluation contract:

```text
Eval(PolicyUniverse, Request, WorldSnapshot, EvaluationConfiguration)
    -> EvaluationResult
```

The same four inputs produce the same explained result. Policy evaluation performs no network
access, persistence, scheduling, or enforcement.

RL2 is designed for machine generation as well as human review. It has one canonical RDF form for
each supported proposition, structural validation, typed conditions, and total evaluation rules.
An LLM may propose a policy, but the policy is accepted only after the same validation and
evaluation used for any other input.

## 2. Policies and Clauses

RL2 defines three policy forms:

| Form | Meaning |
|---|---|
| `rl2:Set` | An operative collection of Norms. |
| `rl2:Offer` | Proposed terms; it contributes no normative result before acceptance. |
| `rl2:Agreement` | Operative terms between an identified grantor and grantee. |

The operative conduct norms are:

| Norm | Meaning |
|---|---|
| `rl2:Privilege` | The subject is authorized to perform an action on an asset. |
| `rl2:Prohibition` | The subject is forbidden to perform an action on an asset. |
| `rl2:Duty` | The subject is required to perform an action or maintain a condition. |

A Duty may name a `counterparty`, identifying the beneficiary to whom performance is owed. This
contains the useful relational information commonly expressed as the correlative claim; RL2 does
not require a second node that repeats the Duty's content.

`rl2:Promise` is a proposed commitment in an Offer. It is not an operative Norm. Promises become
Duties when a caller explicitly materializes the Offer as an Agreement.

## 3. A Simple Policy

The following Set authorizes research use of a dataset when the request context declares a
research purpose.

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix ex:  <https://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:researchPolicy a rl2:Set ;
    rl2:clause ex:researchUse .

ex:researchUse a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:purpose ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "research"
    ] .

ex:Researcher a rl2:Agent .
ex:use a rl2:Action .
ex:Dataset a rl2:Asset .
ex:purpose a rl2:LeftOperand ;
    rdfs:range xsd:string ;
    rl2:resolutionPath "context.purpose" .
```

The policy alone does not answer an access question. Evaluation also receives a Request naming
the requesting agent, action, and asset; a WorldSnapshot containing the purpose value; and an
EvaluationConfiguration selecting a conflict strategy, an evidence-admissibility rule, and finite
bounds.

## 4. Matching and Applicability

A norm is relevant when its subject, action, and object match the Request. Action matching uses
the finite `rl2:includedIn` hierarchy. Subject matching is exact identifier equality against the
authored `rl2:subject`, direct membership in an `rl2:AgentCollection`, or the sentinel
`rl2:anyAgent`, which matches every requesting agent; object matching is the same shape against
`rl2:object`, with equality, direct `rl2:AssetCollection` membership, or the sentinel
`rl2:anyAsset`. A policy over an open population (any researcher, any employee, any asset tagged a
given way) is authored with a sentinel subject or object and a condition over `agent.*`/`asset.*`
facts that delimits who or what actually qualifies; membership in a collection is always direct,
never transitively closed. A missing population-defining fact yields `Indeterminate`, never a
silent match or non-match.

`rl2:condition` is an applicability guard. It answers whether a Policy or Norm applies in the
current environment. It does not say whether a Duty has been performed.

Conditions use typed atomic comparisons and the logical operators `and`, `or`, `xone`, and `not`.
They evaluate in three-valued logic:

- `True` means the condition holds;
- `False` means it does not hold; and
- `Unknown` means a required value was missing, invalid, conflicting, or otherwise unresolved.

Errors remain attributed to the affected clause. Missing data therefore does not silently become
false or depend on an implementation default.

## 5. WorldSnapshot

The immutable WorldSnapshot contains:

- one evaluation time;
- typed, scoped facts; and
- attributed evidence of observations or occurrences.

Profile-defined operands declare a canonical `rl2:resolutionPath`, such as
`agent.department`, `asset.classification`, or `context.purpose`. The path addresses a semantic
input; it is not permission to traverse a host object or perform live I/O.

An implementation may assemble a snapshot from databases, credentials, APIs, or logs before
evaluation. For a given snapshot, however, resolution is fixed: equal assertions agree, unequal
single-valued assertions conflict, invalid values are reported, and absent values are missing.

## 6. Duties

RL2 has two canonical Duty forms. The form is determined structurally; no mode flag is authored.

### 6.1 Achievement Duty

An Achievement Duty requires an `rl2:action` and may have an `rl2:postCondition`. It is fulfilled
by qualifying evidence that the Duty subject performed the action on the Duty object. The
postcondition, if present, must hold at that witness.

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix ex:  <https://example.org/> .

ex:noticePolicy a rl2:Set ;
    rl2:clause ex:noticeDuty .

ex:noticeDuty a rl2:Duty ;
    rl2:subject ex:Controller ;
    rl2:counterparty ex:DataSubject ;
    rl2:action ex:notify ;
    rl2:object ex:DataSubject .

ex:Controller a rl2:Agent .
ex:DataSubject a rl2:Agent .
ex:notify a rl2:Action .
```

Without a finite `rl2:dutyWindow`, an unsatisfied Achievement Duty remains `Active`; passage of
time alone cannot make it violated. With a window, it becomes `Violated` once the window ends
without qualifying evidence.

### 6.2 Maintenance Duty

A Maintenance Duty has one `rl2:invariant` and no action. It requires a state to hold. A finite
half-open `rl2:dutyWindow` represents a warranty-like period: the invariant must hold throughout
`[startInclusive, endExclusive)`.

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ex:  <https://example.org/> .

ex:availabilityPolicy a rl2:Agreement ;
    rl2:grantor ex:Provider ;
    rl2:grantee ex:Customer ;
    rl2:clause ex:availabilityDuty .

ex:availabilityDuty a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Customer ;
    rl2:object ex:Service ;
    rl2:invariant [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:availability ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperand "0.999"^^xsd:decimal
    ] ;
    rl2:dutyWindow [
        a rl2:DutyWindow ;
        rl2:startInclusive "2026-01-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2026-02-01T00:00:00Z"^^xsd:dateTimeStamp
    ] .

ex:Provider a rl2:Agent .
ex:Customer a rl2:Agent .
ex:Service a rl2:Asset .
ex:availability a rl2:LeftOperand ;
    rdfs:range xsd:decimal ;
    rl2:resolutionPath "asset.availability" .
```

A finite Maintenance Duty is `Pending` before the window, `Active` while the invariant has held
so far, `Violated` upon contrary evidence, and `Fulfilled` after complete successful coverage.
Without a finite window it may be Active or Violated, but cannot be Fulfilled.

## 7. Prerequisite Duties

A Privilege may refer to one or more `rl2:prerequisiteDuty` values. Each applicable prerequisite
must already be Fulfilled before that Privilege contributes a permit. Multiple prerequisites are
conjunctive.

The attached Duty is not also a top-level policy clause. One shared Duty node may gate several
Privileges, so one fulfillment result is reused in the same way as a shared ODRL Duty.

RL2 deliberately does not make every Duty block every request. An independent Duty is reported in
the normative result but does not change the access decision. Ongoing enforcement and post-use
scheduling are outside pure evaluation.

## 8. Conflict Resolution and Explanation

Derivation first produces an attributed envelope containing applicable permits, prohibitions,
obligations, and indeterminate clauses. Resolution then applies an explicit strategy:

- `PermitOverrides`;
- `ProhibitOverrides`; or
- `Invalid` for an unresolved permit/prohibit conflict.

Integer priorities are considered before the strategy. The result records the determining
clauses, Duty and Promise statuses, and causal diagnostics. Resolution never depends on RDF
statement order.

## 9. Offers and Promises

An Offer proposes terms but is not itself operative. Acceptance is an explicit pure
transformation:

```text
materialize(Offer, Acceptance)
    -> Materialized(Agreement, sourceMap) | Rejected(errors)
```

The Acceptance supplies the parties and output identifiers needed to make the result
deterministic. A Promise is structurally a proposed Duty, so crystallization unwraps and rebinds
it rather than re-deriving a Duty from separate fields: an action Promise becomes an Achievement
Duty; a state Promise becomes a Maintenance Duty. The Promise's promisor becomes the Duty subject
and its promisee (required on every Promise) becomes the counterparty; an object left unbound on
the Promise is taken from the Acceptance. No Promise remains in the Agreement.

This transformation does not model negotiation, signatures, authorization to accept, storage, or
delivery. Those are protocol concerns. General assignment, delegation, amendment, revocation,
and termination also require a separately specified normative transformation and are not inferred
from action names.

## 10. ODRL 2.2 Migration

ODRL input is translated to canonical RL2 before evaluation. The mapping classifies each source
construct as exact, normalized, clarified, profile-dependent, rejected, or metadata-only.

The common correspondence is direct:

| ODRL 2.2 | RL2 |
|---|---|
| Permission | Privilege |
| Prohibition | Prohibition |
| action-bearing Duty | Achievement Duty with explicit evidence semantics |
| Permission duty | attached prerequisite Duty |
| Policy obligation | independent Duty |
| Set, Offer, Agreement | corresponding RL2 policy form |
| Constraint | typed AtomicConstraint or LogicalConstraint |

Where ODRL leaves a material choice open, translation requires an explicit configuration or
profile. Unsupported failure relations, ordered constraints, unresolved inheritance, and unknown
profile terms are rejected rather than ignored. See
[ODRL 2.2 Migration](../spec/RL2_ODRL_Mapping.md).

## 11. Profiles

Profiles provide domain actions, operands, value types, evidence interpretations, resolution
paths, and provenance requirements. A policy declares every required profile and version. The evaluator
rejects an unknown or incompatible profile.

Profiles extend vocabulary; they do not replace the core truth algebra, conflict handling, or
snapshot-resolution rules with opaque callbacks. This keeps profile-based policies portable.

## 12. Implementation Boundary

RL2 specifies observable policy meaning. It does not prescribe an evaluator architecture. A
conforming implementation may interpret the canonical AST directly, compile an IR, generate
code, or use relational indexes, provided it produces the same result for every conformance
vector.

Persistent cases, event transport, source connectors, retries, commits, distributed coordination,
enforcement, and verified implementation toolchains are possible companion work. They are not
needed to state what an RL2 policy means.

## 13. Reading Next

- [Information Model](../spec/RL2_Model.md) defines the evaluation inputs and outputs.
- [Formal Semantics](../spec/RL2_Semantics.md) defines the evaluator.
- [ODRL 2.2 Migration](../spec/RL2_ODRL_Mapping.md) defines translation.
- [Use Cases](../conformance/usecases/) demonstrate policy patterns.
- [Vocabulary](RL2_Vocabulary.md) summarizes the RDF terms.
