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
| Hierarchy | `rdfs:subClassOf` for classes (roles, assets); `rl2:includedIn` for actions |
| Semantic | Requires reasoning or transitive traversal |

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

`isA` requires a type hierarchy to be defined. The mechanism depends on the kind of entity:

- **Asset/Role hierarchies** use `rdfs:subClassOf` (assets and roles are classes):

```turtle
ex:ConfidentialDocument rdfs:subClassOf ex:InternalDocument .
ex:InternalDocument rdfs:subClassOf ex:Document .
```

- **Action hierarchies** use `rl2:includedIn` (actions are individuals):

```turtle
ex:Create a rl2:Action ; rl2:includedIn ex:Write .
ex:Update a rl2:Action ; rl2:includedIn ex:Write .
ex:Delete a rl2:Action ; rl2:includedIn ex:Write .
ex:Write  a rl2:Action .
```

The evaluator must support transitive traversal (or pre-compute transitive closure).

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

This model demonstrates `isA` matching a document's declared class
against `InternalDocument`, so the Privilege covers both the class
itself and its subclasses (e.g. `ConfidentialDocument`).

```turtle
@prefix ex: <https://example.org/> .
@prefix docclass: <https://example.org/profile/docclass#> .
@prefix rl2: <https://rl2.example/ontology#> .

# ── Privilege: managers may access internal documents (and subtypes) ──
ex:accessInternalDocsPrivilege a rl2:Privilege ;
    rl2:subject ex:Manager ;
    rl2:action ex:access ;
    rl2:object ex:Documents ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand docclass:documentTypeOperand ;
        rl2:constraintOperator rl2:isA ;
        rl2:rightOperandRef docclass:InternalDocument
    ] .

ex:access a rl2:Action ;
    rdfs:label "Access" .

ex:documentAccessPolicy a rl2:Set ;
    rl2:grantor ex:DocumentManagementSystem ;
    rl2:clause ex:accessInternalDocsPrivilege .
```

---

## References

- ODRL Vocabulary — isA operator
- RBAC role hierarchies
- RDF Schema — subClassOf
- OWL — Class hierarchies
