# RL2 Publication Reorganization

**Status:** Complete

**Started:** 2026-07-31

## Objective

Produce a self-contained candidate contribution for ODRL 3 review. The result presents the
RL2 0.7 language, precise evaluation semantics, ODRL 2.2 migration rules, and evidence through
use cases.
It excludes implementation drafts, protocol grammars, issue history, and superseded alternatives.

## Accepted Boundary

- `Eval(PolicyUniverse, Request, WorldSnapshot, EvaluationConfiguration)` defines observable
  policy meaning.
- The core conduct norms are Privilege, Prohibition, and Duty.
- A Duty's optional counterparty identifies its beneficiary; no separate correlative node is
  authored.
- Promise exists only as proposed Offer content. Promises materialize as Duties in an
  Agreement.
- Assignment, delegation, amendment, revocation, termination, and protections against those acts
  require a future pure normative-transformation model.
- Conditions read typed snapshot facts. Achievement Duty and action Promise status read typed
  action evidence.
- Persistent cases, state machines, protocols, enforcement, external connectors, evaluator IRs,
  and proof toolchains are outside the language specification.
- ODRL 2.2 input is deterministically translated to canonical RL2 or rejected with a diagnostic.

## Publication Contents

| Area | Contents |
|---|---|
| `spec/` | Scope, model, ontology, SHACL, formal semantics, ODRL mapping, profiles |
| `docs/` | Primer, architecture, external-data guidance, vocabulary, bibliography |
| `conformance/` | 46 use cases, semantic vectors, ODRL migration fixtures |
| `future/` | One concise list of possible follow-on work |
| `tools/` | `uv`-based validation harness |

Internal planning records are excluded from release archives.

## Progress

| Work | Status |
|---|---|
| Establish pre-reorganization baseline | Complete |
| Reduce ontology and SHACL to operative constructs | Complete |
| Remove persistent protocol and state-machine semantics | Complete |
| Consolidate pure evaluation and Offer materialization | Complete |
| Replace `future/` drafts with one research agenda | Complete |
| Rewrite retained use cases and add an owner-identity case | Complete |
| Add ODRL migration matrix and fixtures | Complete |
| Rewrite reader documentation | Complete |
| Remove redundant event-pattern condition language | Complete |
| Cross-document terminology and reference sweep | Complete |
| Full validation and clean review commit | Complete |

Seven scenarios were not retained as independent core use cases: six depended entirely on
unmodeled normative-change positions, and one was a runtime protocol example. Their durable
requirements are represented in `future/README.md`.

## Exit Gates

- ontology and SHACL parse;
- all retained use cases validate without warnings;
- every Turtle fence in normative and reader documents validates independently;
- ODRL migration fixtures parse and state one expected translation outcome;
- Markdown links resolve;
- public files contain no issue identifiers, repair history, obsolete vocabulary, or protocol
  namespace;
- `future/README.md` is the only file below `future/`;
- each retained vocabulary term has an observable role in projection, evaluation, status, or
  materialization.

## Validation Record

| Date | Result |
|---|---|
| 2026-07-31 | Baseline before publication reduction: 52 use cases passed |
| 2026-07-31 | Reduced core after event-condition removal: 45 retained use cases passed without warnings; Primer fences passed |
| 2026-07-31 | Publication candidate: 46 retained use cases passed without warnings; every Turtle fence passed independently; all local Markdown links resolved |
| 2026-08-01 | Version 0.7 publication set: 46 retained use cases passed without warnings; every Turtle fence passed independently |
