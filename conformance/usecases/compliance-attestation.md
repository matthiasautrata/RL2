# Compliance Attestation Evidence

## Scenario

A controller permits a processor to handle a dataset only when an admissible attestation states
that the processor is certified for the required programme. The attestation is represented as an
attributed snapshot fact, not as a policy type or a self-authenticating statement.

## Why it matters

The applicable profile defines the fact path, value vocabulary, accepted issuers, and validity
requirements. RL2 then resolves that fact deterministically at the evaluation time.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix compliance: <https://example.org/profile/compliance#> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Processor a rl2:Agent .
ex:SensitiveDataset a rl2:Asset .
ex:process a rl2:Action .

compliance:processorStatus a rl2:LeftOperand ;
    rl2:valueType compliance:Status ;
    rl2:resolutionPath "agent.complianceStatus" .
compliance:Certified a compliance:Status .

ex:certifiedProcessing a rl2:Privilege ;
    rl2:subject ex:Processor ;
    rl2:action ex:process ;
    rl2:object ex:SensitiveDataset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand compliance:processorStatus ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef compliance:Certified
    ] .

ex:terms a rl2:Set ; rl2:clause ex:certifiedProcessing .
```

## Request and snapshot

Request: `(Processor, process, SensitiveDataset)`. The snapshot contains an attributed fact with key
`(AgentScope(ex:Processor), "agent.complianceStatus")`, value `compliance:Certified`, an
unexpired validity interval, and attribution accepted by the compliance profile.

## Expected result

The decision is `Permit`. Missing, inadmissible, or conflicting attestation data produces the
corresponding explained `Indeterminate` result.
