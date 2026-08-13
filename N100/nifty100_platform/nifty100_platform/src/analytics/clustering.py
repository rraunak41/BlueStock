"""
Nifty 100 Financial Intelligence Platform
Module 10: Statistical Analysis & Clustering (bonus)

KMeans clustering by financial profile, portfolio-level percentile stats,
correlation matrix, and z-score outlier detection.
"""
import sys
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / "data" / "db" / "nifty100.db"
REPORTS = BASE / "reports"

CLUSTER_FEATURES = ["return_on_equity_pct", "debt_to_equity", "revenue_cagr_5yr_pct",
                     "pat_cagr_5yr_pct", "operating_profit_margin_pct"]

CLUSTER_NAMES = {
    0: "High-Quality Growth", 1: "Defensive / Low Leverage", 2: "Value / Cyclical",
    3: "High Leverage / Turnaround", 4: "Premium Compounder",
}


def run_clustering(conn, n_clusters=5):
    sys.path.insert(0, str(BASE / "src"))
    from analytics.screener import build_screener_universe
    universe = build_screener_universe(conn)

    X = universe[CLUSTER_FEATURES].copy()
    X = X.fillna(X.median())
    Xs = StandardScaler().fit_transform(X)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(Xs)
    distances = km.transform(Xs).min(axis=1)

    universe = universe.copy()
    universe["cluster_id"] = labels
    universe["distance_from_centroid"] = distances.round(3)

    # Assign descriptive names by ranking clusters on mean ROE (proxy for quality)
    cluster_roe = universe.groupby("cluster_id")["return_on_equity_pct"].mean().sort_values(ascending=False)
    name_map = {cid: CLUSTER_NAMES.get(i, f"Cluster {cid}") for i, cid in enumerate(cluster_roe.index)}
    universe["cluster_name"] = universe["cluster_id"].map(name_map)

    return universe[["company_id", "company_name", "cluster_id", "cluster_name", "distance_from_centroid"] + CLUSTER_FEATURES]


def portfolio_stats(universe: pd.DataFrame) -> pd.DataFrame:
    metrics = ["return_on_equity_pct", "return_on_capital_pct", "debt_to_equity",
               "net_profit_margin_pct", "pe_ratio", "pb_ratio", "revenue_cagr_5yr_pct",
               "pat_cagr_5yr_pct", "free_cash_flow_cr", "composite_quality_score"]
    rows = []
    for m in metrics:
        if m not in universe.columns:
            continue
        s = universe[m].dropna()
        rows.append({
            "metric": m, "P10": s.quantile(0.10), "P25": s.quantile(0.25), "P50": s.quantile(0.50),
            "P75": s.quantile(0.75), "P90": s.quantile(0.90), "Mean": s.mean(), "Std": s.std(),
        })
    return pd.DataFrame(rows).round(2)


def outlier_report(universe: pd.DataFrame) -> pd.DataFrame:
    metrics = ["return_on_equity_pct", "debt_to_equity", "revenue_cagr_5yr_pct"]
    rows = []
    for sector, g in universe.groupby("broad_sector"):
        for m in metrics:
            mean, std = g[m].mean(), g[m].std()
            if std == 0 or pd.isna(std):
                continue
            z = (g[m] - mean) / std
            outliers = g[z.abs() > 3]
            for cid, zval in zip(outliers["company_id"], z[z.abs() > 3]):
                rows.append({"company_id": cid, "metric": m, "z_score": round(zval, 2),
                             "sector": sector, "sector_mean": round(mean, 2), "sector_std": round(std, 2)})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)

    print("Running KMeans clustering (5 clusters, StandardScaler)...")
    clustered = run_clustering(conn)
    clustered.to_csv(REPORTS / "cluster_labels.csv", index=False)
    clustered.to_sql("clusters", conn, if_exists="replace", index=False)
    print(clustered["cluster_name"].value_counts().to_string())

    print("\nComputing portfolio-level statistics (P10-P90)...")
    sys.path.insert(0, str(BASE / "src"))
    from analytics.screener import build_screener_universe
    universe = build_screener_universe(conn)
    pstats = portfolio_stats(universe)
    pstats.to_csv(REPORTS / "portfolio_stats.csv", index=False)
    print(pstats.to_string(index=False))

    print("\nDetecting outliers (|Z|>3 within sector)...")
    outliers = outlier_report(universe)
    outliers.to_csv(REPORTS / "outlier_report.csv", index=False)
    print(f"  {len(outliers)} outliers flagged")

    # Correlation matrix
    corr_cols = ["return_on_equity_pct", "return_on_capital_pct", "debt_to_equity",
                 "net_profit_margin_pct", "revenue_cagr_5yr_pct", "pat_cagr_5yr_pct",
                 "free_cash_flow_cr", "pe_ratio", "pb_ratio", "composite_quality_score"]
    corr = universe[corr_cols].corr().round(2)
    corr.to_csv(REPORTS / "correlation_matrix.csv")

    conn.commit()
    conn.close()
    print("\nModule 10 complete.")
