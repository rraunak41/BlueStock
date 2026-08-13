"""
Nifty 100 Financial Intelligence Platform
Module 1: ETL — Schema / Data Quality Validator (16 DQ rules, DQ-01..DQ-16).
"""
from pathlib import Path
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normaliser import normalize_ticker, normalize_year

BASE = Path(__file__).resolve().parents[2]


def _flag(rows, rule_id, rule_name, severity, company_id, year, field, issue):
    rows.append({
        "rule_id": rule_id, "rule_name": rule_name, "severity": severity,
        "company_id": company_id, "year": year, "field": field, "issue": issue,
    })


def validate_all(dfs: dict) -> pd.DataFrame:
    """
    Run all 16 DQ rules against the normalised DataFrames dict.
    Returns a DataFrame of violations: rule_id, rule_name, severity, company_id, year, field, issue.
    """
    v = []
    companies = dfs["companies"]
    pl = dfs["profitandloss"]
    bs = dfs["balancesheet"]
    cf = dfs["cashflow"]
    docs = dfs["documents"]

    # DQ-01: Company PK uniqueness
    if len(companies) != companies["id"].nunique():
        dupes = companies[companies["id"].duplicated(keep=False)]["id"].unique()
        for d in dupes:
            _flag(v, "DQ-01", "Company PK Uniqueness", "CRITICAL", d, None, "id", "Duplicate ticker in companies table")

    # DQ-02: Annual PK uniqueness (company_id, year) in P&L / BS / CF
    for name, df in [("profitandloss", pl), ("balancesheet", bs), ("cashflow", cf)]:
        dupe_mask = df.duplicated(subset=["company_id", "year"], keep=False)
        for _, row in df[dupe_mask].iterrows():
            _flag(v, "DQ-02", "Annual PK Uniqueness", "CRITICAL", row["company_id"], row["year"],
                  f"{name}.(company_id,year)", "Duplicate annual record")

    # DQ-03: FK integrity — company_id in child tables must exist in companies.id
    valid_ids = set(companies["id"])
    for name, df in [("profitandloss", pl), ("balancesheet", bs), ("cashflow", cf),
                      ("documents", docs), ("analysis", dfs["analysis"]),
                      ("prosandcons", dfs["prosandcons"]), ("sectors", dfs["sectors"]),
                      ("stock_prices", dfs["stock_prices"]), ("market_cap", dfs["market_cap"]),
                      ("financial_ratios", dfs["financial_ratios"]), ("peer_groups", dfs["peer_groups"])]:
        orphans = df[~df["company_id"].isin(valid_ids)]
        for _, row in orphans.iterrows():
            _flag(v, "DQ-03", "FK Integrity", "CRITICAL", row["company_id"], None, f"{name}.company_id", "Orphan row — FK not in companies.id")

    # DQ-04: Balance sheet balance check
    bs_check = bs.copy()
    bs_check["diff_pct"] = (bs_check["total_assets"] - bs_check["total_liabilities"]).abs() / bs_check["total_assets"].replace(0, np.nan)
    bad = bs_check[bs_check["diff_pct"] > 0.01]
    for _, row in bad.iterrows():
        _flag(v, "DQ-04", "Balance Sheet Balance", "WARNING", row["company_id"], row["year"],
              "total_assets/total_liabilities", f"Mismatch {row['diff_pct']*100:.1f}%")

    # DQ-05: OPM cross-check
    pl_check = pl.copy()
    computed_opm = pl_check["operating_profit"] / pl_check["sales"].replace(0, np.nan) * 100
    diff = (pl_check["opm_percentage"] - computed_opm).abs()
    bad = pl_check[diff > 1.0]
    for _, row in bad.iterrows():
        _flag(v, "DQ-05", "OPM Cross-Check", "WARNING", row["company_id"], row["year"], "opm_percentage", "Source OPM diverges >1% from computed")

    # DQ-06: Positive sales
    bad = pl[pl["sales"] <= 0]
    for _, row in bad.iterrows():
        _flag(v, "DQ-06", "Positive Sales", "WARNING", row["company_id"], row["year"], "sales", "Sales <= 0")

    # DQ-07: Year format (after normalisation)
    for name, df in [("profitandloss", pl), ("balancesheet", bs), ("cashflow", cf)]:
        normed = df["year"].apply(normalize_year)
        bad_years = df[normed == "PARSE_ERROR"]
        for _, row in bad_years.iterrows():
            _flag(v, "DQ-07", "Year Format", "CRITICAL", row["company_id"], row["year"], f"{name}.year", "Unparseable year value")

    # DQ-08: Ticker format
    for _, row in companies.iterrows():
        t = normalize_ticker(row["id"])
        if not (2 <= len(t) <= 12):
            _flag(v, "DQ-08", "Ticker Format", "CRITICAL", row["id"], None, "id", f"Ticker length {len(t)} out of range 2-12")

    # DQ-09: Net cash check
    cf_check = cf.copy()
    computed_ncf = cf_check["operating_activity"] + cf_check["investing_activity"] + cf_check["financing_activity"]
    diff = (cf_check["net_cash_flow"] - computed_ncf).abs()
    bad = cf_check[diff > 10]
    for _, row in bad.iterrows():
        _flag(v, "DQ-09", "Net Cash Check", "WARNING", row["company_id"], row["year"], "net_cash_flow", "Mismatch vs CFO+CFI+CFF > 10 Cr tolerance")

    # DQ-10: Non-negative fixed assets
    bad = bs[bs["fixed_assets"] < 0]
    for _, row in bad.iterrows():
        _flag(v, "DQ-10", "Non-Negative Fixed Assets", "WARNING", row["company_id"], row["year"], "fixed_assets", "Negative fixed_assets")

    # DQ-11: Tax rate range
    bad = pl[(pl["tax_percentage"] < 0) | (pl["tax_percentage"] > 60)]
    for _, row in bad.iterrows():
        _flag(v, "DQ-11", "Tax Rate Range", "WARNING", row["company_id"], row["year"], "tax_percentage", f"Out of range: {row['tax_percentage']}")

    # DQ-12: Dividend payout cap
    bad = pl[pl["dividend_payout"] > 200]
    for _, row in bad.iterrows():
        _flag(v, "DQ-12", "Dividend Payout Cap", "WARNING", row["company_id"], row["year"], "dividend_payout", f">200%: {row['dividend_payout']}")

    # DQ-13: URL validity — logged as INFO (not fetched live to respect network limits; flagged for null/empty only)
    bad = docs[docs["Annual_Report"].isna() | (docs["Annual_Report"].astype(str).str.strip() == "")]
    for _, row in bad.iterrows():
        _flag(v, "DQ-13", "URL Validity", "WARNING", row["company_id"], row.get("Year"), "Annual_Report", "Missing/empty URL")

    # DQ-14: EPS sign consistency
    bad = pl[(pl["net_profit"] > 0) & (pl["eps"] <= 0)]
    for _, row in bad.iterrows():
        _flag(v, "DQ-14", "EPS Sign Consistency", "WARNING", row["company_id"], row["year"], "eps", "EPS<=0 while net_profit>0")

    # DQ-15: BS/exact balance informational counter
    exact_mismatch = (bs["total_assets"] != bs["total_liabilities"]).sum()
    _flag(v, "DQ-15", "Exact BS Balance (info)", "INFO", None, None, "total_assets/total_liabilities",
          f"{exact_mismatch} rows not exactly equal (informational only)")

    # DQ-16: Coverage check — each company needs >= 5 years of P&L, BS, CF
    for name, df in [("profitandloss", pl), ("balancesheet", bs), ("cashflow", cf)]:
        counts = df.groupby("company_id").size()
        short = counts[counts < 5]
        for cid, n in short.items():
            _flag(v, "DQ-16", "Coverage Check", "WARNING", cid, None, name, f"Only {n} years of history (<5)")

    return pd.DataFrame(v)


if __name__ == "__main__":
    sys.path.insert(0, str(BASE / "src" / "etl"))
    from loader import load_all
    print("Loading datasets for validation...")
    dfs = load_all()
    print("\nRunning 16 DQ rules...")
    violations = validate_all(dfs)
    out_path = BASE / "reports" / "validation_failures.csv"
    violations.to_csv(out_path, index=False)
    print(f"\nTotal violations: {len(violations)}")
    print(violations["severity"].value_counts().to_string())
    print(f"\nWritten to {out_path}")
    critical = violations[violations.severity == "CRITICAL"]
    print(f"\nCRITICAL violations: {len(critical)}")
    if len(critical):
        print(critical.head(10).to_string(index=False))
