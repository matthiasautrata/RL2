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

**Rolling Windows**: For sliding time windows (e.g., "99.9% over rolling 30 days"), the data contracts profile would define a convention for how `rl2dc:measurementWindow` operands are resolved. This is profile-level semantics, not core RL2—the resolver implementation interprets duration values according to profile specifications. E.g., The resolver interprets `rl2:duration "P30D"` as `(current_time - 30d, current_time)`.

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

## 8. Graphical Representation of the Information Model

**Status**: Under discussion

**Background**: RL2 includes two diagram files (`rl2-overview.drawio.svg` and `rl2-information-model.drawio.svg`) that visualize the ontology structure. However, creating effective diagrams for a policy language is inherently challenging.

**The Problem**: Any class diagram of RL2 faces a tradeoff:

- **Completeness vs. readability**: Agent connects to Norm (subject, counterparty), Promise (promiser, promisee), Policy (grantor, grantee), Event (approver, operationalAgent), and more. Showing all arrows creates spaghetti; omitting them is incomplete.

- **Single view limitations**: A static document cannot provide drill-down or filtering. Even the ODRL Information Model diagram—which is well-designed—is necessarily incomplete.

- **Multiple audiences**: A conceptual overview for the White Paper needs different emphasis than a technical reference diagram.

**Current Approach**: Two diagrams at different abstraction levels:

| Diagram | Purpose | Focus |
|---------|---------|-------|
| `rl2-overview.drawio.svg` | Conceptual introduction | Layers, key relationships (Policy→Norm, Promise↔Agent, Promise→Norm) |
| `rl2-information-model.drawio.svg` | Technical reference | All classes, inheritance, selected property arrows |

**Future Options**:

1. **Multiple focused diagrams**: Separate views for Agent relationships, Condition hierarchy, Protocol flow, etc.

2. **Interactive tooling**: A web-based visualization with filtering/drill-down (premature for current stage)

3. **Notation conventions**: Establish rules for what arrows to show vs. imply (e.g., "Agent is referenced by most classes" as a note rather than arrows everywhere)

4. **Generated diagrams**: Auto-generate from the TTL using tools like WebVOWL, with manual refinement

**Current Position**: Accept that static diagrams will be incomplete. Prioritize clarity over completeness. Revisit when the specification stabilizes and an interactive documentation site becomes worthwhile.

---

## 9. Context Subject Typing in Protocol

**Status**: Under discussion

**Background**: The RL2 Protocol's `rl2p:contextSubject` property is currently untyped—it can reference either a literal value or a resource IRI. This ambiguity may cause interoperability issues between implementations.

**The Problem**: Context assertions are used to provide facts for policy evaluation:

```turtle
ex:ctx1 a rl2p:ContextAssertion ;
    rl2p:contextSubject ex:Alice ;           # Resource reference
    rl2p:contextProperty ex:department ;
    rl2p:contextValueRef ex:AutoFinance .

ex:ctx2 a rl2p:ContextAssertion ;
    rl2p:contextSubject "user123" ;          # Literal value - is this valid?
    rl2p:contextProperty ex:userId ;
    rl2p:contextValue "active" .
```

Should `contextSubject` accept literals, or only resource IRIs?

**Possible Approaches**:

1. **Split properties**: `rl2p:contextSubjectIRI` (ObjectProperty) and `rl2p:contextSubjectLiteral` (DatatypeProperty)

2. **Resource-only**: Require `contextSubject` to be a resource; literal identifiers must be wrapped in a resource

3. **Union with SHACL**: Keep single property, use `sh:or` in SHACL to validate either form

**Considerations**:
- Splitting properties adds verbosity but is unambiguous
- Resource-only is cleaner but may not fit all integration patterns
- Union approach is flexible but may complicate query patterns

---

## 10. Multi-Party Agreements

**Status**: Partially addressed — enforcement works, metadata is limited

**Background**: The current `AgreementShape` requires exactly one `grantor` and one `grantee`. However, real-world agreements often involve multiple parties (e.g., data sharing consortiums, co-signers, multi-stakeholder governance).

### Already Supported: Multi-Party Approval Enforcement

The common "co-signer must approve" pattern is **already expressible** using `EventConstraint`:

