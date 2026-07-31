# Semantic Conformance Vectors

This directory will contain evaluator-independent examples of the normative `Eval` contract.
Vectors are specification artifacts, not outputs captured from one implementation.

Component-level vectors may also isolate a normative helper when that makes an error boundary
unambiguous. [WorldSnapshot Resolution Vectors](snapshot-resolution.md) cover S2-C1 identity,
scope, validity, conflict, evidence tie, and admissibility rules. [Duty and Promise Status
Vectors](duty-status.md) cover S2-C2 boundaries, interval coverage, postconditions, invariants,
Promise projection, and status derivation. [Duty Attachment Decision Vectors](duty-attachment.md)
cover S2-C3 prerequisite gating, independent-duty isolation, and multiple-grant locality.

Each vector must identify:

```text
id
purpose
policy graph
canonical AST expectation or digest
request
world snapshot
evaluation configuration
expected decision
expected normative envelope
expected duty/promise statuses
expected diagnostics
```

The first vectors should cover:

1. definite Permit;
2. definite Prohibition/Deny;
3. missing operand causing attributed Indeterminate;
4. priority conflict under each core strategy;
5. Achievement duty evidence and deadline boundaries;
6. Maintenance duty over a finite evidence interval;
7. unrelated Duty isolation;
8. pure Offer→Agreement transformation.

Protocol replay and Case lifecycle are tested only in a future companion suite.
