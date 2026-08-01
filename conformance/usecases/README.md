# RL2 Use Cases

The 46 use cases are concise, self-contained policy scenarios. They demonstrate constructs whose
meaning is defined by the canonical projection, pure evaluation contract, and ODRL migration
rules. Profile-defined operands identify their WorldSnapshot dependencies with resolution paths.

## Conduct, evidence, and duties

| Use case | Use case | Use case |
|---|---|---|
| [Pay to Play](pay-to-play.md) | [Team License](team-license.md) | [Break Glass](break-glass.md) |
| [Fire Alarm](fire-alarm.md) | [Wire Transfer Separation of Duties](wire-transfer-sod.md) | [Check Signing Separation of Duties](check-signing-sod.md) |
| [Ethics Approval](ethics-approval.md) | [Data Stewardship](data-stewardship.md) | [GDPR Erasure](gdpr-erasure.md) |
| [Audit Trail](audit-trail.md) | [Data Freshness Promise](data-freshness-promise.md) | [Schema Evolution](schema-evolution.md) |
| [Quality Circuit Breaker](quality-circuit-breaker.md) | [Step-Up Authentication](step-up-auth.md) | [Chinese Wall](chinese-wall.md) |
| [Concurrent Seats](concurrent-seats.md) | [Trial Period](trial-period.md) | |

## Data-governance patterns

| Use case | Use case | Use case |
|---|---|---|
| [Internal Use Only](internal-use-only.md) | [No Redistribution](no-redistribution.md) | [Derived Data Restriction](derived-data-restriction.md) |
| [Usage Metering](usage-metering.md) | [Display and Non-Display](display-vs-nondisplay.md) | [Pass-Through Terms](pass-through-terms.md) |
| [Purpose Restriction](purpose-restriction.md) | [Geographic Restriction](geo-restriction.md) | [Legal Review Gate](legal-review-gate.md) |
| [Data Retention Limit](data-retention-limit.md) | [Anonymization Required](anonymization-required.md) | [No ML Training](no-ml-training.md) |
| [Multi-Level Approval](multi-level-approval.md) | [Connector Certification](connector-certification.md) | [Data Sovereignty](data-sovereignty.md) |
| [Volume Limit](volume-limit.md) | [Logging and Notification](logging-notification.md) | [Deletion After Use](deletion-after-use.md) |
| [Time Window Access](time-window-access.md) | [Owner Access](owner-access.md) | |

## Conditions, collections, and materialization

| Use case | Use case | Use case |
|---|---|---|
| [Exclusive Use Category](exclusive-use-category.md) | [Multiple Required Certifications](multi-certification.md) | [Suspension Exception](negated-condition.md) |
| [Role-Constrained Access](role-hierarchy.md) | [Collection Access](asset-collection-access.md) | [Compliance Attestation](compliance-attestation.md) |
| [Policy Selection Provenance](policy-versioning.md) | [Fulfillment Evidence](fulfillment-evidence.md) | [SLA Credit Clause](sla-credit-clause.md) |

The [semantic vectors](../vectors/) cover reusable boundary cases. The
[migration fixtures](../migration/) show the corresponding ODRL 2.2 import contract.
