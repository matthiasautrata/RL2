# RL2 References and Glossary

*Companion document for the RL2 specification suite*

---

## Table of Contents

- References
  - Normative Foundations
  - Policy Languages
  - Access Control
  - Semantic Web
- Glossary

---

# References

## Normative Foundations

**[Hohfeld 1919]** Hohfeld, Wesley Newcomb. *Fundamental Legal Conceptions as Applied in Judicial Reasoning*. Yale University Press, 1919.
- Defines the eight fundamental legal relations: Privilege, Duty, Claim, Power, Liability, Immunity, No-Right, Disability
- RL2 adopts six of these (excluding No-Right and Disability as they are absence-of relations)

**[DPCL]** Governatori, Guido, et al. "DPCL: A Language Template for Normative Specifications." *Electronic Government and the Information Systems Perspective*, Springer, 2014.
- https://link.springer.com/chapter/10.1007/978-3-319-10178-1_8
- Provides the normative layer template that RL2 builds upon

**[Promise Theory]** Burgess, Mark, and Jan Bergstra. *Promise Theory: Principles and Applications*. 2014.
- http://markburgess.org/promises.html
- Voluntary cooperation model adopted for RL2's Promise layer

## Policy Languages

**[ODRL 2.2 Model]** W3C. "ODRL Information Model 2.2." W3C Recommendation, 15 February 2018.
- https://www.w3.org/TR/odrl-model/
- The policy model that RL2 extends and clarifies

**[ODRL 2.2 Vocab]** W3C. "ODRL Vocabulary & Expression 2.2." W3C Recommendation, 15 February 2018.
- https://www.w3.org/TR/odrl-vocab/
- Core vocabulary; RL2 provides equivalent constructs in the `rl2:` namespace

**[ODRL Best Practices]** W3C. "ODRL Implementation Best Practices." W3C Working Group Note, 15 February 2018.
- https://www.w3.org/TR/odrl-bp/
- Practical guidance referenced for RL2 compatibility

**[ODRL Formal Semantics]** W3C. "Formal Semantics for the ODRL Policy Language." Draft Community Group Report.
- https://w3c.github.io/odrl/formal-semantics/
- Formal model that RL2 Semantics extends with operational rules
- Defines ODRL Evaluator behavior, state of the world, and compliance checking

**[ODRL 3.0]** W3C ODRL Community Group. "ODRL 3.0 Use Cases and Requirements." Work in progress.
- https://www.w3.org/community/odrl/
- Emerging requirements that RL2 anticipates and addresses

**[ODRE 2024]** Poltronieri, Andrea, et al. "Open Digital Rights Enforcement Framework (ODRE): From Descriptive to Enforceable Policies." *Computers & Security*, 2024.
- https://www.sciencedirect.com/science/article/pii/S0167404824005881
- https://arxiv.org/abs/2409.17602
- Provides ODRL with enforcement capabilities via operational semantics
- Defines obligation lifecycle (Pending → Active → Fulfilled/Violated)
- Covers synchronous and asynchronous enforcement modes
- RL2 incorporates ODRE state machine concepts and extends with Hohfeldian normative theory

**[Pucella-Weissman 2006]** Pucella, Riccardo, and Vicky Weissman. "A Formal Foundation for ODRL." 2006.
- https://arxiv.org/abs/cs/0601085
- First formal semantics for ODRL; proves permission implication is decidable NP-hard
- Defines tractable fragment of ODRL

**[Steyskal-Polleres 2015]** Steyskal, Simon, and Axel Polleres. "Towards Formal Semantics for ODRL Policies." *RuleML*, 2015.
- https://link.springer.com/chapter/10.1007/978-3-319-21542-6_23
- Explores action dependencies in access control policies
- Proposes rule-based reasoning over ODRL policy expressions

**[Fornara-Colombetti 2017]** Fornara, Nicoletta, and Marco Colombetti. "Operational Semantics of an Extension of ODRL Able to Express Obligations." *EUMAS/AT*, 2017.
- https://link.springer.com/chapter/10.1007/978-3-030-01713-2_13
- Extends ODRL with conditional obligations and operational semantics
- Uses Apache Jena rule engine for automatic reasoning on obligation states

