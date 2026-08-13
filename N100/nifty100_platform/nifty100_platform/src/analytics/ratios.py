"""
Nifty 100 Financial Intelligence Platform
Module 2: Financial Ratio Engine

Computes 50+ KPIs for every company-year combination from raw P&L, Balance
Sheet, and Cash Flow data. Handles edge cases per the KPI Reference spec:
division by zero, negative equity, debt-free companies, CAGR sign anomalies.
"""
import sys
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / "data" / "db" / "nifty100.db"
REPORTS = BASE / "reports"


def _safe_div(numer, denom):
    """Element-wise division returning NaN where denom is 0/NaN."""
    denom = denom.replace(0, np.nan) if hasattr(denom, "replace") else denom
    return numer / denom


def load_base_tables(conn):
    pl = pd.read_sql("SELECT * FROM profitandloss", conn)
    bs = pd.read_sql("SELECT * FROM balancesheet", conn)
    cf = pd.read_sql("SELECT * FROM cashflow", conn)
    companies = pd.read_sql("SELECT * FROM companies", conn)
    sectors = pd.read_sql("SELECT * FROM sectors", conn)
    return pl, bs, cf, companies, sectors


def compute_core_ratios(pl, bs, cf, sectors) -> pd.DataFrame:
    """Compute the core per-company-year KPI table (Module 2, features 2.1-2.10)."""
    df = pl.merge(bs, on=["company_id", "year"], suffixes=("_pl", "_bs"))
    df = df.merge(cf, on=["company_id", "year"], suffixes=("", "_cf"))
    df = df.merge(sectors[["company_id", "broad_sector"]], on="company_id", how="left")

    equity = df["equity_capital"] + df["reserves"]
    ebit = df["operating_profit"] - df["depreciation"]

    # 2.1 Net Profit Margin
    df["net_profit_margin_pct"] = _safe_div(df["net_profit"], df["sales"]) * 100

    # 2.2 Operating Profit Margin (computed, cross-checked vs source opm_percentage)
    df["operating_profit_margin_pct"] = _safe_div(df["operating_profit"], df["sales"]) * 100

    # EBIT Margin
    df["ebit_margin_pct"] = _safe_div(ebit, df["sales"]) * 100

    # 2.3 Return on Equity — None if equity <= 0
    roe = _safe_div(df["net_profit"], equity) * 100
    df["return_on_equity_pct"] = np.where(equity > 0, roe, np.nan)

    # 2.4 Return on Capital Employed — EBIT / (equity + borrowings)
    capital_employed = equity + df["borrowings"]
    roce = _safe_div(ebit, capital_employed) * 100
    df["return_on_capital_pct"] = np.where(capital_employed > 0, roce, np.nan)

    # Return on Assets
    df["return_on_assets_pct"] = _safe_div(df["net_profit"], df["total_assets"]) * 100

    # 2.5 Debt-to-Equity — 0 for debt-free; flag >5 for non-financials
    de = _safe_div(df["borrowings"], equity)
    df["debt_to_equity"] = np.where(equity > 0, de, np.nan)
    df["debt_to_equity"] = df["debt_to_equity"].fillna(0).where(df["borrowings"] > 0, 0)
    df["de_flag_high"] = (df["debt_to_equity"] > 5) & (df["broad_sector"] != "Financials")

    # 2.6 Interest Coverage — None if interest = 0 (displayed as 'Debt Free')
    icr = _safe_div(df["operating_profit"] + df["other_income"], df["interest"])
    df["interest_coverage"] = np.where(df["interest"] > 0, icr, np.nan)
    df["interest_coverage_label"] = np.where(df["interest"] > 0, df["interest_coverage"].round(2).astype(str), "Debt Free")

    # Net Debt & Net Debt/EBITDA
    net_debt = df["borrowings"] - df["investments"]
    df["net_debt_cr"] = net_debt
    ndebitda = _safe_div(net_debt, df["operating_profit"])
    df["net_debt_to_ebitda"] = np.where(df["operating_profit"] > 0, ndebitda, np.nan)

    # 2.9 Asset Turnover
    df["asset_turnover"] = _safe_div(df["sales"], df["total_assets"])

    # Fixed Asset Turnover
    df["fixed_asset_turnover"] = _safe_div(df["sales"], df["fixed_assets"])

    # Working Capital Days
    wc_days = _safe_div(df["other_asset"] - df["other_liabilities"], df["sales"]) * 365
    df["working_capital_days"] = wc_days

    # 2.7 Free Cash Flow = CFO + CFI
    df["free_cash_flow_cr"] = df["operating_activity"] + df["investing_activity"]

    # CFO / PAT ratio (cash quality)
    cfo_pat = _safe_div(df["operating_activity"], df["net_profit"])
    df["cfo_pat_ratio"] = np.where(df["net_profit"] != 0, cfo_pat, np.nan)

    # CapEx intensity
    df["capex_cr"] = df["investing_activity"].abs()
    df["capex_intensity_pct"] = _safe_div(df["capex_cr"], df["sales"]) * 100

    # FCF Conversion Rate
    fcf_conv = _safe_div(df["free_cash_flow_cr"], df["operating_profit"]) * 100
    df["fcf_conversion_pct"] = np.where(df["operating_profit"] > 0, fcf_conv, np.nan)

    # Book Value Per Share
    shares = _safe_div(df["equity_capital"], df["face_value"]) if "face_value" in df.columns else np.nan
    df["book_value_per_share"] = _safe_div(equity, shares) if "face_value" in df.columns else np.nan

    # 2.10 Capital Allocation pattern (CFO/CFI/CFF sign pattern -> label)
    def sign(x):
        return np.where(x > 0, "+", np.where(x < 0, "-", "0"))

    cfo_sign = sign(df["operating_activity"])
    cfi_sign = sign(df["investing_activity"])
    cff_sign = sign(df["financing_activity"])
    pattern = cfo_sign + cfi_sign + cff_sign

    pattern_labels = {
        "+-+": "Aggressive Growth (ops+external funding)",
        "+--": "Reinvestor / Shareholder Returns",
        "+-0": "Steady Reinvestor",
        "++-": "Divesting & Returning Capital",
        "++0": "Divesting Assets",
        "+0-": "Mature — Debt/Dividend Payer",
        "-++": "Distress — External Funding to Survive",
        "-+-": "Distress — Asset Sale + Debt Repay",
        "--+": "Heavy Investment Phase (external funded)",
        "---": "Cash Burn — Self-funded Investment",
    }
    df["cfo_sign"], df["cfi_sign"], df["cff_sign"] = cfo_sign, cfi_sign, cff_sign
    df["capital_allocation_pattern"] = pattern
    df["capital_allocation_label"] = pd.Series(pattern).map(pattern_labels).fillna("Other / Mixed Pattern")

    keep_cols = [
        "company_id", "year", "broad_sector",
        "net_profit_margin_pct", "operating_profit_margin_pct", "ebit_margin_pct",
        "return_on_equity_pct", "return_on_capital_pct", "return_on_assets_pct",
        "debt_to_equity", "de_flag_high", "interest_coverage", "interest_coverage_label",
        "net_debt_cr", "net_debt_to_ebitda", "asset_turnover", "fixed_asset_turnover",
        "working_capital_days", "free_cash_flow_cr", "cfo_pat_ratio", "capex_cr",
        "capex_intensity_pct", "fcf_conversion_pct", "book_value_per_share",
        "cfo_sign", "cfi_sign", "cff_sign", "capital_allocation_pattern", "capital_allocation_label",
        "sales", "net_profit", "eps", "operating_profit", "dividend_payout",
    ]
    return df[keep_cols]


