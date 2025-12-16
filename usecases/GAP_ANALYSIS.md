# RL2 Use Case Gap Analysis

**Date:** 2025-12-16  
**Purpose:** Identify missing use cases and vocabulary coverage gaps

---

## 1. Research Findings

### 1.1 W3C ODRL Use Cases

The W3C POE Working Group documented [27 use cases](https://w3c.github.io/poe/ucr/). Key patterns not yet covered:

| Pattern | Description | RL2 Coverage |
|---------|-------------|--------------|
| Policy templates | Policies with variable placeholders | ❌ Not covered |
| Delegation of rights | Assigner delegates to intermediary | ❌ Not covered |
| Selective graph access | Named graph / triple-level permissions | ❌ Not covered |
| Policy inheritance | `inheritFrom` flattening | ✅ Mentioned in Primer |
| Rights aggregation | Combining policies for derived works | ❌ Not covered |
| Group operations | Batch policy application | ❌ Not covered |

### 1.2 EU Data Spaces (IDS/Gaia-X)

From [Policy Patterns for Usage Control in Data Spaces](https://ceur-ws.org/Vol-3510/paper_sem4tra_1.pdf):

| IDS Pattern | Description | RL2 Coverage |
|-------------|-------------|--------------|
| Amount of data | Limit volume of data accessed | ❌ Not covered |
| Deletion after use | Mandatory deletion post-processing | ⚠️ Partial (gdpr-erasure) |
| Anonymization | Must anonymize before redistribution | ❌ Not covered |
| Time-based access | Access only during window | ✅ trial-period |
| Geographic restriction | Access only from regions | ❌ Not covered |
| Purpose limitation | Use only for declared purpose | ⚠️ Partial (gdpr-erasure) |
| Usage counting | N uses per time period | ❌ Not covered |
| Logging/notification | Must log or notify on use | ⚠️ Partial (audit-trail) |
| Connector restriction | Access only via certified connector | ❌ Not covered |

### 1.3 ODRL Temporal Profile

The [ODRL Temporal Profile](https://w3c.github.io/odrl/profile-temporal/) addresses:

| Pattern | Description | RL2 Coverage |
|---------|-------------|--------------|
| Policy versioning | Track policy changes over time | ⚠️ policyGeneration exists |
| Effective intervals | effectiveFrom/effectiveTo | ❌ Not demonstrated |
| Audit support | Reconstruct state at any point | ❌ Not covered |
| Forecasting | Predict future capabilities | ❌ Not covered |

---

## 2. Missing Data Contract Use Cases

### 2.1 Internal Data Marketplace Patterns

| Use Case | Description | Priority |
|----------|-------------|----------|
| **purpose-restriction** | Use only for declared purpose (research, marketing, etc.) | HIGH |
| **geo-restriction** | Access only from approved locations/jurisdictions | HIGH |
| **legal-review-gate** | Access blocked until legal review complete | HIGH |
| **data-retention-limit** | Delete after N days/months | MEDIUM |
| **volume-limit** | Maximum rows/GB per query/period | MEDIUM |
| **anonymization-required** | Must anonymize before downstream use | HIGH |
| **no-ml-training** | Prohibition on use for model training | MEDIUM |
| **attribution-required** | Must credit data source | MEDIUM |
| **audit-logging-duty** | Consumer must log all access | HIGH |
| **notification-duty** | Consumer must notify provider of use | LOW |

### 2.2 Approval Workflow Patterns

| Use Case | Description | Priority |
|----------|-------------|----------|
| **multi-level-approval** | Sequential approvals (manager → legal → compliance) | HIGH |
| **approval-expiry** | Approval valid for limited time | MEDIUM |
| **approval-revocation** | Power to revoke previously granted approval | HIGH |
| **conditional-approval** | Approval contingent on other conditions | MEDIUM |

---

## 3. External Data License Use Cases

Based on Bloomberg, LSEG, CME, ICE license terms:

### 3.1 Core Restrictions

| Use Case | Description | Priority |
|----------|-------------|----------|
| **internal-use-only** | No redistribution; internal purposes only | HIGH |
| **no-redistribution** | Explicit prohibition on sharing externally | HIGH |
| **derived-data-restriction** | Derived works cannot reverse-engineer source | HIGH |
| **display-vs-nondisplay** | Different rules for display vs algorithmic use | MEDIUM |
| **professional-vs-retail** | Different terms by subscriber category | MEDIUM |

### 3.2 Usage Metering

| Use Case | Description | Priority |
|----------|-------------|----------|
| **usage-counting** | Track N uses; excess requires additional license | HIGH |
| **concurrent-user-limit** | Max simultaneous users (extends concurrent-seats) | ✅ Exists |
| **query-throttling** | Rate limits on API calls | MEDIUM |

### 3.3 Compliance Obligations

| Use Case | Description | Priority |
|----------|-------------|----------|
| **pass-through-terms** | Must impose same restrictions on downstream | HIGH |
| **audit-compliance** | Subject to licensor audit of usage | HIGH |
| **export-control** | No transfer to sanctioned countries/entities | MEDIUM |
| **regulatory-exception** | May share with regulators despite restrictions | MEDIUM |

### 3.4 Attribution and Branding

| Use Case | Description | Priority |
|----------|-------------|----------|
| **source-attribution** | Must credit data provider | MEDIUM |
| **no-endorsement-implied** | Cannot imply provider endorses derived product | LOW |
| **trademark-usage** | Restrictions on using provider marks | LOW |

---

## 4. Vocabulary Coverage Analysis

### 4.1 Vocabulary Used in Current Use Cases

| Construct | Use Cases |
|-----------|-----------|
| `rl2:Privilege` | ALL (17/17) |
| `rl2:Duty` | pay-to-play, team-license, ethics-approval, audit-trail, data-stewardship, gdpr-erasure, data-freshness, schema-evolution, quality-circuit-breaker |
| `rl2:Prohibition` | chinese-wall |
| `rl2:Promise` | data-stewardship, data-freshness-promise |
| `rl2:Liability` | break-glass |
| `rl2:Event` | break-glass, fire-alarm, schema-evolution, chinese-wall |
| `rl2:EventConstraint` | break-glass, fire-alarm, ethics-approval |
| `rl2:AtomicConstraint` | ALL |
| `rl2:LogicalConstraint` | Most (and/or combinations) |
| `rl2:obligationStateOperand` | pay-to-play, team-license, audit-trail, quality-circuit-breaker |
| `rl2:dutyPerformerOperand` | pay-to-play, wire-transfer-sod, check-signing-sod |
| `rl2:currentAgent` | Most identity-binding cases |
| `rl2:currentDateTime` | trial-period, chinese-wall |
| `rl2:eq`, `rl2:neq` | ALL |
| `rl2:lte`, `rl2:gte` | trial-period, temporal constraints |
| `rl2:and` | Most compound conditions |
| `rl2:priority` | break-glass |

### 4.2 Vocabulary NOT Demonstrated

| Construct | Status | Recommendation |
|-----------|--------|----------------|
| `rl2:Claim` | **Not demonstrated** | Add use case: data-subject-claim (GDPR Art 17 correlative) |
| `rl2:Power` | **Not demonstrated** | Add use case: approval-revocation, grant-access-power |
| `rl2:Immunity` | **Not demonstrated** | Add use case: tenure-protection, regulatory-immunity |
| `rl2:Agreement` | Mentioned but not shown | Add use case: bilateral-data-contract |
| `rl2:Offer` | **Not demonstrated** | Add use case: license-offer-acceptance |
| `rl2:Privacy` | **Not demonstrated** | Enhance gdpr-erasure to use Privacy policy type |
| `rl2:Assertion` | **Not demonstrated** | Add use case: compliance-attestation |
| `rl2:AssetCollection` | **Not demonstrated** | Add use case: bulk-dataset-access |
| `rl2:or` | **Not demonstrated** | Add to multi-channel-access or fallback scenarios |
| `rl2:xone` | **Not demonstrated** | Add use case: exclusive-choice (either A or B, not both) |
| `rl2:isA` | **Not demonstrated** | Add use case: role-hierarchy-check |
| `rl2:isAnyOf` | **Not demonstrated** | Add use case: purpose-whitelist |
| `rl2:isNoneOf` | **Not demonstrated** | Add use case: jurisdiction-blacklist |
| `rl2:isAllOf` | **Not demonstrated** | Add use case: multi-certification-required |
| `rl2:not` | **Not demonstrated** | Add to prohibition conditions |
| `rl2:policyGeneration` | Defined but not shown | Add use case: policy-versioning |
| `rl2:StateTransition` | **Not demonstrated** | Quality-circuit-breaker could show explicitly |

### 4.3 Protocol Vocabulary (rl2p:)

| Construct | Status |
|-----------|--------|
| `rl2p:Requirement` | Not demonstrated in use cases |
| `rl2p:sourceNorm` | Not demonstrated |
| `rl2p:requirementStatus` | Not demonstrated |
| `rl2p:counterparty` | Not demonstrated |
| `rl2p:fulfillmentEvidence` | Not demonstrated |

**Recommendation:** Add a "runtime evaluation" use case showing protocol artifacts.

---

## 5. Prioritized Recommendations

### 5.1 High Priority (Core Gaps)

1. **purpose-restriction.md** — Demonstrates `isAnyOf` for purpose whitelist
2. **no-redistribution.md** — Core external license pattern; shows prohibition + pass-through duty
3. **derived-data-restriction.md** — Complex prohibition on creating reversible derivatives
4. **approval-revocation.md** — Demonstrates `rl2:Power` to revoke existing privileges
5. **legal-review-gate.md** — Multi-stage approval with `rl2:Offer` → `rl2:Agreement` lifecycle
6. **claim-counterclaim.md** — Demonstrates `rl2:Claim` as correlative to Duty

### 5.2 Medium Priority (Vocabulary Coverage)

7. **jurisdiction-blacklist.md** — Demonstrates `isNoneOf` for geo-restriction
8. **multi-certification.md** — Demonstrates `isAllOf` for combined certifications
9. **exclusive-license.md** — Demonstrates `xone` (one use type only)
10. **compliance-attestation.md** — Demonstrates `rl2:Assertion` policy type
11. **data-catalog-collection.md** — Demonstrates `rl2:AssetCollection`
12. **usage-metering.md** — Count-based constraints (extends IDS patterns)

### 5.3 Lower Priority (Completeness)

13. **policy-versioning.md** — Demonstrates `policyGeneration` and effective intervals
14. **immunity-from-termination.md** — Demonstrates `rl2:Immunity`
15. **bilateral-offer-accept.md** — Demonstrates Offer → Agreement flow
16. **runtime-evaluation.md** — Demonstrates `rl2p:Requirement` artifacts

---

## 6. Vocabulary Assessment

### 6.1 Potentially Superfluous

| Construct | Used? | Assessment |
|-----------|-------|------------|
| `rl2:Liability` | Once (break-glass) | Keep — essential for Hohfeldian completeness |
| `rl2:Immunity` | Never | Keep — essential for Hohfeldian completeness; needs use case |
| `rl2:Assertion` | Never | Keep — useful for compliance contexts; needs use case |
| `rl2:xone` | Never | Keep — standard ODRL operator; needs use case |

**Conclusion:** No vocabulary is truly superfluous. All gaps are due to missing use cases, not excess vocabulary.

### 6.2 Missing Vocabulary?

| Potential Addition | Rationale | Recommendation |
|--------------------|-----------|----------------|
| Usage counter operand | IDS COUNT pattern | Add to profile, not core |
| Geographic operand | Geo-restriction | Add to profile, not core |
| Data volume operand | Volume limits | Add to profile, not core |
| Connector type operand | IDS connector certification | Add to profile, not core |

RL2 Core appears complete. Domain patterns should use profile-declared operands.

---

## 7. Next Steps

1. Create 6 high-priority use cases (§5.1)
2. Update usecases/README.md with new categories
3. Ensure each new use case demonstrates at least one unused vocabulary element
4. Consider creating an "external-data-license" profile for Bloomberg/LSEG patterns
5. Consider creating an "ids-dataspace" profile for EU data space patterns

---

*This analysis identifies gaps, not defects. RL2's vocabulary is complete; the use case library needs expansion.*
