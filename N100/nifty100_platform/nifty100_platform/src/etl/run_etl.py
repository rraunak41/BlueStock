"""
Nifty 100 Financial Intelligence Platform
Module 1: ETL — Master pipeline (clean, normalise, dedupe, validate, load).

Run: python src/etl/run_etl.py
Produces: data/db/nifty100.db, reports/load_audit.csv, reports/validation_failures.csv
"""
import sys
import time
from pathlib import Path
import sqlite3
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "src" / "etl"))

from loader import load_all
from normaliser import normalize_ticker, normalize_year, normalize_company_name
from validator import validate_all

DB_PATH = BASE / "data" / "db" / "nifty100.db"
REPORTS = BASE / "reports"
REPORTS.mkdir(exist_ok=True, parents=True)

TIME_SERIES = ["profitandloss", "balancesheet", "cashflow"]


def clean_and_normalise(dfs: dict) -> dict:
    """Normalise tickers/years, drop TTM snapshot rows, drop FK orphans, dedupe."""
    clean = {}

    # 1. Normalise companies master first (defines the valid ticker universe)
    companies = dfs["companies"].copy()
    companies["id"] = companies["id"].apply(normalize_ticker)
    companies["company_name"] = companies["company_name"].apply(normalize_company_name)
    companies = companies.drop_duplicates(subset="id")
    valid_ids = set(companies["id"])
    clean["companies"] = companies

    # 2. Normalise + clean every other table
    for name, df in dfs.items():
        if name == "companies":
            continue
        d = df.copy()
        if "company_id" in d.columns:
            d["company_id"] = d["company_id"].apply(normalize_ticker)

        # Drop non-annual "TTM" snapshot rows from time-series tables (not a valid FY)
        if name in TIME_SERIES and "year" in d.columns:
            is_ttm = d["year"].astype(str).str.strip().str.upper() == "TTM"
            d = d[~is_ttm]

        # Normalise year label -> YYYY-MM for time-series & documents tables
        if "year" in d.columns and name in TIME_SERIES:
            d["year_raw"] = d["year"]
            d["year"] = d["year"].apply(normalize_year)
            bad = d["year"] == "PARSE_ERROR"
            if bad.any():
                d = d[~bad]

        # Reject FK orphans (company_id not in companies master)
        if "company_id" in d.columns:
            d = d[d["company_id"].isin(valid_ids)]

        # Dedupe (company_id, year) — keep last occurrence
        if name in TIME_SERIES:
            d = d.drop_duplicates(subset=["company_id", "year"], keep="last")
        elif name in ("sectors", "market_cap") and "year" in d.columns:
            d = d.drop_duplicates(subset=["company_id", "year"], keep="last")
        elif name == "financial_ratios" and "year" in d.columns:
            d["year"] = d["year"].astype(str)
            d = d.drop_duplicates(subset=["company_id", "year"], keep="last")

        clean[name] = d

    return clean


