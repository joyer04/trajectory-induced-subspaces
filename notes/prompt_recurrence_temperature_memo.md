# Prompt Recurrence Memo

## Purpose

Assess whether different prompts within the same task family converge toward similar residual-regime profiles.

## Global distance summary

- same_prompt=False, same_family=False, same_outcome=False: mean_js=0.510, mean_tv=0.594
- same_prompt=False, same_family=False, same_outcome=True: mean_js=0.498, mean_tv=0.585
- same_prompt=False, same_family=True, same_outcome=False: mean_js=0.398, mean_tv=0.506
- same_prompt=False, same_family=True, same_outcome=True: mean_js=0.361, mean_tv=0.470
- same_prompt=True, same_family=True, same_outcome=False: mean_js=0.185, mean_tv=0.297
- same_prompt=True, same_family=True, same_outcome=True: mean_js=0.170, mean_tv=0.259

## Same-prompt vs different-prompt inside family

- `arithmetic` / same_prompt=False, same_outcome=False: mean_js=0.604, mean_tv=0.669
- `arithmetic` / same_prompt=False, same_outcome=True: mean_js=0.397, mean_tv=0.487
- `arithmetic` / same_prompt=True, same_outcome=False: mean_js=0.260, mean_tv=0.404
- `arithmetic` / same_prompt=True, same_outcome=True: mean_js=0.209, mean_tv=0.287
- `causal_micro_world` / same_prompt=False, same_outcome=False: mean_js=0.458, mean_tv=0.572
- `causal_micro_world` / same_prompt=False, same_outcome=True: mean_js=0.431, mean_tv=0.539
- `causal_micro_world` / same_prompt=True, same_outcome=False: mean_js=0.092, mean_tv=0.174
- `causal_micro_world` / same_prompt=True, same_outcome=True: mean_js=0.100, mean_tv=0.190
- `commonsense_multihop` / same_prompt=False, same_outcome=False: mean_js=0.313, mean_tv=0.430
- `commonsense_multihop` / same_prompt=False, same_outcome=True: mean_js=0.302, mean_tv=0.419
- `commonsense_multihop` / same_prompt=True, same_outcome=False: mean_js=0.259, mean_tv=0.383
- `commonsense_multihop` / same_prompt=True, same_outcome=True: mean_js=0.222, mean_tv=0.329
- `symbolic_logic` / same_prompt=False, same_outcome=False: mean_js=0.237, mean_tv=0.373
- `symbolic_logic` / same_prompt=False, same_outcome=True: mean_js=0.250, mean_tv=0.387
- `symbolic_logic` / same_prompt=True, same_outcome=False: mean_js=0.117, mean_tv=0.230
- `symbolic_logic` / same_prompt=True, same_outcome=True: mean_js=0.100, mean_tv=0.201
- `temporal_ordering` / same_prompt=False, same_outcome=False: mean_js=0.444, mean_tv=0.536
- `temporal_ordering` / same_prompt=False, same_outcome=True: mean_js=0.418, mean_tv=0.516
- `temporal_ordering` / same_prompt=True, same_outcome=False: mean_js=0.258, mean_tv=0.372
- `temporal_ordering` / same_prompt=True, same_outcome=True: mean_js=0.193, mean_tv=0.267

## Family-level recurrence

- `arithmetic` / same_outcome=False: mean_js=0.553, mean_tv=0.630
- `arithmetic` / same_outcome=True: mean_js=0.345, mean_tv=0.432
- `causal_micro_world` / same_outcome=False: mean_js=0.392, mean_tv=0.500
- `causal_micro_world` / same_outcome=True: mean_js=0.334, mean_tv=0.437
- `commonsense_multihop` / same_outcome=False: mean_js=0.304, mean_tv=0.422
- `commonsense_multihop` / same_outcome=True: mean_js=0.278, mean_tv=0.392
- `symbolic_logic` / same_outcome=False: mean_js=0.210, mean_tv=0.341
- `symbolic_logic` / same_outcome=True: mean_js=0.212, mean_tv=0.340
- `temporal_ordering` / same_outcome=False: mean_js=0.413, mean_tv=0.509
- `temporal_ordering` / same_outcome=True: mean_js=0.349, mean_tv=0.439

## Nearest-neighbor purity

- `arithmetic`: same_family_nn=0.700, same_outcome_nn=0.767, nn_js=0.008
- `causal_micro_world`: same_family_nn=0.783, same_outcome_nn=0.650, nn_js=0.001
- `commonsense_multihop`: same_family_nn=0.483, same_outcome_nn=0.583, nn_js=0.002
- `symbolic_logic`: same_family_nn=0.700, same_outcome_nn=0.433, nn_js=0.001
- `temporal_ordering`: same_family_nn=0.633, same_outcome_nn=0.483, nn_js=0.005

## Reading

If same-family prompt pairs are consistently closer than cross-family pairs, and nearest-neighbor purity stays above chance, then residual regimes are not just artifacts of one prompt.
