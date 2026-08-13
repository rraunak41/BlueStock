const pptxgen = require("pptxgenjs");
const path = require("path");

const BASE = path.resolve(__dirname, "..", "..");
const CHARTS = path.join(BASE, "reports", "charts");
const c = (name) => path.join(CHARTS, name);

const NAVY = "0A2540";
const NAVY_DK = "050F1E";
const AMBER = "D4A017";
const TEAL = "0E9F8E";
const RED = "D6484A";
const SLATE = "4B5A70";
const PAPER = "F3F6FA";
const WHITE = "FFFFFF";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5

const FONT = "Calibri";

function bgSlide(bg = WHITE) {
  const s = pres.addSlide();
  s.background = { color: bg };
  return s;
}

function pageNum(s, n) {
  s.addText(String(n).padStart(2, "0") + " / 12", {
    x: 12.5, y: 7.15, w: 0.7, h: 0.3, fontFace: FONT, fontSize: 9, color: SLATE, align: "right",
  });
}

function kicker(s, text, opts = {}) {
  s.addText(text.toUpperCase(), {
    x: opts.x ?? 0.6, y: opts.y ?? 0.45, w: opts.w ?? 8, h: 0.3,
    fontFace: FONT, fontSize: 12, bold: true, color: AMBER, charSpacing: 2,
  });
}

function title(s, text, opts = {}) {
  s.addText(text, {
    x: opts.x ?? 0.6, y: opts.y ?? 0.72, w: opts.w ?? 11.5, h: opts.h ?? 0.7,
    fontFace: FONT, fontSize: opts.size ?? 30, bold: true, color: opts.color ?? NAVY,
  });
}

function brandMark(s, dark = false) {
  s.addShape("roundRect", { x: 0.5, y: 0.35, w: 0.34, h: 0.34, rectRadius: 0.06, fill: { color: AMBER }, line: { type: "none" } });
  s.addText("B", { x: 0.5, y: 0.35, w: 0.34, h: 0.34, fontFace: FONT, fontSize: 15, bold: true, color: NAVY_DK, align: "center", valign: "middle" });
}

// ============================================================
// SLIDE 1 — TITLE
// ============================================================
{
  const s = bgSlide(NAVY_DK);
  // subtle gradient-like layered rects
  s.addShape("rect", { x: 0, y: 0, w: 13.33, h: 7.5, fill: { color: NAVY_DK }, line: { type: "none" } });
  s.addShape("rect", { x: 8.6, y: 0, w: 4.73, h: 7.5, fill: { color: NAVY }, line: { type: "none" } });
  // ticker-style decorative numbers
  s.addText("₹81L Cr AUM   ·   26.12 Cr FOLIOS   ·   ₹31,002 Cr SIP INFLOW (DEC 2025)", {
    x: 0.6, y: 6.55, w: 12.1, h: 0.4, fontFace: "Courier New", fontSize: 12, color: TEAL, charSpacing: 1,
  });
  s.addShape("roundRect", { x: 0.6, y: 0.6, w: 0.5, h: 0.5, rectRadius: 0.08, fill: { color: AMBER }, line: { type: "none" } });
  s.addText("B", { x: 0.6, y: 0.6, w: 0.5, h: 0.5, fontFace: FONT, fontSize: 22, bold: true, color: NAVY_DK, align: "center", valign: "middle" });
  s.addText("BLUESTOCK FINTECH", { x: 1.25, y: 0.62, w: 5, h: 0.46, fontFace: FONT, fontSize: 16, bold: true, color: WHITE, valign: "middle" });

  s.addText("Mutual Fund\nAnalytics Platform", {
    x: 0.6, y: 2.3, w: 8.5, h: 2.1, fontFace: FONT, fontSize: 48, bold: true, color: WHITE, lineSpacing: 52,
  });
  s.addText("End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard", {
    x: 0.62, y: 4.35, w: 7.6, h: 0.5, fontFace: FONT, fontSize: 17, color: "C7D2E0",
  });
  s.addText("Capstone Project  ·  Mutual Fund / Fintech Domain  ·  August 2026", {
    x: 0.62, y: 4.9, w: 7.6, h: 0.4, fontFace: FONT, fontSize: 12, italic: true, color: AMBER,
  });

  // right-side stat stack
  const stats = [
    ["40", "Real fund schemes tracked"],
    ["46K+", "Daily NAV records, 2022–2026"],
    ["32.7K", "Investor transactions analysed"],
    ["18", "EDA & analytics charts"],
  ];
  let sy = 1.1;
  stats.forEach(([num, lbl]) => {
    s.addText(num, { x: 9.1, y: sy, w: 3.6, h: 0.6, fontFace: FONT, fontSize: 30, bold: true, color: AMBER });
    s.addText(lbl, { x: 9.1, y: sy + 0.62, w: 3.6, h: 0.4, fontFace: FONT, fontSize: 11.5, color: "C7D2E0" });
    sy += 1.35;
  });
}

