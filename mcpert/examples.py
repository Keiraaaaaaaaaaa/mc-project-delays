"""Small hand-made projects used in the notebook and the tests."""

from __future__ import annotations

from .durations import BetaPERT
from .network import Project


def dinner():
    """Two dishes, 60 minutes each, cooked in parallel. Dinner is ready when both are.

    If each dish takes 50 or 70 minutes with probability 1/2 (mean 60, so the plan
    is unbiased), then dinner takes max(D1, D2): E = 65 min and P(on time) = 1/4.
    """
    return Project([60, 60], [[], []], names=["starter", "main course"])


def software_release():
    """A 7-task software project (durations in days), with three-point estimates.

        spec -> backend  -> integration -> release
             -> frontend ->
             -> database ->
             -> docs  ---------------------^

    Backend, frontend and database run in parallel and merge at integration.
    This merge is where the plan becomes optimistic.
    Returns (project, BetaPERT model). The project's planned durations are the
    "most likely" values m.
    """
    names = ["spec", "backend", "frontend", "database", "docs", "integration", "release"]
    a = [3, 7, 6, 4, 2, 3, 1]       # optimistic
    m = [5, 10, 9, 6, 4, 5, 1]      # most likely (the plan)
    b = [9, 20, 18, 12, 8, 12, 2]   # pessimistic
    preds = [[], [0], [0], [0], [0], [1, 2, 3], [4, 5]]
    return Project(m, preds, names), BetaPERT(a, m, b)
