# RL2 Critical Fixes

**Date:** 2025-01-04
**Target:** RL2 Core Ontology and Semantics

---

## Permission-Bound Duties (CRITICAL - ODRL Compatibility)

### Problem

ODRL duties can have actions different from the permitted action (e.g., permit `display` if duty `pay` is fulfilled). RL2 semantics currently only activate duties whose `action` matches the request, so duties with different actions never apply.

**Technical Analysis:**
* `matches(Norm(a,x,s,c), R)` at RL2_Semantics.md:505-512 requires action equality: `(x = x_req ∨ x_req ⊑ x)`
* Duty denotation at RL2_Semantics.md:540-542 uses `matches(Duty(a,x,s,c), R)` to determine activation
* Evaluation algorithm at RL2_Semantics.md:888 filters: `matchingDuties = { d ∈ P.clauses | ... ∧ matches(d, R) }`
* Result: A duty with `action=pay` attached to privilege with `action=display` is dropped on a `display` request

**ODRL Example That Fails:**
```turtle
:offer1 a odrl:Offer ;
    odrl:permission [
        odrl:action odrl:display ;
        odrl:target :photo123 ;
        odrl:duty [
            odrl:action odrl:pay ;
            odrl:constraint [ odrl:payAmount 5.00 ]
        ]
    ] .
```

Expected: `PermitWithObligations` with payment duty
Actual (RL2): `Permit` (duty not surfaced because `pay ≠ display`)

### Approved Solution: Two-Class Model with Preconditions

**Rationale:**
* ODRL duties nested in permissions are semantically different from standalone duties
* Standalone duties are Norms (activate via action matching)
* Permission-bound duties are preconditions (activate when parent privilege matches)
* Context-dependent semantics (single class, dual behavior) lead to ODRL-style complexity
* Separate classes provide semantic clarity at authoring layer
* Both compile to flat I/O rules at execution layer (zero runtime complexity)

**Architecture:**
```
DDL Authoring Layer (RL2 TTL)
  - rl2:Duty (standalone norm, becomes top-level I/O rule)
  - rl2:Precondition (privilege-bound, compiled into privilege output)
  - Numeric priorities for defeat resolution
      ↓ COMPILE
I/O Execution Layer
  - Flat rules: (Condition) → (Permit + Obligation)
  - No class hierarchy, no context-dependence
  - Pure functional evaluation
```

### Required Changes

#### 1. Ontology (rl2.ttl)

```turtle
rl2:Precondition a owl:Class ;
    rdfs:comment "Obligation that must be fulfilled to exercise a privilege, power, or other norm. Not a standalone duty. Lifecycle is coupled to parent norm (defeated when parent defeated)." .

rl2:obligatedAction a owl:ObjectProperty ;
    rdfs:domain rl2:Precondition ;
    rdfs:range rl2:Action ;
    rdfs:comment "The action that must be performed to fulfill this precondition." .

rl2:requires a owl:ObjectProperty ;
    rdfs:domain rl2:Norm ;  # Can apply to Privilege, Power, etc.
    rdfs:range rl2:Precondition ;
    rdfs:comment "Precondition that must be fulfilled to exercise this norm." .

rl2:priority a owl:DatatypeProperty ;
    rdfs:domain rl2:Norm ;
    rdfs:range xsd:integer ;
    rdfs:comment "Numeric priority for conflict resolution; higher values override lower values." .
```

#### 2. Semantics (RL2_Semantics.md:540-542)

Add Precondition denotation after Duty denotation:

```
Precondition activation:

⟦Precondition(action, constraint)⟧(Env) =
    Obligation(action)  if ⟦constraint⟧(Env) = true
    Inactive            otherwise
```

#### 3. Semantics (RL2_Semantics.md:888-896)

Update evaluation algorithm:

```
-- Step 1: Find matching norms (add priority ordering)
let matchingPrivileges = { p ∈ P.clauses | P ∈ applicablePolicies ∧ p : Privilege ∧ matches(p, R) }
let matchingProhibitions = { p ∈ P.clauses | ... }

-- Clause-level duties (standalone, action-matched)
let standaloneDuties = { d ∈ P.clauses | d : Duty ∧ matches(d, R) }

-- Preconditions (from matching privileges, no action matching)
let preconditions = { pc | ∃p ∈ matchingPrivileges : (p, rl2:requires, pc) }

-- Union all obligations
let allObligations = standaloneDuties ∪ preconditions

-- Step 2: Resolve priorities (NEW)
let activePrivileges = resolvePriorities(matchingPrivileges, ⟦_.condition⟧(Env))
let activeProhibitions = resolvePriorities(matchingProhibitions, ⟦_.condition⟧(Env))

-- Step 3: Update obligation states
let Σ' = updateDutyStates(allObligations, Env, Σ)
```

Add priority resolution function:

```
resolvePriorities(norms, conditionEval) =
    let active = { n ∈ norms | conditionEval(n) = true }
    let grouped = groupBy(active, n → (n.subject, n.action, n.object))
    for each group G:
        yield maxBy(G, n → n.priority)
```

#### 4. Semantics: Add Compilation Section

