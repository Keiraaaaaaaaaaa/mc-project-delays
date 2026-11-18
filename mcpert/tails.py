"""Heavy tails and rare events. Part 5, Robin.

Checked by `python tests/test_part5.py`.
"""

from __future__ import annotations

import numpy as np

from .durations import DurationModel
from .montecarlo import mean_ci


class ParetoRatio(DurationModel):
    """Heavy-tailed model: D_i = planned_i * R_i with R_i ~ Pareto(alpha, scale).

    P(R > r) = (scale / r)^alpha for r >= scale. The mean is finite only if
    alpha > 1, and the variance only if alpha > 2. With 1 < alpha <= 2 the law of
    large numbers still holds but the CLT does not.

    Default scale = (alpha - 1) / alpha, so that E[R] = 1 (estimates right on average).
    Follow the other models in durations.py: ppf(U) inverts the CDF, mean() and
    var() are exact (return np.inf where they do not exist).
    """

    def __init__(self, planned, alpha, scale=None):
        self.planned = np.asarray(planned, dtype=float)
        self.alpha = float(alpha)
        self.scale = (self.alpha - 1) / self.alpha if scale is None else float(scale)
        self.k = len(self.planned)

    def ppf(self, U):
        # Inverse of F(r) = 1 - (scale / r)^alpha.
        return self.planned * self.scale * (1 - U) ** (-1 / self.alpha)

    def mean(self):
        a = self.alpha
        if a <= 1:
            return np.full(self.k, np.inf)
        return self.planned * self.scale * a / (a - 1)

    def var(self):
        a = self.alpha
        if a <= 2:
            return np.full(self.k, np.inf)
        return self.planned**2 * self.scale**2 * a / ((a - 1) ** 2 * (a - 2))


def hill_tail_index(x, k):
    """Hill (1975) estimator of the tail index alpha, from the k largest values.

    With X_(1) >= X_(2) >= ... sorted in decreasing order,
        1 / alpha_hat = (1/k) sum_{i=1..k} log( X_(i) / X_(k+1) ).
    """
    X = np.sort(np.asarray(x, dtype=float))[::-1]
    return 1 / np.mean(np.log(X[:k] / X[k]))


def tail_probability_is(project, planned, ratios, t, theta, n, rng=None, tilt="one"):
    """Importance-sampling estimate of p = P(T > t), when D_i = planned_i * R_i
    and each R_i is drawn from the observed `ratios` (the SiP model, m values).

    Plain Monte Carlo picks each ratio uniformly, with probability 1/m. Importance
    sampling picks ratios from a tilted law q_j proportional to r_j ** theta
    (theta > 0 favours long tasks), and reweights each scenario by w = f / g,
    the ratio of the true and the sampling probabilities of the scenario. Then
    E_g[1{T > t} w] = p for every theta (theta = 0 is plain Monte Carlo).

    tilt="all": every task is drawn from q.            w = prod_i (1/m) / q_{J_i}
    tilt="one": one task I, chosen uniformly among the k tasks, is drawn from q and
                the others are drawn uniformly. Averaging over I,
                                                        w = 1 / ( (1/k) sum_i m q_{J_i} )

    Return mean_ci of the weighted samples 1{T > t} * w.
    Hints: rng.choice(m, size=..., p=q) draws indices from q; compute the weights
    in logs (np.log, then np.exp) to avoid overflow.
    """
    rng = np.random.default_rng(rng)
    planned = np.asarray(planned, dtype=float)
    ratios = np.asarray(ratios, dtype=float)
    m, k = len(ratios), project.k

    # 1. Tilted law q_j proportional to r_j^theta, in logs (log-sum-exp).
    a = theta * np.log(ratios)
    log_q = a - (a.max() + np.log(np.exp(a - a.max()).sum()))
    q = np.exp(log_q)
    q /= q.sum()  # rng.choice wants probabilities that sum to 1 exactly

    # 2. Draw the ratio indices J (n, k) and the log-weights log(f / g).
    if tilt == "all":
        J = rng.choice(m, size=(n, k), p=q)
        log_w = -(np.log(m) + log_q[J]).sum(axis=1)
    elif tilt == "one":
        J = rng.integers(m, size=(n, k))
        I = rng.integers(k, size=n)
        J[np.arange(n), I] = rng.choice(m, size=n, p=q)
        b = np.log(m) + log_q[J]  # log(m q_{J_i})
        b_max = b.max(axis=1, keepdims=True)
        log_mean = b_max[:, 0] + np.log(np.exp(b - b_max).mean(axis=1))
        log_w = -log_mean
    else:
        raise ValueError("tilt must be 'all' or 'one'")

    # 3. Weighted indicators 1{T > t} * w.
    T = project.completion_time(planned * ratios[J])
    return mean_ci((T > t) * np.exp(log_w))
