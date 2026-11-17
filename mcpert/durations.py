"""Probability models for task durations.

Every model is written through its inverse CDF ("ppf"): it maps uniforms
U in (0, 1) to durations D = F^{-1}(U). This is the inverse-transform method.
It makes antithetic sampling trivial: use U and 1 - U, and since F^{-1} is
increasing, a long duration in one copy comes with a short one in the other.

Tasks are independent: column i of U drives task i.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


class DurationModel:
    """Base class. Subclasses define ppf(U), mean() and var()."""

    k: int  # number of tasks

    def ppf(self, U):
        """Map uniforms U of shape (n, k) to durations of shape (n, k)."""
        raise NotImplementedError

    def mean(self):
        """Exact expected duration of each task, shape (k,)."""
        raise NotImplementedError

    def var(self):
        """Exact variance of each task's duration, shape (k,)."""
        raise NotImplementedError

    def sample(self, n, rng=None):
        rng = np.random.default_rng(rng)
        return self.ppf(rng.random((n, self.k)))


def _as_float(*arrays):
    out = np.broadcast_arrays(*(np.asarray(a, dtype=float) for a in arrays))
    return [np.array(a) for a in out]


class Normal(DurationModel):
    """D_i ~ N(mu_i, sigma_i^2).

    Durations can be negative, so use this only to check theory (Clark's formula).
    """

    def __init__(self, mu, sigma):
        self.mu, self.sigma = _as_float(mu, sigma)
        self.k = len(self.mu)

    def ppf(self, U):
        return self.mu + self.sigma * stats.norm.ppf(U)

    def mean(self):
        return self.mu.copy()

    def var(self):
        return self.sigma**2


class Triangular(DurationModel):
    """Three-point estimate: a = optimistic, m = most likely, b = pessimistic."""

    def __init__(self, a, m, b):
        self.a, self.m, self.b = _as_float(a, m, b)
        if np.any(self.a > self.m) or np.any(self.m > self.b):
            raise ValueError("need a <= m <= b")
        self.k = len(self.a)

    def ppf(self, U):
        a, m, b = self.a, self.m, self.b
        width = np.where(b > a, b - a, 1.0)
        mode_position = (m - a) / width
        left = a + np.sqrt(U * width * (m - a))
        right = b - np.sqrt((1 - U) * width * (b - m))
        return np.where(U < mode_position, left, right)

    def mean(self):
        return (self.a + self.m + self.b) / 3

    def var(self):
        a, m, b = self.a, self.m, self.b
        return (a**2 + m**2 + b**2 - a * m - a * b - m * b) / 18


class BetaPERT(DurationModel):
    """The classical PERT model (Malcolm et al., 1959).

    D = a + (b - a) X with X ~ Beta(alpha, beta), where alpha = 1 + 4 (m - a)/(b - a)
    and beta = 1 + 4 (b - m)/(b - a). The mean is then (a + 4m + b) / 6.
    A task with a == b is deterministic (for example a dummy task).
    """

    def __init__(self, a, m, b, lam=4.0):
        self.a, self.m, self.b = _as_float(a, m, b)
        if np.any(self.a > self.m) or np.any(self.m > self.b):
            raise ValueError("need a <= m <= b")
        self.k = len(self.a)
        self.lam = lam
        width = np.where(self.b > self.a, self.b - self.a, 1.0)
        self.alpha = 1 + lam * (self.m - self.a) / width
        self.beta = 1 + lam * (self.b - self.m) / width

    def ppf(self, U):
        return self.a + (self.b - self.a) * stats.beta.ppf(U, self.alpha, self.beta)

    def sample(self, n, rng=None):
        # Same law as ppf(uniforms), but about 20x faster than inverting the Beta CDF.
        rng = np.random.default_rng(rng)
        return self.a + (self.b - self.a) * rng.beta(self.alpha, self.beta, size=(n, self.k))

    def mean(self):
        return (self.a + self.lam * self.m + self.b) / (self.lam + 2)

    def var(self):
        s = self.alpha + self.beta
        return (self.b - self.a) ** 2 * self.alpha * self.beta / (s**2 * (s + 1))


class EmpiricalRatio(DurationModel):
    """Real-data model: D_i = planned_i * R_i, with R_i drawn from observed ratios.

    The ratios are actual / estimate for real tasks (the SiP dataset), so this is a
    bootstrap: the inverse CDF of R is the empirical quantile function of the data.
    This is "reference-class forecasting" (Flyvbjerg, 2006): past errors tell us
    how wrong today's estimates are likely to be.
    """

    def __init__(self, planned, ratios):
        self.planned = np.asarray(planned, dtype=float)
        self.ratios = np.sort(np.asarray(ratios, dtype=float))
        self.k = len(self.planned)

    def ppf(self, U):
        m = len(self.ratios)
        idx = np.minimum((U * m).astype(int), m - 1)
        return self.planned * self.ratios[idx]

    def mean(self):
        return self.planned * self.ratios.mean()

    def var(self):
        return self.planned**2 * self.ratios.var()
