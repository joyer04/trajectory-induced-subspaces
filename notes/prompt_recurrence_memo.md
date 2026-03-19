# Prompt Recurrence Memo

## Purpose

Assess whether different prompts within the same task family converge toward similar residual-regime profiles.

## Global distance summary

- same_family=False, same_outcome=False: mean_js=0.435, mean_tv=0.530
- same_family=False, same_outcome=True: mean_js=0.443, mean_tv=0.540
- same_family=True, same_outcome=False: mean_js=0.427, mean_tv=0.521
- same_family=True, same_outcome=True: mean_js=0.414, mean_tv=0.511

## Family-level recurrence

- `arithmetic` / same_outcome=False: mean_js=0.364, mean_tv=0.472
- `arithmetic` / same_outcome=True: mean_js=0.384, mean_tv=0.500
- `causal_micro_world` / same_outcome=False: mean_js=0.458, mean_tv=0.523
- `causal_micro_world` / same_outcome=True: mean_js=0.465, mean_tv=0.538
- `commonsense_multihop` / same_outcome=False: mean_js=0.332, mean_tv=0.451
- `commonsense_multihop` / same_outcome=True: mean_js=0.354, mean_tv=0.476
- `symbolic_logic` / same_outcome=False: mean_js=0.477, mean_tv=0.563
- `symbolic_logic` / same_outcome=True: mean_js=0.507, mean_tv=0.596
- `temporal_ordering` / same_outcome=False: mean_js=0.477, mean_tv=0.577
- `temporal_ordering` / same_outcome=True: mean_js=0.385, mean_tv=0.466

## Nearest-neighbor purity

- `arithmetic`: same_family_nn=0.500, same_outcome_nn=0.750, nn_js=0.015
- `causal_micro_world`: same_family_nn=0.300, same_outcome_nn=0.550, nn_js=0.011
- `commonsense_multihop`: same_family_nn=0.250, same_outcome_nn=0.300, nn_js=0.019
- `symbolic_logic`: same_family_nn=0.150, same_outcome_nn=0.500, nn_js=0.009
- `temporal_ordering`: same_family_nn=0.200, same_outcome_nn=0.450, nn_js=0.029

## Reading

If same-family prompt pairs are consistently closer than cross-family pairs, and nearest-neighbor purity stays above chance, then residual regimes are not just artifacts of one prompt.
