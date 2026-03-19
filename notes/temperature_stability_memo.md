# Temperature Stability Memo

## Purpose

Measure how much prompt-level residual recurrence survives when generation temperature changes.

## Global pairwise summary

- same_prompt=False, same_family=False, same_outcome=False, same_temperature=False: mean_js=0.510, mean_tv=0.593
- same_prompt=False, same_family=False, same_outcome=False, same_temperature=True: mean_js=0.510, mean_tv=0.595
- same_prompt=False, same_family=False, same_outcome=True, same_temperature=False: mean_js=0.499, mean_tv=0.585
- same_prompt=False, same_family=False, same_outcome=True, same_temperature=True: mean_js=0.498, mean_tv=0.584
- same_prompt=False, same_family=True, same_outcome=False, same_temperature=False: mean_js=0.403, mean_tv=0.510
- same_prompt=False, same_family=True, same_outcome=False, same_temperature=True: mean_js=0.387, mean_tv=0.496
- same_prompt=False, same_family=True, same_outcome=True, same_temperature=False: mean_js=0.359, mean_tv=0.468
- same_prompt=False, same_family=True, same_outcome=True, same_temperature=True: mean_js=0.366, mean_tv=0.475
- same_prompt=True, same_family=True, same_outcome=False, same_temperature=False: mean_js=0.191, mean_tv=0.300
- same_prompt=True, same_family=True, same_outcome=False, same_temperature=True: mean_js=0.167, mean_tv=0.287
- same_prompt=True, same_family=True, same_outcome=True, same_temperature=False: mean_js=0.170, mean_tv=0.260
- same_prompt=True, same_family=True, same_outcome=True, same_temperature=True: mean_js=0.169, mean_tv=0.256

## Family temperature margins

- `arithmetic`: same_temp_js=0.182, cross_temp_js=0.219, margin=0.037
- `causal_micro_world`: same_temp_js=0.098, cross_temp_js=0.101, margin=0.002
- `temporal_ordering`: same_temp_js=0.199, cross_temp_js=0.190, margin=-0.009
- `commonsense_multihop`: same_temp_js=0.228, cross_temp_js=0.219, margin=-0.009
- `symbolic_logic`: same_temp_js=0.111, cross_temp_js=0.096, margin=-0.015

## Weakest temperature margins

- `symbolic_logic`: same_temp_js=0.111, cross_temp_js=0.096, margin=-0.015
- `commonsense_multihop`: same_temp_js=0.228, cross_temp_js=0.219, margin=-0.009
- `temporal_ordering`: same_temp_js=0.199, cross_temp_js=0.190, margin=-0.009
- `causal_micro_world`: same_temp_js=0.098, cross_temp_js=0.101, margin=0.002
- `arithmetic`: same_temp_js=0.182, cross_temp_js=0.219, margin=0.037

## Outcome mix by temperature

- temp=0p2, outcome=correct: mean_share=0.753
- temp=0p2, outcome=incorrect: mean_share=0.514
- temp=0p5, outcome=correct: mean_share=0.589
- temp=0p5, outcome=incorrect: mean_share=0.587
- temp=0p8, outcome=correct: mean_share=0.565
- temp=0p8, outcome=incorrect: mean_share=0.578

## Reading

A positive temperature margin means same-prompt traces are more similar when sampled at the same temperature than when pooled across temperatures. If this margin is large, some of the residual regime signal is temperature-sensitive rather than fully prompt-intrinsic.
