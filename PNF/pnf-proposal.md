# RL2 → PNF Execution Model

## Proposal & Rationale (Draft v0.9)

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

**Foundational guarantee:** PNF is a **specification, not a library**. Because PNF is defined by a rigorous schema, the ecosystem is inherently open — alternative implementations in any language are valid as long as they respect the schema. We are defining the execution format, not mandating a single runtime.

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

### 2.4 The Semantic Class

PNF is a **propositional kernel with bounded transitive closure**.

Formally: PNF admits propositional logic over ground terms, plus fixed-point evaluation over a declared set of transitive relations. It explicitly excludes:

* General rule evaluation
* Open quantification
* Arbitrary joins
* Open-world inference

This places PNF in the same computational class as Cedar and Rego's safe subset — decidable, tractable, and amenable to formal verification — while preserving the hierarchy-aware semantics that RL2 requires.

> **Working hypothesis:** Propositional + bounded transitive closure is the correct semantic boundary until proven otherwise by concrete use cases.

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

### 3.2 What Gets Bundled vs. Resolved at Runtime

A critical distinction: PNF bundles **reference data**, not **operational state**.

| Category | Examples | Bundled? | Why |
|----------|----------|----------|-----|
| **Reference data** | Purpose hierarchy, org tree, action taxonomy, type definitions | Yes | Static, versionable, required for hierarchy-aware evaluation |
| **Operational state** | Asset status, event log, session counts, duty performer | No | Dynamic, changes continuously, unbounded |
| **Request context** | Agent attributes, action, target asset | No | Provided per-request by rl2p |

**The execution model:**

```text
┌─────────────────────────────────────────────────────────┐
│                    PNF Artifact                         │
├─────────────────────────────────────────────────────────┤
│  Compiled policy logic (closed grammar)                 │
│  + Bundled reference data (hierarchies, taxonomies)     │
│  + Version identifiers (policy, hierarchy, compiler)    │
└─────────────────────────────────────────────────────────┘
                          │
                          │ evaluate(Env, Σ)
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Runtime Environment                    │
├─────────────────────────────────────────────────────────┤
│  Env: agent, action, asset (from rl2p request)          │
│  Σ: event log, norm states, counters (from runtime)     │
└─────────────────────────────────────────────────────────┘
```

**Clarification:** When §3.1 says "bundles relevant hierarchy data," this means reference data for transitive closure (e.g., `skos:broader*`). It does *not* mean bundling the entire world state. Operational state (`Σ`) and request context (`Env`) are always resolved at evaluation time.

### 3.3 Alignment with rl2p

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
4. **Wildcard semantics** — enumeration vs bounded runtime checks

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
2. **Semantic class** — propositional kernel with bounded transitive closure (§2.4)
3. **Compilation as the boundary** — RL2 semantics resolved before execution
4. **Grammar-first design** — parseability and verifiability as primary constraints
5. **Explicit capabilities** — closed set of declared features, not open to extension
6. **Minimal reasoning** — transitive closure only, over declared properties
7. **Versioning requirement** — every PNF artifact MUST carry stable identifiers for policy version, hierarchy version, and compilation environment

**On tiering:** Earlier drafts distinguished a Tier-1 propositional fast path and Tier-2 full RL2 evaluation. This proposal treats that distinction as an **optimization strategy** rather than a semantic boundary: PNF defines the maximum executable subset of RL2 under closed-world assumptions, while implementations may route trivial cases through propositional specializations.

**On implementation:** See Appendix A (unified OCaml architecture) and Appendix B (runtime distribution via Wasm) for reference implementation recommendations.

It does **not** establish:

* A concrete grammar
* Serialization format details (beyond `bin_prot` direction)
* Specific compilation strategies for hierarchy bundling

---

## 8. Next Steps

1. **Select representative use cases** from existing RL2 examples
2. **Hand-compile** them to candidate PNF representations
3. **Measure** hierarchy sizes in real deployments
4. **Design grammar** based on what the use cases actually need
5. **Iterate**

---

## Appendix A: Implementation Architecture

This appendix presents the case for a unified OCaml implementation stack.

### A.1 Why Not BEAM?

A tempting architectural pattern is to use a distributed runtime like BEAM (Erlang/Elixir) for PNF execution. This approach is **architecturally misaligned** with a CPU-bound, formally verified execution core.

**Workload Mismatch:** The BEAM VM excels at I/O-bound concurrency — millions of open connections, waiting for database responses. Policy evaluation is CPU-bound: tree-walking, set intersection, transitive closure. For CPU-bound graph traversal, OCaml compiles to native code that is exceptionally efficient at recursive data structure manipulation.

**The Polyglot Tax:** If the compiler is OCaml and runtime is BEAM, you must maintain two schema definitions. Every RL2 feature update requires changes to both. With a unified stack, types are defined once in `types.ml` and shared.

**The Federation Fallacy:** In zero-trust environments, you do not open Erlang distribution ports across firewalls. Real federation means nodes pulling policy generations from a secure, immutable source (CDN/S3). Kubernetes handles restarts; OTP supervision is redundant.

**Verified Correctness:** Verified code extracts from Coq or Why3 directly to OCaml. The path from math to binary is unbroken. With BEAM, you verify the algorithm, then hand-translate — introducing human error.

