"""
Bluestock Fintech - Mutual Fund Analytics Platform
Simple rule-based fund recommendation engine.

Usage:
    python recommender.py --risk Moderate --top_n 3
"""
import argparse
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed"

RISK_MAP = {
    "Low": ["Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High": ["High", "Very High"],
}


def recommend(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    perf = pd.read_csv(PROC / "scheme_performance_clean.csv")
    grades = RISK_MAP.get(risk_appetite, [risk_appetite])
    pool = perf[perf["risk_grade"].isin(grades)]
    return pool.sort_values("sharpe_ratio", ascending=False)[
        ["scheme_name", "fund_house", "risk_grade", "sharpe_ratio",
         "return_3yr_pct", "expense_ratio_pct"]
    ].head(top_n)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bluestock MF Fund Recommender")
    parser.add_argument("--risk", choices=["Low", "Moderate", "High"], default="Moderate",
                         help="Investor risk appetite")
    parser.add_argument("--top_n", type=int, default=3, help="Number of funds to recommend")
    args = parser.parse_args()

    results = recommend(args.risk, args.top_n)
    print(f"\nTop {args.top_n} funds for '{args.risk}' risk appetite:\n")
    print(results.to_string(index=False))
