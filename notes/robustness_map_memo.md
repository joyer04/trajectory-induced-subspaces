# Robustness Map Memo

## Purpose

Compress the current state of the project into a small number of scanning figures that show where each finding is strong or weak.

## Strongest prompt-recurrence buckets

- `symbolic_logic` / `correct`: margin=0.329, p=0.001
- `symbolic_logic` / `incorrect`: margin=0.254, p=0.001
- `temporal_ordering` / `incorrect`: margin=0.234, p=0.001
- `arithmetic` / `correct`: margin=0.229, p=0.001
- `causal_micro_world` / `correct`: margin=0.201, p=0.001
- `commonsense_multihop` / `correct`: margin=0.086, p=0.028

## Strongest phase divergences

- `arithmetic` / `middle`: js=0.419, same_mode=False
- `arithmetic` / `early`: js=0.350, same_mode=False
- `temporal_ordering` / `late`: js=0.192, same_mode=False
- `causal_micro_world` / `early`: js=0.177, same_mode=False
- `temporal_ordering` / `early`: js=0.100, same_mode=True
- `temporal_ordering` / `middle`: js=0.098, same_mode=False

## Temperature sensitivity

- `arithmetic`: temperature_margin=0.037
- `causal_micro_world`: temperature_margin=0.002
- `temporal_ordering`: temperature_margin=-0.009
- `commonsense_multihop`: temperature_margin=-0.009
- `symbolic_logic`: temperature_margin=-0.015

## Current evidence scores

- `F1`: score=96.7 (Static semantic axes under-explain dynamic reasoning transitions)
- `F4`: score=94.2 (Residual regimes are phase-specific and path-specific, not uniform over a trace)
- `F3`: score=88.6 (Family/outcome structure matters more than temperature for residual recurrence)
- `F2`: score=66.2 (Some residual geometry is prompt-recurrent rather than pure sampling noise)

## Reading

The robustness maps are not a new theory. They are a scanning layer that tells us where the current theory seems strongest, where it still looks local, and where the next data collection should focus.