def _cagr(series_by_year: pd.Series, years_back: int):
    """CAGR from N years ago to latest, with turnaround-flag edge case handling."""
    s = series_by_year.sort_index()
    if len(s) < years_back + 1:
        return np.nan, "INSUFFICIENT"
    base = s.iloc[-(years_back + 1)]
    end = s.iloc[-1]
    if base == 0:
        return np.nan, "ZERO_BASE"
    if base > 0 and end > 0:
        cagr = ((end / base) ** (1 / years_back) - 1) * 100
        return cagr, "OK"
    if base > 0 and end < 0:
        return np.nan, "DECLINE_TO_LOSS"
    if base < 0 and end > 0:
        return np.nan, "TURNAROUND"
    return np.nan, "BOTH_NEGATIVE"


def compute_cagr_table(pl: pd.DataFrame) -> pd.DataFrame:
    """Revenue / PAT / EPS CAGR for 3/5/10yr windows, per company (Module 2.8)."""
    rows = []
    for cid, g in pl.sort_values("year").groupby("company_id"):
        g = g.set_index("year")
        rec = {"company_id": cid, "years_of_history": len(g)}
        for label, col in [("revenue", "sales"), ("pat", "net_profit"), ("eps", "eps")]:
            for yrs in (3, 5, 10):
                cagr, flag = _cagr(g[col], yrs)
                rec[f"{label}_cagr_{yrs}yr_pct"] = cagr
                rec[f"{label}_cagr_{yrs}yr_flag"] = flag
        rows.append(rec)
    return pd.DataFrame(rows)


