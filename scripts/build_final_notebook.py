"""Build the notebook we submit: notebooks/project.ipynb.

    python scripts/build_final_notebook.py

The instructions ask for a SELF-CONTAINED notebook, so this script:
1. merges the three part notebooks (Parts 1-3, Part 4, Part 5);
2. copies the code of every mcpert module into the notebook, one cell per module,
   in a "Code" section before Part 1, so the notebook does not import mcpert;
3. removes the `mc.` prefix in the experiments, and lets the notebook download
   the data next to itself when it is run outside the repository.

Run it at the end, once all parts are done. Then open notebooks/project.ipynb and
run "Restart & Run All" before submitting.
"""

import ast
import re
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "notebooks"
PARTS = ["part1-3_foundations.ipynb", "part4_results.ipynb", "part5_limitations.ipynb"]
# Order matters: each module only uses the ones above it.
MODULES = ["style", "network", "durations", "montecarlo", "clark", "data",
           "psplib", "criticality", "tails", "examples"]

DATA_DIR_IN_PACKAGE = 'DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"'
DATA_DIR_IN_NOTEBOOK = (
    "# Data folder: data/raw of the repository when the notebook is run from it,\n"
    "# otherwise a folder called data next to the notebook.\n"
    'DATA_DIR = Path("../data/raw") if Path("../data/raw").exists() else Path("data")'
)
PACKAGE_SENTENCE = "The simulation code is a small package, `mcpert`, next to this notebook:"
NOTEBOOK_SENTENCE = "The simulation code is defined in the section *Code* at the top of this notebook, one cell per module:"

CODE_INTRO = """
---
## Code

All the simulation code of the project is defined here, one cell per module, so that the notebook runs on
its own. Each function is short and documented. Part 3 explains how the code works and checks it against
exact results. The datasets (SiP and PSPLIB J30, a few MB) are downloaded the first time they are needed.
"""


# ---------------------------------------------------------------------- modules -> cells

def module_to_cell(name):
    """Source of mcpert/<name>.py as a notebook cell, and the imports it needs.

    The module docstring becomes a comment banner, and the import lines are removed:
    imports between our own modules are useless in a single notebook, and the other
    imports are gathered in the setup cell.
    """
    source = (ROOT / "mcpert" / f"{name}.py").read_text()
    tree = ast.parse(source)
    lines = source.splitlines()
    removed, imports = set(), []

    for node in tree.body:
        is_docstring = node is tree.body[0] and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
        is_import = isinstance(node, (ast.Import, ast.ImportFrom))
        if is_docstring or is_import:
            removed.update(range(node.lineno - 1, node.end_lineno))
        if is_import:
            internal = isinstance(node, ast.ImportFrom) and (node.level > 0 or node.module == "__future__")
            if not internal:
                imports.append(ast.get_source_segment(source, node))

    docstring = ast.get_docstring(tree) or ""
    banner = (["# " + "=" * 70, f"# {name}.py"]
              + [f"# {line}".rstrip() for line in docstring.splitlines()]
              + ["# " + "=" * 70])
    body = "\n".join(line for i, line in enumerate(lines) if i not in removed).strip("\n")
    code = "\n".join(banner) + "\n\n" + re.sub(r"\n{4,}", "\n\n\n", body) + "\n"

    if name == "data":
        if DATA_DIR_IN_PACKAGE not in code:
            sys.exit("build_final_notebook: could not find the DATA_DIR line in data.py")
        code = code.replace(DATA_DIR_IN_PACKAGE, DATA_DIR_IN_NOTEBOOK)
    if name == "style":
        code += "\n\nuse_style()\n"
    return code, imports


