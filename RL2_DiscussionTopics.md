# RL2 Discussion Topics

*Future design decisions and enhancements under consideration*

---

## 1. Alignment Modules for Standard Vocabularies

**Status**: Under discussion

**Background**: RL2 follows a "standalone" design principle, not importing external ontologies to ensure semantic stability. However, Semantic Web best practices encourage reuse and alignment with established vocabularies.

**Proposal**: Create a separate `RL2_Alignment.md` (or alignment module) containing `owl:equivalentClass` and `rdfs:subClassOf` axioms mapping RL2 concepts to standard vocabularies:

| RL2 Concept | Standard Vocabulary |
|-------------|---------------------|
| `rl2:Case`, `rl2:Event` | PROV-O (`prov:Activity`, `prov:Entity`) |
| `rl2:EffectiveInterval` | OWL-Time (`time:Interval`) |
| `rl2:Agent` | FOAF (`foaf:Agent`) |

**Benefits**:
- Enables interoperability with PROV-based provenance systems
- Allows temporal reasoning using OWL-Time tooling
- Preserves standalone core while enabling alignment when needed

**Considerations**:
- Alignment module would be optional—core RL2 remains self-contained
- Requires careful axiom design to avoid unintended inferences
- Version management for alignment as external standards evolve

---

## 2. Common Profile for Baseline Actions and Operands

**Status**: Under discussion

**Background**: RL2 Core intentionally does not define specific actions or left operands, delegating these to domain profiles. This ensures flexibility but may hinder interoperability between implementations using different profile vocabularies.

**Proposal**: Create an `RL2_CommonProfile.md` defining a baseline vocabulary of commonly-used actions and operands:

**Actions** (candidates):
- `rl2common:use` - General exercise or consumption
- `rl2common:read` - Read/view access
- `rl2common:modify` - Alter or update
- `rl2common:transfer` - Transfer to third party
- `rl2common:delete` - Remove or destroy

**Left Operands** (candidates):
- `rl2common:dateTime` - Current timestamp
- `rl2common:purpose` - Declared purpose of access
- `rl2common:recipient` - Intended recipient
- `rl2common:spatial` - Geographic location

**Benefits**:
- Ensures baseline interoperability between implementations
- Provides concrete examples for implementers
- Enables ODRL policy compilation without profile-specific mappings

**Considerations**:
- Must be clearly marked as "common" not "required"
- Domain profiles may still define more specific vocabularies
- Namespace: `rl2common:` vs including in `rl2:` core

---

## 3. Explicit Rejection/Disapproval Semantics

**Status**: Under discussion

**Background**: RL2 currently models approval as the *presence* of an approval event in `Σ.Events`. An `EventConstraint` evaluates to true when a matching event exists. However, there is no explicit mechanism for modeling *disapproval* or *rejection*.

**The Problem**: Active disapproval is semantically distinct from the absence of approval:
- Absence: Request pending, awaiting response, may timeout
- Rejection: Explicit "no", request should be denied, logged for audit

Real workflows need to distinguish these cases. A DataOwner clicking "Reject" should:
- Immediately terminate the request (Case → Denied)
- Be recorded for compliance/audit
- Potentially block re-submission for some period
- Possibly trigger escalation or appeal workflows

**Possible Approaches**:

1. **Separate Rejection Event Type**
   ```turtle
   ex:rejectionEvent a rl2:RejectionEvent ;
       rl2:rejector ex:DataOwner ;
       rl2:reason "Data too sensitive for stated purpose" .
   ```

2. **Event with Outcome Property**
   ```turtle
   ex:approvalEvent a rl2:ApprovalEvent ;
       rl2:approver ex:DataOwner ;
       rl2:outcome rl2:Rejected .  # or rl2:Approved
   ```

3. **Rejection as Prohibition Activation**
   - Disapproval creates/activates a Prohibition that blocks access
   - More compositional but potentially complex

**Considerations**:
- Should rejection be a subclass of Event or a distinct concept?
- How does rejection interact with the Case lifecycle?
- Should EventConstraint have explicit "approved" vs "not rejected" semantics?
- Appeal/override workflows after rejection

---

## 4. Policy Inheritance (odrl:inheritFrom)

**Status**: Under discussion — skeptical

**Background**: ODRL 2.2 supports `odrl:inheritFrom`, allowing a child policy to inherit rules from a parent policy. RL2 currently has no equivalent construct.

