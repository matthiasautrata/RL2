# RL2: Rights Language 2

A next-generation policy language unifying normative, descriptive, and operational semantics for digital rights and data governance.

## Overview

RL2 provides a semantic superset of ODRL 2.2 with:

- **Formal semantics** suitable for verified runtime kernels
- **Hohfeldian normative relations** (privilege, duty, claim, power, liability, immunity)
- **Promise Theory** integration for voluntary cooperation
- **Operational semantics** with explicit state transitions
- **RDF/OWL native** with SHACL validation

## Getting Started

**New to RL2?** Start here:

1. **[RL2_Primer.md](RL2_Primer.md)** — Learn RL2 concepts, see ODRL mapping (Appendix A)
2. **[RL2_Vocabulary.md](RL2_Vocabulary.md)** — Look up any class or property
3. **[usecases/](usecases/)** — Practical policy patterns

## Documentation

### Conceptual

| Document | Description |
|----------|-------------|
| [RL2_Primer.md](RL2_Primer.md) | Technical introduction with ODRL mapping |
| [RL2_Vocabulary.md](RL2_Vocabulary.md) | Complete class and property reference |
| [usecases/](usecases/) | 17 use cases demonstrating RL2 patterns |

### Technical Specifications

| Document | Description |
|----------|-------------|
| [RL2_Semantics.md](RL2_Semantics.md) | Formal denotational and operational semantics |
| [RL2_Architecture.md](RL2_Architecture.md) | Evaluation pipeline and design rationale |
| [RL2_Protocol.md](RL2_Protocol.md) | Runtime evaluation protocol |

### Normative Files

| File | Description |
|------|-------------|
| [rl2.ttl](rl2.ttl) | OWL ontology |
| [rl2-shacl.ttl](rl2-shacl.ttl) | SHACL validation shapes |
| [rl2p.ttl](rl2p.ttl) | Protocol ontology |
| [rl2p-shacl.ttl](rl2p-shacl.ttl) | Protocol SHACL shapes |

### Project Tracking

| Document | Description |
|----------|-------------|
| [backlog.md](backlog.md) | Open decisions and work items |
| [RL2_References.md](RL2_References.md) | Citations and glossary |

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

RL2 defines policy semantics and evaluation protocols. For deployments requiring full audit trails and non-repudiation:

- **Temporal/versioned data stores** — Reconstruct state at any historical point
- **Immutable audit logs** — Append-only storage for decisions and evidence
- **Cryptographic attestation** — Signed decisions for non-repudiation
- **Policy version control** — Bind cases to specific policy generations

## Status

Draft v0.6 — Under active development.

## License

TBD
