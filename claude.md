# RL2 Project Skill

Read **persona.md** first — it defines working stance, source-of-truth hierarchy, and change discipline. This file adds quick reference for policy authoring.

---

## Norm Types

| Class | Semantics | Required Properties |
|-------|-----------|---------------------|
| `Privilege` | May do X | subject, action, object |
| `Duty` | Must do X | subject, action, object |
| `Prohibition` | Must not do X | subject, prohibitedAction, object |
| `Claim` | Right to demand X from Y | claimHolder, claimAgainst, correlativeTo |
| `Power` | Can change Y's position | subject, affectsNorm |
| `Liability` | Exposed to power | subject, exposedTo |
| `Immunity` | Protected from power | subject, immuneFrom |
| `Promise` | Voluntary commitment | promisor, promisee, promiseContent |

---

## State Machines

**Duty:** Pending → Active → Fulfilled | Violated

**Promise:** Pending → Fulfilled | Violated (no Active state — promises bind immediately)

---

## Condition Types

| Type | Use | Example |
|------|-----|---------|
| `AtomicConstraint` | Compare value | `purpose eq "research"` |
| `LogicalConstraint` | Combine conditions | `and`, `or`, `xone`, `not` |
| `EventConstraint` | Require event | `expectsEvent [ approver ex:Committee ]` |

**Temporal patterns** use `AtomicConstraint` with `rl2:currentDateTime`:
- Start only: `currentDateTime gte startDate`
- End only: `currentDateTime lte endDate`  
- Interval: combine with `rl2:and`

---

## Identity Binding Patterns

| Pattern | Condition |
|---------|-----------|
| Sein-sollen (anyone) | `obligationStateOperand eq Fulfilled` |
| Tun-sollen (same agent) | above + `dutyPerformerOperand eq currentAgent` |
| Separation of Duty | above + `dutyPerformerOperand neq currentAgent` |

Both operands require `rl2:targetNorm` pointing to the duty being queried.

---

## SHACL Constraints

**Policy:**
- Must have ≥1 clause
- grantor, grantee, condition: max 1 each

**Agreement:**
- Must have both grantor AND grantee

**Privilege/Duty:**
- Must have subject, action, object

**Prohibition:**
- Must have subject, prohibitedAction, object

**LogicalConstraint:**
- Must have constraintOperator
- Must have ≥1 operand (≥2 for `and`/`or`/`xone`)

**AtomicConstraint:**
- Must have leftOperand, constraintOperator, rightOperand (or rightOperandRef)

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `action` on Prohibition | Use `prohibitedAction` |
| Missing `targetNorm` on state operands | Add `rl2:targetNorm ex:theDuty` |
| TemporalConstraint class | Removed — use AtomicConstraint with currentDateTime |
| Inline query strings for collections | Profile-specific; use AssetCollection + member |
| Duty starts Active | Duties start Pending; activation is explicit |
| Promise has Active state | Promises skip Active — Pending means already binding |

---

## Use Case Index

**Identity binding:** pay-to-play (1), team-license (2), wire-transfer-sod (5), check-signing-sod (6)

**Events:** break-glass (3), fire-alarm (4), schema-evolution (12), chinese-wall (15)

**Promises:** data-stewardship (8), data-freshness-promise (11)

**State machines:** quality-circuit-breaker (13), trial-period (17)

**Approvals:** ethics-approval (7), step-up-auth (14)

**GDPR:** gdpr-erasure (9)

**Audit:** audit-trail (10)

**Counters:** concurrent-seats (16)

See `usecases/README.md` for the full 51-case catalog.

---

## Quick Validation

```bash
# Validate with Apache Jena
shacl validate --shapes rl2-shacl.ttl --data your-policy.ttl
```

---

## File Roles

| File | Purpose |
|------|---------|
| persona.md | Working stance, source hierarchy, change discipline |
| rl2.ttl | Normative ontology |
| rl2-shacl.ttl | Validation shapes |
| rl2p.ttl | Protocol ontology |
| RL2_Primer.md | Learning guide |
| RL2_Vocabulary.md | Complete reference |
| RL2_Semantics.md | Formal definitions |
