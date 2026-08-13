"""
Bluestock Fintech - Mutual Fund Analytics Platform
Day 1: Data Ingestion Script

Loads all 10 raw CSV datasets, prints shape/dtypes/head, and validates
AMFI codes across datasets.
"""
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

DATASETS = {
    "fund_master": "01_fund_master.csv",
    "nav_history": "02_nav_history.csv",
    "aum_by_fund_house": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "benchmark_indices": "10_benchmark_indices.csv",
}


def load_all_datasets(raw_dir: Path = RAW_DIR) -> dict:
    """Load all 10 datasets into a dict of DataFrames."""
    dfs = {}
    for name, filename in DATASETS.items():
        path = raw_dir / filename
        df = pd.read_csv(path)
        dfs[name] = df
        print(f"\n=== {name} ({filename}) ===")
        print(f"Shape: {df.shape}")
        print("Dtypes:")
        print(df.dtypes)
        print("Head:")
        print(df.head(3))
    return dfs


def validate_amfi_codes(dfs: dict) -> None:
    """Cross-check that AMFI codes referenced in other tables exist in fund_master."""
    master_codes = set(dfs["fund_master"]["amfi_code"].astype(str))
    print("\n=== AMFI CODE VALIDATION ===")
    print(f"fund_master unique codes: {len(master_codes)}")

    for name in ["nav_history", "scheme_performance", "investor_transactions", "portfolio_holdings"]:
        codes = set(dfs[name]["amfi_code"].astype(str))
        missing = codes - master_codes
        print(f"{name}: {len(codes)} unique codes, "
              f"{len(missing)} NOT found in fund_master "
              f"{'(OK)' if not missing else missing}")


def fund_master_summary(dfs: dict) -> None:
    fm = dfs["fund_master"]
    print("\n=== FUND MASTER SUMMARY ===")
    print("Fund houses:", fm["fund_house"].nunique())
    print(fm["fund_house"].value_counts())
    print("\nCategories:")
    print(fm["category"].value_counts())
    print("\nSub-categories:")
    print(fm["sub_category"].value_counts())
    print("\nRisk categories:")
    print(fm["risk_category"].value_counts())


if __name__ == "__main__":
    dfs = load_all_datasets()
    fund_master_summary(dfs)
    validate_amfi_codes(dfs)
    print("\nDay 1 ingestion complete: all 10 datasets loaded successfully.")
