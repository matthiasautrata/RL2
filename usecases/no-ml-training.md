# Use Case 30: No ML Training

**Pattern:** Specific use prohibition  
**Vocabulary Demonstrated:** `Prohibition` with action constraint  
**Category:** Data Contracts, AI Governance  
**Status:** DRAFT

---

## Business Context

As AI/ML adoption grows, data providers increasingly restrict training use:

- **Competitive protection:** Don't train competitors' models
- **IP concerns:** Training may constitute derivative work
- **Consent scope:** Original consent didn't cover ML training
- **Quality control:** Provider wants control over model outputs

## Scenario

A content platform licenses images to a marketing agency. The license explicitly states:

> "Licensed content may not be used to train, develop, or improve any machine learning model, artificial intelligence system, or similar technology."

## Policy Intent

> "Use for ML/AI training is PROHIBITED regardless of other permissions."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Scope | All ML/AI training activities |
| Applies to | Models, fine-tuning, embeddings, etc. |
| Exception | None (or requires separate license) |
| Enforcement | Often contractual + technical |

## Real-World Terms

### Getty Images

Explicit prohibition on using licensed images for AI training.

### News Organizations

AP, Reuters, NYT have all added AI training restrictions to their terms.

### Stock Photography

Most major stock photo services now prohibit ML training use.

### Adobe Stock

Separate licensing tier for "AI training" use cases.

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Use Content (general)                   │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Action: use                                         │
│  Object: Licensed Content                            │
│  Condition: [standard license terms]                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Prohibition: ML Training Use                        │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Prohibited Action: trainModel                       │
│  Object: Licensed Content                            │
│  Scope: Any ML/AI system                             │
│  Priority: Higher than general use privilege         │
└─────────────────────────────────────────────────────┘
```

## What Constitutes "Training"?

| Activity | Typically Prohibited? |
|----------|----------------------|
| Training from scratch | Yes |
| Fine-tuning existing model | Yes |
| Creating embeddings | Often yes |
| RAG retrieval (no training) | Usually no |
| Inference only | No |
| Human review/labeling | Depends |

## Conflict Resolution

The prohibition takes priority over general use permissions:

```
General Privilege: "You may use the content"
Specific Prohibition: "You may not train models"

Result: Use permitted EXCEPT for training
```

This requires `rl2:priority` or specificity-based conflict resolution.

## Profile Requirements

```turtle
@prefix ai: <https://example.org/profile/ai#> .

ai:trainModel a rl2:Action ;
    rdfs:label "Train Model" ;
    rdfs:comment "Use data to train, fine-tune, or improve ML/AI systems." .

ai:createEmbeddings a rl2:Action ;
    rdfs:subClassOf ai:trainModel .

ai:fineTune a rl2:Action ;
    rdfs:subClassOf ai:trainModel .

ai:modelTypeOperand a rl2:LeftOperand ;
    rl2:resolutionPath "context.targetSystem.type" .
```

## Technical Enforcement

Beyond policy, technical measures may include:

- Watermarking content
- Monitoring for model outputs resembling licensed content
- API terms prohibiting training use
- Contractual audit rights

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate Prohibition with specific action
```

---

## References

- Getty Images Terms of Service — AI restrictions
- AP News Terms — ML training prohibition
- Creative Commons discussion on AI training
- EU AI Act — Training data requirements
