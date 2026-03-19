# Local Ollama Workflow

## Recommended first model

Use `qwen3:4b` first.

Reason:

- lightweight enough for batch trace collection
- better reasoning quality than very small models
- already available locally

## Minimal command sequence

1. Generate 100 prompts:

```bash
PYTHONPATH=src python -m tis.generate_prompts --per-family 20
```

2. Run Ollama on the first 20 prompts:

```bash
PYTHONPATH=src python -m tis.generate_ollama_outputs --model qwen3:4b --limit 20 --overwrite
```

3. Convert raw outputs into trace format:

```bash
PYTHONPATH=src python -m tis.prepare_traces --input data/raw/model_outputs.jsonl
```

4. Validate traces:

```bash
PYTHONPATH=src python -m tis.validate_traces --traces data/raw/traces.jsonl
```

5. Run analysis:

```bash
PYTHONPATH=src python -m tis.run_pipeline --traces data/raw/traces.jsonl --embedding-model local-hashing
```

## Notes

- start with a small batch before generating the full set
- inspect segmentation quality after the first 10-20 prompts
- keep temperature low for cleaner reasoning structure
- use `local-hashing` first if network-free execution matters more than embedding quality
