# **RL2 Core Specification (Draft v0.2)**

*A Unified Normative, Descriptive, and Operational Rights Language*

---

# **Table of Contents**

- Introduction
- Design Principles
- Conceptual Model
- RL2 Ontology (Complete Turtle)
  - Normative Layer (DPCL)
  - Promise Theory Layer
  - Agent + Role Layer
  - Action / Asset / Condition Layer
  - Operational (ODRE) Layer
  - Temporal and Context Layer
  - Policy Containers
- SHACL Grammar (Syntax Validation)
- Formal Semantics
- Role System (Normative vs Functional Roles)
- Diagram: RL2 Architecture
- References

---

# **Introduction**

RL2 (“Rights Language 2”) is a next-generation policy language designed as a standalone successor to existing rights languages. It provides a **strict superset** of capabilities found in:

* **ODRL 2.2** (W3C Recommendation)
* **DPCL** (Normative specification meta-language)
* **Promise Theory** (Burgess & Røstad)
* **ODRE** (Operational semantics for digital rights enforcement)

RL2 aims to unify:

* **descriptive policies** (permissions, prohibitions, duties)
* **normative relations** (powers, claims, liabilities, promises)
* **multi-party workflows** (approvals, internal obligations)
* **operational behavior** (events, triggers, state transitions)
* **temporal constraints** (validity intervals, sequences)
* **RDF/OWL + SHACL syntax and validation**
* **formal semantics** suitable for deterministic evaluation by a verified runtime kernel

Unlike prior standards, RL2 has **precise semantics**, **clean role modeling**, and **formal operational rules**, while still being **100% RDF-native** and **machine-interpretible**. It is designed to be a compilation target for ODRL 2.2, meaning legacy policies can be losslessly translated into RL2 for unambiguous execution.

---

# **Design Principles**

RL2 follows these design principles:

### **Standalone & Self-Contained**

RL2 does not import or depend on external ODRL definitions. It defines all necessary constructs natively to ensure semantic stability and version control.

### **Normative Completeness**

RL2 incorporates full Hohfeldian normative distinctions:

* Privilege
* Duty
* Claim
* Power
* Liability
* Immunity

### **Voluntary Cooperation**

Based on Promise Theory:

* Promises are voluntary commitments between agents,
* Not simply duties.

### **Clear Role Semantics**

Normative roles (subject, counterparty, promiser, promisee)
are distinct from syntactic/functional roles (grantor, approver, operator).

### **Operational Semantics**

RL2 policies have **state-dependent behavior**.
This is where ODRE concepts enter:

* Events
* Obligation states
* State transitions
* Sequential workflows

### **RDF-native, SHACL-validated**

The RL2 ontology is fully RDF/OWL, with a SHACL grammar defining:

* structural constraints
* cardinality requirements
* typing rules
* role consistency rules

### **Compatible with IR and verified kernels**

RL2 is designed to be translatable into an internal IR (stack-based or term-based)
for deterministic evaluation.

---

# **Conceptual Model**

RL2 consists of **seven layers**:

1. **Normative Layer**
   Fundamental legal/moral categories.
2. **Promise Theory Layer**
   Voluntary cooperation commitments.
3. **Role Layer**
   Roles of agents in normative or syntactic structures.
4. **Action/Asset/Condition Layer**
   Core structural elements.
5. **Operational Layer**
   Events, triggers, state transitions.
6. **Temporal/Context Layer**
   Time windows, dynamic references, contextual constraints.
7. **Policy Container Layer**
   Bundles normative clauses into policies.

The ontology below includes all of these.

---

# **Complete RL2 Ontology (Turtle)**

The ontology is now a self-contained definition. It replaces ODRL constructs with native RL2 equivalents.

