# Possible Follow-on Work

RL2 0.7 is limited to the policy language, its pure evaluation semantics, ODRL 2.2 migration, and
conformance. The following topics may justify separate specifications or implementation projects.
They do not define RL2 behavior. `../spec/RL2_Scope.md` §Out of Scope is the normative enumeration
of what a conforming evaluator does not have to do; the topics below are candidate follow-on work
in that space, not a restatement of it.

## Normative instruments

A companion language could define pure transformations of a policy universe:

```text
apply(PolicyUniverse, Instrument, Invocation, WorldSnapshot)
    -> Applied(PolicyUniverse)
     | Rejected(reason)
     | Indeterminate(errors)
```

Candidate operations include assignment, delegation, amendment, revocation, termination, and
second-order guarantees or suretyship.
Such a specification would need to define the authorized actor, target, permitted scope,
recipient, consent requirements, delegation depth, and transformation result. It could recover
the useful distinction between prohibited conduct and an ineffective normative act: a termination
may be forbidden yet effective, whereas an immunity makes the attempted termination ineffective.

## Protocol and enforcement

Implementations may standardize request transport, evidence submission, evaluation receipts,
audit records, scheduling, retries, enforcement, and distributed coordination. These mechanisms
must preserve the inputs and outputs of the pure RL2 evaluation contract.

## Reference evaluator and verification

A reference project could implement canonical RDF projection, validation, evaluation, explanation,
and ODRL import. Mechanized proofs of termination, determinism, and selected semantic properties
would be useful, but RL2 does not prescribe an implementation language, intermediate
representation, or proof assistant.

## Additional profiles

Potential profiles include privacy and data protection, licensing, employment, organizational
roles, quantitative usage control, and trusted evidence vocabularies. Profiles should add domain
terms without introducing alternative encodings for core propositions.
