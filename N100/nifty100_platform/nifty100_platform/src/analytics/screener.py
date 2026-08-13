"""
Nifty 100 Financial Intelligence Platform
Module 3: Investment Screener & Filter Engine

Loads screener_config.yaml, builds the latest-year analytical view
(ratios + CAGR + market_cap + quality score), and applies preset or
custom threshold filters.
"""
import sys
from pathlib import Path
import sqlite3
import yaml
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / "data" / "db" / "nifty100.db"
CONFIG_PATH = BASE / "config" / "screener_config.yaml"
REPORTS = BASE / "reports"


def build_screener_universe(conn) -> pd.DataFrame:
    """One row per company: latest-year ratios + CAGR + latest market_cap + quality score + sector."""
    ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
    ratios = ratios.drop(columns=["broad_sector"])  # re-joined cleanly below to avoid _x/_y suffixes
    latest_ratios = ratios.sort_values("year").groupby("company_id").tail(1)

    cagr = pd.read_sql("SELECT * FROM growth_cagr", conn)
    score = pd.read_sql("SELECT company_id, composite_quality_score FROM quality_score", conn)
    companies = pd.read_sql("SELECT id AS company_id, company_name FROM companies", conn)
    sectors = pd.read_sql("SELECT company_id, broad_sector, sub_sector FROM sectors", conn)

    mkt = pd.read_sql("SELECT * FROM market_cap", conn)
    latest_mkt = mkt.sort_values("year").groupby("company_id").tail(1)
    latest_mkt["fcf_yield_pct"] = None  # filled below after merge

    pl = pd.read_sql("SELECT company_id, dividend_payout FROM profitandloss", conn)
    latest_div = pl.groupby("company_id").tail(1)

    df = (latest_ratios
          .merge(cagr, on="company_id", how="left")
          .merge(score, on="company_id", how="left")
          .merge(companies, on="company_id", how="left")
          .merge(sectors, on="company_id", how="left")
          .merge(latest_mkt[["company_id", "market_cap_crore", "pe_ratio", "pb_ratio", "ev_ebitda", "dividend_yield_pct"]], on="company_id", how="left")
          .merge(latest_div[["company_id", "dividend_payout"]], on="company_id", how="left"))

    df["fcf_yield_pct"] = df["free_cash_flow_cr"] / df["market_cap_crore"].replace(0, pd.NA) * 100
    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply a dict of {column: {min: x, max: y}} thresholds."""
    mask = pd.Series(True, index=df.index)
    for col, bounds in filters.items():
        if col not in df.columns:
            continue
        if "min" in bounds:
            mask &= df[col] >= bounds["min"]
        if "max" in bounds:
            mask &= df[col] <= bounds["max"]
    return df[mask]


def run_preset(df: pd.DataFrame, preset_cfg: dict) -> pd.DataFrame:
    result = apply_filters(df, preset_cfg["filters"])
    rank_col = preset_cfg.get("rank_by", "composite_quality_score")
    desc = preset_cfg.get("rank_desc", True)
    if rank_col in result.columns:
        result = result.sort_values(rank_col, ascending=not desc)
    return result


def run_all_presets(conn, config_path=CONFIG_PATH) -> dict:
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    universe = build_screener_universe(conn)

    # Turnaround Watch needs multi-year trend logic (FCF improving, D/E declining) —
    # not expressible as simple min/max thresholds, so compute separately (Module 3.6).
    ratios_all = pd.read_sql("SELECT company_id, year, debt_to_equity, free_cash_flow_cr FROM financial_ratios", conn)
    trend_rows = []
    for cid, g in ratios_all.sort_values("year").groupby("company_id"):
        if len(g) < 4:
            continue
        latest, three_back = g.iloc[-1], g.iloc[-4]
        trend_rows.append({
            "company_id": cid,
            "fcf_improving": latest["free_cash_flow_cr"] > 0 and latest["free_cash_flow_cr"] > three_back["free_cash_flow_cr"],
            "de_declining": latest["debt_to_equity"] < three_back["debt_to_equity"],
        })
    trend_df = pd.DataFrame(trend_rows)
    universe_trend = universe.merge(trend_df, on="company_id", how="left")

    results = {}
    for key, preset_cfg in cfg["presets"].items():
        if key == "turnaround_watch":
            base = apply_filters(universe_trend, preset_cfg["filters"])
            base = base[(base["fcf_improving"] == True) & (base["de_declining"] == True)]
            results[preset_cfg["name"]] = base.sort_values(preset_cfg["rank_by"], ascending=False)
        else:
            results[preset_cfg["name"]] = run_preset(universe, preset_cfg)
    return results, universe


DISPLAY_COLS = [
    "company_name", "company_id", "broad_sector", "return_on_equity_pct", "return_on_capital_pct",
    "debt_to_equity", "free_cash_flow_cr", "revenue_cagr_5yr_pct", "pat_cagr_5yr_pct",
    "pe_ratio", "pb_ratio", "dividend_yield_pct", "fcf_yield_pct", "composite_quality_score",
]


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    print("Building screener universe (latest-year view, all 92 companies)...")
    results, universe = run_all_presets(conn)

    print(f"\nUniverse size: {len(universe)} companies\n")
    with pd.ExcelWriter(REPORTS / "screener_output.xlsx") as writer:
        for name, df in results.items():
            cols = [c for c in DISPLAY_COLS if c in df.columns]
            out = df[cols].round(2)
            sheet_name = name[:31]
            out.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"{name:24s} -> {len(out):3d} companies matched")

    print(f"\nscreener_output.xlsx written -> reports/ (6 preset sheets)")
    conn.close()
