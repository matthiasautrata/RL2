# RL2 Use Cases

**Total: 52 use cases** — 52 structurally valid; SCOPE-2 semantic migration in progress

All 52 files pass the current SHACL harness. This is a structural baseline, not a claim that every
current operational explanation matches the revised pure-evaluation scope. The authoritative
migration classification is [`../usecase-disposition.md`](../usecase-disposition.md). Thirty-five
individual files still carry legacy `Status: DRAFT` metadata; those labels will be normalized as
each case is migrated rather than changed mechanically in advance.

---

## Status

| Status | Symbol | Meaning |
|--------|--------|---------|
| Complete | ✅ | Documented with RL2 Turtle model |
| Draft | 📝 | Documented, RL2 model pending |

---

## Core Patterns (1-17)

| # | File | Pattern | Status |
|---|------|---------|--------|
| 1 | pay-to-play.md | Tun-sollen (I must do it myself) | ✅ |
| 2 | team-license.md | Sein-sollen (anyone can fulfill) | ✅ |
| 3 | break-glass.md | Event + personal liability | ✅ |
| 4 | fire-alarm.md | Event, decoupled | ✅ |
| 5 | wire-transfer-sod.md | Separation of Duty | ✅ |
| 6 | check-signing-sod.md | Dynamic SoD | ✅ |
| 7 | ethics-approval.md | Multi-party workflow | ✅ |
| 8 | data-stewardship.md | Promise fulfillment | ✅ |
| 9 | gdpr-erasure.md | GDPR data subject rights | ✅ |
| 10 | audit-trail.md | Compliance prerequisite | ✅ |
| 11 | data-freshness-promise.md | Promise + violation | ✅ |
| 12 | schema-evolution.md | Event + temporal | ✅ |
| 13 | quality-circuit-breaker.md | State machine | ✅ |
| 14 | step-up-auth.md | Conditional duty | ✅ |
| 15 | chinese-wall.md | Event-based expiry | ✅ |
| 16 | concurrent-seats.md | Global state counter | ✅ |
| 17 | trial-period.md | Temporal transition | ✅ |

---

## External Data Licenses (18-23)

| # | File | Pattern | Gap Filled | Status |
|---|------|---------|------------|--------|
| 18 | internal-use-only.md | Basic restriction | — | ✅ |
| 19 | no-redistribution.md | Prohibition + pass-through | — | ✅ |
| 20 | derived-data-restriction.md | Conditional prohibition | — | ✅ |
| 21 | usage-metering.md | Count-based constraint | — | ✅ |
| 22 | display-vs-nondisplay.md | Use-type differentiation | — | ✅ |
| 23 | pass-through-terms.md | Downstream obligations | — | ✅ |

---

## Data Contract Patterns (24-31)

| # | File | Pattern | Gap Filled | Status |
|---|------|---------|------------|--------|
| 24 | purpose-restriction.md | Purpose whitelist | `isAnyOf` | ✅ |
| 25 | geo-restriction.md | Jurisdiction control | `isNoneOf` | ✅ |
| 26 | legal-review-gate.md | Approval workflow | `Offer`→`Agreement` | ✅ |
| 27 | approval-revocation.md | Power to revoke | `Power` | ✅ |
| 28 | data-retention-limit.md | Time-bound deletion | — | ✅ |
| 29 | anonymization-required.md | Processing constraint | — | ✅ |
| 30 | no-ml-training.md | Use prohibition | — | ✅ |
| 31 | multi-level-approval.md | Sequential approvals | — | ✅ |

---

## EU Data Spaces / IDS (32-37)

| # | File | Pattern | Gap Filled | Status |
|---|------|---------|------------|--------|
| 32 | connector-certification.md | Certified connector | — | ✅ |
| 33 | data-sovereignty.md | Provider controls | — | ✅ |
| 34 | volume-limit.md | Data amount restriction | — | ✅ |
| 35 | logging-notification.md | Must log or notify | — | ✅ |
| 36 | deletion-after-use.md | Post-processing deletion | — | ✅ |
| 37 | time-window-access.md | Temporal restriction | — | ✅ |

