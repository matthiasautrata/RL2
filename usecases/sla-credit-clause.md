# Use Case 52: SLA Credit Clause (Offer → Agreement Materialization)

**Pattern:** Promise + sibling Duty, crystallized on acceptance
**Vocabulary Demonstrated:** `Offer`, `Agreement`, `targetNorm` (Promise-valued, then Norm-valued), `materialize`, `prov:wasDerivedFrom`
**Category:** Data Contracts, SLA Enforcement
**Status:** DRAFT

---

## Business Context

A cloud provider publishes a standard SLA offer to its catalog: it *promises* 99.9% monthly
uptime, and separately commits to a service credit *duty* if that promise is broken. The credit
duty's condition needs to say "pay the credit once the uptime promise is violated" — but at
Offer time there is no Duty yet to point at, only the sibling Promise. This is the
Offer-is-the-only-container-where-Promise-and-Norm-clauses-coexist case that motivates
**PROM-7**'s `rl2:targetNorm` range widening and the `materialize` function
(RL2_Semantics.md §Materialization).

The same Offer is accepted by many customers, so whatever the Agreement ends up looking like
must not let two customers' credit duties collide in `Σ`.

## Policy Intent

> "The provider promises 99.9% monthly uptime. If that promise is violated, the provider owes
> the customer a service credit."

## Stage 1 — Offer (catalog, not yet binding)

The Promise and the Duty are siblings in the same Offer. The Duty's condition targets the
Promise directly — this requires `rl2:targetNorm`'s widened range (`rl2:Norm ⊔ rl2:Promise`,
PROM-7) and a Promise-valued left operand, since the promise has not crystallized yet and there
is no Duty to target.

```turtle
@prefix ex: <https://example.org/> .
@prefix sla: <https://example.org/profile/sla#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

sla:monthlyUptimeOperand a rl2:LeftOperand ;
    rdfs:label "Monthly Uptime Percentage" ;
    rdfs:comment "Measured uptime percentage for the current billing month." ;
    rl2:resolutionPath "asset.metadata.monthlyUptime" ;
    rdfs:range xsd:decimal .

sla:promiseStateOperand a rl2:LeftOperand ;
    rdfs:label "Promise State Operand" ;
    rdfs:comment "Queries the PromiseState of the target promise (Offer-stage only)." ;
    rl2:resolutionPath "state.Promises.<target>.state" ;
    rdfs:range rl2:PromiseState .

sla:issueServiceCredit a rl2:Action ;
    rdfs:label "Issue Service Credit" .

# The Promise: provider commits to an uptime SLA (Sein-sollen — a state, not an action).
ex:uptimePromise a rl2:Promise ;
    rl2:promisor ex:CloudProvider ;
    rl2:promisee ex:Customer ;
    rl2:promisedState ex:uptimeMeetsSLA ;
    rl2:object ex:ProductionService .

ex:uptimeMeetsSLA a rl2:AtomicConstraint ;
    rl2:leftOperand sla:monthlyUptimeOperand ;
    rl2:constraintOperator rl2:gte ;
    rl2:rightOperand "99.9"^^xsd:decimal .

# The Duty: sibling clause in the same Offer. Its condition targets the Promise directly —
# there is no crystallized Duty to point at yet.
ex:creditDuty a rl2:Duty ;
    rl2:subject ex:CloudProvider ;
    rl2:action sla:issueServiceCredit ;
    rl2:object ex:Customer ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:uptimePromise ;
        rl2:leftOperand sla:promiseStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Violated
    ] .

ex:uptimeOffer a rl2:Offer ;
    rl2:grantor ex:CloudProvider ;
    rl2:grantee ex:Customer ;
    rl2:clause ex:uptimePromise, ex:creditDuty .
```

## Stage 2 — Materialization (Offer → Agreement)

On acceptance, `materialize(ex:uptimeOffer, Acceptance)` (RL2_Semantics.md §Materialization)
produces a fresh Agreement:

