const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, ImageRun, PageBreak, BorderStyle,
  Header, Footer, PageNumber, LevelFormat, convertInchesToTwip
} = require("docx");

const BASE = path.resolve(__dirname, "..", "..");
const CHARTS = path.join(BASE, "reports", "charts");

const NAVY = "0A2540";
const AMBER = "B8860B";
const SLATE = "4B5A70";
const LIGHT = "F3F6FA";

function img(name, width) {
  const p = path.join(CHARTS, name);
  const buf = fs.readFileSync(p);
  const { imageSize } = require("image-size");
  const dim = imageSize(buf);
  const w = width || 560;
  const h = Math.round((dim.height / dim.width) * w);
  return new ImageRun({ data: buf, transformation: { width: w, height: h }, type: "png" });
}

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 260, after: 120 } });
}
function h3(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 90 } });
}
function p(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    spacing: { after: 140 },
  });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 60 } });
}
function caption(text) {
  return new Paragraph({
    children: [new TextRun({ text, italics: true, size: 18, color: SLATE })],
    spacing: { after: 220 },
    alignment: AlignmentType.CENTER,
  });
}
function imgPara(name, width) {
  return new Paragraph({ children: [img(name, width)], alignment: AlignmentType.CENTER, spacing: { after: 60 } });
}

function simpleTable(headers, rows, widths) {
  const totalWidth = 9000;
  const colWidths = widths || headers.map(() => Math.floor(totalWidth / headers.length));
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((htext, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: NAVY },
      children: [new Paragraph({ children: [new TextRun({ text: htext, bold: true, color: "FFFFFF", size: 18 })] })],
    })),
  });
  const bodyRows = rows.map((r, ri) => new TableRow({
    children: r.map((cell, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: ri % 2 === 0 ? "FFFFFF" : LIGHT },
      children: [new Paragraph({ children: [new TextRun({ text: String(cell), size: 18 })] })],
    })),
  }));
  return new Table({ width: { size: totalWidth, type: WidthType.DXA }, columnWidths: colWidths, rows: [headerRow, ...bodyRows] });
}

// ---------- Load computed data for tables ----------
const csvParse = (file) => {
  const lines = fs.readFileSync(file, "utf8").trim().split("\n");
  const headers = lines[0].split(",");
  return lines.slice(1).map(line => {
    const vals = line.split(",");
    const obj = {};
    headers.forEach((h, i) => obj[h] = vals[i]);
    return obj;
  });
};

const scorecard = csvParse(path.join(BASE, "reports", "fund_scorecard.csv")).slice(0, 10);
const varReport = csvParse(path.join(BASE, "reports", "var_cvar_report.csv")).slice(0, 5);
const cohort = csvParse(path.join(BASE, "reports", "cohort_analysis.csv"));