TABLE_DDL = {
    "companies": """
        CREATE TABLE companies (
            id TEXT PRIMARY KEY, company_logo TEXT, company_name TEXT, chart_link TEXT,
            about_company TEXT, website TEXT, nse_profile TEXT, bse_profile TEXT,
            face_value REAL, book_value REAL, roce_percentage REAL, roe_percentage REAL
        )""",
    "profitandloss": """
        CREATE TABLE profitandloss (
            id INTEGER, company_id TEXT, year TEXT, year_raw TEXT, sales REAL, expenses REAL,
            operating_profit REAL, opm_percentage REAL, other_income REAL, interest REAL,
            depreciation REAL, profit_before_tax REAL, tax_percentage REAL, net_profit REAL,
            eps REAL, dividend_payout REAL,
            PRIMARY KEY (company_id, year),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
    "balancesheet": """
        CREATE TABLE balancesheet (
            id INTEGER, company_id TEXT, year TEXT, year_raw TEXT, equity_capital REAL, reserves REAL,
            borrowings REAL, other_liabilities REAL, total_liabilities REAL, fixed_assets REAL,
            cwip REAL, investments REAL, other_asset REAL, total_assets REAL,
            PRIMARY KEY (company_id, year),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
    "cashflow": """
        CREATE TABLE cashflow (
            id INTEGER, company_id TEXT, year TEXT, year_raw TEXT, operating_activity REAL,
            investing_activity REAL, financing_activity REAL, net_cash_flow REAL,
            PRIMARY KEY (company_id, year),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
    "analysis": """
        CREATE TABLE analysis (
            id INTEGER, company_id TEXT, compounded_sales_growth TEXT, compounded_profit_growth TEXT,
            stock_price_cagr TEXT, roe TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
    "documents": """
        CREATE TABLE documents (
            id INTEGER, company_id TEXT, Year INTEGER, Annual_Report TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
    "prosandcons": """
        CREATE TABLE prosandcons (
            id INTEGER, company_id TEXT, pros TEXT, cons TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
    "sectors": """
        CREATE TABLE sectors (
            id INTEGER, company_id TEXT PRIMARY KEY, broad_sector TEXT, sub_sector TEXT,
            index_weight_pct REAL, market_cap_category TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
    "stock_prices": """
        CREATE TABLE stock_prices (
            id INTEGER, company_id TEXT, date TEXT, open_price REAL, high_price REAL,
            low_price REAL, close_price REAL, volume INTEGER, adjusted_close REAL,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
    "market_cap": """
        CREATE TABLE market_cap (
            id INTEGER, company_id TEXT, year INTEGER, market_cap_crore REAL,
            enterprise_value_crore REAL, pe_ratio REAL, pb_ratio REAL, ev_ebitda REAL,
            dividend_yield_pct REAL,
            PRIMARY KEY (company_id, year),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
    "financial_ratios": """
        CREATE TABLE financial_ratios_src (
            id INTEGER, company_id TEXT, year TEXT, net_profit_margin_pct REAL,
            operating_profit_margin_pct REAL, return_on_equity_pct REAL, debt_to_equity REAL,
            interest_coverage REAL, asset_turnover REAL, free_cash_flow_cr REAL, capex_cr REAL,
            earnings_per_share REAL, book_value_per_share REAL, dividend_payout_ratio_pct REAL,
            total_debt_cr REAL, cash_from_operations_cr REAL,
            PRIMARY KEY (company_id, year),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
    "peer_groups": """
        CREATE TABLE peer_groups (
            id INTEGER, peer_group_name TEXT, company_id TEXT, is_benchmark INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )""",
}


def build_and_load(clean: dict) -> pd.DataFrame:
    """Create the SQLite schema and load all cleaned tables. Returns load_audit DataFrame."""
    DB_PATH.parent.mkdir(exist_ok=True, parents=True)
    DB_PATH.unlink(missing_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    audit_rows = []
    # Load companies first (parent table)
    order = ["companies"] + [k for k in clean if k != "companies"]
    for name in order:
        df = clean[name]
        t0 = time.time()
        table_name = "financial_ratios_src" if name == "financial_ratios" else name
        conn.execute(TABLE_DDL[name])
        cols = [c.split()[0] for c in TABLE_DDL[name].split("(", 1)[1].rsplit(")", 1)[0].split(",")
                if c.strip() and not c.strip().upper().startswith(("PRIMARY", "FOREIGN"))]
        insert_cols = [c for c in df.columns if c in cols]
        df[insert_cols].to_sql(table_name, conn, if_exists="append", index=False)
        rowcount = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        runtime = time.time() - t0
        audit_rows.append({
            "table": table_name, "rows_in": len(df), "rows_out": rowcount,
            "rejected": max(0, len(df) - rowcount), "runtime_s": round(runtime, 3),
        })
        print(f"  Loaded {table_name:22s} rows_in={len(df):6d}  rows_out={rowcount:6d}  ({runtime:.2f}s)")

    conn.commit()
    conn.close()
    return pd.DataFrame(audit_rows)


if __name__ == "__main__":
    print("=" * 60)
    print("Nifty 100 Financial Intelligence Platform — ETL Pipeline")
    print("=" * 60)

    print("\n[1/4] Loading raw datasets...")
    raw_dfs = load_all()

    print("\n[2/4] Running DQ validation on RAW data (pre-clean)...")
    violations = validate_all(raw_dfs)
    violations.to_csv(REPORTS / "validation_failures.csv", index=False)
    print(f"  {len(violations)} violations logged -> reports/validation_failures.csv")
    print(f"  {(violations.severity=='CRITICAL').sum()} CRITICAL, "
          f"{(violations.severity=='WARNING').sum()} WARNING, "
          f"{(violations.severity=='INFO').sum()} INFO")

    print("\n[3/4] Cleaning & normalising (dedupe, FK filter, TTM removal, year/ticker normalise)...")
    clean_dfs = clean_and_normalise(raw_dfs)
    for name, df in clean_dfs.items():
        before = len(raw_dfs[name])
        after = len(df)
        print(f"  {name:16s} {before:6d} -> {after:6d} rows ({before-after} removed)")

    print("\n[4/4] Building SQLite schema & loading nifty100.db...")
    audit = build_and_load(clean_dfs)
    audit.to_csv(REPORTS / "load_audit.csv", index=False)
    print(f"\nLoad audit written -> reports/load_audit.csv")
    print(f"Database written -> {DB_PATH}")
    print(f"\nTotal rows loaded: {audit['rows_out'].sum():,}")
