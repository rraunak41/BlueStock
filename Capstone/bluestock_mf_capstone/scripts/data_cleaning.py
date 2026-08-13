"""
Bluestock Fintech - Mutual Fund Analytics Platform
Day 2: Data Cleaning Script

Cleans all 10 datasets and writes cleaned CSVs to data/processed/.
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
PROC = BASE / "data" / "processed"
PROC.mkdir(exist_ok=True, parents=True)


def clean_fund_master():
    df = pd.read_csv(RAW / "01_fund_master.csv")
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["launch_date"] = pd.to_datetime(df["launch_date"])
    df["fund_house"] = df["fund_house"].str.strip()
    df["scheme_name"] = df["scheme_name"].str.strip()
    df = df.drop_duplicates(subset="amfi_code")
    df.to_csv(PROC / "fund_master_clean.csv", index=False)
    print(f"fund_master: {df.shape}")
    return df


def clean_nav_history():
    df = pd.read_csv(RAW / "02_nav_history.csv")
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["amfi_code", "date"])
    df = df.drop_duplicates(subset=["amfi_code", "date"])

    # Reindex each fund to a full business-day calendar and forward-fill NAV for holidays
    filled = []
    for code, g in df.groupby("amfi_code"):
        g = g.set_index("date").sort_index()
        full_idx = pd.date_range(g.index.min(), g.index.max(), freq="B")
        g = g.reindex(full_idx)
        g["nav"] = g["nav"].ffill()
        g["amfi_code"] = code
        g.index.name = "date"
        filled.append(g.reset_index())
    df = pd.concat(filled, ignore_index=True)

    # Validate NAV > 0
    bad = (df["nav"] <= 0) | df["nav"].isna()
    print(f"nav_history: dropping {bad.sum()} invalid NAV rows")
    df = df[~bad]

    # Daily return
    df = df.sort_values(["amfi_code", "date"])
    df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100

    df.to_csv(PROC / "nav_history_clean.csv", index=False)
    print(f"nav_history: {df.shape}")
    return df


def clean_aum():
    df = pd.read_csv(RAW / "03_aum_by_fund_house.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["fund_house"] = df["fund_house"].str.strip()
    df = df.drop_duplicates()
    df.to_csv(PROC / "aum_by_fund_house_clean.csv", index=False)
    print(f"aum_by_fund_house: {df.shape}")
    return df


def clean_sip_inflows():
    df = pd.read_csv(RAW / "04_monthly_sip_inflows.csv")
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    # Recompute YoY growth where missing (need 12-month lag)
    df = df.sort_values("month").reset_index(drop=True)
    df["yoy_growth_pct_computed"] = df["sip_inflow_crore"].pct_change(periods=12) * 100
    df.to_csv(PROC / "monthly_sip_inflows_clean.csv", index=False)
    print(f"monthly_sip_inflows: {df.shape}")
    return df


def clean_category_inflows():
    df = pd.read_csv(RAW / "05_category_inflows.csv")
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    df["category"] = df["category"].str.strip()
    df.to_csv(PROC / "category_inflows_clean.csv", index=False)
    print(f"category_inflows: {df.shape}")
    return df


def clean_folio_count():
    df = pd.read_csv(RAW / "06_industry_folio_count.csv")
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    df.to_csv(PROC / "industry_folio_count_clean.csv", index=False)
    print(f"industry_folio_count: {df.shape}")
    return df


def clean_scheme_performance():
    df = pd.read_csv(RAW / "07_scheme_performance.csv")
    df["amfi_code"] = df["amfi_code"].astype(str)
    numeric_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
                     "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio",
                     "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct",
                     "expense_ratio_pct"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["negative_sharpe_flag"] = df["sharpe_ratio"] < 0
    df["expense_ratio_in_range"] = df["expense_ratio_pct"].between(0.1, 2.5)
    print(f"scheme_performance: negative Sharpe funds = {df['negative_sharpe_flag'].sum()}, "
          f"out-of-range expense ratio = {(~df['expense_ratio_in_range']).sum()}")
    df.to_csv(PROC / "scheme_performance_clean.csv", index=False)
    print(f"scheme_performance: {df.shape}")
    return df


def clean_transactions():
    df = pd.read_csv(RAW / "08_investor_transactions.csv")
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["transaction_type"] = df["transaction_type"].str.strip().str.title()
    valid_types = {"Sip", "Lumpsum", "Redemption"}
    df["transaction_type"] = df["transaction_type"].replace({"Sip": "SIP"})
    before = len(df)
    df = df[df["amount_inr"] > 0]
    print(f"investor_transactions: dropped {before - len(df)} rows with amount <= 0")
    df["kyc_status"] = df["kyc_status"].str.strip().str.title()
    df.to_csv(PROC / "investor_transactions_clean.csv", index=False)
    print(f"investor_transactions: {df.shape}")
    return df


def clean_portfolio_holdings():
    df = pd.read_csv(RAW / "09_portfolio_holdings.csv")
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"])
    df["sector"] = df["sector"].str.strip()
    df.to_csv(PROC / "portfolio_holdings_clean.csv", index=False)
    print(f"portfolio_holdings: {df.shape}")
    return df


def clean_benchmark_indices():
    df = pd.read_csv(RAW / "10_benchmark_indices.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["index_name", "date"]).drop_duplicates(subset=["index_name", "date"])
    df.to_csv(PROC / "benchmark_indices_clean.csv", index=False)
    print(f"benchmark_indices: {df.shape}")
    return df


if __name__ == "__main__":
    clean_fund_master()
    clean_nav_history()
    clean_aum()
    clean_sip_inflows()
    clean_category_inflows()
    clean_folio_count()
    clean_scheme_performance()
    clean_transactions()
    clean_portfolio_holdings()
    clean_benchmark_indices()
    print("\nDay 2 cleaning complete: all 10 cleaned CSVs written to data/processed/.")
