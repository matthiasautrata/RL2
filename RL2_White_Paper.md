# **RL2: A Verified, Operational Rights Language**

*White Paper Draft v0.2*

---

# **The Problem: "Trust Me" vs "Show Me"**

Modern data governance relies on "Trust Me" policies. 

Organizations write policies in ODRL 2.2 or natural language, assume everyone interprets them the same way, and *trust* that downstream systems will enforce them correctly. 

But they can't *show* it.

*   **Ambiguity:** When does a "duty" actually become active? When is it violated? ODRL doesn't say.
*   **Invisibility:** Did the "approval" happen? In ODRL, approvals are just text comments or metadata, not rigorous conditions.
*   **Unverifiability:** Can you prove that your policy engine will *never* allow access without the ethics board's signature? With current standards, you cannot.

**RL2 ("Rights Language 2") is the "Show Me" language.**

It is a standalone, semantically rigorous policy language designed to replace the ambiguity of legacy standards with **mathematical precision** and **operational reality**.

---

# **What is RL2?**

RL2 is a unified rights language that combines:

1.  **Normative Logic (DPCL/Hohfeld):** Precise definitions of Privilege, Duty, Power, and Liability.
2.  **Promise Theory:** Modeling voluntary commitments between specific agents (not just generic "assignees").
3.  **Operational Semantics (ODRE):** Built-in state machines for every obligation.
4.  **Formal Verification:** A structure designed to be compiled into verifiable logic (Why3/Coq).

It is designed to be a **compilation target**. You can take an ambiguous ODRL policy, "compile" it into RL2, and get a deterministic executable contract.

---

# **"Show Me": ODRL vs. RL2**

The best way to understand RL2 is to see where ODRL fails and RL2 succeeds.

## **Scenario: The "30-Day Deletion" Rule**

**The Goal:** "The researcher must delete the data within 30 days of access."

### **The ODRL Way (Ambiguous)**

```turtle
<policy> a odrl:Set ;
    odrl:permission [
        odrl:action odrl:use ;
        odrl:duty [
            odrl:action odrl:delete ;
            odrl:constraint [
                odrl:operator odrl:lte ;
                odrl:rightOperand "P30D"
            ]
        ]
    ] .
```

**The Failure Points:**
1.  **When does the clock start?** "P30D" (30 days) relative to what? The policy creation? The first access? The approval? ODRL doesn't strictly define the temporal anchor.
2.  **What is the state?** Is the duty "pending" or "active"? ODRL has no state machine.
3.  **What happens if they don't?** ODRL has no formal concept of "violation" or "remedy."

### **The RL2 Way (Precise)**

RL2 models this as an **Operational Duty** with a clear lifecycle.

```turtle
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix ex:   <https://example.org/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# Domain-specific actions (defined by policy/profile)
ex:use a rl2:Action .
ex:delete a rl2:Action .

# Agents and Assets
ex:Researcher a rl2:Agent .
ex:Dataset a rl2:Asset .

ex:policy a rl2:Set ;
    rl2:clause ex:usePrivilege , ex:deleteDuty .

ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset .

ex:deleteDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:action ex:delete ;
    rl2:object ex:Dataset ;
    rl2:obligationState rl2:Pending ;
    # Explicit Operational Semantics
    # Deadline: must be fulfilled within 30 days of access
    rl2:condition [
        a rl2:TemporalConstraint ;
        rl2:interval [
            a rl2:EffectiveInterval ;
            # Deadline is 30 days after the access event
            rl2:end [ a rl2:DynamicOperandReference ;
                      rl2:dynamicOperand "event.AccessEvent.timestamp + P30D" ]
        ]
    ] .
```

**The Result:**
*   **Unambiguous Deadline:** The deletion deadline is explicitly bound to 30 days after the `AccessEvent`.
*   **State Machine:** The RL2 runtime knows exactly when this duty transitions from `Pending` to `Active` to `Violated`.
*   **Enforcement:** If `current_time > deadline` and `delete` has not occurred, the system automatically transitions to `State: Violated`.

---

# **"Show Me": Multi-Party Workflows**

**The Goal:** "Access requires approval from the Data Owner AND a promise of stewardship from the Researcher."

### **The ODRL Way (Silent)**

ODRL typically handles this via "out of band" processes. The policy says "permission granted," and the software engineer has to hard-code the approval check in Java or Python. The policy itself doesn't enforce it.

### **The RL2 Way (Explicit)**

RL2 treats approvals and promises as **Normative Preconditions**.

```turtle
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix ex:   <https://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Domain-specific action
ex:use a rl2:Action .

# Agents and Assets
ex:Researcher a rl2:Agent .
ex:DataOwner a rl2:Agent .
ex:Dataset a rl2:Asset .

# Custom promise content
ex:DataStewardship rdfs:label "Data Stewardship Commitment" .

ex:usePrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:use ;
    rl2:object ex:Dataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand ex:OwnerApproval ;
        rl2:operand ex:StewardshipPromiseCheck
    ] .

ex:OwnerApproval a rl2:EventConstraint ;
    rl2:expectsEvent [
        a rl2:Event ;
        rl2:approver ex:DataOwner
    ] .

ex:StewardshipPromiseCheck a rl2:Condition ;
    rl2:requires ex:StewardshipPromise .

ex:StewardshipPromise a rl2:Promise ;
    rl2:promiser ex:Researcher ;
    rl2:promisee ex:DataOwner ;
    rl2:promiseContent ex:DataStewardship ;
    rl2:promiseState rl2:PromiseFulfilled .
```

**The Result:**
The policy is self-enforcing. The `Privilege` simply *does not exist* in the evaluation state until the `Event` (approval) and the `Promise` are present in the system log. No hard-coding required.

---

# **Concrete Architecture**

How does RL2 fit into an existing system?

1.  **The Compiler:**
    *   Input: ODRL 2.2 (Legacy) or RL2 (Native).
    *   Process: Translates ODRL into strict RL2 structures, flagging ambiguities (e.g., "Warning: ODRL duty missing temporal anchor, defaulting to Policy Start").
    *   Output: A verified RL2 Graph.

2.  **The Kernel (The "Engine"):**
    *   A small, side-effect-free evaluator (written in Rust, OCaml, or Verified C).
    *   Input: RL2 Graph + Event Log + Current State.
    *   Output: `Permit` / `Deny` / `Violations` / `New Obligations`.

3.  **The Enforcer:**
    *   The API Gateway or Data Platform that asks the Kernel for decisions and executes them.

---

# **Why This Matters**

We are moving into an era of **AI Agents** and **Automated Compliance**. 

*   You cannot ask an LLM to "adhere to ODRL" because ODRL is too vague.
*   You *can* ask an Agent to "prove that this action satisfies the RL2 constraints," because RL2 is logic.

RL2 provides the missing link between high-level legal intent and low-level machine execution. It doesn't just tell you what you *can* do; it proves what happened and what must happen next.

---

# **References**

See **RL2_References.md** for complete citations and glossary.

RL2 Specifications:
* RL2_Core.md — Core ontology
* RL2_Semantics.md — Formal semantics
* RL2_Protocol.md — Evaluation protocol
* RL2_ODRL_Coverage.md — ODRL compatibility