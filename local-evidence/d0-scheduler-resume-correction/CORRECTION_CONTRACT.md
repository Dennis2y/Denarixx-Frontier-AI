# Denarixx Frontier AI — Scheduler Resume Correction Contract

Status: DESIGN FROZEN

Scope:

This correction applies only to future runs using the canonical
`ml/run_experiment.py` checkpoint/resume path.

It does not modify, reinterpret, replace, or rerun D0.2.

## Established behavior

D0.2 demonstrated that:

- model state is restored
- optimizer state is restored
- scheduler state is restored
- training_step is restored
- training continues from the checkpoint step
- the source checkpoint remains immutable

D0.2 is COMPLETE and FROZEN.

## Scheduler defect discovered after D0.2

The source run was created with:

    CosineAnnealingLR(T_max=4)

At source step 4 the scheduler reached:

    eta_min = 3e-05

When the run was resumed to maxSteps=8, the saved scheduler state
restored T_max=4.

Calling scheduler.step() for epochs 5 through 8 therefore moved through
the second half of the cosine cycle and increased the learning rate.

Observed sequence:

    step 4: 0.000030000000
    step 5: 0.000069540585
    step 6: 0.000165000000
    step 7: 0.000260459415
    step 8: 0.000300000000

This behavior is valid PyTorch scheduler behavior, but it is not the
intended Denarixx continuation policy.

## Required future behavior

A resumed training run must not silently begin a new upward cosine phase
merely because the source checkpoint reached its original T_max.

For the existing scheduler contract, once the saved scheduler has
reached its configured minimum at the checkpoint boundary, continuation
must remain at eta_min unless an explicitly defined new scheduling policy
is selected.

Therefore the immediate correction policy is:

1. Restore model state.
2. Restore optimizer state.
3. Restore scheduler state.
4. Restore training_step.
5. Detect whether the restored CosineAnnealingLR has already reached or
   passed its original T_max.
6. If it has, continuation uses a constant learning rate equal to the
   saved scheduler eta_min.
7. Do not allow implicit cosine rebound.
8. Preserve ordinary scheduler restoration behavior when the checkpoint
   has not yet reached T_max.

This is intentionally conservative.

A future milestone may introduce a different explicit continuation
schedule, but such a policy must be separately specified and tested.

## Frozen milestone boundary

D0.1 remains COMPLETE.

D0.2 remains COMPLETE.

No D0.2 checkpoint may be modified.

No D0.2 run may be rerun.

POST-007 remains isolated.

No formal dataset may be used for this correction.
