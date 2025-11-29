# RL2 Discussion Topics

*Future design decisions and enhancements under consideration*

---

## 1. Alignment Modules for Standard Vocabularies

**Status**: Under discussion

**Background**: RL2 follows a "standalone" design principle, not importing external ontologies to ensure semantic stability. However, Semantic Web best practices encourage reuse and alignment with established vocabularies.

**Proposal**: Create a separate `RL2_Alignment.md` (or alignment module) containing `owl:equivalentClass` and `rdfs:subClassOf` axioms mapping RL2 concepts to standard vocabularies:

| RL2 Concept | Standard Vocabulary |
|-------------|---------------------|
| `rl2:Case`, `rl2:Event` | PROV-O (`prov:Activity`, `prov:Entity`) |
| `rl2:EffectiveInterval` | OWL-Time (`time:Interval`) |
| `rl2:Agent` | FOAF (`foaf:Agent`) |

**Benefits**:
- Enables interoperability with PROV-based provenance systems
- Allows temporal reasoning using OWL-Time tooling
- Preserves standalone core while enabling alignment when needed

**Considerations**:
- Alignment module would be optional—core RL2 remains self-contained
- Requires careful axiom design to avoid unintended inferences
- Version management for alignment as external standards evolve

---

## 2. Common Profile for Baseline Actions and Operands

**Status**: Under discussion

**Background**: RL2 Core intentionally does not define specific actions or left operands, delegating these to domain profiles. This ensures flexibility but may hinder interoperability between implementations using different profile vocabularies.

**Proposal**: Create an `RL2_CommonProfile.md` defining a baseline vocabulary of commonly-used actions and operands:

**Actions** (candidates):
- `rl2common:use` - General exercise or consumption
- `rl2common:read` - Read/view access
- `rl2common:modify` - Alter or update
- `rl2common:transfer` - Transfer to third party
- `rl2common:delete` - Remove or destroy

**Left Operands** (candidates):
- `rl2common:dateTime` - Current timestamp
- `rl2common:purpose` - Declared purpose of access
- `rl2common:recipient` - Intended recipient
- `rl2common:spatial` - Geographic location

**Benefits**:
- Ensures baseline interoperability between implementations
- Provides concrete examples for implementers
- Enables ODRL policy compilation without profile-specific mappings

**Considerations**:
- Must be clearly marked as "common" not "required"
- Domain profiles may still define more specific vocabularies
- Namespace: `rl2common:` vs including in `rl2:` core

---

## 3. Explicit Rejection/Disapproval Semantics

**Status**: Under discussion

**Background**: RL2 currently models approval as the *presence* of an approval event in `Σ.Events`. An `EventConstraint` evaluates to true when a matching event exists. However, there is no explicit mechanism for modeling *disapproval* or *rejection*.

**The Problem**: Active disapproval is semantically distinct from the absence of approval:
- Absence: Request pending, awaiting response, may timeout
- Rejection: Explicit "no", request should be denied, logged for audit

Real workflows need to distinguish these cases. A DataOwner clicking "Reject" should:
- Immediately terminate the request (Case → Denied)
- Be recorded for compliance/audit
- Potentially block re-submission for some period
- Possibly trigger escalation or appeal workflows

**Possible Approaches**:

1. **Separate Rejection Event Type**
   ```turtle
   ex:rejectionEvent a rl2:RejectionEvent ;
       rl2:rejector ex:DataOwner ;
       rl2:reason "Data too sensitive for stated purpose" .
   ```

2. **Event with Outcome Property**
   ```turtle
   ex:approvalEvent a rl2:ApprovalEvent ;
       rl2:approver ex:DataOwner ;
       rl2:outcome rl2:Rejected .  # or rl2:Approved
   ```

3. **Rejection as Prohibition Activation**
   - Disapproval creates/activates a Prohibition that blocks access
   - More compositional but potentially complex

**Considerations**:
- Should rejection be a subclass of Event or a distinct concept?
- How does rejection interact with the Case lifecycle?
- Should EventConstraint have explicit "approved" vs "not rejected" semantics?
- Appeal/override workflows after rejection

---

## 4. Policy Inheritance (odrl:inheritFrom)

**Status**: Under discussion — skeptical

**Background**: ODRL 2.2 supports `odrl:inheritFrom`, allowing a child policy to inherit rules from a parent policy. RL2 currently has no equivalent construct.

**The Problem with Inheritance**:

Policy inheritance introduces complexity that may not be justified:

1. **Flattening required**: To evaluate an inherited policy, you must first "flatten" it by resolving all inheritance chains into atomic rules. If you have to decompose back to atomic policies for processing, why have inheritance?

2. **Override semantics are ambiguous**: What happens when a child policy has a rule that conflicts with an inherited rule? ODRL doesn't fully specify this.

3. **Complexity vs. value**: If you want multiple policies to apply to the same asset, simply create multiple policies. The evaluation semantics for multiple applicable policies are clearer than inheritance semantics.

4. **Auditability**: Inherited policies are harder to audit — you must trace the inheritance chain to understand what rules actually apply.

**Current Position**: RL2 does not support policy inheritance. If multiple policies should apply to an asset, create them as separate policies and let the evaluator handle policy composition via the existing conflict resolution mechanisms.

**If inheritance is needed**: A future version could add `rl2:refines` with explicit semantics:
- Child clauses override parent clauses with same subject/action/object
- Non-conflicting clauses are merged
- Flattening algorithm specified formally

**Recommendation**: Avoid inheritance. Use explicit policy composition instead.

---

## 5. Conditional/Branching Obligations

