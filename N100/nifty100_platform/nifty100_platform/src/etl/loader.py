"""
Nifty 100 Financial Intelligence Platform
Module 1: ETL — Excel file loader.

Core files (companies, profitandloss, balancesheet, cashflow, analysis,
documents, prosandcons) use header=1 (row 0 is a title/metadata row).
Supplementary files (sectors, stock_prices, market_cap, financial_ratios,
peer_groups) use header=0.
"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data" / "raw"
SUPP = BASE / "data" / "supporting"

CORE_FILES = {
    "companies": RAW / "companies.xlsx",
    "profitandloss": RAW / "profitandloss.xlsx",
    "balancesheet": RAW / "balancesheet.xlsx",
    "cashflow": RAW / "cashflow.xlsx",
    "analysis": RAW / "analysis.xlsx",
    "documents": RAW / "documents.xlsx",
    "prosandcons": RAW / "prosandcons.xlsx",
}

SUPPLEMENTARY_FILES = {
    "sectors": SUPP / "sectors.xlsx",
    "stock_prices": SUPP / "stock_prices.xlsx",
    "market_cap": SUPP / "market_cap.xlsx",
    "financial_ratios": SUPP / "financial_ratios.xlsx",
    "peer_groups": SUPP / "peer_groups.xlsx",
}


def load_core_file(name: str) -> pd.DataFrame:
    """Load a core dataset with header=1 (row 0 is a title/metadata row)."""
    path = CORE_FILES[name]
    return pd.read_excel(path, header=1)


def load_supplementary_file(name: str) -> pd.DataFrame:
    """Load a supplementary dataset with header=0."""
    path = SUPPLEMENTARY_FILES[name]
    return pd.read_excel(path, header=0)


def load_all() -> dict:
    """Load all 12 datasets into a dict of DataFrames, keyed by dataset name."""
    dfs = {}
    for name in CORE_FILES:
        dfs[name] = load_core_file(name)
        print(f"  {name:16s} (core)    shape={dfs[name].shape}")
    for name in SUPPLEMENTARY_FILES:
        dfs[name] = load_supplementary_file(name)
        print(f"  {name:16s} (supp)    shape={dfs[name].shape}")
    return dfs


if __name__ == "__main__":
    print("Loading all 12 Nifty 100 datasets...")
    dfs = load_all()
    total_rows = sum(len(df) for df in dfs.values())
    print(f"\nTotal rows across all datasets: {total_rows:,}")
    for name, df in dfs.items():
        print(f"\n=== {name} — columns ===")
        print(list(df.columns))
