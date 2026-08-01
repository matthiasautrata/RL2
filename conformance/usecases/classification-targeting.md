# Classification-Based Targeting

## Scenario

A data-governance policy permits any agent to read any asset classified as home-loan data. The
policy names neither an agent nor an asset: the classification tag stated as an asset-scoped fact
selects the population. Every such read also carries a logging obligation: whoever is granted
access must log that access against that same asset, as a companion of the grant rather than a
precondition to it.

## Why it matters

This is tag/classifier-driven targeting, not enumerated membership: `rl2:subject rl2:anyAgent` and
`rl2:object rl2:anyAsset` match unconditionally, and the `asset.classification eq ex:HomeLoan`
condition delimits which requests the Privilege actually reaches. `ex:homeLoanAccessLogDuty` is
attached to `ex:homeLoanReadPrivilege` via `rl2:consequentDuty`, not as an independent `rl2:clause`
of the Policy: it never contributes an independently-matched obligation of its own, and its own
`rl2:subject`/`rl2:object` sentinels are never themselves checked against `dutyStatus` or placed in
an envelope — a template Duty has no standalone status (`RL2_Semantics.md` §Duty Template Binding).
It fires only as a consequence of the Privilege granting, and only then is it turned into a
concrete, sentinel-free occurrence: `bind()` replaces `rl2:anyAgent` with the requesting agent and
`rl2:anyAsset` with the requested asset before the obligation is placed in the envelope. This is the
F-01 fix in miniature — a Duty may carry sentinels, but no sentinel ever reaches an emitted envelope
atom or a `dutyStatus` query. (Contrast `attestation-gating.md`, where a named, sentinel-free Duty
plays a *prerequisite* — gating — role instead of a consequent one.)

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:read a rl2:Action .
ex:logAccess a rl2:Action .

ex:dataClassification a rl2:LeftOperand ;
    rl2:valueType ex:Classification ;
    rl2:resolutionPath "asset.classification" .

ex:Classification a rdfs:Class .
ex:HomeLoan a ex:Classification .

ex:homeLoanReadPrivilege a rl2:Privilege ;
    rl2:subject rl2:anyAgent ;
    rl2:action ex:read ;
    rl2:object rl2:anyAsset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:dataClassification ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef ex:HomeLoan
    ] ;
    rl2:consequentDuty ex:homeLoanAccessLogDuty .

ex:homeLoanAccessLogDuty a rl2:Duty ;
    rl2:subject rl2:anyAgent ;
    rl2:object rl2:anyAsset ;
    rl2:action ex:logAccess .

ex:homeLoanPolicy a rl2:Set ;
    rl2:clause ex:homeLoanReadPrivilege .
```

## Request and snapshot

Request: some agent reads asset `ex:LoanBook2026`.

World snapshot: `asset.classification = ex:HomeLoan` for `LoanBook2026`.

## Expected result

The Privilege matches on subject and object via the sentinels, and the classification condition
holds, so `accessResult(ex:homeLoanReadPrivilege, ex:homeLoanPolicy, Env) = True` and the envelope
carries `permit(requestingAgent, ex:read, ex:LoanBook2026, ex:homeLoanPolicy)`; the decision is
`Permit`. Because `accessResult` is `True` (not merely non-`False`), the Privilege's
`rl2:consequentDuty` fires: the envelope also carries the bound obligate atom
`obligate(bind(ex:homeLoanAccessLogDuty, requestingAgent, ex:LoanBook2026),
ex:homeLoanPolicy)` — a concrete, sentinel-free Duty occurrence with the requesting agent as
subject and `ex:LoanBook2026` as object in place of the template's `rl2:anyAgent`/`rl2:anyAsset`,
attributed to `ex:homeLoanAccessLogDuty` as its source. This bound occurrence is recorded in the
`EvaluationResult`; being a concrete Duty, a later evaluation of that same occurrence against a
subsequent `WorldSnapshot` yields an ordinary `dutyStatus` (e.g. `Known(Fulfilled)` once admissible
Evidence records the requesting agent performing `ex:logAccess` on `ex:LoanBook2026`) — the same
well-defined audit path as any concrete Duty, even though the obligation did not exist as a named
individual until it was bound.

A request for an asset classified other than `ex:HomeLoan` makes the condition `False`: no atom for
the Privilege is placed in the envelope at all, and the `consequentDuty` does not fire (firing
requires `accessResult.truth = True`, not merely non-`False`) — the decision is `NotApplicable`. A
missing `asset.classification` fact makes the condition `Unknown`, so `accessResult` is `Unknown`,
placing `indeterminate(ex:homeLoanReadPrivilege, ex:homeLoanPolicy, causes)` in the envelope; the
`consequentDuty` still does not fire (`Unknown` does not satisfy `accessResult.truth = True`), so no
logging obligation is emitted, bound or otherwise. The result is `Indeterminate`, not `Permit` or
`NotApplicable`.