def setup_cell(imports):
    """One cell with every import (standard library first) and the random seed."""
    unique = list(dict.fromkeys(imports + ["from IPython.display import display"]))

    def top_module(line):
        return line.split()[1].split(".")[0]

    stdlib = sorted((i for i in unique if top_module(i) in sys.stdlib_module_names), key=str.lower)
    others = sorted((i for i in unique if top_module(i) not in sys.stdlib_module_names),
                    key=lambda i: top_module(i).lower())
    return ("# Setup: imports and random seed\n" + "\n".join(stdlib) + "\n\n" + "\n".join(others)
            + "\n\nSEED = 2026  # every number in this notebook is reproducible\n")


# ---------------------------------------------------------------------- experiments

def without_package(source):
    """Experiment cell without the `mc.` prefix and without imports of mcpert."""
    lines = [line for line in source.splitlines()
             if not re.match(r"\s*(import mcpert|from mcpert)", line)]
    return re.sub(r"\bmc\.", "", "\n".join(lines))


class AssignedNames(ast.NodeVisitor):
    """Names assigned at the top level of a cell (not inside functions or comprehensions)."""

    def __init__(self):
        self.names = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.names.add(node.id)

    def visit_FunctionDef(self, node):
        self.names.add(node.name)

    visit_ClassDef = visit_FunctionDef

    def _skip(self, node):
        pass

    visit_Lambda = visit_ListComp = visit_SetComp = visit_DictComp = visit_GeneratorExp = _skip


def names_defined_by(code):
    finder = AssignedNames()
    finder.visit(ast.parse(code))
    return finder.names


def check_no_clash(module_names, cells):
    """Stop if an experiment overwrites a function of the code section (e.g. `coverage = ...`)."""
    clashes = {}
    for cell in cells:
        if cell.cell_type != "code":
            continue
        code = "\n".join(line for line in cell.source.splitlines() if not line.lstrip().startswith(("%", "!")))
        for name in names_defined_by(code) & module_names:
            clashes.setdefault(name, code.splitlines()[0])
    if clashes:
        details = "\n".join(f"  {name!r} in the cell starting with: {first}" for name, first in clashes.items())
        sys.exit("build_final_notebook: these variables would overwrite functions of the code section.\n"
                 f"Rename them in the part notebooks:\n{details}")


# ---------------------------------------------------------------------- main

def main():
    # 1. The code section, and the imports it needs.
    module_cells, imports = [], []
    for name in MODULES:
        code, needed = module_to_cell(name)
        module_cells.append(nbformat.v4.new_code_cell(code))
        imports += needed
    module_names = set().union(*(names_defined_by(c.source) for c in module_cells))

    # 2. The experiments of the three parts, without their setup cells.
    parts = [nbformat.read(NOTEBOOKS / name, as_version=4) for name in PARTS]
    first_cells = parts[0].cells
    setup_index = next(i for i, c in enumerate(first_cells) if "setup" in c.metadata.get("tags", []))
    experiments = [c for part in parts for c in part.cells if "setup" not in c.metadata.get("tags", [])]
    head, experiments = experiments[:setup_index], experiments[setup_index:]

    for cell in experiments:
        if cell.cell_type == "code":
            cell.source = without_package(cell.source)
        elif PACKAGE_SENTENCE in cell.source:
            cell.source = cell.source.replace(PACKAGE_SENTENCE, NOTEBOOK_SENTENCE)
    check_no_clash(module_names, experiments)

    # 3. Assemble: title, setup, code section, then Parts 1 to 5.
    final = parts[0]
    final.cells = (head
                   + [nbformat.v4.new_code_cell(setup_cell(imports), metadata={"tags": ["setup"]}),
                      nbformat.v4.new_markdown_cell(CODE_INTRO.strip())]
                   + module_cells
                   + experiments)
    for cell in final.cells:
        if cell.cell_type == "code":
            cell.outputs, cell.execution_count = [], None
    nbformat.write(final, NOTEBOOKS / "project.ipynb")
    print(f"wrote notebooks/project.ipynb ({len(final.cells)} cells, {len(module_cells)} code modules)")


if __name__ == "__main__":
    main()