1. Mint a fresh Agreement IRI (`ex:uptimeAgreement`).
2. Crystallize `ex:uptimePromise` into a freshly-minted Duty `ex:uptimeDuty` (fulfillment
   inherited from `ex:uptimeMeetsSLA`, per the `PromisedState` row of the crystallization table)
   and its correlative Claim `ex:uptimeClaim`.
3. Copy the restated `ex:creditDuty` clause under a **freshly-minted** IRI, `ex:creditDuty_A1`
   — not the same IRI as the Offer's, because `Σ.ObligationState : Duty → State` has no
   per-Agreement dimension (RL2_Semantics.md §Σ): if a second customer accepted the same Offer
   and its copy reused `ex:creditDuty`'s IRI, the two customers' credit-duty states would
   collide in the same map entry.
4. Rewrite `ex:creditDuty_A1`'s condition: `targetNorm` now points at the crystallized
   `ex:uptimeDuty`, and the left operand becomes the ordinary `rl2:obligationStateOperand` —
   the Promise is gone, so there is nothing left for `promiseStateOperand` to query.
5. Record `ex:uptimeAgreement prov:wasDerivedFrom ex:uptimeOffer`.

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix prov: <http://www.w3.org/ns/prov#> .

ex:uptimeDuty a rl2:Duty ;
    rl2:subject ex:CloudProvider ;
    rl2:action sla:maintainUptime ;
    rl2:object ex:ProductionService ;
    rl2:condition ex:uptimeMeetsSLA .

ex:uptimeClaim a rl2:Claim ;
    rl2:subject ex:Customer ;
    rl2:counterparty ex:CloudProvider ;
    rl2:correlativeTo ex:uptimeDuty .

ex:creditDuty_A1 a rl2:Duty ;
    rl2:subject ex:CloudProvider ;
    rl2:action sla:issueServiceCredit ;
    rl2:object ex:Customer ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:uptimeDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Violated
    ] .

ex:uptimeAgreement a rl2:Agreement ;
    rl2:grantor ex:CloudProvider ;
    rl2:grantee ex:Customer ;
    rl2:clause ex:uptimeDuty, ex:uptimeClaim, ex:creditDuty_A1 ;
    prov:wasDerivedFrom ex:uptimeOffer .

sla:maintainUptime a rl2:Action ;
    rdfs:label "Maintain Uptime" .
```

No `rl2:Promise` survives in `ex:uptimeAgreement` — consistent with `AgreementShape` and PROM-1
— and `targetNorm` inside the executed Agreement is Norm-valued throughout, exactly as
`rl2:targetNorm`'s comment in `rl2.ttl` specifies.

## Why fresh IRIs, not the Offer's own clause IRIs

`ex:uptimeOffer` is a catalog entry: one Offer, many customers, many Agreements. Every clause
`materialize` places in an Agreement — crystallized or merely restated — gets its own fresh IRI
for the same reason: `Σ`'s state maps (`ObligationState`, `DutyPerformer`, `Requirements`) are
keyed by bare Duty/Claim IRI with no Case or Agreement dimension. Reusing an IRI across
Agreements would let one customer's fulfillment silently overwrite another's. (Contrast
`usecases/legal-review-gate.md`, which reuses a clause IRI across its Offer and Agreement —
safe there only because that Offer is a single bespoke proposal accepted exactly once, never
republished to a second grantee.)

## References

- RL2_Semantics.md §Crystallization, §Materialization
- RL2_IR.md §7.2 (`CrystallizePromise` is runtime bookkeeping, not `materialize`)
- `rl2:targetNorm` (`rl2.ttl`) — PROM-7 range widening
- PROV-O: <https://www.w3.org/TR/prov-o/> (`prov:wasDerivedFrom`)
- Compare `usecases/data-freshness-promise.md` (a *standalone*, never-crystallized promise) and
  `usecases/legal-review-gate.md` (the corpus's other Offer→Agreement example)
