# Why are projects always late? Monte Carlo for project delivery dates

**3ML project, Mathematics of Modern ML (F. Blibeche), Mines Paris - PSL × Albert School. Topic: Monte Carlo.**

**Team:** Brian Ooi, Robin Levasseur, Keira Chang. Oral exam on Wed 25 Nov 2026 (15 min + 5 min of questions).

## Research question

> **Can we trust a Monte Carlo estimate of a project's delivery date, and when does it break down?**

A project is a network of tasks, and its duration is the **longest path** through that network:
`T = max over paths of (sum of task durations)`. Classical planning (PERT) plugs the *average* duration
of each task into this formula. Because a maximum is convex, Jensen's inequality gives `E[T] >= T_PERT`:
the plan is optimistic **even when every task estimate is right on average**. Computing the law of `T`
exactly is #P-hard (Hagstrom, 1988), so we simulate it, and we study how far the simulation can be trusted.

## Who does what

Each of us edits **only their own files**, so there are no merge conflicts.

| Part | Notebook | Code | Tests | Lead |
|---|---|---|---|---|
| 1. Motivation, 2. Maths, 3. Implementation | `notebooks/part1-3_foundations.ipynb` | `network.py`, `durations.py`, `montecarlo.py`, `clark.py`, `data.py`, `examples.py`, `style.py` | `tests/test_core.py` | Keira |
| 4. Results | `notebooks/part4_results.ipynb` | `mcpert/psplib.py`, `mcpert/criticality.py` | `tests/test_part4.py` | Brian |
| 5. Limitations, conclusion | `notebooks/part5_limitations.ipynb` | `mcpert/tails.py` | `tests/test_part5.py` | Robin |

At the end, `python scripts/build_final_notebook.py` merges the three notebooks into
`notebooks/project.ipynb`, the notebook we submit (with the 5 required parts).

Everyone presents their part at the oral, but **everyone must be able to explain every part**.

## Repository layout

```
mcpert/                     the Python package (short, documented functions)
  network.py                project graph, longest path, critical path
  durations.py              task-duration models (Normal, Triangular, Beta-PERT, resampled SiP ratios)
  montecarlo.py             simulation, confidence intervals, variance reduction, coverage
  clark.py                  Clark's formula and Sculli's approximation
  data.py, examples.py      SiP loader, toy projects
  style.py                  plotting style shared by all notebooks
  psplib.py, criticality.py Part 4: real-size networks, criticality index
  tails.py                  Part 5: Pareto model, Hill estimator, importance sampling
notebooks/                  one notebook per part, merged at the end into project.ipynb
scripts/download_data.py    fetches the datasets into data/raw/ (not committed)
scripts/build_final_notebook.py
tests/                      one test file per part
SOURCES.md                  annotated bibliography
data/README.md              the datasets, their licences and how we use them
```

## Getting started

```bash
git clone https://github.com/Keiraaaaaaaaaaa/mc-project-delays.git && cd mc-project-delays
```

```bash
python3 -m venv .venv && source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
python scripts/download_data.py
```

```bash
python tests/test_core.py
```

```bash
jupyter notebook notebooks/
```

`download_data.py` fetches SiP and PSPLIB J30 (a few MB) with `curl`. On Windows, use `python`
instead of `python3` and `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

## Timeline

| Date | What |
|---|---|
| Thu 19 Nov | Supervised session: research question, notebook plan and the maths of Part 2 understood by all three of us |
| Fri 20 Nov | Monte Carlo crash course |
| Sun 22 Nov | Parts 4 and 5 pushed (suggested deadline) |
| Mon 23 to Tue 24 Nov | Merge the notebooks, check everything runs, rehearse the oral |
| Wed 25 Nov | Oral |

## Datasets and sources

See [data/README.md](data/README.md) and [SOURCES.md](SOURCES.md).
