import pandas as pd
import pytest

from Source.strategies import drawdown_signal, simulate


@pytest.fixture
def two_days():
    idx = pd.to_datetime(["2020-01-02", "2020-02-03"])
    return idx, pd.Series([100.0, 50.0], index=idx)


def test_dca_buys_correct_shares(two_days):
    idx, prices = two_days
    res = simulate(prices, idx, amount=500)
    assert res["shares"].iloc[-1] == pytest.approx(5 + 10)   # 500/100 + 500/50
    assert res["deposited"].iloc[-1] == 1000
    assert res["trades"].iloc[-1] == 2


def test_timer_holds_cash_without_signal(two_days):
    idx, prices = two_days
    signal = pd.Series([False, False], index=idx)
    res = simulate(prices, idx, amount=500, signal=signal)
    assert res["cash"].iloc[-1] == 1000
    assert res["shares"].iloc[-1] == 0
    assert res["value"].iloc[-1] == 1000      # leftover cash counted
    assert res["trades"].iloc[-1] == 0


def test_timer_deploys_whole_bucket_on_signal(two_days):
    idx, prices = two_days
    signal = pd.Series([False, True], index=idx)
    res = simulate(prices, idx, amount=500, signal=signal)
    assert res["shares"].iloc[-1] == pytest.approx(1000 / 50)
    assert res["cash"].iloc[-1] == 0
    assert res["trades"].iloc[-1] == 1


def test_always_true_signal_matches_dca(two_days):
    idx, prices = two_days
    always = pd.Series([True, True], index=idx)
    dca = simulate(prices, idx)
    timer = simulate(prices, idx, signal=always)
    pd.testing.assert_frame_equal(dca, timer)


def test_signal_is_lagged_one_day():
    idx = pd.date_range("2020-01-01", periods=6, freq="B")
    prices = pd.Series([100, 100, 100, 80, 80, 80], index=idx, dtype=float)
    sig = drawdown_signal(prices, window=3, threshold=-0.10)
    # Price drops on day index 3, but the signal must not fire until day 4
    assert not sig.iloc[3]
    assert sig.iloc[4]