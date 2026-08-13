"""
Bluestock Fintech - Mutual Fund Analytics Platform
Day 4: Fund Performance Analytics
Computes CAGR, Sharpe, Sortino, Alpha/Beta (vs benchmark), Max Drawdown,
and a composite Fund Scorecard. Cross-checks against the pre-supplied
scheme_performance.csv metrics.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed"
CHARTS = BASE / "reports" / "charts"
RF = 0.065  # RBI repo-rate proxy, annualised risk-free rate

fund_master = pd.read_csv(PROC / "fund_master_clean.csv")
nav = pd.read_csv(PROC / "nav_history_clean.csv", parse_dates=["date"])
bench = pd.read_csv(PROC / "benchmark_indices_clean.csv", parse_dates=["date"])
perf_given = pd.read_csv(PROC / "scheme_performance_clean.csv")
perf_given["amfi_code"] = perf_given["amfi_code"].astype(str)

nav["amfi_code"] = nav["amfi_code"].astype(str)
fund_master["amfi_code"] = fund_master["amfi_code"].astype(str)

# ---- 1. Daily returns already computed in cleaning step (daily_return_pct) ----
nav["daily_return"] = nav["daily_return_pct"] / 100

# ---- 2. CAGR for 1/3/5yr windows per fund ----
def cagr_for_window(g, years):
    g = g.sort_values("date")
    end_date = g["date"].max()
    start_date = end_date - pd.DateOffset(years=years)
    window = g[g["date"] >= start_date]
    if len(window) < 2:
        return np.nan
    n_years = (window["date"].max() - window["date"].min()).days / 365.25
    if n_years <= 0:
        return np.nan
    return ((window["nav"].iloc[-1] / window["nav"].iloc[0]) ** (1 / n_years) - 1) * 100

cagr_rows = []
for code, g in nav.groupby("amfi_code"):
    cagr_rows.append({
        "amfi_code": code,
        "cagr_1yr_computed": cagr_for_window(g, 1),
        "cagr_3yr_computed": cagr_for_window(g, 3),
        "cagr_5yr_computed": cagr_for_window(g, 4),  # data spans ~4.5yrs
    })
cagr_df = pd.DataFrame(cagr_rows)

# ---- 3. Sharpe Ratio (annualised) ----
sharpe_rows = []
for code, g in nav.groupby("amfi_code"):
    r = g.sort_values("date")["daily_return"].dropna()
    if len(r) < 30:
        continue
    excess = r.mean() * 252 - RF
    ann_std = r.std() * np.sqrt(252)
    sharpe = excess / ann_std if ann_std > 0 else np.nan
    # Sortino: only downside deviation
    downside = r[r < 0]
    downside_std = downside.std() * np.sqrt(252) if len(downside) > 1 else np.nan
    sortino = excess / downside_std if downside_std and downside_std > 0 else np.nan
    sharpe_rows.append({"amfi_code": code, "sharpe_computed": sharpe, "sortino_computed": sortino,
                         "ann_std_computed": ann_std * 100})
risk_df = pd.DataFrame(sharpe_rows)

# ---- 4. Alpha & Beta vs Nifty 100 (OLS regression) ----
nifty100 = bench[bench.index_name.str.contains("100", case=False, na=False)]
if nifty100.empty:
    nifty100 = bench[bench.index_name.str.contains("NIFTY", case=False, na=False)]
nifty100 = nifty100.sort_values("date").copy()
nifty100["bench_return"] = nifty100["close_value"].pct_change()

ab_rows = []
for code, g in nav.groupby("amfi_code"):
    g = g.sort_values("date")[["date", "daily_return"]].dropna()
    merged = g.merge(nifty100[["date", "bench_return"]], on="date", how="inner").dropna()
    if len(merged) < 30:
        continue
    slope, intercept, r_value, p_value, std_err = stats.linregress(merged["bench_return"], merged["daily_return"])
    alpha_ann = intercept * 252 * 100
    ab_rows.append({"amfi_code": code, "alpha_computed": alpha_ann, "beta_computed": slope, "r_squared": r_value ** 2})
ab_df = pd.DataFrame(ab_rows)

# ---- 5. Maximum Drawdown ----
dd_rows = []
for code, g in nav.groupby("amfi_code"):
    g = g.sort_values("date")
    running_max = g["nav"].cummax()
    drawdown = g["nav"] / running_max - 1
    dd_rows.append({"amfi_code": code, "max_drawdown_computed": drawdown.min() * 100,
                     "max_drawdown_date": g.loc[drawdown.idxmin(), "date"]})
dd_df = pd.DataFrame(dd_rows)

# ---- Combine all computed metrics ----
computed = cagr_df.merge(risk_df, on="amfi_code").merge(ab_df, on="amfi_code").merge(dd_df, on="amfi_code")
computed = computed.merge(fund_master[["amfi_code", "scheme_name", "fund_house", "category", "risk_category", "expense_ratio_pct"]], on="amfi_code")
computed.to_csv(BASE / "reports" / "computed_metrics.csv", index=False)
print(f"Computed metrics for {len(computed)} funds -> reports/computed_metrics.csv")

# ---- Cross-check vs provided scheme_performance.csv ----
check = computed.merge(perf_given[["amfi_code", "return_3yr_pct", "sharpe_ratio", "max_drawdown_pct"]], on="amfi_code")
check["cagr_3yr_diff"] = (check["cagr_3yr_computed"] - check["return_3yr_pct"]).abs()
check["sharpe_diff"] = (check["sharpe_computed"] - check["sharpe_ratio"]).abs()
print("\nCross-check (computed vs provided) — mean absolute difference:")
print(f"  3yr CAGR diff: {check['cagr_3yr_diff'].mean():.2f} pct pts")
print(f"  Sharpe diff:   {check['sharpe_diff'].mean():.2f}")

# ---- 6. Fund Scorecard (composite score 0-100) ----
sc = perf_given.copy()
sc["rank_return_3yr"] = sc["return_3yr_pct"].rank(pct=True)
sc["rank_sharpe"] = sc["sharpe_ratio"].rank(pct=True)
sc["rank_alpha"] = sc["alpha"].rank(pct=True)
sc["rank_expense_inv"] = sc["expense_ratio_pct"].rank(pct=True, ascending=False)  # lower expense = higher rank
sc["rank_maxdd_inv"] = sc["max_drawdown_pct"].rank(pct=True)  # less negative (closer to 0) = higher rank

sc["fund_score"] = (
    0.30 * sc["rank_return_3yr"] +
    0.25 * sc["rank_sharpe"] +
    0.20 * sc["rank_alpha"] +
    0.15 * sc["rank_expense_inv"] +
    0.10 * sc["rank_maxdd_inv"]
) * 100
sc = sc.sort_values("fund_score", ascending=False)
scorecard_cols = ["amfi_code", "scheme_name", "fund_house", "category", "return_3yr_pct",
                   "sharpe_ratio", "alpha", "expense_ratio_pct", "max_drawdown_pct", "fund_score"]
sc[scorecard_cols].to_csv(BASE / "reports" / "fund_scorecard.csv", index=False)
print(f"\nFund scorecard written -> reports/fund_scorecard.csv")
print("\nTop 10 funds by composite score:")
print(sc[["scheme_name", "fund_score"]].head(10).to_string(index=False))

# ---- 7. Benchmark comparison chart: top 5 funds vs Nifty 50 / Nifty 100 ----
top5_codes = sc["amfi_code"].astype(str).head(5).tolist()
nifty50 = bench[bench.index_name.str.contains("50", na=False) & ~bench.index_name.str.contains("100")]
plt.figure(figsize=(11, 6))
for code in top5_codes:
    g = nav[nav.amfi_code == code].sort_values("date")
    name = fund_master.loc[fund_master.amfi_code == code, "scheme_name"].values[0]
    plt.plot(g["date"], g["nav"] / g["nav"].iloc[0] * 100, label=name[:30], linewidth=1.6)
for idx_name, color in [("NIFTY50", "black"), ("NIFTY100", "grey")]:
    g = bench[bench.index_name == idx_name].sort_values("date")
    if len(g):
        plt.plot(g["date"], g["close_value"] / g["close_value"].iloc[0] * 100, label=idx_name,
                  linestyle="--", color=color, linewidth=1.4)
plt.title("Top 5 Scorecard Funds vs Nifty 50 / Nifty 100 (Indexed, Base=100)")
plt.xlabel("Date"); plt.ylabel("Indexed Value")
plt.legend(fontsize=8, loc="upper left")
plt.tight_layout()
plt.savefig(CHARTS / "16_benchmark_comparison_top5.png", bbox_inches="tight")
plt.close()

# Tracking error (std of daily return diff vs Nifty100) for top 5
te_rows = []
for code in top5_codes:
    g = nav[nav.amfi_code == code].sort_values("date")[["date", "daily_return"]]
    merged = g.merge(nifty100[["date", "bench_return"]], on="date", how="inner").dropna()
    te = (merged["daily_return"] - merged["bench_return"]).std() * np.sqrt(252) * 100
    name = fund_master.loc[fund_master.amfi_code == code, "scheme_name"].values[0]
    te_rows.append({"scheme_name": name, "tracking_error_pct_ann": te})
te_df = pd.DataFrame(te_rows)
te_df.to_csv(BASE / "reports" / "tracking_error_top5.csv", index=False)
print("\nTracking error (top 5 vs Nifty 100):")
print(te_df.to_string(index=False))

print("\nDay 4 performance analytics complete.")
