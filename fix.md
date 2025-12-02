# RL2 Review & Remediation Plan

**Date:** 2025-12-01
**Review Team:** Ontologist, Mathematician/Semanticist, Senior Copy-Editor, with input from Legal, Operations/SRE, and Risk/Security/IAM
**Status:** Critical issues resolved; remaining items documented for future work

---

## Executive Summary

This review evaluates RL2 as a foundation for enterprise data-use policies, data contracts, and entitlements management. The specification is **ambitious and well-structured**. Critical issues have been addressed; remaining items are documented below.

**Severity Key:**
- **Critical (C)**: Blocks correct implementation; must fix before deployment
- **High (H)**: Causes significant ambiguity or inconsistency; should fix before release
- **Medium (M)**: Best practice violations or editorial issues; fix when convenient

---

## Part I: Critical Issues — RESOLVED

### ✅ C1. Protocol Decision Enumeration Mismatch

**Status:** FIXED

**Issue:** The `Eval` function returns `PermitWithObligations` but the protocol ontology only defined 4 decision values.

**Resolution:** Added `rl2p:PermitWithObligations` to:
- `rl2p.ttl` (owl:oneOf enumeration and individual definition)
- `rl2p-shacl.ttl` (sh:in constraint)
- `RL2_Protocol.md` (documentation and decision semantics table)

---

### ✅ C2. policyGeneration Property Type Violation (OWL DL)

**Status:** FIXED

**Issue:** `rl2p:policyGeneration` was declared as `owl:ObjectProperty` with `rdfs:range xsd:anyURI`, which is invalid in OWL 2 DL.

**Resolution:** Changed to `owl:DatatypeProperty` in:
- `rl2p.ttl`
- `RL2_Protocol.md`

---

### ✅ C3. Condition SHACL Targeting Error

**Status:** FIXED

**Issue:** `AtomicConditionShape` targeted the base `rl2:Condition` class, which would incorrectly apply to subclasses (LogicalConstraint, TemporalConstraint, etc.) when RDFS inference is enabled.

**Resolution:**
- Added `rl2:AtomicConstraint` class to `rl2.ttl` as explicit subclass of Condition
- Updated SHACL shape to target `rl2:AtomicConstraint` specifically
- Updated `RL2_Core.md` condition subclass list
- Updated `RL2_ODRL_Coverage.md` mapping table and examples

---

### ✅ C4. Undefined `deadline` Function in Semantics

**Status:** FIXED

**Issue:** The Promise Violation rule used `deadline(content, Σ)` but the function was never defined.

**Resolution:** Added `deadline : PromiseContent × State → Boolean` definition to `RL2_Semantics.md` after the `timeout` function, with case analysis for Action, Duty, and Condition content types.

---

### ~~C5. PromiseContent OWL 2 DL Incompatibility~~

**Status:** FALSE POSITIVE — REMOVED

**Original Claim:** Union classes cannot be used as ranges of object properties in OWL 2 DL.

**Finding:** This is incorrect. OWL 2 DL allows:
- Union classes defined with `owl:unionOf`
- Union classes used as `rdfs:range` of object properties
- Anonymous union classes as `rdfs:domain`

The `PromiseContent` pattern is valid OWL 2 DL. No changes required.

---

## Part II: High-Priority Issues

### ✅ H1. Action Property Inconsistency (Prohibition)

**Status:** FIXED

**Location:** `rl2.ttl`

**Issue:** Privileges and Duties use `rl2:action`, but Prohibitions use `rl2:prohibitedAction`. This requires special-case handling in queries.

**Resolution:** Added `rdfs:subPropertyOf rl2:action` to `rl2:prohibitedAction`. This ensures all norms can be queried uniformly via `rl2:action` while preserving the specific `prohibitedAction` property for explicit prohibition queries.

---

### ✅ H2. DutySet to DutyRequirement Mapping Undefined

**Status:** FIXED

**Location:** `RL2_Protocol.md`, `rl2p.ttl`

