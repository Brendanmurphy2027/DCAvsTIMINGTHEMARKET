import pandas as pd

def simulate(prices: pd.Series, buy_dates, amount: float = 500.0, signal: pd.Series | None = None) -> pd.DataFrame:
    buy_set = set(buy_dates)
    shares = cash = deposited = 0.0
    trades = 0
    rows = []

    for date, price in prices.items():
        flow = 0.0
        if date in buy_set:
            flow = amount
            deposited += amount
            if signal is None:
                shares += amount / price
                trades += 1
            else:
                cash += amount

        if signal is not None and cash > 0 and bool(signal.at[date]):
            shares += cash / price
            cash = 0.0
            trades += 1

        rows.append((date, shares, cash, deposited, flow,
                     shares * price + cash, trades))

    cols = ["date", "shares", "cash", "deposited", "flow", "value", "trades"]
    return pd.DataFrame(rows, columns=cols).set_index("date")


def drawdown_signal(prices: pd.Series, window: int = 252, threshold: float = -0.10) -> pd.Series:
    peak = prices.rolling(window, min_periods=window).max()
    dip = (prices / peak - 1) <= threshold
    return dip.shift(1, fill_value=False)


def sma_signal(prices: pd.Series, window: int = 200) -> pd.Series:
    sma = prices.rolling(window, min_periods=window).mean()
    below = prices < sma
    return below.shift(1, fill_value=False)