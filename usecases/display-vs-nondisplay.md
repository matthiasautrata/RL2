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

This model demonstrates `isAnyOf` classifying the requested use type
against a whitelist of display uses, alongside a Prohibition on
algorithmic (non-display) use absent a separate license.

```turtle
@prefix ex: <https://example.org/> .
@prefix license: <https://example.org/profile/license#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ── Display use types (whitelist) ─────────────────────────────────
ex:DisplayUseTypes a rl2:AssetCollection ;
    rdfs:label "Display Use Types" ;
    rl2:member ex:View, ex:ManualAnalysis, ex:Reporting .

# ── Privilege: display use is permitted under the base license ────
ex:displayUsePrivilege a rl2:Privilege ;
    rl2:subject ex:LicensedTrader ;
    rl2:action ex:useData ;
    rl2:object ex:MarketData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand license:useTypeOperand ;
        rl2:constraintOperator rl2:isAnyOf ;
        rl2:rightOperandRef ex:DisplayUseTypes
    ] .

ex:useData a rl2:Action ;
    rdfs:label "Use Data" .

# ── Prohibition: algorithmic (non-display) use without a license ──
ex:nonDisplayProhibition a rl2:Prohibition ;
    rl2:subject ex:AnySystem ;
    rl2:prohibitedAction ex:algorithmicUse ;
    rl2:object ex:MarketData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:hasNonDisplayLicenseOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "false"^^xsd:boolean
    ] .

ex:algorithmicUse a rl2:Action ;
    rdfs:label "Algorithmic Use" .

ex:hasNonDisplayLicenseOperand a rl2:LeftOperand ;
    rdfs:label "Has Non-Display License" ;
    rl2:resolutionPath "context.licensee.hasNonDisplayLicense" ;
    rdfs:range xsd:boolean .

ex:marketDataLicense a rl2:Agreement ;
    rl2:grantor ex:DataVendor ;
    rl2:grantee ex:Bank ;
    rl2:clause ex:displayUsePrivilege, ex:nonDisplayProhibition .
```

---

## References

- CME Market Data License — Non-Display Use definition
- LSEG Professional/Non-Professional classification
- NYSE Market Data policies
