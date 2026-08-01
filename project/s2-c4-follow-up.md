# S2-C4 Follow-up Work Package

**Status:** Completed 2026-07-31

**Normative decision:** Closed 2026-07-31

**Authority:** `spec/RL2_Semantics.md` §Pure Offer Acceptance, then `spec/RL2_Model.md` §8

This package is deliberately mechanical. Do not redesign materialization while completing it.
Questions that would change a rule below return to the senior reviewer before editing normative
files.

## Fixed decisions

1. Offers contribute no atoms to `Out` before acceptance.
2. `materialize(Offer,Acceptance)` is pure and returns `Materialized` or `Rejected`; it is not an
   event, effect, state transition, or persistence operation.
3. Acceptance supplies Agreement parties, all output identifiers, optional missing-object
   bindings, and optional Promise Duty windows. No implicit fresh-name operation is allowed.
4. `promisedAction` becomes an Achievement Duty.
5. `promisedState` becomes a Maintenance Duty.
6. Each generated Duty has `subject=promisor`, `counterparty=promisee`, and one Claim with the
   reverse roles and Claim→Duty `correlativeTo`.
7. General `promisedDuty` materialization is rejected as unsupported; do not manufacture an
   action, goal-state Duty, guarantee, indemnity, remedy, or protocol Requirement.
8. Every policy-local Norm gets Agreement-local identity, including attached Duties that are not
   top-level clauses. Preserve attachment structure and rewrite all internal
   prerequisite/correlative/Power/Liability/Immunity links and `targetNorm`; external Norm
   references remain external.
9. Only core `promiseStateOperand` has a core Promise→Duty query rewrite. Reject
   `promisorOperand` and undeclared profile Promise operands during core materialization.
10. No Promise survives in an Agreement.
11. Policy-local Norms are top-level Norm clauses plus attached prerequisite Duties; other
    Norm-valued properties are references and do not establish ownership.
12. An Offer condition is the proposed Agreement applicability guard, not offer validity or
    acceptance authorization.
13. Promise-valued targets are same-Offer sibling references; cross-policy Promise queries are
    invalid.
14. Object binding is uniform for action and state Promises, and every accepted Duty window is a
    valid finite interval.

## Delegated tasks

### A. Active-document terminology sweep

Search `spec/`, `docs/`, `conformance/`, and the root README for:

```text
Acceptance event
fresh IRI
CrystallizePromise
materialization effect
PromiseEntry
no obligations until accepted
RL2_ODRL_Comparison.md
RL2_IR.md
Σ.ObligationState
```

For active documents, replace claims that conflict with the fixed decisions. Historical files
under `future/` may retain the old design but must carry or preserve a clear non-core notice. Do
not rewrite future implementation material as if it were normative.

### B. Offer use-case sweep

Run `rg -l "a rl2:Offer" conformance/usecases`. For every result:

- state whether the Offer is merely inspected or is materialized;
- remove any implication that its Privileges or Duties affect `Out` before acceptance;
- if materialized, show explicit Acceptance identities and party values;
- ensure promised-state content maps to `rl2:invariant`, never to an invented action;
- ensure every generated Claim/Duty pair has mirrored parties;
- replace reused source clause identifiers with Agreement-local identifiers;
- rewrite a core Promise-status target to Duty status in both `targetNorm` and `leftOperand`;
- classify unsupported profile operands or `promisedDuty` acceptance as a rejection, not an
  implementation choice.

Prioritize `legal-review-gate.md`, then recheck `data-stewardship.md`,
`data-freshness-promise.md`, and `sla-credit-clause.md`. The last file is the canonical completed
example and should not be structurally redesigned.

### C. Conformance completion

Use `conformance/vectors/offer-materialization.md` as the expected-results ledger. Add examples
only when they test a distinct listed rule. At minimum verify:

- action and state Promise success;
- optional object binding;
- Offer non-operation;
- party mismatch;
- identifier collision;
- missing object;
- unsupported `promisedDuty`;
- unsupported Promise operand;
- internal-reference rewrite; and
- all-or-nothing error behavior.

Do not claim these vectors are executable until a transformation harness exists. They are
hand-derivable normative vectors in the current spec phase.

### D. Validation and handoff

Use `uv`:

```bash
uv run tools/validate.py --core-only --shapes-only
uv run tools/validate.py
uv run tools/validate.py --per-fence docs/RL2_Primer.md docs/RL2_Vocabulary.md \
  conformance/usecases/sla-credit-clause.md
```

Also run `git diff --check` and verify that active-document links resolve. Record exact counts in
`project/reorganization-plan.md`. The final senior disposition added one SHACL locality constraint
and made the existing Promise-object cardinality uniform; it introduced no new vocabulary IRI.

## Completion gate

This follow-up is complete when every active Offer example either stays non-operative or shows a
valid explicit Acceptance; no active document describes runtime crystallization; all touched
Turtle fences pass independently; and no delegated edit changes a fixed decision above.

## Completion record

- Core parse: `510` ontology triples, `595` shape triples.
- Active corpus: `PASS 51 · WARN 0 · FAIL 0 · SKIP 1`; relocated future case: `PASS 1`.
- Touched active-document fences: `PASS 7 · WARN 0 · FAIL 0 · SKIP 6`.
- Negative cross-policy Promise fixture: rejected by `PromiseTargetLocalityShape`.
- Object-less action Promise Offer: accepted structurally for later Acceptance binding.
- Local Markdown links: zero broken.
