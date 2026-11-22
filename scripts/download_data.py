"""Download the datasets into data/raw/ (they are not committed to git).

    python scripts/download_data.py            # SiP + PSPLIB J30 (a few MB)
    python scripts/download_data.py --all      # + PSPLIB J60, J90, J120
    python scripts/download_data.py --dslib    # + DSLIB real-life projects (~137 MB)

Files that are already present are skipped. The notebooks also download
SiP and J30 by themselves when they are missing.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mcpert.data import DATA_DIR, ensure_data  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--all", action="store_true", help="also PSPLIB J60, J90, J120")
    parser.add_argument("--dslib", action="store_true", help="also DSLIB (~137 MB)")
    args = parser.parse_args()

    families = ("j30", "j60", "j90", "j120") if args.all else ("j30",)
    ensure_data(families, dslib=args.dslib)
    print(f"data ready in {DATA_DIR}")


if __name__ == "__main__":
    main()
