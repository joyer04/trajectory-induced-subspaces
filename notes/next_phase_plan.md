# Next Phase Plan

## Runtime decision

Current recommendation:

- continue with Ollama now
- do not switch the active pipeline to vLLM yet

## Why not switch immediately

Local facts:

- Ollama is already installed and serving usable local models
- the current machine is Apple Silicon M4
- `vllm` is not installed in the local Python environment

Current support picture:

- vLLM officially lists Apple silicon under supported installation targets
- but Apple Silicon support is newer and more operationally complex than the current Ollama setup
- the newest macOS path appears to rely on `vllm-metal` / MLX-style workflows rather than the simple path used on CUDA Linux

Practical conclusion:

- for this research sprint, inference throughput is not yet the main bottleneck
- dataset design, comparison metrics, and bridge analyses matter more than engine migration
- therefore, stay on Ollama for now and revisit vLLM only when batch generation volume becomes the limiting factor

## Revisit trigger for vLLM

Reconsider vLLM when at least one becomes true:

1. trace generation exceeds 500-1000 prompts per batch
2. local interpretation or grading becomes the main runtime bottleneck
3. we need OpenAI-compatible high-throughput serving for downstream tools
4. we decide to standardize around MLX or Docker Model Runner with `vllm-metal`

## Research workstreams

## Framing note

Biology is not the core target of the project.

It is only one possible analogy or application area.

The actual reason for adding Spatial Semantomics is methodological:

- it gives a static semantic manifold baseline
- it provides axes, domains, and graph structure
- it lets us test whether reasoning moves along pre-existing gradients or creates local directions

So the main research object remains:

- reasoning geometry
- trajectory-induced subspaces
- static-vs-dynamic structure comparison

### 1. Data expansion

Target:

- grow Spatial Semantomics text corpora from 20 to 200-1000 phrases

Approach:

- use deterministic domain phrase generators first
- keep families balanced across biology, finance, ML, physics, policy, software, medicine
- store generated corpora as JSON files with metadata

Deliverables:

- `data/spatial_semantomics_corpus_200.json`
- `data/spatial_semantomics_corpus_500.json`
- corpus generation script

### 2. Stability evaluation

Target:

- compare manifold structure across 2-3 embedding models

Recommended embedding set:

- `sentence-transformers/all-MiniLM-L6-v2`
- `sentence-transformers/all-mpnet-base-v2`
- `BAAI/bge-small-en-v1.5`

Metrics:

- adjusted Rand index for cluster agreement
- pairwise cluster size comparison
- axis correlation / cosine overlap
- nearest-neighbor overlap

Deliverables:

- model comparison summary table
- stability note with failure cases

### 3. Static vs dynamic bridge

Target:

- compare Spatial Semantomics axes against TIS trajectory deltas on the same task corpus

Key tests:

- cosine alignment between trajectory deltas and static axes
- whether correct traces align more strongly to dominant static gradients
- whether incorrect traces show higher off-axis residual energy

Deliverables:

- bridge analysis script
- alignment summary CSV
- first memo on static-axis-following vs local-subspace-creation

### 4. Error analysis

Target:

- reduce noise in cluster and axis labeling

Approach:

- keep LLM labels
- add statistical labels from token frequencies and tf-idf style cluster descriptors
- compare the two side by side

Deliverables:

- `cluster_labels_combined.csv`
- `axis_labels_combined.csv`

### 5. Integrated research question

Core question:

- do reasoning trajectories mostly move along pre-existing manifold gradients
- or do they create local directions not recoverable from static semantic structure

Minimal decision criterion:

- if delta vectors are consistently well-explained by static axes, the manifold is mostly pre-structured
- if strong residual structure remains after static-axis projection, local subspace induction is real and non-trivial

## Immediate implementation order

1. build deterministic corpus expansion
2. build statistical labeling for Spatial Semantomics
3. build embedding-model stability comparison
4. build TIS vs Spatial bridge analysis
5. only then reconsider vLLM migration