**[Fornara-Colombetti 2019]** Fornara, Nicoletta, and Marco Colombetti. "Using Semantic Web Technologies and Production Rules for Reasoning on Obligations, Permissions, and Prohibitions." *AI Communications* 32(4), 2019.
- Extends ODRL with activation events and temporal aspects
- Operational semantics via Discrete State Machines

**[Bonatti-Fornara-Harth 2025]** Bonatti, Piero Andrea, Nicoletta Fornara, and Andreas Harth. "Towards a Formal Semantics of the Open Digital Rights Language (ODRL 2.2)." *OPAL 2025* (co-located with ESWC), Portorož, Slovenia, June 2025.
- https://ceur-ws.org/Vol-3977/OPAL2025-4.pdf
- Proposes declarative, model-theoretic semantics for ODRL 2.2's core constructs
- Identifies ambiguities in ODRL's informal specification (duty fulfillment semantics, pre/post-condition duties, constraint activation vs fulfillment, gap resolution, policy scope)
- RL2 addresses these same issues through clean-slate design rather than retroactive formalization
- Includes formal definitions of compliance for monitoring, access control, and policy comparison mechanisms

## Access Control

**[XACML 3.0]** OASIS. "eXtensible Access Control Markup Language (XACML) Version 3.0." OASIS Standard, 22 January 2013.
- https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html
- PDP/PEP architecture referenced for RL2 Protocol design

**[OB-XACML]** Marra, A.L., et al. "OB-XACML: Towards a Full Support of Obligations in XACML." *Trust, Privacy and Security in Digital Business*, Springer, 2015.
- https://link.springer.com/chapter/10.1007/978-3-319-17127-2_14
- Obligation handling patterns that informed RL2 duty tracking

**[Cedar 2024]** Cutler, John G., et al. "Cedar: A New Language for Expressive, Fast, Safe, and Analyzable Authorization." *Proceedings of the ACM on Programming Languages* (OOPSLA), 2024.
- https://dl.acm.org/doi/10.1145/3649835
- https://docs.cedarpolicy.com/
- AWS authorization language with formal verification in Lean
- Supports RBAC and ABAC; lacks obligation lifecycle and temporal semantics
- RL2 comparison: Cedar focuses on fast runtime decisions; RL2 adds normative and operational layers

**[OPA/Rego]** Open Policy Agent. "Policy Language (Rego)." CNCF Project.
- https://www.openpolicyagent.org/
- General-purpose policy engine based on Datalog
- Highly expressive but Turing-complete; runtime exceptions possible
- RL2 comparison: RL2 trades expressiveness for decidability and formal verification

## Data Products and Data Contracts

**[DPROD 2024]** Object Management Group. "Data Product Ontology (DPROD) Version 1.0." OMG Specification, 2024.
- https://www.omg.org/spec/DPROD/
- Extends W3C DCAT for data product metadata
- References ODRL for usage policies; RL2 can serve as the policy layer

**[ODCS]** BITOL. "Open Data Contract Standard (ODCS) v3.0."
- https://bitol-io.github.io/open-data-contract-standard/
- YAML-based schema for data contracts with quality rules and policies
- Focuses on metadata; RL2 provides semantic policy framework

**[ODPS]** Open Data Products Initiative. "Open Data Product Specification."
- https://opendataproducts.org/
- Metadata standard for data products with data contract support (2024)

**[DCAT]** W3C. "Data Catalog Vocabulary (DCAT) - Version 3." W3C Recommendation, 2024.
- https://www.w3.org/TR/vocab-dcat-3/
- Vocabulary for data catalogs; DPROD extends DCAT for data products

## Formal Verification

**[Why3]** Filliâtre, Jean-Christophe, and Andrei Paskevich. "Why3 — Where Programs Meet Provers." *ESOP*, 2013.
- https://www.why3.org/
- Platform for deductive program verification with WhyML specification language
- Backend for multiple provers (Alt-Ergo, Z3, CVC5) and proof assistants (Coq, Isabelle)
- Target for RL2 semantics mechanization

**[Why3-Coq 2024]** Cohen, Joshua M., and Philip Johnson-Freyd. "A Formalization of Core Why3 in Coq." 2024.
- https://www.osti.gov/biblio/2311377
- Formal semantics for Why3 logic fragment in Coq
- Correct-by-construction natural deduction proof system