**Issue:** The `Eval` function returns `DutySet` containing `Duty` objects, but the Protocol expects `rl2p:DutyRequirement` instances. No specification for the transformation exists.

**Resolution:**
- Added "Duty Set Enrichment" section to `RL2_Protocol.md` with formal `enrich` function
- Removed redundant `dutyLabel` and `dutyDescription` properties from `DutyRequirement` (human-readable metadata is available via the linked `rl2:Duty`)
- Updated example to show streamlined `DutyRequirement` structure

---

### ✅ H3. Requestor vs RequestingAgent Security Clarification

**Status:** FIXED

**Location:** `RL2_Protocol.md`

**Issue:** Security implications of delegation (requestor ≠ requestingAgent) are not rigorously specified.

**Resolution:** Added note in Request section documenting that delegation authority validation is explicitly out of scope for RL2. Implementations must handle authentication and delegation verification at the transport/identity layer.

---

### ✅ H4. LogicalConstraint Operand Cardinality

**Status:** FIXED

**Location:** `rl2.ttl`, `rl2-shacl.ttl`

**Issue:** The `not` operator requires exactly one operand, but SHACL only validates minCount 1.

**Resolution:** Documented operator-specific cardinality requirements:
- Added "Requires exactly one operand" to `rl2:not` comment in ontology
- Added explanatory comment to `LogicalConstraintShape` noting that SHACL validates minimum cardinality; implementations must enforce operator-specific rules

---

### ✅ H5. Missing `xone` Semantics Precision

**Status:** FIXED

**Location:** `RL2_Semantics.md`

**Issue:** The `xone` definition doesn't explicitly state behavior when zero conditions are true.

**Resolution:** Added explicit clarification to `Xone` semantics: "true iff exactly one ... is true (false when zero or more than one)".

---

## Part III: Medium-Priority Issues

### ✅ M1. Terminology: `promiser` vs `promisor`

**Status:** FIXED

**Issue:** Legal convention uses "promisor" not "promiser".

**Resolution:** Renamed `rl2:promiser` to `rl2:promisor` across all files:
- `rl2.ttl`, `rl2-shacl.ttl` (ontology and shapes)
- `RL2_Core.md`, `RL2_Semantics.md` (documentation)
- `RL2_ODRL_Coverage.md`, `RL2_DiscussionTopics.md` (examples and mappings)
- `rl2-overview.drawio` (diagram label)

---

### ✅ M2. AssetCollection Security Warning

**Status:** FIXED

**Issue:** `rl2:dynamicQuery` and `rl2:dynamicOperand` accept arbitrary strings with injection risk.

**Resolution:** Added SECURITY notes to `rdfs:comment` for both properties in `rl2.ttl`, warning implementations to sanitize/parameterize inputs and use allowlisted templates where possible.

### ✅ M3. Redundant Marketing Text

**Status:** FIXED

**Issue:** "Strict superset of ODRL" claim appears in 5 documents, creating maintenance burden.

**Resolution:** Added cross-references to the authoritative `RL2_ODRL_Coverage.md` document:
- `README.md`: Added link to ODRL Coverage document
- `RL2_ResearchPlan.md`: Added reference to ODRL Coverage document
- `RL2_White_Paper.md`: Already had cross-reference (no change)
- `RL2_Core.md`: Kept as-is (broader claim about multiple predecessors, not just ODRL)
- `RL2_ODRL_Coverage.md`: Authoritative source (no change)

### ✅ M4. correlativeTo Property Underspecified

**Status:** FIXED

**Issue:** Valid Hohfeldian pairings for `correlativeTo` not documented.

**Resolution:** Expanded `rdfs:comment` in `rl2.ttl` to list valid pairings (Duty ↔ Claim, Power ↔ Liability, Immunity ↔ Disability) with explanations. Also added brief reference in `RL2_Core.md`. SHACL enforcement deferred as optional future enhancement.

### ✅ M5. EventConstraint Semantics Incomplete

