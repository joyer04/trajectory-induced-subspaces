# Source Layout

- `tis/io_utils.py`: JSONL and parquet helpers
- `tis/embedding.py`: sentence embedding wrapper
- `tis/trajectories.py`: step flattening and delta-vector construction
- `tis/analysis.py`: PCA and direction clustering baselines
- `tis/prompt_bank.py`: controlled prompt templates by task family
- `tis/generate_prompts.py`: prompt bank writer
- `tis/generate_ollama_outputs.py`: local Ollama trace generation
- `tis/prepare_traces.py`: convert raw step-by-step outputs into trace JSONL
- `tis/judge_traces.py`: label trace outcomes with a local Ollama judge
- `tis/spatial_semantomics.py`: static semantic manifold experiment
- `tis/run_spatial_semantomics.py`: entry point for the Spatial Semantomics experiment
- `tis/extract_step_corpus.py`: build a static text corpus from TIS reasoning steps
- `tis/summarize_bridge_results.py`: compare bridge alignment by family and outcome
- `tis/analyze_residual_structure.py`: decompose deltas into static-axis and residual structure
- `tis/describe_residual_regimes.py`: summarize residual clusters with exemplars and family/outcome profiles
- `tis/write_midpoint_memo.py`: generate a markdown midpoint review from bridge outputs
- `tis/family_aware_residual_analysis.py`: quantify family-level residual regime differences
- `tis/write_family_regime_memo.py`: write a memo focused on family-specific residual regimes
- `tis/analyze_regime_recurrence.py`: quantify how strongly regimes recur within family/outcome
- `tis/label_residual_regimes.py`: assign names to family-aware residual regimes from exemplars
- `tis/analyze_prompt_level_recurrence.py`: test whether residual-regime profiles recur across prompts
- `tis/write_prompt_recurrence_memo.py`: write a memo on prompt-level recurrence
- `tis/validate_traces.py`: trace schema validator
- `tis/run_pipeline.py`: end-to-end baseline pipeline
- `tis/write_report.py`: markdown report generator

## Intended first run

From the project root:

```bash
PYTHONPATH=src python -m tis.generate_prompts --per-family 20
PYTHONPATH=src python -m tis.generate_ollama_outputs --model qwen3:4b --limit 20 --overwrite
PYTHONPATH=src python -m tis.prepare_traces --input data/raw/model_outputs.jsonl
PYTHONPATH=src python -m tis.validate_traces --traces data/raw/traces.jsonl
PYTHONPATH=src python -m tis.run_pipeline --traces data/raw/traces.jsonl --embedding-model local-hashing
PYTHONPATH=src python -m tis.write_report
```

Before running, create `data/raw/traces.jsonl` using the schema in `notes/trace_schema.md`.

Use `local-hashing` when you want a fully offline baseline with no model downloads.

## Spatial Semantomics

Run the static semantic-geometry experiment:

```bash
PYTHONPATH=src python -m tis.run_spatial_semantomics \
  --input data/spatial_semantomics_texts.json \
  --output-dir outputs/spatial_semantomics \
  --embedding-model sentence-transformers/all-MiniLM-L6-v2 \
  --ollama-model llama3.2:latest
```
