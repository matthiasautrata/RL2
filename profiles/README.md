# RL2 Profiles

This directory contains domain-specific profiles that extend RL2 Core with declared left operands, actions, and domain vocabularies.

## Architectural Principle

**Runtime and contextual data access is expected to go through declared `rl2:LeftOperand` instances.**

(The core SHACL enforces this as a *recommendation* — `OperandResolutionRecommendationShape`
raises a warning, not a violation, for an operand lacking a resolution mechanism — so an
undeclared fallback is permitted but discouraged.)

This means:
- No ad-hoc properties like `ex:dataOwner` or `rl2:eventPerformer` in policies
- Profiles declare operands with explicit `rl2:resolutionPath` or `rl2:resolutionFunction`
- All access is formally grounded in the `resolve`/`deref` semantics

## Creating a Profile

A profile declares domain-specific operands that resolve via the canonical path mechanism:

```turtle
@prefix myprofile: <https://example.org/profile/myprofile#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

myprofile:departmentOperand a rl2:LeftOperand ;
    rdfs:label "Department" ;
    rdfs:comment "Resolves to the agent's department." ;
    rl2:resolutionPath "agent.department" ;
    rdfs:range xsd:string .
```

## Declaring and Requiring Profiles (O3)

A profile is a versioned `rl2:Profile` individual; a policy declares a dependency on it
with `rl2:requiresProfile`:

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix privacy: <https://rl2.example/profile/privacy#> .

privacy:Profile a rl2:Profile ;
    rl2:profileVersion "1.2.0" .        # SemVer MAJOR.MINOR.PATCH

ex:myPolicy a rl2:Set ;
    rl2:requiresProfile privacy:Profile ;   # minimum version = 1.2.0
    rl2:clause ex:someClause .
```

**Unknown-profile rule (fail-closed).** An evaluator maintains a registry of supported
`(profileIRI, version)` pairs. It **rejects a policy at load time** if any required profile
is unsupported or supported only at an incompatible version — it never evaluates a policy
against a vocabulary it does not fully understand. **Version negotiation** is SemVer with
same-major compatibility: a supported `1.4.0` satisfies a required `1.2.0`; a supported
`2.0.0` does *not* (breaking major). See RL2_Semantics.md §Profile Resolution.

## Canonical Path Roots

Resolution paths must start with one of these canonical roots:

| Root | Meaning | Example |
|------|---------|---------|
| `agent` | Requesting agent (Env.Agent) | `agent.department` |
| `asset` | Requested asset (Env.Asset) | `asset.classification` |
| `state` | System state Σ | `state.Events.*.operationalAgent` |
| `context` | External request context | `context.purpose` |
| `request` | rl2p:Request fields | `request.requestTime` |

## Available Profiles

| Profile | Description |
|---------|-------------|
| [rl2-privacy-profile.ttl](rl2-privacy-profile.ttl) | GDPR/privacy operands: dataOwner, purpose, consent, jurisdiction |

## Profile Usage in Policies

Policies reference profile-declared operands:

```turtle
@prefix ex: <https://example.org/> .
@prefix privacy: <https://rl2.example/profile/privacy#> .
@prefix rl2: <https://rl2.example/ontology#> .

privacy:dataOwnerOperand a rl2:LeftOperand ;
    rl2:resolutionPath "asset.dataOwner" .

ex:myPrivilege a rl2:Privilege ;
    rl2:subject ex:Analyst ;
    rl2:action ex:read ;
    rl2:object ex:Dataset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand privacy:dataOwnerOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .
```

## Validation

SHACL shapes in `rl2-shacl.ttl` validate:
- Resolution paths start with canonical roots
- Operands are properly typed
- Warning if operand lacks resolution mechanism

## Why Profile-Declared Operands?

This architecture ensures:

1. **No ontology drift** — RL2 Core stays stable
2. **Formal grounding** — All access maps to `resolve`/`deref` in RL2_Semantics
3. **Type safety** — Operands declare `rdfs:range`
4. **Validation** — SHACL can verify correct usage
5. **Mechanization** — Clear path to the Dafny→Go verified kernel
6. **Interoperability** — Different backends implement resolution differently

See [RL2_Semantics.md](../RL2_Semantics.md) for the formal `resolve` and `deref` specifications.
