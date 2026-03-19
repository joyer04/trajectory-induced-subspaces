# Data Layout

## Raw

- `raw/prompts_seed.jsonl`: seed prompt bank for controlled task families
- `raw/traces.jsonl`: generated reasoning traces

## Processed

- `processed/step_embeddings.npy`: step-level embeddings
- `processed/trajectory_index.parquet`: metadata for each embedded step
- `processed/delta_vectors.npy`: consecutive step deltas
- `processed/delta_index.parquet`: metadata for each delta vector

## Trace schema

Each trace record should contain:

- `trace_id`
- `prompt_id`
- `task_family`
- `model`
- `prompt`
- `steps`
- `final_answer`
- `outcome`
- `difficulty`

`steps` should be an ordered list of reasoning strings.
