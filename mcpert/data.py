"""Data: download the datasets if they are missing, and load SiP."""

from __future__ import annotations

import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

SIP_URL = "https://raw.githubusercontent.com/Derek-Jones/SiP_dataset/master/"
PSPLIB_URL = "https://www.om-db.wi.tum.de/psplib/download_dataset.php?set={}&mode=sm&format=zip"
DSLIB_URL = ("https://github.com/MarioVanhoucke/DSLIB-Dynamic-Scheduling-Empirical-Project-Library"
             "/releases/download/DSLIB_v3.4/DSLIB3.4.zip")


def fetch(url, dest):
    """Download url to dest, unless dest already exists."""
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {url}")
    tmp = dest.with_suffix(dest.suffix + ".part")
    if shutil.which("curl"):
        # curl uses the system certificates (Python from python.org on macOS often has none).
        subprocess.run(["curl", "-fsSL", "-A", "student-project", "-o", str(tmp), url], check=True)
    else:
        request = urllib.request.Request(url, headers={"User-Agent": "student-project"})
        with urllib.request.urlopen(request) as response, open(tmp, "wb") as f:
            shutil.copyfileobj(response, f)
    tmp.rename(dest)


def unzip(archive, folder):
    """Extract archive into folder, unless folder already has files."""
    if folder.exists() and any(folder.iterdir()):
        return
    folder.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        z.extractall(folder)  # zipfile strips absolute paths and '..'


def ensure_data(families=("j30",), dslib=False):
    """Download SiP and the PSPLIB families we need into DATA_DIR (skips what is there)."""
    for name in ["Sip-task-info.csv", "est-act-dates.csv"]:
        fetch(SIP_URL + name, DATA_DIR / "sip" / name)
    for family in families:
        archive = DATA_DIR / "psplib" / f"{family}.sm.zip"
        fetch(PSPLIB_URL.format(family), archive)
        unzip(archive, DATA_DIR / "psplib" / family)
    if dslib:
        archive = DATA_DIR / "dslib" / "DSLIB3.4.zip"
        fetch(DSLIB_URL, archive)
        unzip(archive, DATA_DIR / "dslib" / "DSLIB3.4")


def load_sip(path=None):
    """SiP effort-estimation dataset (Jones & Cullum, 2019).

    About 12k software tasks with estimated and actual hours. Keeps the tasks where
    both are positive and adds `ratio = HoursActual / HoursEstimate`
    (ratio > 1 means the task took longer than estimated).
    Downloads the data first if it is missing.
    """
    if path is None:
        ensure_data()
        path = DATA_DIR / "sip" / "Sip-task-info.csv"
    df = pd.read_csv(path, encoding="latin-1")
    df = df[(df["HoursEstimate"] > 0) & (df["HoursActual"] > 0)].copy()
    df["ratio"] = df["HoursActual"] / df["HoursEstimate"]
    return df
