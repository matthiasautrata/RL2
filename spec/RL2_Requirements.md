# RL2 Requirements

**RL2 version:** 0.7 · **Status:** Draft for owner correction · **Date:** 2026-08-02

## Purpose

This document is layer (1) of the RL2 development order:

```text
requirements  ->  semantics  ->  (optional proofs)  ->  execution options
```

It states what RL2 must be able to express and decide, independently of any concrete syntax. It is
deliberately written without RDF, Turtle, or any authoring form: a requirement that cannot be
stated without naming a serialization is a syntax decision in disguise.

This document is **not part of the language definition**. No evaluator conforms to it. Its
authority is over *scope*: whether a proposed capability belongs in the RL2 core, in a profile, in
an adapter, or nowhere. `RL2_Scope.md` states the conformance boundary that results; this document
states the reasons for it.

## 1. Deployment assumptions

The requirements below are derived from one primary deployment: **data-use agreements over data
products and licensed market data inside a financial institution**, with an existing ODRL 2.2
corpus that must migrate. Every classification in §4 depends on that assumption.

These assumptions are stated so they can be corrected. If any is wrong, the classification in §4
changes and must be redone:

1. The policies that matter are *agreements between parties over data*, not access-control lists
   over application resources.
2. Obligations that survive the access decision — report, log, delete, attest, maintain — are
   load-bearing, not decoration. A model that only answers permit/deny does not meet the need.
3. Policy authors are not exclusively engineers, and policy text must remain inspectable by
   people who are accountable for it (legal, compliance, data owners).
4. Facts about the world (certification, jurisdiction, purpose, quota, approval) originate outside
   the policy engine and arrive with attribution.
5. Interoperability with other organizations is a possible future, not a current requirement. The
   current requirement is migration of an existing internal ODRL 2.2 corpus.

## 2. How the corpus is classified

The 49 use cases in `../conformance/usecases/` are classified on two independent axes. Conflating
them is the mistake this section exists to prevent.

- **Capability** — *Required* if some requirement in §3 has no other witness, or the capability is
  central to the deployment; *Covered* if the capability is already witnessed by another use case.
- **Scenario** — *Domain* if the story is representative of the deployment described in §1;
  *Borrowed* if the capability is real but dressed in an illustration from another field
  (clinical research, building safety, automotive, SaaS licensing).

A borrowed scenario is not a reason to delete a use case. A use case is a **candidate for removal
or merge only when it is both `Covered` and `Borrowed`** — the capability survives elsewhere and
the story does no work for the deployment. Deleting a `Borrowed` use case that is the sole witness
of a `Required` capability silently narrows the language.

## 3. Capability requirements

### 3.1 Who and what a norm applies to

**R-1 Attribute-defined populations.** A policy must be expressible without naming an agent or an
asset. Membership is decided per request from facts, not enumerated at authoring time.
*Witnesses:* classification-targeting, owner-access, role-hierarchy, ethics-approval.
*Demands:* a template form for norms plus a binding step at evaluation, and an identity for the
bound result that survives into the evaluation record.

**R-2 Instance coupling across norms.** Two norms must be able to refer to the same *instance*,
not merely the same type — the check Alice prepared, the licence this customer paid for.
*Witnesses:* wire-transfer-sod, check-signing-sod, pay-to-play.
*Demands:* subject and object identity shared across norms; a segregation-of-duties control is
unexpressible without it.

**R-3 Obligation subject distinct from privilege subject.** The party who owes a duty need not be
the party whose access it gates — an administrator pays, a team member gains access.
*Witnesses:* team-license, attestation-gating.

**R-4 Collections and hierarchies.** Collections of assets and of agents must be addressable as
norm targets, and subsumption over roles, types, and actions must be decidable.
*Witnesses:* asset-collection-access, role-hierarchy, display-vs-nondisplay.

### 3.2 Obligation structure

**R-5 Prerequisite gating.** Access must be expressible as conditional on an obligation having
been fulfilled.
*Witnesses:* pay-to-play, attestation-gating, audit-trail, multi-level-approval, legal-review-gate.

**R-6 Post-use commitments.** A permitted action must be able to *generate* an obligation that did
not gate it — "you may use the data, whoever you are, but you must log the access."
*Witnesses:* logging-notification, data-retention-limit, gdpr-erasure.
*Demands:* an occurrence identity per grant, so that one audit record does not discharge repeated
uses. **This is the requirement that entitlement engines structurally cannot meet** (§5), and it is
therefore the strongest single reason RL2 exists as something other than a Cedar or Rego policy
set.

**R-7 Maintenance obligations.** An obligation to keep a state true over a window, distinct from an
obligation to perform an act.
*Witnesses:* data-freshness-promise, sla-credit-clause, pass-through-terms.

