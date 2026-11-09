"""Run the DCA vs. Market Timer comparison."""
import pandas as pd

from Source.data import load_prices, monthly_buy_dates
from Source.metrics import summarize
from Source.plots import plot_results
from Source.strategies import drawdown_signal, simulate

TICKER = "SPY"
START, END = "2004-01-01", "2024-12-31"
MONTHLY_AMOUNT = 500.0
WINDOW = 252          # trading days for the trailing peak (also the warm-up)
THRESHOLD = -0.10     # buy when price is 10%+ below trailing peak


def main():
    prices = load_prices(TICKER, START, END)
    signal = drawdown_signal(prices, WINDOW, THRESHOLD)

    # Start both strategies AFTER the indicator warm-up so the comparison is fair
    start = prices.index[WINDOW]
    prices, signal = prices.loc[start:], signal.loc[start:]
    buy_dates = monthly_buy_dates(prices)

    dca = simulate(prices, buy_dates, MONTHLY_AMOUNT)
    timer = simulate(prices, buy_dates, MONTHLY_AMOUNT, signal=signal)

    pd.options.display.float_format = "{:,.4f}".format
    print(f"\n{TICKER} | {prices.index[0].date()} -> {prices.index[-1].date()}\n")
    print(summarize({"DCA": dca, "Timer": timer}))

    plot_results(dca, timer, "growth.png")

main()