# Family Regime Memo

## Goal

Characterize residual regimes inside each task family and compare how correct and incorrect traces distribute across them.

## Family divergence

- `arithmetic`: TV distance=0.355, JS divergence=0.222
- `causal_micro_world`: TV distance=0.273, JS divergence=0.105
- `temporal_ordering`: TV distance=0.226, JS divergence=0.045
- `commonsense_multihop`: TV distance=0.143, JS divergence=0.016
- `symbolic_logic`: TV distance=0.102, JS divergence=0.033

## Dominant incorrect-shifted regimes

- `arithmetic`:
  cluster 4: incorrect_minus_correct=0.291, correct=0.209, incorrect=0.500
  exemplar: Plug in the values: Average Speed = 150 km / 3 hours  ==>  Perform the division: Average Speed = 50 km/h
  exemplar: Calculate the total time taken: 1 hour + 2 hours = 3 hours  ==>  Calculate the average speed using the formula: Average Speed = Total Distance / Total Time
  cluster 3: incorrect_minus_correct=0.064, correct=0.186, incorrect=0.250
  exemplar: Calculate the total distance traveled: 60 km + 90 km = 150 km  ==>  Calculate the total time taken: 1 hour + 2 hours = 3 hours
- `causal_micro_world`:
  cluster 3: incorrect_minus_correct=0.253, correct=0.184, incorrect=0.438
  exemplar: Cooling fails.  ==>  Server overheats.
  exemplar: Ice inside the freezer begins to melt due to the lack of refrigeration.  ==>  As the ice melts, it turns into liquid water.
  cluster 2: incorrect_minus_correct=0.020, correct=0.105, incorrect=0.125
  exemplar: Soil drying leads to plant wilting.  ==>  Wilting results in reduced shade coverage.
  exemplar: Without product B, the pH of the solution does not change.  ==>  As a result, the indicator stays blue.
- `commonsense_multihop`:
  cluster 0: incorrect_minus_correct=0.081, correct=0.267, incorrect=0.348
  exemplar: As the ice cube melted, it released latent heat energy into its surroundings.  ==>  This released heat energy onto the metal tray.
  exemplar: The sun's rays pass through the glass of the car window, warming the interior.  ==>  The warm air inside the car is trapped by the closed windows and doors.
  cluster 1: incorrect_minus_correct=0.040, correct=0.156, incorrect=0.196
  exemplar: Over time, the starches converted into sugars through a process called retrogradation.  ==>  As the sugars accumulated, they caused the gluten network in the bread to tighten, leading to hardness.
  exemplar: This means that the temperature at which water begins to freeze is lowered from 0°C (32°F) to a lower value.  ==>  As a result, when the mixture of salt and ice is exposed to air, the water molecules in the ice begin to evaporate more quickly.
- `symbolic_logic`:
  cluster 2: incorrect_minus_correct=0.056, correct=0.167, incorrect=0.222
  exemplar: Some pels are ronts (given).  ==>  From steps 1 and 2, we can conclude that some pels are also neds.
  exemplar: Given that no mivs are pels.  ==>  From steps 1 and 2, we can conclude that no tars are pels (since if something is a tar, it's also an miv, but mivs cannot be pels).
  cluster 0: incorrect_minus_correct=0.046, correct=0.250, incorrect=0.296
  exemplar: However, since P is not sufficient for Q, we cannot conclude that Q must have occurred solely because P occurred.  ==>  We can only conclude that Q may or may not have occurred given that P occurred.
  exemplar: We can only conclude that if there is at least one bloop that is also a raz, then some glims could be razs (but we cannot guarantee this).  ==>  Therefore, we cannot definitively conclude that some glims are razs based on the given information.
- `temporal_ordering`:
  cluster 1: incorrect_minus_correct=0.135, correct=0.154, incorrect=0.289
  exemplar: The bell rang.  ==>  The lecture began.
  exemplar: Repair  ==>  Testing
  cluster 3: incorrect_minus_correct=0.091, correct=0.154, incorrect=0.244
  exemplar: Inspection  ==>  Repair
  exemplar: Concert rehearsal  ==>  Dinner

## Reading

If family-level profile divergence remains non-trivial, then failure is better described as a family-specific residual regime shift than as global off-axis noise.
