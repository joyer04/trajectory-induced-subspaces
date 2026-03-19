# Prompt Recurrence Significance Memo

## Purpose

Test whether prompt-level recurrence margins remain above a shuffled-label baseline within each family/outcome group.

## Summary

- `causal_micro_world` / `incorrect`: prompt_mean_margin=0.352, pairwise_margin=0.399, CI=[0.265, 0.417], positive_prompt_share=1.000, perm_p=0.001, z=10.176
- `temporal_ordering` / `incorrect`: prompt_mean_margin=0.241, pairwise_margin=0.347, CI=[0.125, 0.394], positive_prompt_share=1.000, perm_p=0.001, z=9.868
- `causal_micro_world` / `correct`: prompt_mean_margin=0.354, pairwise_margin=0.303, CI=[0.272, 0.463], positive_prompt_share=1.000, perm_p=0.001, z=13.271
- `arithmetic` / `correct`: prompt_mean_margin=0.228, pairwise_margin=0.189, CI=[0.096, 0.372], positive_prompt_share=1.000, perm_p=0.001, z=11.404
- `symbolic_logic` / `incorrect`: prompt_mean_margin=0.141, pairwise_margin=0.158, CI=[0.071, 0.220], positive_prompt_share=1.000, perm_p=0.001, z=7.511
- `symbolic_logic` / `correct`: prompt_mean_margin=0.122, pairwise_margin=0.143, CI=[0.082, 0.166], positive_prompt_share=1.000, perm_p=0.001, z=7.045
- `commonsense_multihop` / `incorrect`: prompt_mean_margin=0.032, pairwise_margin=0.071, CI=[-0.031, 0.105], positive_prompt_share=0.750, perm_p=0.002, z=3.635
- `commonsense_multihop` / `correct`: prompt_mean_margin=0.183, pairwise_margin=0.086, CI=[0.108, 0.231], positive_prompt_share=1.000, perm_p=0.005, z=3.116
- `temporal_ordering` / `correct`: prompt_mean_margin=0.106, pairwise_margin=0.071, CI=[0.025, 0.152], positive_prompt_share=1.000, perm_p=0.016, z=2.772
- `arithmetic` / `incorrect`: prompt_mean_margin=0.125, pairwise_margin=0.508, CI=[-0.072, 0.323], positive_prompt_share=0.500, perm_p=0.021, z=3.450

## Strongest support

- `causal_micro_world` / `incorrect`: pairwise_margin=0.399, perm_p=0.001
- `temporal_ordering` / `incorrect`: pairwise_margin=0.347, perm_p=0.001
- `causal_micro_world` / `correct`: pairwise_margin=0.303, perm_p=0.001
- `arithmetic` / `correct`: pairwise_margin=0.189, perm_p=0.001
- `symbolic_logic` / `incorrect`: pairwise_margin=0.158, perm_p=0.001

## Weakest support

- `commonsense_multihop` / `incorrect`: pairwise_margin=0.071, perm_p=0.002
- `temporal_ordering` / `correct`: pairwise_margin=0.071, perm_p=0.016
- `commonsense_multihop` / `correct`: pairwise_margin=0.086, perm_p=0.005
- `symbolic_logic` / `correct`: pairwise_margin=0.143, perm_p=0.001
- `symbolic_logic` / `incorrect`: pairwise_margin=0.158, perm_p=0.001

## Reading

The bootstrap interval tracks the mean prompt-level margin, while the permutation test compares the observed pairwise margin against shuffled prompt labels. Positive margins with low permutation p-values indicate that same-prompt residual profiles are tighter than expected under random prompt reassignment. Negative margins or wide confidence intervals indicate unstable or multi-regime prompts.
