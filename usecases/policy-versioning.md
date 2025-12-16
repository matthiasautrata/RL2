# Use Case 49: Policy Versioning

**Pattern:** Generation tracking  
**Vocabulary Demonstrated:** `policyGeneration`  
**Category:** Vocabulary Completeness, Governance  
**Status:** DRAFT

---

## Business Context

Policies change over time. Tracking versions is essential for:

- **Audit:** Which policy governed a past decision?
- **Migration:** Transitioning from old to new terms
- **Rollback:** Reverting problematic changes
- **Compliance:** Proving what rules applied when

## Scenario

An organization updates its data use policy quarterly. Each version is tracked:

> "This policy (Generation Q4-2025) supersedes Generation Q3-2025. Existing agreements under Q3-2025 remain valid until renewal."

## Policy Intent

> "Policies are versioned. Decisions reference the applicable generation."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Identifier | Unique generation ID |
| Lineage | Link to previous/next versions |
| Effective period | When this version applies |
| Coexistence | Multiple versions may be active |

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Policy: Data Use Policy (Q4-2025)                  │
│  ─────────────────────────────────────────────────  │
│  policyGeneration: https://example.org/policy/v4    │
│  effectiveFrom: 2025-10-01                          │
│  effectiveTo: 2025-12-31                            │
│  replaces: https://example.org/policy/v3            │
│  clauses: [...]                                      │
└─────────────────────────────────────────────────────┘
            │
            │ supersedes
            ▼
┌─────────────────────────────────────────────────────┐
│  Policy: Data Use Policy (Q3-2025)                  │
│  ─────────────────────────────────────────────────  │
│  policyGeneration: https://example.org/policy/v3    │
│  effectiveFrom: 2025-07-01                          │
│  effectiveTo: 2025-09-30                            │
│  status: Superseded                                  │
└─────────────────────────────────────────────────────┘
```

## Version Relationships

| Relationship | Meaning |
|--------------|---------|
| `replaces` | This version supersedes another |
| `replacedBy` | This version is superseded by another |
| `derivedFrom` | Based on another policy |
| `sameAs` | Identical content, different ID |

## Evaluation with Versions

```
Decision made at time T

1. Find applicable policy generation for time T
2. Use that generation's rules for evaluation
3. Record generation ID in decision log

Future audit:
1. Retrieve decision record
2. Look up generation ID
3. Reconstruct evaluation with that version
```

## Version Coexistence

Multiple generations may be active simultaneously:

```
Time T:
  - New agreements: Use v4 (current)
  - Existing v3 agreements: Still valid under v3
  - Legacy v2 agreements: Grandfathered
```

## ODRL Temporal Profile

The ODRL Temporal Profile provides `TemporalPolicy` with versioning:

```turtle
ex:temporalPolicy a tpl:TemporalPolicy ;
    pav:hasVersion ex:policy-v1, ex:policy-v2, ex:policy-v3 .

ex:policy-v3 a odrl:Agreement ;
    tpl:effectiveFrom "2025-10-01"^^xsd:dateTime ;
    tpl:effectiveTo "2025-12-31"^^xsd:dateTime .
```

## Audit Trail Integration

Each evaluation decision should record:

```turtle
ex:decision123 a rl2p:Decision ;
    rl2p:basedOnPolicy ex:dataUsePolicy ;
    rl2p:policyGeneration <https://example.org/policy/v4> ;
    rl2p:evaluatedAt "2025-10-15T14:30:00Z"^^xsd:dateTime ;
    rl2p:result rl2p:Permit .
```

## Profile Requirements

```turtle
@prefix versioning: <https://example.org/profile/versioning#> .

versioning:policyGenerationOperand a rl2:LeftOperand ;
    rl2:resolutionPath "policy.policyGeneration" .

versioning:effectiveFromOperand a rl2:LeftOperand ;
    rl2:resolutionPath "policy.effectiveFrom" .

versioning:effectiveToOperand a rl2:LeftOperand ;
    rl2:resolutionPath "policy.effectiveTo" .
```

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate policyGeneration property
```

---

## References

- ODRL Temporal Profile
- PAV (Provenance, Authoring, Versioning) ontology
- Semantic versioning principles
- Legal document version control