**Status**: Known limitation

**Background**: RL2's duty lifecycle is linear: Pending → Active → Fulfilled/Violated. However, real-world workflows often require *branching* based on intermediate outcomes.

**Motivating Example** (real enterprise use case):

> "The obligation is to ask the review committee if they choose to review. Option (1): they decline and we're done. Option (2): they accept, and then the obligation *grows* to obtain full approval."

This requires:
1. An initial duty with multiple possible outcomes (not just fulfilled/violated)
2. Outcome-dependent continuation (duty transforms or spawns new duties)
3. Conditional obligation graphs

**What RL2 Currently Supports**:
- Duties with activation conditions ✓
- Duties with deadlines (timeout → violation) ✓
- EventConstraints (approval present/absent) ✓
- Power/Liability for creating new norms ✓

**What RL2 Lacks**:
- **Event outcomes with branching**: Events are binary (present/absent), not multi-valued
- **Duty spawning**: One duty completing cannot directly activate a *different* duty
- **Obligation automata**: No native support for stateful obligation graphs

**Possible Approaches**:

1. **Duty with Outcomes**
   ```turtle
   ex:askCommitteeDuty a rl2:Duty ;
       rl2:subject ex:Requester ;
       rl2:action ex:askForReview ;
       rl2:possibleOutcome ex:DeclinedOutcome, ex:AcceptedOutcome .

   ex:DeclinedOutcome a rl2:DutyOutcome ;
       rl2:condition [ ... committee declines ... ] ;
       rl2:resultState rl2:Fulfilled .  # Done, no further obligation

   ex:AcceptedOutcome a rl2:DutyOutcome ;
       rl2:condition [ ... committee accepts ... ] ;
       rl2:activates ex:obtainFullApprovalDuty .  # Spawns new duty
   ```

2. **Obligation Automata** (more general)
   - Model obligations as finite state machines
   - States can have multiple outgoing transitions based on events
   - More expressive but significantly more complex

3. **Encode in Powers**
   - Committee acceptance = exercise of Power that creates new Duty
   - Conceptually clean but verbose for common patterns

**Considerations**:
- How complex should the duty lifecycle become?
- Is this a core feature or a profile extension?
- Interaction with existing ObligationState semantics

**Recommendation**: This is a genuine gap. For now, workaround via Power/Liability modeling. Future RL2 versions should consider native support for branching obligations.

---

## 6. Expressive Completeness: Characterizing RL2's Policy Space

**Status**: Foundational question

**Background**: Given the universe of all possible policies, RL2 expresses a certain subset. How do we characterize that subset precisely? This is analogous to asking: "Does your number system cover rationals, reals, or complex numbers?"

**Why This Matters**:
- Avoid "oops, can't handle that" surprises in production
- Enable principled comparison with other policy languages
- Guide future extensions

**Formal Characterization via Logic Correspondence**:

| Policy Language | Approximate Logic | Temporal Model |
|-----------------|-------------------|----------------|
| Simple ACLs | Propositional logic | None |
| XACML | First-order logic over attributes | Point-in-time |
| ODRL 2.2 | Deontic logic (O, P, F) | Implicit |
| **RL2 (current)** | **LTL + Deontic + Finite State** | **Linear time** |
| Full temporal deontic | CTL* + Deontic | Branching time |

**Key Distinctions**:

1. **Linear vs Branching Time**
   - **LTL** (Linear Temporal Logic): One future path; "eventually X", "always Y"
   - **CTL** (Computation Tree Logic): Branching futures; "there exists a path where X", "on all paths Y"
   - RL2 is currently LTL-like: duties have one timeline (activate → fulfill/violate)
   - Branching obligations (Topic #5) would require CTL-like semantics

2. **What RL2 Can Express**:
   - Single-deadline obligations ✓
   - Conditional activation ("duty activates when X") ✓
   - Sequential dependencies ("A before B") ✓
   - Compensatory obligations via Power/Liability ✓
   - Contrary-to-duty ("if violated, then Y") — partial

3. **What RL2 Cannot Express** (currently):
   - Repeating/periodic obligations ("every month")
   - Branching obligations based on intermediate outcomes
   - Quorum approvals ("any 2 of 5 committee members")
   - Nested temporal modalities ("eventually always X")

**Proposed Characterization**:

```
RL2 ≈ LTL_F + Deontic(P, O, F) + Finite Obligation Automata
```

Where:
- `LTL_F` = Linear Temporal Logic with finite traces
- `Deontic(P, O, F)` = Permission, Obligation, Prohibition modalities
- `Finite Obligation Automata` = Duty lifecycle state machine (Pending → Active → Fulfilled/Violated)

**To extend RL2** for branching obligations, we would need:

```
RL2* ≈ CTL + Deontic(P, O, F) + Obligation Automata with Branching
```

**Practical Approach**:

Rather than proving RL2 covers "all policies" (impossible), we should:
1. Collect real use cases from enterprise deployments
2. Attempt to model each in RL2
3. Document gaps as they emerge (like Topic #5)
4. Either extend RL2 or explicitly document exclusions

**Open Questions**:
- Should RL2 aim for CTL-level expressiveness, or is LTL sufficient for 90% of use cases?
- What is the complexity cost of branching? (CTL model checking is PSPACE vs LTL's PSPACE-complete, but CTL* is 2EXPTIME)
- Can we define a "RL2 Lite" (strictly LTL) and "RL2 Full" (CTL) distinction?

---

## Notes

These topics represent potential future enhancements. They do not affect the validity of the current RL2 specification. Feedback and proposals are welcome.
