# Why are projects always late? Monte Carlo for project delivery dates

**3ML project, Mathematics of Modern ML (F. Blibeche), Mines Paris - PSL × Albert School. Topic: Monte Carlo.**

**Team:** Brian Ooi, Robin Levasseur, Keira Chang.

## Research question

> **Can we trust a Monte Carlo estimate of a project's delivery date, and when does it break down?**

A project is a network of tasks, and its duration is the **longest path** through that network:
`T = max over paths of (sum of task durations)`. Classical planning (PERT) plugs the *average* duration
of each task into this formula. Because a maximum is convex, Jensen's inequality gives `E[T] >= T_PERT`:
the plan is optimistic **even when every task estimate is right on average**. Computing the law of `T`
exactly is #P-hard (Hagstrom, 1988), so we simulate it, and we study how far the simulation can be trusted.

## What we find

- Monte Carlo gives the delivery date with an error of order `1/sqrt(n)`, whatever the size of the network,
  and it matches exact formulas where they exist. Antithetic variables and a control variate divide its cost by about 4.
- The probability of being on time and the 90% date come with error bars that need no assumption
  (Hoeffding, order statistics). The CLT error bar on the *mean* breaks down with heavy-tailed delays,
  which is what real overruns look like.
- Rare catastrophic delays need importance sampling designed for heavy tails, and no amount of simulation
  corrects a wrong model of how task delays depend on each other.

## The notebook

`notebooks/project.ipynb` is the notebook we submit. It is **self-contained**: it includes all the code,
downloads the data the first time it runs, and contains the 5 required parts (motivation, mathematical
foundations, implementation, results, limitations and conclusion).

It is built from three working notebooks (`part1-3_foundations`, `part4_results`, `part5_limitations`)
and from the `mcpert` package:

```bash
python scripts/build_final_notebook.py
```

Then open `notebooks/project.ipynb` and run **Restart & Run All**.

## Repository layout

```
mcpert/                     the Python package (short, documented functions)
  network.py                project graph, longest path, critical path
  durations.py              task-duration models (Normal, Triangular, Beta-PERT, resampled SiP ratios)
  montecarlo.py             simulation, confidence intervals, variance reduction, coverage
  clark.py                  Clark's formula and Sculli's approximation
  data.py, examples.py      data download, SiP loader, toy projects
  style.py                  plotting style shared by all notebooks
  psplib.py, criticality.py real-size networks, criticality index
  tails.py                  Pareto model, Hill estimator, importance sampling
notebooks/                  working notebooks, merged into project.ipynb
scripts/download_data.py    fetches the datasets into data/raw/ (not committed)
scripts/build_final_notebook.py
tests/                      checks of the package
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
python tests/test_core.py && python tests/test_part4.py && python tests/test_part5.py
```

```bash
jupyter notebook notebooks/project.ipynb
```

`download_data.py` fetches SiP and PSPLIB J30 (a few MB) with `curl`. On Windows, use `python`
instead of `python3` and `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

## Datasets and sources

See [data/README.md](data/README.md) and [SOURCES.md](SOURCES.md).
