# Prompt Stability Memo

## Purpose

Assess whether residual regimes are stable at the prompt level, not just at the family level.

## Overall

- mean within-prompt JS: 0.226
- mean same-family between-prompt JS: 0.337
- mean JS margin (between - within): 0.095
- mean JS ratio (within / between): 0.723
- mean centroid entropy: 1.555
- mean dominant residual-cluster share: 0.457
- mean dominant outcome share: 0.770

## Family summary

- `causal_micro_world` / `correct`: within_js=0.210, between_js=0.433, margin=0.237, ratio=0.454, cluster_share=0.497
- `causal_micro_world` / `incorrect`: within_js=0.238, between_js=0.450, margin=0.182, ratio=0.581, cluster_share=0.529
- `temporal_ordering` / `incorrect`: within_js=0.122, between_js=0.332, margin=0.181, ratio=0.360, cluster_share=0.429
- `commonsense_multihop` / `incorrect`: within_js=0.223, between_js=0.368, margin=0.173, ratio=0.579, cluster_share=0.484
- `commonsense_multihop` / `correct`: within_js=0.146, between_js=0.323, margin=0.150, ratio=0.495, cluster_share=0.336
- `symbolic_logic` / `correct`: within_js=0.157, between_js=0.291, margin=0.149, ratio=0.442, cluster_share=0.344
- `symbolic_logic` / `incorrect`: within_js=0.116, between_js=0.291, margin=0.119, ratio=0.495, cluster_share=0.458
- `arithmetic` / `correct`: within_js=0.203, between_js=0.235, margin=0.031, ratio=0.841, cluster_share=0.519
- `temporal_ordering` / `correct`: within_js=0.443, between_js=0.366, margin=-0.064, ratio=1.217, cluster_share=0.475
- `arithmetic` / `incorrect`: within_js=0.579, between_js=0.250, margin=-0.328, ratio=2.288, cluster_share=0.508
- `causal_micro_world` / `uncertain`: within_js=nan, between_js=0.394, margin=nan, ratio=nan, cluster_share=0.500

## Strongest prompt-level recurrence

- `causal_003` / `causal_micro_world` / `incorrect`: margin=0.290, ratio=0.349, entropy=1.906, dominant_cluster=3
- `causal_004` / `causal_micro_world` / `correct`: margin=0.279, ratio=0.268, entropy=1.356, dominant_cluster=0
- `temporal_003` / `temporal_ordering` / `incorrect`: margin=0.259, ratio=0.240, entropy=1.000, dominant_cluster=1
- `commonsense_004` / `commonsense_multihop` / `incorrect`: margin=0.250, ratio=0.503, entropy=1.795, dominant_cluster=2
- `temporal_004` / `temporal_ordering` / `incorrect`: margin=0.228, ratio=0.000, entropy=1.000, dominant_cluster=1

## Weakest prompt-level recurrence

- `arith_004` / `arithmetic` / `incorrect`: margin=-0.416, ratio=2.471, entropy=1.883, dominant_cluster=4
- `arith_002` / `arithmetic` / `incorrect`: margin=-0.241, ratio=2.104, entropy=1.252, dominant_cluster=4
- `temporal_003` / `temporal_ordering` / `correct`: margin=-0.235, ratio=1.691, entropy=1.743, dominant_cluster=2
- `arith_001` / `arithmetic` / `correct`: margin=-0.039, ratio=1.164, entropy=1.436, dominant_cluster=4
- `arith_002` / `arithmetic` / `correct`: margin=0.011, ratio=0.951, entropy=1.483, dominant_cluster=0

## Outcome consistency

- `causal_001` / `causal_micro_world`: dominant_outcome=incorrect, share=0.600, entropy=1.371
- `arith_002` / `arithmetic`: dominant_outcome=correct, share=0.600, entropy=0.971
- `arith_004` / `arithmetic`: dominant_outcome=correct, share=0.600, entropy=0.971
- `causal_003` / `causal_micro_world`: dominant_outcome=correct, share=0.600, entropy=0.971
- `commonsense_001` / `commonsense_multihop`: dominant_outcome=incorrect, share=0.600, entropy=0.971

## Reading

A positive JS margin means same-prompt trials are closer to each other than to different prompts in the same family and outcome. A lower JS ratio means tighter prompt-level recurrence. High centroid entropy means the prompt spreads across several residual regimes even when it recurs.
