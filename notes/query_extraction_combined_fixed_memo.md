# Query Extraction Combined Fixed

Artifacts:

- `/Users/tedhong/Research/trajectory-induced-subspaces/data/raw/traces_query_extraction_combined_fixed.jsonl`
- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/static_dynamic_bridge_query_extraction_combined_fixed`
- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/atlas_vs_global_query_extraction_combined_fixed/atlas_vs_global_comparison.csv`
- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/empirical_energy_query_extraction_combined_fixed/empirical_saddle_ranking.csv`
- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/continuation_collapse_query_extraction_combined_fixed/continuation_collapse_controls.csv`
- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/same_location_history_query_extraction_combined_fixed/same_location_history_summary.csv`

## Why this rerun happened

`query_extraction` was previously blocked by very low correct-trace density. During the rerun, the temporal oracle was audited and fixed to avoid treating question words and generic tokens as entities:

- `Who`
- `Which`
- `What`
- `Event`
- `Stage`

This raised usable correct support.

## Dataset

The combined fixed set has:

- `60` traces
- `16 correct`
- `44 incorrect`

This is still imbalanced, but it is much better than the earlier `2 correct / 28 incorrect` condition.

## What strengthened

### Same-location / different-history now works

The strongest local source is `M:3`.

- valid neighborhoods: `13`
- median principal angle: `78.4 deg`
- mean principal angle: `74.9 deg`

This is the most important improvement. It means `query_extraction` now shows history-conditioned local geometry once enough correct support is available.

### Local atlas still beats global basis

- atlas gain mean: `0.171`
- branch atlas gain mean: `0.288`

So the local-structure read remains alive.

## What weakened

The branch sharpness and collapse picture is less strong in the combined set:

- middle-to-late weighted source JS: `0.213`
- strongest source: `M:3`
- entropy gain over matched control: `0.107`
- variance gain over matched control: `-0.041`

So the strongest local history signal does not yet translate into a clean commitment-collapse signal.

## Current label

`query_extraction` should move from:

- `late_split_candidate`

to:

- `history_sensitive_candidate`

It has real local geometry, but the commitment-like branch collapse is not strong enough to call it `state_dominant` or `two_stage`.

## Interpretation

`query_extraction` may be a different kind of temporal regime:

- not a clean late-commit system
- not a strong two-stage system
- but a history-sensitive local geometry where correct and incorrect continuations diverge inside similar residual neighborhoods

This is useful because it prevents overforcing all subfamilies into the same taxonomy.
