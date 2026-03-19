# Prompt Recurrence Memo

## Purpose

Assess whether different prompts within the same task family converge toward similar residual-regime profiles.

## Global distance summary

- same_prompt=False, same_family=False, same_outcome=False: mean_js=0.498, mean_tv=0.588
- same_prompt=False, same_family=False, same_outcome=True: mean_js=0.500, mean_tv=0.586
- same_prompt=False, same_family=True, same_outcome=False: mean_js=0.444, mean_tv=0.538
- same_prompt=False, same_family=True, same_outcome=True: mean_js=0.442, mean_tv=0.534
- same_prompt=True, same_family=True, same_outcome=False: mean_js=0.299, mean_tv=0.402
- same_prompt=True, same_family=True, same_outcome=True: mean_js=0.269, mean_tv=0.354

## Same-prompt vs different-prompt inside family

- `arithmetic` / same_prompt=False, same_outcome=False: mean_js=0.367, mean_tv=0.493
- `arithmetic` / same_prompt=False, same_outcome=True: mean_js=0.383, mean_tv=0.501
- `arithmetic` / same_prompt=True, same_outcome=False: mean_js=0.243, mean_tv=0.365
- `arithmetic` / same_prompt=True, same_outcome=True: mean_js=0.192, mean_tv=0.303
- `causal_micro_world` / same_prompt=False, same_outcome=False: mean_js=0.469, mean_tv=0.564
- `causal_micro_world` / same_prompt=False, same_outcome=True: mean_js=0.423, mean_tv=0.523
- `causal_micro_world` / same_prompt=True, same_outcome=False: mean_js=0.305, mean_tv=0.387
- `causal_micro_world` / same_prompt=True, same_outcome=True: mean_js=0.292, mean_tv=0.369
- `commonsense_multihop` / same_prompt=False, same_outcome=False: mean_js=0.334, mean_tv=0.449
- `commonsense_multihop` / same_prompt=False, same_outcome=True: mean_js=0.324, mean_tv=0.440
- `commonsense_multihop` / same_prompt=True, same_outcome=False: mean_js=0.258, mean_tv=0.376
- `commonsense_multihop` / same_prompt=True, same_outcome=True: mean_js=0.252, mean_tv=0.370
- `symbolic_logic` / same_prompt=False, same_outcome=False: mean_js=0.564, mean_tv=0.615
- `symbolic_logic` / same_prompt=False, same_outcome=True: mean_js=0.576, mean_tv=0.616
- `symbolic_logic` / same_prompt=True, same_outcome=False: mean_js=0.318, mean_tv=0.390
- `symbolic_logic` / same_prompt=True, same_outcome=True: mean_js=0.291, mean_tv=0.341
- `temporal_ordering` / same_prompt=False, same_outcome=False: mean_js=0.489, mean_tv=0.575
- `temporal_ordering` / same_prompt=False, same_outcome=True: mean_js=0.501, mean_tv=0.583
- `temporal_ordering` / same_prompt=True, same_outcome=False: mean_js=0.412, mean_tv=0.537
- `temporal_ordering` / same_prompt=True, same_outcome=True: mean_js=0.303, mean_tv=0.377

## Family-level recurrence

- `arithmetic` / same_outcome=False: mean_js=0.355, mean_tv=0.480
- `arithmetic` / same_outcome=True: mean_js=0.364, mean_tv=0.480
- `causal_micro_world` / same_outcome=False: mean_js=0.454, mean_tv=0.548
- `causal_micro_world` / same_outcome=True: mean_js=0.408, mean_tv=0.506
- `commonsense_multihop` / same_outcome=False: mean_js=0.327, mean_tv=0.443
- `commonsense_multihop` / same_outcome=True: mean_js=0.315, mean_tv=0.431
- `symbolic_logic` / same_outcome=False: mean_js=0.543, mean_tv=0.596
- `symbolic_logic` / same_outcome=True: mean_js=0.542, mean_tv=0.583
- `temporal_ordering` / same_outcome=False: mean_js=0.483, mean_tv=0.572
- `temporal_ordering` / same_outcome=True: mean_js=0.476, mean_tv=0.557

## Nearest-neighbor purity

- `arithmetic`: same_family_nn=0.650, same_outcome_nn=0.400, nn_js=0.003
- `causal_micro_world`: same_family_nn=0.575, same_outcome_nn=0.450, nn_js=0.002
- `commonsense_multihop`: same_family_nn=0.350, same_outcome_nn=0.500, nn_js=0.007
- `symbolic_logic`: same_family_nn=0.625, same_outcome_nn=0.525, nn_js=0.005
- `temporal_ordering`: same_family_nn=0.375, same_outcome_nn=0.775, nn_js=0.015

## Reading

If same-family prompt pairs are consistently closer than cross-family pairs, and nearest-neighbor purity stays above chance, then residual regimes are not just artifacts of one prompt.
