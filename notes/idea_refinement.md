# Idea Refinement

## What to emphasize

The strongest sentence in the original concept is:

`trajectory creates subspace`

That is the actual research lever. Keep the project centered there.

## What to de-emphasize for now

Do not lead with biology in the first stage.

Why:

- biology introduces domain-knowledge confounds
- pathway reasoning can hide whether the geometry comes from reasoning or from specialized vocabulary
- the first PoC should isolate mechanism, not application area

## Better foundational framing

A stronger sequence is:

1. show trajectory-induced subspace effects in controlled general reasoning
2. show the effect survives across task families
3. only then test a domain application such as biology

This makes the project more fundamental and more publishable as a method or conceptual contribution.

## Suggested foundational task ladder

Start simple:

- arithmetic
- symbolic transformation
- temporal ordering
- if-then causal chains

Then expand:

- commonsense multi-hop
- factual QA with distractors
- adversarial failure cases

## Stronger hypothesis split

Use three explicit hypotheses instead of one broad claim.

H1:
Reasoning traces produce locally low-dimensional delta structure.

H2:
Task families differ in the geometry of their induced subspaces.

H3:
Reasoning failure appears as geometric divergence, instability, or subspace escape.

## Practical modeling choice

For the first round, prefer lightweight sentence embeddings over hidden-state extraction from a large model.

Reason:

- faster iteration
- lower engineering overhead
- easier comparison across trace datasets

If signal appears, later upgrade to hidden-state trajectories for stronger claims.

## Non-overlap with Phi-Bridge

This project is not about mapping one embedding space to another.

It is about whether sequential semantic movement itself has stable geometry.

Clean separation:

- Phi-Bridge asks about alignment across spaces
- this project asks about dynamics within a reasoning path

## Proposed first claim to pursue

A realistic first claim is:

"Across controlled reasoning tasks, step-to-step semantic transitions occupy reusable low-dimensional directions, and incorrect trajectories deviate from those dominant directions."

That claim is narrower than the full vision, but strong enough for a PoC.