**The Problem with Inheritance**:

Policy inheritance introduces complexity that may not be justified:

1. **Flattening required**: To evaluate an inherited policy, you must first "flatten" it by resolving all inheritance chains into atomic rules. If you have to decompose back to atomic policies for processing, why have inheritance?

2. **Override semantics are ambiguous**: What happens when a child policy has a rule that conflicts with an inherited rule? ODRL doesn't fully specify this.

3. **Complexity vs. value**: If you want multiple policies to apply to the same asset, simply create multiple policies. The evaluation semantics for multiple applicable policies are clearer than inheritance semantics.

4. **Auditability**: Inherited policies are harder to audit — you must trace the inheritance chain to understand what rules actually apply.

**Current Position**: RL2 does not support policy inheritance. If multiple policies should apply to an asset, create them as separate policies and let the evaluator handle policy composition via the existing conflict resolution mechanisms.

**If inheritance is needed**: A future version could add `rl2:refines` with explicit semantics:
- Child clauses override parent clauses with same subject/action/object
- Non-conflicting clauses are merged
- Flattening algorithm specified formally

**Recommendation**: Avoid inheritance. Use explicit policy composition instead.

---

## 5. Dynamic Policy Applicability

**Status**: ✅ **Integrated**

This topic has been fully integrated into the RL2 specification:

- **RL2_Core.md**: `rl2:condition` domain extended to include Policy; `rl2:policyGeneration` property added
- **RL2_Semantics.md**: §Policy-Level Activation, §Policy Generations, §Expressive Characterization
- **RL2_Protocol.md**: §Re-evaluation Triggers
- **RL2_White_Paper.md**: "Show Me: Dynamic Workflows" example

**Key insight**: Events don't branch duties — they change which policies apply. This compositional approach fits RL2's architecture naturally without introducing CTL-style branching.

---

## 6. Expressive Completeness

**Status**: ✅ **Integrated** — See RL2_Semantics.md §Expressive Characterization

The formal characterization of RL2's expressive power is now documented in the Semantics specification.

**Open questions for future work**:
- Should RL2 extend to CTL-level expressiveness, or is LTL sufficient?
- Repeating/periodic obligations ("every month")
- Quorum approvals ("any 2 of 5 committee members")

---

## 7. RL2 for Data Contracts

**Status**: Under discussion

**Background**: Data contract ontologies like DCON (Data Contract Ontology) define contracts between data providers and consumers, specifying delivery schedules, schema guarantees, and change notification commitments. These ontologies typically extend ODRL with Promise-based semantics.

**Key Insight**: RL2 already includes Promise Theory as a core layer, making it a natural fit for data contracts without requiring a separate ontology.

**Core Formula**:

> **SLO = Promise + Measurable Condition + Time Window + Remedy**

This maps directly to RL2's existing constructs—no extensions required.

### DCON → RL2 Mapping

| DCON Concept | RL2 Equivalent |
|--------------|----------------|
| `dcon:DataContract` (extends `odrl:Offer`) | `rl2:Offer` |
| `dcon:DataContractSubscription` (extends `odrl:Agreement`) | `rl2:Agreement` |
| `dcon:Promise` | `rl2:Promise` |
| `dcon:ProviderPromise` | `rl2:Promise` with `rl2:promiser` |
| `dcon:hasEffectivePeriod` | `rl2:TemporalConstraint` + `rl2:EffectiveInterval` |
| `dcon:Status` (Pending/Active/Retired) | `rl2:ObligationState` or Protocol `CaseStatus` |

DCON's specialized promise types (`ProviderTimelinessPromise`, `ProviderSchemaPromise`, `ProviderChangeNotificationPromise`) are domain-specific patterns that map to RL2 promises with appropriate conditions.

### SLO and Data Quality Integration

Service Level Objectives (SLOs) and W3C Data Quality Vocabulary (DQV) integrate naturally:

**SLOs as Promises with Measurable Conditions:**

```turtle
ex:AvailabilitySLO a rl2:Promise ;
    rl2:promiser :PlatformTeam ;
    rl2:promisee :Consumer ;
    rl2:promiseContent ex:maintainService ;
    rl2:condition [
        a rl2:Condition ;
        rl2:leftOperand rl2q:availability ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperand "99.9"^^xsd:decimal
    ] .
```

