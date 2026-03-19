# Phase Predictability Memo

## Purpose

Estimate how early regime information predicts later paths and final outcome.

## Outcome predictability

- `arithmetic` / `early_middle`: accuracy=0.817, balanced_accuracy=0.562
- `arithmetic` / `early_only`: accuracy=0.817, balanced_accuracy=0.500
- `arithmetic` / `full_path`: accuracy=0.800, balanced_accuracy=0.552
- `causal_micro_world` / `early_middle`: accuracy=0.683, balanced_accuracy=0.647
- `causal_micro_world` / `early_only`: accuracy=0.717, balanced_accuracy=0.676
- `causal_micro_world` / `full_path`: accuracy=0.667, balanced_accuracy=0.633
- `commonsense_multihop` / `early_middle`: accuracy=0.617, balanced_accuracy=0.574
- `commonsense_multihop` / `early_only`: accuracy=0.500, balanced_accuracy=0.440
- `commonsense_multihop` / `full_path`: accuracy=0.583, balanced_accuracy=0.534
- `symbolic_logic` / `early_middle`: accuracy=0.483, balanced_accuracy=0.481
- `symbolic_logic` / `early_only`: accuracy=0.467, balanced_accuracy=0.467
- `symbolic_logic` / `full_path`: accuracy=0.433, balanced_accuracy=0.431
- `temporal_ordering` / `early_middle`: accuracy=0.667, balanced_accuracy=0.665
- `temporal_ordering` / `early_only`: accuracy=0.633, balanced_accuracy=0.618
- `temporal_ordering` / `full_path`: accuracy=0.733, balanced_accuracy=0.735

## Late-cluster rule accuracy

- `arithmetic` / `early_middle`: late_cluster_accuracy=0.741
- `arithmetic` / `early_only`: late_cluster_accuracy=0.481
- `causal_micro_world` / `early_middle`: late_cluster_accuracy=0.918
- `causal_micro_world` / `early_only`: late_cluster_accuracy=0.837
- `commonsense_multihop` / `early_middle`: late_cluster_accuracy=0.483
- `commonsense_multihop` / `early_only`: late_cluster_accuracy=0.417
- `symbolic_logic` / `early_middle`: late_cluster_accuracy=0.605
- `symbolic_logic` / `early_only`: late_cluster_accuracy=0.474
- `temporal_ordering` / `early_middle`: late_cluster_accuracy=0.625
- `temporal_ordering` / `early_only`: late_cluster_accuracy=0.531

## Reading

If early-only features already predict outcome well, the regime is being selected near the start of reasoning. If early-middle is much stronger than early-only, the decisive branching happens during the transition to the middle phase.
