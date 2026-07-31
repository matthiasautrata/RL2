# ODRL 2.2 Migration Fixtures

Each fixture pairs an ODRL source graph with either a canonical RL2 result or an expected importer
diagnostic. Fixtures implement the disposition rows in `../../spec/RL2_ODRL_Mapping.md`.

Required fixture metadata:

```text
odrl_construct
disposition: exact | normalized | clarified | profile-dependent | rejected | metadata-only
declared_interpretation_or_profile
source_graph
expected_rl2_graph_or_ast
preservation_claim
expected_diagnostics
```

Structural translation fixtures should be executable before a reference evaluator exists.
Behavioral preservation fixtures additionally include a request, world snapshot, and expected
result shared by the ODRL interpretation and translated RL2 policy.
