"""Reading PSPLIB project networks (Kolisch & Sprecher, 1997). Part 4, Brian.

TODO (Brian): implement read_psplib. Run
`python tests/test_part4.py` until every test passes.
"""

from __future__ import annotations

from pathlib import Path

from .data import DATA_DIR
from .network import Project


def read_psplib(path):
    """Read a PSPLIB single-mode instance (.sm file).

    Keep the precedence graph and the task durations, and ignore resources.
    Renumber jobs from 0. Job 0 and the last job are dummy start/end tasks
    of duration 0.

    The useful sections of the file are:
      PROJECT INFORMATION   row: pronr. #jobs rel.date duedate tardcost MPM-Time
      PRECEDENCE RELATIONS  rows: jobnr. #modes #successors successor_1 successor_2 ...
      REQUESTS/DURATIONS    rows: jobnr. mode duration R1 R2 R3 R4

    Returns (project, info), where
      project = Project.from_successors(durations, successors)
      info    = {"due_date": ..., "mpm_time": ..., "name": file name without extension}.
    `mpm_time` is the critical-path length given in the file, a free check of the
    parser: project.planned_duration() must equal it.
    """
    raise NotImplementedError("Part 4 (Brian): read_psplib")


def psplib_files(family="j30"):
    """Sorted list of the .sm files of one PSPLIB family (after scripts/download_data.py)."""
    return sorted((DATA_DIR / "psplib" / family).rglob("*.sm"))
