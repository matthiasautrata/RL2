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

## Notes

These topics represent potential future enhancements. They do not affect the validity of the current RL2 specification. Feedback and proposals are welcome.
