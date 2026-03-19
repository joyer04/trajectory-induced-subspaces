# Prompt Recurrence Memo

## Purpose

Assess whether different prompts within the same task family converge toward similar residual-regime profiles.

## Global distance summary

- same_prompt=False, same_family=False, same_outcome=False: mean_js=0.492, mean_tv=0.597
- same_prompt=False, same_family=False, same_outcome=True: mean_js=0.520, mean_tv=0.609
- same_prompt=False, same_family=True, same_outcome=False: mean_js=0.421, mean_tv=0.533
- same_prompt=False, same_family=True, same_outcome=True: mean_js=0.386, mean_tv=0.475
- same_prompt=True, same_family=True, same_outcome=False: mean_js=0.239, mean_tv=0.362
- same_prompt=True, same_family=True, same_outcome=True: mean_js=0.285, mean_tv=0.376

## Same-prompt vs different-prompt inside family

- `arithmetic` / same_prompt=False, same_outcome=True: mean_js=0.296, mean_tv=0.347
- `arithmetic` / same_prompt=True, same_outcome=True: mean_js=0.336, mean_tv=0.383
- `causal_micro_world` / same_prompt=False, same_outcome=False: mean_js=0.649, mean_tv=0.721
- `causal_micro_world` / same_prompt=False, same_outcome=True: mean_js=0.589, mean_tv=0.686
- `causal_micro_world` / same_prompt=True, same_outcome=False: mean_js=0.345, mean_tv=0.485
- `causal_micro_world` / same_prompt=True, same_outcome=True: mean_js=0.328, mean_tv=0.428
- `commonsense_multihop` / same_prompt=False, same_outcome=False: mean_js=0.239, mean_tv=0.402
- `commonsense_multihop` / same_prompt=False, same_outcome=True: mean_js=0.140, mean_tv=0.212
- `commonsense_multihop` / same_prompt=True, same_outcome=False: mean_js=0.147, mean_tv=0.300
- `commonsense_multihop` / same_prompt=True, same_outcome=True: mean_js=0.220, mean_tv=0.324
- `symbolic_logic` / same_prompt=False, same_outcome=False: mean_js=0.551, mean_tv=0.607
- `symbolic_logic` / same_prompt=False, same_outcome=True: mean_js=0.527, mean_tv=0.595
- `symbolic_logic` / same_prompt=True, same_outcome=False: mean_js=0.189, mean_tv=0.276
- `symbolic_logic` / same_prompt=True, same_outcome=True: mean_js=0.284, mean_tv=0.395
- `temporal_ordering` / same_prompt=False, same_outcome=False: mean_js=0.225, mean_tv=0.371
- `temporal_ordering` / same_prompt=False, same_outcome=True: mean_js=0.349, mean_tv=0.500
- `temporal_ordering` / same_prompt=True, same_outcome=False: mean_js=0.262, mean_tv=0.377
- `temporal_ordering` / same_prompt=True, same_outcome=True: mean_js=0.247, mean_tv=0.367

## Family-level recurrence

- `arithmetic` / same_outcome=True: mean_js=0.314, mean_tv=0.363
- `causal_micro_world` / same_outcome=False: mean_js=0.522, mean_tv=0.623
- `causal_micro_world` / same_outcome=True: mean_js=0.465, mean_tv=0.563
- `commonsense_multihop` / same_outcome=False: mean_js=0.215, mean_tv=0.375
- `commonsense_multihop` / same_outcome=True: mean_js=0.198, mean_tv=0.293
- `symbolic_logic` / same_outcome=False: mean_js=0.379, mean_tv=0.450
- `symbolic_logic` / same_outcome=True: mean_js=0.426, mean_tv=0.512
- `temporal_ordering` / same_outcome=False: mean_js=0.242, mean_tv=0.374
- `temporal_ordering` / same_outcome=True: mean_js=0.304, mean_tv=0.441

## Nearest-neighbor purity

- `arithmetic`: same_family_nn=0.700, same_outcome_nn=0.900, nn_js=0.028
- `causal_micro_world`: same_family_nn=0.400, same_outcome_nn=0.700, nn_js=0.053
- `commonsense_multihop`: same_family_nn=0.500, same_outcome_nn=0.500, nn_js=0.027
- `symbolic_logic`: same_family_nn=0.500, same_outcome_nn=0.300, nn_js=0.014
- `temporal_ordering`: same_family_nn=0.100, same_outcome_nn=0.600, nn_js=0.010

## Reading

If same-family prompt pairs are consistently closer than cross-family pairs, and nearest-neighbor purity stays above chance, then residual regimes are not just artifacts of one prompt.