**R-8 Status-triggered obligations.** An obligation owed *because* another norm was not met —
service credits, remedies, escalation.
*Witnesses:* sla-credit-clause.
*Status:* core machinery exists; the ODRL `remedy`/`consequence` mapping is profile-dependent
(`backlog.md` §2).

**R-9 Proposal and acceptance.** A proposed term must be distinguishable from a term in force, and
acceptance must be a pure, replayable transformation rather than an inferred side effect.
*Witnesses:* data-product-offer, data-stewardship, sla-credit-clause.

### 3.3 Facts, evidence, and uncertainty

**R-10 Facts are external and attributed.** No condition input may be inferred from a policy label
or a vocabulary name. Every input arrives in an immutable snapshot with attribution.
*Witnesses:* anonymization-required, geo-restriction, purpose-restriction, derived-data-restriction.

**R-11 Admissibility.** A deployment must be able to constrain which sources, ages, and signers
count for a given input, and the constraint must be part of the replayable configuration.
*Witnesses:* compliance-attestation, step-up-auth, connector-certification.

**R-12 Status from evidence, not workflow state.** An obligation's status must be derivable from
the supplied snapshot alone. The engine holds no state machine.
*Witnesses:* fulfillment-evidence, audit-trail, deletion-after-use.

**R-13 Indeterminacy is a first-class outcome.** Missing or conflicting facts must not silently
become a denial. The engine must report *why* it could not decide, and the fallback must be an
explicit, recorded configuration choice.
*Witnesses:* negated-condition, and the missing-fact path of every other use case.
*Demands:* three-valued evaluation with cause attribution; this is a hard constraint on any
execution target (§5).

### 3.4 Conditions

**R-14 Temporal conditions.** Half-open intervals with unambiguous boundaries, comparisons against
evaluation time, and obligation windows with relative endpoints.
*Witnesses:* time-window-access, trial-period, fulfillment-evidence.

**R-15 Quantitative limits.** Exact-decimal comparison of request parameters and trusted counters
against plan ceilings and remaining quota. The engine reads counters; it never updates or reserves
them.
*Witnesses:* volume-limit, usage-metering, concurrent-seats.

**R-16 Logical composition.** Conjunction, disjunction, exactly-one-of, and a negation that
preserves indeterminacy.
*Witnesses:* exclusive-use-category, negated-condition, internal-use-only.

### 3.5 Prohibition, conflict, and provenance

**R-17 Independent prohibitions with a declared conflict strategy.** A prohibition is not the
absence of a permission, and the resolution of an overlap must be a declared, recorded choice.
*Witnesses:* no-redistribution, no-ml-training, chinese-wall, quality-circuit-breaker.

**R-18 Exceptions.** A prohibition must admit a narrower carve-out — a legally required disclosure
inside a redistribution ban — without rewriting the prohibition.
*Witnesses:* no-redistribution, break-glass.

**R-19 Derived and downstream assets.** Restrictions must be expressible over data derived from a
governed asset, and over the terms a downstream recipient must already be bound by.
*Witnesses:* derived-data-restriction, pass-through-terms.
*Note:* together with R-6, this is the part of the problem that relationship-based and
attribute-based authorization systems do not address at all.

**R-20 Replayable policy selection.** Which policies were in force is the caller's decision, and
the evaluation record must make that decision reproducible.
*Witnesses:* universe-selection.

## 4. Corpus classification

Capability: **Req** = sole or near-sole witness of a §3 requirement · **Cov** = capability
witnessed elsewhere. Scenario: **Dom** = deployment-representative · **Bor** = borrowed
illustration.

