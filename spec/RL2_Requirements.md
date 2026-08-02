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
*Witnesses:* asset-collection-access (asset collections), role-hierarchy (type subsumption).
*Evidence gap (§7):* agent collections and action subsumption are both unevidenced.
display-vs-nondisplay is **not** evidence for action subsumption — it declares two sibling actions
precisely to avoid a hierarchy, and is closer to an argument that the deployment does not need one.

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

### 3.6 Composition

**R-21 Composable policy layers.** Policies written by different authorities at different times —
enterprise standard, line-of-business rule, product terms, individual agreement — must compose
without any of them being rewritten, and the composition must resolve deterministically where the
layers disagree.
*Witnesses:* **none.** Owner-asserted 2026-08-02 ("for scalability, we want composable policies");
no use case in the corpus exercises layered composition or an override between layers.
*Existing mechanism:* universe union (`RL2_Semantics.md` §Policy Composition Semantics), plus
`rl2:priority` and the configured conflict strategy for disagreement. Composition is set union of
clauses; there is no policy inheritance, no parameterized or reusable clause library, and no
reference from one policy into another beyond sharing a Duty by IRI within one universe.
*Open (§8):* this requirement is the missing justification for `rl2:priority` (§7), and it is the
one place where the authoring-scalability question and the evaluation-scalability question must be
separated before anything is designed.

## 4. Corpus classification

The same classification is presented twice. §4.1 is keyed by use case and answers *what is this
document for?*; §4.2 is keyed by requirement and answers *is this requirement actually witnessed?*
§4.2 is derived from §4.1 and must be regenerated with it — the two are one table, not two claims.

### 4.1 By use case

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
| derived-data-restriction | R-10, R-19 | Req | Dom |
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

### 4.2 By requirement

Evidence marked `*` is a removal candidate from §4.1. **N** counts all evidence; **After cut**
counts evidence surviving if every candidate is removed.

| Requirement | Evidence | N | After cut |
|---|---|---|---|
| **R-1** Attribute-defined populations | classification-targeting, ethics-approval*, owner-access, role-hierarchy | 4 | 3 |
| **R-2** Instance coupling across norms | check-signing-sod, owner-access, pay-to-play, wire-transfer-sod | 4 | 4 |
| **R-3** Obligation subject distinct from privilege subject | attestation-gating, team-license | 2 | 2 |
| **R-4** Collections and hierarchies | asset-collection-access, display-vs-nondisplay, role-hierarchy | 3 | 3 |
| **R-5** Prerequisite gating | attestation-gating, audit-trail, data-stewardship, legal-review-gate, multi-level-approval, pay-to-play, team-license | 7 | 7 |
| **R-6** Post-use commitments | data-retention-limit, deletion-after-use*, gdpr-erasure, logging-notification, step-up-auth | 5 | 4 |
| **R-7** Maintenance obligations | connector-certification*, data-freshness-promise, data-product-offer, pass-through-terms, sla-credit-clause | 5 | 4 |
| **R-8** Status-triggered obligations | sla-credit-clause | 1 | **1** |
| **R-9** Proposal and acceptance | data-freshness-promise, data-product-offer, data-stewardship, sla-credit-clause | 4 | 4 |
| **R-10** Facts are external and attributed | anonymization-required*, data-sovereignty*, derived-data-restriction, ethics-approval*, fire-alarm*, geo-restriction, purpose-restriction | 7 | 3 |
| **R-11** Admissibility | compliance-attestation, connector-certification*, multi-certification*, multi-level-approval, step-up-auth | 5 | 3 |
| **R-12** Status from evidence, not workflow state | audit-trail, deletion-after-use*, fulfillment-evidence, schema-evolution | 4 | 3 |
| **R-13** Indeterminacy is a first-class outcome | negated-condition | 1 | **1** |
| **R-14** Temporal conditions | data-retention-limit, fulfillment-evidence, schema-evolution, time-window-access, trial-period* | 5 | 4 |
| **R-15** Quantitative limits | concurrent-seats, usage-metering, volume-limit | 3 | 3 |
| **R-16** Logical composition | exclusive-use-category, internal-use-only, multi-certification*, negated-condition | 4 | 3 |
| **R-17** Independent prohibitions with a declared conflict strategy | chinese-wall, concurrent-seats, internal-use-only, no-ml-training, no-redistribution, quality-circuit-breaker | 6 | 6 |
| **R-18** Exceptions | break-glass, no-redistribution | 2 | 2 |
| **R-19** Derived and downstream assets | derived-data-restriction, pass-through-terms | 2 | 2 |
| **R-20** Replayable policy selection | universe-selection | 1 | **1** |
| **R-21** Composable policy layers | *none* | 0 | **0** |

