# RL2 Tools

Python tooling for RL2. Scripts are self-contained via [PEP 723](https://peps.python.org/pep-0723/)
inline dependencies — [`uv`](https://docs.astral.sh/uv/) installs what they need
on first run; there is no virtualenv to manage.

## `validate.py` — SHACL validation harness

Validates RL2 policies against the ontology and SHACL shapes in `spec/`.

```bash
uv run tools/validate.py                       # all conformance/usecases/*.md
uv run tools/validate.py conformance/usecases/foo.md
uv run tools/validate.py path/to/policy.ttl    # a raw Turtle file
uv run tools/validate.py --shapes-only         # just parse ontology + shapes
uv run tools/validate.py conformance/usecases/foo.md -v
```

**How it handles use cases.** Markdown use cases embed policies in ```` ```turtle ````
fences. The harness extracts and concatenates those blocks, prepends a standard
prefix preamble (so illustrative snippets that omit `@prefix` still resolve), and
**merges the ontology into the data graph** — RL2 policies reference ontology
individuals (operators like `rl2:eq`, state enums like `rl2:Fulfilled`,
`rl2:currentAgent`), and SHACL `sh:class` checks need those types present as facts.
Blocks that are placeholders or use `...` elisions are skipped as documentation.

**Conformance.** A file fails only on `sh:Violation` results; `sh:Warning` /
`sh:Info` are reported (⚠) but do not break conformance, per the SHACL spec. Exit
code is non-zero if any target fails to parse or has a violation.

**Status legend:** `✓` conforms · `✓ ⚠` conforms with warnings · `✗` violation or
parse error · `–` skipped (no validatable Turtle).