| Use case | Requirements | Cap | Scen |
|---|---|---|---|
| anonymization-required | R-10 | Cov | Bor |
| asset-collection-access | R-4 | Req | Bor |
| attestation-gating | R-3, R-5 | Req | Dom |
| audit-trail | R-5, R-12 | Cov | Dom |
| break-glass | R-18 | Req | Dom |
| check-signing-sod | R-2 | Cov | Dom |
| chinese-wall | R-17 | Req | Dom |
| classification-targeting | R-1 | Req | Dom |
| compliance-attestation | R-11 | Req | Dom |
| concurrent-seats | R-15, R-17 | Cov | Dom |
| connector-certification | R-7, R-11 | Cov | Bor |
| data-freshness-promise | R-7, R-9 | Req | Dom |
| data-product-offer | R-7, R-9 | Req | Dom |
| data-retention-limit | R-6, R-14 | Req | Dom |
| data-sovereignty | R-10 (narrative) | Cov | Bor |
| data-stewardship | R-5, R-9 | Cov | Dom |
| deletion-after-use | R-6, R-12 | Cov | Bor |
| derived-data-restriction | R-19 | Req | Dom |
| display-vs-nondisplay | R-4 | Req | Dom |
| ethics-approval | R-1, R-10 | Cov | Bor |
| exclusive-use-category | R-16 | Req | Bor |
| fire-alarm | R-10 (global state) | Cov | Bor |
| fulfillment-evidence | R-12, R-14 | Req | Dom |
| gdpr-erasure | R-6 | Cov | Dom |
| geo-restriction | R-10 | Cov | Dom |
| internal-use-only | R-16, R-17 | Cov | Dom |
| legal-review-gate | R-5 | Cov | Dom |
| logging-notification | R-6 | Req | Dom |
| multi-certification | R-11, R-16 | Cov | Bor |
| multi-level-approval | R-5, R-11 | Req | Dom |
| negated-condition | R-13, R-16 | Req | Dom |
| no-ml-training | R-17 | Req | Dom |
| no-redistribution | R-17, R-18 | Req | Dom |
| owner-access | R-1, R-2 | Req | Dom |
| pass-through-terms | R-7, R-19 | Req | Dom |
| pay-to-play | R-2, R-5 | Req | Dom |
| purpose-restriction | R-10 | Req | Dom |
| quality-circuit-breaker | R-17 | Cov | Dom |
| role-hierarchy | R-1, R-4 | Req | Dom |
| schema-evolution | R-12, R-14 | Cov | Dom |
| sla-credit-clause | R-7, R-8, R-9 | Req | Dom |
| step-up-auth | R-6, R-11 | Req | Dom |
| team-license | R-3, R-5 | Req | Bor |
| time-window-access | R-14 | Req | Bor |
| trial-period | R-14 | Cov | Bor |
| universe-selection | R-20 | Req | Dom |
| usage-metering | R-15 | Req | Dom |
| volume-limit | R-15 | Req | Dom |
| wire-transfer-sod | R-2 | Req | Dom |

**Candidates for removal or merge** (`Cov` and `Bor` — capability preserved elsewhere, scenario
does no work for the deployment): anonymization-required, connector-certification,
data-sovereignty, deletion-after-use, ethics-approval, fire-alarm, multi-certification,
trial-period. Eight of 49.

These are candidates, not decisions. Each carries a secondary argument for retention — fire-alarm
is the only agent-independent global-state example, deletion-after-use is the only
evidence-*activated* obligation, multi-certification is the only conjunction over a certification
set — and the owner decides whether the corpus keeps them as pedagogy after the requirement is
witnessed elsewhere.

## 5. Consequences for execution targets

The requirements partition, and the partition is by expressive power, not by speed:

| Requirements | Target class |
|---|---|
| R-1, R-2, R-4, R-10, R-11, R-14, R-15, R-16, R-17, R-18 | An entitlement engine can decide these |
| R-3, R-5, R-6, R-7, R-8, R-9, R-12, R-19, R-20 | Require the full engine |
| R-13 | Constrains **both**: a two-valued target cannot represent it |

R-13 is the load-bearing line. An entitlement target that collapses `Unknown` into deny does not
implement a fragment of RL2 — it implements a different function that agrees with RL2 only when
every fact happens to be present. Any fast target must therefore either carry the third value or
refuse to compile a policy whose evaluation can reach it.

The obligation this creates: define the fragment explicitly, prove the fast target agrees with the
reference engine on it, and **reject** rather than silently truncate a policy outside it.

## 6. Non-requirements

RL2 does not do these, and a proposal to add one is out of scope unless this document changes:

- perform or enforce any action — it decides and reports;
- update counters, reserve quota, or coordinate concurrent admissions;
- maintain agreement lifecycle state (draft, active, suspended, terminated) or obligation workflow;
- fetch facts, verify signatures, or establish trust — those precede evaluation and arrive as
  attributed snapshot input;
- standardize approval workflows, log transport, alert delivery, or incident management;
- negotiate agreements or establish acceptance authority;
- select which policies are in force (R-20 makes that the caller's recorded decision).

## 7. Open questions

1. Are the §1 deployment assumptions right? Assumption 3 (non-engineer authors) is the one that
   most affects the authoring-surface decision.
2. Is cross-organization interoperability genuinely out of scope for now? If it returns, R-20 and
   the identity requirements tighten considerably.
3. Is R-8 (status-triggered obligations) load-bearing for the deployment, or is it retained for
   ODRL migration coverage only? Its only witness is sla-credit-clause.
4. Does the deployment need R-19 (derived assets and pass-through) at evaluation time, or is
   lineage handled upstream and delivered as a fact?