```turtle
@base <https://rl2.example/ontology#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .

<https://rl2.example/ontology>
  a owl:Ontology ;
  rdfs:label "RL2 Ontology" ;
  dc:description "A unified normative, descriptive, and operational rights language." ;
  owl:versionInfo "0.2" ;
  owl:versionIRI <https://rl2.example/ontology/0.2> .

############################################################
# 4.1 Normative Layer (DPCL)
############################################################

# Norms represent deontic/legal relations between agents, actions, and assets.
rl2:Norm a owl:Class ;
    rdfs:label "Norm" ;
    rdfs:comment "A normative relation in the DPCL sense." .

rl2:Privilege a owl:Class ;
    rdfs:subClassOf rl2:Norm ;
    rdfs:label "Privilege" ;
    rdfs:comment "A normative absence of duty not to perform an action." .

rl2:Duty a owl:Class ;
    rdfs:subClassOf rl2:Norm ;
    rdfs:label "Duty" ;
    rdfs:comment "An obligation imposed on an agent." .

rl2:Prohibition a owl:Class ;
    rdfs:subClassOf rl2:Norm ;
    rdfs:label "Prohibition" ;
    rdfs:comment "A prohibition on performing an action." .

rl2:Claim a owl:Class ;
    rdfs:subClassOf rl2:Norm ;
    rdfs:label "Claim" ;
    rdfs:comment "A correlative entitlement held by another agent." .

rl2:Power a owl:Class ;
    rdfs:subClassOf rl2:Norm ;
    rdfs:label "Power" ;
    rdfs:comment "Ability to alter normative relations." .

rl2:Liability a owl:Class ;
    rdfs:subClassOf rl2:Norm ;
    rdfs:label "Liability" ;
    rdfs:comment "Exposure to exercise of power by another agent." .

rl2:Immunity a owl:Class ;
    rdfs:subClassOf rl2:Norm ;
    rdfs:label "Immunity" ;
    rdfs:comment "Protection against the power of another agent." .

# Hohfeldian Correlatives and Additional Norm Properties
# -------------------------------------------------------
# These properties capture the relational structure of Hohfeldian positions.

rl2:correlativeTo a owl:ObjectProperty, owl:SymmetricProperty ;
    rdfs:domain rl2:Norm ;
    rdfs:range rl2:Norm ;
    rdfs:comment "Links correlative Hohfeldian positions (Duty-Claim, Power-Liability, Immunity-Power)." .

rl2:claimHolder a owl:ObjectProperty ;
    rdfs:domain rl2:Claim ;
    rdfs:range rl2:Agent ;
    rdfs:comment "Agent who holds the claim (the right-holder)." .

rl2:claimAgainst a owl:ObjectProperty ;
    rdfs:domain rl2:Claim ;
    rdfs:range rl2:Agent ;
    rdfs:comment "Agent against whom the claim is held (the duty-bearer)." .

rl2:affectsNorm a owl:ObjectProperty ;
    rdfs:domain rl2:Power ;
    rdfs:range rl2:Norm ;
    rdfs:comment "The norm that this power can create, modify, or extinguish." .

rl2:exposedTo a owl:ObjectProperty ;
    rdfs:domain rl2:Liability ;
    rdfs:range rl2:Power ;
    rdfs:comment "The power to which this liability is exposed." .

rl2:immuneFrom a owl:ObjectProperty ;
    rdfs:domain rl2:Immunity ;
    rdfs:range rl2:Power ;
    rdfs:comment "The power from which this immunity protects." .

############################################################
# 4.2 Promise Theory Layer
############################################################

# A Promise is a voluntary commitment between agents.
rl2:Promise a owl:Class ;
    rdfs:label "Promise" ;
    rdfs:comment "Voluntary cooperative commitment from promiser to promisee." .

rl2:promiser a owl:ObjectProperty ;
    rdfs:domain rl2:Promise ;
    rdfs:range rl2:Agent ;
    rdfs:comment "Agent making the promise." .

rl2:promisee a owl:ObjectProperty ;
    rdfs:domain rl2:Promise ;
    rdfs:range rl2:Agent ;
    rdfs:comment "Agent receiving the benefit of the promise." .

rl2:PromiseContent a owl:Class ;
    owl:unionOf (rl2:Action rl2:Duty rl2:Condition) ;
    rdfs:label "Promise Content" ;
    rdfs:comment """Union of types that may constitute the content of a promise.
    Note: A promise references one of these types to describe what is promised.
    The promiser commits to performing an Action, fulfilling a Duty, or ensuring
    a Condition holds. This is a pragmatic modeling choice; the promise is
    'about' the content, not identical to it.""" .

rl2:promiseContent a owl:ObjectProperty ;
    rdfs:domain rl2:Promise ;
    rdfs:range rl2:PromiseContent ;
    rdfs:comment "Content of the promise: action, duty, or condition." .

############################################################
# 4.3 Agents and Roles
############################################################

rl2:Agent a owl:Class ;
    rdfs:label "Agent" ;
    rdfs:comment "Any party participating in a normative or functional role." .

# Normative roles (core semantic roles)
rl2:subject a owl:ObjectProperty ;
    rdfs:domain rl2:Norm ;
    rdfs:range rl2:Agent ;
    rdfs:comment "The agent bearing the normative status." .

rl2:counterparty a owl:ObjectProperty ;
    rdfs:domain rl2:Norm ;
    rdfs:range rl2:Agent ;
    rdfs:comment "The agent standing in normative relation to the subject." .

# Functional (syntactic) roles
rl2:grantor a owl:ObjectProperty ;
    rdfs:domain rl2:Policy ;
    rdfs:range rl2:Agent ;
    rdfs:comment "Agent granting a privilege or policy." .

rl2:grantee a owl:ObjectProperty ;
    rdfs:domain rl2:Policy ;
    rdfs:range rl2:Agent ;
    rdfs:comment "Agent receiving a privilege or policy." .

rl2:NormOrEvent a owl:Class ;
    owl:unionOf (rl2:Norm rl2:Event) ;
    rdfs:comment "Union class for properties applicable to both Norms and Events." .

rl2:approver a owl:ObjectProperty ;
    rdfs:domain rl2:NormOrEvent ;
    rdfs:range rl2:Agent ;
    rdfs:comment "Agent whose approval is required for activation." .

rl2:operationalAgent a owl:ObjectProperty ;
    rdfs:domain rl2:NormOrEvent ;
    rdfs:range rl2:Agent ;
    rdfs:comment "Agent performing an operational action." .

rl2:participant a owl:ObjectProperty ;
    rdfs:domain rl2:Event ;
    rdfs:range rl2:Agent ;
    rdfs:comment "General syntactic participant in a workflow or event." .

############################################################
# 4.4 Actions, Assets, Conditions
############################################################

rl2:Action a owl:Class ;
    rdfs:label "Action" ;
    rdfs:comment """An action that may be performed on an asset.
    RL2 Core does not define specific action instances; these are provided
    by profiles tailored to specific domains. For example:
    - A media licensing profile might define: play, stream, display, reproduce
    - A software license profile might define: execute, install, modify
    - A data governance profile might define: process, transfer, anonymize
    Profiles define actions as individuals of this class.""" .

rl2:Asset a owl:Class ;
    rdfs:label "Asset" ;
    rdfs:comment "A resource or object subject to normative control." .

rl2:AssetCollection a owl:Class ;
    rdfs:label "Asset Collection" ;
    rdfs:comment "A (possibly dynamic) collection of assets." .

rl2:Condition a owl:Class ;
    rdfs:label "Condition" ;
    rdfs:comment "A constraint or requirement that must hold for a norm to be active." .

rl2:LogicalConstraint a owl:Class ;
    rdfs:subClassOf rl2:Condition ;
    rdfs:label "Logical Constraint" ;
    rdfs:comment "A condition combining other conditions via logical operators." .

rl2:TemporalConstraint a owl:Class ;
    rdfs:subClassOf rl2:Condition ;
    rdfs:label "Temporal Constraint" ;
    rdfs:comment "A condition based on time intervals or temporal relations." .

rl2:ContextualConstraint a owl:Class ;
    rdfs:subClassOf rl2:Condition ;
    rdfs:label "Contextual Constraint" ;
    rdfs:comment "Constraint depending on contextual state or environment." .

rl2:DynamicOperandReference a owl:Class ;
    rdfs:subClassOf rl2:Condition ;
    rdfs:label "Dynamic Operand Reference" ;
    rdfs:comment "Reference resolved at evaluation time." .

rl2:EventConstraint a owl:Class ;
    rdfs:subClassOf rl2:Condition ;
    rdfs:label "Event Constraint" ;
    rdfs:comment "A condition requiring a specific event to occur, optionally with an approver." .

rl2:expectsEvent a owl:ObjectProperty ;
    rdfs:domain rl2:EventConstraint ;
    rdfs:range rl2:Event ;
    rdfs:comment "The event that must occur for this constraint to be satisfied." .

rl2:action a owl:ObjectProperty ;
    rdfs:domain rl2:Norm ;
    rdfs:range rl2:Action ;
    rdfs:comment "Action specified in a norm." .

rl2:prohibitedAction a owl:ObjectProperty ;
    rdfs:domain rl2:Prohibition ;
    rdfs:range rl2:Action ;
    rdfs:comment "Action prohibited by the norm." .

rl2:object a owl:ObjectProperty ;
    rdfs:domain rl2:Norm ;
    rdfs:range rl2:Asset ;
    rdfs:comment "Asset specified in a norm." .

rl2:member a owl:ObjectProperty ;
    rdfs:domain rl2:AssetCollection ;
    rdfs:range rl2:Asset ;
    rdfs:comment "Membership relation for asset collections." .

rl2:condition a owl:ObjectProperty ;
    rdfs:domain rl2:Norm ;
    rdfs:range rl2:Condition ;
    rdfs:comment "Condition that activates or constrains a norm." .

rl2:LeftOperand a owl:Class ;
    rdfs:label "Left Operand" ;
    rdfs:comment """A property or attribute to be evaluated in a condition.
    RL2 Core does not define specific left operand instances; these are
    provided by profiles (e.g., privacy, media licensing, financial).
    Profiles define left operands as individuals of this class, such as
    purpose, dateTime, spatial, recipient, payAmount, fileFormat, etc.""" .

rl2:leftOperand a owl:ObjectProperty ;
    rdfs:domain rl2:Condition ;
    rdfs:range rl2:LeftOperand ;
    rdfs:comment "Left operand of a condition (the property being evaluated)." .

rl2:constraintOperator a owl:ObjectProperty ;
    rdfs:domain rl2:Condition ;
    rdfs:range rl2:Operator ;
    rdfs:comment "Operator of a condition; may be a ComparisonOperator or LogicalOperator." .

rl2:rightOperand a owl:DatatypeProperty ;
    rdfs:domain rl2:Condition ;
    rdfs:comment "Right operand of a condition (literal value)." .

rl2:rightOperandRef a owl:ObjectProperty ;
    rdfs:domain rl2:Condition ;
    rdfs:comment "Right operand of a condition (resource reference)." .

rl2:ConditionOrEvent a owl:Class ;
    owl:unionOf (rl2:Condition rl2:Event) ;
    rdfs:label "Condition Or Event" ;
    rdfs:comment "Union class for properties that may reference either a Condition or an Event." .

rl2:requires a owl:ObjectProperty ;
    rdfs:domain rl2:Condition ;
    rdfs:range rl2:ConditionOrEvent ;
    rdfs:comment "Composite condition requirement; may require another condition or a specific event." .

rl2:dynamicOperand a owl:DatatypeProperty ;
    rdfs:domain rl2:DynamicOperandReference ;
    rdfs:range xsd:string ;
    rdfs:comment "Path expression resolved at evaluation time." .

rl2:contextPath a owl:DatatypeProperty ;
    rdfs:domain rl2:ContextualConstraint ;
    rdfs:range xsd:string ;
    rdfs:comment "Context path used in contextual constraints." .

rl2:dynamicQuery a owl:DatatypeProperty ;
    rdfs:domain rl2:AssetCollection ;
    rdfs:range xsd:string ;
    rdfs:comment "Query expression used to materialize dynamic collections." .

rl2:interval a owl:ObjectProperty ;
    rdfs:domain rl2:TemporalConstraint ;
    rdfs:range rl2:EffectiveInterval ;
    rdfs:comment "Interval used by a temporal constraint." .

# Operand property for LogicalConstraint
rl2:operand a owl:ObjectProperty ;
    rdfs:domain rl2:LogicalConstraint ;
    rdfs:range rl2:Condition ;
    rdfs:comment "A sub-condition operand of a logical constraint." .

# Operator Type Hierarchy
# -----------------------
# RL2 defines a typed operator system for use in constraints.

rl2:Operator a owl:Class ;
    rdfs:label "Operator" ;
    rdfs:comment "Abstract class for constraint operators." .

rl2:LogicalOperator a owl:Class ;
    rdfs:subClassOf rl2:Operator ;
    rdfs:label "Logical Operator" ;
    rdfs:comment "Operators for combining conditions (and, or, xone, not)." ;
    owl:oneOf (rl2:and rl2:or rl2:xone rl2:not) .

rl2:ComparisonOperator a owl:Class ;
    rdfs:subClassOf rl2:Operator ;
    rdfs:label "Comparison Operator" ;
    rdfs:comment "Operators for comparing values (eq, neq, lt, lte, gt, gte, isA, isAnyOf, isAllOf, isNoneOf)." ;
    owl:oneOf (rl2:eq rl2:neq rl2:lt rl2:lte rl2:gt rl2:gte rl2:isA rl2:isAnyOf rl2:isAllOf rl2:isNoneOf) .

# Logical Operators (for LogicalConstraint)
# -----------------------------------------
rl2:and a rl2:LogicalOperator ;
    rdfs:label "and" ;
    rdfs:comment "Logical conjunction: all sub-conditions must hold." .

rl2:or a rl2:LogicalOperator ;
    rdfs:label "or" ;
    rdfs:comment "Logical disjunction: at least one sub-condition must hold." .

rl2:xone a rl2:LogicalOperator ;
    rdfs:label "xone" ;
    rdfs:comment "Exclusive or: exactly one sub-condition must hold." .

rl2:not a rl2:LogicalOperator ;
    rdfs:label "not" ;
    rdfs:comment "Logical negation: the sub-condition must not hold." .

# Comparison Operators (for atomic Conditions)
# --------------------------------------------
rl2:eq a rl2:ComparisonOperator ;
    rdfs:label "eq" ;
    rdfs:comment "Equality comparison." .

rl2:neq a rl2:ComparisonOperator ;
    rdfs:label "neq" ;
    rdfs:comment "Inequality comparison." .

rl2:lt a rl2:ComparisonOperator ;
    rdfs:label "lt" ;
    rdfs:comment "Less-than comparison." .

rl2:lte a rl2:ComparisonOperator ;
    rdfs:label "lte" ;
    rdfs:comment "Less-than-or-equal comparison." .

rl2:gt a rl2:ComparisonOperator ;
    rdfs:label "gt" ;
    rdfs:comment "Greater-than comparison." .

rl2:gte a rl2:ComparisonOperator ;
    rdfs:label "gte" ;
    rdfs:comment "Greater-than-or-equal comparison." .

rl2:isA a rl2:ComparisonOperator ;
    rdfs:label "isA" ;
    rdfs:comment "Type/class membership check." .

rl2:isAnyOf a rl2:ComparisonOperator ;
    rdfs:label "isAnyOf" ;
    rdfs:comment "Value is any of a specified set." .

rl2:isAllOf a rl2:ComparisonOperator ;
    rdfs:label "isAllOf" ;
    rdfs:comment "Value satisfies all of a specified set." .

rl2:isNoneOf a rl2:ComparisonOperator ;
    rdfs:label "isNoneOf" ;
    rdfs:comment "Value is none of a specified set." .

############################################################
# 4.5 Operational Layer (ODRE)
############################################################

rl2:Event a owl:Class ;
    rdfs:label "Event" ;
    rdfs:comment "Observable event that may trigger obligations or transitions." .

# Obligation States (enumeration pattern)
rl2:ObligationState a owl:Class ;
    rdfs:label "Obligation State" ;
    rdfs:comment "State of a duty: pending, active, fulfilled, violated." ;
    owl:oneOf (rl2:Pending rl2:Active rl2:Fulfilled rl2:Violated) .

rl2:Pending a rl2:ObligationState ;
    rdfs:label "Pending" ;
    rdfs:comment "Duty exists but activation condition not yet met." .

rl2:Active a rl2:ObligationState ;
    rdfs:label "Active" ;
    rdfs:comment "Duty is active and must be fulfilled." .

rl2:Fulfilled a rl2:ObligationState ;
    rdfs:label "Fulfilled" ;
    rdfs:comment "Duty has been satisfied." .

rl2:Violated a rl2:ObligationState ;
    rdfs:label "Violated" ;
    rdfs:comment "Duty was not fulfilled within required constraints." .

# Promise States (enumeration pattern)
rl2:PromiseState a owl:Class ;
    rdfs:label "Promise State" ;
    rdfs:comment "State of a promise: pending, fulfilled, violated." ;
    owl:oneOf (rl2:PromisePending rl2:PromiseFulfilled rl2:PromiseViolated) .

rl2:PromisePending a rl2:PromiseState ;
    rdfs:label "Promise Pending" ;
    rdfs:comment "Promise has been made but not yet fulfilled." .

rl2:PromiseFulfilled a rl2:PromiseState ;
    rdfs:label "Promise Fulfilled" ;
    rdfs:comment "Promise content has been satisfied." .

rl2:PromiseViolated a rl2:PromiseState ;
    rdfs:label "Promise Violated" ;
    rdfs:comment "Promise was broken or deadline expired without fulfillment." .

rl2:promiseState a owl:ObjectProperty ;
    rdfs:domain rl2:Promise ;
    rdfs:range rl2:PromiseState ;
    rdfs:comment "Current state of the promise." .

rl2:obligationState a owl:ObjectProperty ;
    rdfs:domain rl2:Duty ;
    rdfs:range rl2:ObligationState ;
    rdfs:comment "Current state of the duty." .

rl2:StateTransition a owl:Class ;
    rdfs:label "State Transition" ;
    rdfs:comment "Transition in system state resulting from events or actions." .

rl2:triggeredBy a owl:ObjectProperty ;
    rdfs:domain rl2:StateTransition ;
    rdfs:range rl2:Event ;
    rdfs:comment "Event triggering a transition." .

rl2:fromState a owl:ObjectProperty ;
    rdfs:domain rl2:StateTransition ;
    rdfs:comment "State before the transition." .

rl2:toState a owl:ObjectProperty ;
    rdfs:domain rl2:StateTransition ;
    rdfs:comment "State after the transition." .

rl2:after a owl:ObjectProperty ;
    rdfs:comment "Temporal sequence relation between events or transitions." .

############################################################
# 4.6 Temporal and Contextual Constructs
############################################################

rl2:EffectiveInterval a owl:Class ;
    rdfs:label "Effective Interval" ;
    rdfs:comment "A time interval with explicit start and end." .

rl2:start a owl:DatatypeProperty ;
    rdfs:domain rl2:EffectiveInterval ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "Start of an interval." .

rl2:end a owl:DatatypeProperty ;
    rdfs:domain rl2:EffectiveInterval ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "End of an interval." .

############################################################
# 4.7 Policy Containers
############################################################

rl2:Policy a owl:Class ;
    rdfs:label "Policy" ;
    rdfs:comment "A container of one or more RL2 normative clauses." .

# Policy Types as Subclasses
# --------------------------
# RL2 distinguishes policy types by their normative force and party structure.

rl2:Set a owl:Class ;
    rdfs:subClassOf rl2:Policy ;
    rdfs:label "Set" ;
    rdfs:comment """A unilateral policy declaration without identified counterparties.
    Sets express normative positions but do not create binding obligations between
    specific parties. They may be used for public licenses, general terms, or
    policy templates. No acceptance or agreement is required for a Set to be valid.""" .

rl2:Offer a owl:Class ;
    rdfs:subClassOf rl2:Policy ;
    rdfs:label "Offer" ;
    rdfs:comment """A policy proposed by an assigner to potential assignees.
    An Offer expresses willingness to grant privileges or accept duties, contingent
    on acceptance. It creates no obligations until accepted, at which point it
    becomes an Agreement.""" .

rl2:Agreement a owl:Class ;
    rdfs:subClassOf rl2:Policy ;
    rdfs:label "Agreement" ;
    rdfs:comment """A bilateral or multilateral policy with identified, consenting parties.
    Unlike a Set, an Agreement binds specific agents who have accepted its terms.
    All parties are identified via grantor/grantee or subject/counterparty roles.
    Duties in an Agreement create enforceable obligations; violations have
    normative consequences for the violating party.""" .

rl2:Privacy a owl:Class ;
    rdfs:subClassOf rl2:Policy ;
    rdfs:label "Privacy" ;
    rdfs:comment """A policy governing personal data processing and data subject rights.
    Privacy policies typically include duties on data controllers, privileges
    for data subjects, and conditions related to consent, purpose limitation,
    and data retention.""" .

rl2:Assertion a owl:Class ;
    rdfs:subClassOf rl2:Policy ;
    rdfs:label "Assertion" ;
    rdfs:comment """A policy stating claims or facts about normative status.
    Assertions declare that certain privileges, duties, or conditions hold,
    without necessarily creating them. Used for compliance statements,
    certification claims, or status declarations.""" .

# Note on Evaluation:
# -------------------
# Policy evaluation is a complex runtime process that may span multiple events,
# state transitions, and temporal intervals. The semantics of evaluation are
# defined in RL2_Semantics.md (Sections 7-8) rather than as an ontology class.
# Future versions may introduce rl2:EvaluationContext or rl2:EvaluationResult
# once operational patterns stabilize.

rl2:clause a owl:ObjectProperty ;
    rdfs:domain rl2:Policy ;
    rdfs:range rl2:Norm ;
    rdfs:comment "Associates norms with a policy container." .

rl2:clauseOf a owl:ObjectProperty ;
    owl:inverseOf rl2:clause ;
    rdfs:domain rl2:Norm ;
    rdfs:range rl2:Policy ;
    rdfs:comment "The policy containing this norm." .

```

