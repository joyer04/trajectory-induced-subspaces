# Spatial Semantomics Plan

## Objective

Implement a reusable experiment that treats embedding space as a spatial manifold with:

- semantic axes
- semantic domains
- local neighborhood graph structure

## Immediate implementation target

Build a modular Python pipeline with these required functions:

- `compute_embeddings()`
- `build_knn_graph()`
- `discover_axes()`
- `segment_domains()`
- `visualize_space()`
- `interpret_clusters()`
- `interpret_axes()`

## Phase 1

Run a minimal end-to-end experiment on a compact text list.

Deliverables:

- embeddings matrix
- cosine kNN graph
- top 5 semantic axes from PCA
- spectral clustering over axis coordinates
- UMAP cluster plot
- axis gradient plots
- cluster and axis interpretation tables

## Phase 2

Stress-test on larger text sets.

Questions:

- do clusters remain stable across embedding models?
- do axes remain interpretable across corpora?
- do graph communities align with gradient segmentation?

## Phase 3

Connect back to trajectory-induced subspaces.

Proposed bridge:

- compare static semantic axes from Spatial Semantomics
- against dynamic trajectory-induced directions from TIS

Key question:

Do reasoning traces move along pre-existing spatial gradients, or do they create new local directions not visible in the static manifold?
