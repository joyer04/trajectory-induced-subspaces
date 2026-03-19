# Prompt Stability Memo

## Purpose

Assess whether residual regimes are stable at the prompt level, not just at the family level.

## Overall

- mean within-prompt JS: 0.276
- mean same-family between-prompt JS: 0.435
- mean JS margin (between - within): 0.162
- mean JS ratio (within / between): 0.654
- mean centroid entropy: 1.601
- mean dominant residual-cluster share: 0.458
- mean dominant outcome share: 0.740

## Family summary

- `symbolic_logic` / `correct`: within_js=0.214, between_js=0.579, margin=0.350, ratio=0.361, cluster_share=0.452
- `temporal_ordering` / `correct`: within_js=0.232, between_js=0.480, margin=0.270, ratio=0.459, cluster_share=0.525
- `symbolic_logic` / `incorrect`: within_js=0.323, between_js=0.571, margin=0.248, ratio=0.566, cluster_share=0.497
- `temporal_ordering` / `incorrect`: within_js=0.308, between_js=0.500, margin=0.192, ratio=0.634, cluster_share=0.468
- `causal_micro_world` / `correct`: within_js=0.245, between_js=0.423, margin=0.182, ratio=0.581, cluster_share=0.460
- `arithmetic` / `correct`: within_js=0.233, between_js=0.384, margin=0.151, ratio=0.598, cluster_share=0.418
- `arithmetic` / `incorrect`: within_js=0.272, between_js=0.380, margin=0.113, ratio=0.691, cluster_share=0.412
- `causal_micro_world` / `incorrect`: within_js=0.372, between_js=0.410, margin=0.061, ratio=0.856, cluster_share=0.543
- `commonsense_multihop` / `incorrect`: within_js=0.270, between_js=0.317, margin=0.048, ratio=0.847, cluster_share=0.414
- `commonsense_multihop` / `correct`: within_js=0.290, between_js=0.324, margin=0.034, ratio=0.899, cluster_share=0.408

## Strongest prompt-level recurrence

- `logic_003` / `symbolic_logic` / `incorrect`: margin=0.580, ratio=0.023, entropy=0.991, dominant_cluster=2
- `causal_003` / `causal_micro_world` / `correct`: margin=0.526, ratio=0.000, entropy=1.585, dominant_cluster=0
- `logic_001` / `symbolic_logic` / `correct`: margin=0.476, ratio=0.000, entropy=1.585, dominant_cluster=1
- `temporal_001` / `temporal_ordering` / `correct`: margin=0.469, ratio=0.000, entropy=1.585, dominant_cluster=1
- `temporal_008` / `temporal_ordering` / `incorrect`: margin=0.417, ratio=0.290, entropy=1.258, dominant_cluster=1

## Weakest prompt-level recurrence

- `causal_007` / `causal_micro_world` / `incorrect`: margin=-0.145, ratio=1.316, entropy=1.459, dominant_cluster=1
- `commonsense_008` / `commonsense_multihop` / `incorrect`: margin=-0.089, ratio=1.270, entropy=1.945, dominant_cluster=3
- `commonsense_003` / `commonsense_multihop` / `correct`: margin=-0.079, ratio=1.227, entropy=1.384, dominant_cluster=3
- `arith_004` / `arithmetic` / `incorrect`: margin=-0.078, ratio=1.196, entropy=1.864, dominant_cluster=0
- `arith_001` / `arithmetic` / `correct`: margin=-0.046, ratio=1.112, entropy=0.918, dominant_cluster=0

## Outcome consistency

- `arith_001` / `arithmetic`: dominant_outcome=incorrect, share=0.600, entropy=0.971
- `arith_003` / `arithmetic`: dominant_outcome=incorrect, share=0.600, entropy=0.971
- `arith_004` / `arithmetic`: dominant_outcome=incorrect, share=0.600, entropy=0.971
- `arith_005` / `arithmetic`: dominant_outcome=correct, share=0.600, entropy=0.971
- `arith_008` / `arithmetic`: dominant_outcome=correct, share=0.600, entropy=0.971

## Reading

A positive JS margin means same-prompt trials are closer to each other than to different prompts in the same family and outcome. A lower JS ratio means tighter prompt-level recurrence. High centroid entropy means the prompt spreads across several residual regimes even when it recurs.
