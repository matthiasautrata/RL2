# RL2 SCOPE-2 Reorganization Plan

**Status:** Active

**Started:** 2026-07-31

**Control document:** Update this file whenever a phase, disposition, dependency, or validation result changes.

## Objective

Reorganize RL2 around its primary deliverable: an AI-generatable, deterministically evaluable
policy language that extends and clarifies ODRL 2.2. The normative core specifies observable
policy meaning. Protocol workflows, persistence, distributed coordination, and reference
implementation design are separated from the language specification.

The reorganization must preserve the business intent of the 52 existing use cases, provide an
explicit migration path from ODRL 2.2, and leave enough formal precision to build and verify an
independent evaluator as a follow-on project.

## Governing Decisions

1. `Eval(PolicyUniverse, Request, WorldSnapshot, EvaluationConfiguration)` is the center of the
   normative semantics.
2. RL2 specifies observable results, including applicability, decisions, duties, determining
   norms, and attributed errors. It does not prescribe storage, scheduling, retry, commit, or
   distributed-consistency mechanisms.
3. Duty fulfillment and violation remain normative language semantics, expressed declaratively
   over supplied evidence rather than through a required persistent workflow engine.
4. Canonical RDF-to-AST projection remains normative because generatability and deterministic
   evaluation depend on it. Optimized IRs and evaluator architectures are informative.
5. ODRL 2.2 migration is a first-class normative workstream. Ambiguous ODRL input is translated
   under a declared interpretation or rejected with a diagnostic; it is not silently guessed.
6. Existing protocol and implementation material is retained under `future/` unless a
   section-level review identifies a core definition that must first be extracted.

The full boundary is stated in `spec/RL2_Scope.md`.
The heading-level extraction ledger is `project/section-disposition.md`.

## Baseline

| Item | Baseline |
|---|---|
| C3-1 integration | Commit `0707a54` |
| Working tree before reorganization | Clean |
| Use-case files | 52 |
| SHACL validation | PASS 52 · WARN 0 · FAIL 0 (`uv run tools/validate.py`, 2026-07-31) |
| Use-case status metadata | Inconsistent: 35 files say `DRAFT`; index says 52 complete |
| Use cases containing `rl2p:` | 5, excluding the index |

## Target Repository Structure

```text
RL2/
├── README.md
├── AGENTS.md
├── spec/                         # normative language and migration
├── conformance/                  # use cases, vectors, migration fixtures
├── docs/                         # informative reader-facing material
├── future/
│   ├── protocol/                 # optional/future workflow protocol
│   ├── reference-implementation/ # IR and evaluator design ideas
│   └── research/                 # historical and exploratory work
├── project/                      # active plan and issue history
└── tools/
```

## Artifact Disposition

| Existing artifact | Destination | Planned treatment |
|---|---|---|
| `rl2.ttl`, `rl2-shacl.ttl` | `spec/` | Normative; paths change, IRIs do not |
| `RL2_Semantics.md` | `spec/` | Retain and reduce to pure language semantics |
| `RL2_ODRL_Comparison.md` | `spec/RL2_ODRL_Mapping.md` | Expand into normative migration matrix |
| `profiles/` | `spec/profiles/` | Normative/profile-defined extensions |
| `usecases/` | `conformance/usecases/` | Preserve all scenarios; classify and migrate incrementally |
| `RL2_Primer.md` | `docs/` | Rewrite after the core stabilizes |
| `RL2_Architecture.md` | `docs/` | Shorten to conceptual boundaries and data flow |
| `RL2_Vocabulary.md` | `docs/` | Derived reference; establish generation check |
| `RL2_ExternalData.md` | `docs/` | Extract snapshot contract to core; retain guidance here |
| `RL2_References.md`, `FAQ/` | `docs/` | Informative |
| `RL2_Protocol.md`, `rl2p.ttl`, `rl2p-shacl.ttl` | `future/protocol/` | Future companion; not core conformance |
| `RL2_IR.md` | `future/reference-implementation/` | Extract canonical AST/projection first; retain remaining design |
| `research/` | `future/research/` | Historical/exploratory |
| `issues.md`, `issues-log.md` | `project/` | Reclassify by core, migration, conformance, or future work |

## Work Phases

| Phase | Work | Status | Exit gate |
|---|---|---|---|
| 0 | Establish clean C3-1 and validation baseline | Complete | Clean commit and 52/52 validation |
| 1 | Adopt SCOPE-2 and create this control plan | Complete | Scope boundary is explicit and linked from project guidance |
| 2 | Complete section-level disposition audit | Complete | Every mixed-document section has a destination before removal |
| 3 | Create directories and move clear whole-file artifacts | Complete | Paths, links, imports, and tools work; 52/52 validation retained |
| 4 | Reduce normative core to pure evaluation semantics | In progress | No core requirement depends on persistence or distributed workflow |
| 5 | Migrate and classify all 52 use cases | In progress | Every original case has a successor or explicit future disposition |
| 6 | Build the ODRL 2.2 disposition and translation matrix | Pending | Every ODRL term/shape has mapping, assumption, diagnostic, and fixture |
| 7 | Rewrite informative documentation | In progress | README/Primer/Architecture explain one consistent model without duplication |
| 8 | Complete semantic conformance suite and final consistency pass | Pending | Independent evaluation is unambiguous for all normative vectors |

## Immediate Next Work

