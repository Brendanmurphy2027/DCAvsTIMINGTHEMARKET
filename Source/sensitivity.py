import pandas as pd

from Source.data import load_prices, monthly_buy_dates
from Source.metrics import max_drawdown, xirr
from Source.strategies import drawdown_signal, simulate

WARMUP = 252
prices_full = load_prices("SPY", "2004-01-01", "2024-12-31")

rows = []
for window in (100, 200, 252):
    for threshold in (-0.05, -0.10, -0.15, -0.20):
        sig = drawdown_signal(prices_full, window, threshold)
        start = prices_full.index[WARMUP]
        prices, sig = prices_full.loc[start:], sig.loc[start:]
        dates = monthly_buy_dates(prices)

        dca = simulate(prices, dates)
        timer = simulate(prices, dates, signal=sig)
        rows.append({
            "window": window,
            "threshold": f"{threshold:.0%}",
            "timer_final": timer["value"].iloc[-1],
            "dca_final": dca["value"].iloc[-1],
            "timer_xirr": xirr(timer),
            "dca_xirr": xirr(dca),
            "timer_maxdd": max_drawdown(timer)[0],
            "timer_wins": timer["value"].iloc[-1] > dca["value"].iloc[-1],
        })

pd.options.display.float_format = "{:,.3f}".format
print(pd.DataFrame(rows).to_string(index=False))