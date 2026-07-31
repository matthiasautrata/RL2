# RL2 Conformance

This directory contains policy scenarios, future semantic vectors, and ODRL migration fixtures.

The 52 existing use cases are structurally valid against the current ontology and shapes. SHACL
validity does not yet prove their evaluation result: SCOPE-2 migration will add an explicit request,
world snapshot, expected result, and migration disposition to each normative case.

- [`usecases/`](usecases/) — existing numbered scenarios
- [`usecase-disposition.md`](usecase-disposition.md) — migration classification and required changes

Run the structural corpus with:

```bash
uv run tools/validate.py
```