---

# **SHACL Grammar (Syntax Validation)**

Core shapes are included here for syntactic correctness and policy typing.

```turtle
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# Policy shape - validates policy structure
# Note: Policy types are subclasses, so rdf:type checks class membership directly
rl2:PolicyShape a sh:NodeShape ;
    sh:targetClass rl2:Policy ;
    sh:property [
        sh:path rl2:clause ;
        sh:minCount 1 ;
        sh:class rl2:Norm ;
        sh:message "A policy must have at least one clause (norm)."
    ] ;
    sh:property [
        sh:path rl2:grantor ;
        sh:maxCount 1 ;
        sh:class rl2:Agent
    ] ;
    sh:property [
        sh:path rl2:grantee ;
        sh:maxCount 1 ;
        sh:class rl2:Agent
    ] .

# Agreement requires both grantor and grantee
rl2:AgreementShape a sh:NodeShape ;
    sh:targetClass rl2:Agreement ;
    sh:property [
        sh:path rl2:grantor ;
        sh:minCount 1 ;
        sh:message "An Agreement must identify a grantor."
    ] ;
    sh:property [
        sh:path rl2:grantee ;
        sh:minCount 1 ;
        sh:message "An Agreement must identify a grantee."
    ] .

rl2:PrivilegeShape a sh:NodeShape ;
    sh:targetClass rl2:Privilege ;
    sh:property [ sh:path rl2:subject ; sh:minCount 1 ; sh:class rl2:Agent ] ;
    sh:property [ sh:path rl2:action ; sh:minCount 1 ; sh:class rl2:Action ] ;
    sh:property [ sh:path rl2:object ; sh:minCount 1 ] .

rl2:DutyShape a sh:NodeShape ;
    sh:targetClass rl2:Duty ;
    sh:property [ sh:path rl2:subject ; sh:minCount 1 ; sh:class rl2:Agent ] ;
    sh:property [ sh:path rl2:action ; sh:minCount 1 ; sh:class rl2:Action ] ;
    sh:property [ sh:path rl2:object ; sh:minCount 1 ] .

rl2:ProhibitionShape a sh:NodeShape ;
    sh:targetClass rl2:Prohibition ;
    sh:property [ sh:path rl2:subject ; sh:minCount 1 ; sh:class rl2:Agent ] ;
    sh:property [ sh:path rl2:prohibitedAction ; sh:minCount 1 ; sh:class rl2:Action ] ;
    sh:property [ sh:path rl2:object ; sh:minCount 1 ] .

rl2:PromiseShape a sh:NodeShape ;
    sh:targetClass rl2:Promise ;
    sh:property [ sh:path rl2:promiser ; sh:minCount 1 ; sh:class rl2:Agent ] ;
    sh:property [ sh:path rl2:promisee ; sh:minCount 1 ; sh:class rl2:Agent ] ;
    sh:property [ sh:path rl2:promiseContent ; sh:minCount 1 ] .

# Condition shapes - split by subclass for proper validation
# ----------------------------------------------------------

# Atomic conditions (base Condition class used for simple comparisons)
rl2:AtomicConditionShape a sh:NodeShape ;
    sh:targetClass rl2:Condition ;
    sh:property [ sh:path rl2:leftOperand ; sh:minCount 1 ] ;
    sh:property [ sh:path rl2:constraintOperator ; sh:minCount 1 ; sh:class rl2:ComparisonOperator ] ;
    sh:or (
        [ sh:property [ sh:path rl2:rightOperand ; sh:minCount 1 ] ]
        [ sh:property [ sh:path rl2:rightOperandRef ; sh:minCount 1 ] ]
    ) .

# Logical constraints combine sub-conditions via logical operators
rl2:LogicalConstraintShape a sh:NodeShape ;
    sh:targetClass rl2:LogicalConstraint ;
    sh:property [ sh:path rl2:constraintOperator ; sh:minCount 1 ; sh:class rl2:LogicalOperator ] ;
    sh:property [ sh:path rl2:operand ; sh:minCount 1 ; sh:class rl2:Condition ] .

# Contextual constraints require a context path
rl2:ContextualConstraintShape a sh:NodeShape ;
    sh:targetClass rl2:ContextualConstraint ;
    sh:property [ sh:path rl2:contextPath ; sh:minCount 1 ; sh:datatype xsd:string ] .

# Dynamic operand references require a dynamic operand path
rl2:DynamicOperandReferenceShape a sh:NodeShape ;
    sh:targetClass rl2:DynamicOperandReference ;
    sh:property [ sh:path rl2:dynamicOperand ; sh:minCount 1 ; sh:datatype xsd:string ] .

# Event constraints require an expected event
rl2:EventConstraintShape a sh:NodeShape ;
    sh:targetClass rl2:EventConstraint ;
    sh:property [ sh:path rl2:expectsEvent ; sh:minCount 1 ; sh:class rl2:Event ] .

rl2:TemporalConstraintShape a sh:NodeShape ;
    sh:targetClass rl2:TemporalConstraint ;
    sh:property [
        sh:path rl2:interval ;
        sh:minCount 1 ;
        sh:class rl2:EffectiveInterval
    ] .

rl2:EffectiveIntervalShape a sh:NodeShape ;
    sh:targetClass rl2:EffectiveInterval ;
    sh:property [
        sh:path rl2:start ;
        sh:maxCount 1 ;
        sh:datatype xsd:dateTime
    ] ;
    sh:property [
        sh:path rl2:end ;
        sh:maxCount 1 ;
        sh:datatype xsd:dateTime
    ] ;
    sh:sparql [
        sh:message "rl2:start must be less than or equal to rl2:end" ;
        sh:prefixes rl2: ;
        sh:select """
            SELECT $this
            WHERE {
                $this rl2:start ?start .
                $this rl2:end ?end .
                FILTER (?start > ?end)
            }
        """
    ] .

rl2:AssetCollectionShape a sh:NodeShape ;
    sh:targetClass rl2:AssetCollection ;
    sh:property [
        sh:path rl2:member ;
        sh:class rl2:Asset
    ] ;
    sh:property [
        sh:path rl2:dynamicQuery ;
        sh:maxCount 1 ;
        sh:datatype xsd:string
    ] .
```

