# Use Case 42: No-Claim Inference

**Pattern:** Privilege correlative (absence of duty)  
**Vocabulary Demonstrated:** Inference pattern (not explicit class)  
**Category:** Hohfeldian Relations  
**Status:** DRAFT

---

## Business Context

When Alice has a **Privilege** to X, Bob has **No-Claim** that Alice not X. Bob cannot demand Alice refrain.

Unlike Claim (which RL2 models explicitly), No-Claim is an *absence* — it's inferred from the presence of Privilege, not modeled as a class.

## Scenario

A user has a Privilege to use their computer for personal activities during lunch:

> "Employees may use company equipment for personal purposes during designated breaks."

The employer has **No-Claim** — they cannot demand the employee refrain from personal use during breaks.

## Hohfeldian Analysis

| Position | Holder | Description |
|----------|--------|-------------|
| **Privilege** | Employee | May use for personal purposes |
| **No-Claim** | Employer | Cannot demand Employee refrain |

No-Claim is the correlative of Privilege.

## Policy Intent

> "The Privilege to personal use means no one can demand you not do it."

## Why No-Claim Is Not a Class

RL2 does not model No-Claim explicitly because:

1. **It's an absence:** No-Claim means "there is no Claim" — modeling absence as presence is confusing
2. **It's inferrable:** Given a Privilege, we can infer the No-Claim
3. **Ontological economy:** Modeling absences as classes is problematic

Same reasoning applies to Disability (correlative of Immunity).

## Inference Pattern

```
Given:
  ex:personalUsePrivilege a rl2:Privilege ;
      rl2:subject ex:Employee ;
      rl2:action ex:personalUse ;
      rl2:object ex:CompanyComputer .

Inferred:
  # No Claim exists where:
  #   subject      = (anyone)     # right-holder
  #   counterparty = ex:Employee  # duty-bearer
  #   content = "refrain from personalUse of CompanyComputer"
```

## Practical Implications

No-Claim matters for:

1. **Conflict resolution:** If someone asserts a Claim that conflicts with a Privilege, the Privilege (No-Claim) prevails
2. **Enforcement:** No one can sanction the privileged action
3. **Documentation:** Making explicit that no duty exists

## When No-Claim Becomes Relevant

| Situation | Relevance |
|-----------|-----------|
| Policy conflict | Privilege trumps attempted prohibition |
| Dispute | "You can't demand I stop" |
| Audit | Confirming no violation occurred |

## Example Conflict

```
Policy A: Employee has Privilege to personal use during breaks
Policy B: Supervisor claims Employee must not use personal apps

Resolution:
  - Privilege establishes No-Claim
  - Supervisor's claim is invalid (during breaks)
  - No violation can be assessed
```

## Comparison with Claim/Duty

| Relation | Modeled Explicitly? | Why? |
|----------|--------------------| ----- |
| Duty | Yes | Active obligation |
| Claim | Yes | Active entitlement |
| Privilege | Yes | Active liberty |
| No-Claim | No (inferred) | Absence of Claim |
| Power | Yes | Active authority |
| Liability | Yes | Passive exposure |
| Immunity | Yes | Active protection |
| Disability | No (inferred) | Absence of Power |

## Profile Requirements

No special vocabulary needed — this is inference, not explicit modeling.

```turtle
# The Privilege automatically implies No-Claim
ex:personalUsePrivilege a rl2:Privilege ;
    rl2:subject ex:Employee ;
    rl2:action ex:personalUse ;
    rl2:object ex:CompanyComputer ;
    rl2:condition [
        # During breaks only
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:workPeriodOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef ex:Break
    ] .

# No-Claim is inferred: Employer cannot demand Employee refrain
# from personalUse of CompanyComputer during breaks
```

---

## RL2 Model

*This use case demonstrates inference, not explicit modeling.*

The key insight is that RL2's Privilege class implicitly establishes No-Claim as a correlative. No separate RL2 constructs are needed.

---

## References

- Hohfeld, W.N. "Fundamental Legal Conceptions" (1919)
- RL2_Vocabulary.md Appendix — Why No-Claim and Disability Are Not Classes
- Sergot, M. "Normative Positions" — Stanford Encyclopedia of Philosophy
