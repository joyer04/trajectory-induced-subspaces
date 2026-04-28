# Next-Generation Research Roadmap

Current goal stays fixed:

> Test whether LLM reasoning is better explained as static manifold following or trajectory-conditioned local structure.

The next step is to move from:

- `family -> subfamily -> regime`

to:

- `task form -> regime mechanism`

## Current Mechanism Map

Primary artifacts:

- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/regime_mechanism_synthesis/regime_mechanism_table.csv`
- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/regime_mechanism_synthesis/regime_mechanism_counts.csv`
- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/regime_mechanism_synthesis/regime_mechanism_heatmap.png`
- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/regime_mechanism_synthesis/regime_mechanism_strength.png`

Current strongest reads:

- `gated_condition`: `state_dominant`
- `chain_propagation`: `two_stage`
- `full_ordering`: `state_dominant`
- `query_extraction`: `history_sensitive` candidate
- `combine_subtract`: `late_split_candidate`
- `average_speed`: `distributed_shaping_candidate`
- `inverse_linear`: weak / unresolved

## Experiment 1: Clean Task Curation

Purpose:

Separate real geometry from task/oracle fragility.

Input:

- existing prompt banks
- oracle-labeled traces
- parser outputs

Procedure:

1. Build a task audit table for every prompt.
2. Mark each prompt as `clean`, `parser_fragile`, `ambiguous`, or `exclude`.
3. Recompute geometry only on `clean` prompts.

Metrics:

- oracle parse success
- outcome balance
- prompt-level correctness variance
- subfamily coverage

Success condition:

- each supported/candidate subfamily has at least `5` clean prompts and both outcomes represented

Expected artifacts:

- `outputs/task_audit/task_audit_table.csv`
- `outputs/task_audit/subfamily_clean_support.csv`
- `notes/task_audit_memo.md`

## Experiment 2: Mechanism-Specific Validators

Purpose:

Do not force every subfamily into one validation metric. Each mechanism label needs a matching validator.

Validators:

- `state_dominant`
  - branch-local state predicts outcome
  - branch collapse beats matched control
- `two_stage`
  - prebranch interaction is positive
  - branch-local state dominance follows interaction
- `history_sensitive`
  - same-location different-history angle is high
  - collapse can be weak
- `distributed_shaping`
  - no single dominant branch
  - phase contributions are spread

Success condition:

- each mechanism has at least one metric where it clearly beats its relevant null/control

Expected artifacts:

- `outputs/mechanism_validators/mechanism_validator_scores.csv`
- `outputs/mechanism_validators/mechanism_validator_heatmap.png`
- `notes/mechanism_validator_memo.md`

## Experiment 3: Task-Form Predictor

Purpose:

Test whether task form predicts geometry regime.

Candidate task-form variables:

- `answer_space_size`
- `answer_compression`
- `binary_gate`
- `propagation_depth`
- `ordering_completion`
- `query_extraction`
- `aggregation_or_ratio`
- `inverse_solve`

Target:

- `two_stage`
- `state_dominant`
- `history_sensitive`
- `distributed_shaping`
- `mixed_or_weak`

Procedure:

1. Construct task-form descriptors for every prompt and subfamily.
2. Aggregate descriptors by subfamily.
3. Fit simple interpretable rules before any complex model.

Success condition:

- rules explain supported regimes without contradicting candidate regimes

Expected artifacts:

- `outputs/task_form_predictor/task_form_descriptors.csv`
- `outputs/task_form_predictor/rule_table.csv`
- `outputs/task_form_predictor/task_form_to_regime.png`

## Experiment 4: Candidate Promotion

Purpose:

Move candidates into supported labels or demote them cleanly.

Priority order:

1. `query_extraction`
2. `combine_subtract`
3. `average_speed`
4. `inverse_linear`

Promotion requirements:

- `query_extraction`
  - keep high same-location angle
  - improve outcome balance with cleaner deterministic prompts
  - show stable history-sensitive behavior under one more embedding backbone
- `combine_subtract`
  - repeat local state/history tests
  - run mpnet revalidation
- `average_speed`
  - expand prompts
  - verify whether geometry is truly distributed across phases
- `inverse_linear`
  - expand prompts before assigning any sharper label

## Immediate Next Action

Implement `task_audit_table` first.

Reason:

The recent `query_extraction` issue showed that oracle/parser fragility can masquerade as model geometry. The next cycle should make task cleanliness visible before adding more traces.

Concrete next command target:

- add `src/tis/audit_task_cleanliness.py`
- generate `outputs/task_audit/task_audit_table.csv`
- generate `outputs/task_audit/subfamily_clean_support.csv`
- write `notes/task_audit_memo.md`
