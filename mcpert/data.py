"""Where the data lives, and the SiP loader (see data/README.md)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def load_sip(path=None):
    """SiP effort-estimation dataset (Jones & Cullum, 2019).

    About 12k software tasks with estimated and actual hours. Keeps the tasks where
    both are positive and adds `ratio = HoursActual / HoursEstimate`
    (ratio > 1 means the task took longer than estimated).
    """
    path = Path(path) if path is not None else DATA_DIR / "sip" / "Sip-task-info.csv"
    df = pd.read_csv(path, encoding="latin-1")
    df = df[(df["HoursEstimate"] > 0) & (df["HoursActual"] > 0)].copy()
    df["ratio"] = df["HoursActual"] / df["HoursEstimate"]
    return df
