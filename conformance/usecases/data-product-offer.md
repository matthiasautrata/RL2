# Data Product Offer (Concrete Ports)

## Scenario

A provider offers a data product with two named output ports: a daily-delivery port and a
history-backfill port. The Offer proposes, per port, a quality commitment as a Promise — a
maintenance invariant that the daily port stays fresh, and an achievement commitment that the
history port's initial load is delivered — and grants the consumer a read Privilege over each
port, both gated by a single product-wide conformance-attestation Duty. Every party, port, and
attestation is concrete and named at Offer time.

## Why it matters

This is the Level 1 (concrete-at-acceptance) shape for a multi-port data product, and it needs no
new kernel machinery: `materialize(Offer, Acceptance)` stays single-Offer, single-Acceptance,
single-Agreement, exactly as defined in `RL2_Semantics.md` §Pure Offer Acceptance. There is no
`materializeBundle` and `rl2:Offer`/`requiresProfile` are not overloaded to carry a bundle of
tagged `Set` policies — "two ports" is expressed as two ordinary concrete Assets, each the
`rl2:object` of its own per-port Promise, both Promises sitting as ordinary clauses of one Offer.

The product-wide attestation, `ex:attestConformance`, is a genuine, sentinel-free Duty — never a
template with `rl2:anyAgent`/`rl2:anyAsset` — attached via `rl2:prerequisiteDuty` to *both* read
Privileges rather than authored twice. It is not itself a top-level clause of the Offer, but it is
still in `localNorms(O)`: the Offer-level locality rule includes a non-clause Duty owned through a
Privilege's `rl2:prerequisiteDuty` (`RL2_Semantics.md` §Pure Offer Acceptance,
"Clause copying and reference rewriting"). It therefore receives a `primaryIds` entry, is
structurally copied and reference-rewritten by `materialize`, and remains attached — not promoted
to an Agreement clause — on both materialized Privileges, exactly as `PrerequisiteDutyShape`
permits a prerequisite Duty to be referenced by more than one Privilege.

The daily-port commitment is a state-form (`Maintain`) Promise; the history-port commitment is an
action-form (`Achieve`) Promise — one of each, for variety, both carrying their port as `rl2:object`
per `PromiseShape`. Before acceptance, the Offer's clauses contribute no normative atoms (`Eval`
over an Offer is inspection-only, `RL2_Semantics.md` §Normative Derivation); `materialize` itself
reads no `WorldSnapshot` and emits no effect, and produces the two crystallized, beneficiary-bearing
Duties plus the copied, prerequisite-attached read Privileges in the resulting Agreement.

