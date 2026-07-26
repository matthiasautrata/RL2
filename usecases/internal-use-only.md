# Use Case 18: Internal Use Only

**Pattern:** Basic use restriction  
**Vocabulary Demonstrated:** `Prohibition` (basic), `Privilege` (scoped)  
**Category:** External Data Licenses  
**Status:** DRAFT

---

## Business Context

The most fundamental restriction in data licensing: **internal use only**. This means:

- Data can be used within the licensee organization
- Data cannot be shared with third parties
- Data cannot be resold or redistributed
- Data cannot be exposed in external products

This is the baseline from which all other license restrictions build.

## Scenario

A company licenses reference data (company identifiers, security metadata) from a data vendor. The license permits use for:
- Internal analytics
- Internal reporting
- Internal systems

But prohibits:
- Sharing with partners
- Including in products sold to customers
- Displaying on public websites

## Policy Intent

> "Licensee may use the data for internal business purposes only. External use is prohibited."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Scope | Organization boundary |
| Permitted | Internal operations |
| Prohibited | Any external exposure |
| Typical term | Per-user or enterprise license |

## Real-World Terms

### Bloomberg

> "Database Information is provided for Customer's internal commercial (non-consumer related) use only and may not be provided to third parties."

### SAP

> "All information provided to Customer by SAP... is provided for Customer's internal commercial (non-consumer related) use only and may not be provided to third parties."

### Fannie Mae

> "Licensee will strictly prohibit End Users from reselling, disclosing or redistributing the Data externally."

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Internal Use                             │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Action: use (internal operations)                   │
│  Object: Licensed Data                               │
│  Scope: Internal purposes only                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Prohibition: External Use                           │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Prohibited Action: externalUse                      │
│  Object: Licensed Data                               │
│  Scope: Any external party                           │
└─────────────────────────────────────────────────────┘
```

## What Counts as "Internal"?

| Entity | Internal? | Notes |
|--------|-----------|-------|
| Same legal entity | Yes | Core case |
| Wholly-owned subsidiary | Usually | Check license terms |
| Affiliate (>50% owned) | Maybe | Often requires extension |
| Joint venture | Usually no | Separate license needed |
| Contractor (on premises) | Maybe | With appropriate controls |
| Contractor (off premises) | Usually no | Depends on terms |
| Outsourced function | Maybe | Often requires DPA |

## What Counts as "External Use"?

| Activity | External? | Notes |
|----------|-----------|-------|
| Internal dashboard | No | Core permitted use |
| Report to board | No | Internal governance |
| Report to regulator | Special case | Often explicitly permitted |
| Send to customer | Yes | Prohibited |
| Display on website | Yes | Prohibited |
| Include in product | Yes | Prohibited |
| API for partners | Yes | Prohibited |

## Evaluation Logic

```
Request: Agent A wants to perform action X on data D

1. Is X an internal use?
   - Check action type
   - Check recipient (if any)
   
2. If internal use → Check Privilege conditions → PERMIT/DENY
   If external use → Check Prohibition → DENY
```

## Exception Patterns

Most "internal use only" licenses include exceptions:

| Exception | Description |
|-----------|-------------|
| Regulatory disclosure | May share with regulators |
| Legal process | May disclose under subpoena |
| Audit | May show to auditors |
| Transaction counterparty | May share in transaction context |

## Comparison with Related Use Cases

| Use Case | Relationship |
|----------|--------------|
| **internal-use-only** | Basic restriction |
| no-redistribution (19) | More explicit prohibition |
| derived-data-restriction (20) | Derived works nuance |
| pass-through-terms (23) | Downstream obligations |

## Profile Requirements

```turtle
@prefix license: <https://example.org/profile/license#> .

license:internalUse a rl2:Action ;
    rdfs:label "Internal Use" ;
    rdfs:comment "Use within the licensee organization." .

license:externalUse a rl2:Action ;
    rdfs:label "External Use" ;
    rdfs:comment "Use involving third parties outside the organization." .

license:recipientTypeOperand a rl2:LeftOperand ;
    rl2:resolutionPath "context.recipient.type" ;
    rdfs:comment "Type of recipient: internal, regulator, external, etc." .

license:isAffiliateOperand a rl2:LeftOperand ;
    rl2:resolutionPath "context.recipient.isAffiliate" ;
    rdfs:range xsd:boolean .
```

## Audit Requirements

Internal use licenses often require:
- User access logging
- Periodic usage reports to vendor
- Compliance certification
- Right to audit clause

---

## RL2 Model

This model demonstrates a scoped Privilege (internal use) with a
`context.recipient.type` condition, and a basic Prohibition against
external use. All entities are declared within the model block so the
graph is self-contained.

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ── Actions ──────────────────────────────────────────────────────
ex:internalUse a rl2:Action ;
    rdfs:label "Internal Use" ;
    rdfs:comment "Use within the licensee organization." .

ex:externalUse a rl2:Action ;
    rdfs:label "External Use" ;
    rdfs:comment "Use involving third parties outside the organization." .

# ── Operand — resolves to the recipient context ─────────────────
ex:recipientTypeOperand a rl2:LeftOperand ;
    rdfs:label "Recipient Type" ;
    rl2:resolutionPath "context.recipient.type" .

# ── Privilege: internal use permitted ───────────────────────────
ex:internalUsePrivilege a rl2:Privilege ;
    rl2:subject ex:Licensee ;
    rl2:action ex:internalUse ;
    rl2:object ex:LicensedData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:recipientTypeOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "internal"
    ] .

# ── Prohibition: external use forbidden ─────────────────────────
ex:externalUseProhibition a rl2:Prohibition ;
    rl2:subject ex:Licensee ;
    rl2:prohibitedAction ex:externalUse ;
    rl2:object ex:LicensedData .

# ── Policy grouping both norms ──────────────────────────────────
# Uses rl2:Policy (the base class) with both a Privilege clause and
# a Prohibition clause.
ex:internalUsePolicy a rl2:Policy ;
    rl2:grantor ex:DataVendor ;
    rl2:grantee ex:Licensee ;
    rl2:clause ex:internalUsePrivilege, ex:externalUseProhibition .
```

---

## References

- Bloomberg Data License Terms
- SAP Data License Provisions  
- Fannie Mae Data License Agreement
- Typical enterprise software EULA patterns
