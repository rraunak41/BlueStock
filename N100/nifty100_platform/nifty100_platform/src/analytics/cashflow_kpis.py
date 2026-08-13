"""
Nifty 100 Financial Intelligence Platform
Module 7: Cash Flow Intelligence

CFO quality score, CapEx intensity tier, FCF CAGR, FCF conversion tier,
debt-repayment / distress-pattern detection, full capital allocation matrix.
"""
import sys
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / "data" / "db" / "nifty100.db"
REPORTS = BASE / "reports"


def cfo_quality_score(ratios: pd.DataFrame) -> pd.DataFrame:
    """5yr avg CFO/PAT ratio -> High Quality Earnings (>1.0) / Accrual Risk (<0.5) / Moderate."""
    avg5 = (ratios.sort_values("year").groupby("company_id").tail(5)
            .groupby("company_id")["cfo_pat_ratio"].mean().reset_index())
    avg5.columns = ["company_id", "cfo_pat_5yr_avg"]
    avg5["cfo_quality_label"] = np.select(
        [avg5["cfo_pat_5yr_avg"] > 1.0, avg5["cfo_pat_5yr_avg"] < 0.5],
        ["High Quality Earnings", "Accrual Risk"],
        default="Moderate",
    )
    return avg5


def capex_intensity_tier(ratios: pd.DataFrame) -> pd.DataFrame:
    latest = ratios.sort_values("year").groupby("company_id").tail(1)
    out = latest[["company_id", "capex_intensity_pct"]].copy()
    out["capex_tier"] = np.select(
        [out["capex_intensity_pct"] < 3, out["capex_intensity_pct"] > 8],
        ["Asset-Light", "Capital-Intensive"],
        default="Moderate",
    )
    return out


def fcf_cagr(ratios: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cid, g in ratios.sort_values("year").groupby("company_id"):
        g = g.set_index("year")
        s = g["free_cash_flow_cr"]
        rec = {"company_id": cid}
        for yrs in (5, 10):
            if len(s) < yrs + 1:
                rec[f"fcf_cagr_{yrs}yr_pct"] = np.nan
                continue
            base, end = s.iloc[-(yrs + 1)], s.iloc[-1]
            if base > 0 and end > 0:
                rec[f"fcf_cagr_{yrs}yr_pct"] = ((end / base) ** (1 / yrs) - 1) * 100
            else:
                rec[f"fcf_cagr_{yrs}yr_pct"] = np.nan
        rows.append(rec)
    return pd.DataFrame(rows)


def fcf_conversion_tier(ratios: pd.DataFrame) -> pd.DataFrame:
    latest = ratios.sort_values("year").groupby("company_id").tail(1)
    out = latest[["company_id", "fcf_conversion_pct"]].copy()
    out["fcf_conversion_tier"] = np.select(
        [out["fcf_conversion_pct"] > 60, out["fcf_conversion_pct"] < 30],
        ["Efficient", "CapEx Heavy"],
        default="Moderate",
    )
    return out


def deleveraging_and_distress(conn) -> pd.DataFrame:
    """CFF<0 & borrowings declining -> Deleveraging. CFO<0 & CFF>0 -> Distress Signal."""
    bs = pd.read_sql("SELECT company_id, year, borrowings FROM balancesheet", conn)
    ratios = pd.read_sql("SELECT company_id, year, cfo_sign, cff_sign FROM financial_ratios", conn)
    df = ratios.merge(bs, on=["company_id", "year"])
    df = df.sort_values(["company_id", "year"])
    df["borrowings_prev"] = df.groupby("company_id")["borrowings"].shift(1)
    df["deleveraging_flag"] = (df["cff_sign"] == "-") & (df["borrowings"] < df["borrowings_prev"])
    df["distress_flag"] = (df["cfo_sign"] == "-") & (df["cff_sign"] == "+")
    return df[["company_id", "year", "deleveraging_flag", "distress_flag"]]


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
    companies = pd.read_sql("SELECT id AS company_id, company_name FROM companies", conn)

    print("Computing CFO Quality Score...")
    cfo_q = cfo_quality_score(ratios)
    print(cfo_q["cfo_quality_label"].value_counts().to_string())

    print("\nComputing CapEx Intensity tiers...")
    capex_t = capex_intensity_tier(ratios)
    print(capex_t["capex_tier"].value_counts().to_string())

    print("\nComputing FCF CAGR (5yr, 10yr)...")
    fcf_c = fcf_cagr(ratios)

    print("\nComputing FCF Conversion tiers...")
    fcf_conv = fcf_conversion_tier(ratios)
    print(fcf_conv["fcf_conversion_tier"].value_counts().to_string())

    print("\nDetecting deleveraging & distress patterns...")
    dd = deleveraging_and_distress(conn)
    print(f"  Deleveraging events: {dd['deleveraging_flag'].sum()}  |  Distress events: {dd['distress_flag'].sum()}")

    # Combine into cashflow_intelligence.xlsx
    combined = (cfo_q.merge(capex_t, on="company_id", how="outer")
                .merge(fcf_c, on="company_id", how="outer")
                .merge(fcf_conv, on="company_id", how="outer")
                .merge(companies, on="company_id", how="left"))
    latest_dd = dd.sort_values("year").groupby("company_id").tail(1)
    combined = combined.merge(latest_dd[["company_id", "deleveraging_flag", "distress_flag"]], on="company_id", how="left")

    cols = ["company_id", "company_name", "cfo_pat_5yr_avg", "cfo_quality_label",
            "capex_intensity_pct", "capex_tier", "fcf_cagr_5yr_pct", "fcf_cagr_10yr_pct",
            "fcf_conversion_pct", "fcf_conversion_tier", "deleveraging_flag", "distress_flag"]
    combined = combined[cols].round(2)
    combined.to_excel(REPORTS / "cashflow_intelligence.xlsx", index=False)

    distress_companies = combined[combined.distress_flag == True]
    distress_companies.to_csv(REPORTS / "distress_alerts.csv", index=False)

    print(f"\ncashflow_intelligence.xlsx written -> reports/ ({len(combined)} companies)")
    print(f"distress_alerts.csv written -> reports/ ({len(distress_companies)} flagged)")
    conn.close()
