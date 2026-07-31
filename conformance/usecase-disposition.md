# Use-Case Disposition for SCOPE-2

**Status:** Initial classification complete; encoding migration pending.

**Invariant:** Preserve every business scenario and original use-case number. A scenario may move
to future workflow work, but it is not silently deleted because its current RDF is operational.

## Summary

| Disposition | Count |
|---|---:|
| Core conformance; current intent is already snapshot-oriented | 13 |
| Core conformance; encoding must be rewritten | 26 |
| RL2 language-extension conformance | 11 |
| Future workflow/protocol | 2 |
| **Total** | **52** |

`rewrite` means that the business rule remains in core while mutable lifecycle, automatic side
effects, or event-log assumptions are replaced by facts and evidence in the supplied world
snapshot.

## Complete Disposition

| # | Use case | Disposition | Required SCOPE-2 adjustment |
|---:|---|---|---|
| 1 | Pay-to-Play | Core · rewrite | Use attributed payment evidence instead of stored duty lifecycle |
| 2 | Team License | Core · rewrite | Use entitlement/payment evidence instead of shared duty state |
| 3 | Break Glass | Extension | Keep Liability; treat break-glass activation as attributed evidence |
| 4 | Fire Alarm | Core · rewrite | Treat alarm occurrence as snapshot evidence, not a trigger protocol |
| 5 | Wire Transfer SoD | Core · rewrite | Use transfer-scoped, actor-attributed preparation and approval evidence |
| 6 | Check Signing SoD | Core · rewrite | Use check-scoped actor evidence instead of mutable norm state |
| 7 | Ethics Approval | Core · rewrite | Supply attributed approval and expiry evidence; omit orchestration |
| 8 | Data Stewardship | Extension | Derive Promise status from evidence rather than stored Promise state |
| 9 | GDPR Erasure | Core · rewrite | Use erasure-request and deletion evidence; omit Case lifecycle |
| 10 | Audit Trail | Core · rewrite | Use an audit-enabled fact instead of another Duty's stored status |
| 11 | Data Freshness Promise | Extension | Derive status from freshness evidence/time; omit ticket automation |
| 12 | Schema Evolution | Core · rewrite | Supply schema-change and notice facts; omit event-trigger machinery |
| 13 | Quality Circuit Breaker | Core · rewrite | Evaluate quality facts directly; omit circuit-breaker state machine |
| 14 | Step-Up Authentication | Core · rewrite | Treat authentication level as request/snapshot data |
| 15 | Chinese Wall | Core · rewrite | Supply publication status; omit event-log transition semantics |
| 16 | Concurrent Seats | Core · rewrite | Evaluate supplied seat facts; omit counters, CAS, and admission commit |
| 17 | Trial Period | Core · rewrite | Derive from trial facts and evaluation time; omit deactivation machine |
| 18 | Internal Use Only | Core | Retain basic restriction |
| 19 | No Redistribution | Core · rewrite | Keep prohibition/duty; treat downstream compliance as evidence |
| 20 | Derived Data Restriction | Core | Retain conditional restriction over supplied classification facts |
| 21 | Usage Metering | Core · rewrite | Read usage total from snapshot; omit counter mutation |
| 22 | Display vs Non-Display | Core | Retain use-type conditions |
| 23 | Pass-Through Terms | Core · rewrite | Keep downstream duty; omit agreement-generation workflow |
| 24 | Purpose Restriction | Core | Retain purpose allow-list |
| 25 | Geographic Restriction | Core | Retain jurisdiction condition |
| 26 | Legal Review Gate | Core · rewrite | Keep pure Offer transformation; omit review workflow |
| 27 | Approval Revocation | Extension | Keep Power/Liability meaning; externalize policy mutation |
| 28 | Data Retention Limit | Core · rewrite | Derive duty status from deadline and deletion evidence |
| 29 | Anonymization Required | Core · rewrite | Gate use on anonymization evidence, not stored duty state |
| 30 | No ML Training | Core | Retain direct prohibition |
| 31 | Multi-Level Approval | Core · rewrite | Evaluate attributed approvals; omit approval orchestration |
| 32 | Connector Certification | Core | Retain certification validity facts |
| 33 | Data Sovereignty | Extension | Keep Claim/Power semantics; externalize monitoring and revocation effects |
| 34 | Volume Limit | Core · rewrite | Read period total from snapshot; omit counter mutation |
| 35 | Logging and Notification | Core · rewrite | Determine duties from supplied evidence; omit dispatch workflow |
| 36 | Deletion After Use | Core · rewrite | Use completion/deletion evidence and time; omit triggers |
| 37 | Time Window Access | Core | Retain evaluation-time condition |
| 38 | Claim and Duty Correlation | Extension | Keep correlative semantics; remove Requirement/Case projection |
| 39 | Immunity from Termination | Extension | Keep Immunity; externalize termination effect |
| 40 | Power to Grant Access | Extension | Keep Power/Liability; externalize privilege creation and audit logging |
| 41 | Liability Exposure | Extension | Keep normative position; externalize resulting policy changes |
| 42 | No-Claim Inference | Extension | Retain Hohfeldian non-inference clarification |
| 43 | Exclusive License | Core | Retain `xone` semantics |
| 44 | Multi-Certification | Core | Retain `isAllOf` semantics |
| 45 | Negated Condition | Core | Retain `not` semantics |
| 46 | Role Hierarchy | Core | Retain `isA` semantics |
| 47 | Asset Collection Access | Core | Retain collection membership semantics |
| 48 | Compliance Attestation | Core · rewrite | Treat Assertion/evidence as snapshot data; omit publication lifecycle |
| 49 | Policy Versioning | Core · rewrite | Select policy universe through evaluation configuration; omit Case binding |
| 50 | Runtime Evaluation | Future workflow | Retain as request/result/Case protocol research, not core conformance |
| 51 | Fulfillment Evidence | Future workflow | Extract evidence meaning to core; retain records/signatures/lifecycle as future work |
| 52 | SLA Credit Clause | Extension | Keep Promise and pure materialization; omit runtime state/ID machinery |

## Migration Gate Per Case

A case becomes `migrated` only when it has:

1. a canonical policy graph;
2. an explicit request;
3. an immutable world snapshot;
4. a hand-derivable expected result, normative envelope, duties, and diagnostics;
5. an ODRL migration note where an ODRL representation exists;
6. passing structural validation.
