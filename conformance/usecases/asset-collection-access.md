# Use Case 47: Asset Collection Access

**Pattern:** Bulk dataset access  
**Vocabulary Demonstrated:** `AssetCollection`, `member`  
**Category:** Vocabulary Completeness, Data Management  
**Status:** DRAFT

---

## Business Context

Policies often apply to groups of assets rather than individuals:

- All datasets in a catalog
- All tables in a schema
- All files in a folder
- All resources matching criteria

`AssetCollection` groups assets for collective policy application.

## Scenario

A data catalog contains multiple related datasets. A single policy governs access to the entire collection:

> "Research team may access all datasets in the 'Clinical Outcomes' collection."

## Policy Intent

> "Access is PERMITTED to any asset that is a member of the specified collection."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Grouping | Multiple assets under one policy |
| Membership | Static or dynamic |
| Inheritance | Policy applies to all members |
| Efficiency | One policy vs many |

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  AssetCollection: Clinical Outcomes                  │
│  ─────────────────────────────────────────────────  │
│  Members:                                            │
│    - PatientDemographics                             │
│    - TreatmentRecords                                │
│    - OutcomeMeasures                                 │
│    - AdverseEvents                                   │
└─────────────────────────────────────────────────────┘
            │
            │ governs
            ▼
┌─────────────────────────────────────────────────────┐
│  Privilege: Access Collection                        │
│  ─────────────────────────────────────────────────  │
│  Subject: ResearchTeam                               │
│  Action: access                                      │
│  Object: ClinicalOutcomesCollection                  │
│  Scope: All members                                  │
└─────────────────────────────────────────────────────┘
```

## Static vs Dynamic Collections

| Type | Definition | Example |
|------|------------|---------|
| **Static** | Explicit member list | Named datasets |
| **Dynamic** | Query-based membership | "All tables with PII tag" |

RL2 Core supports static membership via `rl2:member`. Dynamic membership requires profile-defined resolution.

## Evaluation Logic

```
Request: Access to dataset D

1. Is D a member of any collection with applicable policy?
2. Find policies targeting collections containing D
3. Evaluate policy conditions
4. If any collection policy permits → PERMIT
```

## Collection Membership

```turtle
ex:ClinicalOutcomesCollection a rl2:AssetCollection ;
    rl2:member ex:PatientDemographics ;
    rl2:member ex:TreatmentRecords ;
    rl2:member ex:OutcomeMeasures ;
    rl2:member ex:AdverseEvents .
```

## Nested Collections

Collections may contain other collections:

```
ResearchDataCatalog
├── ClinicalOutcomesCollection
│   ├── PatientDemographics
│   └── TreatmentRecords
└── GenomicsCollection
    ├── SequenceData
    └── VariantCalls
```

## Collection Operations

| Operation | Description |
|-----------|-------------|
| Add member | Extend collection |
| Remove member | Shrink collection |
| Union | Combine collections |
| Intersection | Common members |
| Difference | Members in A but not B |

## Policy Inheritance

When policy targets a collection, it applies to all members:

```
Policy on ClinicalOutcomesCollection applies to:
  - PatientDemographics ✓
  - TreatmentRecords ✓
  - OutcomeMeasures ✓
  - AdverseEvents ✓
```

Individual assets may have additional, more specific policies.

## Profile Requirements

```turtle
@prefix catalog: <https://example.org/profile/catalog#> .

catalog:collectionMembershipOperand a rl2:LeftOperand ;
    rdfs:label "Collection Membership" ;
    rl2:resolutionPath "asset.memberOf" .

ex:ClinicalOutcomesCollection a rl2:AssetCollection ;
    rdfs:label "Clinical Outcomes" ;
    rl2:member ex:PatientDemographics ;
    rl2:member ex:TreatmentRecords ;
    rl2:member ex:OutcomeMeasures ;
    rl2:member ex:AdverseEvents .
```

---

## RL2 Model

This model demonstrates a single Privilege whose object is an
`AssetCollection`, so the grant applies uniformly to every member
dataset without a separate norm per asset.

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

# ── AssetCollection: the governed group of datasets ──────────────
ex:ClinicalOutcomesCollection a rl2:AssetCollection ;
    rdfs:label "Clinical Outcomes" ;
    rl2:member ex:PatientDemographics ;
    rl2:member ex:TreatmentRecords ;
    rl2:member ex:OutcomeMeasures ;
    rl2:member ex:AdverseEvents .

# ── Privilege: access applies to the collection as a whole ──────
ex:collectionAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:ResearchTeam ;
    rl2:action ex:access ;
    rl2:object ex:ClinicalOutcomesCollection .

ex:access a rl2:Action ;
    rdfs:label "Access" .

ex:catalogPolicy a rl2:Set ;
    rl2:grantor ex:DataCatalog ;
    rl2:clause ex:collectionAccessPrivilege .
```

---

## References

- ODRL — Asset and AssetCollection
- DCAT — Dataset and Catalog
- Data catalog design patterns