**[K Framework]** Roșu, Grigore. "K: A Semantic Framework for Programming Languages and Formal Analysis Tools." *Marktoberdorf Summer School*, 2017.
- https://kframework.org/
- Rewrite-based executable semantic framework
- 20-year effort toward ideal language framework vision
- Used for formal semantics of JavaScript, PHP, C, Java
- Alternative target for RL2 executable semantics

**[Lean 4]** de Moura, Leonardo, et al. "The Lean 4 Theorem Prover and Programming Language." *CADE*, 2021.
- https://lean-lang.org/
- Proof assistant and functional programming language
- Strong type system, tactic framework, code extraction
- Notable: AlphaProof (2024) achieved IMO silver medal using Lean
- Potential target for RL2 mechanization with executable extraction

**[Coq]** The Coq Development Team. "The Coq Proof Assistant."
- https://coq.inria.fr/
- Interactive theorem prover based on Calculus of Inductive Constructions
- Used for CompCert verified C compiler
- Alternative to Why3/Lean for RL2 mechanization

## Deontic Logic and Normative Reasoning

**[von Wright 1963]** von Wright, Georg Henrik. *Norm and Action: A Logical Enquiry*. Routledge & Kegan Paul, 1963.
- Foundational work in deontic logic distinguishing norms governing actions from norms governing states of affairs
- Introduces the distinction between:
  - **Action norms** (obligation to *do* A) → maps to RL2's **Tun-Sollen**
  - **State norms** (obligation that *p be the case*) → maps to RL2's **Sein-Sollen**
- **RL2 relevance**: Primary conceptual foundation for RL2's separation of action-directed norms (Promises, permissions, prohibitions evaluated at request/event time) from state-directed norms (invariants, compliance conditions, boundary sets evaluated continuously). This distinction resolves ODRL's conflation of procedural constraints with declarative state requirements.

**[Brown 2013]** Brown, Mark A. "The Structure of Deontic Logic." In Gabbay, Dov, et al. (eds.), *Handbook of Deontic Logic and Normative Systems*, vol. 1, College Publications, 2013.
- Modern survey explicitly separating action-based and state-based deontic logics
- Demonstrates why O(p) (state obligation) and O(do A) (action obligation) require different formal treatments
- Analyzes how violations behave differently in each logic: action violations are events, state violations are conditions
- **RL2 relevance**: Provides formal justification for RL2's two-layer architecture. Action-based logic governs runtime authorization decisions (Tun-Sollen); state-based logic governs compliance monitoring and invariant checking (Sein-Sollen). The differing violation semantics explain why RL2 separates entitlement engines from audit engines.

**[UCON_ABC]** Park, Jaehong, and Ravi Sandhu. "The UCON_ABC Usage Control Model." *ACM Transactions on Information and System Security (TISSEC)* 7(1), February 2004.
- https://profsandhu.com/journals/tissec/ucon-abc.pdf
- Foundational usage control model integrating Authorizations, oBligations, and Conditions
- Introduces continuity (ongoing controls) and mutability of attributes
- **RL2 relevance**: UCON uses binary obligation states (satisfied/revoked) vs RL2's explicit lifecycle (Pending→Active→Fulfilled/Violated). UCON's continuity concept validates RL2's operational layer; its mutability patterns support RL2's Power normative concept. Functional decision model (f(subject, resource, env, obligations)) informs Why3 mechanization.
- **Gap**: UCON lacks Hohfeldian normative categories; operates via allow/deny rather than explicit normative relations

**[LegalRuleML]** Athan, Tara, Guido Governatori, Monica Palmirani, Adrian Paschke, and Adam Wyner. "LegalRuleML: Design Principles and Foundations." *Reasoning Web 2015*, LNCS 9203, Springer, 2015.
- https://link.springer.com/chapter/10.1007/978-3-319-21768-0_6
- XML format extending RuleML for legal domain norms; based on defeasible logic
- Includes deontic operators: obligations, permissions, prohibitions, rights
- **RL2 relevance**: LegalRuleML's defeasibility (rule conflicts, exclusionary rules) addresses normative conflict that RL2 currently delegates to profiles. Its temporalized normative positions align with RL2's operational semantics. Syntax based on defeasible logic offers alternative formalization path.
- **Gap**: LegalRuleML uses XML vs RL2's RDF/OWL; lacks Promise Theory integration

