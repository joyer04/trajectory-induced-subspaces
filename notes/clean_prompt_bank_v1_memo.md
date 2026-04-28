# Clean Prompt Bank v1

This bank is designed for prompt-recurrent regime experiments where parser/oracle ambiguity should not dominate the geometry.

Design constraints:
- Every prompt has a dry-run expected answer.
- Every prompt has an oracle-recognized subfamily.
- Temporal prompts use parser-stable proper names or symbolic entities.
- Causal prompts preserve rule-token coverage from the current causal oracle.
- Arithmetic prompts target the three existing arithmetic mechanisms: combine-subtract, inverse-linear, and average-speed.

Total prompts: 66

Family counts:
- arithmetic: 30
- causal_reasoning: 16
- temporal_ordering: 20

Subfamily counts:
- arithmetic/average_speed: 10
- arithmetic/combine_subtract: 10
- arithmetic/inverse_linear: 10
- causal_reasoning/chain_propagation: 8
- causal_reasoning/gated_condition: 8
- temporal_ordering/full_ordering: 10
- temporal_ordering/query_extraction: 10

Difficulty counts:
- easy: 17
- hard: 23
- medium: 26

Next use:
```bash
PYTHONPATH=src python3 -m tis.build_subfamily_jobs --input data/raw/clean_prompt_bank_v1.jsonl --output data/raw/clean_prompt_bank_v1_jobs.jsonl --repeats 5 --temperature 0.3
```

Generation command once local model serving is available:
```bash
PYTHONPATH=src python3 -m tis.generate_ollama_outputs --prompts data/raw/clean_prompt_bank_v1_jobs.jsonl --output data/raw/model_outputs_clean_prompt_bank_v1.jsonl --model qwen3:4b --limit 330 --overwrite --temperature 0.3
```

vLLM/OpenAI-compatible alternative:
```bash
PYTHONPATH=src python3 -m tis.generate_openai_compatible_outputs --prompts data/raw/clean_prompt_bank_v1_jobs.jsonl --output data/raw/model_outputs_clean_prompt_bank_v1.jsonl --base-url http://127.0.0.1:8000/v1 --model MODEL_NAME --limit 330 --overwrite --temperature 0.3
```

Post-generation pipeline:
```bash
PYTHONPATH=src .venv/bin/python -m tis.run_clean_prompt_bank_pipeline --model-outputs data/raw/model_outputs_clean_prompt_bank_v1.jsonl --traces data/raw/traces_clean_prompt_bank_v1.jsonl --oracle-traces data/raw/traces_clean_prompt_bank_v1_oracle.jsonl --summary-dir outputs/clean_prompt_bank_v1
```

Optional task audit on this clean run:
```bash
PYTHONPATH=src .venv/bin/python -m tis.audit_task_cleanliness --trace-files data/raw/traces_clean_prompt_bank_v1_oracle.jsonl --output-dir outputs/task_audit_clean_prompt_bank_v1
```
