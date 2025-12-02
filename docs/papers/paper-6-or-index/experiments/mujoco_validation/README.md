# MuJoCo Continuous Control Validation

## Objective
Validate O/R Index on high-dimensional continuous control tasks using Multi-Agent MuJoCo.

## Environments
1. **ManyAgent Ant** - 2x4 agents controlling ant segments
2. **ManyAgent Swimmer** - 2x2 agents controlling swimmer segments

## O/R Definition for Continuous Actions
- Numerator: Trace of conditional action covariance Σ(a|o)
- Denominator: Trace of marginal action covariance Σ(a)
- O/R = Tr(Σ(a|o)) / Tr(Σ(a)) - 1

## Timeline
- Week 1: Environment setup, baseline training
- Week 2: Training runs (3 seeds × 2 envs)
- Week 3: O/R computation and analysis
- Week 4: Writing and integration
- Week 5: Buffer for debugging

## Expected Results
- Continuous control O/R follows same correlation as discrete
- Validates O/R is not an artifact of discrete action spaces