Per-request, tag-based selection of which `CompiledPolicyModule`s belong in a given evaluation's
policy universe (see `conformance/usecases/universe-selection.md` and
`docs/RL2_ExternalData.md` §6) is a distinct, assembler-side concern that this scenario does not
need: the ports and the consumer are already concrete when the Offer is authored, so nothing here
depends on per-request universe assembly. Ports and counterparties are concrete at Offer/Acceptance
time; a data product creating new ports under an already-live Agreement is out of scope for this
transformation — that is policy amendment/lifecycle, not evaluation (`backlog.md` §6, "Port churn
under a live agreement").

## Source Offer

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Consumer a rl2:Agent .
ex:DataProduct a rl2:Asset .
ex:PortDaily a rl2:Asset .
ex:PortHistory a rl2:Asset .
ex:read a rl2:Action .
ex:attest a rl2:Action .
ex:deliverInitialLoad a rl2:Action .

ex:portAge a rl2:LeftOperand ;
    rl2:valueType xsd:dayTimeDuration ;
    rl2:resolutionPath "asset.metadata.age" .

ex:portFresh a rl2:AtomicConstraint ;
    rl2:leftOperand ex:portAge ;
    rl2:constraintOperator rl2:lte ;
    rl2:rightOperand "PT18H"^^xsd:dayTimeDuration .

ex:dailyPortPromise a rl2:Promise ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Consumer ;
    rl2:invariant ex:portFresh ;
    rl2:object ex:PortDaily .

ex:historyPortPromise a rl2:Promise ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Consumer ;
    rl2:action ex:deliverInitialLoad ;
    rl2:object ex:PortHistory .

ex:attestConformance a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Consumer ;
    rl2:action ex:attest ;
    rl2:object ex:DataProduct .

ex:readDailyPortPrivilege a rl2:Privilege ;
    rl2:subject ex:Consumer ;
    rl2:action ex:read ;
    rl2:object ex:PortDaily ;
    rl2:prerequisiteDuty ex:attestConformance .

ex:readHistoryPortPrivilege a rl2:Privilege ;
    rl2:subject ex:Consumer ;
    rl2:action ex:read ;
    rl2:object ex:PortHistory ;
    rl2:prerequisiteDuty ex:attestConformance .

ex:dataProductOffer a rl2:Offer ;
    rl2:grantor ex:Provider ;
    rl2:grantee ex:Consumer ;
    rl2:clause ex:dailyPortPromise, ex:historyPortPromise,
               ex:readDailyPortPrivilege, ex:readHistoryPortPrivilege .
```

## Acceptance

```text
Acceptance(
  agreementId = ex:dataProductAgreement,
  grantor = ex:Provider,
  grantee = ex:Consumer,
  primaryIds = {
    ex:dailyPortPromise -> ex:dailyPortDuty,
    ex:historyPortPromise -> ex:historyPortDuty,
    ex:readDailyPortPrivilege -> ex:readDailyPortPrivilege_A1,
    ex:readHistoryPortPrivilege -> ex:readHistoryPortPrivilege_A1,
    ex:attestConformance -> ex:attestConformance_A1
  },
  objectBindings = {},
  dutyWindows = {}
)
```

## Materialized Agreement

```turtle
@prefix ex: <https://example.org/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Consumer a rl2:Agent .
ex:DataProduct a rl2:Asset .
ex:PortDaily a rl2:Asset .
ex:PortHistory a rl2:Asset .
ex:read a rl2:Action .
ex:attest a rl2:Action .
ex:deliverInitialLoad a rl2:Action .

ex:portAge a rl2:LeftOperand ;
    rl2:valueType xsd:dayTimeDuration ;
    rl2:resolutionPath "asset.metadata.age" .

ex:portFresh a rl2:AtomicConstraint ;
    rl2:leftOperand ex:portAge ;
    rl2:constraintOperator rl2:lte ;
    rl2:rightOperand "PT18H"^^xsd:dayTimeDuration .

ex:dailyPortDuty a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Consumer ;
    rl2:object ex:PortDaily ;
    rl2:invariant ex:portFresh .

ex:historyPortDuty a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Consumer ;
    rl2:object ex:PortHistory ;
    rl2:action ex:deliverInitialLoad .

ex:attestConformance_A1 a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Consumer ;
    rl2:action ex:attest ;
    rl2:object ex:DataProduct .

ex:readDailyPortPrivilege_A1 a rl2:Privilege ;
    rl2:subject ex:Consumer ;
    rl2:action ex:read ;
    rl2:object ex:PortDaily ;
    rl2:prerequisiteDuty ex:attestConformance_A1 .

ex:readHistoryPortPrivilege_A1 a rl2:Privilege ;
    rl2:subject ex:Consumer ;
    rl2:action ex:read ;
    rl2:object ex:PortHistory ;
    rl2:prerequisiteDuty ex:attestConformance_A1 .

ex:dataProductAgreement a rl2:Agreement ;
    rl2:grantor ex:Provider ;
    rl2:grantee ex:Consumer ;
    rl2:clause ex:dailyPortDuty, ex:historyPortDuty,
               ex:readDailyPortPrivilege_A1, ex:readHistoryPortPrivilege_A1 ;
    prov:wasDerivedFrom ex:dataProductOffer .
```

## Request and snapshot

Request: `(agent = Consumer, action = read, asset = PortDaily)` against `ex:dataProductAgreement`.

World snapshot: qualifying, admissible Evidence records `Provider` performing `attest` on
`DataProduct`; `asset.metadata.age = "PT4H"^^xsd:dayTimeDuration` for `PortDaily`.

## Expected result

Before acceptance, `ex:dataProductOffer`'s clauses are inert: no Promise or Privilege in the Offer
grants, denies, or gates anything, and `Eval` never sees the Offer as an operative policy.

After acceptance, `ex:attestConformance_A1` is an unbounded Achievement Duty (no `dutyWindow`), so
qualifying evidence alone makes it `dutyStatuses[ex:attestConformance_A1] = Known(Fulfilled)`,
regardless of elapsed time. The prerequisite check on `ex:readDailyPortPrivilege_A1` reads this
status directly (not filtered by `matchesRequest`), so `accessResult(ex:readDailyPortPrivilege_A1,
ex:dataProductAgreement, Env) = True` and the envelope carries `permit(Consumer, ex:read,
ex:PortDaily, ex:dataProductAgreement)`; the decision is `Permit`. `ex:readHistoryPortPrivilege_A1`
does not match this request (its object is `PortHistory`, not `PortDaily`) and contributes no atom.

`ex:dailyPortDuty` is a Maintenance Duty without a window: with `asset.metadata.age = PT4H ≤
PT18H`, its invariant is true now, so `dutyStatuses[ex:dailyPortDuty] = Known(Active)` — reported
for inspection, but it does not gate this request since only `ex:attestConformance_A1` is the
prerequisite. `ex:historyPortDuty` is an unbounded Achievement Duty with no recorded evidence of
`deliverInitialLoad`, so `dutyStatuses[ex:historyPortDuty] = Known(Pending)`; it likewise does not
gate the `PortDaily` read.

Ports and counterparties are concrete at acceptance; a data product creating additional ports under
this already-live `ex:dataProductAgreement` is out of scope here — extending product terms to a
later-created port is policy amendment/lifecycle, not an `Eval` concern.
