# Prompt Recurrence Significance Memo

## Purpose

Test whether prompt-level recurrence margins remain above a shuffled-label baseline within each family/outcome group.

## Summary

- `causal_micro_world` / `correct`: prompt_mean_margin=0.237, pairwise_margin=0.244, CI=[0.208, 0.279], positive_prompt_share=1.000, perm_p=0.003, z=3.704
- `commonsense_multihop` / `incorrect`: prompt_mean_margin=0.173, pairwise_margin=0.209, CI=[0.092, 0.250], positive_prompt_share=1.000, perm_p=0.005, z=3.743
- `temporal_ordering` / `incorrect`: prompt_mean_margin=0.181, pairwise_margin=0.159, CI=[0.054, 0.259], positive_prompt_share=1.000, perm_p=0.005, z=2.813
- `symbolic_logic` / `incorrect`: prompt_mean_margin=0.119, pairwise_margin=0.197, CI=[0.090, 0.143], positive_prompt_share=1.000, perm_p=0.013, z=2.579
- `causal_micro_world` / `incorrect`: prompt_mean_margin=0.182, pairwise_margin=0.214, CI=[0.073, 0.290], positive_prompt_share=1.000, perm_p=0.046, z=2.055
- `arithmetic` / `correct`: prompt_mean_margin=0.031, pairwise_margin=0.040, CI=[-0.025, 0.104], positive_prompt_share=0.750, perm_p=0.143, z=1.139
- `temporal_ordering` / `correct`: prompt_mean_margin=-0.064, pairwise_margin=0.088, CI=[-0.235, 0.107], positive_prompt_share=0.500, perm_p=0.212, z=0.841
- `symbolic_logic` / `correct`: prompt_mean_margin=0.149, pairwise_margin=-0.027, CI=[0.091, 0.228], positive_prompt_share=1.000, perm_p=0.573, z=-0.389
- `arithmetic` / `incorrect`: prompt_mean_margin=-0.328, pairwise_margin=-0.186, CI=[-0.416, -0.241], positive_prompt_share=0.000, perm_p=0.678, z=-0.706
- `commonsense_multihop` / `correct`: prompt_mean_margin=0.150, pairwise_margin=-0.045, CI=[0.122, 0.177], positive_prompt_share=1.000, perm_p=0.971, z=-1.156

## Strongest support

- `causal_micro_world` / `correct`: pairwise_margin=0.244, perm_p=0.003
- `commonsense_multihop` / `incorrect`: pairwise_margin=0.209, perm_p=0.005
- `temporal_ordering` / `incorrect`: pairwise_margin=0.159, perm_p=0.005
- `symbolic_logic` / `incorrect`: pairwise_margin=0.197, perm_p=0.013
- `causal_micro_world` / `incorrect`: pairwise_margin=0.214, perm_p=0.046

## Weakest support

- `arithmetic` / `incorrect`: pairwise_margin=-0.186, perm_p=0.678
- `commonsense_multihop` / `correct`: pairwise_margin=-0.045, perm_p=0.971
- `symbolic_logic` / `correct`: pairwise_margin=-0.027, perm_p=0.573
- `arithmetic` / `correct`: pairwise_margin=0.040, perm_p=0.143
- `temporal_ordering` / `correct`: pairwise_margin=0.088, perm_p=0.212

## Reading

The bootstrap interval tracks the mean prompt-level margin, while the permutation test compares the observed pairwise margin against shuffled prompt labels. Positive margins with low permutation p-values indicate that same-prompt residual profiles are tighter than expected under random prompt reassignment. Negative margins or wide confidence intervals indicate unstable or multi-regime prompts.
