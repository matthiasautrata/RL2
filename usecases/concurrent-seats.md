# Use Case 16: Concurrent Seat Licensing

**Pattern:** Global State with capacity constraint
**Identity Check:** Session tracking
**Category:** Software Licensing, API Quotas

## Scenario

An organization has 50 concurrent licenses. Only 50 users can be active at once. The 51st login attempt is denied until someone logs out.

## Policy Intent

> "Maximum 50 concurrent sessions. Deny new sessions when at capacity."

## Key Characteristics

- **Global State** tracking (active session count)
- Capacity-based constraint
- Dynamic admission control
- Session lifecycle management

## Why RL2?

This requires **Offer-tier (shared) state**. The live-seat count is read through `global.*`
(`rl2p:GlobalLeftOperand`) as `|activeAgreements(Offer)|`; a request checks `global.activeSessions.count < 50`.

ODRL can express "license count = 50" but cannot:
- Track current consumption
- Enforce capacity at runtime
- Model session lifecycle (login/logout events)

## Scope: this is Offer-tier ("class variable") state

The concurrent-seat pool is shared across **every user who accepts the license** — it is not
private to any one seat. In RL2's scope model (RL2_Semantics.md §State Scope, Identity, and
Concurrency, S5), the license is an **Offer** (the "class"), each activated seat is an **Agreement**
(an "instance"), and the live-seat count is an **Offer-tier ("class variable")** read shared across
all instances. That is exactly what `rl2p:GlobalLeftOperand` and the `global.*` resolution root are
for. Contrast the *default* per-Agreement ("instance variable") scope — e.g. one customer's private
usage meter in [usage-metering.md](usage-metering.md) — which needs none of this machinery.

The seat count is **derived, not a mutable counter**: `seatsUsed = |activeAgreements(Offer)|`, a
read-only aggregate over the Offer's active seats resolved into the immutable `ResolvedContext`
before evaluation. So there is no shared-counter algebra; the only concurrency concern is the
check-then-act admission race, handled by the versioned-snapshot + compare-and-swap commit rule (S5,
see *Scaling Considerations*).

## Profile-Declared Operands

```turtle
@prefix licensing: <https://example.org/profile/licensing#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rl2p: <https://rl2.example/protocol#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

licensing:activeSessionCountOperand a rl2p:GlobalLeftOperand ;
    rdfs:label "Active Session Count" ;
    rdfs:comment "Live seat count = |activeAgreements(Offer)|. Offer-tier, read-only aggregate." ;
    rl2:resolutionPath "global.activeSessions.count" ;
    rdfs:range xsd:integer .

licensing:maxSeatsOperand a rl2p:GlobalLeftOperand ;
    rdfs:label "Maximum Seats" ;
    rdfs:comment "Maximum concurrent sessions the Offer grants (Offer-tier capacity constant)." ;
    rl2:resolutionPath "global.maxConcurrentSeats" ;
    rdfs:range xsd:integer .

licensing:userHasActiveSessionOperand a rl2p:GlobalLeftOperand ;
    rdfs:label "User Has Active Session" ;
    rdfs:comment "Whether the requesting agent already holds an active seat (Offer-tier read, filtered by agent)." ;
    rl2:resolutionPath "global.activeSessions.currentAgentHasSession" ;
    rdfs:range xsd:boolean .
```

## RL2 Model

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix licensing: <https://example.org/profile/licensing#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Login event template
ex:LoginEvent a rl2:Event ;
    rdfs:comment "User session start." .

ex:LogoutEvent a rl2:Event ;
    rdfs:comment "User session end." .

# Privilege: Login allowed if capacity available or user already has session
ex:loginPrivilege a rl2:Privilege ;
    rl2:subject ex:LicensedUser ;
    rl2:action ex:login ;
    rl2:object ex:Application ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:or ;
        rl2:operand [
            # User already has a session (reconnecting)
            a rl2:AtomicConstraint ;
            rl2:leftOperand licensing:userHasActiveSessionOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand true
        ] ;
        rl2:operand [
            # Capacity available
            a rl2:AtomicConstraint ;
            rl2:leftOperand licensing:activeSessionCountOperand ;
            rl2:constraintOperator rl2:lt ;
            rl2:rightOperand 50
        ]
    ] .

