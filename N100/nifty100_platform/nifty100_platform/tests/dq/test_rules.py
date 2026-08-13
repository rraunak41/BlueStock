"""Unit tests for DQ rules — crafted violation records per rule."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import pandas as pd
from etl.validator import validate_all


def _minimal_dfs(**overrides):
    """Build a minimal valid dataset dict, with overrides for specific tables."""
    base = {
        "companies": pd.DataFrame({"id": ["TCS", "INFY"], "roe_percentage": [50, 40]}),
        "profitandloss": pd.DataFrame({
            "company_id": ["TCS", "INFY"], "year": ["2023-03", "2023-03"],
            "sales": [1000, 800], "expenses": [700, 600], "operating_profit": [300, 200],
            "opm_percentage": [30, 25], "other_income": [10, 5], "interest": [0, 5],
            "depreciation": [20, 15], "profit_before_tax": [290, 190], "tax_percentage": [25, 25],
            "net_profit": [217, 142], "eps": [10, 8], "dividend_payout": [40, 30],
        }),
        "balancesheet": pd.DataFrame({
            "company_id": ["TCS", "INFY"], "year": ["2023-03", "2023-03"],
            "equity_capital": [10, 10], "reserves": [990, 790], "borrowings": [0, 50],
            "other_liabilities": [100, 80], "total_liabilities": [1100, 930],
            "fixed_assets": [200, 150], "cwip": [5, 5], "investments": [50, 30],
            "other_asset": [845, 745], "total_assets": [1100, 930],
        }),
        "cashflow": pd.DataFrame({
            "company_id": ["TCS", "INFY"], "year": ["2023-03", "2023-03"],
            "operating_activity": [250, 180], "investing_activity": [-50, -40],
            "financing_activity": [-100, -60], "net_cash_flow": [100, 80],
        }),
        "analysis": pd.DataFrame({"company_id": ["TCS"]}),
        "documents": pd.DataFrame({"company_id": ["TCS"], "Year": [2023], "Annual_Report": ["http://x.com/a.pdf"]}),
        "prosandcons": pd.DataFrame({"company_id": ["TCS"]}),
        "sectors": pd.DataFrame({"company_id": ["TCS", "INFY"], "broad_sector": ["Information Technology"] * 2}),
        "stock_prices": pd.DataFrame({"company_id": ["TCS"]}),
        "market_cap": pd.DataFrame({"company_id": ["TCS"]}),
        "financial_ratios": pd.DataFrame({"company_id": ["TCS"]}),
        "peer_groups": pd.DataFrame({"company_id": ["TCS"]}),
    }
    base.update(overrides)
    return base


def test_dq01_duplicate_ticker():
    dfs = _minimal_dfs(companies=pd.DataFrame({"id": ["TCS", "TCS"], "roe_percentage": [50, 50]}))
    v = validate_all(dfs)
    assert (v.rule_id == "DQ-01").any()


def test_dq02_duplicate_annual_record():
    pl = _minimal_dfs()["profitandloss"]
    pl_dup = pd.concat([pl, pl.iloc[[0]]], ignore_index=True)
    dfs = _minimal_dfs(profitandloss=pl_dup)
    v = validate_all(dfs)
    assert (v.rule_id == "DQ-02").any()


def test_dq03_fk_orphan():
    pl = _minimal_dfs()["profitandloss"].copy()
    pl.loc[0, "company_id"] = "GHOSTCO"
    dfs = _minimal_dfs(profitandloss=pl)
    v = validate_all(dfs)
    assert (v.rule_id == "DQ-03").any()


def test_dq04_bs_balance_mismatch():
    bs = _minimal_dfs()["balancesheet"].copy()
    bs.loc[0, "total_liabilities"] = bs.loc[0, "total_assets"] * 1.05  # 5% mismatch > 1% tolerance
    dfs = _minimal_dfs(balancesheet=bs)
    v = validate_all(dfs)
    assert (v.rule_id == "DQ-04").any()


def test_dq06_zero_sales():
    pl = _minimal_dfs()["profitandloss"].copy()
    pl.loc[0, "sales"] = 0
    dfs = _minimal_dfs(profitandloss=pl)
    v = validate_all(dfs)
    assert (v.rule_id == "DQ-06").any()


def test_dq11_tax_rate_out_of_range():
    pl = _minimal_dfs()["profitandloss"].copy()
    pl.loc[0, "tax_percentage"] = 85
    dfs = _minimal_dfs(profitandloss=pl)
    v = validate_all(dfs)
    assert (v.rule_id == "DQ-11").any()


def test_dq12_dividend_payout_cap():
    pl = _minimal_dfs()["profitandloss"].copy()
    pl.loc[0, "dividend_payout"] = 250
    dfs = _minimal_dfs(profitandloss=pl)
    v = validate_all(dfs)
    assert (v.rule_id == "DQ-12").any()


def test_no_violations_on_clean_data():
    dfs = _minimal_dfs()
    v = validate_all(dfs)
    critical = v[v.severity == "CRITICAL"]
    assert len(critical) == 0, f"Unexpected critical violations on clean fixture: {critical.to_dict('records')}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
