# RL2 Discussion Topics

*Future design decisions and enhancements under consideration*

Active discussion topics are tracked as GitHub Issues. This document provides detailed background and serves as design rationale.

---

## Active Topics

| # | Topic | Labels | Issue |
|---|-------|--------|-------|
| 1 | Alignment Modules for Standard Vocabularies | ontology | [#2](https://github.com/matthiasautrata/RL2/issues/2) |
| 2 | Common Profile for Baseline Actions/Operands | profile | [#3](https://github.com/matthiasautrata/RL2/issues/3) |
| 3 | Explicit Rejection/Disapproval Semantics | semantics, protocol | [#4](https://github.com/matthiasautrata/RL2/issues/4) |
| 4 | Policy Inheritance (skeptical) | semantics | [#5](https://github.com/matthiasautrata/RL2/issues/5) |
| 9 | Context Subject Typing in Protocol | protocol | [#6](https://github.com/matthiasautrata/RL2/issues/6) |
| 11 | Recurrent Duties (Periodic Obligations) | semantics, ontology | [#8](https://github.com/matthiasautrata/RL2/issues/8) |
| 12 | Duty Consumption Modes | semantics | [#9](https://github.com/matthiasautrata/RL2/issues/9) |
| 13 | Profile Guidance (RL2-Minimal vs RL2-Full) | profile, documentation | [#10](https://github.com/matthiasautrata/RL2/issues/10) |

---

## Technical Notes

These sections provide detailed analysis and design rationale. They are not tracked as issues because they are reference material rather than actionable decisions.

### Data Contracts and SLOs (§7)

**Key Insight**: RL2 already includes Promise Theory as a core layer, making it a natural fit for data contracts without requiring a separate ontology.

**Core Formula**:

> **SLO = Promise + Measurable Condition + Time Window + Remedy**

This maps directly to RL2's existing constructs—no extensions required.

#### DCON → RL2 Mapping

| DCON Concept | RL2 Equivalent |
|--------------|----------------|
| `dcon:DataContract` | `rl2:Offer` |
| `dcon:DataContractSubscription` | `rl2:Agreement` |
| `dcon:Promise` | `rl2:Promise` |
| `dcon:hasEffectivePeriod` | `rl2:TemporalConstraint` + `rl2:EffectiveInterval` |

#### DQV Alignment

DQV is **descriptive** (what was measured), RL2 is **normative** (what should be measured and what happens when it isn't):

| Concept | DQV | RL2 |
|---------|-----|-----|
| What is measured? | `dqv:Metric` | `rl2:LeftOperand` |
| What *should* the value be? | ❌ | `rl2:Condition` with threshold |
| What happens on violation? | ❌ | `rl2:Duty` / `rl2:Claim` / `rl2:Power` |

**Strategic Value**: This use-case elevates RL2 from "rights language" to **a general normative policy language for data ecosystems**.

---

### Graphical Representation (§8)

**The Problem**: Any class diagram of RL2 faces a tradeoff between completeness and readability. Agent connects to many classes; showing all arrows creates spaghetti.

**Current Approach**: Two diagrams at different abstraction levels:

| Diagram | Purpose |
|---------|---------|
| `rl2-overview.drawio.svg` | Conceptual introduction |
| `rl2-information-model.drawio.svg` | Technical reference |

**Current Position**: Accept that static diagrams will be incomplete. Prioritize clarity over completeness.

---

### OPAL Formal Semantics Comparison (§15)

**Background**: The OPAL 2025 paper (Bonatti, Fornara, Harth) proposes model-theoretic semantics for ODRL 2.2. RL2 takes a different approach—rebuilding from first principles.

#### Fundamental Difference: Formal Method Choice

| Aspect | OPAL | RL2 |
|--------|------|-----|
| **Formal Method** | Model Theory (sets, truth tables) | Programming Language Theory (types, state machines) |
| **Semantics Style** | Denotational (what a policy "means") | Operational (how the machine transitions) |
| **Primary Question** | "Looking at logs, did Alice violate policy?" | "Alice is clicking now—should state change?" |
| **Focus** | Audit/compliance checking | Real-time enforcement |

#### Summary Comparison

| Feature | OPAL 2025 | RL2 |
|---------|-----------|-----|
| **Primary Goal** | Formalize ODRL 2.2 (fix ambiguity) | Define a new, rigorous language |
| **Math Style** | Set Theory / Model Theory | Type Theory / Operational Semantics |
| **Data Types** | Hard-coded (Money=ℚ) | Abstracted (Profiles define types) |
| **Norms** | Permissions, Prohibitions, Duties | Full Hohfeldian (Powers, Claims, Immunities) |
| **Promise Theory** | None (purely deontic) | Native support with PromiseState lifecycle |
| **Implementation** | Theoretical reference | Protocol spec & SHACL shapes included |
| **Verdict** | Rigorous but rigid | Rigorous and executable |

#### RL2's Structural Advantages

- **Abstract Algebraic Approach**: Data types delegated to Profiles, separating Kernel from Data
- **Normative Expressivity**: Full Hohfeldian model including Power/Liability/Immunity
- **Promise Theory**: Distinguishes imposed norms from voluntary commitments

#### Potential Adoptions from OPAL

1. **Denotation function notation (δ)** for mapping RDF syntax to formal structures
2. **Correctness framework** for monitoring, access control, and policy comparison
3. **Trace semantics** to connect with temporal logic literature
4. **Explicit policy scope semantics**

#### Strategic Positioning

RL2 is **not** less rigorous than OPAL. RL2's small-step operational semantics are arguably **more** rigorous for implementation purposes because they leave zero ambiguity about state changes.

---

### Documentation Roadmap (§14)

**Priority order** for additional documentation:

1. Best Current Practice (BCP) with examples (highest value for adoption)
2. Conformance test suite (implementation validation)
3. Profile development guide (enables ecosystem)
4. Standards alignment guide (interoperability)
5. Versioning policy (governance)

---

## Resolved Topics

These topics have been resolved. The detailed rationale is preserved below for reference.

### ✅ Dynamic Policy Applicability (§5)

**Resolution**: Fully integrated into RL2 specification.

- **RL2_Core.md**: `rl2:condition` domain extended to include Policy; `rl2:policyGeneration` property added
- **RL2_Semantics.md**: §Policy-Level Activation, §Policy Generations, §Expressive Characterization
- **RL2_Protocol.md**: §Re-evaluation Triggers

**Key insight**: Events don't branch duties — they change which policies apply.

---

### ✅ Expressive Completeness (§6)

**Resolution**: See RL2_Semantics.md §Expressive Characterization.

**Open questions for future work**:
- Should RL2 extend to CTL-level expressiveness, or is LTL sufficient?
- Repeating/periodic obligations ("every month")
- Quorum approvals ("any 2 of 5 committee members")

---

### ✅ Multi-Party Agreements (§10)

**Resolution**: Enforcement via EventConstraint; metadata deferred to profiles.

The common "co-signer must approve" pattern is **already expressible**:

```turtle
ex:accessPrivilege a rl2:Privilege ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:EventConstraint ;
            rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:DataProvider ]
        ] ;
        rl2:operand [
            a rl2:EventConstraint ;
            rl2:expectsEvent [ a rl2:Event ; rl2:approver ex:LegalDept ]
        ]
    ] .
```

This handles:
- **Blocking co-signers**: All required approvals must be present
- **N-of-M approval**: Use `rl2:or` with multiple EventConstraints
- **Sequential approval**: Use `rl2:after` to require ordering

Agreement-level party metadata (explicit enumeration, signature tracking) can be addressed by domain profiles if needed.

---

## Archived Detail

The following sections contain full detail from the original discussion topics. They are preserved for completeness but the canonical discussion is now in GitHub Issues.

<details>
<summary>§1. Alignment Modules — Full Detail</summary>

**Proposal**: Create a separate `RL2_Alignment.md` containing `owl:equivalentClass` and `rdfs:subClassOf` axioms:

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

</details>

<details>
<summary>§2. Common Profile — Full Detail</summary>

**Proposal**: Create an `RL2_CommonProfile.md` defining baseline vocabulary:

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

</details>

<details>
<summary>§3. Rejection Semantics — Full Detail</summary>

**The Problem**: Active disapproval is semantically distinct from the absence of approval:
- Absence: Request pending, awaiting response, may timeout
- Rejection: Explicit "no", request should be denied, logged for audit

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
       rl2:outcome rl2:Rejected .
   ```

3. **Rejection as Prohibition Activation**

**Considerations**:
- Should rejection be a subclass of Event or a distinct concept?
- How does rejection interact with the Case lifecycle?
- Appeal/override workflows after rejection

</details>

<details>
<summary>§4. Policy Inheritance — Full Detail</summary>

**Current Position**: Skeptical. RL2 does not support policy inheritance.

**The Problem with Inheritance**:

1. **Flattening required**: To evaluate an inherited policy, you must resolve all inheritance chains into atomic rules.

2. **Override semantics are ambiguous**: What happens when a child policy conflicts with an inherited rule?

3. **Complexity vs. value**: Simply create multiple policies and let the evaluator handle composition.

4. **Auditability**: Inherited policies are harder to audit.

**Recommendation**: Avoid inheritance. Use explicit policy composition instead.

</details>

<details>
<summary>§9. Context Subject Typing — Full Detail</summary>

**The Problem**: `rl2p:contextSubject` is currently untyped—it can reference either a literal value or a resource IRI.

**Possible Approaches**:

1. **Split properties**: `rl2p:contextSubjectIRI` and `rl2p:contextSubjectLiteral`

2. **Resource-only**: Require `contextSubject` to be a resource

3. **Union with SHACL**: Keep single property, use `sh:or` to validate either form

</details>

<details>
<summary>§11. Recurrent Duties — Full Detail</summary>

**The Gap**: No native way to express periodic recurrence, maximum occurrences, or per-period violation semantics.

**Possible Approaches**:

1. **RecurrentDuty subclass** with `rl2:period` and `rl2:maxOccurrences`

2. **iCal-style recurrence rules**: `rl2:recurrence "FREQ=QUARTERLY;BYMONTH=3,6,9,12"`

3. **Profile-level**: Delegate to domain profiles

**Semantic Complexity**:
- Each recurrence instance needs its own obligation state
- The formal semantics would need "duty instances" vs "duty templates"

**Current Position**: Significant complexity. The compositional approach (create new duties via Power exercise) may suffice.

</details>

<details>
<summary>§12. Duty Consumption Modes — Full Detail</summary>

**The Problem**: Does one fulfilled duty enable one action, unlimited actions, or actions until expiration?

**Possible Approaches**:

1. **Duty consumption mode property**: `rl2:ConsumptionMode owl:oneOf (rl2:Once rl2:PerAction rl2:Unlimited)`

2. **Explicit via conditions**: Combine with temporal constraints and counters

3. **Protocol-level**: Track fulfillment-to-action mappings in Cases

**Current Position**: May be addressable via existing mechanisms rather than new core vocabulary.

</details>

<details>
<summary>§13. Profile Guidance — Full Detail</summary>

**Proposed Profiles**:

1. **RL2-Minimal**: Privilege, Prohibition, Duty, Policy, Condition (atomic + temporal)
   - Sufficient for: ODRL-equivalent policies, basic access control

2. **RL2-Standard**: Minimal + Promise, EventConstraint
   - Sufficient for: Approval workflows, data contracts

3. **RL2-Full**: Standard + Power, Liability, Immunity, Claim
   - Sufficient for: Full normative reasoning, legal compliance

**Current Position**: This is documentation work, not specification change.

</details>

---

## Notes

These topics represent potential future enhancements. They do not affect the validity of the current RL2 specification. Feedback and proposals are welcome via GitHub Issues.
