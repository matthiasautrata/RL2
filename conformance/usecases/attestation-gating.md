# Attestation Gating

## Scenario

A data-governance agreement requires a data processor to hold a current conformance attestation.
That same attestation is also declared, at the agreement level, as a prerequisite for every access
privilege the agreement grants: reading and exporting the governed dataset both wait on it.

## Why it matters

`ex:attestConformance` plays both roles at once: it is an independent `rl2:clause` of the Agreement
(a standing obligation, reported on its own regardless of any request), and it is the object of the
Agreement's own `rl2:prerequisiteDuty` (gating every Privilege clause of that Agreement, not just
one). One Duty node, one derived status, two effects: its own obligation atom when a request's
action matches it directly, and a gating effect on `readPrivilege`/`exportPrivilege` regardless of
the requested action, because prerequisite gating reads the Duty's derived status directly and does
not filter by `matchesRequest`. The status itself — `dutyStatuses[ex:attestConformance]` — is part of
every `EvaluationResult` for this policy, independent of which action was requested, because
`deriveDutyStatuses` is total over the policy universe and takes no `Request` argument.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Regulator a rl2:Agent .
ex:DataProcessor a rl2:Agent .
ex:GovernedDataset a rl2:Asset .
ex:read a rl2:Action .
ex:export a rl2:Action .
ex:attest a rl2:Action .

ex:attestConformance a rl2:Duty ;
    rl2:subject ex:DataProcessor ;
    rl2:counterparty ex:Regulator ;
    rl2:action ex:attest ;
    rl2:object ex:GovernedDataset ;
    rl2:dutyWindow [
        a rl2:DutyWindow ;
        rl2:startInclusive "2026-01-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2027-01-01T00:00:00Z"^^xsd:dateTimeStamp
    ] .

ex:readPrivilege a rl2:Privilege ;
    rl2:subject ex:DataProcessor ; rl2:action ex:read ; rl2:object ex:GovernedDataset .

ex:exportPrivilege a rl2:Privilege ;
    rl2:subject ex:DataProcessor ; rl2:action ex:export ; rl2:object ex:GovernedDataset .

ex:dataGovernanceAgreement a rl2:Agreement ;
    rl2:grantor ex:Regulator ;
    rl2:grantee ex:DataProcessor ;
    rl2:prerequisiteDuty ex:attestConformance ;
    rl2:clause ex:attestConformance, ex:readPrivilege, ex:exportPrivilege .
```

## Request and snapshot

Three snapshots at the same policy, varying only evaluation time and attestation evidence. Two
requests are evaluated against each: `(DataProcessor, read, GovernedDataset)` and, where noted,
`(DataProcessor, attest, GovernedDataset)`.

**Fulfilled.** Evaluation time `2026-06-01T00:00:00Z` (inside the window). The snapshot carries
qualifying, admissible Evidence that `DataProcessor` performed `attest` on `GovernedDataset` inside
the window.

**Pending.** Evaluation time `2025-06-01T00:00:00Z` — before the window's declared start.

**Indeterminate.** Evaluation time `2026-06-01T00:00:00Z` (inside the window), but the snapshot
carries two equally-admissible, equally-trusted Evidence records that disagree on whether the
qualifying `attest` occurred — a genuine conflict in the evidentiary fact, not a missing one.

## Expected result

**Fulfilled:** `dutyStatuses[ex:attestConformance] = Known(Fulfilled)`. For the `read` request, the
prerequisite check reads this status directly (not gated by `matchesRequest`), so the decision is
`Permit`. For the `attest` request, the independent-clause branch applies (its `matchesRequest`
succeeds — the requested action equals the Duty's own action), and, since `ex:attestConformance` has
no applicability `condition` of its own, the envelope carries `obligate(ex:attestConformance,
ex:dataGovernanceAgreement)` regardless of the Duty's own fulfillment (an owed obligation is still
reported once it is owed); the decision for that request is `NotApplicable`, since no Privilege
clause matches action `attest`.

**Pending:** `dutyStatuses[ex:attestConformance] = Known(Pending)` (evaluation time precedes the
declared window). `fulfilledResult` is `False`; with no applicability condition of its own the
prerequisite result is `kOr(notResult(True), False) = False`, so `accessResult` for both
`readPrivilege` and `exportPrivilege` is a definite `False` — no atom for either is placed in the
envelope at all (a definite `False`, not `Unknown`, is a silent absence, not an `indeterminate`
atom). With no permit, prohibition, or indeterminate atoms in the envelope, `resolveDecision` yields
`NotApplicable` under all three combining strategies (`ProhibitOverrides`, `PermitOverrides`,
`Invalid`) — there being no matching rule is not the same as an explicit `Deny`, and RL2 has no
implicit denial. The decision for the `read` request is `NotApplicable`, not `Deny`.

**Indeterminate:** the conflicting Evidence yields `dutyStatuses[ex:attestConformance] =
IndeterminateStatus(causes)`. `fulfilledResult` is `Unknown`; the prerequisite result is
`kOr(notResult(True), Unknown) = Unknown`, so `accessResult(readPrivilege) = kAnd(True, Unknown) =
Unknown`, placing `indeterminate(ex:readPrivilege, ex:dataGovernanceAgreement, causes)` in the
envelope (likewise for `exportPrivilege`). Resolving this against the empty-choice summary
(`NotApplicable`) and the activated-choice summary (`Permit`, since no Prohibition clause exists to
override it under any strategy) yields two distinct reachable decisions, so `resolveDecision` returns
`Indeterminate` for the `read` request, regardless of the configured combining strategy.
