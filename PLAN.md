# PoC Plan

## Goal

Build a small but defensible prototype showing whether reasoning trajectories exhibit recurring low-dimensional geometry.

## Research position

This project should stay at the level of representation geometry, not domain biology.

Working thesis:

- not "biology reasoning has geometry"
- but "reasoning itself may generate local geometric structure"

## Phase 1: framing and dataset spec

Deliverables:

- fixed task families
- prompt template set
- trace storage format
- success criteria

Task families:

- arithmetic chains
- symbolic logic chains
- temporal ordering
- causal micro-world reasoning
- commonsense multi-hop QA

Success criteria:

- each sample has explicit step segmentation
- each trace has final outcome label: correct / incorrect / uncertain
- at least 100 usable trajectories in the first dataset

## Phase 2: trace collection

Deliverables:

- `data/raw/prompts.jsonl`
- `data/raw/traces.jsonl`

Collection rules:

- keep prompts short and controlled
- request step-by-step outputs
- retain final answer and confidence if available
- include task family and difficulty metadata

## Phase 3: embedding and trajectory construction

Deliverables:

- `data/processed/step_embeddings.npy`
- `data/processed/trajectory_index.parquet`
- delta vectors per trace

Methods:

- embed each step independently
- optionally normalize vectors
- compute consecutive deltas
- compare raw-step geometry vs delta geometry

Primary default:

- start with `intfloat/e5-small-v2`

## Phase 4: geometry analysis

Deliverables:

- PCA spectra
- cluster assignments for delta vectors
- trajectory-level subspace estimates
- 2D visualization for inspection

Baseline analyses:

- PCA on delta vectors
- spherical k-means or cosine k-means
- per-task subspace dimension estimates
- pairwise principal angle comparison

Main tests:

1. Are cluster directions reused across traces?
2. Does each task family have a distinct subspace signature?
3. Are incorrect traces geometrically less coherent?

## Phase 5: interpretation

Deliverables:

- cluster exemplars
- cluster labels as semantic transition types
- short memo of what each direction may represent

Interpretation strategy:

- sample representative step transitions
- inspect them manually first
- only then ask an LLM for semantic naming support

## Two-week execution target

Week 1:

- finalize task suite
- collect first traces
- build embedding and delta pipeline
- add prompt generation and validation tooling

Week 2:

- run clustering and subspace metrics
- compare correct vs failure traces
- write a short findings memo

## Risks

- step segmentation may be noisy
- sentence embeddings may be too coarse
- clustering may reflect style rather than reasoning

## Risk mitigation

- keep prompts templated
- compare multiple embedding models later
- use synthetic tasks with controlled wording
- analyze both within-task and cross-task geometry

## Exit criteria for PoC

The PoC is successful if at least one of the following is demonstrated:

- recurring delta directions emerge across independent traces
- task families show separable subspace geometry
- failure traces show larger deviation from dominant subspaces
