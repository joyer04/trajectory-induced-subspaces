# Prompt Stability Memo

## Purpose

Assess whether residual regimes are stable at the prompt level, not just at the family level.

## Overall

- mean within-prompt JS: 0.173
- mean same-family between-prompt JS: 0.361
- mean JS margin (between - within): 0.190
- mean JS ratio (within / between): 0.501
- mean centroid entropy: 1.496
- mean dominant residual-cluster share: 0.500
- mean dominant outcome share: 0.743

## Family summary

- `causal_micro_world` / `correct`: within_js=0.079, between_js=0.434, margin=0.354, ratio=0.167, cluster_share=0.509
- `causal_micro_world` / `incorrect`: within_js=0.132, between_js=0.434, margin=0.352, ratio=0.246, cluster_share=0.541
- `temporal_ordering` / `incorrect`: within_js=0.184, between_js=0.425, margin=0.241, ratio=0.463, cluster_share=0.499
- `arithmetic` / `correct`: within_js=0.191, between_js=0.420, margin=0.228, ratio=0.489, cluster_share=0.429
- `commonsense_multihop` / `correct`: within_js=0.115, between_js=0.298, margin=0.183, ratio=0.391, cluster_share=0.478
- `symbolic_logic` / `incorrect`: within_js=0.108, between_js=0.249, margin=0.141, ratio=0.434, cluster_share=0.568
- `arithmetic` / `incorrect`: within_js=0.365, between_js=0.490, margin=0.125, ratio=0.822, cluster_share=0.581
- `symbolic_logic` / `correct`: within_js=0.127, between_js=0.249, margin=0.122, ratio=0.520, cluster_share=0.552
- `temporal_ordering` / `correct`: within_js=0.278, between_js=0.384, margin=0.106, ratio=0.709, cluster_share=0.469
- `commonsense_multihop` / `incorrect`: within_js=0.265, between_js=0.298, margin=0.032, ratio=0.915, cluster_share=0.409

## Strongest prompt-level recurrence

- `causal_002` / `causal_micro_world` / `correct`: margin=0.518, ratio=0.046, entropy=1.571, dominant_cluster=3
- `temporal_004` / `temporal_ordering` / `incorrect`: margin=0.481, ratio=0.122, entropy=1.177, dominant_cluster=3
- `arith_004` / `arithmetic` / `correct`: margin=0.450, ratio=0.242, entropy=1.878, dominant_cluster=0
- `causal_002` / `causal_micro_world` / `incorrect`: margin=0.417, ratio=0.233, entropy=1.556, dominant_cluster=3
- `causal_003` / `causal_micro_world` / `incorrect`: margin=0.373, ratio=0.000, entropy=0.918, dominant_cluster=3

## Weakest prompt-level recurrence

- `arith_003` / `arithmetic` / `incorrect`: margin=-0.072, ratio=1.187, entropy=1.252, dominant_cluster=2
- `commonsense_002` / `commonsense_multihop` / `incorrect`: margin=-0.051, ratio=1.196, entropy=1.851, dominant_cluster=1
- `commonsense_004` / `commonsense_multihop` / `incorrect`: margin=0.022, ratio=0.923, entropy=1.736, dominant_cluster=3
- `temporal_001` / `temporal_ordering` / `correct`: margin=0.025, ratio=0.943, entropy=1.782, dominant_cluster=0
- `commonsense_001` / `commonsense_multihop` / `incorrect`: margin=0.026, ratio=0.909, entropy=1.919, dominant_cluster=3

## Outcome consistency

- `causal_002` / `causal_micro_world`: dominant_outcome=correct, share=0.533, entropy=0.997
- `logic_001` / `symbolic_logic`: dominant_outcome=correct, share=0.533, entropy=0.997
- `temporal_003` / `temporal_ordering`: dominant_outcome=incorrect, share=0.533, entropy=0.997
- `arith_004` / `arithmetic`: dominant_outcome=incorrect, share=0.600, entropy=0.971
- `causal_003` / `causal_micro_world`: dominant_outcome=correct, share=0.600, entropy=0.971

## Reading

A positive JS margin means same-prompt trials are closer to each other than to different prompts in the same family and outcome. A lower JS ratio means tighter prompt-level recurrence. High centroid entropy means the prompt spreads across several residual regimes even when it recurs.
