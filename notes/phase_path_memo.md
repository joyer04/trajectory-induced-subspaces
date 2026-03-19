# Phase Path Memo

## Purpose

Assess whether correct and incorrect traces occupy different early-to-middle-to-late residual regime paths.

## Family path divergence

- `arithmetic`: correct_path=NA->2->4, incorrect_path=NA->0->4, same_path=False, path_js=0.888
- `temporal_ordering`: correct_path=3->4->3, incorrect_path=NA->3->1, same_path=False, path_js=0.638
- `commonsense_multihop`: correct_path=1->3->1, incorrect_path=1->3->1, same_path=True, path_js=0.602
- `causal_micro_world`: correct_path=4->1->3, incorrect_path=1->3->3, same_path=False, path_js=0.495
- `symbolic_logic`: correct_path=3->0->0, incorrect_path=NA->3->0, same_path=False, path_js=0.309

## Dominant paths

- `arithmetic` / `correct`: path=NA->2->4, count=19
- `arithmetic` / `incorrect`: path=NA->0->4, count=4
- `causal_micro_world` / `correct`: path=4->1->3, count=9
- `causal_micro_world` / `incorrect`: path=1->3->3, count=6
- `commonsense_multihop` / `correct`: path=1->3->1, count=3
- `commonsense_multihop` / `incorrect`: path=1->3->1, count=3
- `symbolic_logic` / `correct`: path=3->0->0, count=8
- `symbolic_logic` / `incorrect`: path=NA->3->0, count=9
- `temporal_ordering` / `correct`: path=3->4->3, count=2
- `temporal_ordering` / `incorrect`: path=NA->3->1, count=14

## Dominant transitions

- `arithmetic` / `correct` / `early_to_middle`: 2->3 (count=6)
- `arithmetic` / `correct` / `middle_to_late`: 2->4 (count=21)
- `arithmetic` / `incorrect` / `early_to_middle`: 0->3 (count=3)
- `arithmetic` / `incorrect` / `middle_to_late`: 0->4 (count=4)
- `causal_micro_world` / `correct` / `early_to_middle`: 1->3 (count=9)
- `causal_micro_world` / `correct` / `middle_to_late`: 1->3 (count=9)
- `causal_micro_world` / `incorrect` / `early_to_middle`: 1->3 (count=6)
- `causal_micro_world` / `incorrect` / `middle_to_late`: 1->1 (count=6)
- `commonsense_multihop` / `correct` / `early_to_middle`: 1->3 (count=5)
- `commonsense_multihop` / `correct` / `middle_to_late`: 3->1 (count=5)
- `commonsense_multihop` / `incorrect` / `early_to_middle`: 1->3 (count=9)
- `commonsense_multihop` / `incorrect` / `middle_to_late`: 3->1 (count=5)
- `symbolic_logic` / `correct` / `early_to_middle`: 3->0 (count=14)
- `symbolic_logic` / `correct` / `middle_to_late`: 0->0 (count=9)
- `symbolic_logic` / `incorrect` / `early_to_middle`: 3->0 (count=8)
- `symbolic_logic` / `incorrect` / `middle_to_late`: 0->3 (count=9)
- `temporal_ordering` / `correct` / `early_to_middle`: 3->4 (count=4)
- `temporal_ordering` / `correct` / `middle_to_late`: 4->3 (count=7)
- `temporal_ordering` / `incorrect` / `early_to_middle`: 4->3 (count=4)
- `temporal_ordering` / `incorrect` / `middle_to_late`: 3->1 (count=15)

## Reading

If dominant paths diverge early, then failure may be selected near the start of reasoning. If paths only diverge in the late transition, then the regime difference is more about answer commitment than initial decomposition.
