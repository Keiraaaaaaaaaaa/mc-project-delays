"""Merge the three part notebooks into the final deliverable, notebooks/project.ipynb.

    python scripts/build_final_notebook.py

Run it at the end, once all parts are done. Each part notebook starts with the same
setup cell (tagged "setup"); only the first one is kept. Outputs are cleared:
open project.ipynb and run "Restart & Run All" before submitting.
"""

from pathlib import Path

import nbformat

NOTEBOOKS = Path(__file__).resolve().parent.parent / "notebooks"
PARTS = ["part1-3_foundations.ipynb", "part4_results.ipynb", "part5_limitations.ipynb"]


def main():
    merged = nbformat.read(NOTEBOOKS / PARTS[0], as_version=4)
    for name in PARTS[1:]:
        part = nbformat.read(NOTEBOOKS / name, as_version=4)
        merged.cells += [c for c in part.cells if "setup" not in c.metadata.get("tags", [])]

    for cell in merged.cells:
        if cell.cell_type == "code":
            cell.outputs, cell.execution_count = [], None

    nbformat.write(merged, NOTEBOOKS / "project.ipynb")
    print(f"wrote notebooks/project.ipynb ({len(merged.cells)} cells)")


if __name__ == "__main__":
    main()