Four readings of this table matter.

**The proposed cut is safe.** No requirement loses all of its evidence, and none is left relying
solely on borrowed scenarios. R-10 is the most exposed — seven witnesses down to three — but the
three that remain are all deployment-representative. That is the strongest argument available for
the §4.1 candidate set, and it is the reason the removal question is decidable at all.

**Three requirements rest on a single use case: R-8, R-13, R-20.** A single-witness requirement is
fragile in both directions — remove the use case and the requirement is unevidenced; change the
requirement and there is only one place to check the consequence.

**R-13 is the serious one.** §5 identifies indeterminacy as the constraint that decides whether a
fast execution target is possible at all, and its only evidence is `negated-condition`, which
tests that *one operator* preserves indeterminacy. There is no use case exercising indeterminacy
across obligation status, admissibility filtering, prerequisite gating, or conflict resolution —
the places where a two-valued target would silently disagree with the reference engine. The
requirement with the largest architectural consequence has the thinnest evidence in the corpus.

**Evidence density is not importance.** R-5 has seven witnesses; R-19 has two, and R-19 is one of
the two requirements §5 says an entitlement engine cannot address at all. Density reflects how
easy a capability is to illustrate, not how much of the deployment depends on it. Do not use this
column to prioritize work. R-6 makes the same point from the other side: three witnesses for the
requirement §3.2 calls the strongest single reason RL2 is not a Cedar policy set.

**R-21 has no evidence at all, and that is the correct state to record.** It is asserted by the
owner and unwitnessed by the corpus. A requirement in this condition is not yet a property of the
language; it is a decision to design one. It appears here so that the gap is visible rather than
implicit — and so that §7's unbacked composition machinery is not mistaken for its fulfilment.

### 4.3 Consequence for the vector suite

This pivot is the acceptance criterion for `backlog.md` §1: **every requirement needs at least one
executable vector, and the single-witness requirements need theirs first.** A requirement with no
executable vector is an assertion about the language, not a property of it.

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

## 7. Vocabulary audit

§3 and §4 ask whether every requirement has evidence. This section asks the reverse: whether every
shipped vocabulary term has a requirement. It was produced by counting each `rl2:` term's
occurrences across the 49 use cases and reading the semantics for every term at or near zero.

Terms never written directly because they are type-hierarchy positions — `Norm`, `Policy`,
`Clause`, `Condition`, `Operator`, `ComparisonOperator`, `LogicalOperator`, `ObligationState` —
are excluded. Their absence from instance data is correct.

| Term | Corpus uses | Requirement | Finding |
|---|---|---|---|
| `rl2:priority` | 0 | none | A complete second conflict-resolution mechanism |
| `rl2:includedIn` | 0 | R-4 (over-claimed) | Action subsumption, with precomputed closures, never exercised |
| `rl2:AgentCollection`, `rl2:agentMember` | 0 | R-4 (over-claimed) | Agent collections indexed in universe identity, never used |
| `rl2:postCondition` | 0 | none | Added by review (F-05); no requirement, no use case |
| `rl2:Profile`, `ProfileOperator`, `requiresProfile`, `profileVersion`, `leftParamType`, `rightParamType` | 0 | none | Whole extensibility subsystem unbacked |
| `rl2:RuntimeReference` | 0 (`rightOperandRef` 12) | R-10 | Feature used; the class is never asserted on instances |
| `rl2:consequentDuty` | 3 | R-6 | Backed, but thin for its architectural weight |