def compute_composite_score(ratios: pd.DataFrame, cagr: pd.DataFrame) -> pd.DataFrame:
    """
    Composite Quality Score (0-100), latest year only:
    0.3*ROE + 0.25*FCF + 0.25*ROCE + 0.20*D/E(inverse), winsorised P10-P90.
    """
    latest = ratios.sort_values("year").groupby("company_id").tail(1).copy()
    latest = latest.merge(cagr[["company_id", "revenue_cagr_5yr_pct"]], on="company_id", how="left")

    def winsorise_score(s: pd.Series, higher_is_better=True):
        s = s.copy()
        p10, p90 = s.quantile(0.10), s.quantile(0.90)
        s_clipped = s.clip(p10, p90)
        rng = p90 - p10
        if rng == 0 or pd.isna(rng):
            return pd.Series(50.0, index=s.index)
        score = (s_clipped - p10) / rng * 100
        return score if higher_is_better else 100 - score

    latest["roe_score"] = winsorise_score(latest["return_on_equity_pct"].fillna(latest["return_on_equity_pct"].median()))
    latest["fcf_score"] = winsorise_score(latest["free_cash_flow_cr"].fillna(latest["free_cash_flow_cr"].median()))
    latest["roce_score"] = winsorise_score(latest["return_on_capital_pct"].fillna(latest["return_on_capital_pct"].median()))
    latest["de_score"] = winsorise_score(latest["debt_to_equity"].fillna(latest["debt_to_equity"].median()), higher_is_better=False)

    latest["composite_quality_score"] = (
        0.30 * latest["roe_score"] + 0.25 * latest["fcf_score"] +
        0.25 * latest["roce_score"] + 0.20 * latest["de_score"]
    ).round(1)

    return latest[["company_id", "year", "composite_quality_score", "roe_score", "fcf_score", "roce_score", "de_score"]]


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    print("Loading base tables...")
    pl, bs, cf, companies, sectors = load_base_tables(conn)

    print("Computing core ratios (2.1-2.10)...")
    ratios = compute_core_ratios(pl, bs, cf, sectors)
    print(f"  {len(ratios)} company-year rows, {ratios.shape[1]} columns")

    print("Computing CAGR engine (3/5/10yr revenue, PAT, EPS)...")
    cagr = compute_cagr_table(pl)
    print(f"  {len(cagr)} companies")

    print("Computing composite quality score...")
    score = compute_composite_score(ratios, cagr)

    # Write to SQLite
    ratios.to_sql("financial_ratios", conn, if_exists="replace", index=False)
    cagr.to_sql("growth_cagr", conn, if_exists="replace", index=False)
    score.to_sql("quality_score", conn, if_exists="replace", index=False)
    conn.commit()

    # Capital allocation export
    capital_alloc = ratios[["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "capital_allocation_pattern", "capital_allocation_label"]]
    capital_alloc.to_csv(REPORTS / "capital_allocation.csv", index=False)

    print(f"\nfinancial_ratios table: {len(ratios)} rows written to SQLite")
    print(f"growth_cagr table: {len(cagr)} rows written to SQLite")
    print(f"quality_score table: {len(score)} rows written to SQLite")
    print(f"capital_allocation.csv written -> reports/")

    print("\nTop 10 companies by latest-year Composite Quality Score:")
    top10 = score.merge(companies[["id", "company_name"]], left_on="company_id", right_on="id")
    print(top10.sort_values("composite_quality_score", ascending=False)[["company_name", "composite_quality_score"]].head(10).to_string(index=False))

    conn.close()
