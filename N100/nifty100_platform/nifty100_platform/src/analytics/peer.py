"""
Nifty 100 Financial Intelligence Platform
Module 4: Peer Comparison Engine

Computes within-peer-group percentile ranks across 8 metrics for each of
the 11 defined peer groups, flags Best-in-Class / Watch List companies.
"""
import sys
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / "data" / "db" / "nifty100.db"
REPORTS = BASE / "reports"

RADAR_METRICS = [
    "return_on_equity_pct", "return_on_capital_pct", "net_profit_margin_pct",
    "debt_to_equity", "free_cash_flow_cr", "pat_cagr_5yr_pct", "revenue_cagr_5yr_pct",
]
# For debt_to_equity, LOWER is better -> invert percentile
INVERT_METRICS = {"debt_to_equity"}


def build_peer_universe(conn) -> pd.DataFrame:
    from analytics.screener import build_screener_universe
    universe = build_screener_universe(conn)
    peer_groups = pd.read_sql("SELECT * FROM peer_groups", conn)
    merged = peer_groups.merge(universe, on="company_id", how="left")
    return merged


def compute_peer_percentiles(peer_universe: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group_name, g in peer_universe.groupby("peer_group_name"):
        for metric in RADAR_METRICS:
            if metric not in g.columns:
                continue
            vals = g[metric]
            pct = vals.rank(pct=True)
            if metric in INVERT_METRICS:
                pct = 1 - pct
            for cid, v, p in zip(g["company_id"], vals, pct):
                rows.append({
                    "peer_group_name": group_name, "company_id": cid,
                    "metric": metric, "value": v, "percentile_rank": p,
                })
    return pd.DataFrame(rows)


def detect_best_in_class_and_watch(percentiles: pd.DataFrame) -> pd.DataFrame:
    piv = percentiles.pivot_table(index=["peer_group_name", "company_id"], columns="metric", values="percentile_rank").reset_index()
    metric_cols = [c for c in piv.columns if c in RADAR_METRICS]
    piv["n_top_quartile"] = (piv[metric_cols] >= 0.75).sum(axis=1)
    piv["n_bottom_quartile"] = (piv[metric_cols] <= 0.25).sum(axis=1)
    piv["best_in_class"] = piv["n_top_quartile"] >= 6 * len(metric_cols) / 10  # >=6 of 10 metrics -> scaled to our 7
    piv["watch_list"] = piv["n_bottom_quartile"] >= 4 * len(metric_cols) / 10
    return piv


def peer_comparison_excel(conn, peer_universe: pd.DataFrame, percentiles: pd.DataFrame):
    out_path = REPORTS / "peer_comparison.xlsx"
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for group_name, g in peer_universe.groupby("peer_group_name"):
            cols = ["company_id", "company_name", "is_benchmark"] + [m for m in RADAR_METRICS if m in g.columns]
            sheet = g[cols].round(2)
            pct_wide = percentiles[percentiles.peer_group_name == group_name].pivot_table(
                index="company_id", columns="metric", values="percentile_rank"
            ).round(2)
            pct_wide.columns = [f"{c}_pctile" for c in pct_wide.columns]
            sheet = sheet.merge(pct_wide, on="company_id", how="left")
            sheet.to_excel(writer, sheet_name=str(group_name)[:31], index=False)
    print(f"peer_comparison.xlsx written -> reports/ ({peer_universe.peer_group_name.nunique()} sheets)")


if __name__ == "__main__":
    sys.path.insert(0, str(BASE / "src"))
    conn = sqlite3.connect(DB_PATH)

    print("Building peer universe (56 members across 11 peer groups)...")
    peer_universe = build_peer_universe(conn)
    print(f"  {len(peer_universe)} peer-group memberships, {peer_universe.peer_group_name.nunique()} groups")

    print("Computing intra-group percentile ranks (7 metrics)...")
    percentiles = compute_peer_percentiles(peer_universe)
    percentiles.to_sql("peer_percentiles", conn, if_exists="replace", index=False)
    print(f"  {len(percentiles)} percentile rows written to SQLite")

    print("Detecting Best-in-Class / Watch List companies...")
    flags = detect_best_in_class_and_watch(percentiles)
    print(f"  Best-in-Class: {flags['best_in_class'].sum()}  |  Watch List: {flags['watch_list'].sum()}")
    flags.to_csv(REPORTS / "peer_bic_watchlist.csv", index=False)

    print("\nGenerating peer_comparison.xlsx (11 sheets)...")
    peer_comparison_excel(conn, peer_universe, percentiles)

    conn.commit()
    conn.close()
    print("\nModule 4 complete.")
