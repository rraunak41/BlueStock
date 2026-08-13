"""
Bluestock Fintech - Mutual Fund Analytics Platform
Day 2: Load cleaned CSVs into SQLite database using the star schema.
"""
import sqlite3
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed"
DB_PATH = BASE / "data" / "db" / "bluestock_mf.db"
SCHEMA_PATH = BASE / "sql" / "schema.sql"


def build_schema():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Schema created.")


def build_dim_date(min_date, max_date):
    dates = pd.date_range(min_date, max_date, freq="D")
    dim = pd.DataFrame({"date": dates})
    dim["date_id"] = dim["date"].dt.strftime("%Y-%m-%d")
    dim["year"] = dim["date"].dt.year
    dim["month"] = dim["date"].dt.month
    dim["month_name"] = dim["date"].dt.strftime("%B")
    dim["quarter"] = dim["date"].dt.quarter
    dim["is_weekday"] = dim["date"].dt.dayofweek < 5
    return dim


def load_all():
    engine = create_engine(f"sqlite:///{DB_PATH}")

    fund_master = pd.read_csv(PROC / "fund_master_clean.csv")
    fund_master.to_sql("dim_fund", engine, if_exists="append", index=False)
    print(f"dim_fund: {len(fund_master)} rows loaded")

    nav = pd.read_csv(PROC / "nav_history_clean.csv")
    dim_date = build_dim_date(nav["date"].min(), nav["date"].max())
    dim_date.to_sql("dim_date", engine, if_exists="append", index=False)
    print(f"dim_date: {len(dim_date)} rows loaded")

    nav.to_sql("fact_nav", engine, if_exists="append", index=False)
    print(f"fact_nav: {len(nav)} rows loaded")

    tx = pd.read_csv(PROC / "investor_transactions_clean.csv")
    tx_cols = ["investor_id", "transaction_date", "amfi_code", "transaction_type",
               "amount_inr", "state", "city", "city_tier", "age_group", "gender",
               "annual_income_lakh", "payment_mode", "kyc_status"]
    tx[tx_cols].to_sql("fact_transactions", engine, if_exists="append", index=False)
    print(f"fact_transactions: {len(tx)} rows loaded")

    perf = pd.read_csv(PROC / "scheme_performance_clean.csv")
    perf_cols = ["amfi_code", "scheme_name", "fund_house", "category", "plan",
                 "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct",
                 "alpha", "beta", "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct",
                 "max_drawdown_pct", "aum_crore", "expense_ratio_pct", "morningstar_rating",
                 "risk_grade"]
    perf[perf_cols].to_sql("fact_performance", engine, if_exists="append", index=False)
    print(f"fact_performance: {len(perf)} rows loaded")

    port = pd.read_csv(PROC / "portfolio_holdings_clean.csv")
    port.to_sql("fact_portfolio", engine, if_exists="append", index=False)
    print(f"fact_portfolio: {len(port)} rows loaded")

    aum = pd.read_csv(PROC / "aum_by_fund_house_clean.csv")
    aum.to_sql("fact_aum", engine, if_exists="append", index=False)
    print(f"fact_aum: {len(aum)} rows loaded")

    sip = pd.read_csv(PROC / "monthly_sip_inflows_clean.csv")
    sip_cols = ["month", "sip_inflow_crore", "active_sip_accounts_crore",
                "new_sip_accounts_lakh", "sip_aum_lakh_crore", "yoy_growth_pct"]
    sip[sip_cols].to_sql("fact_sip_industry", engine, if_exists="append", index=False)
    print(f"fact_sip_industry: {len(sip)} rows loaded")

    cat = pd.read_csv(PROC / "category_inflows_clean.csv")
    cat.to_sql("fact_category_inflows", engine, if_exists="append", index=False)
    print(f"fact_category_inflows: {len(cat)} rows loaded")

    folio = pd.read_csv(PROC / "industry_folio_count_clean.csv")
    folio.to_sql("fact_folio_count", engine, if_exists="append", index=False)
    print(f"fact_folio_count: {len(folio)} rows loaded")

    bench = pd.read_csv(PROC / "benchmark_indices_clean.csv")
    bench.to_sql("fact_benchmark", engine, if_exists="append", index=False)
    print(f"fact_benchmark: {len(bench)} rows loaded")


if __name__ == "__main__":
    DB_PATH.unlink(missing_ok=True)
    build_schema()
    load_all()
    print(f"\nDatabase built at {DB_PATH}")
