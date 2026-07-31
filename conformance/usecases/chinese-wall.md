# Use Case 15: Chinese Wall (Embargo)

**Pattern:** Event-based prohibition expiry
**Identity Check:** Role/department membership
**Category:** Financial Entitlements, Conflict of Interest

## Scenario

Investment Bankers cannot view Research Analyst drafts until the "Publication" event occurs. Once published, the embargo lifts and bankers may access the research.

## Policy Intent

> "Research drafts are embargoed from Investment Banking until publication."

## Key Characteristics

- **Prohibition** with event-based expiry
- Conflict of interest prevention
- Temporal boundary (publication event)
- Role-based subject restriction

## Why RL2?

The policy is a `Prohibition` that explicitly expires upon receipt of a `PublicationEvent`. ODRL can express prohibitions but cannot model:
- Event-based lifting of prohibitions
- The transition from "embargoed" to "available"
- The dependency on an external event

RL2's `EventConstraint` and temporal conditions via `currentDateTime` provide the necessary machinery.

## Profile-Declared Operands

```turtle
@prefix finance: <https://example.org/profile/finance#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

finance:researchStatusOperand a rl2:LeftOperand ;
    rdfs:label "Research Status" ;
    rdfs:comment "Publication status of research document." ;
    rl2:resolutionPath "asset.publicationStatus" ;
    rdfs:range finance:PublicationStatus .

finance:agentDepartmentOperand a rl2:LeftOperand ;
    rdfs:label "Agent Department" ;
    rdfs:comment "Department of the requesting agent." ;
    rl2:resolutionPath "agent.department" ;
    rdfs:range finance:Department .

# Publication status values
finance:Draft a finance:PublicationStatus .
finance:Published a finance:PublicationStatus .

# Department values
finance:InvestmentBanking a finance:Department .
finance:Research a finance:Department .

# Actions
finance:read a rl2:Action ;
    rdfs:label "Read" ;
    rdfs:comment "Read access to financial documents." .
```

## RL2 Model

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix finance: <https://example.org/profile/finance#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Event template for publication
ex:PublicationEvent a rl2:Event ;
    rdfs:comment "Triggered when research is officially published." .

# Embargo: Investment Banking cannot view draft research
# Note: No priority needed - conditions are mutually exclusive with privilege (Draft vs Published)
ex:researchEmbargo a rl2:Prohibition ;
    rl2:subject ex:InvestmentBanker ;
    rl2:prohibitedAction finance:read ;
    rl2:object ex:ResearchReport ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Agent is in Investment Banking
            a rl2:AtomicConstraint ;
            rl2:leftOperand finance:agentDepartmentOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef finance:InvestmentBanking
        ] ;
        rl2:operand [
            # Research is still in draft
            a rl2:AtomicConstraint ;
            rl2:leftOperand finance:researchStatusOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef finance:Draft
        ]
    ] .

# After publication: Embargo lifts
ex:publishedResearchAccess a rl2:Privilege ;
    rl2:subject ex:InvestmentBanker ;
    rl2:action finance:read ;
    rl2:object ex:ResearchReport ;
    rl2:condition [
        # Research is published
        a rl2:AtomicConstraint ;
        rl2:leftOperand finance:researchStatusOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef finance:Published
    ] .

# Research analysts can always access their own work
# Note: Different subject class (ResearchAnalyst), no conflict with InvestmentBanker norms
ex:researchAnalystAccess a rl2:Privilege ;
    rl2:subject ex:ResearchAnalyst ;
    rl2:action finance:read ;
    rl2:object ex:ResearchReport .
```

## State Transitions

```
Research Document Lifecycle:

    ┌──────────┐                      ┌───────────┐
    │  DRAFT   │   PublicationEvent   │ PUBLISHED │
    │          │─────────────────────▶│           │
    │ IB: DENY │                      │ IB: PERMIT│
    │ RA: OK   │                      │ RA: OK    │
    └──────────┘                      └───────────┘
```

## Evaluation

| Scenario | Requester | Document Status | Result |
|----------|-----------|-----------------|--------|
| Analyst views draft | Research Analyst | Draft | PERMIT |
| Banker views draft | Investment Banker | Draft | DENY (Embargo) |
| Banker views published | Investment Banker | Published | PERMIT |
| Compliance views draft | Compliance | Draft | PERMIT (different rule) |

## Regulatory Context

This pattern implements the "Chinese Wall" (now often called "Information Barrier") required by:
- SEC regulations for broker-dealers
- MiFID II for investment firms
- FINRA rules on research independence

The wall prevents conflicts of interest where investment banking activity could influence research recommendations.

## Alternative: Event-Based Model

Instead of status polling, an event-driven model could use a profile-declared operand:

```turtle
# Profile operand for checking event occurrence
finance:publicationEventOccurredOperand a rl2:LeftOperand ;
    rdfs:label "Publication Event Occurred" ;
    rdfs:comment "Whether the publication event has occurred for this asset." ;
    rl2:resolutionPath "state.Events.PublicationEvent.exists" ;
    rdfs:range xsd:boolean .

# Embargo active until publication event received
ex:researchEmbargoEventBased a rl2:Prohibition ;
    rl2:subject ex:InvestmentBanker ;
    rl2:prohibitedAction finance:read ;
    rl2:object ex:ResearchReport ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand finance:agentDepartmentOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef finance:InvestmentBanking
        ] ;
        rl2:operand [
            # Publication event has NOT occurred
            a rl2:AtomicConstraint ;
            rl2:leftOperand finance:publicationEventOccurredOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand false
        ]
    ] .
```

## Comparison

| Aspect | Manual Process | ODRL | RL2 |
|--------|----------------|------|-----|
| Embargo expression | Physical separation | Prohibition (static) | Prohibition + condition |
| Event-based lifting | Manual notification | Not supported | EventConstraint |
| Role-based targeting | Access lists | Subject constraints | Profile operand |
| Audit trail | Separate system | Not built-in | Event log |

## PNF Considerations

This use case requires:
- Status/attribute checking (propositional)
- Role hierarchy traversal (if "Investment Banker" is a role class)
- Event occurrence tracking

The role hierarchy check may require transitive closure over `memberOf` or `hasRole` relations — confirming the "propositional + bounded transitive closure" semantic class.
