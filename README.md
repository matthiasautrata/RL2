# RL2: Rights Language 2

A next-generation policy language unifying normative, descriptive, and operational semantics for digital rights and data governance.

## Overview

RL2 provides a semantic superset of ODRL 2.2 capabilities (see [ODRL Coverage](RL2_ODRL_Coverage.md)) with:

- **Formal semantics** suitable for verified runtime kernels
- **Hohfeldian normative relations** (privilege, duty, claim, power, liability, immunity)
- **Promise Theory** integration for voluntary cooperation
- **Operational semantics** with explicit state transitions
- **RDF/OWL native** with SHACL validation

## Getting Started

**New to RL2?** Start here:

1. **[RL2_Primer.md](RL2_Primer.md)** — Learn RL2 concepts step by step
2. **[RL2_Vocabulary.md](RL2_Vocabulary.md)** — Look up any class or property

## Documentation

### Conceptual Documentation

| Document | Description |
|----------|-------------|
| [RL2_Primer.md](RL2_Primer.md) | Progressive tutorial for learning RL2 |
| [RL2_Vocabulary.md](RL2_Vocabulary.md) | Complete class and property reference |

### Technical Specifications

| Document | Description |
|----------|-------------|
| [RL2_Semantics.md](RL2_Semantics.md) | Formal denotational and operational semantics |
| [RL2_Protocol.md](RL2_Protocol.md) | Runtime evaluation protocol |
| [RL2_ODRL_Coverage.md](RL2_ODRL_Coverage.md) | ODRL 2.2 feature coverage |

### Normative Files

| File | Description |
|------|-------------|
| [rl2.ttl](rl2.ttl) | OWL ontology (Turtle) |
| [rl2-shacl.ttl](rl2-shacl.ttl) | SHACL validation shapes |

### Reference

| Document | Description |
|----------|-------------|
| [RL2_References.md](RL2_References.md) | Citations and glossary |
| [RL2_ResearchPlan.md](RL2_ResearchPlan.md) | Mechanization roadmap |

## Quick Example

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix ex:  <https://example.org/> .

# A simple data use agreement
ex:agreement a rl2:Agreement ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:usePrivilege, ex:deletionDuty .

# Researcher may use the dataset
ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset .

# Researcher must delete by deadline
ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:delete ;
    rl2:object ex:Dataset ;
    rl2:obligationState rl2:Pending .
```

See [RL2_Primer.md](RL2_Primer.md) for a complete walkthrough.

## High-Trust Deployment Prerequisites

RL2 defines policy semantics and evaluation protocols. For deployments requiring full audit trails and non-repudiation, the following infrastructure is assumed:

- **Temporal/versioned data stores** — Reconstruct collection membership and attribute values at any historical point. Required for auditing decisions that reference dynamic data (e.g., "High Risk Client" lists).
- **Immutable audit logs** — Append-only storage for EvaluationResults, ContextAssertions, and state transitions.
- **Cryptographic attestation** — Signed decisions and evidence chains for non-repudiation.
- **Policy version control** — Use `rl2:policyGeneration` to bind cases to specific policy versions.

The spec provides hooks (`evaluationTime`, `policyGeneration`, `ContextAssertion`) — implementations wire these to appropriate infrastructure.

## Status

Draft v0.4 — Under active development.

## License

TBD
