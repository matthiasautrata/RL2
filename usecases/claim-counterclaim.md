# Use Case 38: Claim and Duty Correlation

**Pattern:** Correlative normative positions  
**Vocabulary Demonstrated:** `Claim`, `correlativeTo`, `claimHolder`, `claimAgainst`  
**Category:** Hohfeldian Relations, Data Contracts  
**Status:** DRAFT

---

## Business Context

When a data provider commits to data quality, they incur a **Duty**. But from whose perspective? The data consumer holds a **Claim** — a right to demand performance.

This duality is fundamental:
- **Duty** (provider's view): "I must deliver quality data"
- **Claim** (consumer's view): "I can demand quality data"

Most policy languages model only duties. RL2 models both sides of the normative relationship.

## Scenario

A data provider and consumer enter a data contract:

> "Provider shall ensure data freshness not exceeding 24 hours. Consumer may demand correction if freshness exceeds threshold."

The provider has a **Duty** to maintain freshness. The consumer holds a **Claim** against the provider for that performance.

## Hohfeldian Analysis

Hohfeld identified that Duty and Claim are **jural correlatives**:

```
If A has a Duty to B to do X,
Then B has a Claim against A that A do X.
```

They are two descriptions of the same normative relationship from different vantage points.

| Position | Holder | Description |
|----------|--------|-------------|
| **Duty** | Provider | Must maintain freshness |
| **Claim** | Consumer | Can demand freshness |

## Why Model Both?

Modeling only duties is incomplete:

| Question | Duty-only model | Claim-aware model |
|----------|-----------------|-------------------|
| Who can demand performance? | Unclear | claimHolder |
| Who must answer demands? | Unclear | claimAgainst |
| Can claims be transferred? | N/A | Yes, via assignment |
| Can claims be waived? | N/A | Yes, explicit waiver |

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Duty: Data Freshness                                │
│  ─────────────────────────────────────────────────  │
│  Subject: Provider                                   │
│  Action: maintain freshness                          │
│  Object: Dataset                                     │
│  Counterparty: Consumer                              │
│  Condition: freshness ≤ 24 hours                     │
└─────────────────────────────────────────────────────┘
            │
            │ correlativeTo
            ▼
┌─────────────────────────────────────────────────────┐
│  Claim: Right to Freshness                           │
│  ─────────────────────────────────────────────────  │
│  Claim Holder: Consumer                              │
│  Claim Against: Provider                             │
│  Correlative To: ex:freshnessDuty                    │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

For **Duty** evaluation:
```
Request: Check if Provider is meeting freshness duty

1. Resolve current freshness from Σ
2. Compare against threshold (≤ 24 hours)
3. If satisfied → Duty state = Fulfilled
   If violated → Duty state = Violated
```

For **Claim** evaluation:
```
Request: Can Consumer demand correction?

1. Find Claim held by Consumer
2. Find correlative Duty
3. Check Duty state:
   - If Violated → Consumer CAN demand correction
   - If Fulfilled → No grounds for demand
```

## Claims Enable Additional Patterns

### Claim Transfer (Assignment)

```
Original: Consumer1 holds Claim against Provider
After assignment: Consumer2 holds Claim against Provider
```

The Duty remains with Provider, but the right to demand transfers.

### Claim Waiver

Consumer may waive their claim (release the provider from duty):

```
Before waiver: Consumer holds Claim → Provider has Duty
After waiver: No Claim → Provider has no Duty to Consumer
```

### Multiple Claimants

A provider may owe the same duty to multiple consumers, each holding their own claim:

```
Provider has Duty D to maintain freshness
Consumer1 holds Claim C1 correlative to D
Consumer2 holds Claim C2 correlative to D
```

## Real-World Examples

### SLA Contracts

- Provider duty: 99.9% uptime
- Consumer claim: Demand service credits if breached

### Data Marketplaces

- Provider duty: Accurate metadata
- Consumer claim: Request correction or refund

### GDPR Rights

- Controller duty: Respond to access requests within 30 days
- Data subject claim: Demand response (Article 15)

## Comparison with Related Use Cases

| Use Case | Focus |
|----------|-------|
| **claim-counterclaim** | Claim as correlative to Duty |
| data-freshness-promise (11) | Promise-based (voluntary) |
| gdpr-erasure (9) | Duty triggered by claim exercise |

## Distinction: Promise vs Duty+Claim

| Concept | Promise | Duty+Claim |
|---------|---------|------------|
| Source | Voluntary commitment | May be imposed |
| Correlative | Implicit expectation | Explicit Claim |
| Transfer | Typically non-transferable | Claim may transfer |
| Enforcement | Reputational | Legal/contractual |

## Protocol Representation

When a Claim exists, the protocol can represent the Consumer's position:

```turtle
ex:freshnessRequirement a rl2p:Requirement ;
    rl2p:sourceNorm ex:freshnessDuty ;
    rl2p:counterparty ex:Consumer ;  # The claim holder
    rl2p:requirementStatus rl2:Active .
```

The `counterparty` field on `rl2p:Requirement` captures who holds the correlative Claim.

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder for RL2 implementation
# Will demonstrate: Claim, claimHolder, claimAgainst, correlativeTo
```

---

## References

- Hohfeld, W.N. "Fundamental Legal Conceptions" (1919)
- Sergot, M. "Normative Positions" — Stanford Encyclopedia of Philosophy
- RL2_Protocol.md — Requirement with counterparty
