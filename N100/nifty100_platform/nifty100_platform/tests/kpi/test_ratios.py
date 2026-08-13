"""Unit tests for KPI formulas — mirrors the spec's KPI test reference table."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import pandas as pd
import numpy as np
from analytics.ratios import _safe_div, _cagr


def test_roe_positive():
    net_profit, equity = pd.Series([100]), pd.Series([500])
    roe = _safe_div(net_profit, equity) * 100
    assert roe.iloc[0] == 20.0


def test_roe_negative_equity_none():
    # Per spec: ROE = None if equity+reserves <= 0
    equity = pd.Series([-50])
    net_profit = pd.Series([100])
    roe = np.where(equity > 0, _safe_div(net_profit, equity) * 100, np.nan)
    assert np.isnan(roe[0])


def test_de_debt_free():
    borrowings, equity = pd.Series([0]), pd.Series([500])
    de = _safe_div(borrowings, equity)
    assert de.iloc[0] == 0


def test_icr_debt_free_is_none():
    interest = pd.Series([0])
    op_profit, other_income = pd.Series([1000]), pd.Series([50])
    icr = np.where(interest > 0, _safe_div(op_profit + other_income, interest), np.nan)
    assert np.isnan(icr[0])


def test_cagr_turnaround_flag():
    s = pd.Series([-100, -50, 0, 100, 200], index=[2020, 2021, 2022, 2023, 2024])
    cagr, flag = _cagr(s, 4)
    assert cagr is None or np.isnan(cagr)
    assert flag == "TURNAROUND"


def test_cagr_normal():
    s = pd.Series([100, 120, 135, 150, 161], index=[2019, 2020, 2021, 2022, 2023])
    cagr, flag = _cagr(s, 4)
    assert flag == "OK"
    assert abs(cagr - 12.5) < 2  # ~10% CAGR range check, loose bound


def test_cagr_zero_base():
    s = pd.Series([0, 50, 100, 150, 200], index=[2019, 2020, 2021, 2022, 2023])
    cagr, flag = _cagr(s, 4)
    assert flag == "ZERO_BASE"
    assert cagr is None or np.isnan(cagr)


def test_cagr_insufficient_history():
    s = pd.Series([100, 110], index=[2022, 2023])
    cagr, flag = _cagr(s, 5)
    assert flag == "INSUFFICIENT"


def test_cagr_decline_to_loss():
    s = pd.Series([100, 80, 50, 10, -20], index=[2019, 2020, 2021, 2022, 2023])
    cagr, flag = _cagr(s, 4)
    assert flag == "DECLINE_TO_LOSS"


def test_cagr_both_negative():
    s = pd.Series([-100, -90, -80, -70, -60], index=[2019, 2020, 2021, 2022, 2023])
    cagr, flag = _cagr(s, 4)
    assert flag == "BOTH_NEGATIVE"


def test_safe_div_zero_denominator():
    numer, denom = pd.Series([100]), pd.Series([0])
    result = _safe_div(numer, denom)
    assert np.isnan(result.iloc[0])


def test_safe_div_normal():
    numer, denom = pd.Series([100]), pd.Series([4])
    result = _safe_div(numer, denom)
    assert result.iloc[0] == 25.0


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
