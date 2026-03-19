# Prompt Recurrence Memo

## Purpose

Assess whether different prompts within the same task family converge toward similar residual-regime profiles.

## Global distance summary

- same_prompt=False, same_family=False, same_outcome=False: mean_js=0.526, mean_tv=0.610
- same_prompt=False, same_family=False, same_outcome=True: mean_js=0.496, mean_tv=0.583
- same_prompt=False, same_family=True, same_outcome=False: mean_js=0.344, mean_tv=0.450
- same_prompt=False, same_family=True, same_outcome=True: mean_js=0.325, mean_tv=0.426
- same_prompt=True, same_family=True, same_outcome=False: mean_js=0.282, mean_tv=0.400
- same_prompt=True, same_family=True, same_outcome=True: mean_js=0.203, mean_tv=0.296

## Same-prompt vs different-prompt inside family

- `arithmetic` / same_prompt=False, same_outcome=False: mean_js=0.376, mean_tv=0.480
- `arithmetic` / same_prompt=False, same_outcome=True: mean_js=0.233, mean_tv=0.328
- `arithmetic` / same_prompt=True, same_outcome=False: mean_js=0.381, mean_tv=0.533
- `arithmetic` / same_prompt=True, same_outcome=True: mean_js=0.214, mean_tv=0.292
- `causal_micro_world` / same_prompt=False, same_outcome=False: mean_js=0.389, mean_tv=0.497
- `causal_micro_world` / same_prompt=False, same_outcome=True: mean_js=0.439, mean_tv=0.538
- `causal_micro_world` / same_prompt=True, same_outcome=False: mean_js=0.285, mean_tv=0.403
- `causal_micro_world` / same_prompt=True, same_outcome=True: mean_js=0.201, mean_tv=0.311
- `commonsense_multihop` / same_prompt=False, same_outcome=False: mean_js=0.265, mean_tv=0.401
- `commonsense_multihop` / same_prompt=False, same_outcome=True: mean_js=0.377, mean_tv=0.491
- `commonsense_multihop` / same_prompt=True, same_outcome=False: mean_js=0.240, mean_tv=0.344
- `commonsense_multihop` / same_prompt=True, same_outcome=True: mean_js=0.212, mean_tv=0.320
- `symbolic_logic` / same_prompt=False, same_outcome=False: mean_js=0.307, mean_tv=0.415
- `symbolic_logic` / same_prompt=False, same_outcome=True: mean_js=0.282, mean_tv=0.384
- `symbolic_logic` / same_prompt=True, same_outcome=False: mean_js=0.209, mean_tv=0.321
- `symbolic_logic` / same_prompt=True, same_outcome=True: mean_js=0.175, mean_tv=0.283
- `temporal_ordering` / same_prompt=False, same_outcome=False: mean_js=0.389, mean_tv=0.464
- `temporal_ordering` / same_prompt=False, same_outcome=True: mean_js=0.327, mean_tv=0.423
- `temporal_ordering` / same_prompt=True, same_outcome=False: mean_js=0.339, mean_tv=0.453
- `temporal_ordering` / same_prompt=True, same_outcome=True: mean_js=0.207, mean_tv=0.272

## Family-level recurrence

- `arithmetic` / same_outcome=False: mean_js=0.377, mean_tv=0.490
- `arithmetic` / same_outcome=True: mean_js=0.228, mean_tv=0.320
- `causal_micro_world` / same_outcome=False: mean_js=0.371, mean_tv=0.481
- `causal_micro_world` / same_outcome=True: mean_js=0.380, mean_tv=0.482
- `commonsense_multihop` / same_outcome=False: mean_js=0.261, mean_tv=0.392
- `commonsense_multihop` / same_outcome=True: mean_js=0.334, mean_tv=0.447
- `symbolic_logic` / same_outcome=False: mean_js=0.287, mean_tv=0.396
- `symbolic_logic` / same_outcome=True: mean_js=0.259, mean_tv=0.362
- `temporal_ordering` / same_outcome=False: mean_js=0.382, mean_tv=0.463
- `temporal_ordering` / same_outcome=True: mean_js=0.294, mean_tv=0.381

## Nearest-neighbor purity

- `arithmetic`: same_family_nn=0.800, same_outcome_nn=0.750, nn_js=0.005
- `causal_micro_world`: same_family_nn=0.550, same_outcome_nn=0.450, nn_js=0.020
- `commonsense_multihop`: same_family_nn=0.500, same_outcome_nn=0.550, nn_js=0.023
- `symbolic_logic`: same_family_nn=0.700, same_outcome_nn=0.700, nn_js=0.003
- `temporal_ordering`: same_family_nn=0.550, same_outcome_nn=0.450, nn_js=0.017

## Reading

If same-family prompt pairs are consistently closer than cross-family pairs, and nearest-neighbor purity stays above chance, then residual regimes are not just artifacts of one prompt.
