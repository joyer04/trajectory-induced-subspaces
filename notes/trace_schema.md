# Trace Schema

## Prompt record

```json
{
  "prompt_id": "logic_001",
  "task_family": "symbolic_logic",
  "difficulty": "medium",
  "prompt": "Reason step by step: ..."
}
```

## Trace record

```json
{
  "trace_id": "trace_0001",
  "prompt_id": "logic_001",
  "task_family": "symbolic_logic",
  "model": "gpt-4.1-mini",
  "difficulty": "medium",
  "prompt": "Reason step by step: ...",
  "steps": [
    "Step text 1",
    "Step text 2",
    "Step text 3"
  ],
  "final_answer": "Final answer text",
  "outcome": "correct"
}
```

## Field notes

- `trace_id`: unique id per trajectory
- `prompt_id`: links the trace to the prompt bank
- `task_family`: one of the controlled task families
- `model`: generation source
- `steps`: ordered step strings after segmentation
- `outcome`: use `correct`, `incorrect`, or `uncertain`

## Segmentation rule

Keep step segmentation simple and deterministic.

Preferred rule:

- one reasoning sentence per step when possible
- preserve original order
- do not merge semantically separate operations

If the model outputs numbered steps, preserve them as separate entries.