**[OWL-POLAR]** Sensoy, Murat, Timothy J. Norman, Wamberto W. Vasconcelos, and Katia Sycara. "OWL-POLAR: A Framework for Semantic Policy Representation and Reasoning." *Journal of Web Semantics* 12-13, April 2012.
- https://www.sciencedirect.com/science/article/abs/pii/S1570826811000965
- OWL-DL based policy representation with decidable reasoning
- Covers permissions, prohibitions, obligations; conflict detection and resolution
- **RL2 relevance**: Directly relevant—uses OWL-DL like RL2. Demonstrates decidable policy reasoning within OWL bounds. Conflict anticipation mechanisms could inform RL2 conflict handling. Authority modeling (who issues policy) parallels RL2's grantor/grantee.
- **Gap**: Predates SHACL; focuses on multi-agent systems rather than data governance

**[Rodríguez-Doncel 2024]** Esteves, Beatriz, Víctor Rodríguez-Doncel, et al. "Analysis of Ontologies and Policy Languages to Represent Information Flows in GDPR." *Semantic Web Journal*, 2024.
- https://journals.sagepub.com/doi/10.3233/SW-223009
- Surveys 13 policy languages and 9 data protection vocabularies against 57 GDPR informational items
- Finds ODRL + DPV + GDPRtEXT covers 39/57 items; identifies temporal/spatial constraint gaps
- **RL2 relevance**: Validates ODRL as best foundation (which RL2 extends). Identifies gaps RL2 should address: retention periods, data expiry, sector-specific constraints. Suggests vocabulary layering approach (core + domain profiles) that aligns with RL2's profile extensibility.
- **Action**: Review 57 GDPR items for RL2 Privacy policy coverage

**[ODRL Limitations 2025]** "Improving ODRL 2.2: Current Limitations and Theoretical Solutions." *OPAL 2025* (co-located with ESWC), June 2025.
- https://ceur-ws.org/Vol-3977/OPAL2025-6.pdf
- Systematically catalogs ODRL 2.2 limitations with proposed taxonomy
- Notes ODRL has only informal English semantics; no enforcement specification
- **RL2 relevance**: Directly validates RL2's design rationale—RL2 addresses these exact gaps through formal operational semantics. Paper's taxonomy of limitations provides checklist for RL2 completeness verification.
- **Action**: Cross-reference limitation taxonomy against RL2 design decisions

## Semantic Web

**[OWL 2]** W3C. "OWL 2 Web Ontology Language." W3C Recommendation, 11 December 2012.
- https://www.w3.org/TR/owl2-overview/
- Ontology language used for RL2 Core

**[SHACL]** W3C. "Shapes Constraint Language (SHACL)." W3C Recommendation, 20 July 2017.
- https://www.w3.org/TR/shacl/
- Constraint language used for RL2 syntax validation

**[RDF 1.1]** W3C. "RDF 1.1 Concepts and Abstract Syntax." W3C Recommendation, 25 February 2014.
- https://www.w3.org/TR/rdf11-concepts/
- Data model underlying RL2

**[Turtle]** W3C. "RDF 1.1 Turtle." W3C Recommendation, 25 February 2014.
- https://www.w3.org/TR/turtle/
- Serialization format used in RL2 examples

---

# Glossary

## Normative Terms

**Agent**
: Any party participating in a normative or functional role. Includes persons, organizations, and software systems.

**Claim**
: A Hohfeldian correlative to Duty. If A has a duty to B, then B has a claim against A.

**Counterparty**
: The agent standing in normative relation to the subject of a norm.

**Duty**
: An obligation imposed on an agent to perform (or refrain from) an action.

**Immunity**
: Protection against the power of another agent to alter one's normative position.

**Liability**
: Exposure to the exercise of power by another agent.

**Norm**
: A normative relation in the DPCL/Hohfeldian sense. Superclass of Privilege, Duty, Prohibition, Claim, Power, Liability, Immunity.

**Power**
: The ability to alter normative relations (create, modify, or extinguish norms).

**Privilege**
: A normative absence of duty not to perform an action. Also called "liberty" in Hohfeldian terms.

