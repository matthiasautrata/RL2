# Exclusive Use Category

## Scenario

A media service permits a licensee to use a work only when the declared use category is exactly
one of advertising, editorial, or personal use. The rule is a category-selection constraint; it
does not assert exclusivity against other licensees.

## Why it matters

`xone` is true exactly when one operand is true. It is appropriate where several mutually
exclusive classifications are tested in one condition.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix licensing: <https://example.org/profile/licensing#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Licensee a rl2:Agent .
ex:Track a rl2:Asset .
ex:use a rl2:Action .

licensing:useCategory a rl2:LeftOperand ;
    rdfs:range licensing:UseCategory ;
    rl2:resolutionPath "context.useCategory" .

licensing:Advertising a licensing:UseCategory .
licensing:Editorial a licensing:UseCategory .
licensing:Personal a licensing:UseCategory .

ex:categoryPrivilege a rl2:Privilege ;
    rl2:subject ex:Licensee ;
    rl2:action ex:use ;
    rl2:object ex:Track ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:xone ;
        rl2:operand
            [ a rl2:AtomicConstraint ; rl2:leftOperand licensing:useCategory ; rl2:constraintOperator rl2:eq ; rl2:rightOperandRef licensing:Advertising ],
            [ a rl2:AtomicConstraint ; rl2:leftOperand licensing:useCategory ; rl2:constraintOperator rl2:eq ; rl2:rightOperandRef licensing:Editorial ],
            [ a rl2:AtomicConstraint ; rl2:leftOperand licensing:useCategory ; rl2:constraintOperator rl2:eq ; rl2:rightOperandRef licensing:Personal ]
    ] .

ex:license a rl2:Set ; rl2:clause ex:categoryPrivilege .
```

## Request and snapshot

Request: `(Licensee, use, Track)`. The snapshot contains
`context.useCategory = licensing:Advertising`.

## Expected result

The decision is `Permit`. A value outside the three categories makes the rule inapplicable. A
missing or conflicting value yields an explained `Indeterminate` result.
