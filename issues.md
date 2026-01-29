# RL2 Open Issues

Tracked design questions and unresolved issues for the RL2 ontology, semantics, and tooling.

---

## Issue 1: Action Ontological Status and Hierarchy Mechanism

**Status:** Resolved
**Affects:** `rl2.ttl`, `RL2_Semantics.md`, `RL2_Vocabulary.md`, use cases
**Related:** ODRL 2.2 `odrl:includedIn`, `RL2_Semantics.md` lines 640-654

### Problem

RL2 had no defined mechanism for expressing action hierarchies. The ontology declared `rl2:Action` as an OWL class and said profiles define actions as individuals of that class, but provided no property for relating actions hierarchically.

Use cases used `rdfs:subClassOf` on action individuals (OWL punning), which was confusing for authors, fragile for tooling, and inconsistent with the "actions are individuals" design.

The semantics document referenced three possible mechanisms (`rdfs:subClassOf`, `skos:broader`, `skos:narrower`) without committing to one.

### Design Question

Are actions **individuals**, **classes**, or both? And how are action hierarchies expressed?

| Approach | Mechanism | Pros | Cons |
| -------- | --------- | ---- | ---- |
| **Individuals + dedicated property** (ODRL style) | `rl2:includedIn` | Clean separation; no punning; ODRL-compatible; simple SPARQL queries | Requires defining a new property; subsumption is not RDFS-entailed |
| **Classes** (pure OWL) | `rdfs:subClassOf` | Standard RDFS entailment; reasoners work out of the box | Actions-as-classes is semantically odd; requires punning in norms |
| **SKOS concepts** | `skos:broader` / `skos:narrower` | Well-established hierarchy pattern | Imports SKOS dependency; transitivity subtleties; conflates concept taxonomy with operational semantics |
| **OWL punning** (de facto before fix) | `a rl2:Action` + `rdfs:subClassOf` | Works in OWL 2 | Confusing for authors; tooling support varies; semantically muddled |

### Decision: Individuals + `rl2:includedIn`

Actions are **named individuals** (type-symbols representing kinds of actions, not concrete events). Action hierarchies are expressed via `rl2:includedIn`, a transitive object property in RL2 Core.

**Rationale:**

1. **No punning.** Actions remain pure individuals of `rl2:Action`. No IRI is both instance and class.
2. **Deterministic evaluation.** Action subsumption is a bounded graph reachability problem, not OWL reasoning. Evaluators do explicit traversal; no reasoner required.
3. **ODRL compatibility.** Mirrors `odrl:includedIn` structurally, simplifying translation/transpilation. RL2 omits the SKOS dependency (optional alignment available separately).
4. **Clean author story.** "Define actions as individuals; relate them with `rl2:includedIn`."

### Changes Made

**`rl2.ttl`** -- Added `rl2:includedIn`:

```turtle
rl2:includedIn a owl:ObjectProperty, owl:TransitiveProperty ;
    rdfs:domain rl2:Action ;
    rdfs:range rl2:Action ;
    rdfs:label "Included In" ;
    rdfs:comment """Action taxonomy: A includedIn B means A is a narrower action
    included within B. Transitive. Do NOT use rdfs:subClassOf for action hierarchies.""" .
```

**`RL2_Semantics.md`** -- Replaced vague RDF grounding with:

```
action_match(x_req, x_pol) := (x_req = x_pol) ∨ reachable(x_req, rl2:includedIn, x_pol)
```

SPARQL: `ASK { ?x_req rl2:includedIn* ?x_pol }`. Usage of `rdfs:subClassOf` for action refinement is non-normative.

**`RL2_Vocabulary.md`** -- Documented `rl2:includedIn` in the Action class notes and property reference table.

**`CLAUDE.md`** -- Added common mistake: "Using `rdfs:subClassOf` for action hierarchies → Use `rl2:includedIn`".

**`usecases/no-ml-training.md`** -- Replaced `rdfs:subClassOf` with `rl2:includedIn`:

```turtle
ai:createEmbeddings a rl2:Action ;
    rdfs:label "Create Embeddings" ;
    rl2:includedIn ai:trainModel .
```

**`usecases/internal-use-only.md`** -- Removed bogus `rdfs:subClassOf rl2:Action` from action individuals.

**`usecases/role-hierarchy.md`** -- Clarified that asset/role hierarchies use `rdfs:subClassOf` while action hierarchies use `rl2:includedIn`.

### SKOS Alignment (Optional, Not Yet Implemented)

For environments that want SKOS tooling interop, a separate alignment module can be created:

```turtle
# rl2-skos.ttl (optional, not core)
rl2:includedIn rdfs:subPropertyOf skos:broaderTransitive .
rl2:Action rdfs:subClassOf skos:Concept .
```

This keeps Core lean while enabling SKOS-aware UI tooling.

### Compatibility Stance

Be strict in profiles (no punning), tolerant in ingestion: if legacy data contains `?a rdfs:subClassOf ?b` where both are `rl2:Action` individuals, treat it as a repairable authoring error and transpile to `?a rl2:includedIn ?b` with a diagnostic.

---

## Issue 2: Action Subsumption Asymmetry Between Request Matching and Duty Fulfillment

