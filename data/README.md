# Datasets

The notebook downloads the data into this folder the first time it runs. Nothing here is committed
except this file.

We need two kinds of data, because no public dataset has both at a large scale:

1. **How wrong are task estimates?** We need estimated vs actual durations for many real tasks. Source: **SiP**.
2. **What do real project networks look like?** We need tasks with precedence constraints. Source: **PSPLIB**.

Monte Carlo puts them together: PSPLIB gives the network, SiP gives the delay of each task.

## 1. SiP: estimated vs actual effort

- **What:** 12,299 tasks from 10 years of commercial agile software development (Software in Partnership Ltd), 20 project codes, 22 developers. Each task has `HoursEstimate` and `HoursActual`.
- **Paper:** Jones, D. M. & Cullum, S. (2019). *A conversation around the analysis of the SiP effort estimation dataset.* [arXiv:1901.01621](https://arxiv.org/abs/1901.01621)
- **Source:** <https://github.com/Derek-Jones/SiP_dataset>, file `Sip-task-info.csv` (read with `encoding="latin-1"`). Saved as `data/sip/Sip-task-info.csv`.
- **Licence:** CC BY-NC-ND 4.0. Non-commercial coursework is fine. Do not redistribute modified copies, which is why we don't commit it.
- **What it shows:** the ratio actual/estimate has median 1.0 but mean 1.8, its 99th percentile is 8.8 and its max is 281. The tail is very heavy (Part 5 of the notebook).

## 2. PSPLIB: project networks

- **What:** the standard benchmark library of project-scheduling instances. We use the J30 family: 480 networks of 30 tasks (32 with the dummy start and end tasks). Each `.sm` file gives the precedence graph, a duration per task, resource needs, and the critical-path length (`MPM-Time`).
- **Paper:** Kolisch, R. & Sprecher, A. (1997). PSPLIB: A project scheduling problem library. *EJOR* 96(1), 205-216.
- **Source:** <https://www.om-db.wi.tum.de/psplib/getdata.php?mode=sm> (direct: `download_dataset.php?set=j30&mode=sm&format=zip`). Saved in `data/psplib/j30/`.
- **Use:** we ignore resources and keep the precedence graph and the durations (`read_psplib`, Section 4.3 of the notebook). Our longest path equals the `MPM-Time` of the file for all 480 networks, which checks the parser.

## Not used, but good to know

- **DSLIB** (Batselier & Vanhoucke, 2015, *IJPM* 33(3), 697-710): 231 real projects, mostly construction, with baseline schedules and tracking data. It is the only public dataset with real networks and real delays together, so it would allow a check of our model on real projects (Section 5.6). Source: <https://github.com/MarioVanhoucke/DSLIB-Dynamic-Scheduling-Empirical-Project-Library>.
- **CESAW** (Jones & Nichols, 2021, [arXiv:2106.03679](https://arxiv.org/abs/2106.03679)): 61,817 Team Software Process tasks with estimates and actuals. It is larger than SiP, but harder to obtain and clean.
- **Flyvbjerg et al. (2022)** studied 5,392 IT projects and found that cost overruns follow a **power law**. The data is not public, but the result supports Part 5.
