# Nifty 100 Financial Intelligence Platform

A working build of the platform specified in DAD-PROJ-001 v1.0 — an ETL
pipeline, a 50+ KPI financial ratio engine, an investment screener, financial
health scoring, sector & peer analytics, cash flow intelligence, automated
PDF reporting, and an interactive dashboard, covering 92 Nifty 100 companies.

> Delivered as a single-session implementation covering the full analytical
> scope of the 45-day/6-sprint specification. See `docs/Nifty100_Build_Report.pdf`
> Section 10 for the two scope adaptations (no live FastAPI server; the
> dashboard is a self-contained HTML app rather than Streamlit).

## Quick start

```bash
pip install pandas numpy scipy scikit-learn openpyxl PyYAML reportlab matplotlib seaborn --break-system-packages

python src/etl/run_etl.py                      # -> data/db/nifty100.db
python src/analytics/ratios.py                  # -> financial_ratios table (50+ KPIs)
python src/analytics/screener.py                # -> reports/screener_output.xlsx
python src/analytics/peer.py                     # -> reports/peer_comparison.xlsx
python src/analytics/sector.py                   # -> reports/sector_benchmarks.csv
python src/analytics/cashflow_kpis.py            # -> reports/cashflow_intelligence.xlsx
python src/analytics/health_and_nlp.py           # -> health scores + pros/cons
python src/analytics/clustering.py               # -> cluster_labels.csv, portfolio_stats.csv
python src/reports/tearsheet.py --all            # -> reports/tearsheets/ (92 PDFs)
python src/reports/portfolio_and_sector.py       # -> reports/portfolio/, reports/sector/

open dashboard/nifty100_dashboard.html            # no server required

pytest tests/ -v                                  # 56 tests
```

## Folder structure

```
nifty100_platform/
├── data/
│   ├── raw/                 7 core Excel files (companies, P&L, BS, CF, analysis, documents, prosandcons)
│   ├── supporting/          5 supplementary Excel files (sectors, stock_prices, market_cap, financial_ratios, peer_groups)
│   └── db/
│       ├── nifty100.db      SQLite — 11 base tables + 4 derived analytics tables
│       └── exploratory_queries.sql   10 exploratory SQL queries
├── src/
│   ├── etl/
│   │   ├── loader.py         Excel loader (header=1 core / header=0 supplementary)
│   │   ├── normaliser.py     Ticker/year normalisation utilities
│   │   ├── validator.py      16 DQ rules (DQ-01 .. DQ-16)
│   │   └── run_etl.py        Master pipeline: clean, normalise, dedupe, load
│   ├── analytics/
│   │   ├── ratios.py          50+ KPI financial ratio engine
│   │   ├── screener.py        6 preset investment screens
│   │   ├── peer.py             11 peer-group percentile comparison engine
│   │   ├── sector.py           Sector benchmarks + valuation flags
│   │   ├── cashflow_kpis.py    CFO quality, CapEx intensity, distress detection
│   │   ├── health_and_nlp.py   Financial Health Score + auto pros/cons generator
│   │   └── clustering.py       KMeans clustering + portfolio statistics
│   └── reports/
│       ├── tearsheet.py               Company tearsheet PDF generator (2-page × 92)
│       └── portfolio_and_sector.py    Portfolio summary + sector PDF reports
├── dashboard/
│   └── nifty100_dashboard.html   7-page interactive dashboard (self-contained)
├── config/
│   └── screener_config.yaml   All screener thresholds — analyst-editable, no code changes
├── tests/
│   ├── etl/test_normalise.py     21 tests
│   ├── kpi/test_ratios.py        12 tests
│   ├── dq/test_rules.py           8 tests
│   └── test_integration.py       15 tests — live checks against the built database
├── reports/                  All generated CSV/Excel/PDF outputs (see docs/analyst_guide.md)
│   ├── charts/                Chart PNGs
│   ├── tearsheets/             92 company tearsheet PDFs
│   ├── sector/                 10 sector PDF reports
│   └── portfolio/              Portfolio summary PDF
└── docs/
    ├── Nifty100_Build_Report.docx / .pdf   Full build report
    ├── Nifty100_Presentation.pptx           11-slide presentation
    └── analyst_guide.md                     How to use the screener & dashboard
```

## Database schema

11 base tables (companies, profitandloss, balancesheet, cashflow, analysis,
documents, prosandcons, sectors, stock_prices, market_cap, peer_groups) plus
4 derived analytics tables (financial_ratios, growth_cagr, quality_score,
health_scores, peer_percentiles, clusters, sector_benchmarks — written by the
analytics scripts). Zero foreign-key violations (`PRAGMA foreign_key_check`
returns empty).

## Validated accuracy

The independently-computed `financial_ratios` table matches the pre-supplied
`financial_ratios.xlsx` reference **exactly** — 0.00 mean absolute difference
across all 1,041 matched company-year rows for ROE, Debt-to-Equity, and Free
Cash Flow. See `docs/Nifty100_Build_Report.pdf` Section 5 for detail.

## Known data caveats

See `docs/analyst_guide.md` Section 6 — most importantly, `market_cap.xlsx`
valuation multiples are simulated and run structurally higher than real
Indian-market norms, which affects a few screener preset match-counts
(documented, not silently altered).

## Testing

56 pytest tests, 100% passing — unit tests for normalisation, KPI formulas
(including edge cases: negative equity, debt-free, CAGR turnaround), the 16
DQ rules (crafted violation fixtures), plus 15 integration tests running live
queries against the built database. HTML report: `reports/pytest_report.html`.