### A.2 The Unified OCaml Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    Unified OCaml Stack                  │
├─────────────────────────────────────────────────────────┤
│  rl2c (Compiler)                                        │
│  ├─ Reads Turtle/RL2, validates SHACL                   │
│  ├─ Outputs PNF (bin_prot)                              │
│  └─ Shares types.ml with interpreter                    │
│                                                         │
│  rl2d (Interpreter/Daemon)                              │
│  ├─ mmap's PNF file, executes requests                  │
│  └─ Shares types.ml with compiler                       │
│                                                         │
│  libpolicy.so (Optional)                                │
│  └─ C-callable, embeds in NGINX/Envoy/Python            │
└─────────────────────────────────────────────────────────┘
```

**Properties:** Single codebase, single type system. Native compilation, CPU-optimal. Verifiable via Coq/Why3 extraction. Minimal deployment footprint. Zero serialization overhead.

---

## Appendix B: Runtime Distribution Decision

### B.1 PNF is an Open Specification

Before selecting a reference implementation, we state the architectural guarantee: **PNF is a specification, not a library.**

Because PNF is defined by a rigorous schema (available as `bin_prot` binary or S-expression text), the ecosystem is inherently open:

* A scientist can use a **Python** binding in a Jupyter notebook
* A legacy application can use a **Java** wrapper via JNI
* Alternative implementations can treat policies as data

As long as they respect the PNF schema, *how* they interpret it is an implementation detail. We are choosing the **reference runtime** for the enterprise control plane, not the only runtime allowed.

### B.2 The Contenders

| Feature | **OCaml** | **Go** | **Wasm** |
|---------|-----------|--------|----------|
| **Primary Value** | Consistency — compiler and runtime share code | Acceptance — easy hiring, SRE comfort | Portability — run inside Envoy, Browser, Edge |
| **Performance** | Native, unbeatable for recursive logic | Good, but GC pauses and weak ADTs | Near-native, sandboxed execution |
| **Risk** | "Bus factor" — OCaml hiring in 5 years? | "Logic gap" — type system too simple for RL2 | "Bleeding edge" — WASI still maturing |

### B.3 Reference Implementation: WebAssembly Distribution

**Recommendation:** Adopt WebAssembly as the primary distribution format for the reference implementation.

Wasm solves political, technical, and operational constraints simultaneously:

1. **The "Trojan Horse" Strategy (Political)**
   * Write core logic in OCaml for correctness
   * Compile to Wasm
   * Hand Ops a "standard Wasm module" — they see a standard artifact fitting Envoy filters, OPA plugins, or cloud-native gateways

2. **Hot Reloading (Operational)**
   * Go binaries require recompile/redeploy of the entire microservice
   * Wasm enables pushing new policy logic to 10,000 sidecars without restarting the host process
   * For environments that cannot accept downtime, this is decisive

3. **Future-Proofing (Technical)**
   * Wasm is converging as the universal runtime — Cloud, Edge, Browser, Device
   * The security sandbox prevents policy bugs from crashing host processes or leaking memory

**Implementation Path:**

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  OCaml Source   │────▶│   Wasm Module   │────▶│   Everywhere    │
│  (Correctness)  │     │  (Distribution) │     │   (Envoy, OPA,  │
│                 │     │                 │     │    Edge, JVM)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### B.4 Preference Ordering

**C → A → B**

| Rank | Option | Rationale |
|------|--------|-----------|
| **1st** | **Wasm** | Write OCaml, ship Wasm. Correctness *and* political cover. Hot reloading is the operational trump card. Toolchain risk is bounded — pure-compute workloads don't stress WASI maturity. |
| **2nd** | **Pure OCaml** | If Wasm tooling disappoints, take the "exotic" hit. The runtime is simple enough for a small team to own. Hire two good OCaml devs, train two more. Bus factor is manageable if you're honest about it. |
| **3rd** | **Go** | Only under executive mandate. Ship faster, hire easier, debug harder. Type system gap means bugs hide in translation — not in visible logic, but in ceremony around it. Trading correctness for comfort. |

> **The one-liner:** "Write OCaml. Ship Wasm. Defend the boundary."

### B.5 Alternatives Considered

| Alternative | Assessment |
|-------------|------------|
| **Pure OCaml binary** | Optimal performance and consistency; "exotic" for Ops but viable with operational investment |
| **Scala interpreter** | Strong type system (ADTs, pattern matching); JVM-native; viable fallback if Wasm path proves immature |
| **Go runtime** | Maximum hiring pool and SRE comfort; type system too weak for RL2 ADTs; correctness risk during translation |

**Fallback hierarchy:**
1. If OCaml→Wasm tooling (`wasm_of_ocaml`) proves insufficient: **Scala** on JVM preserves type safety with familiar runtime
2. If JVM overhead is unacceptable: **Pure OCaml binary** with dedicated operational support

### B.6 Open Questions

* OCaml-to-Wasm toolchain maturity assessment
* Debugging workflow (native OCaml in dev, Wasm in prod)
* WASI evolution for any I/O requirements beyond pure computation

---

## Appendix C: Document History

* **v0.1** — Initial draft with eager materialization model
* **v0.2** — Added tiered execution model (Tier 1/Tier 2)
* **v0.3** — Simplified to core concept; execution model deferred
* **v0.4** — Added reasoning analysis from Themis experience; emphasis on explicit capability declaration
* **v0.5** — Added unified OCaml architecture recommendation; argued against BEAM for CPU-bound policy evaluation
* **v0.6** — Added runtime architecture decision: Wasm as distribution format with OCaml implementation
* **v0.7** — Explicit semantic class (propositional + bounded transitive closure); versioning now normative; tiering reconciled as optimization strategy; tightened political language
* **v0.8** — Structural reorganization: front matter (what/why), proposal (§1-5), summary (§6-8), implementation details moved to appendices
* **v0.9** — Clarified bundled vs. runtime state: reference data (hierarchies) bundled, operational state (Σ) and request context (Env) resolved at runtime
