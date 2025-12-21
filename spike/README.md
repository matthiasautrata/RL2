# MiniStack Verification Spike

Comparison of Dafny vs Stainless vs Why3/WhyML for RL2 verified kernel.

## Specification

See [spike-ministack.md](../spike-ministack.md) for the full specification.

## Quick Start

### Dafny

```bash
cd dafny

# Verify (proofs + assertions)
make verify

# Run tests (Dafny interpreter)
make run

# Extract to Go
make extract
```

Prerequisites:
- Dafny 4.x (`brew install dafny` or https://github.com/dafny-lang/dafny/releases)

### Stainless

```bash
cd stainless

# Verify
make verify
```

Prerequisites:
- Stainless (https://epfl-lara.github.io/stainless/installation.html)
- Scala 3.3.x

### Why3/WhyML

```bash
cd whyml

# Verify with default prover
make verify

# Verify with multiple provers
make verify-all

# Interactive proof IDE
make ide

# Extract to OCaml
make extract
```

Prerequisites:
- Why3 (`opam install why3`)
- Provers: Alt-Ergo, Z3, CVC4 (`why3 config detect`)

## Files

```
spike/
├── README.md              # This file
├── dafny/
│   ├── MiniStack.dfy      # Dafny implementation
│   └── Makefile
├── stainless/
│   ├── MiniStack.scala    # Stainless implementation  
│   ├── build.sbt
│   └── Makefile
└── whyml/
    ├── MiniStack.mlw      # Why3/WhyML implementation
    └── Makefile
```

## Line Counts

| Implementation | Lines | Notes |
|----------------|-------|-------|
| Dafny | ~180 | C-family syntax |
| Stainless | ~200 | Scala/functional |
| WhyML | ~220 | ML syntax, separate test module |

## Evaluation

After running all three, score each on:

| Criterion | Dafny | Stainless | WhyML |
|-----------|-------|-----------|-------|
| Code clarity | | | |
| Proof annotations | | | |
| Error messages | | | |
| IDE experience | | | |
| Build friction | | | |
| Output quality | | | |
| Prover flexibility | | | |

See spike-ministack.md §Evaluation Criteria for details.

## Key Differences

| Aspect | Dafny | Stainless | WhyML |
|--------|-------|-----------|-------|
| Syntax | C-family | Scala | ML/OCaml |
| Prover | Z3 only | Z3 + Inox | Alt-Ergo, Z3, CVC4, ... |
| Extraction | Go, Java, C#, JS, Python | None (native JVM) | OCaml |
| IDE | VS Code plugin | IntelliJ/Metals | Why3 IDE (GTK) |
| Style | Imperative | Functional | Functional |
| Maturity | 10+ years | ~5 years | 15+ years |

## Decision Matrix

| If you need... | Choose |
|----------------|--------|
| Go deployment | Dafny |
| JVM native, no extraction | Stainless |
| OCaml deployment, multiple provers | WhyML |
| Strongest proof ecosystem | WhyML |
| Easiest onboarding | Dafny |
| Scala team | Stainless |