**DQV Alignment:**

DQV is **descriptive** (what was measured), RL2 is **normative** (what should be measured and what happens when it isn't). They interlock:

| Concept | DQV | RL2 |
|---------|-----|-----|
| What is measured? | `dqv:Metric` | `rl2:LeftOperand` |
| What dimension? | `dqv:Dimension` | Operand categories (profiles) |
| What is the observed value? | `dqv:value` | Resolved via `resolve(leftOperand, Env)` |
| Where are measurements stored? | DQV measurement graph | RL2 Σ.State or external context |
| What *should* the value be? | ❌ | `rl2:Condition` with threshold |
| What happens on violation? | ❌ | `rl2:Duty` / `rl2:Claim` / `rl2:Power` |

**Alignment recommendation**: Use `rdfs:subClassOf` rather than `owl:equivalentClass`:

```turtle
rl2q:QualityLeftOperand rdfs:subClassOf rl2:LeftOperand, dqv:Metric .
```

This allows RL2 operands that are *not* quality metrics (e.g., access context operands).

**What RL2 adds beyond DQV:**

- Define thresholds/targets (as conditions)
- Express commitments (as Promises)
- Define violation consequences (as Duties, Claims)
- Track obligation lifecycle (operational semantics)
- Formal verification (mechanization)

### Data Product Example

A `dprod:DataProduct` with multiple output ports, covered by a single RL2 offer with port-specific promises:

```turtle
@prefix rl2:    <https://rl2.example/ontology#> .
@prefix rl2dc:  <https://rl2.example/datacontracts#> .
@prefix dprod:  <https://ekgf.github.io/data-product-spec/dprod/> .
@prefix dcat:   <http://www.w3.org/ns/dcat#> .
@prefix ex:     <https://example.org/> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .

# === The Data Product ===

ex:CustomerDataProduct a dprod:DataProduct ;
    rdfs:label "Customer Master Data Product" ;
    dprod:outputPort ex:FilePort, ex:APIPort ;
    dprod:inputPort ex:CRMIngestion ;
    ex:hasOffer ex:CustomerDataOffer .

# === Output Ports ===

ex:FilePort a dprod:OutputPort, dcat:Distribution ;
    rdfs:label "Daily CSV Export" ;
    dcat:mediaType "text/csv" ;
    dcat:downloadURL <s3://data-lake/customer/daily/> .

ex:APIPort a dprod:OutputPort, dcat:DataService ;
    rdfs:label "Customer REST API" ;
    dcat:endpointURL <https://api.example.com/customer/v2> .

# === The RL2 Offer (covers entire data product) ===

ex:CustomerDataOffer a rl2:Offer ;
    rdfs:label "Customer Data Product Offer v2.0" ;
    rl2:grantor ex:DataGovernanceTeam ;
    rl2:target ex:CustomerDataProduct ;
    rl2:clause
        ex:FileDeliveryPromise,
        ex:APIAvailabilityPromise,
        ex:SchemaPromise,
        ex:ChangeNoticePromise ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            rl2:start "2025-01-01T00:00:00Z"^^xsd:dateTime ;
            rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime
        ]
    ] .

# === Port-Specific Promises ===

# Promise 1: File port - daily batch delivery
ex:FileDeliveryPromise a rl2:Promise ;
    rdfs:label "Daily File Delivery by 6am" ;
    rl2:promiser ex:BatchOpsTeam ;
    rl2:promisee rl2:AnyAgent ;
    rl2:target ex:FilePort ;              # Specific to file port
    rl2:promiseContent rl2dc:deliver ;
    rl2:condition [
        a rl2:Condition ;
        rl2:leftOperand rl2dc:schedule ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "FREQ=DAILY;BYHOUR=6;BYMINUTE=0"
    ] .

# Promise 2: API port - 99.9% availability
ex:APIAvailabilityPromise a rl2:Promise ;
    rdfs:label "API 99.9% Availability SLO" ;
    rl2:promiser ex:APIPlatformTeam ;
    rl2:promisee rl2:AnyAgent ;
    rl2:target ex:APIPort ;               # Specific to API port
    rl2:promiseContent rl2dc:maintainAvailability ;
    rl2:condition [
        a rl2:Condition ;
        rl2:leftOperand rl2dc:availability ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperand "99.9"^^xsd:decimal
    ] .

# Promise 3: Schema conformance (applies to all ports)
ex:SchemaPromise a rl2:Promise ;
    rdfs:label "Schema Conformance" ;
    rl2:promiser ex:DataGovernanceTeam ;
    rl2:promisee rl2:AnyAgent ;
    # No rl2:target → applies to entire data product
    rl2:promiseContent rl2dc:conformToSchema ;
    rl2:condition [
        a rl2:Condition ;
        rl2:leftOperand rl2dc:schemaRef ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand ex:CustomerSchemaV2
    ] .

# Promise 4: Change notification (applies to all ports)
ex:ChangeNoticePromise a rl2:Promise ;
    rdfs:label "90-Day Change Notice" ;
    rl2:promiser ex:DataGovernanceTeam ;
    rl2:promisee rl2:AnyAgent ;
    rl2:promiseContent rl2dc:notifyChanges ;
    rl2:condition [
        a rl2:Condition ;
        rl2:leftOperand rl2dc:noticePeriod ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperand "P90D"^^xsd:duration
    ] .

# === Violation Remedy (Duty activated on SLO breach) ===

ex:SLOViolationRemedy a rl2:Duty ;
    rdfs:label "Service Credit on SLO Violation" ;
    rl2:subject ex:APIPlatformTeam ;
    rl2:action rl2dc:issueServiceCredit ;
    rl2:object rl2:AnyAgent ;
    rl2:condition [
        a rl2:Condition ;
        rl2:leftOperand rl2dc:availability ;
        rl2:constraintOperator rl2:lt ;
        rl2:rightOperand "99.9"^^xsd:decimal
    ] .

# === Organizations ===

ex:DataGovernanceTeam a rl2:Agent ;
    rdfs:label "Data Governance Team" .

ex:BatchOpsTeam a rl2:Agent ;
    rdfs:label "Batch Operations Team" .

ex:APIPlatformTeam a rl2:Agent ;
    rdfs:label "API Platform Team" .
```

### Semantics Verification

This integration requires no changes to RL2's formal semantics:

| RL2 Semantic Component | SLO/DQV Application |
|------------------------|---------------------|
| `resolve(leftOperand, Env)` | Quality metrics resolved from monitoring/DQV |
| Promise fulfillment | SLO success when condition holds |
| Promise violation | SLO breach when condition false + deadline passed |
| Power/Duty activation | Remedies triggered by violation events |
| Temporal intervals | SLO measurement windows |

**Rolling Windows**: For sliding time windows (e.g., "99.9% over rolling 30 days"), define:

```
RollingWindow(d) ::= TemporalInterval(now - d, now)
```

The resolver interprets `rl2:duration "P30D"` as `(current_time - 30d, current_time)`.

### Proposed Data Contracts Profile

A minimal `rl2-datacontracts` profile would define:

**Actions:**

- `rl2dc:deliver` - Deliver data according to schedule
- `rl2dc:conformToSchema` - Conform to specified schema
- `rl2dc:notifyChanges` - Notify of upcoming changes
- `rl2dc:maintainAvailability` - Maintain service availability
- `rl2dc:issueServiceCredit` - Issue credit for SLO violation

**Left Operands:**

- `rl2dc:schedule` - Delivery schedule (iCal format)
- `rl2dc:schemaRef` - Reference to schema specification
- `rl2dc:noticePeriod` - Advance notice duration
- `rl2dc:availability` - Service availability percentage
- `rl2dc:latencyP95` - 95th percentile latency
- `rl2dc:completeness` - Data completeness metric
- `rl2dc:freshness` - Data freshness/staleness

**Benefits over separate data contract ontologies:**

- Unified language for rights, contracts, and SLOs
- Built-in Promise Theory with operational semantics
- Formal verification path via RL2 mechanization
- No ODRL dependency (standalone)
- Richer lifecycle tracking (promise states, violation handling)

### Strategic Value

This use-case elevates RL2 from "rights language" to **a general normative policy language for data ecosystems**, covering:

- Rights & access policies (who can do what)
- Data contracts (what data is provided, when)
- SLOs/SLAs (what quality levels are promised)
- Remedies (what happens on violation)

Enterprises need unified modeling for all of the above. RL2 provides it without requiring multiple overlapping ontologies.

---

## Notes

These topics represent potential future enhancements. They do not affect the validity of the current RL2 specification. Feedback and proposals are welcome.
