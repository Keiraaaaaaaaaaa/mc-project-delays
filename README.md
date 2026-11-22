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

Everything is in one notebook, [`why_projects_are_late.ipynb`](why_projects_are_late.ipynb). It is
self-contained: it holds the explanations, the proofs and all the code, and it downloads its two datasets
(a few MB) into `data/` the first time it runs. It follows the 5 required parts: motivation, mathematical
foundations, implementation, results, limitations and conclusion. Each function is defined in the section
that first uses it.

To run it, open it and choose **Restart & Run All** (about 20 seconds).

## Getting started

```bash
git clone https://github.com/Keiraaaaaaaaaa/mc-project-delays.git && cd mc-project-delays
```

```bash
python3 -m venv .venv && source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
jupyter notebook why_projects_are_late.ipynb
```

On Windows, use `python` instead of `python3` and `.venv\Scripts\activate` instead of
`source .venv/bin/activate`.

## Repository layout

```
why_projects_are_late.ipynb   the notebook (the only code of the project)
SOURCES.md                    annotated bibliography
data/README.md                the datasets, their licences and how we use them
requirements.txt              Python packages
```
