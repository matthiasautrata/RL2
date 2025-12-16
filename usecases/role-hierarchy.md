# Use Case 46: Role Hierarchy

**Pattern:** Type-based access control  
**Vocabulary Demonstrated:** `isA` operator  
**Category:** Vocabulary Completeness, RBAC  
**Status:** DRAFT

---

## Business Context

Access control often uses role hierarchies:

- Senior roles inherit junior role permissions
- Type hierarchies (Manager isA Employee)
- Asset classifications (ConfidentialDoc isA Document)

The `isA` operator checks type membership, including subtypes.

## Scenario

A document management system uses classification hierarchy:

```
Document
├── InternalDocument
│   ├── ConfidentialDocument
│   └── RestrictedDocument
└── PublicDocument
```

Policy: "Managers may access any InternalDocument (including subtypes)."

## Policy Intent

> "Access is PERMITTED if document type IS-A InternalDocument."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Operator | Type membership check |
| Inheritance | Includes subtypes |
| Hierarchy | Uses rdfs:subClassOf or similar |
| Semantic | Requires reasoning |

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Access Internal Documents               │
│  ─────────────────────────────────────────────────  │
│  Subject: Manager                                    │
│  Action: access                                      │
│  Object: Documents                                   │
│  Condition:                                          │
│    document.type isA InternalDocument                │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

```
Given document D with type T
Check: T isA InternalDocument

isA(T, InternalDocument) evaluates to:
  - TRUE if T = InternalDocument
  - TRUE if T is a subclass of InternalDocument
  - FALSE otherwise

Document type: ConfidentialDocument
  - ConfidentialDocument subClassOf InternalDocument? YES
  - isA = TRUE → PERMIT

Document type: PublicDocument
  - PublicDocument subClassOf InternalDocument? NO
  - isA = FALSE → DENY
```

## Type Hierarchies

### Role Hierarchy
```
Employee
├── Manager
│   └── SeniorManager
└── Contractor
```

### Asset Classification
```
Asset
├── Data
│   ├── PersonalData
│   └── FinancialData
└── Document
    ├── Contract
    └── Report
```

### Action Hierarchy
```
Action
├── Read
├── Write
│   ├── Create
│   ├── Update
│   └── Delete
└── Execute
```

## isA vs isAnyOf

| Operator | Mechanism | Use Case |
|----------|-----------|----------|
| `isA` | Type hierarchy | Role/class inheritance |
| `isAnyOf` | Set membership | Flat list of values |

```
# isA: Uses type hierarchy
document.type isA InternalDocument
# Matches: InternalDocument, ConfidentialDocument, RestrictedDocument

# isAnyOf: Explicit list
document.type isAnyOf {InternalDocument, ConfidentialDocument, RestrictedDocument}
# Matches: Only those three, no inference
```

## Semantic Requirements

`isA` requires type hierarchy to be defined:

```turtle
ex:ConfidentialDocument rdfs:subClassOf ex:InternalDocument .
ex:InternalDocument rdfs:subClassOf ex:Document .
```

The evaluator must support subclass reasoning (or pre-compute transitive closure).

## Profile Requirements

```turtle
@prefix docclass: <https://example.org/profile/docclass#> .

docclass:documentTypeOperand a rl2:LeftOperand ;
    rl2:resolutionPath "asset.rdf:type" .

docclass:Document a rdfs:Class .
docclass:InternalDocument a rdfs:Class ;
    rdfs:subClassOf docclass:Document .
docclass:ConfidentialDocument a rdfs:Class ;
    rdfs:subClassOf docclass:InternalDocument .
docclass:PublicDocument a rdfs:Class ;
    rdfs:subClassOf docclass:Document .
```

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate isA operator with type hierarchy
```

---

## References

- ODRL Vocabulary — isA operator
- RBAC role hierarchies
- RDF Schema — subClassOf
- OWL — Class hierarchies
