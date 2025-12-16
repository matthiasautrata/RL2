# Use Case 22: Display vs Non-Display Use

**Pattern:** Use-type differentiation  
**Vocabulary Demonstrated:** `isAnyOf` for use-type classification  
**Category:** External Data Licenses  
**Status:** DRAFT

---

## Business Context

Market data vendors distinguish between:
- **Display use:** Human views data on screen
- **Non-display use:** System processes data algorithmically

Different fees and terms apply to each. Non-display use (algorithmic trading, risk models) often costs significantly more.

## Scenario

A bank licenses market data. The license permits:
- Display use by authorized traders (included in base fee)
- Non-display use for risk calculations (additional fee required)

Using data for algorithmic trading without non-display license is prohibited.

## Policy Intent

> "Data may be used for display purposes. Non-display use requires separate authorization."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Classification | Use type (display vs non-display) |
| Fee structure | Different pricing per type |
| Audit | Must track use type |
| Common violation | Algorithmic use under display license |

## Use Type Definitions

### Display Use (typically included)

- Viewing on terminal/screen
- Manual decision-making
- Report generation for human review
- Quality assurance (visual inspection)

### Non-Display Use (typically additional license)

- Algorithmic/automated trading
- Risk model inputs
- Pricing engines
- Index calculations
- Any system-to-system use

## Real-World Terms

### CME Group

> "Non-Display Use means access to, use, or receipt of Real Time Market Data for purposes other than the support of a Subscriber's Display Use activities... including, but not limited to... automated order routing, program trading, algorithm evaluation..."

### LSEG

Distinguishes "Professional" vs "Non-Professional" subscribers with different fee structures.

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Display Use                              │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensed Trader                            │
│  Action: view, analyze (manual)                      │
│  Object: Market Data                                 │
│  Condition: useType ∈ {display, reporting}           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Prohibition: Non-Display Without License            │
│  ─────────────────────────────────────────────────  │
│  Subject: Any System                                 │
│  Prohibited Action: algorithmicUse                   │
│  Object: Market Data                                 │
│  Condition: NOT hasNonDisplayLicense                 │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

```
Request: System S wants to use data D for purpose P

1. Classify P:
   - Is P in {view, manual-analysis, reporting}? → Display
   - Is P in {algo-trading, risk-calc, pricing}? → Non-Display
   
2. Check authorization:
   - Display → Check display license
   - Non-Display → Check non-display license
   
3. If authorized → PERMIT
   If not → DENY
```

## Profile Requirements

```turtle
@prefix license: <https://example.org/profile/license#> .

license:useTypeOperand a rl2:LeftOperand ;
    rdfs:label "Use Type" ;
    rl2:resolutionPath "context.useType" .

license:DisplayUse a license:UseType .
license:NonDisplayUse a license:UseType .

license:DisplayUseTypes a rdf:List ;
    rdf:first license:View ;
    rdf:rest ( license:ManualAnalysis license:Reporting ) .
```

## Comparison with Related Use Cases

| Use Case | Focus |
|----------|-------|
| **display-vs-nondisplay** | Use type classification |
| purpose-restriction (24) | Purpose whitelist |
| internal-use-only (18) | Internal vs external |

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate isAnyOf for use type sets
```

---

## References

- CME Market Data License — Non-Display Use definition
- LSEG Professional/Non-Professional classification
- NYSE Market Data policies
