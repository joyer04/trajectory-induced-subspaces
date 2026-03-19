# Finding Scores Memo

## Interpretation

These are heuristic evidence scores from 0 to 100. They are not p-values or posterior probabilities. They summarize sample size, effect size, and consistency across runs.

## Scores

- `F1` score=96.7: Static semantic axes under-explain dynamic reasoning transitions (sample=1.000, effect=0.918, consistency=1.000)
  note: High residual norms and low best-axis alignments persist across task/outcome groups.
- `F4` score=94.2: Residual regimes are phase-specific and path-specific, not uniform over a trace (sample=1.000, effect=0.977, consistency=0.800)
  note: Different families diverge in different phases and often follow different dominant regime paths.
- `F3` score=88.6: Family/outcome structure matters more than temperature for residual recurrence (sample=1.000, effect=0.715, consistency=1.000)
  note: Temperature margins are small while recurrence remains strong in the temperature-conditioned dataset.
- `F2` score=66.2: Some residual geometry is prompt-recurrent rather than pure sampling noise (sample=0.899, effect=0.449, consistency=0.700)
  note: Repeated-prompt significance survives across 4x5, 8x5, and temperature-conditioned runs.
