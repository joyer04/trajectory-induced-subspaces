# Trajectory-Induced Subspaces: Exploratory Research Note

This is not a paper draft. It is a working research note for the current state of the project.

This repository is being used as a personal learning and exploratory research space, so the goal here is not to present a polished final claim. The goal is to keep the experiments, plots, questions, and partial conclusions legible in public.

The core question is simple:

> Does LLM reasoning mostly follow pre-existing semantic axes, or does the trajectory itself induce local residual structure?

There is now adjacent public writing making a similar high-level pivot from static representation to trajectory geometry, such as Kareem Soliman's 2026 Towards AI article on LLM thought geometry in arithmetic tasks ([link](https://pub.towardsai.net/what-does-the-shape-of-thought-look-like-inside-an-llm-475a43093390)). I read that as useful context, but not as covering the same ground: the focus here is the bridge between static manifold structure and dynamic residual regimes, plus family-specific phase topology.

## Current Dataset Footprint

- Temperature-conditioned run: `300` traces, `1302` steps, `1002` deltas
- Repeated 8x5 run: `200` traces, `861` steps, `661` deltas
- Embedding backbone: `sentence-transformers/all-MiniLM-L6-v2`
- Reasoning models: local Ollama-served models for generation and judging

## The Short Version

- Static top axes are weak explanatory variables for actual reasoning motion. Mean best-axis alignment is only `0.148`, while mean residual energy stays around `0.987`.
- Repeated same-prompt runs are often more similar to each other than different prompts from the same family, so the residual geometry is not just noise.
- The geometry is not universal. It depends strongly on task family, outcome, and even phase of the reasoning trace.
- Temperature changes outcome mix, but it does not appear to be the dominant source of residual regime structure.

## Evidence Scoreboard

These are heuristic evidence scores, not probabilities.

- `F1` `96.7/100`: Static semantic axes under-explain dynamic reasoning transitions
- `F4` `94.2/100`: Residual regimes are phase-specific and path-specific, not uniform over a trace
- `F3` `88.6/100`: Family/outcome structure matters more than temperature for residual recurrence
- `F2` `66.2/100`: Some residual geometry is prompt-recurrent rather than pure sampling noise

## What Looks Strong

### 1. Static semantic manifold is not enough

The average alignment to the best static axis remains low (`0.148`), while residual norms stay very high across families. That is the cleanest and most stable finding in the project right now.

### 2. Residual structure is phase-specific

- `arithmetic`: correct `NA->2->4` vs incorrect `NA->0->4` (path JS `0.888`)
- `temporal_ordering`: correct `3->4->3` vs incorrect `NA->3->1` (path JS `0.638`)
- `commonsense_multihop`: correct `1->3->1` vs incorrect `1->3->1` (path JS `0.602`)
- `causal_micro_world`: correct `4->1->3` vs incorrect `1->3->3` (path JS `0.495`)
- `symbolic_logic`: correct `3->0->0` vs incorrect `NA->3->0` (path JS `0.309`)

This is important because it suggests failures are not just 'further away' from the manifold. They often follow different path topologies through phase space.

### 3. Repeated prompts still matter when prompt support is widened

- `symbolic_logic` / `correct`: pairwise margin `0.329`, `p=0.001`, prompts `7`
- `symbolic_logic` / `incorrect`: pairwise margin `0.254`, `p=0.001`, prompts `7`
- `temporal_ordering` / `incorrect`: pairwise margin `0.234`, `p=0.001`, prompts `7`
- `arithmetic` / `correct`: pairwise margin `0.229`, `p=0.001`, prompts `8`
- `causal_micro_world` / `correct`: pairwise margin `0.201`, `p=0.001`, prompts `8`
- `commonsense_multihop` / `correct`: pairwise margin `0.086`, `p=0.028`, prompts `7`

This is the main reason I am comfortable saying that at least part of the residual geometry is genuinely prompt-recurrent.

## Where The Story Gets More Interesting

### Arithmetic

Arithmetic is not just 'harder'. Its divergence often appears early or in the middle phase. That makes it look more like an early regime-selection problem than a late answer-commitment problem.

### Temporal Ordering

Temporal tasks often look more path-sensitive late in the trace. That suggests the failure may emerge when the model commits to an ordering rather than when it first decomposes the problem.

### Causal Micro World

Causal tasks are surprisingly structured. Early-phase signals already carry useful information about later path and outcome.

## Temperature: Important, But Not The Main Character

- `arithmetic`: same-temp JS `0.182` vs cross-temp JS `0.219` (margin `0.037`)
- `causal_micro_world`: same-temp JS `0.098` vs cross-temp JS `0.101` (margin `0.002`)
- `temporal_ordering`: same-temp JS `0.199` vs cross-temp JS `0.190` (margin `-0.009`)
- `commonsense_multihop`: same-temp JS `0.228` vs cross-temp JS `0.219` (margin `-0.009`)
- `symbolic_logic`: same-temp JS `0.111` vs cross-temp JS `0.096` (margin `-0.015`)

The margins are mostly small. Temperature does move the correct/incorrect ratio, but it is not the main driver of the residual regime structure.

## A Useful Mental Model

Right now the project looks less like 'the model walks along a single semantic gradient' and more like this:

1. The prompt family constrains a coarse region of semantic space.
2. The reasoning trajectory enters a local regime.
3. Different outcomes correspond to different phase paths through that regime.
4. Static axes explain some background organization, but not the actual motion.

## What Still Looks Unsettled

- Prompt recurrence is real, but not equally strong in every family/outcome bucket.
- Some groups still have weak or unstable significance when prompt support grows.
- The current cluster labels are useful for orientation, but they are still exploratory rather than definitive.

## What I Would Do Next

- Build a robustness map that shows each finding by family, outcome, temperature, and phase in one place.
- Test whether early-phase regime features can predict final outcome on held-out prompts rather than held-out traces only.
- Compare multiple embedding backbones on the full repeated datasets, not just the static text corpus.
- Add a small interactive notebook or dashboard view for phase paths and regime transitions.

## Files Worth Opening

- [Evidence scores](outputs/finding_evidence_scores.csv)
- [Temperature bridge outputs](outputs/static_dynamic_bridge_temperature_minilm)
- [Repeated 8x5 bridge outputs](outputs/static_dynamic_bridge_repeated_8x5_minilm)
- [Phase path memo](notes/phase_path_memo.md)
- [Prompt recurrence significance memo](notes/prompt_recurrence_significance_repeated_8x5_memo.md)

## Bottom Line

The exploratory picture is getting sharper. The strongest reading so far is that reasoning is not well described as simple static-axis following. It looks more like family-specific, phase-specific local geometry, with some regimes recurring across repeated runs and others remaining unstable.
