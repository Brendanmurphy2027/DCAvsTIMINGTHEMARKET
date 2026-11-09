import matplotlib.pyplot as plt

from Source.metrics import max_drawdown

CRISES = [
    ("2007-10-09", "2009-03-09", "2008 Financial Crisis"),
    ("2020-02-19", "2020-03-23", "2020 COVID Crash"),
]


def _shade_crises(ax, start, end):
    for s, e, label in CRISES:
        if e < str(start.date()) or s > str(end.date()):
            continue  # crisis outside the simulated window
        ax.axvspan(s, e, color="red", alpha=0.15, label=label)


def plot_results(dca, timer, path="growth.png"):
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 9), sharex=True,
        gridspec_kw={"height_ratios": [2, 1]})

    # --- Top panel: portfolio value ---
    ax1.plot(dca.index, dca["value"], lw=1.8, label="DCA ($500/mo)")
    ax1.plot(timer.index, timer["value"], lw=1.8, label="Market Timer")
    ax1.plot(dca.index, dca["deposited"], "k--", lw=1, label="Cash deposited")
    _shade_crises(ax1, dca.index[0], dca.index[-1])
    ax1.set_ylabel("Portfolio Value (USD)")
    ax1.set_title("DCA vs. Drawdown-Triggered Market Timing")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left")

    # --- Bottom panel: drawdowns ---
    ax2.plot(dca.index, max_drawdown(dca)[1] * 100, lw=1.3, label="DCA")
    ax2.plot(timer.index, max_drawdown(timer)[1] * 100, lw=1.3, label="Market Timer")
    _shade_crises(ax2, dca.index[0], dca.index[-1])
    ax2.set_xlabel("Timeline")
    ax2.set_ylabel("Drawdown (%)")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="lower left")

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.show()