**Status:** FIXED

**Issue:** `matches` function unclear on approver matching and EventPattern type.

**Resolution:** Clarified in `RL2_Semantics.md` that `EventPattern` is an `Event` instance used as a template, and that matching includes properties like `rl2:approver`. Temporal bounds are handled separately via `rl2:TemporalConstraint` on norms (separation of concerns).

### ~~M6. Open Interval Validation Edge Cases~~

**Status:** NOT AN ISSUE — REMOVED

**Original Claim:** `sh:lessThanOrEquals` needs SPARQL replacement for conditional start ≤ end validation.

**Finding:** Per SHACL spec, `sh:lessThanOrEquals` is vacuously satisfied when either property has no value. The current shape already handles open intervals correctly:
- Start only (open-ended): constraint satisfied
- End only (deadline): constraint satisfied
- Both present: validates start ≤ end

The existing comment in `rl2-shacl.ttl` (lines 204-208) documents this correctly.

---

## Part IV: Removed Items

### ~~S3. NormOrEvent Union Class Usage~~

**Status:** NOT AN ISSUE — REMOVED

The `NormOrEvent` union class is a valid OWL pattern for sharing properties between `Norm` and `Event`. No changes needed.

---

## Part V: Security & Risk Considerations

### R1. Dynamic Query Injection

Both `rl2:dynamicQuery` and `rl2:dynamicOperand` accept arbitrary strings. Recommend:
1. Security annotations in ontology
2. Parameterized query patterns in BCP document
3. Allowlisted query templates

### R2. Entitlement Escalation via Power/Liability

Power construct allows norm creation/modification. Recommend:
1. Audit logging for Power exercise
2. Consider `rl2:powerScope` property
3. Document least privilege patterns

### R3. Temporal Constraint Bypass

If `Σ.Clock` is client-controlled, temporal constraints can be bypassed. Recommend:
1. Document trusted time source requirement
2. Use `rl2p:evaluationTime` as authoritative timestamp

---

## Part VI: Testing & Conformance

### T1. Test Suite Required

Create conformance test suite with:
1. Valid policies that MUST pass SHACL validation
2. Invalid policies that MUST fail SHACL validation
3. Evaluation scenarios with expected outcomes
4. Edge cases (empty duty sets, temporal boundaries, etc.)

### T2. Interoperability Profile

Define "RL2 Baseline" profile specifying required classes, properties, and common vocabulary.

---

## Summary of Changes Made

| File | Changes |
|------|---------|
| `rl2.ttl` | Added `rl2:AtomicConstraint` class; added `rdfs:subPropertyOf rl2:action` to `prohibitedAction`; renamed `promiser` → `promisor` |
| `rl2-shacl.ttl` | Changed `AtomicConstraintShape` to target `rl2:AtomicConstraint`; added explanatory comment; renamed `promiser` → `promisor` |
| `rl2p.ttl` | Added `rl2p:PermitWithObligations`; fixed `policyGeneration` to DatatypeProperty; removed `dutyLabel`/`dutyDescription` |
| `rl2p-shacl.ttl` | Added `PermitWithObligations` to decision enum |
| `RL2_Protocol.md` | Updated Decision ontology and semantics table; fixed policyGeneration type; added Duty Set Enrichment section; removed dutyLabel/dutyDescription from DutyRequirement |
| `RL2_Core.md` | Added `AtomicConstraint` to condition subclasses list; renamed `promiser` → `promisor` |
| `RL2_ODRL_Coverage.md` | Updated mapping table; changed example to use `AtomicConstraint`; renamed `promiser` → `promisor` |
| `RL2_Semantics.md` | Added `deadline` function definition; clarified `Xone` semantics; renamed `promiser` → `promisor` |
| `RL2_DiscussionTopics.md` | Renamed `promiser` → `promisor` |
| `rl2-overview.drawio` | Renamed `promiser` → `promisor` in diagram label |

---

*End of Review*
