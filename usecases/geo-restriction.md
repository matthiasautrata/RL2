# Use Case 25: Geographic Restriction

**Pattern:** Jurisdiction blacklist/whitelist  
**Vocabulary Demonstrated:** `isNoneOf`, `isAnyOf` (depending on approach)  
**Category:** Data Sovereignty, Compliance  
**Status:** DRAFT

---

## Business Context

Data sovereignty laws require controlling where data is accessed from:

- **GDPR:** Restrictions on transfers outside EU/EEA
- **China PIPL:** Data localization requirements
- **US State Laws:** Varying privacy requirements
- **Sanctions:** OFAC restrictions on certain countries

Geographic restrictions are a fundamental control in data licensing and compliance.

## Scenario

A European bank's customer data may only be accessed from approved jurisdictions. Access from sanctioned countries (Russia, North Korea, Iran) is prohibited regardless of user authorization.

## Policy Intent

### Blacklist Approach
> "Access is DENIED if request originates from a prohibited jurisdiction."

### Whitelist Approach
> "Access is PERMITTED only if request originates from an approved jurisdiction."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Constraint type | Set membership (inclusion/exclusion) |
| Enforcement point | Request time |
| Resolution | IP geolocation, declared location, or both |
| Override | Emergency access may bypass (with logging) |

## Blacklist vs Whitelist

| Approach | Use Case | Operator |
|----------|----------|----------|
| **Blacklist** | Sanctions (block specific countries) | `isNoneOf` |
| **Whitelist** | Data sovereignty (allow only approved) | `isAnyOf` |

## Normative Structure (Blacklist)

```
┌─────────────────────────────────────────────────────┐
│  Prohibition: Access from Sanctioned Countries       │
│  ─────────────────────────────────────────────────  │
│  Subject: Any User                                   │
│  Prohibited Action: access                           │
│  Object: Customer Data                               │
│  Condition: jurisdiction ∈ {RU, KP, IR, ...}         │
└─────────────────────────────────────────────────────┘
```

## Normative Structure (Whitelist)

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Access Customer Data                     │
│  ─────────────────────────────────────────────────  │
│  Subject: Authorized User                            │
│  Action: access                                      │
│  Object: Customer Data                               │
│  Condition: jurisdiction ∈ {EU, CH, UK, ...}         │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

### Blacklist
```
Request: User from jurisdiction J wants to access data

1. Resolve J from request context
2. Check: J ∈ {RU, KP, IR, SY, CU}?
   - If YES → DENY (sanctioned)
   - If NO → continue other checks
```

### Whitelist
```
Request: User from jurisdiction J wants to access data

1. Resolve J from request context
2. Check: J ∈ {EU-countries, CH, UK}?
   - If YES → continue other checks
   - If NO → DENY (not approved)
```

## Jurisdiction Resolution

Multiple sources may determine jurisdiction:

| Source | Method | Reliability |
|--------|--------|-------------|
| IP geolocation | MaxMind, IP2Location | Medium (VPN bypass) |
| User declaration | Profile attribute | Low (trust-based) |
| Device location | GPS, network | Medium-High |
| Office location | HR system | High |
| Contract location | Legal entity | High |

## Combining Multiple Sources

```turtle
rl2:condition [
    a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:and ;
    rl2:operand [
        # IP-based check
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:ipJurisdictionOperand ;
        rl2:constraintOperator rl2:isNoneOf ;
        rl2:rightOperand (ex:RU ex:KP ex:IR)
    ] ;
    rl2:operand [
        # Declared location check
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:declaredJurisdictionOperand ;
        rl2:constraintOperator rl2:isNoneOf ;
        rl2:rightOperand (ex:RU ex:KP ex:IR)
    ]
] .
```

## Real-World Examples

### GDPR Data Transfers

EU personal data may only be transferred to:
- EU/EEA countries (automatic)
- Adequacy decision countries (UK, Switzerland, Japan, etc.)
- With appropriate safeguards (SCCs, BCRs)

### OFAC Sanctions

US persons may not provide services to:
- North Korea, Iran, Syria, Cuba
- Crimea region
- Certain designated entities

### Bloomberg Data License

From Bloomberg terms:
> "Distributor shall not... export, re-export, divert or transfer... to any country, territory, or entity prohibited by OFAC."

### IDS Data Spaces

Geographic constraints are a core IDS policy pattern for ensuring data remains within approved jurisdictions.

## Edge Cases

| Scenario | Handling |
|----------|----------|
| VPN masking true location | Layer multiple signals |
| Traveling employee | Use primary work location |
| Multi-jurisdiction entity | Apply strictest applicable |
| Unknown jurisdiction | Fail closed (deny) |

## Comparison with Related Use Cases

| Use Case | Operator | Focus |
|----------|----------|-------|
| **geo-restriction** | `isNoneOf` / `isAnyOf` | Jurisdiction sets |
| purpose-restriction (24) | `isAnyOf` | Purpose sets |
| role-hierarchy (46) | `isA` | Type membership |

## Profile Requirements

```turtle
@prefix compliance: <https://example.org/profile/compliance#> .

compliance:jurisdictionOperand a rl2:LeftOperand ;
    rdfs:label "Request Jurisdiction" ;
    rl2:resolutionPath "context.jurisdiction" ;
    rdfs:comment "ISO 3166-1 alpha-2 country code of request origin." .

compliance:ipJurisdictionOperand a rl2:LeftOperand ;
    rdfs:label "IP-based Jurisdiction" ;
    rl2:resolutionPath "context.ipGeolocation.country" .

# Jurisdiction sets
compliance:SanctionedCountries a rdf:List ;
    rdf:first "RU" ; rdf:rest ( "KP" "IR" "SY" "CU" ) .

compliance:EUCountries a rdf:List ;
    rdf:first "AT" ; rdf:rest ( "BE" "BG" ... "SE" ) .
```

## Audit Requirements

Geographic access should be logged:
- Resolved jurisdiction
- Resolution method (IP, declared, etc.)
- Decision (permit/deny)
- If denied, which restriction triggered

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder for RL2 implementation
# Will demonstrate: isNoneOf for blacklist, isAnyOf for whitelist
```

---

## References

- GDPR Chapter V — Transfers to third countries
- OFAC Sanctions Programs — US Treasury
- ISO 3166-1 — Country codes
- IDS Reference Architecture — Location constraints
