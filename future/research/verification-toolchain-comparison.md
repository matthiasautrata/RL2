# Verification Toolchain Comparison for Verified Stack-VM Policy Evaluator

> **SCOPE-2 status:** Historical implementation research; not part of RL2 core conformance.

> **Superseded (SCOPE-1, 2026-07-29).** RL2 dropped both the stack-VM IR this comparison
> targets and the Dafny/Go mechanization plan it recommends — the project's scope now stops at
> specification, validated by differential testing (RL2_IR.md §10), not mechanized proof. This
> document is retained for its research value (a snapshot comparison of formal-verification
> toolchains circa mid-2026) but no longer reflects RL2's direction.

**Research date:** July 25, 2026
**Use case:** Stack-based VM, ~45 opcodes, needs termination/determinism/memory-safety proofs, extraction to deployable language. Project RL2 previously planned **Dafny→Go** (superseded, see note above).

---

## 1. Dafny

- **Current version:** 4.11.0 (released Aug 25, 2025); nightly builds ongoing (nightly-2026-07-23).
  - URL: https://github.com/dafny-lang/dafny/releases
- **Actively maintained?** YES. 3.5k GitHub stars, 1.2k open issues, 190 PRs. Releases every ~2-3 months. Backed by AWS (Mikael Mayer, Rustan Leino). Active Zulip community. Blog posts through Dec 2025.
- **Extraction targets:** C#, Java, Go, JavaScript, Python, C++ (all "first-class"). **Rust backend is in active development** (PR #5433 "chore-rust-operators-followup" merged May 2024; issues labeled `lang: rust` being filed/closed as recently as Dec 2024 — #5962, Aug 2025 — #6333). Rust is NOT yet production-ready.
  - Go backend reference: §13.8.7 of Dafny reference manual (dafny.org/docs)
  - Dafny 4.11 added `--enforce-determinism` compatibility with `--standard-libraries` — directly relevant to determinism proofs.
- **Proof strengths:**
  - Hoare-style pre/postconditions, loop invariants, termination via `decreases` clauses
  - Inductive datatypes, ghost state, quantifiers, refinement types (subset types)
  - Automated via Z3; `--enforce-determinism` mode for deterministic execution proofs
  - 4.11 added `Std.Termination` and `Std.Ordinal` std libraries for termination proofs
  - 4.11 added verified parser combinators with guaranteed termination
