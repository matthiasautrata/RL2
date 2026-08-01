# RL2 Conformance Material

This directory provides reviewable examples of RL2 0.7 policy meaning and ODRL 2.2 migration.

- [`usecases/`](usecases/) contains compact policy scenarios with canonical RL2 graphs.
- [`vectors/`](vectors/) states normative evaluator observations and diagnostics.
- [`migration/`](migration/) contains ODRL source fixtures and their expected translation outcome.

Validate the use-case corpus with:

```bash
uv run tools/validate.py
```

For documents containing independent examples, validate each Turtle fence separately:

```bash
uv run tools/validate.py --per-fence spec/RL2_Semantics.md
```
