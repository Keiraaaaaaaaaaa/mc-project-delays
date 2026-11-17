"""Download the datasets into data/raw/ (they are not committed to git).

    python scripts/download_data.py            # SiP + PSPLIB J30 (a few MB)
    python scripts/download_data.py --all      # + PSPLIB J60, J90, J120
    python scripts/download_data.py --dslib    # + DSLIB real-life projects (~137 MB)

Files that are already present are skipped.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

SIP = "https://raw.githubusercontent.com/Derek-Jones/SiP_dataset/master/"
PSPLIB = "https://www.om-db.wi.tum.de/psplib/download_dataset.php?set={}&mode=sm&format=zip"
DSLIB = ("https://github.com/MarioVanhoucke/DSLIB-Dynamic-Scheduling-Empirical-Project-Library"
         "/releases/download/DSLIB_v3.4/DSLIB3.4.zip")


def fetch(url, dest):
    if dest.exists():
        print(f"  already there: {dest.relative_to(RAW)}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {url}")
    tmp = dest.with_suffix(dest.suffix + ".part")
    if shutil.which("curl"):
        # curl uses the system certificates (Python from python.org on macOS often has none).
        subprocess.run(["curl", "-fsSL", "-A", "mcpert-student-project", "-o", str(tmp), url], check=True)
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "mcpert-student-project"})
        with urllib.request.urlopen(req) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
    tmp.rename(dest)
    print(f"  saved {dest.relative_to(RAW)} ({dest.stat().st_size / 1e6:.1f} MB)")


def unzip(archive, folder):
    if folder.exists() and any(folder.iterdir()):
        return
    folder.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        z.extractall(folder)  # zipfile strips absolute paths and '..'
    print(f"  extracted to {folder.relative_to(RAW)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--all", action="store_true", help="also PSPLIB J60, J90, J120")
    parser.add_argument("--dslib", action="store_true", help="also DSLIB (~137 MB)")
    args = parser.parse_args()

    print("SiP (Jones & Cullum 2019, CC BY-NC-ND 4.0)")
    for name in ["Sip-task-info.csv", "est-act-dates.csv"]:
        fetch(SIP + name, RAW / "sip" / name)

    families = ["j30", "j60", "j90", "j120"] if args.all else ["j30"]
    print("PSPLIB (Kolisch & Sprecher 1997)")
    for fam in families:
        archive = RAW / "psplib" / f"{fam}.sm.zip"
        fetch(PSPLIB.format(fam), archive)
        unzip(archive, RAW / "psplib" / fam)

    if args.dslib:
        print("DSLIB (Batselier & Vanhoucke 2015)")
        archive = RAW / "dslib" / "DSLIB3.4.zip"
        fetch(DSLIB, archive)
        unzip(archive, RAW / "dslib" / "DSLIB3.4")


if __name__ == "__main__":
    main()
