# RL2: Rights Language 2

RL2 is an AI-generatable, deterministically evaluable policy language for digital rights and
data governance. It extends and clarifies ODRL 2.2 so that independent evaluators can agree about
what a policy means.

RL2 focuses on four deliverables:

- a canonical RDF/OWL policy model with SHACL validation;
- formal evaluation semantics over a request and immutable world snapshot;
- an explicit ODRL 2.2 migration specification;
- structural and semantic conformance cases.

Hohfeldian normative positions and Promise Theory extend the ODRL policy model. Persistent Cases,
event sourcing, workflow orchestration, distributed coordination, enforcement, and optimized
evaluator implementations are not part of the normative language core.

## Start Here

1. [Project scope](spec/RL2_Scope.md) — normative boundary and deliverables.
2. [Information model](spec/RL2_Model.md) — pure evaluation inputs and outputs.
3. [Primer](docs/RL2_Primer.md) — concepts and examples; currently being aligned to SCOPE-2.
4. [Formal semantics](spec/RL2_Semantics.md) — authoritative evaluation meaning.
5. [Use cases](conformance/usecases/) — 52 policy scenarios.
6. [Reorganization plan](project/reorganization-plan.md) — active work and validation gates.

## Repository

| Area | Purpose |
|---|---|
| [`spec/`](spec/) | Normative language, ontology, SHACL, profiles, and ODRL mapping |
| [`conformance/`](conformance/) | Use cases, semantic vectors, and migration fixtures |
| [`docs/`](docs/) | Informative Primer, architecture, vocabulary, external-data guidance, and FAQ |
| [`future/protocol/`](future/protocol/) | Retained protocol/workflow work outside core conformance |
| [`future/reference-implementation/`](future/reference-implementation/) | IR and evaluator design ideas for follow-on implementation |
| [`future/research/`](future/research/) | Historical and exploratory design work |
| [`project/`](project/) | Active plan, issue tracker, and issue history |
| [`tools/`](tools/) | Validation tooling |

## Normative Sources

When sources conflict, use this order:

1. [`spec/rl2.ttl`](spec/rl2.ttl) and [`spec/rl2-shacl.ttl`](spec/rl2-shacl.ttl)
2. [`spec/RL2_Model.md`](spec/RL2_Model.md)
3. [`spec/RL2_Semantics.md`](spec/RL2_Semantics.md)
4. [`spec/RL2_ODRL_Mapping.md`](spec/RL2_ODRL_Mapping.md)
5. Accepted conformance vectors

Documents under `docs/` are explanatory. Documents under `future/` are not part of RL2 core
conformance.

## Quick Example

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix ex:  <https://example.org/> .

ex:agreement a rl2:Agreement ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:researchUse .

ex:researchUse a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:declaredPurpose ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "research"
    ] .
```

The policy is evaluated against an explicit request and world snapshot. RL2 specifies the result;
an implementation decides how the snapshot is collected and how a permitted action is enforced.

## Validation

The project uses `uv` for Python tooling:

```bash
uv run tools/validate.py
uv run tools/validate.py --per-fence spec/RL2_Semantics.md
```

The current structural baseline is 52/52 use cases passing SHACL validation.

## Status

Draft v0.6. SCOPE-2 reorganization is active; consult
[`project/reorganization-plan.md`](project/reorganization-plan.md) for current status.

## License

TBD