After line 1102 (## Relationship to RL2 Protocol), add new section:

```markdown
## Compilation from DDL to I/O Rules

RL2 policies are authored in DDL (with priorities, exceptions, defeat relations) and compiled to flat I/O rules for execution.

### Compilation Algorithm

For each privilege P in priority-resolved order:
    if P.condition holds and P not defeated:
        preconditions = { pc | (P, rl2:requires, pc) }
        emit_rule: (P.matchConditions ∧ P.condition) → (Permit + preconditions)

For each duty D:
    emit_rule: (D.matchConditions ∧ D.condition) → Obligation(D.action)

### Priority Resolution

When multiple norms match the same (subject, action, object), the norm with highest rl2:priority value wins. Defeated norms do not emit rules.

### Example

DDL Authoring:
```turtle
ex:basePrivilege a rl2:Privilege ;
    rl2:priority 100 ;
    rl2:action ex:display ;
    rl2:requires [ a rl2:Precondition ; rl2:obligatedAction ex:pay ] .

ex:staffException a rl2:Privilege ;
    rl2:priority 200 ;
    rl2:action ex:display ;
    rl2:condition [ rl2:leftOperand ex:role ; rl2:operator rl2:eq ; rl2:rightOperand "staff" ] .
```

Compiled I/O Rules:
```
Rule_staff: (action=display ∧ role=staff) → Permit
Rule_base:  (action=display ∧ role≠staff) → Permit + Obligation(pay)
```
```

#### 5. ODRL Coverage (RL2_ODRL_Coverage.md:105)

```markdown
| odrl:duty | rl2:Precondition (nested in permission) OR rl2:Duty (standalone) | Context-dependent mapping |
```

Add mapping rule:

```
ODRL Transformation:
- IF duty is nested in odrl:permission THEN map to rl2:Precondition via rl2:requires
- ELSE IF duty is top-level policy element THEN map to rl2:Duty via rl2:clause
```

#### 6. SHACL Validation

```turtle
rl2:PreconditionShape a sh:NodeShape ;
    sh:targetClass rl2:Precondition ;
    sh:property [
        sh:path [ sh:inversePath rl2:clause ] ;
        sh:maxCount 0 ;
        sh:message "Preconditions cannot be policy clauses (use rl2:Duty for standalone obligations)" .
    ] .

rl2:DutyNotPreconditionShape a sh:NodeShape ;
    sh:targetClass rl2:Duty ;
    sh:property [
        sh:path [ sh:inversePath rl2:requires ] ;
        sh:maxCount 0 ;
        sh:message "Duties cannot be preconditions (use rl2:Precondition for privilege-bound obligations)" .
    ] .
```

#### 7. Priority Guidelines (Documentation)

```markdown
Priority Ranges:
- 0-99: System defaults and base policies
- 100-199: Standard organizational policies
- 200-299: Departmental/role-based exceptions
- 300-399: Team-level policies
- 400-499: Individual grants and overrides
- 500+: Emergency/break-glass procedures
```

### Example Usage

```turtle
# Standalone duty (not privilege-bound)
ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:delete ;
    rl2:object ex:Dataset ;
    rl2:condition [ rl2:interval [ rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime ] ] .

# Privilege with precondition (ODRL-style permission/duty)
ex:displayPrivilege a rl2:Privilege ;
    rl2:priority 100 ;
    rl2:subject ex:User ;
    rl2:action ex:display ;
    rl2:object ex:Photo ;
    rl2:requires [
        a rl2:Precondition ;
        rl2:obligatedAction ex:pay ;
        rl2:constraint [ rl2:leftOperand ex:payAmount ; rl2:operator rl2:eq ; rl2:rightOperand 5.00 ]
    ] .

# Power with precondition (break-glass example)
ex:updateProdDataPower a rl2:Power ;
    rl2:priority 500 ;
    rl2:affectsNorm ex:prodDataOwnership ;
    rl2:requires [
        a rl2:Precondition ;
        rl2:obligatedAction ex:invokeBreakGlass ;
        rl2:constraint [ rl2:leftOperand ex:procedure ; rl2:operator rl2:eq ; rl2:rightOperand "emergency-override" ]
    ] .
```

---

## Other ODRL Compatibility Issues

### Inheritance (`odrl:inheritFrom`)

RL2 explicitly excludes runtime inheritance, requiring a pre-processing/flattening step. While semantically equivalent results can be achieved, it is not a syntactic superset.

**Recommendation:** Explicitly document the transformation required for `inheritFrom` in ODRL mapping documentation.

### Conflict Strategies (`odrl:conflict`)

ODRL allows policies to specify their conflict resolution strategy (e.g., `perm:perm`, `prohibit:perm`). RL2 relies on numeric priorities and compilation-time resolution.

**Recommendation:** Document how ODRL conflict strategies map to RL2 priority-based resolution in ODRL coverage documentation.

### Policy Request Type

ODRL defines `odrl:Request` as a policy class. `rl2.ttl` lacks a policy-level Request; `rl2p.ttl` introduces a runtime `rl2p:Request` (evaluation artifact, not a policy container).

**Recommendation:** Add `rl2:Request` policy subclass or document mapping for `odrl:Request` policies.

---

## Documentation Claim Refinement

The claim in `RL2_ODRL_Coverage.md` that "RL2 is a strict superset of ODRL" should be softened to **"Semantic Superset"** or **"Expressive Superset"** to acknowledge that transformation/compilation is required for certain ODRL features (inheritance, permission-bound duties with different actions).

---

## Documentation Synchronization Required

After implementing the ontology and semantics changes above, the following documentation must be updated:

* **RL2_Vocabulary.md** - Add `rl2:Precondition`, `rl2:obligatedAction`, `rl2:requires`, `rl2:priority` with full descriptions and examples
* **RL2_Core.md** - Update examples to show Precondition usage; add priority examples
* **RL2_ODRL_Coverage.md** - Update duty mapping table (line 105); add ODRL→RL2 transformation rules for nested duties
* **RL2_White_Paper.md** - Update architecture description to include DDL→I/O compilation layer
* **RL2_DiscussionTopics.md** - Remove or mark resolved any discussion of duty-binding approaches
