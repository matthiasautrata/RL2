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

For comparison, the ODRL Temporal Profile expresses versioning with `TemporalPolicy`
(foreign vocabulary, shown here only as a contrast — not RL2):

```
ex:temporalPolicy a tpl:TemporalPolicy ;
    pav:hasVersion ex:policy-v1, ex:policy-v2, ex:policy-v3 .

ex:policy-v3 a odrl:Agreement ;
    tpl:effectiveFrom "2025-10-01"^^xsd:dateTime ;
    tpl:effectiveTo "2025-12-31"^^xsd:dateTime .
```

## Audit Trail Integration

Each case records the generation it was evaluated under via the protocol property
`rl2p:policyGeneration` (`xsd:anyURI`, immutable once the case is created), so any
past decision can be reconstructed against the exact rules then in force. The
complete `rl2p:Case` model — with its initial request, status, and evaluation
history — is shown in the protocol use cases (`runtime-evaluation`, `audit-trail`);
here we only note that the generation identifier flows from policy to case record.

## Profile Requirements

Versioning needs **no profile-declared operands**. Generation identity is carried
by the core datatype property `rl2:policyGeneration` (policy metadata, not a
runtime operand), and the effective window is expressed with the core temporal
operand `rl2:currentDateTime` compared against literal bounds — the standard
temporal pattern. Generation selection for a given decision time is performed by
the evaluation pipeline (applicable-policy selection), not by a clause condition.

---

## RL2 Model

Each generation is a policy stamped with `rl2:policyGeneration` and bounded by an
effective window expressed via `rl2:currentDateTime`. Multiple generations coexist;
the pipeline selects the one in force at the decision time.

```turtle
# Generation Q4-2025 (current)
ex:dataUsePolicyV4 a rl2:Policy ;
    rl2:policyGeneration "https://example.org/policy/gen/2025-Q4"^^xsd:anyURI ;
    rl2:clause ex:v4UsePrivilege .

ex:v4UsePrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:use ;
    rl2:object ex:Dataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand rl2:currentDateTime ;
            rl2:constraintOperator rl2:gte ;
            rl2:rightOperand "2025-10-01T00:00:00Z"^^xsd:dateTimeStamp
        ] ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand rl2:currentDateTime ;
            rl2:constraintOperator rl2:lte ;
            rl2:rightOperand "2025-12-31T23:59:59Z"^^xsd:dateTimeStamp
        ]
    ] .

# Generation Q3-2025 (superseded, still governs its existing agreements)
ex:dataUsePolicyV3 a rl2:Policy ;
    rl2:policyGeneration "https://example.org/policy/gen/2025-Q3"^^xsd:anyURI ;
    rl2:clause ex:v3UsePrivilege .

ex:v3UsePrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:use ;
    rl2:object ex:Dataset .
```

Each case records the generation it was evaluated under (see *Audit Trail
Integration* above).

---

## References

- ODRL Temporal Profile
- PAV (Provenance, Authoring, Versioning) ontology
- Semantic versioning principles
- Legal document version control
