# Sources

★ = read this first. The "Part" column says where each source is used in the notebook.

## Monte Carlo theory (Parts 2, 3, 5)

| | Reference | Why we use it | Part |
|---|---|---|---|
| ★ | **Course notes, Ch. 1**: Hoeffding, confidence radii, coverage experiment, "When concentration is not enough" | Our intervals and our coverage experiment copy this method | 2, 3, 5 |
| ★ | Owen, A. B. (2013). *Monte Carlo theory, methods and examples.* Free online: <https://artowen.su.domains/mc/> | Best free textbook. Ch. 2 covers simple MC and error estimates, Ch. 8 antithetic variables and control variates, Ch. 9 importance sampling | 2, 5 |
| | Glasserman, P. (2003). *Monte Carlo Methods in Financial Engineering*, Ch. 4. Springer | Clear proofs for antithetic variables and control variates (the optimal β, variance factor 1 − ρ²) | 2 |
| | Esary, Proschan & Walkup (1967). Association of random variables, with applications. *Ann. Math. Stat.* 38(5), 1466-1474 | Why antithetic variables work here: T is increasing in every Dᵢ, so T(U) and T(1−U) are negatively correlated | 2 |
| | Massart, P. (1990). The tight constant in the Dvoretzky-Kiefer-Wolfowitz inequality. *Ann. Probab.* 18(3), 1269-1283 | A confidence band for the whole CDF of T (a Hoeffding bound that holds for all dates at once) | 2 |
| | Boucheron, Lugosi & Massart (2013). *Concentration Inequalities*, §2.5. Oxford UP | Maximal inequality E[max of N sub-Gaussians] ≤ σ√(2 ln N), giving an upper bound on the delay | 2 (optional) |
| | Hill, B. M. (1975). A simple general approach to inference about the tail of a distribution. *Ann. Stat.* 3(5), 1163-1174 | Tail-index estimator: is the variance of the SiP ratios even finite? | 5 |

## Project scheduling under uncertainty (Parts 1, 2, 4)

| | Reference | Why we use it | Part |
|---|---|---|---|
| | Malcolm, Roseboom, Clark & Fazar (1959). Application of a technique for R&D program evaluation. *Oper. Res.* 7(5), 646-669 | The original PERT: three-point estimates, mean (a + 4m + b)/6 | 1 |
| ★ | Clark, C. E. (1961). The greatest of a finite set of random variables. *Oper. Res.* 9(2), 145-162 | Exact E[max] of two Gaussians. Our analytic check of the simulator | 2, 3 |
| ★ | Van Slyke, R. M. (1963). Monte Carlo methods and the PERT problem. *Oper. Res.* 11(5), 839-860 | First Monte Carlo study of PERT networks. Introduces the criticality index | 2, 4 |
| | MacCrimmon & Ryavec (1964). An analytical study of the PERT assumptions. *Oper. Res.* 12(1), 16-37 | Quantifies the "merge bias": PERT is optimistic at every merge of paths | 1, 2 |
| ★ | Hagstrom, J. N. (1988). Computational complexity of PERT problems. *Networks* 18(2), 139-147 | Computing P(T ≤ t), or even E[T], is #P-hard. This is why Monte Carlo is needed | 1, 2 |
| | Sculli, D. (1983). The completion time of PERT networks. *J. Oper. Res. Soc.* 34(2), 155-158 | Clark's formula applied through the whole network, assuming independent paths. An analytic approximation that Monte Carlo can test | 3, 4 |
| | Sullivan, Hayya & Schaul (1982). Efficiency of the antithetic variate method for simulating stochastic networks. *Mgmt. Sci.* 28(5), 563-572; and Grant (1983), *Mgmt. Sci.* 29(3), 381-384 | Antithetic variables on project networks. Reported gain: the same precision for about 1/4 of the computation | 2, 4 |
| | Dodin & Elmaghraby (1985). Approximating the criticality indices of the activities in PERT networks. *Mgmt. Sci.* 31(2), 207-223 | Criticality indices, checked against Monte Carlo | 4 |
| | Elmaghraby, S. E. (2000). On criticality and sensitivity in activity networks. *EJOR* 127(2), 220-238 | Criticality index vs sensitivity ∂E[T]/∂μᵢ | 2, 4 |
| | Baccelli, Cohen, Olsder & Quadrat (1992). *Synchronization and Linearity: An Algebra for Discrete Event Systems.* Wiley | Max-plus algebra for networks with synchronisation: the reference for the tropical view of project durations | 2 (remark) |
| | Maclagan & Sturmfels (2015). *Introduction to Tropical Geometry.* Graduate Studies in Mathematics 161, AMS | Tropical polynomials are maxima of linear functions, hence convex: the convexity behind Jensen's inequality for T | 2 (remark) |

## Why real projects are late (Part 1, Part 5)

| | Reference | Why we use it | Part |
|---|---|---|---|
| | Kahneman & Tversky (1979). Intuitive prediction: biases and corrective procedures. *TIMS Studies in Mgmt. Sci.* 12, 313-327 | The "planning fallacy" | 1 |
| | Buehler, Griffin & Ross (1994). Exploring the "planning fallacy". *J. Pers. Soc. Psychol.* 67(3), 366-381 | Experimental evidence that people underestimate completion times | 1 |
| ★ | Flyvbjerg, Budzier, Lee, Keil, Lunn & Bester (2022). The empirical reality of IT project cost overruns: discovering a power-law distribution. *JMIS* 39(3), 607-639. [arXiv:2210.01573](https://arxiv.org/abs/2210.01573) | 5,392 IT projects: overruns are fat-tailed (power law). Real-world support for our heavy-tail part | 1, 5 |
| | Flyvbjerg, B. (2006). From Nobel Prize to project management: getting risks right. *Project Mgmt. J.* 37(3), 5-15 | Reference-class forecasting: use past projects' delays. This is what our SiP bootstrap does | 4, 5 |

## Datasets

See [data/README.md](data/README.md).

| | Dataset | Paper |
|---|---|---|
| ★ | **SiP**: 12,299 tasks, estimate vs actual | Jones & Cullum (2019), [arXiv:1901.01621](https://arxiv.org/abs/1901.01621) |
| ★ | **PSPLIB**: J30 to J120 project networks | Kolisch & Sprecher (1997), *EJOR* 96(1), 205-216 |
| | **DSLIB**: 231 real projects, baseline and tracking data (optional) | Batselier & Vanhoucke (2015), *IJPM* 33(3), 697-710 |
| | **CESAW**: 61,817 tasks (not used) | Jones & Nichols (2021), [arXiv:2106.03679](https://arxiv.org/abs/2106.03679) |
