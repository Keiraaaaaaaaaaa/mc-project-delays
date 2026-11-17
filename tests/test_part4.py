"""Checks for Part 4 (Brian). Run with `python tests/test_part4.py` until all pass.

They test mcpert/psplib.py and mcpert/criticality.py.
"""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import mcpert as mc  # noqa: E402
from mcpert.examples import software_release  # noqa: E402


def test_read_psplib_on_small_file():
    project, info = mc.read_psplib(ROOT / "tests" / "fixtures" / "tiny.sm")
    assert project.k == 6
    assert info == {"due_date": 10, "mpm_time": 9, "name": "tiny"}
    assert project.planned_duration() == info["mpm_time"]
    assert project.critical_path() == [0, 2, 4, 5]


def test_read_psplib_on_all_j30_networks():
    files = mc.psplib_files("j30")
    assert files, "run `python scripts/download_data.py` first"
    for f in files:
        project, info = mc.read_psplib(f)
        assert project.k == 32
        assert project.planned_duration() == info["mpm_time"], f.name


def test_criticality_index():
    project, model = software_release()
    crit = dict(zip(project.names, mc.criticality_index(project, model, 20_000, rng=8)))
    assert np.isclose(crit["spec"], 1) and np.isclose(crit["release"], 1)
    # exactly one of the four parallel branches is critical in every scenario
    assert np.isclose(crit["backend"] + crit["frontend"] + crit["database"] + crit["docs"], 1)
    assert 0.55 < crit["backend"] < 0.70 and 0.28 < crit["frontend"] < 0.42


def test_shift_sensitivity_equals_criticality():
    # The theorem of Part 4: dE[T]/dmu_i = P(i is critical)
    project, model = software_release()
    crit = mc.criticality_index(project, model, 50_000, rng=9)
    for name in ["backend", "frontend", "docs"]:
        i = project.names.index(name)
        slope = mc.shift_sensitivity(project, model, task=i, h=0.01, n=50_000, rng=10)
        assert abs(slope.value - crit[i]) < 0.02, name


if __name__ == "__main__":
    from _runner import run
    run(globals())