# **Example: Standalone RL2 Policy (Turtle)**

This example demonstrates a pure RL2 policy. Note that actions and left operands
are defined by the policy author or a domain profile, not by RL2 Core.

```turtle
@prefix ex:   <https://example.org/demo#> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# Domain-specific actions (defined by this policy/profile)
ex:use a rl2:Action ;
    rdfs:label "use" ;
    rdfs:comment "Exercise or consume an asset." .

ex:distribute a rl2:Action ;
    rdfs:label "distribute" ;
    rdfs:comment "Make an asset available to third parties." .

ex:submitReport a rl2:Action ;
    rdfs:label "submitReport" ;
    rdfs:comment "Submit a research report on dataset usage." .

# Agents
ex:DataOwner a rl2:Agent .
ex:Researcher a rl2:Agent .

# Asset
ex:DatasetA a rl2:Asset .

# A Set policy: unilateral declaration, no binding agreement
ex:policy1 a rl2:Set ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:use1 , ex:report1 , ex:ban1 .

ex:use1 a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:DatasetA ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:start "2024-09-01T00:00:00Z"^^xsd:dateTime ;
            rl2:end   "2025-01-31T23:59:59Z"^^xsd:dateTime
        ]
    ] .

ex:report1 a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:submitReport ;
    rl2:object ex:DatasetA ;
    rl2:obligationState rl2:Pending ;
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            rl2:end "2024-12-15T23:59:59Z"^^xsd:dateTime
        ]
    ] .

ex:ban1 a rl2:Prohibition ;
    rl2:subject ex:Researcher ;
    rl2:prohibitedAction ex:distribute ;
    rl2:object ex:DatasetA .
```

