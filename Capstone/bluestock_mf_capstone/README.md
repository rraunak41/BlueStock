# Bluestock MF Analytics Platform

End-to-end Mutual Fund Analytics capstone for Bluestock Fintech — ETL pipeline,
SQLite database, EDA, performance & risk analytics, and a 5-page interactive
dashboard, built from 10 AMFI-anchored datasets covering 40 real mutual fund
schemes.

> All data is derived from publicly available AMFI India, mfapi.in, and
> NSE/BSE information. This project is for educational purposes only and
> does not constitute financial advice.

## Quick start

```bash
# 1. Install dependencies
pip install pandas numpy matplotlib seaborn scipy sqlalchemy --break-system-packages

# 2. Run the full pipeline in order
python scripts/data_ingestion.py        # Day 1 — load & validate 10 raw CSVs
python scripts/data_cleaning.py         # Day 2 — clean → data/processed/
python scripts/load_database.py         # Day 2 — build SQLite star schema
python scripts/eda_analysis.py          # Day 3 — 18 EDA charts → reports/charts/
python scripts/performance_analytics.py # Day 4 — Sharpe/Sortino/Alpha/Beta/scorecard
python scripts/advanced_analytics.py    # Day 6 — VaR/CVaR, cohorts, HHI, rolling Sharpe
python scripts/recommender.py --risk Moderate --top_n 3   # standalone recommender CLI

# 3. Open the dashboard
open dashboard/bluestock_mf_dashboard.html   # or double-click it — no server needed
```

## Folder structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/            10 original CSVs
│   ├── processed/      10 cleaned CSVs (output of data_cleaning.py)
│   └── db/              bluestock_mf.db (SQLite, 11-table star schema)
├── scripts/
│   ├── data_ingestion.py        Day 1 — load & validate
│   ├── data_cleaning.py         Day 2 — cleaning
│   ├── load_database.py         Day 2 — schema + load
│   ├── eda_analysis.py          Day 3 — EDA charts
│   ├── performance_analytics.py Day 4 — risk/return metrics + scorecard
│   ├── advanced_analytics.py    Day 6 — VaR, cohorts, HHI, rolling Sharpe
│   └── recommender.py           Standalone fund recommender CLI
├── sql/
│   ├── schema.sql       DDL for the 11-table star schema
│   └── queries.sql      10 core analytical queries
├── dashboard/
│   └── bluestock_mf_dashboard.html   5-page interactive web dashboard
├── reports/
│   ├── charts/                        18 EDA/analytics PNG charts
│   ├── Bluestock_MF_Final_Report.docx / .pdf
│   ├── Bluestock_MF_Presentation.pptx
│   ├── EDA_Findings.md
│   ├── Advanced_Analytics_Summary.md
│   ├── fund_scorecard.csv, var_cvar_report.csv, cohort_analysis.csv, ...
│   └── queries_output.txt
├── data_dictionary.md
└── README.md
```

## Database schema (star schema)

| Table | Type | Rows |
|---|---|---|
| dim_fund | Dimension | 40 |
| dim_date | Dimension | 1,608 |
| fact_nav | Fact | 46,000 |
| fact_transactions | Fact | 32,778 |
| fact_performance | Fact | 40 |
| fact_portfolio | Fact | 322 |
| fact_aum | Fact | 90 |
| fact_sip_industry | Fact | 48 |
| fact_category_inflows | Fact | 144 |
| fact_folio_count | Fact | 21 |
| fact_benchmark | Fact | 8,050 |

See `data_dictionary.md` for full column-level documentation.

## Dashboard

`dashboard/bluestock_mf_dashboard.html` is a **self-contained, single-file**
interactive dashboard (Chart.js) — no server, database connection, or Power BI
license required to view it. It's the browser-based alternative to a native
`.pbix` file, chosen because Power BI Desktop is a licensed Windows
application not available in this build environment. The same cleaned
CSVs / SQLite database can be pointed at Power BI Desktop directly if needed.

5 pages: **Industry Overview · Fund Performance · Investor Analytics ·
SIP & Market Trends · Portfolio & Risk** — each with live slicers, a KPI
ticker, and sortable/filterable charts and tables.

## Key metrics computed

- **CAGR** (1/3/5yr, trailing from latest NAV date)
- **Sharpe & Sortino ratio** (annualised, Rf = 6.5%)
- **Alpha & Beta** vs Nifty 100 (OLS regression)
- **Maximum Drawdown** (from running-peak NAV)
- **Value at Risk (95%) & CVaR** (historical simulation)
- **Composite Fund Scorecard** (0–100, blended return/risk/cost rank)
- **Tracking Error** vs benchmark (top 5 scorecard funds)
- **Sector concentration (HHI)** per equity portfolio
- **Investor cohort & SIP-continuity ("at-risk") analysis**

## Known limitations

See Section 11 of the Final Report for full details:
- NAV and transaction data are simulated (anchored to real published AMFI
  figures), not pulled live from AMFI/mfapi.in APIs.
- Independently re-computed metrics differ modestly from the pre-supplied
  `scheme_performance.csv` due to a "trailing from latest date" vs.
  "fixed as-of date" methodology difference — see `reports/computed_metrics.csv`.
- The dashboard is HTML/JS, not a native `.pbix`, for the reason above.
