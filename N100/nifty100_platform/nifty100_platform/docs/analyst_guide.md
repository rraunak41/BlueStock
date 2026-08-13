# Nifty 100 Financial Intelligence Platform — Analyst Guide

## 1. What you're looking at

This is a working analytics build covering all 92 Nifty 100 companies in the
provided datasets: a validated SQLite database, a 50+ KPI ratio engine, an
investment screener, sector/peer analytics, cash-flow intelligence, 92 PDF
tearsheets, and an interactive dashboard.

## 2. Quick start

```bash
pip install pandas numpy scipy scikit-learn openpyxl PyYAML reportlab matplotlib seaborn --break-system-packages

# Run the pipeline in order:
python src/etl/run_etl.py                    # builds data/db/nifty100.db
python src/analytics/ratios.py                # 50+ KPIs -> financial_ratios table
python src/analytics/screener.py               # 6 preset screens -> reports/screener_output.xlsx
python src/analytics/peer.py                    # 11 peer groups -> reports/peer_comparison.xlsx
python src/analytics/sector.py                  # sector benchmarks -> reports/sector_benchmarks.csv
python src/analytics/cashflow_kpis.py           # cash flow intelligence -> reports/cashflow_intelligence.xlsx
python src/analytics/health_and_nlp.py          # health scores + auto pros/cons
python src/analytics/clustering.py              # KMeans clusters + portfolio stats
python src/reports/tearsheet.py --all           # 92 PDF tearsheets -> reports/tearsheets/
python src/reports/portfolio_and_sector.py      # portfolio summary + 10 sector PDFs

# Open the dashboard (no server needed):
open dashboard/nifty100_dashboard.html

# Run tests:
pytest tests/ -v
```

All scripts add `src/` to the Python path automatically or via `PYTHONPATH=src`.
Run everything from the project root.

## 3. Using the Screener

Open `reports/screener_output.xlsx` for the 6 pre-built screens (Quality
Compounder, Value Pick, Growth Accelerator, Dividend Champion, Debt-Free Blue
Chip, Turnaround Watch), or use the **Screener** tab in the dashboard for
live, sector-filterable results.

To create a new screen or change thresholds, edit `config/screener_config.yaml`
— no code changes required. Add a new entry under `presets:` with your own
`filters` (any column in the screener universe, with `min`/`max` bounds) and
a `rank_by` column.

## 4. Using the Dashboard

`dashboard/nifty100_dashboard.html` is a single self-contained file — open it
directly in any browser. Seven pages:

1. **Overview** — headline KPIs, sector mix, quality-score distribution, top 15 companies
2. **Company Profile** — search any of 92 companies for KPI tiles, trend charts, pros/cons
3. **Screener** — all 6 presets with a sector filter and sortable results table
4. **Peer Comparison** — radar chart + percentile table for any of the 11 peer groups
5. **Sector Analysis** — median KPIs by sector, revenue-vs-ROE bubble chart
6. **Capital Allocation** — CFO/CFI/CFF pattern classification across all companies
7. **Clusters** — KMeans 5-cluster segmentation, sizes and scatter view

## 5. Interpreting the Composite Quality Score

`0–100`, computed per company (latest year): 30% ROE + 25% Free Cash Flow +
25% ROCE + 20% low-leverage (Debt-to-Equity, inverted), each percentile-ranked
and winsorised at P10/P90 to limit outlier distortion. Bands: **Excellent**
(≥70), **Moderate** (40–70), **Weak** (<40).

## 6. Known data caveats (read before drawing conclusions)

- **market_cap.xlsx is simulated**, and its P/E / P/B multiples run
  structurally higher than real Indian-market norms — this is why the "Value
  Pick" and a few other screens return fewer/more matches than the spec's
  expected range. See Section 6 of the build report for detail.
- **2 of 92 companies** (insufficient multi-year history) are excluded from
  CAGR-dependent views (screener, health score, clustering) but remain in the
  base company/P&L/BS/CF tables.
- **Extreme ROE values** (e.g. >1000%) occur where a company's equity base is
  near zero in a given year — these are logged, not errors. See
  `reports/ratio_edge_cases.log`.
- All monetary figures are in ₹ Crore unless stated otherwise.

## 7. Where everything lives

See the root `README.md` for the full folder structure and file-by-file
deliverables map.
