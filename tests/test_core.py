"""Checks for Parts 1-3. Run with `pytest` or `python tests/test_core.py`.

Monte Carlo checks use a fixed seed and a tolerance of several standard errors,
so they are deterministic and are not flaky.
"""

import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import mcpert as mc  # noqa: E402
from mcpert.examples import dinner, software_release  # noqa: E402


# ---------------------------------------------------------------- network

def test_longest_path_and_critical_path():
    project, _ = software_release()
    assert project.planned_duration() == 5 + 10 + 5 + 1
    names = [project.names[j] for j in project.critical_path()]
    assert names == ["spec", "backend", "integration", "release"]


def test_cycle_is_rejected():
    try:
        mc.Project([1, 1], [[1], [0]])
    except ValueError:
        return
    raise AssertionError("a cycle should raise ValueError")


def test_vectorised_matches_one_scenario_at_a_time():
    project, model = software_release()
    D = model.sample(50, rng=0)
    T = project.completion_time(D)
    for s in range(50):
        assert np.isclose(T[s], project.completion_time(D[s])[0])


def test_exactly_one_branch_is_critical():
    project, model = software_release()
    on_path = project.critical_tasks(model.sample(5_000, rng=1))
    branches = [project.names.index(x) for x in ["backend", "frontend", "database", "docs"]]
    assert np.all(on_path[:, branches].sum(axis=1) == 1)


# ---------------------------------------------------------------- dinner (exact answer known)

def test_dinner_example():
    project = dinner()
    model = mc.EmpiricalRatio(project.durations, ratios=[50 / 60, 70 / 60])  # 50 or 70 min
    T = mc.simulate(project, model, 200_000, rng=1)
    assert np.allclose(model.mean(), 60)           # each estimate is unbiased...
    assert abs(T.mean() - 65) < 0.1                # ...but dinner takes 65 min on average
    assert abs((T <= 60).mean() - 0.25) < 0.01     # and is on time 1/4 of the time


# ---------------------------------------------------------------- Clark

def test_clark_equal_means():
    m, _ = mc.clark_max(10.0, 2.0, 10.0, 2.0)
    assert np.isclose(m, 10 + np.sqrt(8) / np.sqrt(2 * np.pi))


def test_clark_against_monte_carlo():
    rng = np.random.default_rng(2)
    mu1, s1, mu2, s2, rho = 10.0, 2.0, 11.0, 3.0, 0.4
    cov = [[s1**2, rho * s1 * s2], [rho * s1 * s2, s2**2]]
    M = rng.multivariate_normal([mu1, mu2], cov, size=400_000).max(axis=1)
    m, s = mc.clark_max(mu1, s1, mu2, s2, rho)
    assert abs(M.mean() - m) < 5 * M.std() / np.sqrt(len(M))
    assert abs(M.std() - s) < 0.02


def test_sculli_exact_on_two_independent_paths():
    project = mc.Project([0, 0], [[], []])
    m, s = mc.sculli(project, mu=[10, 11], sigma=[2, 3])
    assert np.allclose((m, s), mc.clark_max(10, 2, 11, 3))


# ---------------------------------------------------------------- duration models

def test_model_means_and_variances():
    a, m, b = [2.0, 1.0], [4.0, 1.0], [10.0, 1.0]  # second task is deterministic
    U = np.random.default_rng(3).random((400_000, 2))
    for model in [mc.BetaPERT(a, m, b), mc.Triangular(a, m, b)]:
        for D in [model.sample(400_000, rng=3), model.ppf(U)]:  # both sampling routes
            assert np.allclose(D.mean(axis=0), model.mean(), atol=0.02)
            assert np.allclose(D.var(axis=0), model.var(), rtol=0.02, atol=1e-9)
    assert np.isclose(mc.BetaPERT(a, m, b).mean()[0], (2 + 4 * 4 + 10) / 6)


# ---------------------------------------------------------------- estimators

def test_jensen_pert_is_optimistic():
    project, model = software_release()
    T = mc.simulate(project, model, 100_000, rng=4)
    assert T.mean() > mc.pert_duration(project, model)


def test_quantile_ci_contains_true_quantile():
    x = np.random.default_rng(5).exponential(size=5_000)
    assert stats.expon.ppf(0.9) in mc.quantile_ci(x, 0.9)


def test_hoeffding_wider_than_clt():
    e = np.random.default_rng(6).random(1_000) < 0.3
    assert mc.prob_ci(e, method="hoeffding").radius > mc.prob_ci(e, method="clt").radius


def test_antithetic_and_control_variate_reduce_variance():
    project, model = software_release()
    n = 40_000
    plain = mc.mean_ci(mc.simulate(project, model, n, rng=7))
    anti = mc.mean_ci(mc.simulate(project, model, n, rng=7, antithetic=True))
    assert anti.radius < plain.radius
    T, D = mc.simulate(project, model, n, rng=7, return_durations=True)
    path = project.critical_path(model.mean())
    cv, _, corr = mc.control_variate(T, D[:, path].sum(axis=1), model.mean()[path].sum())
    assert cv.radius < plain.radius and corr > 0.5


def test_coverage_of_clt_interval_on_light_tails():
    project, model = software_release()
    true_mean = mc.simulate(project, model, 400_000, rng=9).mean()
    cov = mc.coverage(lambda g: mc.simulate(project, model, 2_000, rng=g), mc.mean_ci,
                      true_mean, reps=200, rng=10)
    assert 0.90 <= cov <= 0.99


if __name__ == "__main__":
    from _runner import run
    run(globals())
