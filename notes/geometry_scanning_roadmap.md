# Geometry Scanning Roadmap

## Why a new roadmap

The project has moved past the stage where the main question is simply:

- do residuals exist?
- do repeated prompts matter?

Those questions have useful preliminary answers.

The next stage is to scan the geometry of reasoning more systematically.

That means moving from:

- single analyses
- one-off memos

to:

- a staged scanning program
- comparable figures across axes
- explicit decision rules about what counts as a stable signal

## Current strongest findings

1. Static semantic axes under-explain dynamic reasoning transitions.
2. Residual regimes are family-specific and often phase-specific.
3. Some residual geometry is prompt-recurrent.
4. Temperature matters less than family, outcome, and phase for residual organization.

## Stage A. Robustness map

Question:

Where is each finding strong, weak, or unstable?

Why this matters:

Right now the project has several good local results, but it still needs a global map.

Tasks:

1. build family x outcome heatmaps for prompt recurrence
2. build family x phase heatmaps for failure divergence
3. build family summaries for temperature sensitivity
4. combine those into one exploratory “robustness map”

Expected outputs:

- figures that make it obvious which claims are broad and which are local
- one dashboard/report section that compresses the current state

Decision value:

- identifies where to trust the current story
- identifies where more data is needed

## Stage B. Early-branch vs late-commit scan

Question:

At what point in the reasoning trace is the future path effectively determined?

Why this matters:

This turns geometric description into a timing question:

- early regime selection
- mid-trace branching
- late answer commitment

Tasks:

1. compare early-only, early+middle, and full-path predictability
2. estimate held-out prompt outcome prediction where possible
3. compare late-cluster predictability from early-phase features

Expected outputs:

- family-specific timing signatures
- figures showing when different families “lock in”

Decision value:

- sharpens what kind of geometry each family exhibits

## Stage C. Path topology scan

Question:

Are correct and incorrect traces using different path topologies, or just different path frequencies?

Why this matters:

Phase paths already show divergence, but the next step is to look at the path system itself.

Tasks:

1. build transition graphs per family/outcome
2. compare path entropy and dominant transition reuse
3. identify branch points with the largest correct/incorrect split

Expected outputs:

- transition-graph figures
- branch-point rankings

Decision value:

- reveals where the geometry actually bifurcates

## Stage D. Local subspace scan

Question:

Can we characterize the residual geometry itself as a local low-dimensional object?

Why this matters:

This is the deepest version of the original hypothesis.

Tasks:

1. fit local PCA around phase-conditioned residual clusters
2. estimate intrinsic dimension per family/outcome/phase bucket
3. compare subspace overlap across prompts and temperatures

Expected outputs:

- local dimension estimates
- subspace overlap tables
- phase-conditioned local-plane figures

Decision value:

- directly tests whether the residual is structured as a reusable local subspace

## Stage E. Backbone robustness

Question:

How much of the story survives a different embedding backbone?

Why this matters:

The project currently leans heavily on MiniLM.

Tasks:

1. rerun the strongest analyses with mpnet and bge-small
2. compare robustness maps across embedding models
3. score which findings are backbone-stable

Expected outputs:

- cross-backbone comparison table
- backbone robustness memo

Decision value:

- separates geometry claims from backbone artifacts

## Practical order

The recommended order is:

1. Stage A: robustness map
2. Stage B: early-branch vs late-commit scan
3. Stage C: path topology scan
4. Stage D: local subspace scan
5. Stage E: backbone robustness

## Immediate implementation target

Implement Stage A first.

Reason:

- the project already has most of the required CSVs
- the figures can be generated quickly
- the result improves every later decision

## Rule for moving deeper

Only move from Stage A/B into Stage D if both remain true:

1. residual structure stays strong under broader scanning
2. the strongest signals are not confined to a single family or artifact source
