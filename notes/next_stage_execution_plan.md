# Next Stage Execution Plan

## Stage objective

Turn the current prototype into a sharper test of:

- static manifold following
- versus
- trajectory-induced subspace formation

## Stage 1. Strengthen the bridge analysis

Goal:

- move from raw alignment inspection to decomposition analysis

Tasks:

1. compute static-axis explained variance for each delta
2. compute residual deltas after static projection
3. run PCA and clustering on residual deltas
4. summarize by task family and outcome

Expected outputs:

- `outputs/static_dynamic_bridge_50_minilm/residual_summary.csv`
- `outputs/static_dynamic_bridge_50_minilm/residual_group_summary.csv`

## Stage 2. Replace global error question with family-specific error question

Goal:

- stop asking whether incorrect traces are always more off-axis
- ask which families show structured failure geometry

Tasks:

1. compare correct vs incorrect inside each task family
2. measure dominant axis usage differences
3. measure residual clustering differences
4. identify families with stable failure signatures

Expected outputs:

- `outputs/static_dynamic_bridge_50_minilm/failure_regime_summary.csv`

## Stage 3. Expand data enough for stability

Goal:

- reduce variance from tiny sample sizes

Immediate target:

- 100 balanced traces

Follow-up target:

- 200 balanced traces

Tasks:

1. continue balanced prompt generation
2. keep scoring pipeline consistent
3. rerun MiniLM bridge pipeline at 100 traces

Expected outputs:

- `data/raw/traces_balanced_100_scored.jsonl`
- `data/processed_balanced_100_scored_minilm/`

## Stage 4. Model robustness

Goal:

- test whether static-vs-dynamic conclusions hold across embedding models

Tasks:

1. rerun TIS and bridge with `all-mpnet-base-v2`
2. rerun static step manifold with the same model
3. compare bridge summaries across embedding backbones

Expected outputs:

- side-by-side bridge comparison table

## Stage 5. Tighten interpretation

Goal:

- make the outputs read like evidence, not just artifacts

Tasks:

1. pair LLM labels with statistical descriptors
2. extract representative deltas for each cluster
3. write a short memo per family:
   what static axes capture
   what residual geometry adds

Expected outputs:

- `notes/midpoint_memo.md`

## Decision rule for the next milestone

We move forward with the stronger claim only if both hold:

1. static axes leave meaningful residual structure
2. that residual structure is reusable across traces or families

If not, the project shifts toward a static-manifold interpretation of reasoning.
