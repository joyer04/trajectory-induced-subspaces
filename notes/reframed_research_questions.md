# Reframed Research Questions

## Core project objective

The real objective of this project is not simply to visualize embeddings.

It is to distinguish between two competing views of reasoning:

1. reasoning as movement along pre-existing semantic structure
2. reasoning as local structure formation induced by the trajectory itself

In short:

- static manifold following
- versus
- trajectory-induced subspace formation

## Reframed central question

When an LLM reasons step by step, is it mainly traversing pre-existing semantic gradients, or does the reasoning process create new local geometric structure that is not recoverable from the static manifold alone?

## Why this is better than the earlier framing

Earlier versions of the question were too weak or too narrow:

- "Do trajectories cluster?"
- "Are incorrect traces more off-axis?"

Those are useful diagnostics, but they are not the real research target.

The stronger framing asks whether static and dynamic geometry are fundamentally the same object or different ones.

## Three primary research questions

### RQ1. Static dependence

To what extent are reasoning deltas explainable by pre-existing static semantic axes?

Operational test:

- project trajectory deltas onto static axis bases
- measure alignment and residual energy

Interpretation:

- high explained movement implies manifold following
- high residual structure implies additional local geometry

### RQ2. Local structure formation

Do reasoning traces form reusable low-dimensional local subspaces beyond what static axes explain?

Operational test:

- remove static-axis components from deltas
- analyze residual deltas with PCA and clustering
- check whether residuals still exhibit recurring structure

Interpretation:

- structured residuals support trajectory-induced subspace formation
- unstructured residuals support static-axis sufficiency

### RQ3. Failure regime geometry

Are reasoning failures random deviations, or do they occupy their own geometric regimes?

Operational test:

- compare correct and incorrect traces within task family
- compare axis alignment, residual energy, and residual clustering

Interpretation:

- random errors should look diffuse and unstable
- failure regimes should show repeatable geometric signatures

## Falsifiable hypotheses

### H1. Partial static explainability

Static semantic axes explain some, but not most, of reasoning movement.

Predicted signal:

- non-trivial but modest axis alignment
- substantial residual energy remains

### H2. Residual structure is real

After removing static-axis components, residual trajectory deltas still show low-dimensional structure.

Predicted signal:

- residual PCA spectra remain concentrated
- residual delta clusters remain task-sensitive

### H3. Failure is structured

Incorrect reasoning is not merely noisier; in at least some task families it occupies alternative geometric regimes.

Predicted signal:

- incorrect traces differ in residual clustering or dominant axis usage
- effect is family-dependent, not globally uniform

## What this project is not

- not mainly a biology project
- not mainly a manifold visualization project
- not mainly a prompt-engineering exercise

Biology can be a downstream application area, but the core contribution is methodological and conceptual.

## Strongest one-sentence project description

This project builds an experimental framework to test whether LLM reasoning follows pre-existing semantic manifolds or induces new local subspaces during the trajectory itself.