Notes:

* Policy type is expressed via `rdf:type` (e.g., `a rl2:Set`), not a separate `policyType` property.
* Actions are defined in the example namespace (`ex:`). RL2 Core provides the `rl2:Action` class; profiles or policies define the vocabulary.
* Temporal constraints use the `rl2:interval` wrapper with `rl2:EffectiveInterval`.
* Duty state is explicit via `rl2:obligationState`.

---

# **Formal Semantics**

RL2 is defined by a rigorous formal semantics that unifies normative logic, promise theory, and operational state transitions.

The complete formal semantics—including denotational definitions, small-step operational rules, and the policy evaluation function—are specified in **RL2_Semantics.md**.

Key semantic components include:
*   **Semantic Universe**: Agents, Actions, Assets, States, Events.
*   **Denotational Semantics**: Truth conditions for Norms and Conditions.
*   **Operational Semantics**: State transitions for Duty lifecycle (Pending -> Active -> Fulfilled/Violated).
*   **Event Semantics**: How events trigger transitions.


---

# **Role System**

RL2 distinguishes between normative roles (which have deontic significance) and functional roles (which describe workflow or syntactic positions).

## Normative Roles

| Role | Property | Description |
|------|----------|-------------|
| Subject | `rl2:subject` | Agent bearing the normative burden (duty-bearer, privilege-holder) |
| Counterparty | `rl2:counterparty` | Agent in correlative normative position (claim-holder against duty-bearer) |
| Claim Holder | `rl2:claimHolder` | Agent who holds a claim-right |
| Claim Against | `rl2:claimAgainst` | Agent against whom the claim is enforceable |

