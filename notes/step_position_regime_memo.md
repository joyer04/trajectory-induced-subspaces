# Step Position Regime Memo

## Purpose

Assess whether residual geometry changes across early, middle, and late reasoning transitions.

## Global phase means

- `early`: mean_static_projection=0.189, mean_residual_norm=0.978
- `middle`: mean_static_projection=0.192, mean_residual_norm=0.978
- `late`: mean_static_projection=0.207, mean_residual_norm=0.975

## Strongest failure-regime divergences by phase

- `arithmetic` / `middle`: js=0.419, tv=0.633, correct_mode=2, incorrect_mode=3, same_mode=False
- `arithmetic` / `early`: js=0.350, tv=0.611, correct_mode=2, incorrect_mode=0, same_mode=False
- `temporal_ordering` / `late`: js=0.192, tv=0.391, correct_mode=3, incorrect_mode=1, same_mode=False
- `causal_micro_world` / `early`: js=0.177, tv=0.366, correct_mode=4, incorrect_mode=1, same_mode=False
- `temporal_ordering` / `early`: js=0.100, tv=0.344, correct_mode=4, incorrect_mode=4, same_mode=True
- `temporal_ordering` / `middle`: js=0.098, tv=0.350, correct_mode=4, incorrect_mode=3, same_mode=False
- `causal_micro_world` / `late`: js=0.060, tv=0.204, correct_mode=3, incorrect_mode=3, same_mode=True
- `commonsense_multihop` / `late`: js=0.060, tv=0.265, correct_mode=1, incorrect_mode=3, same_mode=False
- `commonsense_multihop` / `early`: js=0.055, tv=0.234, correct_mode=1, incorrect_mode=1, same_mode=True
- `arithmetic` / `late`: js=0.052, tv=0.154, correct_mode=4, incorrect_mode=4, same_mode=True

## Most concentrated prompt-phase regimes

- `arith_003` / `arithmetic` / `early` / `incorrect`: cluster=2, share=1.000, entropy=-0.000
- `arith_003` / `arithmetic` / `middle` / `incorrect`: cluster=3, share=1.000, entropy=-0.000
- `arith_004` / `arithmetic` / `early` / `incorrect`: cluster=0, share=1.000, entropy=-0.000
- `causal_002` / `causal_micro_world` / `early` / `correct`: cluster=2, share=1.000, entropy=-0.000
- `causal_002` / `causal_micro_world` / `middle` / `incorrect`: cluster=4, share=1.000, entropy=-0.000
- `causal_003` / `causal_micro_world` / `early` / `correct`: cluster=1, share=1.000, entropy=-0.000
- `causal_003` / `causal_micro_world` / `early` / `incorrect`: cluster=1, share=1.000, entropy=-0.000
- `causal_003` / `causal_micro_world` / `late` / `incorrect`: cluster=3, share=1.000, entropy=-0.000
- `causal_003` / `causal_micro_world` / `middle` / `correct`: cluster=3, share=1.000, entropy=-0.000
- `causal_003` / `causal_micro_world` / `middle` / `incorrect`: cluster=3, share=1.000, entropy=-0.000

## Reading

If late-phase divergences dominate, then residual geometry may be tied to convergence and answer commitment. If early-phase divergences dominate, then the regime is being selected near the start of reasoning.