**Status:** Resolved
**Affects:** `RL2_Semantics.md`
**Related:** Issue 1 (`rl2:includedIn`)

### Problem

Action subsumption via `rl2:includedIn` applies to **request matching** but not to **duty fulfillment**. This creates an asymmetry:

**Request matching** (line 645) uses subsumption:

```
matches(Norm(a, x, s, c), R) =
    ... (x = x_req ∨ x_req ⊑ x) ...
```

A privilege on `trainModel` covers a request to `fineTune` because `fineTune includedIn trainModel`.

**Duty fulfillment** (line 1278) checks exact action:

```
Σ.ObligationState(d) = Active
Σ.Performed(d.subject, d.action, d.object) = true
```

A duty requiring `trainModel` is NOT fulfilled by performing `fineTune`, because the event log records `Performed(a, fineTune, s)` and the check looks up `Performed(a, trainModel, s)` — an exact match that fails.

### Concrete Example

```turtle
# Action hierarchy
ai:fineTune a rl2:Action ; rl2:includedIn ai:trainModel .

# Privilege: "Licensee may train models"
ex:trainPrivilege a rl2:Privilege ;
    rl2:action ai:trainModel .

# Duty: "Licensee must train a model before deadline"
ex:trainDuty a rl2:Duty ;
    rl2:action ai:trainModel .
```

Agent performs `fineTune`:
- Privilege check: **PERMIT** (fineTune ⊑ trainModel, subsumption applies)
- Duty fulfillment: **NOT FULFILLED** (Performed looks up trainModel exactly, finds nothing)

### Design Tension

Both interpretations are defensible:

**Subsumption should apply to duties too:**
- A duty to "train a model" is naturally satisfied by fine-tuning (a kind of training)
- The asymmetry is surprising — if the action hierarchy says fineTune IS a kind of trainModel, that should hold everywhere
- Parallel with request matching: if fineTune is "close enough" to trainModel for permission, it should be "close enough" for fulfillment

**Exact match for duties is intentional:**
- Duties are more specific obligations — "train a model" might mean full training, not just fine-tuning
- Narrower actions may not satisfy the full intent of a broader duty
- Prohibitions would also need consideration: if `fineTune` is performed, is a prohibition on `trainModel` violated? Subsumption says yes, which seems correct — but the same `Performed` check applies

### Note on Prohibitions

The prohibition violation rule (line 1099-1102) also uses `Performed`:

```
ProhibitionActive(a, x, s, c)
Σ.Performed(a, x, s) = true
```

Under exact match: performing `fineTune` does NOT violate a prohibition on `trainModel`. This seems clearly wrong — if `fineTune includedIn trainModel`, then fine-tuning should violate a training prohibition.

This strengthens the case that `Performed` checks should be subsumption-aware, at least for prohibitions.

### Possible Resolutions

1. **Make `Performed` subsumption-aware**: When recording `Performed(a, fineTune, s)`, also record `Performed(a, trainModel, s)` for all ancestors in the `includedIn` chain. Simple but changes the state model.

2. **Make fulfillment/violation checks subsumption-aware**: Change duty fulfillment and prohibition violation checks to use `∃x' : Performed(a, x', s) ∧ (x' = x ∨ x' ⊑ x)`. Keeps `Performed` exact but adds traversal at check time.

3. **Distinguish by norm type**: Privileges and prohibitions use subsumption; duties require exact match. Document this as intentional. Requires a clear rationale for the asymmetry.

4. **Leave to profiles**: Profiles that define action hierarchies are responsible for specifying whether subsumption applies to fulfillment. Core semantics remain exact-match.

### Decision: Uniform Subsumption via `performed()` Helper (Resolution 2)

Action subsumption applies uniformly across all norm types. `Σ.Performed` remains the raw log of exact actions. A subsumption-aware helper `performed()` is used at query time:

```
performed(a, x, s, Σ) :=
    ∃x' : Σ.Performed(a, x', s) ∧ (x' = x ∨ x' ⊑ x)
```

This is the same bounded graph traversal already required for request matching — no additional reasoning complexity.

**Rationale:** The prohibition case is decisive. If `fineTune includedIn trainModel`, performing fine-tuning must violate a prohibition on training. The same logic extends to duty fulfillment: fine-tuning satisfies a duty to train. If a profile needs exact-match duty semantics, it should define the action at the exact level required rather than relying on the absence of subsumption.

### Changes Made

All `Σ.Performed(a, x, s)` checks in `RL2_Semantics.md` replaced with `performed(a, x, s, Σ)`:

- **Request matching section**: Defined `performed()` alongside `action_match()` and the `⊑` notation
- **Duty fulfillment** (small-step rule): `performed(a,x,s,Σ) = true`
- **Duty violation** (small-step rule): `performed(a,x,s,Σ) = false`
- **Prohibition violation**: `performed(a, x, s, Σ) = true`
- **contentHolds**: `performed(a, x, s, Σ)` for `Action` content
- **D-FULFILL / D-VIOLATE** (big-step rules): Both use `performed()`
- **updateOneDuty** (algorithmic form): Uses `performed()`

`Σ.Performed` is unchanged — it still records exact actions via `processEvent`. `performed()` adds subsumption at read time.