## Promise Roles

| Role | Property | Description |
|------|----------|-------------|
| Promiser | `rl2:promiser` | Agent making a voluntary commitment |
| Promisee | `rl2:promisee` | Agent who is the beneficiary of the promise |

## Functional (Syntactic) Roles

| Role | Property | Description |
|------|----------|-------------|
| Grantor | `rl2:grantor` | Agent who issues or grants the policy |
| Grantee | `rl2:grantee` | Agent who receives privileges under the policy |
| Approver | `rl2:approver` | Agent whose approval is required for activation |
| Operational Agent | `rl2:operationalAgent` | Agent performing operational actions |
| Participant | `rl2:participant` | General participant in a workflow or event |

---

# **RL2 Architecture Diagram (ASCII)**

```
                      +-------------------+
                      |      rl2:Policy  |
                      +---------+---------+
                                |
                                v
                        +---------------+
                        |    rl2:Norm   |
                        +---------------+
        -------------------------------------------------
        |                 |                |            |
   Privilege            Duty             Claim        Power ...
        |
        v
+-----------------+      +------------------+
| Agents & Roles  |      |  Actions/Assets  |
+-----------------+      +------------------+
        |
        v
+---------------------------------------------------------+
| Operational / Temporal / Contextual (Events, States...) |
+---------------------------------------------------------+
```

---

# **References**

See **RL2_References.md** for complete citations and glossary.

Key sources:
* [Hohfeld 1919] — Fundamental Legal Conceptions (Hohfeldian relations)
* [DPCL] — Language Template for Normative Specifications
* [Promise Theory] — Burgess & Bergstra
* [ODRE] — Operational semantics for duty lifecycle
* [OWL 2], [SHACL], [RDF 1.1] — Semantic web foundations