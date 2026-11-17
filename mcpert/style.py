"""Shared plotting style, so that the three parts of the notebook look the same."""

import matplotlib.pyplot as plt

# Series colours, always used in this order: blue first, then orange, then aqua.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
# Text and reference lines.
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def use_style():
    """Thin lines, light grid, no top/right frame."""
    plt.rcParams.update({
        "figure.figsize": (7, 3.6),
        "figure.dpi": 110,
        "axes.prop_cycle": plt.cycler(color=[BLUE, ORANGE, AQUA]),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "axes.titlesize": 11,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "lines.linewidth": 2,
        "legend.frameon": False,
    })
