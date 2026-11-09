from pathlib import Path
import pandas as pd
import yfinance as yf


def load_prices(ticker: str = "SPY", start: str = "2004-01-01", end: str = "2024-12-31", cache_dir: str = "data") -> pd.Series:
    cache = Path(cache_dir) / f"{ticker}_{start}_{end}.csv"
    if cache.exists():
        return pd.read_csv(cache, index_col=0, parse_dates=True)["price"]

    df = yf.download(ticker, start=start, end=end,
                     auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data returned for {ticker}")

    prices = df["Close"]
    if isinstance(prices, pd.DataFrame):
        prices = prices.squeeze("columns")
    prices = prices.dropna().rename("price")
    prices.index = pd.to_datetime(prices.index)
    prices.index.name = "date"

    assert prices.index.is_monotonic_increasing, "Dates out of order"
    assert (prices > 0).all(), "Non-positive prices found"

    cache.parent.mkdir(exist_ok=True)
    prices.to_frame().to_csv(cache)
    return prices


def monthly_buy_dates(prices: pd.Series) -> pd.DatetimeIndex:
    first_days = prices.groupby([prices.index.year, prices.index.month]).head(1)
    return pd.DatetimeIndex(first_days.index)


def next_trading_day(prices: pd.Series, target: str) -> pd.Timestamp:
    pos = prices.index.searchsorted(pd.Timestamp(target))
    if pos >= len(prices):
        raise ValueError("Target date is after the end of the data")
    return prices.index[pos]