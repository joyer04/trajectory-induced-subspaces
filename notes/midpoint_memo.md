# Midpoint Memo

## Core question

Can LLM reasoning be explained as movement along pre-existing static semantic axes, or does the trajectory itself induce additional local geometric structure?

## Current answer

Current evidence supports partial static explainability but not static sufficiency. Across the 100-trace MiniLM analysis, static-axis alignment remains modest while large residual structure remains.

## Bridge summary

- `arithmetic` / `correct`: best_abs_alignment=0.160, residual_energy=0.984
- `arithmetic` / `incorrect`: best_abs_alignment=0.216, residual_energy=0.974
- `causal_micro_world` / `correct`: best_abs_alignment=0.173, residual_energy=0.983
- `causal_micro_world` / `incorrect`: best_abs_alignment=0.163, residual_energy=0.984
- `commonsense_multihop` / `correct`: best_abs_alignment=0.168, residual_energy=0.984
- `commonsense_multihop` / `incorrect`: best_abs_alignment=0.161, residual_energy=0.985
- `symbolic_logic` / `correct`: best_abs_alignment=0.124, residual_energy=0.991
- `symbolic_logic` / `incorrect`: best_abs_alignment=0.121, residual_energy=0.991
- `temporal_ordering` / `correct`: best_abs_alignment=0.141, residual_energy=0.989
- `temporal_ordering` / `incorrect`: best_abs_alignment=0.107, residual_energy=0.993

## Residual structure

- Residual PCA top components: residual_pc_1=0.031, residual_pc_2=0.028, residual_pc_3=0.024, residual_pc_4=0.022, residual_pc_5=0.019
- Residual variance does not collapse after static-axis projection.

## Failure-regime observations

- `arithmetic`: correct_residual=0.972, incorrect_residual=0.964, same_mode_cluster=False
- `causal_micro_world`: correct_residual=0.968, incorrect_residual=0.975, same_mode_cluster=False
- `commonsense_multihop`: correct_residual=0.971, incorrect_residual=0.972, same_mode_cluster=False
- `symbolic_logic`: correct_residual=0.983, incorrect_residual=0.985, same_mode_cluster=False
- `temporal_ordering`: correct_residual=0.980, incorrect_residual=0.986, same_mode_cluster=False

## Cluster-level differences

- `arithmetic`:
  residual cluster 4 is shifted toward incorrect by 0.291
  exemplar: Nels are a subset of quars (from step 1)  ==>  Quars are a subset of brims (from step 2)
  exemplar: Check-in  ==>  Security
  residual cluster 3 is shifted toward incorrect by 0.064
  exemplar: Inspection  ==>  Repair
  exemplar: We know that passing the exam is sufficient for receiving a certificate.  ==>  Mina received no certificate.
- `causal_micro_world`:
  residual cluster 3 is shifted toward incorrect by 0.253
  exemplar: Inspection  ==>  Repair
  exemplar: We know that passing the exam is sufficient for receiving a certificate.  ==>  Mina received no certificate.
  residual cluster 2 is shifted toward incorrect by 0.020
  exemplar: The only activity mentioned that could fit between attending class and eating lunch is practicing a sport (practice).  ==>  Therefore, Hana practiced before eating lunch.
  exemplar: Sorting  ==>  Delivery
- `commonsense_multihop`:
  residual cluster 0 is shifted toward incorrect by 0.081
  exemplar: As the ice melts, it turns into liquid water.  ==>  The melted water collects at the bottom of the freezer.
  exemplar: As the ice cube melted, it released latent heat energy into its surroundings.  ==>  This released heat energy onto the metal tray.
  residual cluster 1 is shifted toward incorrect by 0.040
  exemplar: The bell rang.  ==>  The lecture began.
  exemplar: Repair  ==>  Testing
- `symbolic_logic`:
  residual cluster 2 is shifted toward incorrect by 0.056
  exemplar: The only activity mentioned that could fit between attending class and eating lunch is practicing a sport (practice).  ==>  Therefore, Hana practiced before eating lunch.
  exemplar: Sorting  ==>  Delivery
  residual cluster 0 is shifted toward incorrect by 0.046
  exemplar: As the ice melts, it turns into liquid water.  ==>  The melted water collects at the bottom of the freezer.
  exemplar: As the ice cube melted, it released latent heat energy into its surroundings.  ==>  This released heat energy onto the metal tray.
- `temporal_ordering`:
  residual cluster 1 is shifted toward incorrect by 0.135
  exemplar: The bell rang.  ==>  The lecture began.
  exemplar: Repair  ==>  Testing
  residual cluster 3 is shifted toward incorrect by 0.091
  exemplar: Inspection  ==>  Repair
  exemplar: We know that passing the exam is sufficient for receiving a certificate.  ==>  Mina received no certificate.

## Interpretation

The strongest reading at this stage is that reasoning uses some static manifold structure, but dynamic transitions retain family-sensitive residual geometry. Failure appears less like global noise and more like entry into different residual regimes.

## Remaining limits

- Static axes are limited to a low-rank PCA basis.
- Residual clusters are unsupervised and may still mix multiple transition types.
- Outcome labels are model-judged, not gold-labeled.

## Next step

Move from residual-cluster presence to residual-cluster semantics: label the residual regimes and test whether the same regime recurs across prompts within each family.
