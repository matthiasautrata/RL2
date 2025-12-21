# MiniStack Verification Spike

Comparison of Dafny vs Stainless for RL2 verified kernel.

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

## Files

```
spike/
├── README.md           # This file
├── dafny/
│   ├── MiniStack.dfy   # Dafny implementation
│   └── Makefile
└── stainless/
    ├── MiniStack.scala # Stainless implementation  
    ├── build.sbt
    └── Makefile
```

## Evaluation

After running both, score each on:

| Criterion | Dafny | Stainless |
|-----------|-------|-----------|
| Code clarity | | |
| Proof annotations | | |
| Error messages | | |
| IDE experience | | |
| Build friction | | |
| Output quality | | |

See spike-ministack.md §Evaluation Criteria for details.
