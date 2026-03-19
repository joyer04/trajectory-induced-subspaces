# Prompt Recurrence Significance Memo

## Purpose

Test whether prompt-level recurrence margins remain above a shuffled-label baseline within each family/outcome group.

## Summary

- `symbolic_logic` / `correct`: prompt_mean_margin=0.350, pairwise_margin=0.329, CI=[0.258, 0.424], positive_prompt_share=1.000, perm_p=0.001, z=4.850
- `symbolic_logic` / `incorrect`: prompt_mean_margin=0.248, pairwise_margin=0.254, CI=[0.131, 0.378], positive_prompt_share=1.000, perm_p=0.001, z=4.374
- `temporal_ordering` / `incorrect`: prompt_mean_margin=0.192, pairwise_margin=0.234, CI=[0.070, 0.306], positive_prompt_share=0.857, perm_p=0.001, z=5.435
- `arithmetic` / `correct`: prompt_mean_margin=0.151, pairwise_margin=0.229, CI=[0.065, 0.239], positive_prompt_share=0.875, perm_p=0.001, z=5.130
- `causal_micro_world` / `correct`: prompt_mean_margin=0.182, pairwise_margin=0.201, CI=[0.082, 0.322], positive_prompt_share=1.000, perm_p=0.001, z=4.566
- `commonsense_multihop` / `correct`: prompt_mean_margin=0.034, pairwise_margin=0.086, CI=[-0.017, 0.083], positive_prompt_share=0.571, perm_p=0.028, z=1.854
- `commonsense_multihop` / `incorrect`: prompt_mean_margin=0.048, pairwise_margin=0.060, CI=[-0.021, 0.115], positive_prompt_share=0.667, perm_p=0.060, z=1.574
- `arithmetic` / `incorrect`: prompt_mean_margin=0.113, pairwise_margin=0.084, CI=[-0.024, 0.257], positive_prompt_share=0.600, perm_p=0.086, z=1.447
- `temporal_ordering` / `correct`: prompt_mean_margin=0.270, pairwise_margin=0.063, CI=[-0.014, 0.469], positive_prompt_share=0.667, perm_p=0.250, z=0.692
- `causal_micro_world` / `incorrect`: prompt_mean_margin=0.061, pairwise_margin=0.006, CI=[-0.048, 0.155], positive_prompt_share=0.800, perm_p=0.452, z=0.072

## Strongest support

- `symbolic_logic` / `correct`: pairwise_margin=0.329, perm_p=0.001
- `symbolic_logic` / `incorrect`: pairwise_margin=0.254, perm_p=0.001
- `temporal_ordering` / `incorrect`: pairwise_margin=0.234, perm_p=0.001
- `arithmetic` / `correct`: pairwise_margin=0.229, perm_p=0.001
- `causal_micro_world` / `correct`: pairwise_margin=0.201, perm_p=0.001

## Weakest support

- `causal_micro_world` / `incorrect`: pairwise_margin=0.006, perm_p=0.452
- `commonsense_multihop` / `incorrect`: pairwise_margin=0.060, perm_p=0.060
- `temporal_ordering` / `correct`: pairwise_margin=0.063, perm_p=0.250
- `arithmetic` / `incorrect`: pairwise_margin=0.084, perm_p=0.086
- `commonsense_multihop` / `correct`: pairwise_margin=0.086, perm_p=0.028

## Reading

The bootstrap interval tracks the mean prompt-level margin, while the permutation test compares the observed pairwise margin against shuffled prompt labels. Positive margins with low permutation p-values indicate that same-prompt residual profiles are tighter than expected under random prompt reassignment. Negative margins or wide confidence intervals indicate unstable or multi-regime prompts.
