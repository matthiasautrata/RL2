# RL2 Use Cases

**Total: 51 use cases** — 17 complete, 34 draft

---

## Status

| Status | Symbol | Meaning |
|--------|--------|---------|
| Complete | ✅ | Documented with RL2 Turtle model |
| Draft | 📝 | Documented, RL2 model pending |

---

## Core Patterns (1-17) ✅

| # | File | Pattern |
|---|------|---------|
| 1 | pay-to-play | Tun-sollen (I must do it myself) |
| 2 | team-license | Sein-sollen (anyone can fulfill) |
| 3 | break-glass | Event + personal liability |
| 4 | fire-alarm | Event, decoupled |
| 5 | wire-transfer-sod | Separation of Duty |
| 6 | check-signing-sod | Dynamic SoD |
| 7 | ethics-approval | Multi-party workflow |
| 8 | data-stewardship | Promise fulfillment |
| 9 | gdpr-erasure | Data subject rights |
| 10 | audit-trail | Compliance prerequisite |
| 11 | data-freshness-promise | Promise + violation |
| 12 | schema-evolution | Event + temporal |
| 13 | quality-circuit-breaker | State machine |
| 14 | step-up-auth | Conditional duty |
| 15 | chinese-wall | Event-based expiry |
| 16 | concurrent-seats | Global state counter |
| 17 | trial-period | Temporal transition |

---

## External Data Licenses (18-23) 📝

| # | File | Pattern | Gap Filled |
|---|------|---------|------------|
| 18 | internal-use-only | Basic restriction | — |
| 19 | no-redistribution | Prohibition + pass-through | — |
| 20 | derived-data-restriction | Conditional prohibition | — |
| 21 | usage-metering | Count-based constraint | — |
| 22 | display-vs-nondisplay | Use-type differentiation | — |
| 23 | pass-through-terms | Downstream obligations | — |

---

## Data Contract Patterns (24-31) 📝

| # | File | Pattern | Gap Filled |
|---|------|---------|------------|
| 24 | purpose-restriction | Purpose whitelist | `isAnyOf` |
| 25 | geo-restriction | Jurisdiction control | `isNoneOf` |
| 26 | legal-review-gate | Approval workflow | `Offer`→`Agreement` |
| 27 | approval-revocation | Power to revoke | `Power` |
| 28 | data-retention-limit | Time-bound deletion | — |
| 29 | anonymization-required | Processing constraint | — |
| 30 | no-ml-training | Use prohibition | — |
| 31 | multi-level-approval | Sequential approvals | — |

---

## EU Data Spaces / IDS (32-37) 📝

| # | File | Pattern | Gap Filled |
|---|------|---------|------------|
| 32 | connector-certification | Certified connector | — |
| 33 | data-sovereignty | Provider controls | — |
| 34 | volume-limit | Data amount restriction | — |
| 35 | logging-notification | Must log or notify | — |
| 36 | deletion-after-use | Post-processing deletion | — |
| 37 | time-window-access | Temporal restriction | — |

---

## Hohfeldian Completeness (38-42) 📝

| # | File | Pattern | Gap Filled |
|---|------|---------|------------|
| 38 | claim-counterclaim | Correlative positions | `Claim` |
| 39 | immunity-from-termination | Protection from power | `Immunity` |
| 40 | power-to-grant | Authority to create | `Power` |
| 41 | liability-exposure | Exposure to power | — |
| 42 | no-claim-inference | Privilege correlative | — |

---

## Vocabulary Completeness (43-49) 📝

| # | File | Pattern | Gap Filled |
|---|------|---------|------------|
| 43 | exclusive-license | Exactly-one choice | `xone` |
| 44 | multi-certification | All required | `isAllOf` |
| 45 | negated-condition | Unless clause | `not` |
| 46 | role-hierarchy | Type-based access | `isA` |
| 47 | asset-collection-access | Bulk dataset | `AssetCollection` |
| 48 | compliance-attestation | Status declaration | `Assertion` |
| 49 | policy-versioning | Generation tracking | `policyGeneration` |

---

## Protocol (50-51) 📝

| # | File | Pattern | Gap Filled |
|---|------|---------|------------|
| 50 | runtime-evaluation | Evaluation trace | `rl2p:Requirement` |
| 51 | fulfillment-evidence | Audit trail | `rl2p:fulfillmentEvidence` |

---

## Next Steps

Work through drafts in batches to add RL2 models. Priority:
1. **Vocabulary gaps** (24-27, 38-40, 43-49) — demonstrate unused constructs
2. **External licenses** (18-23) — real-world applicability
3. **IDS patterns** (32-37) — EU data space alignment
