"""Checks for Part 5 (Robin). Run with `python tests/test_part5.py` until all pass.

They test mcpert/tails.py.
"""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import mcpert as mc  # noqa: E402


def test_pareto_mean_and_variance():
    assert np.isclose(mc.ParetoRatio([5.0], alpha=3.0).mean()[0], 5.0)   # E[R] = 1 by default
    assert np.isinf(mc.ParetoRatio([5.0], alpha=1.5).var()[0])            # alpha <= 2
    assert np.isinf(mc.ParetoRatio([5.0], alpha=0.8).mean()[0])           # alpha <= 1


def test_pareto_tail_is_right():
    model = mc.ParetoRatio([1.0], alpha=1.5, scale=1.0)
    R = model.sample(400_000, rng=1)[:, 0]
    for x in [2, 5, 20]:
        assert abs((R > x).mean() - x**-1.5) < 0.003


def test_hill_estimator_on_pareto():
    x = 1 + np.random.default_rng(11).pareto(1.5, size=200_000)  # tail index 1.5
    assert abs(mc.hill_tail_index(x, k=5_000) - 1.5) < 0.1


def test_importance_sampling_with_theta_zero_is_plain_monte_carlo():
    ratios = np.array([0.5, 1.0, 2.0, 10.0])
    one_task = mc.Project([1.0], [[]])
    for tilt in ["all", "one"]:
        est = mc.tail_probability_is(one_task, [1.0], ratios, t=5, theta=0.0, n=100_000,
                                     rng=2, tilt=tilt)
        assert abs(est.value - 0.25) < 0.01, tilt


def test_importance_sampling_is_unbiased_and_more_precise():
    # Two tasks in parallel: P(T > t) = 1 - (1 - p1)(1 - p2), known exactly.
    ratios = np.random.default_rng(3).lognormal(0, 1, size=5_000)
    two_tasks = mc.Project([0.0, 0.0], [[], []])
    planned = np.array([1.0, 2.0])
    t = 2 * np.quantile(ratios, 0.999)
    p1, p2 = (planned[0] * ratios > t).mean(), (planned[1] * ratios > t).mean()
    exact = 1 - (1 - p1) * (1 - p2)
    plain = mc.tail_probability_is(two_tasks, planned, ratios, t, theta=0.0, n=20_000, rng=4)
    for tilt in ["all", "one"]:
        est = mc.tail_probability_is(two_tasks, planned, ratios, t, theta=1.5, n=20_000,
                                     rng=4, tilt=tilt)
        assert abs(est.value - exact) < 4 * est.radius / 1.96, tilt
        assert est.radius < plain.radius, tilt


if __name__ == "__main__":
    from _runner import run
    run(globals())
