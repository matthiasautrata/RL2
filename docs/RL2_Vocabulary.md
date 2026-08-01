# RL2 Vocabulary

**Version:** 0.7

## Status

This document is an informative index. The authoritative vocabulary and structural constraints
are `../spec/rl2.ttl` and `../spec/rl2-shacl.ttl`.

Namespace: `https://rl2.example/ontology#` (provisional)

## 1. Policy and Clause Classes

| Term | Meaning |
|---|---|
| `rl2:Policy` | Container for one or more clauses, with an optional applicability condition. |
| `rl2:Set` | Operative unilateral policy containing only Norms. |
| `rl2:Offer` | Proposed policy; the only policy form that may contain Promises. |
| `rl2:Agreement` | Operative policy with one grantor and one grantee, containing only Norms. |
| `rl2:Clause` | A Norm or Promise admissible as policy content. |
| `rl2:Norm` | Abstract superclass of operative normative clauses. |
| `rl2:Privilege` | Authorization for its subject to perform its action on its object. |
| `rl2:Prohibition` | Prohibition on its subject performing its prohibited action on its object. |
| `rl2:Duty` | Requirement to perform an action or maintain a condition. |
| `rl2:Promise` | Proposed commitment that may be materialized as a Duty upon Offer acceptance. |

`rl2:Promise` and `rl2:Norm` are disjoint. A Set or Agreement cannot contain a Promise. A Duty's
optional `rl2:counterparty` identifies its beneficiary; the vocabulary does not require a second
node to restate the beneficiary-facing relation.

## 2. Policy Properties

| Term | Domain → range | Meaning |
|---|---|---|
| `rl2:clause` | Policy → Clause | Direct policy content. |
| `rl2:grantor` | Policy → Agent | Party granting or proposing the terms. |
| `rl2:grantee` | Policy → Agent | Party receiving or accepting the terms. |
| `rl2:condition` | Policy or Norm → Condition | Applicability guard. |
| `rl2:requiresProfile` | Policy → Profile | Required profile and version. |

An Agreement requires exactly one grantor and one grantee; an Offer may state them; a Set carries
neither. A Policy requires at least one clause and has at most one policy-level condition.

## 3. Conduct Norms

| Term | Use |
|---|---|
| `rl2:subject` | Agent bearing a Norm. |
| `rl2:counterparty` | Beneficiary or other Agent to whom a Duty is owed. |
| `rl2:action` | Action of a Privilege or Achievement Duty. |
| `rl2:prohibitedAction` | Action of a Prohibition. |
| `rl2:object` | Asset or resource governed by a Norm or Promise. |
| `rl2:priority` | Integer on a Privilege or Prohibition, used before conflict-strategy resolution; default `0`. |
| `rl2:prerequisiteDuty` | Duty that must be Fulfilled before its owning Privilege contributes a permit. |

A Privilege and Prohibition each have exactly one subject, action, and object. An attached
prerequisite Duty is not also a direct policy clause. The same Duty node may be shared by several
Privileges.

## 4. Duty Forms

Exactly one Duty form is valid:

| Form | Required content | Optional content | Excluded content |
|---|---|---|---|
| Achievement | `rl2:action` | `rl2:postCondition`, `rl2:dutyWindow` | `rl2:invariant` |
| Maintenance | `rl2:invariant` | `rl2:dutyWindow` | `rl2:action`, `rl2:postCondition` |

Every Duty also has one subject and one object. `rl2:condition` controls applicability;
`rl2:postCondition` tests the result at an Achievement witness; `rl2:invariant` is the maintained
state. These properties are not interchangeable.

`rl2:DutyWindow` is one finite half-open interval. It has exactly one timezone-qualified
`rl2:startInclusive` and `rl2:endExclusive`, with start before end.

The derived Duty states are `rl2:Pending`, `rl2:Active`, `rl2:Fulfilled`, and `rl2:Violated`.
They are evaluator results and comparison values, not asserted Duty properties.

## 5. Promises

| Term | Meaning |
|---|---|
| `rl2:promisor` | Agent making the proposed commitment. |
| `rl2:promisee` | Intended beneficiary. |
| `rl2:promisedAction` | Action content; materializes as an Achievement Duty. |
| `rl2:promisedState` | Condition content; materializes as a Maintenance Duty. |
A Promise has exactly one content property. Its derived states are `Pending`, `Fulfilled`, and
`Violated`; Promises do not use `Active`. Policy RDF does not assert Promise status.

