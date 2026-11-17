# Datasets

Nothing in `data/raw/` is committed. Run `python scripts/download_data.py` to fetch it.

We need two kinds of data, because no public dataset has both at a large scale:

1. **How wrong are task estimates?** We need estimated vs actual durations for many real tasks. Source: **SiP**.
2. **What do real project networks look like?** We need tasks with precedence constraints. Source: **PSPLIB**.

Monte Carlo puts them together: PSPLIB gives the network, SiP gives the delay of each task.

## 1. SiP: estimated vs actual effort (main dataset)

- **What:** 12,299 tasks from 10 years of commercial agile software development (Software in Partnership Ltd), 20 project codes, 22 developers. Each task has `HoursEstimate` and `HoursActual`.
- **Paper:** Jones, D. M. & Cullum, S. (2019). *A conversation around the analysis of the SiP effort estimation dataset.* [arXiv:1901.01621](https://arxiv.org/abs/1901.01621)
- **Get it:** <https://github.com/Derek-Jones/SiP_dataset>, files `Sip-task-info.csv` and `est-act-dates.csv`. Read them with `encoding="latin-1"`.
- **Licence:** CC BY-NC-ND 4.0. Non-commercial coursework is fine. Do not redistribute modified copies, which is why we don't commit it.
- **What it shows:** the ratio actual/estimate has median 1.0 but mean 1.8, its 99th percentile is 8.8 and its max is 281. The tail is very heavy, which is exactly what Part 5 needs.

| column | meaning |
|---|---|
| `HoursEstimate`, `HoursActual` | estimated and actual effort (hours) |
| `ProjectCode`, `DeveloperID`, `Category`, `SubCategory`, `Priority` | context, useful to split the ratios by project or task type |
| `est-act-dates.csv` | `EstimateOn`, `StartedOn`, `CompletedOn` dates per `TaskNumber` |

## 2. PSPLIB: project networks (main dataset)

- **What:** the standard benchmark library of project-scheduling instances. Families J30, J60, J90 and J120 (30 to 120 tasks), 480 to 600 instances each. Each `.sm` file gives the precedence graph, a duration per task, resource needs, and the critical-path length (`MPM-Time`).
- **Paper:** Kolisch, R. & Sprecher, A. (1997). PSPLIB: A project scheduling problem library. *EJOR* 96(1), 205-216.
- **Get it:** <https://www.om-db.wi.tum.de/psplib/getdata.php?mode=sm>
  (direct: `download_dataset.php?set=j30&mode=sm&format=zip`). A single sample file is at <https://github.com/PyJobShop/PSPLIB/tree/main/data> (MIT).
- **Use:** we ignore resources and keep the precedence graph plus durations. We read them with `mcpert.psplib.read_psplib`.

## 3. Optional: DSLIB, real projects with planned and actual durations

- **What:** 231 real-life projects (mostly construction) from Ghent University / OR&S. Each project has its baseline schedule and, for many, its tracking data (actual progress). It is the only public dataset with **real networks and real delays together**, so it is ideal for a bonus check: does our model predict the actual delay?
- **Paper to cite:** Batselier, J. & Vanhoucke, M. (2015). Construction and evaluation framework for a real-life project database. *IJPM* 33(3), 697-710.
- **Get it:** <https://github.com/MarioVanhoucke/DSLIB-Dynamic-Scheduling-Empirical-Project-Library/releases/latest> (`DSLIB3.4.zip`, about 137 MB, one Excel file per project, needs `openpyxl`).
- **Cost:** reading the Excel files takes some work. Only do it if Parts 1 to 5 are done.

## Not used, but good to know

- **CESAW** (Jones & Nichols, 2021, [arXiv:2106.03679](https://arxiv.org/abs/2106.03679)): 61,817 Team Software Process tasks with estimates and actuals. It is larger than SiP, but harder to obtain and clean.
- **Flyvbjerg et al. (2022)** studied 5,392 IT projects and found that cost overruns follow a **power law**. The data is not public, but the result supports our heavy-tail part.