```turtle
ex:dataShareAgreement a rl2:Agreement ;
    rl2:grantor ex:DataProvider ;
    rl2:grantee ex:DataConsumer ;
    rl2:clause ex:accessPrivilege .

ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:DataConsumer ;
    rl2:action ex:use ;
    rl2:object ex:Dataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:EventConstraint ;
            rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:DataProvider ]
        ] ;
        rl2:operand [
            a rl2:EventConstraint ;
            rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:LegalDept ]  # Co-signer
        ]
    ] .
```

The privilege only activates when **both** approval events exist in Σ. This handles:

- **Blocking co-signers**: All required approvals must be present
- **N-of-M approval**: Use `rl2:or` with multiple EventConstraints
- **Sequential approval**: Use `rl2:after` to require ordering

### What's Not Supported: Agreement-Level Party Metadata

The gap is **structural/metadata**, not **enforcement**:

1. **Explicit party enumeration**: No way to declare "this agreement has parties A, B, C" as metadata independent of the norms
2. **Role symmetry**: `grantor`/`grantee` implies asymmetry; peer-to-peer agreements don't fit cleanly
3. **Signature tracking**: No standard way to record "who has signed" vs "who must sign" at the agreement level

### Current Position

For **enforcement** of multi-party approval, use the existing `EventConstraint` mechanism — it's compositional and already has formal semantics.

For **agreement metadata** (party enumeration, signature status), this could be addressed by:

- A simple `rl2:party` property (but this adds no semantic value without accompanying enforcement semantics)
- Protocol-level tracking of agreement signatures (similar to Case lifecycle)
- Domain profiles that define agreement metadata for specific use cases

No changes to RL2 Core are currently proposed. The enforcement mechanism is sufficient; metadata extensions can be added by profiles if needed.

---

## 11. Recurrent Duties (Periodic Obligations)

**Status**: Under discussion

**Background**: RL2 currently models duties with single-deadline semantics. However, many real-world obligations are recurring: "submit a report every quarter", "renew certification annually", "perform backup daily".

**The Gap**: There is no native way to express:
- Periodic recurrence (daily, weekly, monthly)
- Maximum occurrences
- Per-period violation semantics (does missing one period violate the whole duty, or just that instance?)

**Possible Approaches**:

1. **RecurrentDuty subclass**:
   ```turtle
   rl2:RecurrentDuty rdfs:subClassOf rl2:Duty .

   rl2:period a owl:DatatypeProperty ;
       rdfs:domain rl2:RecurrentDuty ;
       rdfs:range xsd:duration .

   rl2:maxOccurrences a owl:DatatypeProperty ;
       rdfs:domain rl2:RecurrentDuty ;
       rdfs:range xsd:integer .
   ```

2. **iCal-style recurrence rules**:
   ```turtle
   ex:quarterlyReport a rl2:Duty ;
       rl2:recurrence "FREQ=QUARTERLY;BYMONTH=3,6,9,12" .
   ```

3. **Profile-level**: Delegate to domain profiles that need recurrence

**Semantic Complexity**:
- Each recurrence instance needs its own obligation state (Pending → Active → Fulfilled/Violated)
- The formal semantics would need to model "duty instances" vs "duty templates"
- Violation of one instance may or may not affect other instances

**Current Position**: This is significant complexity. The compositional approach (create new duties via Power exercise or policy activation) may suffice for many cases. A dedicated recurrence mechanism would be valuable but requires careful design.

---

## 12. Duty Consumption Modes

**Status**: Under discussion

**Background**: When a duty is attached to a privilege, how many times must it be fulfilled? Consider:

- **Pay-per-view**: Each viewing action requires separate payment
- **Subscription**: One payment enables unlimited viewing for a period
- **One-time setup**: Complete training once, then access indefinitely

RL2 currently doesn't distinguish between "one duty fulfillment enables many actions" vs "one duty per action".

**The Problem**: Given:
```turtle
ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:viewDataset ;
    rl2:condition [ rl2:requires ex:paymentDuty ] .

ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:pay ;
    rl2:obligationState rl2:Fulfilled .
```

Does one fulfilled payment enable:
- One view? (pay-per-action)
- Unlimited views? (pay-once)
- Views until some expiration? (subscription)

**Possible Approaches**:

1. **Duty consumption mode property**:
   ```turtle
   rl2:dutyConsumptionMode a owl:ObjectProperty ;
       rdfs:domain rl2:Duty ;
       rdfs:range rl2:ConsumptionMode .

   rl2:ConsumptionMode owl:oneOf (rl2:Once rl2:PerAction rl2:Unlimited) .
   ```

