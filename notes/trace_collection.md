# Trace Collection

## Goal

Move from raw model outputs to a consistent trajectory dataset.

## Minimal workflow

1. Generate model answers from `data/raw/prompts_seed.jsonl`
2. Store each answer in `data/raw/model_outputs.jsonl`
3. Convert those raw outputs into `data/raw/traces.jsonl`
4. Validate the trace file
5. Run the geometry pipeline

## Raw model output schema

```json
{
  "prompt_id": "arith_001",
  "task_family": "arithmetic",
  "difficulty": "easy",
  "model": "your-model-name",
  "prompt": "Solve step by step: ...",
  "raw_output": "1. ...\n2. ...\nFinal answer: ..."
}
```

## Conversion policy

- split numbered steps when available
- otherwise split by line
- drop empty lines
- keep the final answer separately when detectable
- assign outcome manually at first, or with an external grader later

## Recommendation

For the first 20-40 traces, keep the workflow semi-manual.

That keeps segmentation quality high and reduces noise before automating more of the labeling pipeline.
