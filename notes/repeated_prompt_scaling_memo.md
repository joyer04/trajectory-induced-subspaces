# Repeated Prompt Scaling Memo

## Purpose

Compare the smaller repeated-prompt experiment (2 prompts/family x 5 repeats) against the larger repeated-prompt experiment (4 prompts/family x 5 repeats).

## Global same-prompt advantage

- 2x5: same_prompt_js=0.285, diff_prompt_js=0.386, gap=0.101
- 4x5: same_prompt_js=0.203, diff_prompt_js=0.325, gap=0.121

## Family-level same-prompt advantage

- `causal_micro_world`: 2x5_gap=0.261, 4x5_gap=0.238, delta=-0.023
- `commonsense_multihop`: 2x5_gap=-0.081, 4x5_gap=0.166, delta=0.246
- `temporal_ordering`: 2x5_gap=0.102, 4x5_gap=0.120, delta=0.018
- `symbolic_logic`: 2x5_gap=0.243, 4x5_gap=0.108, delta=-0.135
- `arithmetic`: 2x5_gap=-0.040, 4x5_gap=0.019, delta=0.058

## Nearest-neighbor shifts

- `arithmetic`: same_family_nn 0.700 -> 0.800, same_outcome_nn 0.900 -> 0.750
- `symbolic_logic`: same_family_nn 0.500 -> 0.700, same_outcome_nn 0.300 -> 0.700
- `causal_micro_world`: same_family_nn 0.400 -> 0.550, same_outcome_nn 0.700 -> 0.450
- `temporal_ordering`: same_family_nn 0.100 -> 0.550, same_outcome_nn 0.600 -> 0.450
- `commonsense_multihop`: same_family_nn 0.500 -> 0.500, same_outcome_nn 0.500 -> 0.550

## Reading

If the 4x5 run keeps or increases the same-prompt advantage over different prompts within the same family then the residual regime signal is less likely to be a fluke of tiny prompt support.