# Prohibition: Deny login when at capacity
ex:capacityProhibition a rl2:Prohibition ;
    rl2:priority 100 ;
    rl2:subject ex:LicensedUser ;
    rl2:prohibitedAction ex:login ;
    rl2:object ex:Application ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # User does NOT have existing session
            a rl2:AtomicConstraint ;
            rl2:leftOperand licensing:userHasActiveSessionOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand false
        ] ;
        rl2:operand [
            # At capacity
            a rl2:AtomicConstraint ;
            rl2:leftOperand licensing:activeSessionCountOperand ;
            rl2:constraintOperator rl2:gte ;
            rl2:rightOperand 50
        ]
    ] .
```

## State Management

```
Offer-tier seat pool (the "class variable"):

┌───────────────────────────────────────────────┐
│ global.activeSessions   (= activeAgreements)   │
│ ├─ count: 48   (derived: |activeAgreements|)   │
│ └─ seats: [                                    │
│      Agreement{ user: alice, active },         │
│      Agreement{ user: bob,   active },         │
│      ...                                       │
│    ]                                           │
└───────────────────────────────────────────────┘

A seat is an Agreement in the active set. Its lifecycle (the active() predicate) is the
temporal concern of WP-4; this step fixes only the set the count aggregates over:
  LoginEvent  → a seat Agreement enters the active set
  LogoutEvent → the seat Agreement leaves the active set
  Timeout     → the seat Agreement leaves the active set

The count is resolved (read-only) into the immutable ResolvedContext before evaluation;
nothing in the specified evaluator core writes a shared counter.
```

## Evaluation

| Scenario | Active Sessions | User Status | Result |
|----------|-----------------|-------------|--------|
| Normal login | 30 | No session | PERMIT, count→31 |
| Reconnect | 50 | Has session | PERMIT (same session) |
| At capacity | 50 | No session | DENY |
| After logout | 49 | No session | PERMIT, count→50 |

## Queue / Waitlist Extension

For fairer capacity management, add a queue:

```turtle
# Duty: Join waitlist when at capacity
ex:joinWaitlistDuty a rl2:Duty ;
    rl2:subject ex:LicensedUser ;
    rl2:action ex:joinWaitlist ;
    rl2:object ex:SessionQueue ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand licensing:activeSessionCountOperand ;
            rl2:constraintOperator rl2:gte ;
            rl2:rightOperand 50
        ] ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand licensing:userHasActiveSessionOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand false
        ]
    ] .
```

## Comparison

| Aspect | Manual Tracking | ODRL | RL2 |
|--------|-----------------|------|-----|
| Capacity declaration | License agreement | `odrl:count` | Constraint |
| Runtime tracking | Separate system | Not supported | State in Σ |
| Admission control | Application logic | Not supported | Condition evaluation |
| Session lifecycle | Application logic | Not supported | Event handling |

## PNF Considerations

This use case requires:
- Offer-tier shared-state access (`global.activeSessions.count`)
- Numeric comparison (propositional)
- Session tracking (state management, not policy logic)

The policy itself is propositional. The complexity is in **state management** (tracking sessions), not in policy evaluation. PNF evaluates against the current state; maintaining that state is a runtime concern.

## Scaling Considerations

Because admission reads Offer-tier shared state, it is the one policy class that needs strong
coordination (S5, *shared-strong-state vs case-local*). RL2 makes evaluation a pure function over a
**versioned snapshot** and requires the effect to **commit under compare-and-swap / a serializable
transaction**: two evaluators that both read `count = 49` cannot both admit, because only the one
committing against the still-current snapshot version succeeds; the other re-resolves and
re-evaluates. The *mechanism* (shared store, locks, reservations, retry) is a deployment concern
**outside the specified evaluator core** (I4); `evalIR`'s obligation is only that the pure decision and
effect set computed for version `v` are what get applied while `v` is current.