---

## Hohfeldian Completeness (38-42)

| # | File | Pattern | Gap Filled | Status |
|---|------|---------|------------|--------|
| 38 | claim-counterclaim.md | Correlative positions | `Claim` | ✅ |
| 39 | immunity-from-termination.md | Protection from power | `Immunity` | ✅ |
| 40 | power-to-grant.md | Authority to create | `Power` | ✅ |
| 41 | liability-exposure.md | Exposure to power | — | ✅ |
| 42 | no-claim-inference.md | Privilege correlative | — | ✅ |

---

## Vocabulary Completeness (43-49)

| # | File | Pattern | Gap Filled | Status |
|---|------|---------|------------|--------|
| 43 | exclusive-license.md | Exactly-one choice | `xone` | ✅ |
| 44 | multi-certification.md | All required | `isAllOf` | ✅ |
| 45 | negated-condition.md | Unless clause | `not` | ✅ |
| 46 | role-hierarchy.md | Type-based access | `isA` | ✅ |
| 47 | asset-collection-access.md | Bulk dataset | `AssetCollection` | ✅ |
| 48 | compliance-attestation.md | Status declaration | `Assertion` | ✅ |
| 49 | policy-versioning.md | Generation tracking | `policyGeneration` | ✅ |

---

## Protocol (50-51)

| # | File | Pattern | Gap Filled | Status |
|---|------|---------|------------|--------|
| 50 | runtime-evaluation.md | Evaluation trace | `rl2p:Requirement` | ✅ |
| 51 | fulfillment-evidence.md | Audit trail | `rl2p:fulfillmentEvidence` | ✅ |
| 52 | sla-credit-clause.md | Promise + sibling Duty, crystallized on acceptance | `targetNorm` (Promise-valued), `materialize`, `prov:wasDerivedFrom` | ✅ |
---

## Sources

Use case selection informed by:
- [W3C ODRL Use Cases and Requirements](https://w3c.github.io/poe/ucr/) (27 patterns)
- [IDS Policy Patterns for Usage Control in Data Spaces](https://ceur-ws.org/Vol-3510/paper_sem4tra_1.pdf)
- [ODRL Temporal Profile](https://w3c.github.io/odrl/profile-temporal/)
- Bloomberg, LSEG, CME, ICE license terms (external data patterns)

---

## Vocabulary Coverage

Core patterns (1-17) demonstrate:

| Construct | Use Cases |
|-----------|-----------|
| `Privilege` | All |
| `Duty` | 1, 2, 7, 8, 9, 10, 11, 12, 13 |
| `Prohibition` | 15 |
| `Promise` | 8, 11 |
| `Liability` | 3 |
| `Event` | 3, 4, 12, 15 |
| `obligationStateOperand` | 1, 2, 10, 13 |
| `dutyPerformerOperand` | 1, 5, 6 |

Draft use cases (18-51) fill remaining vocabulary gaps:

| Construct | Use Case |
|-----------|----------|
| `Claim` | 38 |
| `Power` | 27, 40 |
| `Immunity` | 39 |
| `Offer`/`Agreement` | 26 |
| `Assertion` | 48 |
| `AssetCollection` | 47 |
| `isAnyOf` | 24 |
| `isNoneOf` | 25 |
| `isAllOf` | 44 |
| `xone` | 43 |
| `not` | 45 |
| `isA` | 46 |
| `policyGeneration` | 49 |
| `rl2p:Requirement` | 50 |
| `rl2p:fulfillmentEvidence` | 51 |
| `targetNorm` (Promise-valued) / `materialize` | 52 |

---

## Next Steps

All 52 use cases are complete with validated RL2 Turtle models. Future work: expand Hohfeldian and Protocol categories with additional scenarios as needed.
