# RL2 → PNF Execution Model

## Proposal & Rationale (Draft v0.4)

**Status:** Discussion Draft
**Scope:** Execution semantics only
**Related specs:** RL2 Core, RL2 Semantics, RL2 Protocol (rl2p)

---

## 1. Motivation

RL2 deliberately separates:

* **Normative structure** (RL2 Core)
* **Formal meaning** (RL2 Semantics)
* **Runtime interaction** (RL2 Protocol / rl2p)

This gives us a policy language with both deontic rigor and operational semantics.

However, RL2 inherits a fundamental problem from its RDF foundation:

> **RDF graphs are open to arbitrary extension.**

Any node can have any predicate. Parsers must handle unknown constructs gracefully. Semantics depend on interpretation. This openness is powerful for interoperability but creates three hard problems for execution:

1. **Parsing complexity** — a conformant parser cannot reject unknown extensions
2. **Semantic ambiguity** — evaluation depends on what the evaluator understands
3. **Verification impossibility** — you cannot prove properties of a system that accepts arbitrary input

ODRL compounds this with pervasive optionality — constructs that may or may not be present, with underspecified semantics when absent.

RL2 is more disciplined than ODRL, but as long as it lives in RDF, the fundamental openness remains.

---

## 2. The PNF Solution

We propose:

> **PNF — Policy Normal Form**
> A closed, unambiguous, compiled execution format for RL2.

### 2.1 What PNF *Is*

PNF is:

* A **closed grammar** — fixed syntax, unknown constructs rejected
* A **compiled format** — produced by RL2 → PNF compilation, not hand-authored
* **Deterministic** — same input always produces same evaluation
* **Parseable** — simple grammar, no graph traversal at parse time
* **Verifiable** — amenable to mechanical proof

### 2.2 What PNF *Is Not*

PNF is **not**:

* RDF or any graph format
* Open to extension
* A human authoring language
* A place where semantic interpretation occurs

### 2.3 The Core Guarantee

> **If it parses, it evaluates. If it doesn't parse, it's rejected.**

No "unknown predicate" handling. No "ignore what you don't understand." No interpretation.

---

## 3. Relationship to RL2

```text
┌─────────────────┐
│   RL2 (RDF)     │  ← Human authoring, full expressiveness
└────────┬────────┘
         │ compile
         ▼
┌─────────────────┐
│      PNF        │  ← Machine execution, closed grammar
└────────┬────────┘
         │ evaluate
         ▼
┌─────────────────┐
│    Decision     │  ← Permit / Deny / Obligate
└─────────────────┘
```

RL2 remains the policy language. PNF is the execution format. The compiler is the semantic firewall.

### 3.1 What Compilation Does

The RL2 → PNF compiler:

* Resolves all `rl2:resolutionPath` and `rl2:resolutionFunction` references
* Normalizes logical conditions
* Rejects policies that cannot be compiled (e.g., unresolvable references)
* Bundles relevant hierarchy data (see §5)
* Produces a closed PNF artifact

### 3.2 Alignment with rl2p

The RL2 Protocol already defines `rl2p:policyGeneration` as an opaque identifier for the policy snapshot under evaluation. PNF formalizes what that snapshot *is*.

---

## 4. Grammar Requirements

PNF must have a **small, closed, efficient grammar**:

* **Context-free** — parseable without external state
* **Deterministic** — no ambiguity in parse or evaluation
* **Compact** — efficient wire representation
* **Dual-mode** — binary for runtime, text for git/audit

Precedent: **bin_prot** + **sexplib** from Jane Street — binary serialization paired with S-expression text format, both derived from the same OCaml type definitions.

---

## 5. Reasoning: What's Actually Needed

Experience building ODRL evaluators (cf. Themis project) shows that practical "reasoning" reduces to a single operation:

> **Transitive closure over declared properties.**

### 5.1 The Evidence

In production policy evaluation, the only inference patterns used are:

| Use Case | Property Path | Pattern |
|----------|---------------|---------|
| Purpose hierarchy | `skos:broader*` | Transitive |
| Org membership | `(org:memberOf\|org:subOrganizationOf)*` | Transitive |
| Action subsumption | `odrl:includedIn*` | Transitive |
| Type hierarchy | `rdfs:subClassOf*` | Transitive |

No OWL reasoning. No complex rule engines. No RDFS inference beyond what property paths provide.

### 5.2 The Algorithm

`rdfs:subClassOf`, `rdfs:subPropertyOf`, and `owl:TransitiveProperty` all reduce to the same algorithm:

```text
closure(R) = R ∪ (R ∘ closure(R))
```

This is computable, tractable, and well-understood.

### 5.3 The Data Size Question

The relevant hierarchies are small:

| Hierarchy | Typical Size |
|-----------|--------------|
| SKOS purposes | 100s – low 1000s |
| Org units | 1000s – 10000s |
| Actions | 10s – 100s |
| Type hierarchy | 100s |

These fit easily in memory. A few MB at most.

### 5.4 What This Means for PNF

The key principle is **explicit declaration of capabilities**:

1. **Closed set of transitive properties** — declared upfront, not open-ended
2. **Bundled hierarchy data** — shipped with policies, not resolved at runtime
3. **No inference engine** — just transitive closure over declared relations

Whether closures are materialized at compile time or evaluated at runtime against an embedded micro-graph store is an implementation detail. The important thing is:

> **The set of "reasoning" operations is fixed and known. Not open to arbitrary extension.**

This is richer than pure propositional flat structures, but far simpler than open-world RDF reasoning.

---

## 6. What Remains Open

The following are explicitly deferred pending real-world validation:

1. **Compilation strategy** — full materialization vs bundled hierarchies vs embedded engine
2. **Grammar specification** — concrete syntax and serialization format
3. **Hierarchy bundling format** — how to package subgraphs efficiently
4. **Versioning model** — how to handle underlying data changes
5. **Wildcard semantics** — enumeration vs bounded runtime checks

These questions require working through representative use cases:

* Break-glass with identity binding
* Separation of duty with performer tracking
* GDPR erasure with temporal constraints
* High-volume entitlement checks

The execution model should emerge from these scenarios, not be designed in advance.

---

## 7. What This Proposal Establishes

This proposal establishes:

1. **PNF as a concept** — a closed execution format for RL2
2. **Compilation as the boundary** — RL2 semantics resolved before execution
3. **Grammar-first design** — parseability and verifiability as primary constraints
4. **Explicit capabilities** — closed set of declared features, not open to extension
5. **Minimal reasoning** — transitive closure only, over declared properties

It does **not** establish:

* A concrete grammar
* A compilation strategy
* An execution architecture
* Serialization formats

---

## 8. Next Steps

1. **Select representative use cases** from existing RL2 examples
2. **Hand-compile** them to candidate PNF representations
3. **Measure** hierarchy sizes in real deployments
4. **Design grammar** based on what the use cases actually need
5. **Iterate**

---

## Appendix: Document History

* **v0.1** — Initial draft with eager materialization model
* **v0.2** — Added tiered execution model (Tier 1/Tier 2)
* **v0.3** — Simplified to core concept; execution model deferred
* **v0.4** — Added reasoning analysis from Themis experience; emphasis on explicit capability declaration
