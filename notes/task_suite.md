# Task Suite

## Objective

Use compact, controlled task families that reveal reasoning structure without relying on specialized domain knowledge.

## Families

### Arithmetic

Purpose:

- test explicit multi-step numerical decomposition

Templates:

- totals then subtraction
- inverse operation
- average / rate reasoning

### Symbolic Logic

Purpose:

- test rule-based inference detached from real-world facts

Templates:

- all / some / none statements
- implication and contradiction
- necessary vs sufficient condition checks

### Temporal Ordering

Purpose:

- test ordering relations with minimal lexical variation

Templates:

- before / after chains
- event ordering with 3-4 items

### Causal Micro-World

Purpose:

- test chained consequence reasoning in toy systems

Templates:

- ecosystem
- circuit
- traffic
- temperature and pressure

### Commonsense Multi-Hop

Purpose:

- test everyday reasoning where multiple latent steps are needed

Templates:

- physical state change
- intention and consequence
- omitted but implied intermediate cause

## Sampling target

Initial target:

- 20 prompts per family
- total 100 prompts

Stretch target:

- 50 prompts per family
- total 250 prompts

## Labeling

For each trace, record:

- task family
- difficulty
- model
- outcome
- number of steps

## First comparison set

The first clean comparison should be:

- arithmetic vs symbolic logic
- correct vs incorrect within each family

This is enough to see whether geometry differs by task and failure mode before broadening the dataset.