2. **Explicit via conditions**: Combine with temporal constraints and counters
   ```turtle
   ex:paymentDuty a rl2:Duty ;
       rl2:condition [ rl2:leftOperand ex:usageCount ; rl2:constraintOperator rl2:eq ; rl2:rightOperand 0 ] .
   ```

3. **Protocol-level**: Track fulfillment-to-action mappings in Cases rather than in policy

**Considerations**:
- This affects the formal semantics of duty fulfillment
- Counters/usage tracking may belong in state (Σ) rather than policy
- Some consumption models are temporal (subscription = fulfilled + within interval)

**Current Position**: The distinction is real and affects policy interpretation. However, it may be addressable via existing mechanisms (temporal conditions, protocol-level tracking) rather than new core vocabulary. Further analysis needed.

---

## 13. Profile Guidance (RL2-Minimal vs RL2-Full)

**Status**: Under discussion

**Background**: RL2 includes a rich set of constructs: Hohfeldian norms (7 types), Promises, Conditions (6 subtypes), Protocol artifacts, and more. Not all implementations need all features.

**The Need**: Clear guidance on which RL2 constructs to use for common scenarios:

| Use Case | Required Constructs |
|----------|---------------------|
| Simple access control | Privilege, Prohibition, Policy |
| Obligations with deadlines | + Duty, TemporalConstraint, ObligationState |
| Approval workflows | + EventConstraint, Event |
| Bilateral commitments | + Promise, PromiseState |
| Normative reasoning | + Claim, Power, Liability, Immunity |
| Full enterprise governance | All of the above |

**Proposed Profiles**:

1. **RL2-Minimal**: Privilege, Prohibition, Duty, Policy, Condition (atomic + temporal)
   - Sufficient for: ODRL-equivalent policies, basic access control with obligations

2. **RL2-Standard**: Minimal + Promise, EventConstraint, DynamicOperandReference
   - Sufficient for: Approval workflows, data contracts, bilateral agreements

3. **RL2-Full**: Standard + Power, Liability, Immunity, Claim
   - Sufficient for: Full normative reasoning, legal compliance modeling

**Documentation Approach**:
- Quick-start guide using Minimal profile
- Examples showing when to "level up" to Standard or Full
- Clear labeling in Core spec of which profile each construct belongs to

**Current Position**: This is documentation work, not specification change. Should be prioritized for adoption.

---

## 14. Documentation Roadmap

**Status**: Future work

**Background**: RL2 currently has specification documents (Core, Semantics, Protocol) and a White Paper. For adoption, additional documentation is needed.

### Needed Documents

**Best Current Practice (BCP) Document**

A practical guide with worked examples for common patterns:

- **Multi-party agreements**: Co-signer workflows, N-of-M approval, sequential signing (using EventConstraint)
- **Data Quality (DQV) integration**: Quality metrics as left operands, thresholds as conditions
- **SLO/SLA modeling**: Promises with measurable conditions, violation remedies
- **Data contracts**: Producer/consumer commitments, schema guarantees, delivery schedules
- **Approval workflows**: Committee review, escalation, rejection handling
- **Temporal patterns**: Deadlines, open intervals, relative durations via DynamicOperandReference

**Profile Development Guide**

How to create domain-specific RL2 profiles:

- Defining Actions and LeftOperands for a domain
- SHACL shapes for profile-specific validation
- Namespace conventions and versioning
- Interoperability with RL2 Core

**Standards Alignment Guide**

Mapping RL2 to related standards:

- **PROV-O**: Case/Event provenance, activity tracking
- **OWL-Time**: Temporal interval alignment
- **FOAF/ORG**: Agent modeling
- **DQV**: Quality vocabulary integration
- **DCAT/DPROD**: Data product metadata

**Versioning and Evolution**

- RL2 Core versioning policy
- Profile versioning independent of Core
- Backward compatibility guarantees
- Migration guidance between versions

### Current Position

These are documentation tasks, not specification changes. Priority order:

1. BCP with examples (highest value for adoption)
2. Profile development guide (enables ecosystem)
3. Standards alignment (interoperability)
4. Versioning policy (governance)

---

## Notes

These topics represent potential future enhancements. They do not affect the validity of the current RL2 specification. Feedback and proposals are welcome.