## 6. Agents, Actions, and Assets

| Term | Meaning |
|---|---|
| `rl2:Agent` | Person, organization, service, or other policy party. |
| `rl2:Action` | Profile-defined action individual. |
| `rl2:includedIn` | Transitive relation from a narrower action to a broader action. |
| `rl2:Asset` | Resource governed by a policy. |
| `rl2:AssetCollection` | Asset whose direct members may be matched. |
| `rl2:member` | Direct collection membership; core matching does not recursively flatten nested collections. |

Agent matching is exact in the core. Group, role, and organizational relationships are expressed
by profile-defined facts and conditions.

## 7. Conditions

| Term | Meaning |
|---|---|
| `rl2:Condition` | Abstract condition. |
| `rl2:AtomicConstraint` | One typed comparison. |
| `rl2:LogicalConstraint` | Combination of subconditions. |
| `rl2:leftOperand` | Value to resolve. |
| `rl2:constraintOperator` | Comparison or logical operator. |
| `rl2:rightOperand` | Literal comparison value. |
| `rl2:rightOperandRef` | IRI constant or dynamic `RuntimeReference` used as the comparison value. |
| `rl2:rightOperandSet` | Inline `rl2:ValueSet` used by a set comparison. |
| `rl2:valueMember` | Literal or IRI member of a ValueSet. |
| `rl2:operand` | Child of a LogicalConstraint. |
| `rl2:targetNorm` | Duty or Offer-local Promise queried by a status operand. |

An AtomicConstraint has exactly one left operand, one comparison operator, and exactly one of
`rightOperand`, `rightOperandRef`, or `rightOperandSet`. A LogicalConstraint has one logical operator. `not` has one
operand; `and`, `or`, and `xone` have at least two.

Comparison operators are `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `isA`, `isAnyOf`, `isAllOf`, and
`isNoneOf`. Logical operators are `and`, `or`, `xone`, and `not`.

## 8. Snapshot Operands

| Term | Meaning |
|---|---|
| `rl2:LeftOperand` | Typed value resolved from the Request, WorldSnapshot, or a defined status query. |
| `rl2:resolutionPath` | Canonical scoped fact key declared by a profile operand. |
| `rl2:RuntimeReference` | Dynamic right-side value. |
| `rl2:currentDateTime` | `WorldSnapshot.evaluationTime`. |
| `rl2:currentAgent` | Requesting agent, for a right-operand reference. |
| `rl2:obligationStateOperand` | Derived status of the Duty named by `targetNorm`. |
| `rl2:promiseStateOperand` | Derived status of an Offer-local Promise. |

Every profile-defined LeftOperand has one `resolutionPath`. Canonical roots are `agent`, `asset`,
`context`, `state`, `request`, and `global`; the information model defines their scopes.

## 9. Evidence

Evidence is a typed part of the WorldSnapshot rather than authored RDF vocabulary. It records an
observed action with an identity, occurrence time, actor, action, object, and attribution. Core
uses it to derive Achievement Duty and action Promise status. The information model defines exact
selection behavior.

Policies that depend on externally established events or approvals use profile-defined facts.
Their snapshot scopes, validity intervals, and attribution requirements make the relevant result
explicit without embedding an event-query language in policy RDF.

## 10. Profiles

`rl2:Profile` identifies a domain vocabulary. `rl2:profileVersion` is a semantic-version string.
A required profile is compatible when the evaluator supports the same major version at least as
high as the required version.

Profiles define actions, operands, ranges, evidence interpretations, and provenance rules. The illustrative
privacy profile is in `../spec/profiles/`; it supplies policy vocabulary, not a representation of
legal compliance.

## 11. Canonicality

SHACL validation is part of ingestion. Important canonicality constraints include:

- one authored shape for each Duty form;
- one policy placement for an attached Duty;
- no Promise in a Set or Agreement;
- one right-operand representation per AtomicConstraint;
- local Promise targets that can be deterministically rewritten during materialization; and
- explicit paths for profile-defined operands.

Validation establishes structural conformance. The information model and formal semantics define
the remaining typing, bounds, evaluation, and diagnostic behavior.
