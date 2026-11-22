"""Reading PSPLIB project networks (Kolisch & Sprecher, 1997). Part 4."""

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
    path = Path(path)
    section = None
    project_info = {}
    successors = {}
    durations = {}

    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("PROJECT INFORMATION"):
                section = "project"
                continue
            if line.startswith("PRECEDENCE RELATIONS"):
                section = "precedence"
                continue
            if line.startswith("REQUESTS/DURATIONS"):
                section = "durations"
                continue
            if line.startswith("RESOURCEAVAILABILITIES"):
                section = None
                continue

            parts = line.split()
            if not parts or not parts[0].isdigit():
                continue

            values = [int(x) for x in parts]
            if section == "project":
                if len(values) < 6:
                    continue
                project_info = {
                    "due_date": values[3],
                    "mpm_time": values[5],
                }
            elif section == "precedence":
                if len(values) < 3:
                    continue
                job = values[0] - 1
                successor_count = values[2]
                successors[job] = [x - 1 for x in values[3:3 + successor_count]]
            elif section == "durations":
                if len(values) < 3:
                    continue
                job = values[0] - 1
                durations[job] = values[2]

    k = max(max(successors, default=-1), max(durations, default=-1)) + 1
    duration_array = [durations[i] for i in range(k)]
    successor_array = [successors.get(i, []) for i in range(k)]
    project = Project.from_successors(duration_array, successor_array)
    info = {
        "due_date": project_info["due_date"],
        "mpm_time": project_info["mpm_time"],
        "name": path.stem,
    }
    return project, info


def psplib_files(family="j30"):
    """Sorted list of the .sm files of one PSPLIB family (after scripts/download_data.py)."""
    return sorted((DATA_DIR / "psplib" / family).rglob("*.sm"))