// ================= DOCUMENT =================
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 22 } },
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", run: { size: 32, bold: true, color: NAVY, font: "Calibri" } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", run: { size: 26, bold: true, color: NAVY, font: "Calibri" } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", run: { size: 23, bold: true, color: AMBER, font: "Calibri" } },
    ],
  },
  sections: [
    // ---- COVER PAGE ----
    {
      properties: { page: { size: { width: 12240, height: 15840 } } },
      children: [
        new Paragraph({ text: "", spacing: { before: 1800 } }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "BLUESTOCK FINTECH", bold: true, size: 30, color: AMBER })],
          spacing: { after: 100 },
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Mutual Fund Analytics Platform", bold: true, size: 54, color: NAVY })],
          spacing: { after: 100 },
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard — Final Report", size: 26, color: SLATE })],
          spacing: { after: 800 },
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Capstone Project · Mutual Fund / Fintech Domain", size: 22, italics: true })],
          spacing: { after: 2400 },
        }),
        simpleTable(
          ["Field", "Detail"],
          [
            ["Company", "Bluestock Fintech Pvt. Ltd."],
            ["Domain", "Mutual Fund / Fintech"],
            ["Data Source", "AMFI India (Public), mfapi.in, NSE/BSE Public Data"],
            ["Technologies", "Python, SQL (SQLite), Interactive Web Dashboard, Pandas, Matplotlib, Seaborn"],
            ["Schemes Tracked", "40 real mutual fund schemes"],
            ["NAV History", "46,000 rows · Jan 2022 – May 2026"],
            ["Investor Transactions", "32,778 rows across 5,000 investors"],
            ["Prepared By", "Data Analyst — Bluestock Fintech"],
            ["Date", "August 2026"],
          ],
          [3000, 6000]
        ),
        new Paragraph({ text: "", spacing: { before: 1200 } }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "All data sourced from publicly available AMFI India, NSE, BSE and open API (mfapi.in) information. This project is for educational purposes only and does not constitute financial advice.", size: 18, italics: true, color: SLATE })],
        }),
        new Paragraph({ children: [new PageBreak()] }),
      ],
    },
    // ---- MAIN CONTENT ----
    {
      properties: {
        page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: "Bluestock Fintech | Mutual Fund Analytics Capstone", size: 16, color: SLATE })],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "Page ", size: 16 }), new TextRun({ children: [PageNumber.CURRENT], size: 16 })],
          })],
        }),
      },
      children: [
        h1("1. Executive Summary"),
        p("Bluestock Fintech commissioned this capstone project to build a full-stack Mutual Fund Analytics Platform covering 40 real mutual fund schemes across 10 major Indian AMCs. The project ingests publicly available AMFI/mfapi.in-anchored data, runs it through a Python ETL pipeline, loads it into a normalised SQLite star-schema database, and surfaces the results through 15+ EDA charts, a full performance & risk analytics suite, advanced investor-behaviour analytics, and a 5-page interactive web dashboard."),
        p("Headline findings: the tracked fund universe broadly mirrors real Indian market cycles (2022 correction, 2023-24 rally); SBI Mutual Fund remains the largest AMC by AUM; monthly SIP inflows trend upward, closing near the real Rs. 31,002 crore all-time high; and small/mid-cap funds carry materially higher volatility, VaR, and drawdown than large-cap or liquid funds — consistent with textbook risk-return expectations. A composite Fund Scorecard (0–100) ranks all 40 schemes on a blended return/risk/cost basis to support fund selection."),
        p("Deliverables: ETL scripts, a SQLite database with an 11-table schema, 10 analytical SQL queries, an 18-chart EDA notebook equivalent, a fund performance/risk engine (CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown, tracking error), advanced analytics (VaR/CVaR, rolling Sharpe, investor cohorts, SIP-continuity risk, a rule-based recommender, sector HHI concentration), and an interactive 5-page HTML dashboard replicating a Power BI-style experience with live filtering, sorting, and drill-down.", { }),

        h1("2. Problem Statement"),
        h3("P1 — Data Fragmentation"),
        p("NAV, AUM, SIP-flow, and portfolio-holdings data are scattered across different AMFI website sections in different formats. Solution: a single consolidated SQLite database built by an automated ETL pipeline."),
        h3("P2 — Performance Comparison Gap"),
        p("Investors struggle to compare funds across AMCs on a risk-adjusted basis. Solution: a computed Sharpe / Sortino / Alpha / Beta / Max-Drawdown suite plus a composite Fund Scorecard, all visualised in one dashboard."),
        h3("P3 — No Benchmark Tracking"),
        p("Most retail investors don't know if their fund beats its benchmark. Solution: NAV joined with benchmark index prices to compute rolling alpha and tracking error for the top-scoring funds."),
        h3("P4 — Investor Behaviour Blind Spot"),
        p("AMCs have limited visibility into how demographics and geography drive SIP behaviour. Solution: investor transaction analysis producing demographic and geographic segmentation, plus a SIP-continuity 'at-risk' flag."),
        h3("P5 — Slow Reporting"),
        p("Monthly MF reports are static PDFs. Solution: a live, filterable, self-service web dashboard fed directly by the ETL pipeline's output."),

        h1("3. Data Sources & Datasets"),
        p("All datasets are derived from publicly available AMFI India, mfapi.in, and NSE/BSE information, anchored to real published figures (e.g., SBI MF AUM Rs. 12.50 lakh crore, Dec 2025; industry AUM Rs. 81 lakh crore; SIP inflow Rs. 31,002 crore, Dec 2025 all-time high; 26.12 crore total folios)."),
        simpleTable(
          ["Dataset", "Rows", "Description"],
          [
            ["01_fund_master.csv", "40", "Scheme master: AMFI code, AMC, category, expense ratio, risk grade"],
            ["02_nav_history.csv", "46,000", "Daily NAV, Jan 2022 – May 2026, anchored to real mfapi.in values"],
            ["03_aum_by_fund_house.csv", "90", "Quarterly AUM by fund house, 2022–2025"],
            ["04_monthly_sip_inflows.csv", "48", "Monthly SIP inflow, active accounts, new registrations"],
            ["05_category_inflows.csv", "144", "Net inflow by category, FY 2024-25"],
            ["06_industry_folio_count.csv", "21", "Industry folio counts by Equity/Debt/Hybrid"],
            ["07_scheme_performance.csv", "40", "1/3/5yr returns, Sharpe, Sortino, Alpha, Beta, Max DD"],
            ["08_investor_transactions.csv", "32,778", "SIP/Lumpsum/Redemption transactions, 5,000 investors"],
            ["09_portfolio_holdings.csv", "322", "Top equity holdings by fund, sector, weight %"],
            ["10_benchmark_indices.csv", "8,050", "Daily closes: Nifty 50/100/Midcap150, BSE SmallCap, CRISIL"],
          ],
          [3200, 1200, 4600]
        ),

        h1("4. System Architecture & ETL Pipeline"),
        p("The pipeline follows a standard Extract → Transform → Load → Analyse → Visualise architecture, the same pattern used by real fintech platforms such as Zerodha and Groww."),
        bullet("Layer 1 (Extract): 10 pre-packaged CSVs, structured to mirror AMFI's NAVAll.txt, Historical NAV API, mfapi.in REST API, and AMFI Monthly Notes."),
        bullet("Layer 2 (Transform): Pandas cleaning — date parsing, holiday forward-fill on NAV, duplicate removal, AMFI-code validation, numeric coercion, and derived fields (daily returns, CAGR)."),
        bullet("Layer 3 (Load): SQLite database with an 11-table star schema (dim_fund, dim_date, fact_nav, fact_transactions, fact_performance, fact_portfolio, fact_aum, fact_sip_industry, fact_category_inflows, fact_folio_count, fact_benchmark), indexed on amfi_code + date."),
        bullet("Layer 4 (Analyse): Python risk/performance engine — Sharpe, Sortino, Alpha/Beta via OLS regression, Max Drawdown, VaR/CVaR, rolling Sharpe, sector HHI, investor cohorts."),
        bullet("Layer 5 (Visualise): A 5-page interactive HTML/JS dashboard (Chart.js) with live slicers, sortable tables, and drill-down — delivered as a standalone, browser-based alternative to Power BI Desktop."),

        h2("4.1 Database Schema (Star Schema)"),
        simpleTable(
          ["Table", "Type", "Rows"],
          [
            ["dim_fund", "Dimension", "40"],
            ["dim_date", "Dimension", "1,608"],
            ["fact_nav", "Fact", "46,000"],
            ["fact_transactions", "Fact", "32,778"],
            ["fact_performance", "Fact", "40"],
            ["fact_portfolio", "Fact", "322"],
            ["fact_aum", "Fact", "90"],
            ["fact_sip_industry", "Fact", "48"],
            ["fact_category_inflows", "Fact", "144"],
            ["fact_folio_count", "Fact", "21"],
            ["fact_benchmark", "Fact", "8,050"],
          ],
          [4000, 2500, 2500]
        ),

        h1("5. Data Cleaning & Quality"),
        bullet("NAV history reindexed to a full business-day calendar; holiday gaps forward-filled — 0 invalid (≤0/null) NAV rows found in the final dataset."),
        bullet("100% of AMFI codes in nav_history, scheme_performance, investor_transactions and portfolio_holdings validated against fund_master — no orphan codes."),
        bullet("0 negative Sharpe ratios and 0 out-of-range expense ratios (0.1%–2.5%) found in the provided performance file."),
        bullet("0 transactions with non-positive amounts; transaction_type and kyc_status values standardised."),
        p("Full column-level documentation is provided in the accompanying data_dictionary.md."),

        h1("6. Exploratory Data Analysis — Key Charts"),
        p("18 charts were produced (exceeding the 15+ target). Selected exhibits below; the complete set ships in reports/charts/."),

        h3("6.1 NAV Trend — All 40 Schemes"),
        imgPara("01_nav_trend_all_schemes.png", 500),
        caption("Figure 1. Indexed NAV (base=100) for all 40 tracked schemes, 2022–2026, with 5 schemes highlighted."),

        h3("6.2 AUM by Fund House"),
        imgPara("02_aum_growth_by_amc.png", 500),
        caption("Figure 2. Year-end peak AUM by fund house — SBI Mutual Fund leads throughout, consistent with its real ~Rs.12.5L Cr AUM (Dec 2025)."),

        h3("6.3 SIP Inflow Trend"),
        imgPara("03_sip_inflow_trend.png", 500),
        caption("Figure 3. Monthly SIP inflow, closing near the real Rs. 31,002 Cr all-time high (Dec 2025)."),

        h3("6.4 Category-wise Inflow Heatmap"),
        imgPara("04_category_inflow_heatmap.png", 500),
        caption("Figure 4. Net inflow by category, FY 2024-25."),

        h3("6.5 Risk vs Return"),
        imgPara("11_risk_return_scatter.png", 480),
        caption("Figure 5. 3-year return vs annualised std. dev, bubble size = AUM. Higher-return funds cluster at higher volatility, as expected."),

        h3("6.6 Return Correlation Matrix"),
        imgPara("08_correlation_matrix.png", 420),
        caption("Figure 6. Daily-return correlation across 10 selected funds — large-cap-heavy funds move together; liquid/debt funds are near-uncorrelated with equity."),

        h3("6.7 Investor Geography & Demographics"),
        imgPara("06a_geo_distribution_state.png", 420),
        caption("Figure 7. Transaction amount by state."),
        imgPara("05b_sip_amount_by_age.png", 460),
        caption("Figure 8. SIP amount distribution by age group — the 26–45 cohort shows the widest spread."),

        h3("6.8 Folio Count Growth"),
        imgPara("07_folio_count_growth.png", 480),
        caption("Figure 9. Total MF folios growing from 13.26 Cr to 26.12 Cr over the data window, matching real AMFI milestones."),

        h2("6.9 EDA — 10 Key Findings"),
        bullet("All 40 schemes track the real equity cycle: 2022 correction, 2023–24 rally, 2024-end pullback."),
        bullet("SBI Mutual Fund is the largest AMC by AUM throughout the sample period."),
        bullet("Monthly SIP inflows trend upward, closing near the real Dec-2025 all-time high."),
        bullet("Small/Mid Cap categories show the most volatile but generally highest FY24-25 net inflows."),
        bullet("Investors aged 26–45 drive the bulk of SIP volume and show the widest SIP-amount variance."),
        bullet("T30 cities contribute disproportionately to transaction value vs. B30, mirroring AMFI's real T30/B30 skew."),
        bullet("Total folios grew from 13.26 Cr to 26.12 Cr across the data window; equity folios dominate the mix."),
        bullet("Large-cap-heavy funds show high return correlation (>0.85); cross-category correlation is much lower, useful for diversification."),
        bullet("Banking, IT and FMCG are consistently the top-weighted sectors across equity portfolios."),
        bullet("Higher-return funds cluster at higher volatility, confirming the expected risk-return tradeoff."),

        h1("7. Fund Performance Analytics"),
        p("All 40 schemes were independently re-computed from raw NAV history (annualised Sharpe with Rf = 6.5%, Sortino with downside deviation only, Alpha/Beta via OLS regression on Nifty 100 daily returns, and Max Drawdown from running-peak NAV) and cross-checked against the provided scheme_performance.csv. The two sources broadly agree in direction and ranking; point-in-time differences reflect methodology (our CAGR windows are 'trailing N years from the latest NAV date' vs. the source file's fixed as-of date) — see Section 11, Limitations."),

        h3("7.1 Fund Scorecard — Top 10 (of 40)"),
        p("Composite Score = 30%×(3yr return rank) + 25%×(Sharpe rank) + 20%×(Alpha rank) + 15%×(low-expense rank) + 10%×(low-max-drawdown rank), all percentile-ranked 0–100."),
        simpleTable(
          ["Scheme", "3Y Return %", "Sharpe", "Alpha", "Score"],
          scorecard.map(r => [r.scheme_name.length > 38 ? r.scheme_name.slice(0, 38) + "…" : r.scheme_name, r.return_3yr_pct, r.sharpe_ratio, r.alpha, Number(r.fund_score).toFixed(1)]),
          [4200, 1600, 1400, 1400, 1400]
        ),

        h3("7.2 Benchmark Comparison — Top 5 Scorecard Funds vs Nifty 50/100"),
        imgPara("16_benchmark_comparison_top5.png", 500),
        caption("Figure 10. Indexed NAV of the top 5 scorecard funds vs Nifty 50 and Nifty 100. All 5 substantially outperform both benchmarks over the data window."),

        h1("8. Advanced Analytics & Risk Metrics"),
        h3("8.1 Value at Risk (95%) — Riskiest Funds"),
        simpleTable(
          ["Scheme", "Daily VaR 95% (%)", "Daily CVaR 95% (%)"],
          varReport.map(r => [r.scheme_name, Number(r.var_95_daily_pct).toFixed(2), Number(r.cvar_95_daily_pct).toFixed(2)]),
          [5500, 2000, 2000]
        ),
        p("Small-cap equity funds dominate the highest-VaR list, confirming they carry the largest one-day tail-risk exposure in the tracked universe."),

        h3("8.2 Rolling 90-Day Sharpe Ratio"),
        imgPara("17_rolling_sharpe.png", 500),
        caption("Figure 11. Rolling 90-day Sharpe for 5 sample funds — Sharpe is highly time-varying; funds attractive on a full-period basis can go through extended negative-Sharpe stretches."),

        h3("8.3 Investor Cohort Analysis"),
        simpleTable(
          ["Cohort (First-Tx Year)", "Avg SIP Amount (INR)", "Total Invested (INR)", "Investors", "Top Category"],
          cohort.map(r => [r.cohort_year, Number(r.avg_sip_amount).toLocaleString("en-IN", { maximumFractionDigits: 0 }), Number(r.total_invested).toLocaleString("en-IN"), r.num_investors, r.top_category_preference]),
          [2600, 2000, 2200, 1400, 1800]
        ),

        h3("8.4 Sector Concentration (HHI)"),
        imgPara("18_sector_hhi.png", 460),
        caption("Figure 12. Herfindahl-Hirschman Index by fund — higher values indicate more sector-concentrated equity portfolios."),

        h3("8.5 Fund Recommendation Engine"),
        p("A simple rule-based recommender (scripts/recommender.py) maps investor risk appetite (Low / Moderate / High) to the matching SEBI risk grade(s) and returns the top-N funds by Sharpe ratio. Example — 'Moderate' risk appetite: HDFC Top 100 Fund, Mirae Asset Large Cap Fund, and ICICI Pru Bluechip Fund (Direct) are the top 3 recommendations, all with Sharpe ≈ 1.0+ and 3yr returns ≈ 14–15%."),

        h1("9. Interactive Dashboard"),
        p("The dashboard is delivered as a standalone, self-contained HTML file (dashboard/bluestock_mf_dashboard.html) — an interactive, browser-based equivalent to a Power BI Desktop report, chosen because Power BI Desktop is a licensed Windows application not available in this build environment. It reproduces the same design goals as the original spec: 5 pages (exceeding the 4-page requirement), live slicers, sortable tables, tooltips, and a branded KPI ticker."),
        h3("9.1 Page 1 — Industry Overview"),
        bullet("KPI ticker: Total AUM (Rs. 81L Cr), SIP Inflow (Rs. 31,002 Cr), Folios (26.12 Cr), Active Schemes (1,908), Active SIP Accounts (9.35 Cr)."),
        bullet("Industry AUM trend line, AUM-by-fund-house grouped bar (by year), folio count growth line."),
        h3("9.2 Page 2 — Fund Performance"),
        bullet("Return-vs-risk bubble scatter (bubble size = AUM), sortable Fund Scorecard table, and a fund-selector NAV-vs-benchmark comparison chart."),
        bullet("Slicers: Fund House, Category, Plan."),
        h3("9.3 Page 3 — Investor Analytics"),
        bullet("Transaction amount by state, SIP/Lumpsum/Redemption split, T30 vs B30 pie, average SIP by age group, monthly transaction volume."),
        bullet("Slicers: State, Age Group, City Tier."),
        h3("9.4 Page 4 — SIP & Market Trends"),
        bullet("Dual-axis SIP inflow (bar) + Nifty 50 (line), category-inflow heatmap, top-5 categories by FY25 net inflow."),
        h3("9.5 Page 5 — Portfolio & Risk (bonus page)"),
        bullet("Sector allocation donut and portfolio concentration (HHI) bar chart, extending the dashboard beyond the original 4-page spec."),
        p("All charts are wired directly to the cleaned datasets (embedded as JSON at build time) so filtering is instantaneous and requires no server or database connection to view."),

        h1("10. Deliverables Summary"),
        simpleTable(
          ["#", "Deliverable", "Format", "Location"],
          [
            ["D1", "ETL Pipeline Scripts", ".py", "scripts/"],
            ["D2", "SQLite Database", ".db", "data/db/bluestock_mf.db"],
            ["D3", "EDA Charts & Findings", ".png + .md", "reports/charts/, reports/EDA_Findings.md"],
            ["D4", "Performance Metrics", ".py + .csv", "scripts/performance_analytics.py, reports/*.csv"],
            ["D5", "Interactive Dashboard", ".html", "dashboard/bluestock_mf_dashboard.html"],
            ["D6", "Advanced Analytics", ".py + .csv", "scripts/advanced_analytics.py, reports/*.csv"],
            ["D7", "Final Report + Slides", ".docx + .pptx", "reports/"],
          ],
          [700, 3200, 2200, 2900]
        ),

        h1("11. Limitations & Future Work"),
        bullet("NAV history and investor transactions are simulated (anchored to real published AMFI figures) rather than pulled live from AMFI/mfapi.in APIs, per the project's offline dataset design."),
        bullet("Independently re-computed 3yr CAGR and Sharpe differ from the pre-supplied scheme_performance.csv by a modest average margin, due to 'trailing from latest NAV date' vs. a fixed as-of-date methodology — both are directionally consistent and the discrepancy is documented in reports/computed_metrics.csv for transparency."),
        bullet("The dashboard is delivered as an interactive HTML/JS application rather than a native .pbix file, since Power BI Desktop requires a licensed Windows environment not available in this build; the same data model (CSV/SQLite) can be pointed at Power BI Desktop directly if required."),
        bullet("SIP-continuity 'at-risk' flagging uses a simple fixed 35-day-gap threshold; a production system would tune this per investor cohort and fund category."),
        bullet("Future work: live AMFI/mfapi.in API integration, a scheduled daily refresh job, Monte Carlo NAV projection, and a Markowitz efficient-frontier portfolio optimiser (see Appendix bonus challenges)."),

        h1("12. Conclusion"),
        p("This project delivers a complete, auditable path from raw AMFI-style CSVs to a governed SQLite database to a fully interactive analytics dashboard — covering all 8 project objectives (ETL, SQL schema, EDA, performance metrics, dashboard, investor-behaviour analysis, benchmark comparison, and documentation) set out in the original brief. The resulting Fund Scorecard, VaR/CVaR risk report, and investor-cohort analysis give Bluestock Fintech a reusable analytical foundation for retail fund-selection tooling."),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  const outPath = path.join(BASE, "reports", "Bluestock_MF_Final_Report.docx");
  fs.writeFileSync(outPath, buffer);
  console.log("Report written to", outPath);
});