**`rl2:priority` is the significant finding.** It is fully specified — integer, higher overrides
lower, default 0, resolved *before* the configured strategy applies (`RL2_Semantics.md`
§Conflict Resolution) — SHACL-validated, and present in the compile check table. It is used by no
use case, and `RL2_Semantics.md` explicitly records that it, together with strategy, is what
breaks monotonicity. RL2 therefore carries two conflict mechanisms, one of which has no stated
reason to exist.

The resolution is R-21. Per-norm priority is exactly the mechanism a layered composition needs to
let an enterprise standard override a product term. **If R-21 is adopted, `priority` is its
implementation and needs a use case; if R-21 is declined, `priority` is the largest single
simplification available to the semantics.** The two questions cannot be decided separately.

**Two requirement over-claims.** R-4 asserts agent collections and action subsumption; neither is
witnessed, and `display-vs-nondisplay` is evidence against needing the latter. Either write the
use cases or narrow R-4 — but note that the compilation contract already pays for both, in
materialized closures and in universe identity, so narrowing R-4 means deleting machinery.

**Extensibility has no requirement.** Profiles carry a normative denotation obligation, a
conformance quarantine, and their own compile phase, and §3 never says why RL2 needs them. This is
the largest unbacked subsystem in the specification. It is very likely genuinely required — a
market-data or privacy vocabulary has to live somewhere — but the requirement must be written
before the subsystem can be judged.

### 7.1 Capabilities the vocabulary does not have

Two gaps found by asking what the audited terms *cannot* express.

**Threshold and quorum are inexpressible.** `admitsEvidence` tests
`issuer ∈ evidenceSigners(d)` — one evidence item, one issuer, membership in an allowed set. That
states *which* signers are acceptable, never *how many* are required. "Two of these three
signatories" has no vocabulary, no semantics, and no use case. Conjunction over named facts
(multi-level-approval, multi-certification) is not a substitute: it expresses N-of-N over
individually named approvals, not M-of-N over an interchangeable set. For a financial deployment
this is a conventional control, and its absence should be a deliberate decision rather than an
oversight.

**Third-party roles are partly implicit.** The vocabulary carries `subject`, `object`,
`counterparty` (23 uses), `grantor` and `grantee` (30 each), so a duty owed *to* a party other
than the grantor is expressible. No requirement states this: R-3 covers a duty whose subject
differs from the gated privilege's subject, but not to whom the duty is owed. Any further party —
a risk team, a supervisor, an approver — exists only as a fact in the snapshot, which may be the
right answer, but it is currently an accident rather than a decision.

## 8. Open questions

1. Are the §1 deployment assumptions right? Assumption 3 (non-engineer authors) is the one that
   most affects the authoring-surface decision.
2. Is cross-organization interoperability genuinely out of scope for now? If it returns, R-20 and
   the identity requirements tighten considerably.
3. Is R-8 (status-triggered obligations) load-bearing for the deployment, or is it retained for
   ODRL migration coverage only? Its only witness is sla-credit-clause.
4. Does the deployment need R-19 (derived assets and pass-through) at evaluation time, or is
   lineage handled upstream and delivered as a fact?

Forced by §7, in the order they have to be answered:

5. **Is R-21 adopted?** If yes, `rl2:priority` is its mechanism and needs use cases, and the
   composition story (union only, no inheritance, no clause library) has to be judged against it.
   If no, `priority` and one of the two conflict mechanisms should be removed.
6. **Is extensibility a requirement?** Write it, or retire the profile subsystem. It cannot stay
   unbacked at its current size.
7. **Does R-4 keep agent collections and action subsumption?** Either write the use cases or narrow
   R-4 and delete the corresponding closure and universe-identity machinery.
8. **Is M-of-N approval required?** If yes it needs vocabulary and semantics, since `admitsEvidence`
   cannot express it. If no, record the decision so the gap is deliberate.
9. **Is `rl2:postCondition` kept?** It arrived from review, not from a requirement.
10. Should R-3 be extended to say to whom a duty is owed, making `counterparty` deliberate rather
    than incidental?
