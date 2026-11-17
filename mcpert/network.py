"""Project networks: tasks, precedence constraints, and the longest path.

A project is a set of k tasks with precedence constraints: task j can only start
once all its predecessors are finished. With task durations D_1, ..., D_k, the
earliest finish time of task j is

    F_j = D_j + max_{i in pred(j)} F_i        (F_j = D_j if j has no predecessor)

and the project duration is T = max over final tasks of F_j. Equivalently, T is
the length of the longest path through the network:

    T = max over paths P of  sum_{i in P} D_i.

Everything here is vectorised over scenarios: a matrix D of shape (n, k) holds n
simulated scenarios (rows) of the k task durations (columns). One pass over the
tasks in topological order computes all n longest paths at once.
"""

from __future__ import annotations

import numpy as np


class Project:
    """A project network (a directed acyclic graph of tasks).

    Parameters
    ----------
    durations : array of shape (k,)
        Planned single-point duration of each task (what a naive plan uses).
    predecessors : list of k lists of int
        predecessors[j] = tasks that must be finished before task j can start.
    names : list of k str, optional
    """

    def __init__(self, durations, predecessors, names=None):
        self.durations = np.asarray(durations, dtype=float)
        self.k = len(self.durations)
        if len(predecessors) != self.k:
            raise ValueError("need one list of predecessors per task")
        self.predecessors = [[int(i) for i in p] for p in predecessors]
        self.successors = [[] for _ in range(self.k)]
        for j, preds in enumerate(self.predecessors):
            for i in preds:
                self.successors[i].append(j)
        self.names = list(names) if names is not None else [str(i) for i in range(self.k)]
        self.order = self._topological_order()
        # Final tasks: the project ends when all of them are finished.
        self.terminals = np.array([j for j in range(self.k) if not self.successors[j]])

    @classmethod
    def from_successors(cls, durations, successors, names=None):
        """Build a project from successor lists (the format used by PSPLIB)."""
        preds = [[] for _ in successors]
        for i, succ in enumerate(successors):
            for j in succ:
                preds[j].append(i)
        return cls(durations, preds, names)

    def _topological_order(self):
        """Kahn's algorithm: an order in which every task comes after its predecessors."""
        indegree = [len(p) for p in self.predecessors]
        ready = [j for j in range(self.k) if indegree[j] == 0]
        order = []
        while ready:
            i = ready.pop()
            order.append(i)
            for j in self.successors[i]:
                indegree[j] -= 1
                if indegree[j] == 0:
                    ready.append(j)
        if len(order) != self.k:
            raise ValueError("the precedence graph has a cycle")
        return order

    # ------------------------------------------------------------------ longest path

    def _forward_pass(self, D):
        """Finish times F (n, k) and, for each task, the predecessor that finished last."""
        D = np.atleast_2d(np.asarray(D, dtype=float))
        if D.shape[1] != self.k:
            raise ValueError(f"expected {self.k} task durations per scenario, got {D.shape[1]}")
        n = D.shape[0]
        rows = np.arange(n)
        F = np.empty_like(D)
        last_pred = np.full(D.shape, -1)  # -1 = no predecessor
        for j in self.order:
            preds = self.predecessors[j]
            if preds:
                Fp = F[:, preds]
                best = Fp.argmax(axis=1)
                F[:, j] = Fp[rows, best] + D[:, j]
                last_pred[:, j] = np.asarray(preds)[best]
            else:
                F[:, j] = D[:, j]
        return F, last_pred

    def finish_times(self, D):
        """Earliest finish time of every task, shape (n, k)."""
        return self._forward_pass(D)[0]

    def completion_time(self, D):
        """Project duration T (longest path) for each scenario, shape (n,)."""
        return self.finish_times(D)[:, self.terminals].max(axis=1)

    def planned_duration(self):
        """Longest path when every task takes its planned duration (the naive plan)."""
        return float(self.completion_time(self.durations)[0])

    # ------------------------------------------------------------------ critical path

    def critical_tasks(self, D):
        """Boolean array (n, k): is task j on the critical path of scenario s?

        Walk back from the final task that finishes last, each time following the
        predecessor that finished last. Ties go to the first predecessor; they
        have probability 0 when durations are continuous.
        """
        F, last_pred = self._forward_pass(D)
        n = F.shape[0]
        rows = np.arange(n)
        on_path = np.zeros(F.shape, dtype=bool)

        # 1. Start, in every scenario, from the final task that finishes last.
        task = self.terminals[F[:, self.terminals].argmax(axis=1)]
        walking = np.ones(n, dtype=bool)  # scenarios still walking back

        # 2. Mark the task, then step back to its last-finishing predecessor,
        #    until we reach a task with no predecessor.
        while walking.any():
            on_path[rows[walking], task[walking]] = True
            previous = last_pred[rows, task]
            walking &= previous >= 0
            task = np.where(walking, previous, 0)
        return on_path

    def critical_path(self, D=None):
        """Tasks on the critical path of one scenario (planned durations by default)."""
        D = self.durations if D is None else D
        on_path = self.critical_tasks(D)[0]
        return [j for j in self.order if on_path[j]]

    def __repr__(self):
        n_arcs = sum(len(p) for p in self.predecessors)
        return (f"Project({self.k} tasks, {n_arcs} precedence arcs, "
                f"planned duration {self.planned_duration():g})")
