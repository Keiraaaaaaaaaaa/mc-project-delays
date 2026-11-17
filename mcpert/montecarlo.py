"""Monte Carlo estimation of project-duration quantities, with error bars.

The estimator is simple. Draw n independent scenarios of the task durations,
compute the project duration T^(1), ..., T^(n) of each, and average:

    E[T]          ~  (1/n) sum_s T^(s)
    P(T <= t)     ~  (1/n) sum_s 1{T^(s) <= t}
    90% date      ~  empirical 0.9-quantile of the T^(s)

What matters is how much to trust these numbers. That is the job of the
confidence intervals below.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class Estimate:
    """A point estimate with a confidence interval [low, high]."""

    value: float
    low: float
    high: float
    n: int
    method: str

    @property
    def radius(self):
        return (self.high - self.low) / 2

    @property
    def interval(self):
        """The interval as text, for tables: '[low, high]'."""
        return f"[{self.low:.4g}, {self.high:.4g}]"

    def __contains__(self, x):
        return self.low <= x <= self.high

    def __str__(self):
        return f"{self.value:.4g}  [{self.low:.4g}, {self.high:.4g}]  ({self.method}, n={self.n})"


# ---------------------------------------------------------------------- simulation

def simulate(project, model, n, rng=None, antithetic=False, return_durations=False):
    """Simulate project durations T = longest path with random task durations.

    With antithetic=True, n // 2 uniform vectors U are drawn and each is paired with
    1 - U. The function then returns the n // 2 pair averages (T(U) + T(1 - U)) / 2.
    They are i.i.d., so the confidence intervals below apply to them directly,
    and the total number of longest-path evaluations is still n.
    """
    if model.k != project.k:
        raise ValueError(f"model has {model.k} tasks but project has {project.k}")
    rng = np.random.default_rng(rng)
    if antithetic:
        if return_durations:
            raise ValueError("return_durations is not available with antithetic=True")
        U = rng.random((n // 2, project.k))
        return (project.completion_time(model.ppf(U)) + project.completion_time(model.ppf(1 - U))) / 2
    D = model.sample(n, rng)
    T = project.completion_time(D)
    return (T, D) if return_durations else T


def pert_duration(project, model):
    """The classical PERT answer: the longest path when every task takes its mean duration.

    max is convex, so by Jensen's inequality E[T] >= pert_duration.
    """
    return float(project.completion_time(model.mean())[0])


def pert_normal_approx(project, model):
    """Classical PERT distribution: T ~ N(sum of means, sum of variances) along the
    critical path computed with the mean durations. It ignores every other path."""
    path = project.critical_path(model.mean())
    return float(model.mean()[path].sum()), float(np.sqrt(model.var()[path].sum()))


# ---------------------------------------------------------------------- confidence intervals

def _z(level):
    return stats.norm.ppf(0.5 + level / 2)


def mean_ci(x, level=0.95):
    """CLT interval for E[X]: mean +/- z * s / sqrt(n).

    Asymptotic, and it requires Var(X) < infinity. Part 5 tests how it fails
    with heavy tails.
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    m = x.mean()
    r = _z(level) * x.std(ddof=1) / np.sqrt(n)
    return Estimate(m, m - r, m + r, n, "CLT")


def prob_ci(event, level=0.95, method="hoeffding"):
    """Interval for p = P(event) from 0/1 outcomes.

    hoeffding : p_hat +/- sqrt(log(2/delta) / (2n)), with delta = 1 - level.
                Non-asymptotic: valid for every n (Hoeffding's inequality, Ch. 1).
    clt       : p_hat +/- z sqrt(p_hat (1 - p_hat) / n). Narrower, but only asymptotic.
    """
    e = np.asarray(event, dtype=float)
    n = len(e)
    p = e.mean()
    if method == "hoeffding":
        r = np.sqrt(np.log(2 / (1 - level)) / (2 * n))
    elif method == "clt":
        r = _z(level) * np.sqrt(p * (1 - p) / n)
    else:
        raise ValueError("method must be 'hoeffding' or 'clt'")
    return Estimate(p, max(0.0, p - r), min(1.0, p + r), n, method)


def quantile_ci(x, q, level=0.95):
    """Distribution-free interval for the q-quantile (q = 0.9: the date met with 90% probability).

    If xi is the true q-quantile, the number of samples below xi is Binomial(n, q),
    so binomial quantiles give the ranks of two order statistics that bracket xi
    with probability at least `level`. There is no CLT and no variance assumption,
    so the interval stays valid even with infinite variance.
    """
    xs = np.sort(np.asarray(x, dtype=float))
    n = len(xs)
    delta = 1 - level
    lo = max(int(stats.binom.ppf(delta / 2, n, q)), 1)  # 1-based ranks
    hi = min(int(stats.binom.ppf(1 - delta / 2, n, q)) + 1, n)
    value = float(np.quantile(xs, q, method="inverted_cdf"))
    return Estimate(value, float(xs[lo - 1]), float(xs[hi - 1]), n, "order statistics")


def dkw_radius(n, level=0.95):
    """Dvoretzky-Kiefer-Wolfowitz with Massart's constant: with probability >= level,
    sup_t |F_n(t) - F(t)| <= sqrt(log(2/delta) / (2n)). It is one band for the whole
    CDF of T, so it covers every deadline t at once."""
    return float(np.sqrt(np.log(2 / (1 - level)) / (2 * n)))


# ---------------------------------------------------------------------- variance reduction

def control_variate(y, c, c_mean, level=0.95):
    """Control-variate estimate of E[y], using a variable c whose mean is known exactly.

    y_cv = y - beta (c - E[c]), with beta = Cov(y, c) / Var(c) estimated from the
    sample. The variance is multiplied by 1 - corr(y, c)^2. Estimating beta from
    the same sample adds a bias of order 1/n, which is negligible here.

    Natural choice for projects: c = length of the PERT critical path, whose mean is
    the sum of the mean durations on it. Returns (estimate, beta, corr).
    """
    y = np.asarray(y, dtype=float)
    c = np.asarray(c, dtype=float)
    cov = np.cov(y, c)
    beta = cov[0, 1] / cov[1, 1]
    corr = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    est = mean_ci(y - beta * (c - c_mean), level)
    est.method = "CLT + control variate"
    return est, float(beta), float(corr)


# ---------------------------------------------------------------------- diagnostics

def running_mean(x):
    """Running average (1/m) sum_{s<=m} x_s for m = 1..n, to plot the convergence."""
    x = np.asarray(x, dtype=float)
    return np.cumsum(x) / np.arange(1, len(x) + 1)


def coverage(sample_fn, ci_fn, true_value, reps=500, rng=None):
    """Fraction of `reps` independent experiments whose interval contains true_value.

    sample_fn(rng) -> a Monte Carlo sample;  ci_fn(sample) -> Estimate.
    A 95% interval should cover about 95% of the time (the coverage experiment of Ch. 1).
    """
    rng = np.random.default_rng(rng)
    hits = sum(true_value in ci_fn(sample_fn(rng)) for _ in range(reps))
    return hits / reps