**Prohibition**
: A duty not to perform an action. Equivalent to a duty to refrain.

**Promise**
: A voluntary commitment from a promisor to a promisee (Promise Theory).

**Sein-Sollen** (State-Directed Ought)
: A norm specifying that a state of affairs *ought to be the case*. From German legal philosophy (Kant → Kelsen → von Wright). In RL2, Sein-Sollen norms govern world states rather than agent actions: invariants, compliance conditions, boundary set definitions, and regulatory safety requirements. Evaluated continuously or via monitoring (SHACL, SPARQL, TLA+). Violations represent illegal states rather than behavioral infractions. Contrasts with Tun-Sollen. See [von Wright 1963].

**Tun-Sollen** (Action-Directed Ought)
: A norm specifying that an agent *ought to do* (or refrain from doing) an action. From German legal philosophy (Kant → Kelsen → von Wright). In RL2, Tun-Sollen norms govern agent behavior: Promises, permissions, prohibitions, and event-triggered duties. Evaluated at request time or upon event occurrence. Violations are behavioral—an agent failed to act as required. Maps to ODRL duties and RL2's ConsumerPromise/ProviderPromise. Contrasts with Sein-Sollen. See [von Wright 1963].

## Policy Terms

**Agreement**
: A bilateral or multilateral policy with identified, consenting parties. Creates binding obligations.

**Assertion**
: A policy stating claims or facts about normative status without creating them.

**Offer**
: A policy proposed by an assigner to potential assignees, contingent on acceptance.

**Policy**
: A container of one or more RL2 normative clauses.

**Privacy Policy**
: A policy governing personal data processing and data subject rights.

**Set**
: A unilateral policy declaration without identified counterparties.

## Operational Terms

**Active**
: Obligation state indicating a duty is in force and must be fulfilled.

**Event**
: An observable occurrence that may trigger state transitions.

**Fulfilled**
: Obligation state indicating a duty has been satisfied.

**Pending**
: Obligation state indicating a duty exists but its activation condition is not yet met.

**State Transition**
: A change in system state resulting from events or actions.

**Violated**
: Obligation state indicating a duty was not fulfilled within required constraints.

## Condition Terms

**Condition**
: A constraint or requirement that must hold for a norm to be active.

**Contextual Constraint**
: A condition depending on environmental or system state.

**Left Operand**
: The property or attribute being evaluated in a condition (e.g., purpose, dateTime).

**Logical Constraint**
: A condition combining sub-conditions via logical operators (and, or, xone, not).

**Operator**
: A function used in conditions. Either LogicalOperator or ComparisonOperator.

**Right Operand**
: The value against which the left operand is compared.

**Temporal Constraint**
: A condition based on time intervals or temporal relations.

## Protocol Terms (RL2P)

**Case**
: An access case tracking the complete lifecycle from request through enforcement and expiration.

**Context Assertion**
: A contextual fact provided for policy evaluation, referencing the request it belongs to.

**Decision**
: The outcome of policy evaluation: Permit, Deny, Indeterminate, or NotApplicable.

**Duty Requirement**
: A duty imposed by policy evaluation that must be fulfilled for access to proceed.

**Evaluation Result**
: The outcome of evaluating a request against policies, including decision and active duties.

**Request**
: A request to evaluate policy for a specific action. Runtime artifact, not a policy type.

## Role Terms

**Approver**
: Functional role; agent whose approval is required for activation.

**Grantee**
: Functional role; agent receiving privileges under a policy.

**Grantor**
: Functional role; agent who issues or grants a policy.

**Promisee**
: Promise role; agent who is the beneficiary of a promise.

**Promisor**
: Promise role; agent making a voluntary commitment.

**Subject**
: Normative role; agent bearing the normative status (duty-bearer, privilege-holder).

---

# Document Cross-References

| Document | Description |
|----------|-------------|
| RL2_Core.md | Core ontology (OWL) and SHACL shapes |
| RL2_Semantics.md | Formal evaluation semantics |
| RL2_Protocol.md | Request/response protocol for interoperability |
| RL2_ODRL_Coverage.md | Mapping from ODRL 2.2/3.0 to RL2 |
| RL2_White_Paper.md | Introduction and motivation |
