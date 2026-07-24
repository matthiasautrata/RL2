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

This requires **Global State**. RL2's state (`Σ`) can track `active_sessions`. A request checks `count(Σ.sessions) < 50`.

ODRL can express "license count = 50" but cannot:
- Track current consumption
- Enforce capacity at runtime
- Model session lifecycle (login/logout events)

## Profile-Declared Operands

```turtle
@prefix licensing: <https://example.org/profile/licensing#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

licensing:activeSessionCountOperand a rl2:LeftOperand ;
    rdfs:label "Active Session Count" ;
    rdfs:comment "Current number of active sessions for this license." ;
    rl2:resolutionPath "state.License.activeSessions.count" ;
    rdfs:range xsd:integer .

licensing:maxSeatsOperand a rl2:LeftOperand ;
    rdfs:label "Maximum Seats" ;
    rdfs:comment "Maximum concurrent sessions allowed." ;
    rl2:resolutionPath "state.License.maxConcurrentSeats" ;
    rdfs:range xsd:integer .

licensing:userHasActiveSessionOperand a rl2:LeftOperand ;
    rdfs:label "User Has Active Session" ;
    rdfs:comment "Whether the current user already has an active session." ;
    rl2:resolutionPath "state.License.activeSessions.includes(agent)" ;
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
Session State in Σ:

┌─────────────────────────────────────┐
│ state.License.activeSessions        │
│ ├─ count: 48                        │
│ └─ sessions: [                      │
│      { user: alice, started: ... }, │
│      { user: bob, started: ... },   │
│      ...                            │
│    ]                                │
└─────────────────────────────────────┘

Events update state:
  LoginEvent  → count++, add session
  LogoutEvent → count--, remove session
  Timeout     → count--, remove session
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
- Global state access (`state.License.activeSessions.count`)
- Numeric comparison (propositional)
- Session tracking (state management, not policy logic)

The policy itself is propositional. The complexity is in **state management** (tracking sessions), not in policy evaluation. PNF evaluates against the current state; maintaining that state is a runtime concern.

## Scaling Considerations

For distributed deployments:
- Session state must be shared (Redis, etc.)
- Eventual consistency issues with concurrent logins
- May need optimistic locking or reservation system

These are implementation concerns outside PNF scope.
