import numpy as np
import pandas as pd
from scipy.optimize import brentq


def total_return(res: pd.DataFrame) -> float:
    return res["value"].iloc[-1] / res["deposited"].iloc[-1] - 1


def xirr(res: pd.DataFrame) -> float:
    flows = res["flow"]
    deposits = flows[flows > 0]
    dates = deposits.index.append(res.index[[-1]])
    amounts = np.append(-deposits.values, res["value"].iloc[-1])
    t = (dates - dates[0]).days.values / 365.25

    def npv(r):
        return np.sum(amounts / (1 + r) ** t)

    return brentq(npv, -0.99, 10)


def max_drawdown(res: pd.DataFrame) -> tuple[float, pd.Series]:
    v, flow = res["value"], res["flow"]
    daily_ret = (v - flow) / v.shift(1) - 1
    index = (1 + daily_ret.fillna(0)).cumprod()
    dd = index / index.cummax() - 1
    return dd.min(), dd


def summarize(results: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pd.DataFrame({
        name: {
            "Final value ($)": r["value"].iloc[-1],
            "Cash deposited ($)": r["deposited"].iloc[-1],
            "Leftover cash ($)": r["cash"].iloc[-1],
            "Total return": total_return(r),
            "XIRR (annualized)": xirr(r),
            "Max drawdown": max_drawdown(r)[0],
            "Trades": int(r["trades"].iloc[-1]),
        }
        for name, r in results.items()
    })