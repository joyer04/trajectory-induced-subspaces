# Trajectory-Induced Subspaces in LLM Semantic Manifolds

Personal learning and exploratory research on reasoning geometry in LLMs.

This repository is a personal learning, experimentation, and exploratory research space.

It is being used as a public workbench for studying reasoning geometry in LLMs:

- ideas in progress are kept visible
- exploratory plots and dashboards are part of the repo
- claims should be read as provisional unless explicitly stress-tested

## Why this folder exists

This project studies a core hypothesis:

Reasoning trajectories may induce local subspaces in representation space, rather than merely selecting fixed semantic axes.

This is intentionally adjacent to, but distinct from, Phi-Bridge.

- Phi-Bridge: cross-embedding alignment
- This project: reasoning geometry and trajectory-induced subspace formation

## Current framing

Primary question:

Can multi-step reasoning traces be represented as geometric trajectories whose local transitions form recurring low-dimensional subspaces?

Current exploratory write-up:

- [Exploratory research note](./outputs/exploratory_research_note.md)
- [Exploratory dashboard](./outputs/dashboard/index.html)
- [Blog-style research report](./docs/research_blog_report.md)

If you are browsing this repo on GitHub, the note and dashboard are probably the best entry points.

Suggested GitHub repo metadata:

- Description: `Personal learning and exploratory research on reasoning geometry in LLMs.`
- Website: `outputs/dashboard/index.html`

Core object:

- trajectory = {x_0, x_1, ..., x_n}
- delta step = x_i - x_(i-1)
- induced subspace S ~= span(delta_1, delta_2, ..., delta_n)

Stronger reframing:

The key question is whether reasoning mostly follows pre-existing semantic gradients, or whether the trajectory itself induces local geometric structure not recoverable from the static manifold alone.

## Design principles

- Prefer lightweight embeddings for fast iteration
- Stay domain-general before moving into biology
- Focus on synthetic and foundational reasoning tasks first
- Keep the stack simple enough for one-agent PoC execution

## Initial non-biology task focus

To keep the work fundamental rather than domain-specific, start with:

- arithmetic and symbolic reasoning
- logical entailment / contradiction
- temporal ordering
- causal toy problems
- multi-step commonsense QA

These tasks are preferable to biology for the first pass because they reduce confounds from domain knowledge and let us isolate geometry induced by reasoning structure itself.

## Embedding strategy

Use a lightweight sentence embedding model first.

Recommended order:

1. `intfloat/e5-small-v2`
2. `sentence-transformers/all-MiniLM-L6-v2`
3. `BAAI/bge-small-en-v1.5`

Reason:

- small enough for rapid experiments
- good enough for trajectory-level comparisons
- easy to swap for robustness checks

## PoC scope

The first PoC should answer only these questions:

1. Do reasoning step vectors cluster into recurring directions?
2. Do different task families induce measurably different subspaces?
3. Do failure trajectories deviate from dominant task subspaces?

Avoid for now:

- multimodal work
- biology-specific pathway reasoning
- heavy interpretability claims at token-layer granularity
- cross-model alignment beyond a minimal sanity check

## Minimal structure

- `data/`: raw prompts, generated traces, processed trajectory tables
- `src/`: loaders, embedding, trajectory construction, clustering, metrics
- `notebooks/`: exploration and plotting
- `outputs/`: figures, PCA plots, cluster summaries, reports
- `papers/`: references and reading notes
- `notes/`: framing, hypotheses, experiment notes

## Immediate next actions

1. Define a compact task suite with 20-50 prompts per family
2. Fix one embedding model and one generation source
3. Serialize traces as step lists plus metadata
4. Build delta vectors and run baseline PCA + clustering
5. Compare correct vs failure trajectories

## Working commands

Generate a larger prompt bank:

```bash
PYTHONPATH=src python -m tis.generate_prompts --per-family 20
```

Validate trace formatting:

```bash
PYTHONPATH=src python -m tis.validate_traces --traces data/raw/traces.jsonl
```

Run the baseline pipeline:

```bash
PYTHONPATH=src python -m tis.run_pipeline --traces data/raw/traces.jsonl --embedding-model local-hashing
```

Write a short markdown summary from processed outputs:

```bash
PYTHONPATH=src python -m tis.write_report
```