// ============================================================
// SLIDE 2 — PROBLEM & OBJECTIVE
// ============================================================
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "The Brief", { x: 1.0 }); title(s, "Problem & Objective", { x: 1.0 });
  s.addText("India's mutual fund industry manages ₹81L Cr across 1,908 schemes — but data is fragmented and retail investors can't easily compare risk-adjusted performance.", {
    x: 1.0, y: 1.5, w: 11.6, h: 0.6, fontFace: FONT, fontSize: 14, color: SLATE,
  });

  const problems = [
    ["01", "Data Fragmentation", "NAV, AUM, SIP & holdings data live in different AMFI formats — no unified database."],
    ["02", "Performance Comparison Gap", "Investors can't compare funds on Sharpe, Alpha, Beta without heavy manual work."],
    ["03", "No Benchmark Tracking", "Most investors don't know if their fund beats its benchmark index."],
    ["04", "Investor Behaviour Blind Spot", "AMCs lack visibility into demographic & geographic SIP patterns."],
  ];
  let x = 1.0;
  problems.forEach(([num, h, d]) => {
    s.addShape("roundRect", { x, y: 2.35, w: 2.78, h: 2.85, rectRadius: 0.08, fill: { color: PAPER }, line: { color: "E1E7EF", width: 1 } });
    s.addText(num, { x: x + 0.2, y: 2.55, w: 1.5, h: 0.5, fontFace: FONT, fontSize: 22, bold: true, color: AMBER });
    s.addText(h, { x: x + 0.2, y: 3.05, w: 2.4, h: 0.7, fontFace: FONT, fontSize: 13.5, bold: true, color: NAVY });
    s.addText(d, { x: x + 0.2, y: 3.75, w: 2.4, h: 1.3, fontFace: FONT, fontSize: 10.5, color: SLATE });
    x += 2.95;
  });

  s.addShape("roundRect", { x: 1.0, y: 5.55, w: 11.33, h: 1.35, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("OBJECTIVE", { x: 1.3, y: 5.72, w: 3, h: 0.3, fontFace: FONT, fontSize: 11, bold: true, color: AMBER, charSpacing: 1.5 });
  s.addText("Build a governed ETL pipeline + SQL database + risk-adjusted performance engine + interactive dashboard covering all 40 tracked schemes, end to end.", {
    x: 1.3, y: 6.0, w: 10.7, h: 0.8, fontFace: FONT, fontSize: 13.5, color: WHITE,
  });
  pageNum(s, 2);
}

// ============================================================
// SLIDE 3 — DATA SOURCES
// ============================================================
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Foundations", { x: 1.0 }); title(s, "Data Sources & Datasets", { x: 1.0 });

  const rows = [
    ["Dataset", "Rows", "Description"],
    ["01 Fund Master", "40", "AMFI code, AMC, category, expense ratio, risk grade"],
    ["02 NAV History", "46,000", "Daily NAV, Jan 2022–May 2026, anchored to real mfapi.in values"],
    ["03 AUM by Fund House", "90", "Quarterly AUM, 2022–2025"],
    ["04 Monthly SIP Inflows", "48", "Industry SIP inflow, active accounts, registrations"],
    ["05 Category Inflows", "144", "Net inflow by category, FY 2024-25"],
    ["06 Industry Folio Count", "21", "Folio counts by Equity / Debt / Hybrid"],
    ["07 Scheme Performance", "40", "Returns, Sharpe, Sortino, Alpha, Beta, Max DD"],
    ["08 Investor Transactions", "32,778", "SIP / Lumpsum / Redemption, 5,000 investors"],
    ["09 Portfolio Holdings", "322", "Top equity holdings, sector weights"],
    ["10 Benchmark Indices", "8,050", "Nifty 50/100/Midcap150, BSE SmallCap, CRISIL"],
  ];
  s.addTable(rows, {
    x: 1.0, y: 1.55, w: 8.0, h: 5.2,
    fontFace: FONT, fontSize: 10.5,
    border: { type: "solid", color: "E1E7EF", pt: 0.5 },
    fill: { color: WHITE },
    color: NAVY,
    autoPage: false,
    rowH: 0.44,
    colW: [2.7, 1.1, 4.2],
  });
  // style header row
  s.tables && null;

  s.addShape("roundRect", { x: 9.25, y: 1.55, w: 3.1, h: 5.2, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("REAL DATA ANCHORS", { x: 9.5, y: 1.8, w: 2.6, h: 0.3, fontFace: FONT, fontSize: 10.5, bold: true, color: AMBER, charSpacing: 1 });
  const anchors = [
    "SBI MF AUM: ₹12.50L Cr (largest AMC)",
    "Industry AUM: ₹81L Cr, Dec 2025",
    "SIP Inflow: ₹31,002 Cr, Dec 2025 (ATH)",
    "Active SIP Accounts: 9.35 Cr",
    "Total MF Folios: 26.12 Cr",
    "HDFC Top 100 NAV anchor from mfapi.in code 125497",
  ];
  let ay = 2.25;
  anchors.forEach(a => {
    s.addText("•  " + a, { x: 9.5, y: ay, w: 2.7, h: 0.55, fontFace: FONT, fontSize: 10, color: WHITE, lineSpacing: 13 });
    ay += 0.72;
  });
  pageNum(s, 3);
}

// ============================================================
// SLIDE 4 — ARCHITECTURE
// ============================================================
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Pipeline", { x: 1.0 }); title(s, "System Architecture & ETL Pipeline", { x: 1.0 });
  s.addText("Extract → Transform → Load → Analyse → Visualise — the same pattern used by real fintech platforms (Zerodha, Groww).", {
    x: 1.0, y: 1.45, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 12.5, color: SLATE,
  });

  const layers = [
    ["EXTRACT", "10 pre-packaged CSVs mirroring AMFI NAVAll.txt, Historical NAV API, mfapi.in REST, Monthly Notes", TEAL],
    ["TRANSFORM", "Pandas cleaning — date parsing, holiday forward-fill, dedup, AMFI-code validation, derived returns", AMBER],
    ["LOAD", "SQLite star schema — 11 tables, indexed on amfi_code + date", NAVY],
    ["ANALYSE", "Sharpe, Sortino, Alpha/Beta (OLS), Max DD, VaR/CVaR, rolling Sharpe, HHI, cohorts", "8C564B"],
    ["VISUALISE", "5-page interactive HTML dashboard — live slicers, sortable tables, drill-down", RED],
  ];
  let ly = 2.15;
  layers.forEach(([name, desc, color]) => {
    s.addShape("roundRect", { x: 1.0, y: ly, w: 2.0, h: 0.82, rectRadius: 0.08, fill: { color }, line: { type: "none" } });
    s.addText(name, { x: 1.0, y: ly, w: 2.0, h: 0.82, fontFace: FONT, fontSize: 12, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addShape("roundRect", { x: 3.2, y: ly, w: 9.15, h: 0.82, rectRadius: 0.08, fill: { color: PAPER }, line: { color: "E1E7EF", width: 1 } });
    s.addText(desc, { x: 3.45, y: ly, w: 8.7, h: 0.82, fontFace: FONT, fontSize: 11.5, color: NAVY, valign: "middle" });
    ly += 0.98;
  });
  pageNum(s, 4);
}

// ============================================================
// SLIDE 5 — EDA HIGHLIGHTS I
// ============================================================
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Exploratory Data Analysis", { x: 1.0 }); title(s, "EDA Highlights — Market & Industry Trends", { x: 1.0 });
  s.addImage({ path: c("03_sip_inflow_trend.png"), x: 0.9, y: 1.55, w: 5.7, h: 2.57 });
  s.addImage({ path: c("02_aum_growth_by_amc.png"), x: 6.8, y: 1.55, w: 5.7, h: 2.85 });
  s.addImage({ path: c("07_folio_count_growth.png"), x: 0.9, y: 4.35, w: 5.7, h: 2.55 });
  s.addImage({ path: c("04_category_inflow_heatmap.png"), x: 6.8, y: 4.6, w: 5.7, h: 2.6 });
  pageNum(s, 5);
}

// ============================================================
// SLIDE 6 — EDA HIGHLIGHTS II
// ============================================================
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Exploratory Data Analysis", { x: 1.0 }); title(s, "EDA Highlights — Risk & Investor Behaviour", { x: 1.0 });
  s.addImage({ path: c("11_risk_return_scatter.png"), x: 0.9, y: 1.55, w: 5.7, h: 4.1 });
  s.addImage({ path: c("08_correlation_matrix.png"), x: 6.8, y: 1.55, w: 5.0, h: 4.4 });
  s.addText("18 charts produced (exceeds the 15+ target) — full set in reports/charts/", {
    x: 0.9, y: 6.85, w: 11.0, h: 0.35, fontFace: FONT, fontSize: 10.5, italic: true, color: SLATE,
  });
  pageNum(s, 6);
}

// ============================================================
// SLIDE 7 — PERFORMANCE METRICS I
// ============================================================
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Fund Performance Analytics", { x: 1.0 }); title(s, "Fund Scorecard — Composite Ranking", { x: 1.0 });
  s.addText("Score = 30%×(3yr return) + 25%×(Sharpe) + 20%×(Alpha) + 15%×(low expense) + 10%×(low max-drawdown), all percentile-ranked", {
    x: 1.0, y: 1.45, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 11.5, color: SLATE,
  });

  const rows = [
    ["Scheme", "3Y Return", "Sharpe", "Alpha", "Score"],
    ["Kotak Flexicap Fund - Regular", "15.65%", "0.98", "1.85", "71.8"],
    ["SBI Small Cap Fund - Regular", "23.39%", "0.94", "1.23", "70.6"],
    ["ICICI Pru Liquid Fund - Regular", "7.68%", "7.68", "0.42", "70.5"],
    ["HDFC Short Term Debt - Regular", "7.37%", "6.03", "0.31", "70.3"],
    ["Kotak Emerging Equity - Regular", "18.23%", "0.96", "1.68", "68.3"],
    ["SBI Small Cap Fund - Direct", "23.87%", "0.98", "1.47", "68.0"],
    ["Mirae Asset Large Cap - Regular", "14.81%", "1.06", "1.15", "66.7"],
  ];
  s.addTable(rows, {
    x: 1.0, y: 2.0, w: 8.3, h: 4.6,
    fontFace: FONT, fontSize: 11.5,
    border: { type: "solid", color: "E1E7EF", pt: 0.5 },
    color: NAVY, autoPage: false, rowH: 0.55,
    colW: [3.7, 1.4, 1.1, 1.1, 1.0],
  });

  s.addShape("roundRect", { x: 9.55, y: 2.0, w: 2.8, h: 4.6, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("TOP INSIGHT", { x: 9.8, y: 2.25, w: 2.3, h: 0.3, fontFace: FONT, fontSize: 10.5, bold: true, color: AMBER, charSpacing: 1 });
  s.addText("Liquid & short-duration debt funds post surprisingly high Sharpe ratios (6+) due to very low volatility — but modest absolute returns.\n\nEquity flexi-cap & small-cap funds top the composite score by balancing strong 3yr returns with reasonable risk-adjusted metrics.", {
    x: 9.8, y: 2.65, w: 2.3, h: 3.7, fontFace: FONT, fontSize: 11, color: WHITE, lineSpacing: 16,
  });
  pageNum(s, 7);
}

// ============================================================
// SLIDE 8 — PERFORMANCE METRICS II
// ============================================================
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Fund Performance Analytics", { x: 1.0 }); title(s, "Benchmark Comparison — Top 5 vs Nifty", { x: 1.0 });
  s.addImage({ path: c("16_benchmark_comparison_top5.png"), x: 1.3, y: 1.5, w: 10.7, h: 5.4 });
  s.addText("All 5 top-scorecard funds substantially outperform Nifty 50 / Nifty 100 over the tracked period.", {
    x: 1.3, y: 6.95, w: 10.7, h: 0.35, fontFace: FONT, fontSize: 11, italic: true, color: SLATE,
  });
  pageNum(s, 8);
}

// ============================================================
// SLIDE 9 — DASHBOARD I
// ============================================================
{
  const s = bgSlide(NAVY_DK);
  s.addShape("roundRect", { x: 0.5, y: 0.5, w: 0.44, h: 0.44, rectRadius: 0.08, fill: { color: AMBER }, line: { type: "none" } });
  s.addText("B", { x: 0.5, y: 0.5, w: 0.44, h: 0.44, fontFace: FONT, fontSize: 18, bold: true, color: NAVY_DK, align: "center", valign: "middle" });
  s.addText("INTERACTIVE DASHBOARD", { x: 1.1, y: 0.55, w: 6, h: 0.35, fontFace: FONT, fontSize: 12, bold: true, color: AMBER, charSpacing: 1.5 });
  s.addText("A 5-Page Web Dashboard, Live in the Browser", { x: 1.0, y: 0.95, w: 11.3, h: 0.6, fontFace: FONT, fontSize: 27, bold: true, color: WHITE });
  s.addText("Delivered as a self-contained HTML/JS app — no server, no license required to view — with the same design goals as a Power BI report.", {
    x: 1.0, y: 1.55, w: 11.0, h: 0.4, fontFace: FONT, fontSize: 12.5, color: "C7D2E0",
  });

  const pages = [
    ["1", "Industry Overview", "KPI ticker, industry AUM trend, AUM by fund house, folio growth"],
    ["2", "Fund Performance", "Risk-return bubble scatter, sortable scorecard, NAV vs benchmark"],
    ["3", "Investor Analytics", "Transactions by state, SIP/Lumpsum/Redemption split, demographics"],
    ["4", "SIP & Market Trends", "SIP inflow vs Nifty 50, category inflow heatmap, top categories"],
    ["5", "Portfolio & Risk", "Sector allocation, concentration (HHI) — bonus page beyond spec"],
  ];
  let py = 2.35;
  pages.forEach(([num, h, d]) => {
    s.addShape("roundRect", { x: 1.0, y: py, w: 0.55, h: 0.55, rectRadius: 0.08, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(num, { x: 1.0, y: py, w: 0.55, h: 0.55, fontFace: FONT, fontSize: 18, bold: true, color: NAVY_DK, align: "center", valign: "middle" });
    s.addText(h, { x: 1.75, y: py - 0.02, w: 3.4, h: 0.4, fontFace: FONT, fontSize: 14, bold: true, color: WHITE });
    s.addText(d, { x: 1.75, y: py + 0.32, w: 9.5, h: 0.35, fontFace: FONT, fontSize: 10.5, color: "9FB0C6" });
    py += 0.85;
  });
  pageNum(s, 9);
}

// ============================================================
// SLIDE 10 — DASHBOARD II (visual charts as proxy for screenshots)
// ============================================================
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Dashboard Preview", { x: 1.0 }); title(s, "Sample Visuals Powering the Dashboard", { x: 1.0 });
  s.addImage({ path: c("09_sector_allocation_donut.png"), x: 0.8, y: 1.5, w: 4.0, h: 3.9 });
  s.addImage({ path: c("18_sector_hhi.png"), x: 4.95, y: 1.5, w: 3.9, h: 4.35 });
  s.addImage({ path: c("06a_geo_distribution_state.png"), x: 9.0, y: 1.5, w: 3.5, h: 4.3 });
  s.addText("Every chart in the live dashboard is filterable — the underlying data updates instantly on slicer changes (Fund House, Category, State, Age Group, etc.).", {
    x: 0.8, y: 6.0, w: 11.6, h: 0.6, fontFace: FONT, fontSize: 11.5, italic: true, color: SLATE,
  });
  pageNum(s, 10);
}

// ============================================================
// SLIDE 11 — KEY FINDINGS
// ============================================================
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Synthesis", { x: 1.0 }); title(s, "Key Findings", { x: 1.0 });

  const findings = [
    ["Market Alignment", "All 40 schemes track the real equity cycle — 2022 correction, 2023–24 rally.", TEAL],
    ["AMC Leadership", "SBI Mutual Fund is the largest AMC by AUM throughout the sample period.", NAVY],
    ["SIP Momentum", "Monthly SIP inflow trends upward, closing near the real ₹31,002 Cr all-time high.", AMBER],
    ["Investor Core", "Ages 26–45 drive the bulk of SIP volume with the widest amount variance.", RED],
    ["Diversification", "Cross-category fund correlation is low — useful for portfolio construction.", "8C564B"],
    ["Risk-Return Tradeoff", "Higher-return funds cluster at higher volatility, as textbook theory predicts.", "6B4F9E"],
  ];
  let fx = 1.0, fy = 1.6;
  findings.forEach(([h, d, color], i) => {
    if (i === 3) { fx = 1.0; fy = 4.2; }
    s.addShape("roundRect", { x: fx, y: fy, w: 3.6, h: 2.35, rectRadius: 0.08, fill: { color: PAPER }, line: { type: "none" } });
    s.addShape("roundRect", { x: fx + 0.25, y: fy + 0.25, w: 0.5, h: 0.5, rectRadius: 0.25, fill: { color }, line: { type: "none" } });
    s.addText(h, { x: fx + 0.25, y: fy + 0.9, w: 3.1, h: 0.6, fontFace: FONT, fontSize: 14, bold: true, color: NAVY });
    s.addText(d, { x: fx + 0.25, y: fy + 1.45, w: 3.1, h: 0.8, fontFace: FONT, fontSize: 10.5, color: SLATE });
    fx += 3.85;
  });
  pageNum(s, 11);
}

// ============================================================
// SLIDE 12 — THANK YOU
// ============================================================
{
  const s = bgSlide(NAVY_DK);
  s.addShape("rect", { x: 8.6, y: 0, w: 4.73, h: 7.5, fill: { color: NAVY }, line: { type: "none" } });
  s.addShape("roundRect", { x: 0.6, y: 0.6, w: 0.5, h: 0.5, rectRadius: 0.08, fill: { color: AMBER }, line: { type: "none" } });
  s.addText("B", { x: 0.6, y: 0.6, w: 0.5, h: 0.5, fontFace: FONT, fontSize: 22, bold: true, color: NAVY_DK, align: "center", valign: "middle" });
  s.addText("BLUESTOCK FINTECH", { x: 1.25, y: 0.62, w: 5, h: 0.46, fontFace: FONT, fontSize: 16, bold: true, color: WHITE, valign: "middle" });

  s.addText("Thank You", { x: 0.6, y: 2.6, w: 8, h: 1.2, fontFace: FONT, fontSize: 46, bold: true, color: WHITE });
  s.addText("Questions & discussion welcome.", { x: 0.62, y: 3.75, w: 7, h: 0.5, fontFace: FONT, fontSize: 16, color: "C7D2E0" });

  const links = [
    ["GitHub Repo", "bluestock_mf_capstone/"],
    ["Interactive Dashboard", "dashboard/bluestock_mf_dashboard.html"],
    ["Final Report (PDF/DOCX)", "reports/Bluestock_MF_Final_Report"],
    ["SQLite Database", "data/db/bluestock_mf.db"],
  ];
  let ly = 4.5;
  links.forEach(([l, v]) => {
    s.addText(l + ":", { x: 0.62, y: ly, w: 3, h: 0.35, fontFace: FONT, fontSize: 11.5, bold: true, color: AMBER });
    s.addText(v, { x: 0.62, y: ly + 0.32, w: 6.5, h: 0.35, fontFace: "Courier New", fontSize: 11, color: WHITE });
    ly += 0.72;
  });

  s.addText("All data sourced from publicly available AMFI India, NSE, BSE and open API (mfapi.in) information.\nFor educational purposes only — not investment advice.", {
    x: 9.1, y: 5.9, w: 3.7, h: 1.2, fontFace: FONT, fontSize: 10, italic: true, color: "9FB0C6",
  });
  pageNum(s, 12);
}

pres.writeFile({ fileName: path.join(BASE, "reports", "Bluestock_MF_Presentation.pptx") })
  .then(() => console.log("Presentation written."));