1. Complete S2-C4: pure Offer→Agreement transformation without runtime effects or persistence.
2. Migrate the first use-case wave (static Privilege/Prohibition/condition cases) into exact
   request + snapshot + expected-result vectors.
3. Extract canonical projection rules from the preserved SCOPE-1 Architecture/IR into the core
   before simplifying those future documents further.

Do not resume the former C3-2 state-machine repair directly; its core question is now S2-C2 and
depends on S2-C1's evidence model.

## Use-Case Migration Rules

Each use case keeps its business scenario and number. Its current encoding may be rewritten.
Every case receives:

- scope: `core`, `extension`, or `future-workflow`;
- migration status: `current`, `rewrite-required`, or `migrated`;
- constructs covered;
- policy graph, request, and world snapshot;
- expected decision, normative envelope, duties, and errors;
- ODRL source or migration note where applicable.

Use cases are migrated in five waves:

1. Static privileges, prohibitions, matching, and condition algebra.
2. Duties and fulfillment evidence.
3. Events, temporal conditions, and external snapshot data.
4. Hohfeldian positions, Promises, and Offer-to-Agreement transformation.
5. Workflow/protocol scenarios, retained under future work where their intent is not a language
   evaluation question.

No use case is deleted merely because its current encoding depends on material leaving the core.

## ODRL Migration Deliverable

Each ODRL 2.2 construct receives one disposition:

- `exact`;
- `normalized`;
- `clarified`;
- `profile-dependent`;
- `rejected`;
- `metadata-only`.

For each construct, the mapping records the source shape, canonical RL2 result, added semantic
assumption, preservation guarantee, rejection diagnostic, and positive/negative fixture.

## Validation Gates

Run with `uv`:

```bash
uv run tools/validate.py
uv run tools/validate.py --core-only --shapes-only
uv run tools/validate.py --per-fence spec/RL2_Semantics.md
```

Before closing the reorganization:

- all structural use-case validation passes;
- all normative Turtle fences pass per-fence validation;
- all internal links and moved-file references resolve;
- ontology and generated vocabulary agree;
- ODRL migration fixtures pass;
- semantic vectors have one hand-derivable expected result;
- future documents carry an explicit non-core status notice.

## Change Log

| Date | Change |
|---|---|
| 2026-07-31 | Created plan; recorded SCOPE-2 decisions and 52/52 validation baseline |
| 2026-07-31 | Added `spec/RL2_Scope.md`; updated repository guidance to make SCOPE-2 authoritative |
| 2026-07-31 | Created `spec/`, `docs/`, `conformance/`, `future/`, and `project/`; moved clearly classified artifacts |
| 2026-07-31 | Completed section-level disposition audit for Semantics, Architecture, IR, External Data, and Protocol |
| 2026-07-31 | Classified all 52 use cases: 13 core, 26 core rewrites, 11 extensions, 2 future workflow |
| 2026-07-31 | Updated validation paths and reader navigation; local Markdown-link check found no broken links |
| 2026-07-31 | Revalidated reorganized corpus: PASS 52 · WARN 0 · FAIL 0 |
| 2026-07-31 | Approved S2-C2 vocabulary: applicability `condition`, Achievement `postCondition`, Maintenance `invariant`, optional half-open `dutyWindow`; no authored duty mode or state machine |
| 2026-07-31 | Completed S2-C2 model, semantics, protected vocabulary/SHACL, migration note, and component vectors; full validation PASS 52 · WARN 0 · FAIL 0 |
| 2026-07-31 | Added normative `RL2_Model.md` scaffold for Request, WorldSnapshot, configuration, result, and conformance |
| 2026-07-31 | Reframed the ODRL comparison as the in-progress normative migration specification |
| 2026-07-31 | Replaced the 865-line active Architecture with a concise SCOPE-2 overview; preserved the former design under `future/reference-implementation/` |
| 2026-07-31 | Replaced live-resolution External Data guidance with the WorldSnapshot boundary; preserved SourceBinding/ContextManifest design under future work |
| 2026-07-31 | Added a core-only validation mode and verified `spec/rl2.ttl` + `spec/rl2-shacl.ttl` independently of future protocol artifacts |
| 2026-07-31 | Updated active issue ordering for SCOPE-2 and mapped every former C3 stopper to core or future work |
| 2026-07-31 | Final post-move corpus validation retained PASS 52 · WARN 0 · FAIL 0; local Markdown-link check retained zero broken links |
| 2026-07-31 | Closed S2-C1: adopted the immutable WorldSnapshot and pure Eval contract, added nine snapshot-resolution component vectors, aligned protected ontology/SHACL annotations without changing axioms or constraints, and advanced active work to S2-C2 |
| 2026-07-31 | Audited S2-C2 against the semantics and 52 cases; bounded the pure status algebra and identified the remaining language decision: norm applicability must be distinct from Duty/Promise performance conditions and occurrence windows |
| 2026-07-31 | Closed S2-C3: added canonical `prerequisiteDuty` attachment with ODRL-compatible shared fulfillment, made unsatisfied prerequisites local to their Privilege, excluded independent Duties from access resolution, and moved concurrent/post-use packaging plus `PermitWithObligations` outside core; core parse 510/593 triples, corpus PASS 52 · WARN 0 · FAIL 0, touched-document fences PASS 3 · WARN 0 · FAIL 0 |
