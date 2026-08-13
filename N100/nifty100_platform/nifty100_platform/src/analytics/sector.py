"""
Nifty 100 Financial Intelligence Platform
Module 6: Sector Analytics

Sector median KPIs, relative scoring, and overvaluation flags using the
sector benchmark ranges from the project spec (Section 28).
"""
import sys
from pathlib import Path
import sqlite3
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / "data" / "db" / "nifty100.db"
REPORTS = BASE / "reports"

METRICS = ["return_on_equity_pct", "return_on_capital_pct", "debt_to_equity",
           "net_profit_margin_pct", "free_cash_flow_cr", "revenue_cagr_5yr_pct"]


def sector_benchmarks(conn) -> pd.DataFrame:
    sys.path.insert(0, str(BASE / "src"))
    from analytics.screener import build_screener_universe
    universe = build_screener_universe(conn)

    agg = universe.groupby("broad_sector")[METRICS + ["pe_ratio", "pb_ratio"]].median().round(2)
    agg["num_companies"] = universe.groupby("broad_sector").size()
    agg = agg.reset_index().sort_values("num_companies", ascending=False)
    return agg, universe


def overvaluation_flags(universe: pd.DataFrame, sector_pe: pd.Series) -> pd.DataFrame:
    df = universe.copy()
    df["sector_median_pe"] = df["broad_sector"].map(sector_pe)
    df["valuation_flag"] = "Neutral"
    df.loc[df["pe_ratio"] > df["sector_median_pe"] * 1.5, "valuation_flag"] = "Caution (overvalued)"
    df.loc[df["pe_ratio"] < df["sector_median_pe"] * 0.7, "valuation_flag"] = "Discount (undervalued)"
    return df[["company_id", "company_name", "broad_sector", "pe_ratio", "sector_median_pe", "valuation_flag"]]


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    print("Computing sector benchmarks (median KPIs across 11 broad sectors)...")
    sector_kpi, universe = sector_benchmarks(conn)
    sector_kpi.to_sql("sector_benchmarks", conn, if_exists="replace", index=False)
    sector_kpi.to_csv(REPORTS / "sector_benchmarks.csv", index=False)
    print(sector_kpi.to_string(index=False))

    print("\nFlagging overvalued / discount companies (sector-relative P/E)...")
    pe_map = sector_kpi.set_index("broad_sector")["pe_ratio"]
    flags = overvaluation_flags(universe, pe_map)
    flags.to_csv(REPORTS / "valuation_flags.csv", index=False)
    print(flags["valuation_flag"].value_counts().to_string())

    conn.commit()
    conn.close()
    print("\nModule 6 complete. sector_benchmarks.csv + valuation_flags.csv written -> reports/")
