# RL2 Frequently Asked Questions

*Common questions about RL2 design decisions and usage*

---

## Table of Contents

- [Overview](#overview)
- [ODRL Relationship](#odrl-relationship)
- [Core Concepts](#core-concepts)
- [Runtime and Execution](#runtime-and-execution)
- [Deontic Concepts](#deontic-concepts)
- [Operands and Resolution](#operands-and-resolution)
- [Practical Considerations](#practical-considerations)

---

## Overview

### What is RL2, in one sentence?

RL2 (Rights & Licenses 2) is a policy language and execution model that extends ODRL with explicit promises, events, policy lifecycles, and executable semantics, enabling both real-time authorization and continuous compliance.

### Who is RL2 intended for?

RL2 is designed for:
- Data governance architects
- Policy engineers
- Platform security teams
- Legal-tech engineers
- AI governance teams

It is not meant for end-users writing policies by hand.

### Is RL2 only for data governance?

No. While data governance is a primary use case, RL2 also models:
- Software licensing
- API usage policies
- Contractual SLAs
- AI usage policies
- Regulatory compliance obligations

Anything that involves rights, duties, events, and stateful obligations fits naturally.

---

## ODRL Relationship

### Why was RL2 created if ODRL already exists?

ODRL is excellent at expressing permissions, prohibitions, and duties, but it remains:
- Largely document-centric
- Ambiguous at runtime
- Underspecified on:
  - When policies become active
  - How obligations are triggered
  - How violations are detected
  - How policies evolve over time

RL2 was created to make ODRL-style policies:
- Operational
- Event-driven
- Lifecycle-aware
- Directly executable in policy engines

You can think of RL2 as giving ODRL a formal execution model.

### Is RL2 a replacement for ODRL?

No. RL2 is:
- A semantic superset, an extension
- Not a competing standard

Every valid ODRL policy can be:
- Interpreted in RL2
- Decomposed into RL2 atomic policies
- Executed under RL2's runtime model

RL2 exists to close the gap between ODRL documents and real operational systems.

### What is the biggest conceptual difference between ODRL and RL2?

ODRL describes what the policy *says*.
RL2 describes what actually *happens* over time.

| ODRL | RL2 |
|------|-----|
| Static policy graphs | Event-driven policy lifecycle |
| Implicit obligations | Explicit promises |
| Single evaluation moment | Continuous evaluation |
| Informal constraints | Typed, executable conditions |
| No execution semantics | Formal runtime semantics |

### Can RL2 coexist with existing ODRL tools?

Yes. Typical migration path:

1. Keep existing ODRL authoring
2. Translate ODRL → RL2 atomic policies
3. Execute via RL2 runtime
4. Feed decisions into existing enforcement points

RL2 can be introduced incrementally.

---

## Core Concepts

### What are "Promises" in RL2, and why add them?

In ODRL, a Duty informally expresses that "someone must do something."
RL2 makes this explicit using Promises:

- **ProviderPromise** — commitments by the data provider
- **ConsumerPromise** — commitments by the data consumer
- **ThirdPartyPromise** — commitments by auditors, processors, etc.

Promises are necessary because:
- They can be triggered by events
- They can succeed, fail, or remain pending
- They can generate violations
- They can span time

This turns policy obligations into trackable runtime objects.

### What does "event-driven policy" mean?

In RL2, policies do not exist in a vacuum. They are:
- Activated by events
- Satisfied by events
- Violated by events

Examples:
- A dataset is published → policy becomes active
- Access is granted → logging obligation starts
- Retention period expires → deletion obligation triggers

This allows RL2 to correctly model:
- SLAs
- Retention rules
- Reporting duties
- Breach notification requirements

### What are "policy generations"?

A policy generation is a snapshot of all active RL2 policies at a given time.

Policies evolve because:
- Assets change
- Classifications change
- Laws change
- Contracts change

RL2 does not overwrite policies — it creates new generations. This enables:
- Full auditability
- Time-travel reasoning
- Retroactive compliance analysis
- Historical policy reconstruction

### What does "atomic policy" mean in RL2?

RL2 decomposes complex policies into minimal, executable atomic units.

Each atomic policy contains exactly one:
- Permission, or
- Prohibition, or
- Promise

With fully resolved:
- Subject
- Action
- Target
- Conditions

This allows:
- Deterministic evaluation
- Parallel execution
- Clean conflict detection
- Efficient compilation to Rego, Cedar, Prolog, etc.

### Why does RL2 distinguish between events and duties?

The distinction is intentional and fundamental.

An **event** represents a factual change in the world ("something has happened"), while a **duty** or **promise** represents a normative commitment by an agent ("someone is responsible for making something happen").

Although many duties aim to bring about events, the two concepts are not equivalent:

- An event may occur without any duty being fulfilled (e.g., automation, failure, third-party action)
- A duty may exist and even be violated without the corresponding event ever occurring
- Events do not identify responsibility; duties do
- Events act as conditions and triggers for policy state transitions; duties act as obligations with lifecycle and violations

RL2 separates these layers so it can model:

- World facts independently of responsibility
- External and automated processes
- Policy activation and deactivation
- Obligation fulfillment and failure
- Full audit and forensic reasoning

Collapsing events into duties would eliminate this separation and make it impossible to distinguish *what happened* from *who was responsible*.

### Can one event satisfy multiple duties?

Yes. In RL2, a single event can satisfy multiple duties at once.

Events represent factual occurrences ("what happened"), while duties represent agent-specific responsibilities ("who was obligated"). When an event occurs, RL2 evaluates all active duties that reference that event as a satisfaction condition and may resolve several obligations simultaneously.

This is essential for:

- Correct accountability (each duty-bearer's obligation is tracked independently)
- Auditability (the event is recorded once; fulfillments are recorded per duty)
- Multi-party governance (different parties may have overlapping obligations satisfied by the same action)

### Can one duty require multiple events to occur?

Yes. In RL2, a single duty may require multiple events to occur, possibly in a specific order and within time constraints.

This allows RL2 to model multi-step obligations such as:

- Approvals followed by actions
- Publication plus notification
- Actions that must occur within a deadline

A duty is considered satisfied only when all required events have occurred according to the defined conditions.

### Can events occur in RL2 that satisfy no duties at all?

Yes. In RL2, events serve multiple roles beyond duty fulfillment:

- Activating or deactivating policies
- Enabling permissions
- Transitioning policy state

Not all such events correspond to obligation fulfillment.

**Example:** A standing policy (`rl2:Set`) states: "Engineers in Technology may use GitHub." When a new employee becomes active in the Technology department, an `employeeActivated` event occurs. This event:

- Is normatively relevant (it enables a permission)
- Is explicitly modeled in RL2
- Does not satisfy any duty

Later, when the employee requests GitHub access, the permission is evaluated. The enabling event already occurred — it was a precondition, not an obligation.

RL2 distinguishes events from duties so that policy activation conditions, obligation fulfillment, and state transitions can be modeled independently and unambiguously.

### How does RL2 handle conflicts between policies?

Conflicts are handled at three levels:

1. **Logical conflicts** — both permit and prohibit the same action
2. **Deontic conflicts** — obligation vs prohibition
3. **Temporal conflicts** — what was permitted yesterday, but not today

Because RL2 policies are atomic, typed, and time-scoped, conflicts become explicit objects, not informal interpretations.

---

## Runtime and Execution

### How is RL2 evaluated at runtime?

At runtime, RL2 usually runs in two modes:

**Decisioning mode:**
> "May subject S perform action A on asset X now?"

**Compliance mode:**
> "Are all required obligations currently satisfied?"

These are intentionally separated:
- One is transactional
- The other is continuous

### Is RL2 tied to a specific policy engine?

No. RL2 is deliberately engine-agnostic.

Atomic RL2 policies can be compiled to:
- Rego / OPA
- Cedar
- Prolog
- Datalog
- Custom interpreters

RL2's purpose is to act as a semantic and structural intermediate representation (IR) for policy systems.

### Does RL2 require a knowledge graph?

No, but it strongly benefits from one.

RL2 works best when:
- Assets are identified semantically
- Classifications are modeled with SKOS or OWL
- Policies reference concepts, not hard-coded IDs

This enables:
- Federated governance
- Cross-domain reasoning
- AI-assisted policy interpretation

### How expensive is RL2 at scale?

RL2 itself is a modeling and compilation layer. Performance depends on:
- The backend policy engine
- The number of atomic policies
- The event throughput

Because RL2 compiles to simple atomic rules, it is suitable for:
- Millions of decisions per minute
- High-frequency API authorization
- Large-scale compliance monitoring

### How formal is RL2, really?

RL2 is intentionally designed so that:
- The core model can be given formal semantics
- The execution model can be proved sound, deterministic, and conflict-detectable

RL2 is compatible with:
- Deontic logic
- Input/Output logic
- Temporal logic (for events)
- Program verification frameworks (Why3, TLA+)

### What problem does RL2 solve that most policy engines do not?

Most policy engines answer:
> "Is this request allowed right now?"

RL2 additionally answers:
- Why was it allowed?
- Under which generation?
- Which promises are now active?
- Which future obligations have been created?
- What must continue to be true?
- What would count as a violation?

RL2 turns authorization into governed behavior over time.

---

## Deontic Concepts

### What is the difference between Tun-Sollen and Sein-Sollen?

These terms from German legal philosophy (von Wright 1963) distinguish two fundamental types of normative requirements:

**Tun-Sollen** (Action-Directed Ought):
- "An agent ought to **do** X"
- Governs agent behavior: promises, permissions, prohibitions, duties
- Evaluated at request time or upon event occurrence
- Violations are behavioral — an agent failed to act as required
- RL2 examples: `Promise`, `Privilege`, `Duty`

**Sein-Sollen** (State-Directed Ought):
- "It ought to **be the case** that φ holds"
- Governs world states: invariants, compliance conditions, boundary definitions
- Evaluated continuously or via monitoring
- Violations are states — an illegal condition exists
- RL2 examples: SHACL shape violations, boundary set membership, regulatory compliance conditions

**Why this matters for RL2:**

ODRL conflates these two — a "constraint" might be an action precondition or a state invariant, with no formal distinction. This creates ambiguity: Do we check once at decision time? Monitor continuously? Block actions or flag violations?

RL2 separates them into two semantic layers:
1. **Action Calculus Layer** (Tun-Sollen) → entitlement engines, runtime authorization
2. **State Calculus Layer** (Sein-Sollen) → compliance engines, audit, monitoring

See: [RL2_References.md](RL2_References.md) — glossary entries and [von Wright 1963], [Brown 2013]

---

## Operands and Resolution

### Why are some operands in RL2 Core while others are profile-declared?

**Short answer:** Core operands query RL2's own normative state; profile operands query domain-specific external state.

**RL2 Core operands** (e.g., `rl2:obligationStateOperand`, `rl2:dutyPerformerOperand`):
- Query RL2's internal normative machinery — obligation lifecycle states, duty fulfillment records
- These concepts are defined by RL2 itself (Pending/Active/Fulfilled/Violated states, norm performers)
- Any RL2 implementation must track this information to function
- Resolution is implicit/built-in: "look up this norm's state in Σ"

**Profile-declared operands** (e.g., `emergency:eventPerformerOperand`):
- Query domain-specific external state — who physically broke a glass panel, what sensor reported
- RL2 has no inherent knowledge of domain events like "glass breaking" or "temperature readings"
- The profile must declare an explicit `rl2:resolutionPath` to tell RL2 where to find this data
- Different domains will have entirely different event types and state structures

**Example contrast:**

| Use Case | Operand | Source | Why |
|----------|---------|--------|-----|
| Check signing SoD | `rl2:dutyPerformerOperand` | RL2 Core | Queries who fulfilled an RL2 Duty — RL2's own bookkeeping |
| Break glass | `emergency:eventPerformerOperand` | Profile | Queries who performed a physical event — domain knowledge |

See: [check-signing-sod.md](usecases/check-signing-sod.md), [break-glass.md](usecases/break-glass.md)

---

## Practical Considerations

### How do I get started with RL2?

1. Work through the [Primer](RL2_Primer.md) for a tutorial introduction
2. Study the [use cases](usecases/README.md) for concrete examples
3. Reference [rl2.ttl](rl2.ttl) and [RL2_Vocabulary.md](RL2_Vocabulary.md) for the ontology specification

### Where can I find example policies?

The `usecases/` directory contains worked examples including:

- Break glass emergency access
- Check signing with dynamic separation of duty
- Data retention and deletion
- Team licensing
- Audit trail requirements

Each use case shows the policy intent, RL2 model, and evaluation semantics.

---

## Document Cross-References

| Document | Description |
|----------|-------------|
| [RL2_Primer.md](RL2_Primer.md) | Tutorial introduction |
| [rl2.ttl](rl2.ttl) | Core ontology (OWL) |
| [rl2-shacl.ttl](rl2-shacl.ttl) | SHACL validation shapes |
| [RL2_Semantics.md](RL2_Semantics.md) | Formal evaluation semantics |
| [RL2_References.md](RL2_References.md) | Bibliography and glossary |
