# Use Case 39: Immunity from Termination

**Pattern:** Protection against normative change  
**Vocabulary Demonstrated:** `Immunity`, `immuneFrom`  
**Category:** Hohfeldian Relations  
**Status:** DRAFT

---

## Business Context

Some rights cannot be revoked. Immunity protects against exercise of another's power:

- **Tenure:** Professor cannot be fired without cause
- **Vested rights:** Earned entitlements cannot be withdrawn
- **Constitutional:** Fundamental rights cannot be overridden
- **Contractual:** Irrevocable licenses

## Scenario

A researcher receives an irrevocable license to use a dataset:

> "This license is perpetual and irrevocable. Licensor waives any right to terminate access to the Dataset."

The researcher has **immunity** from the licensor's power to terminate.

## Hohfeldian Analysis

| Position | Holder | Description |
|----------|--------|-------------|
| **Power** | Licensor | Would normally have power to terminate |
| **Immunity** | Researcher | Protected from that power |
| **Disability** | Licensor | Cannot exercise power against Researcher |

Immunity and Disability are correlatives, just as Claim and Duty are correlatives.

## Policy Intent

> "The license privilege CANNOT be revoked by the Licensor."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Protects | Existing privilege or other right |
| Against | Specific power |
| Scope | May be absolute or conditional |
| Duration | Often perpetual |

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Use Dataset (perpetual)                 │
│  ─────────────────────────────────────────────────  │
│  Subject: Researcher                                 │
│  Action: use                                         │
│  Object: Dataset                                     │
└─────────────────────────────────────────────────────┘
            │
            │ protected by
            ▼
┌─────────────────────────────────────────────────────┐
│  Immunity: Protection from Termination               │
│  ─────────────────────────────────────────────────  │
│  Subject: Researcher                                 │
│  Immune From: Licensor's terminationPower            │
│  Effect: Power cannot be exercised against Researcher│
└─────────────────────────────────────────────────────┘
            │
            │ correlates with (not explicitly modeled)
            ▼
┌─────────────────────────────────────────────────────┐
│  Disability: Cannot Terminate                        │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensor                                   │
│  Cannot exercise: terminationPower against Researcher│
└─────────────────────────────────────────────────────┘
```

Note: RL2 does not model Disability as an explicit class (see RL2_Vocabulary.md Appendix). It is inferred from the presence of Immunity.

## Immunity vs Protection by Condition

| Mechanism | How It Works |
|-----------|--------------|
| **Immunity** | Power cannot be exercised at all |
| **Conditional Power** | Power exists but conditions limit exercise |

Example: "Licensor may terminate only for material breach" is a **conditional Power**, not Immunity. The Researcher has no immunity but the Power is constrained.

## Real-World Examples

### Academic Tenure

Tenured faculty have immunity from at-will termination. University retains power only for cause (different, narrower power).

### Irrevocable Licenses

Open source licenses (BSD, MIT) are typically irrevocable once granted.

### Constitutional Rights

Fundamental rights create immunity from legislative powers that would abridge them.

### Vested Pension Rights

Once vested, pension rights cannot be unilaterally reduced.

## Evaluation Logic

```
Request: Licensor attempts to terminate Researcher's access

1. Does Licensor have Power P to terminate?
2. Does Researcher have Immunity from P?
3. If Immunity exists → Power exercise fails
   If no Immunity → Power may be exercised
```

## Profile Requirements

```turtle
@prefix protection: <https://example.org/profile/protection#> .

protection:terminationPower a rl2:Power ;
    rdfs:label "Power to Terminate License" ;
    rl2:subject ex:Licensor ;
    rl2:affectsNorm ex:usePrivilege .

protection:irrevocableImmunity a rl2:Immunity ;
    rl2:subject ex:Researcher ;
    rl2:immuneFrom protection:terminationPower .
```

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate Immunity, immuneFrom
```

---

## References

- Hohfeld, W.N. "Fundamental Legal Conceptions" (1919)
- Academic tenure law
- Irrevocable license doctrine
- Constitutional immunity concepts
