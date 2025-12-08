# FAQ: Why RL2 Needs Promises (And Why Duties Aren't Enough)

**Executive Summary:** In distributed systems and legal contracts, you cannot simply "impose" rules on external parties. You must model their voluntary **assent**. RL2 introduces **Promises** not as "weak" moral sentiments, but as the fundamental atomic unit of **Contracts**.

---

### Q: Why do we need "Promises"? Can't everything just be a "Duty"?
**A: No. You must distinguish between *imposition* and *voluntary binding*.**

*   **Duty (Imposition):** A rule imposed by authority (e.g., "Pay taxes," "Do not murder"). The subject is bound regardless of consent.
*   **Promise (Voluntary):** A commitment made by an agent (e.g., "I agree to these Terms of Service").

In a **Data Mesh** or **B2B** scenario, Bank A cannot "write" a Duty into Vendor B's server. Bank A has no root access or authority. Bank A can only transfer data after verifying Vendor B has **Promised** to follow the rules. Without the Promise primitive, you are simulating control you do not actually possess.

### Q: Aren't Promises "weaker" than Contracts?
**A: Legally, a Contract *is* a set of Promises.**

In contract law, a contract is defined as "a promise or set of promises for the breach of which the law gives a remedy."
*   **Technical vs. Legal Enforcement:** If technical controls (DRM) fail, your *only* recourse is the user's **Promise** (the signed Agreement).
*   **Liability:** You cannot sue a user for violating a policy they never agreed to. The **Promise** is the specific legal instrument that creates the liability. It is the trigger that turns a text file (policy) into a binding obligation.

### Q: Why not just model this as a "Duty to Agree"?
**A: That is technically possible but semantically weak and architecturally brittle.**

Trying to shoehorn a Promise into a `Duty(Action: "Agree")` fails for three critical reasons:

1.  **Action ≠ State**
    *   **The Problem:** "Agreeing" is a point-in-time *event* (an Action). A Contract is a persistent relationship.
    *   **The RL2 Solution:** A `Promise` is a **standing object in the system state (Σ)**. It persists. It has a lifecycle (`PromisePending` → `PromiseFulfilled` → `PromiseViolated`). You don't just want to know that an event happened; you want to check if a binding relationship *currently exists*.

2.  **Promise Content (Crucial)**
    *   **The Problem:** A `Duty(Action: "Agree")` is opaque. The system sees the user performed "Agree," but the structure of *what* they agreed to is lost or buried in metadata.
    *   **The RL2 Solution:** In RL2, a `Promise` explicitly contains complex content (`Action`, `Duty`, or `Condition`).
    *   *Practical Reality:* You aren't just "agreeing." You are promising to *delete data by Friday*. RL2's Promise primitive encapsulates this payload, allowing the evaluator to reason about the *content* of the commitment, not just the act of assent.

3.  **Parsimony**
    *   **The Problem:** Modeling consent as a duty requires "Meta-Policies" (Policies about agreeing to Policies). This creates brittle, recursive logic chains.
    *   **The RL2 Solution:** A Promise is a direct primitive. It removes the need for meta-layers. "I commit to X" is simpler, safer, and easier to verify than "I have a duty to perform the action of agreeing to the duty of X."
