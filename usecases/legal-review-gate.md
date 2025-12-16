# Use Case 26: Legal Review Gate

**Pattern:** Multi-stage approval with policy lifecycle  
**Vocabulary Demonstrated:** `Offer`, `Agreement`, policy lifecycle  
**Category:** Data Contracts, Governance  
**Status:** DRAFT

---

## Business Context

Access to sensitive data often requires legal review before approval. This involves a state transition:

1. **Request submitted** — Prospective user asks for access
2. **Terms offered** — System presents terms (Offer)
3. **Legal review** — Legal team reviews and may modify terms
4. **Agreement formed** — User accepts, binding Agreement created
5. **Access enabled** — Privileges become active

The transition from **Offer** to **Agreement** is a key governance control.

## Scenario

A third-party vendor requests access to customer data for integration testing. Before access is granted:

1. Standard data use terms are presented (Offer)
2. Legal reviews the vendor's request and terms
3. Legal may require additional clauses
4. Vendor accepts modified terms
5. Agreement formed; access privileges activate

## Policy Intent

> "Access privileges are NOT active until legal review completes AND requestor accepts the terms."

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Offer: Proposed Access Terms                        │
│  ─────────────────────────────────────────────────  │
│  Grantor: Data Owner                                 │
│  Proposed Grantee: Vendor                            │
│  Clauses: [accessPrivilege, deletionDuty, ...]       │
│  Status: Pending review                              │
└─────────────────────────────────────────────────────┘
            │
            │ After legal review + acceptance
            ▼
┌─────────────────────────────────────────────────────┐
│  Agreement: Binding Data Contract                    │
│  ─────────────────────────────────────────────────  │
│  Grantor: Data Owner                                 │
│  Grantee: Vendor                                     │
│  Clauses: [accessPrivilege, deletionDuty, ...]       │
│  Effective: Agreement formation date                 │
└─────────────────────────────────────────────────────┘
```

## Offer vs Agreement

| Aspect | Offer | Agreement |
|--------|-------|-----------|
| **Status** | Proposed, not binding | Binding on both parties |
| **Privileges** | Not yet active | Active |
| **Duties** | Not yet enforceable | Enforceable |
| **Can be modified** | Yes, before acceptance | Only by amendment |

## State Transitions

```
         ┌──────────┐
         │  Draft   │
         └────┬─────┘
              │ submit
              ▼
         ┌──────────┐
         │  Offer   │ ◄─── Legal may request changes
         └────┬─────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌────────┐         ┌─────────┐
│Rejected│         │Accepted │
└────────┘         └────┬────┘
                        │ forms
                        ▼
                  ┌───────────┐
                  │ Agreement │
                  └───────────┘
```

## Legal Review as Event

Legal review completion is modeled as an Event:

```turtle
ex:legalReviewEvent a rl2:Event ;
    rl2:approver ex:LegalTeam ;
    rl2:eventTime "2025-01-15T14:30:00Z"^^xsd:dateTime .
```

The Agreement formation is conditioned on this event:

```turtle
ex:vendorAgreement a rl2:Agreement ;
    rl2:condition [
        a rl2:EventConstraint ;
        rl2:expectsEvent [
            a rl2:Event ;
            rl2:approver ex:LegalTeam
        ]
    ] .
```

## Evaluation Logic

```
Request: Vendor wants to access customer data

1. Find applicable policy
2. Is policy type Agreement? 
   - If Offer → privileges NOT active
   - If Agreement → continue
3. Check Agreement conditions:
   - Legal review event exists? YES/NO
   - Acceptance recorded? YES/NO
4. If all YES → privileges active
   If any NO → access denied
```

## Multi-Level Review Pattern

Complex scenarios may require sequential reviews:

```
Request → Manager Review → Legal Review → Compliance Review → Agreement
```

Each stage can be an Event with its own approver:

```turtle
rl2:condition [
    a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:and ;
    rl2:operand [
        a rl2:EventConstraint ;
        rl2:expectsEvent [ rl2:approver ex:Manager ]
    ] ;
    rl2:operand [
        a rl2:EventConstraint ;
        rl2:expectsEvent [ rl2:approver ex:LegalTeam ]
    ] ;
    rl2:operand [
        a rl2:EventConstraint ;
        rl2:expectsEvent [ rl2:approver ex:Compliance ]
    ]
] .
```

## Real-World Examples

### Enterprise Software Licensing

Before deploying third-party software:
1. Vendor offers license terms
2. Legal reviews for risk
3. Procurement negotiates pricing
4. Agreement signed

### Data Partnership

Before sharing data with partner:
1. DPA (Data Processing Agreement) offered
2. Legal reviews data protection terms
3. Privacy team approves
4. Both parties sign

### Clinical Research

Before research access to patient data:
1. Data use terms offered
2. IRB reviews ethics
3. Legal reviews liability
4. Agreement formed

## Comparison with Related Use Cases

| Use Case | Focus |
|----------|-------|
| **legal-review-gate** | Offer → Agreement lifecycle |
| ethics-approval (7) | Single approval event |
| multi-level-approval (31) | Sequential events |
| approval-revocation (27) | Power to undo |

## Profile Requirements

```turtle
@prefix contract: <https://example.org/profile/contract#> .

contract:submitRequest a rl2:Action ;
    rdfs:label "Submit Access Request" .

contract:acceptTerms a rl2:Action ;
    rdfs:label "Accept Terms" .

contract:policyStatusOperand a rl2:LeftOperand ;
    rdfs:label "Policy Status" ;
    rl2:resolutionPath "policy.rdf:type" ;
    rdfs:comment "Distinguishes Offer from Agreement." .
```

## Audit Requirements

Track the full lifecycle:
- Request submission timestamp
- Each review decision (approve/reject/modify)
- Terms modifications
- Acceptance timestamp
- Agreement effective date

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder for RL2 implementation
# Will demonstrate: Offer, Agreement, EventConstraint for approval
```

---

## References

- Contract law: Offer and acceptance doctrine
- GDPR Article 28: Data Processing Agreements
- Enterprise software procurement workflows