- **Deployment story:** Mature. Dafny→Go produces a Go package + runtime `_dafny.go` helper. Generated Go is readable. Caveats: pre-module mode historically limited; some std lib features incompatible with `--enforce-determinism` (e.g. `Seq.SetToSeq` removed in 4.11 for this reason).
- **Known Go extraction issues:**
  - Issues labeled `lang: golang` exist in tracker (e.g. #6333 affects Go among others — "SinglePassCodeGenerator produces init calls inconsistent with standard library externs", Aug 2025, OPEN, has-workaround)
  - EVM-Dafny project (below) chose Java target, not Go, for their compiled output — possibly informative.
- **Verified VM precedent:** **YES — Consensys/evm-dafny** (https://github.com/Consensys/evm-dafny)
  - "An EVM interpreter in Dafny" — 140 stars, 1,086 commits, actively developed by Dave Pearce (Consensys).
  - Functional specification of the Ethereum Virtual Machine; verified free of runtime errors (div-by-zero, arithmetic under/overflow).
  - Executable: runs bytecode, compared against Geth and Ethereum Common Reference Tests.
  - Provides API for formal verification of EVM bytecode properties.
  - README explicitly says they chose Dafny over Coq/Isabelle/HOL "because it is relatively accessible to someone without significant prior experience."
  - Dafny blog post "Formal Verification of EVM Bytecode in Dafny" (Jun 24, 2025) — https://dafny.org/blog/ (post URL slug not directly resolvable; linked from blog index)
  - Related: **franck44/yul-dafny** (Yul semantics in Dafny), **DavePearce/DevmProofGen** (EVM proof generator).
- **Dafny→Rust?** In development, NOT production-ready. PR #5433 (May 2024) was a "followup" to make the Rust code generator possible. Issues with `lang: rust` label still being filed in 2024-2025. Not viable for production deployment today.

---

## 2. Lean 4

- **Current version:** v4.32.1 (released ~July 22, 2026); v4.33.0-rc1 available.
  - URL: https://github.com/leanprover/lean4/releases
- **Actively maintained?** YES. 8.6k stars, 945 issues, 586 PRs. Monthly release cadence. Backed by Lean FRO (nonprofit). Reference manual covers v4.33.0-rc1.
- **Extraction targets:** **Lean compiles to C (via LLVM)** natively — Lean is itself a functional programming language with a code generator. NO native Rust extraction. NO native Go extraction. FFI to C is supported (doc/dev/ffi.md → now in reference manual ch.21 IO / FFI).
  - The "extraction story" for Lean is: Lean IS the implementation language, compiled directly to C via the Lean compiler's own backend. You don't "extract" — you compile.
  - For Rust/Go deployment, you'd need: Lean→C, then call from Rust/Go via FFI; OR write a custom code generator (Lean's compiler is extensible in Lean itself).
- **Proof strengths:**
  - Dependent type theory (CiC), very expressive
  - Tactics, metaprogramming, automation (`grind`, `simp`, `mvcgen` — new in 4.32+)
  - Mathlib — enormous math library (but heavyweight; adds build dependency)
  - Termination proofs via well-founded recursion / `decreasing_by`
- **Deployment story:** Awkward for embedding. Lean runtime is a ref-counted GC'd runtime; calling Lean-compiled C from Go/Rust is possible but you ship the Lean runtime. Cedar-spec uses FFI (`cedar-lean-ffi`) to call Lean-compiled code from Rust.
- **Verified VM precedent:**
  - **Cedar-spec** (https://github.com/cedar-policy/cedar-spec) — AWS Cedar policy language formalized in Lean 4. 191 stars, 736 commits, actively maintained (commits 2-3 days ago as of research).
  - Includes `cedar-lean` (Lean formalization), `cedar-lean-ffi` (FFI to call from Rust), `cedar-lean-cli` (CLI wrapper), `cedar-drt` (differential regression testing).
  - This is a **policy language formalization precedent** — very close to RL2's domain. Cedar's validator and evaluator are formalized; properties like type safety, authorization soundness proven.
  - Note: Cedar's production Rust implementation is NOT extracted from Lean — the Lean spec is a definitional implementation used for testing/verification against the hand-written Rust. The `cedar-lean-ffi` enables calling the Lean reference implementation from Rust for differential testing.

---

## 3. WhyML / Why3

- **Current version:** 1.8.2 (current release per why3.org homepage)
  - URL: https://www.why3.org/
- **Actively maintained?** Moderately. Developed by Inria Toccata team. Opam/Debian/Fedora/Ubuntu packaged. Zulip chat. Less frequent releases than Dafny/Lean but still alive. Used as backend by SPARK 2014 (Ada verification), Creusot (Rust verification), Frama-C/WP.
- **Extraction targets:** OCaml (primary, "correct-by-construction"), C. No Go, no Rust, no direct extraction to deployable languages for RL2.
- **Proof strengths:**
  - Multi-prover: Z3, CVC5, Alt-Ergo, E, Vampire, etc. (why3.org/external-provers/)
  - WhyML as intermediate language for C/Java/Ada verification
  - Strong on integer arithmetic, floating-point (LMF team expertise)
  - Proof preservation across spec changes (VSTTE 2013 paper)
- **Deployment story:** WhyML→OCaml is the main path. OCaml is deployable but not Go/Rust. For RL2, you'd extract to OCaml and wrap.
- **Verified VM precedent:** No direct VM precedent found. Used for Solidity smart contract verification (Formal Verification for Solidity Contracts), Michelson (Tezos) smart contracts (WhylSon).
- **Strengths vs Dafny:** Multi-prover (not locked to Z3); more academic/less industrial; WhyML is simpler than Dafny's full language. Dafny has better tooling, IDE support, and more extraction targets.

---

## 4. F* (F-star)

- **Current version:** v2026.07.24 (weekly releases; latest 10 hours before research)
  - URL: https://github.com/FStarLang/FStar/releases
- **Actively maintained?** YES — very. 3.1k stars, 495 issues. Weekly automated releases. Active Pulse sub-language development (gebner, mtzguido, tahina-pro, dzomo, KimayaBedarkar all contributing in 2026).
- **Extraction targets:**
  - **OCaml** (via KaRaMeL — main extraction)
  - **F#** (via KaRaMeL)
  - **C** (via Low* subset + KaRaMeL — for systems code)
  - No Go, no Rust direct extraction. Rust integration via Aeneas (translates Rust to F* for verification, not extraction FROM F*).
- **Proof strengths:**
  - Dependent types + monadic effects (Dijkstra monads, indexed effects)
  - **Pulse** — new separation logic DSL for concurrent/impredicative reasoning (active 2026 development)
  - SMT automation (Z3) + interactive tactics + metaprogramming (Meta-F*)
  - Strongest in cryptographic/security verification
  - Relational verification, information flow security
- **Deployment story:** Project Everest deployed HACL*/EverCrypt to Firefox, Linux kernel, Python, mbedTLS. Low*→C is production-proven for crypto. For RL2: extract to OCaml or C, wrap in Go/Rust.
- **Verified VM precedent:** Verified abstract interpreter ("Verified Functional Programming of an Abstract Interpreter"). Vale (verified assembly). EverParse (verified parsers). No direct stack-VM precedent but strong interpreter/parser verification track record.
- **Relevant:** "Formal Security and Functional Verification of Cryptographic Protocol Implementations in Rust" — shows F*→Rust workflow exists for verification (not extraction).

---

## 5. Coq / Rocq

- **Current version:** Rocq 9.2.0 (latest stable, released Mar 27, 2026); Rocq 9.3+rc1 (July 22, 2026).
  - URL: https://github.com/rocq-prover/rocq/releases
  - Note: Coq was renamed to Rocq (9.0.0 was first Rocq release, Mar 12, 2025).
- **Actively maintained?** YES. 5.5k stars, 2.4k issues, 114 PRs. Rocq 9.0 (Mar 2025) was the major rename release. Active development by Inria and community.
- **Extraction targets:** OCaml (primary), Haskell, **C** (via `Extraction` + `notation` or via VST/CertiCoq). No Go, no Rust direct.
  - Rocq reference manual confirms: "extraction of verified programs to programming languages such as OCaml and Haskell"
  - CertiCoq (separate project) extracts Coq Gallina to C with correctness guarantees.
- **Proof strengths:**
  - CiC (Calculus of Inductive Constructions) — very expressive dependent type theory
  - Ltac2, SSReflect, MathComp — powerful tactic languages
  - Strong mathematical foundation; CompCert precedent
  - Irrelevance, universe polymorphism
- **Deployment story:** OCaml extraction is mature and used in production (e.g., CompCert extracted C compiler, CoqHammer, etc.). Performance of extracted OCaml is good but depends on extraction settings. For RL2: extract to OCaml, wrap via FFI.
- **Verified VM precedent:**
  - **CompCert** — verified C compiler (not a VM, but landmark verified interpreter/compiler).
  - Multiple verified lambda calculus interpreters, SEw/machine semantics in Coq.
  - No direct "stack VM in Coq for policy" precedent found, but the methodology is well-established.
- **Performance of extracted code:** OCaml extraction produces efficient code but requires `Set Extraction` tuning, inline directives. CompCert's extracted OCaml runs at production speed.

---

## 6. Rust + Prusti / Creusot

### Prusti
- **Current version:** Nightly releases only; last "stable" release v-2023-08-22-1715 (Aug 2023). Nightlies through Mar 2024.
  - URL: https://github.com/viperproject/prusti-dev/releases
- **Actively maintained?** Stalled. Last nightly Mar 26, 2024. No 2025-2026 releases. 1.8k stars, 269 issues. Viper-based (uses Viper verification framework + Silicon/Silicon backends).
- **Extraction:** NONE NEEDED — verifies Rust directly. This is the key advantage.
- **Proof strengths:** Viper-based separation logic; heap-dependent reasoning; assertions/assumptions via `prusti_contracts` crate. Weaker automation than Dafny (Viper is less automated than Z3+Dafny's SMT encoding).
- **Deployment:** Direct Rust — no extraction gap. But maturity is a concern (stalled development).
- **Verified VM precedent:** None known.

### Creusot
- **Current version:** v0.12.0 (Jun 12, 2026); rapid release cadence (v0.4 Mar 2025 → v0.12 Jun 2026).
  - URL: https://github.com/creusot-rs/creusot/releases
- **Actively maintained?** YES — very active. 1.8k stars, 94 issues. Maintained by Lysxia (active release manager), xldenis (original author). 9 releases in ~15 months.
- **Extraction:** NONE NEEDED — verifies Rust directly. Contracts erased at compile time.
- **Proof strengths:** Why3-based (translates Rust to WhyML, uses Z3/CVC5/Alt-Ergo via Why3). Pearlite DSL for specifications. Type invariants, ghost code. Best suited for data structures/algorithms (per their release notes).
- **Deployment:** Direct Rust — no extraction. CreuSAT (verified SAT solver) and Sprout (verified SMT solver) are notable verified projects.
- **Verified VM precedent:** No direct stack-VM precedent, but verified solver internals (CreuSAT) involve similar interpreter-like structures.
- **Maturity caveat:** v0.12 — still pre-1.0. API may change. "Less suited for systems which interact heavily with the outside world or exploit concurrency" (per release notes). For a pure policy evaluator (no I/O, no concurrency), this is a good fit functionally.

---

## 7. Isabelle/HOL

- **Current version:** Isabelle2025-2 (January 2026).
  - URL: https://isabelle.in.tum.de/
- **Actively maintained?** YES. Annual/biannual releases. Maintained at TUM (Munich) + Cambridge. Archive of Formal Proofs (AFP) continuously updated. Zulip chat, mailing lists.
- **Extraction targets:** Haskell (via code generator), SML, OCaml, Scala. **No Go, no Rust direct.**
  - Code generation is a first-class feature (NEWS mentions "various improvements to code generation" in 2025-2).
  - Refinement Framework (Lammich) supports stepwise refinement from abstract spec → executable code.
- **Proof strengths:**
  - Higher-order logic (HOL) — simpler than CiC but very effective
  - Sledgehammer (calls Z3/CVC5/E/Vampire/Zipperposition automatically)
  - **Refinement Framework** — proven methodology for verified imperative code (Lammich's work)
  - Strong automation, good libraries (AFP)
- **Deployment story:** Extract to Haskell/SML/OCaml/Scala, wrap via FFI. Lammich's Refinement Framework has produced verified imperative code (sepsets, graphs, algorithms).
- **Verified VM precedent:**
  - **SLED/IMP semantics** — textbook IMP language semantics in Isabelle (Nipkow-Klein "Concrete Semantics")
  - Verified microkernels (seL4 — Isabelle/HOL's flagship)
  - Small-step and big-step operational semantics are bread-and-butter Isabelle formalizations
  - No direct "policy VM" precedent but the IMP/stack-machine semantics methodology is extremely well-trodden.

---

## Summary Comparison Table

| Tool | Version (date) | Maintained? | Extraction to Go/Rust? | Proof Strength | VM Precedent | Fit for RL2 |
|------|----------------|-------------|------------------------|----------------|--------------|-------------|
| **Dafny** | 4.11.0 (Aug 2025) | ✅ Active | **Go ✅ mature**; Rust ⚠️ in-dev | Z3, Hoare, termination, `--enforce-determinism` | **EVM-Dafny** (Consensys, 140★) | ★★★★★ Best fit |
| **Lean 4** | 4.32.1 (Jul 2026) | ✅ Very active | C only (via LLVM); no Go/Rust | Dependent types, Mathlib, `grind` | Cedar-spec (policy language!) | ★★★☆☆ Cedar precedent strong but deployment awkward |
| **Why3** | 1.8.2 | ✅ Moderate | OCaml/C only | Multi-prover (Z3/CVC5/Alt-Ergo) | Solidity/Michelson contracts | ★★☆☆☆ Fewer targets |
| **F*** | v2026.07.24 | ✅ Very active | OCaml/F#/C (KaRaMeL); no Go/Rust | Dependent types + Pulse (sep logic) | Abstract interpreter, Vale | ★★★☆☆ Strong but heavy |
| **Rocq/Coq** | 9.2.0 (Mar 2026) | ✅ Active | OCaml/Haskell/C; no Go/Rust | CiC, Ltac2, MathComp | CompCert | ★★★☆☆ Mature but heavy |
| **Prusti** | nightly (Mar 2024) | ⚠️ Stalled | None (verifies Rust) | Viper separation logic | None | ★★☆☆☆ Stalled |
| **Creusot** | v0.12.0 (Jun 2026) | ✅ Very active | None (verifies Rust) | Why3 backend, Pearlite | CreuSAT solver | ★★★★☆ Pre-1.0 but promising |
| **Isabelle/HOL** | 2025-2 (Jan 2026) | ✅ Active | Haskell/SML/OCaml/Scala; no Go/Rust | HOL, Sledgehammer, Refinement Framework | seL4, IMP semantics | ★★★☆☆ Mature, no Go |

---

## Key Findings for RL2's Dafny→Go Decision

### ✅ Dafny→Go is the RIGHT choice for RL2. Evidence:

1. **Direct precedent exists:** Consensys/evm-dafny verified an EVM (stack machine, ~140 opcodes) in Dafny with runtime-error freedom proofs. This is architecturally identical to RL2's needs (stack VM, ~45 opcodes, determinism).
   - https://github.com/Consensys/evm-dafny

2. **Go backend is mature and production-ready:** One of Dafny's 5 first-class extraction targets. The EVM-Dafny project considered Java for compilation but Go is equally supported.

3. **Determinism support is first-class:** Dafny 4.11's `--enforce-determinism` mode (now compatible with `--standard-libraries`) directly addresses RL2's determinism requirement. The 4.11 release removed std-lib features incompatible with this mode, showing active investment.

4. **Termination proofs are built-in:** `decreases` clauses, `Std.Termination`, `Std.Ordinal` (new in 4.11) — all directly serve RL2's termination proof needs.

5. **Active maintenance:** 4.11.0 (Aug 2025), nightlies through July 2026. AWS-backed (Mikael Mayer, Rustan Leino). Not a stale academic project.

6. **Community precedent:** EVM-Dafny README explicitly chose Dafny over Coq/Isabelle/HOL for accessibility — relevant for team adoption.

### ⚠️ Risks to watch:
- **Dafny→Rust is NOT ready** (in active development, bugs being filed 2024-2025). If RL2 wants to pivot to Rust deployment, the Rust backend is not viable today.
- **Go extraction has open bugs** (e.g. #6333 SinglePassCodeGenerator init calls — has workaround).
- **Std lib churn:** 4.11 had breaking std-lib changes (Result vs Option for UTF8 functions). Pin a version.

### 🔄 Alternatives worth considering:

- **Creusot** (verify Rust directly) is the most interesting alternative IF RL2 is willing to write in Rust and accept pre-1.0 tooling. Eliminates the extraction gap entirely. v0.12.0 (Jun 2026) is very active. But: no determinism mode like Dafny's `--enforce-determinism`, and less mature.

- **Cedar-spec / Lean 4** is the closest *domain* precedent (policy language in Lean), but Lean's deployment story (C via LLVM + FFI) is more awkward than Dafny→Go. Cedar deliberately keeps Lean spec separate from Rust production code (differential testing, not extraction).

---

## URLs Referenced

- Dafny releases: https://github.com/dafny-lang/dafny/releases
- Dafny 4.11.0: https://github.com/dafny-lang/dafny/releases/tag/v4.11.0
- Dafny Rust backend PR: https://github.com/dafny-lang/dafny/pull/5433
- Dafny Rust issues: https://github.com/dafny-lang/dafny/issues?q=lang%3A%20rust
- Dafny blog (EVM post): https://dafny.org/blog/
- **Consensys/evm-dafny: https://github.com/Consensys/evm-dafny** ⭐ key precedent
- franck44/yul-dafny: https://github.com/franck44/yul-dafny
- DavePearce/DevmProofGen: https://github.com/DavePearce/DevmProofGen
- Lean 4 releases: https://github.com/leanprover/lean4/releases
- Lean language reference: https://lean-lang.org/doc/reference/latest/
- **Cedar-spec: https://github.com/cedar-policy/cedar-spec** ⭐ policy precedent
- Why3: https://www.why3.org/
- F* releases: https://github.com/FStarLang/FStar/releases
- F* homepage: https://www.fstar-lang.org/
- Rocq releases: https://github.com/rocq-prover/rocq/releases
- Rocq docs: https://rocq-prover.org/doc/V9.2.0/refman/
- Prusti releases: https://github.com/viperproject/prusti-dev/releases
- Creusot releases: https://github.com/creusot-rs/creusot/releases
- Isabelle/HOL: https://isabelle.in.tum.de/
