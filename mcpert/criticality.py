"""Which tasks drive the delivery date? Part 4, Brian.

Criticality index of task i: P(i is on the critical path) (Van Slyke, 1963).
Theorem (to prove in Part 4): if D_i = mu_i + noise_i, then dE[T]/dmu_i = P(i is critical).

TODO (Brian): implement the two functions, then run `python tests/test_part4.py`.
"""

from __future__ import annotations

import numpy as np

from .montecarlo import mean_ci


def criticality_index(project, model, n, rng=None):
    """Monte Carlo estimate of P(task j is on the critical path), for every task j.

    Draw n scenarios with model.sample, find the critical path of each one with
    project.critical_tasks (a boolean array of shape (n, k)), and average over the
    scenarios. Returns an array of shape (k,).
    """
    raise NotImplementedError("Part 4 (Brian): criticality_index")


def shift_sensitivity(project, model, task, h, n, rng=None):
    """Finite-difference estimate of dE[T]/dmu_task, with common random numbers.

    Draw n scenarios D once. Compute T on D, and T on a copy of D where h is added
    to column `task`. Return mean_ci((T_shifted - T) / h).
    Using the SAME durations in both runs makes them strongly correlated, so the
    difference has a tiny variance. That is the "common random numbers" trick.
    """
    raise NotImplementedError("Part 4 (Brian): shift_sensitivity")
