"""Analytic baselines: Clark's exact formula, and Sculli's network approximation.

Clark (1961). For (X1, X2) jointly Gaussian with means mu1, mu2, standard
deviations s1, s2 and correlation rho, let

    theta = sqrt(s1^2 + s2^2 - 2 rho s1 s2),      a = (mu1 - mu2) / theta.

Then, with Phi and phi the standard normal CDF and density,

    E[max(X1, X2)]   = mu1 Phi(a) + mu2 Phi(-a) + theta phi(a)
    E[max(X1, X2)^2] = (mu1^2 + s1^2) Phi(a) + (mu2^2 + s2^2) Phi(-a) + (mu1 + mu2) theta phi(a).

Special case mu1 = mu2 = mu: E[max] = mu + theta / sqrt(2 pi) > mu. This is the
merge bias in one line: two paths that are each on time *on average* give a
project that is late on average.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def clark_max(mu1, s1, mu2, s2, rho=0.0):
    """Mean and standard deviation of max(X1, X2) for jointly Gaussian X1, X2 (exact)."""
    theta2 = s1**2 + s2**2 - 2 * rho * s1 * s2
    if theta2 <= 1e-300:  # X1 - X2 is constant: the max is simply the larger one
        return (mu1, s1) if mu1 >= mu2 else (mu2, s2)
    theta = np.sqrt(theta2)
    a = (mu1 - mu2) / theta
    Pa, Pma, pa = stats.norm.cdf(a), stats.norm.cdf(-a), stats.norm.pdf(a)
    m1 = mu1 * Pa + mu2 * Pma + theta * pa
    m2 = (mu1**2 + s1**2) * Pa + (mu2**2 + s2**2) * Pma + (mu1 + mu2) * theta * pa
    return float(m1), float(np.sqrt(max(m2 - m1**2, 0.0)))


def sculli(project, mu, sigma):
    """Approximate mean and std of the project duration for independent N(mu_i, sigma_i^2) tasks.

    Sculli (1983): go through the network in topological order and keep a Gaussian
    approximation of every finish time. At a merge, take pairwise maxima with
    Clark's formula, *pretending the merging paths are independent* (rho = 0).
    Paths that share tasks are in fact positively correlated, so this is only an
    approximation. Monte Carlo tells us how good it is.
    """
    mu = np.asarray(mu, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    fin_mean = np.zeros(project.k)
    fin_sd = np.zeros(project.k)

    def fold_max(tasks):
        m, s = fin_mean[tasks[0]], fin_sd[tasks[0]]
        for i in tasks[1:]:
            m, s = clark_max(m, s, fin_mean[i], fin_sd[i], rho=0.0)
        return m, s

    for j in project.order:
        preds = project.predecessors[j]
        start_m, start_s = fold_max(preds) if preds else (0.0, 0.0)
        fin_mean[j] = start_m + mu[j]
        fin_sd[j] = np.sqrt(start_s**2 + sigma[j] ** 2)
    return fold_max(list(project.terminals))
