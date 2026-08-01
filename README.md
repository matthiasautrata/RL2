# RL2: A Deterministic Policy Language for ODRL

RL2 is a candidate language contribution for the evolution of ODRL. It retains the familiar
policy concepts of permissions, prohibitions, duties, actions, assets, parties, constraints,
profiles, offers, and agreements while defining the inputs and algorithms needed for independent
evaluators to agree.

The proposal addresses three recurring sources of ambiguity:

- the meaning of a policy for a particular request;
- the facts and evidence that constitute the state of the world; and
- the fulfillment, violation, and applicability of duties.

RL2 defines a pure evaluation contract:

```text
Eval(PolicyUniverse, Request, WorldSnapshot, EvaluationConfiguration)
    -> EvaluationResult
```

It adds canonical RDF projection, SHACL validation, typed three-valued condition evaluation,
declarative Duty status, explained conflict resolution, and a pure Offer-to-Agreement
transformation.

Canonical shapes and total semantics make RL2 suitable for generation by software and language
models. Generated RDF is not trusted as prose: it must pass canonical projection, validation, and
the same evaluator semantics as any other policy.

## Documents

1. [Scope](spec/RL2_Scope.md)
2. [Information model](spec/RL2_Model.md)
3. [Formal semantics](spec/RL2_Semantics.md)
4. [ODRL 2.2 migration](spec/RL2_ODRL_Mapping.md)
5. [Ontology](spec/rl2.ttl) and [SHACL shapes](spec/rl2-shacl.ttl)
6. [Primer](docs/RL2_Primer.md)
7. [Use cases and conformance material](conformance/)

## Repository Structure

| Area | Contents |
|---|---|
| [`spec/`](spec/) | Normative model, semantics, ontology, shapes, profiles, and migration rules |
| [`conformance/`](conformance/) | Use cases, semantic vectors, and ODRL translation fixtures |
| [`docs/`](docs/) | Informative Primer, architecture, external-data guidance, vocabulary, and bibliography |
| [`future/`](future/) | One non-normative list of possible follow-on work |
| [`tools/`](tools/) | Validation tooling |

## Example

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix ex:  <https://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:policy a rl2:Set ;
    rl2:clause ex:researchUse .

ex:researchUse a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:purpose ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "research"
    ] .

ex:Researcher a rl2:Agent .
ex:use a rl2:Action .
ex:Dataset a rl2:Asset .
ex:purpose a rl2:LeftOperand ;
    rdfs:range xsd:string ;
    rl2:resolutionPath "context.purpose" .
```

For a matching request and a snapshot containing `context.purpose = "research"`, the Privilege
contributes a permit. A missing purpose produces an attributed `Indeterminate` result rather than
being silently interpreted as false.

## Validation

The tools use [`uv`](https://docs.astral.sh/uv/):

```bash
uv run tools/validate.py
uv run tools/validate.py --per-fence spec/RL2_Semantics.md
```

## Status

RL2 is a draft proposal for technical and academic review. The example namespace is provisional.
