# Use Case 43: Exclusive License

**Pattern:** Exactly-one-of choice  
**Vocabulary Demonstrated:** `xone` (exclusive or)  
**Category:** Vocabulary Completeness, Licensing  
**Status:** DRAFT

---

## Business Context

Some licenses grant exclusive rights — the licensee gets *one* type of use, excluding others:

- **Single use type:** Commercial OR non-commercial, not both
- **Single territory:** North America OR Europe, not both
- **Single channel:** Online OR physical, not both

This is "exclusive or" — exactly one must be true.

## Scenario

A music licensing service offers tracks with exclusive use categories:

> "This license permits exactly ONE of: (a) advertising use, (b) editorial use, or (c) personal use. Multi-category use requires separate licenses."

## Policy Intent

> "Exactly ONE use category must apply. If multiple or none apply, license is invalid."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Cardinality | Exactly one |
| Exclusive | If one is true, others must be false |
| Exhaustive | At least one must apply |
| Violation | 0 or 2+ categories = invalid |

## Comparison: AND vs OR vs XONE

| Operator | Meaning | Example |
|----------|---------|---------|
| `and` | All must hold | "Must be employee AND have training" |
| `or` | At least one | "Manager OR delegate may approve" |
| `xone` | Exactly one | "Commercial XOR non-commercial" |

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Use Music Track                         │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Action: use                                         │
│  Object: Music Track                                 │
│  Condition:                                          │
│    xone(                                             │
│      useCategory = Advertising,                      │
│      useCategory = Editorial,                        │
│      useCategory = Personal                          │
│    )                                                 │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

```
Given use category C from request:

xone(A, B, C) evaluates to:
  - TRUE if exactly one of {A, B, C} is true
  - FALSE if zero are true (no category)
  - FALSE if two or more are true (multiple categories)

Request: Use for advertising (useCategory = Advertising)
  - Advertising: TRUE
  - Editorial: FALSE
  - Personal: FALSE
  - xone = TRUE → PERMIT

Request: Use for advertising AND editorial
  - Advertising: TRUE
  - Editorial: TRUE
  - Personal: FALSE
  - xone = FALSE (more than one) → DENY
```

## Real-World Examples

### Software Licensing

"Desktop OR server license, not both" — prevents using one license for multiple deployment types.

### Media Licensing

Stock photos often have exclusive use categories (editorial, commercial, merchandise).

### Exclusive Territories

Distribution rights for exactly one geographic region.

## Profile Requirements

```turtle
@prefix licensing: <https://example.org/profile/licensing#> .

licensing:useCategoryOperand a rl2:LeftOperand ;
    rl2:resolutionPath "context.useCategory" .

licensing:Advertising a licensing:UseCategory .
licensing:Editorial a licensing:UseCategory .
licensing:Personal a licensing:UseCategory .
```

## RL2 Model Pattern

```turtle
rl2:condition [
    a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:xone ;
    rl2:operand [
        a rl2:AtomicConstraint ;
        rl2:leftOperand licensing:useCategoryOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand licensing:Advertising
    ] ;
    rl2:operand [
        a rl2:AtomicConstraint ;
        rl2:leftOperand licensing:useCategoryOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand licensing:Editorial
    ] ;
    rl2:operand [
        a rl2:AtomicConstraint ;
        rl2:leftOperand licensing:useCategoryOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand licensing:Personal
    ]
] .
```

---

## RL2 Model

*To be added after pattern documentation is approved.*

---

## References

- ODRL Vocabulary — xone operator
- Music licensing practices
- Software licensing — deployment type restrictions
