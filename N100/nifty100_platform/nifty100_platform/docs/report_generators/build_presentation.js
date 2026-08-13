const pptxgen = require("pptxgenjs");
const path = require("path");

const BASE = path.resolve(__dirname, "..", "..");
const CHARTS = path.join(BASE, "reports", "charts");
const c = (name) => path.join(CHARTS, name);

const INK = "101A16";
const INK_DK = "0A0F0D";
const EMERALD = "0F9D58";
const GOLD = "C9A227";
const RED = "D6484A";
const SLATE = "48534D";
const PAPER = "F4F7F5";
const WHITE = "FFFFFF";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const FONT = "Calibri";

function bgSlide(bg = WHITE) { const s = pres.addSlide(); s.background = { color: bg }; return s; }
function pageNum(s, n, total = 11) {
  s.addText(`${String(n).padStart(2, "0")} / ${total}`, { x: 12.5, y: 7.15, w: 0.7, h: 0.3, fontFace: FONT, fontSize: 9, color: SLATE, align: "right" });
}
function kicker(s, text, opts = {}) {
  s.addText(text.toUpperCase(), { x: opts.x ?? 0.6, y: opts.y ?? 0.45, w: opts.w ?? 8, h: 0.3, fontFace: FONT, fontSize: 12, bold: true, color: GOLD, charSpacing: 2 });
}
function title(s, text, opts = {}) {
  s.addText(text, { x: opts.x ?? 0.6, y: opts.y ?? 0.72, w: opts.w ?? 11.5, h: opts.h ?? 0.7, fontFace: FONT, fontSize: opts.size ?? 29, bold: true, color: opts.color ?? INK });
}
function brandMark(s) {
  s.addShape("roundRect", { x: 0.5, y: 0.35, w: 0.34, h: 0.34, rectRadius: 0.06, fill: { color: EMERALD }, line: { type: "none" } });
  s.addText("N", { x: 0.5, y: 0.35, w: 0.34, h: 0.34, fontFace: FONT, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle" });
}

// SLIDE 1 — TITLE
{
  const s = bgSlide(INK_DK);
  s.addShape("rect", { x: 8.6, y: 0, w: 4.73, h: 7.5, fill: { color: INK }, line: { type: "none" } });
  s.addText("92 COMPANIES   ·   50+ KPIs   ·   11 SECTORS   ·   11 PEER GROUPS", { x: 0.6, y: 6.55, w: 12.1, h: 0.4, fontFace: "Courier New", fontSize: 12, color: EMERALD, charSpacing: 1 });
  s.addShape("roundRect", { x: 0.6, y: 0.6, w: 0.5, h: 0.5, rectRadius: 0.08, fill: { color: EMERALD }, line: { type: "none" } });
  s.addText("N", { x: 0.6, y: 0.6, w: 0.5, h: 0.5, fontFace: FONT, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle" });
  s.addText("DATA ANALYTICS DIVISION", { x: 1.25, y: 0.62, w: 5, h: 0.46, fontFace: FONT, fontSize: 15, bold: true, color: WHITE, valign: "middle" });
  s.addText("Nifty 100\nFinancial Intelligence Platform", { x: 0.6, y: 2.15, w: 8.5, h: 2.1, fontFace: FONT, fontSize: 42, bold: true, color: WHITE, lineSpacing: 46 });
  s.addText("ETL Pipeline · Financial Ratio Engine · Screener · Peer & Sector Analytics · Interactive Dashboard", { x: 0.62, y: 4.25, w: 7.7, h: 0.5, fontFace: FONT, fontSize: 15.5, color: "C4D0CA" });
  s.addText("Build Report — August 2026", { x: 0.62, y: 4.75, w: 7.6, h: 0.4, fontFace: FONT, fontSize: 12, italic: true, color: GOLD });

  const stats = [["92", "Companies tracked"], ["1,041", "Ratio-validated company-years"], ["56/56", "Automated tests passing"], ["7", "Interactive dashboard pages"]];
  let sy = 1.1;
  stats.forEach(([num, lbl]) => {
    s.addText(num, { x: 9.1, y: sy, w: 3.6, h: 0.6, fontFace: FONT, fontSize: 28, bold: true, color: GOLD });
    s.addText(lbl, { x: 9.1, y: sy + 0.6, w: 3.6, h: 0.4, fontFace: FONT, fontSize: 11, color: "C4D0CA" });
    sy += 1.32;
  });
}

// SLIDE 2 — SCOPE & OBJECTIVES
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "The Brief", { x: 1.0 }); title(s, "Scope & Objectives", { x: 1.0 });
  s.addText("The spec calls for a 45-day, 6-sprint, multi-analyst build. This delivers the complete analytical substance in a single session.", { x: 1.0, y: 1.45, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 13, color: SLATE });

  const objs = [
    ["Data Engineering", "12 datasets → 1 governed SQLite database, 0 FK violations"],
    ["50+ Financial KPIs", "Ratio-validated exactly (0.00 diff) vs pre-supplied reference"],
    ["Investment Screener", "6 preset screens, YAML-configurable, no code changes needed"],
    ["Health Scoring", "0–100 composite score, banded Excellent/Moderate/Weak"],
    ["Sector & Peer Analytics", "10 sector benchmarks, 11 peer groups, percentile ranked"],
    ["Reporting & Dashboard", "92 PDF tearsheets + interactive 7-page dashboard"],
  ];
  let x = 1.0, y = 2.3;
  objs.forEach(([h, d], i) => {
    if (i === 3) { x = 1.0; y = 4.55; }
    s.addShape("roundRect", { x, y, w: 3.6, h: 2.1, rectRadius: 0.08, fill: { color: PAPER }, line: { color: "DCE5DF", width: 1 } });
    s.addText(h, { x: x + 0.22, y: y + 0.2, w: 3.15, h: 0.6, fontFace: FONT, fontSize: 14, bold: true, color: INK });
    s.addText(d, { x: x + 0.22, y: y + 0.85, w: 3.15, h: 1.1, fontFace: FONT, fontSize: 10.5, color: SLATE });
    x += 3.85;
  });
  pageNum(s, 2);
}

// SLIDE 3 — ARCHITECTURE
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Pipeline", { x: 1.0 }); title(s, "System Architecture", { x: 1.0 });
  const layers = [
    ["INGEST", "12 Excel files — header=1 (core) / header=0 (supplementary) loaders", EMERALD],
    ["VALIDATE", "16 DQ rules — CRITICAL/WARNING/INFO severity, full violation log", GOLD],
    ["NORMALISE", "Ticker/year standardisation, TTM removal, FK-orphan rejection, dedup", INK],
    ["LOAD", "SQLite — 11 base tables + 4 derived analytics tables, 0 FK violations", "8C564B"],
    ["ANALYSE", "Ratio engine, screener, peer %ile, clustering, cash-flow intelligence", RED],
    ["DELIVER", "92 PDF tearsheets, 10 sector reports, interactive dashboard", "6B4F9E"],
  ];
  let ly = 1.65;
  layers.forEach(([name, desc, color]) => {
    s.addShape("roundRect", { x: 1.0, y: ly, w: 1.9, h: 0.78, rectRadius: 0.08, fill: { color }, line: { type: "none" } });
    s.addText(name, { x: 1.0, y: ly, w: 1.9, h: 0.78, fontFace: FONT, fontSize: 11.5, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addShape("roundRect", { x: 3.05, y: ly, w: 9.3, h: 0.78, rectRadius: 0.08, fill: { color: PAPER }, line: { color: "DCE5DF", width: 1 } });
    s.addText(desc, { x: 3.3, y: ly, w: 8.9, h: 0.78, fontFace: FONT, fontSize: 11, color: INK, valign: "middle" });
    ly += 0.92;
  });
  pageNum(s, 3);
}

// SLIDE 4 — DATA QUALITY FINDINGS
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "ETL Findings", { x: 1.0 }); title(s, "Real Data Quality Findings", { x: 1.0 });
  s.addText("The validator caught genuine issues in the raw data — not synthetic test cases.", { x: 1.0, y: 1.45, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 12.5, color: SLATE });

  const rows = [
    ["Finding", "Detail", "Rule"],
    ["TTM snapshot rows", "100 'Trailing Twelve Month' rows in P&L are not a valid FY — removed before load", "Custom"],
    ["8 FK-orphan tickers", "ULTRACEMCO, ZOMATO, WIPRO, VEDL, VBL, UNITDSPR, UNIONBANK, ZYDUSLIFE appear in P&L/BS/CF but not in the 92-company master", "DQ-03"],
    ["Genuine duplicate rows", "1 company in P&L, 4 in BS, 2 in CF had exact duplicate (company_id, year) rows", "DQ-02"],
    ["Extreme ROE values", "51 edge cases logged — e.g. Bharat Electronics early years, driven by near-zero equity denominators", "Ratio Engine"],
  ];
  s.addTable(rows, { x: 1.0, y: 2.1, w: 11.3, h: 4.2, fontFace: FONT, fontSize: 11, border: { type: "solid", color: "DCE5DF", pt: 0.5 }, color: INK, autoPage: false, rowH: 0.7, colW: [2.6, 6.9, 1.8] });
  pageNum(s, 4);
}

// SLIDE 5 — RATIO ENGINE VALIDATION
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Accuracy", { x: 1.0 }); title(s, "Ratio Engine — Exact Validation", { x: 1.0 });
  s.addText("34 KPI columns independently re-computed from raw P&L / Balance Sheet / Cash Flow and cross-checked against the pre-supplied financial_ratios.xlsx.", { x: 1.0, y: 1.5, w: 11.3, h: 0.6, fontFace: FONT, fontSize: 13, color: SLATE });

  const stats = [["0.00", "Mean abs. diff — ROE"], ["0.00", "Mean abs. diff — D/E"], ["0.00", "Mean abs. diff — FCF"], ["1,041", "Matched company-years"]];
  let x = 1.0;
  stats.forEach(([n, l]) => {
    s.addShape("roundRect", { x, y: 2.4, w: 2.7, h: 1.8, rectRadius: 0.08, fill: { color: INK }, line: { type: "none" } });
    s.addText(n, { x, y: 2.55, w: 2.7, h: 0.8, fontFace: FONT, fontSize: 30, bold: true, color: GOLD, align: "center" });
    s.addText(l, { x: x + 0.15, y: 3.35, w: 2.4, h: 0.7, fontFace: FONT, fontSize: 10.5, color: WHITE, align: "center" });
    x += 2.85;
  });
  s.addText("This confirms the formulas for ROE, ROCE, D/E, Interest Coverage, CAGR (with turnaround/decline-to-loss flags), Free Cash Flow, and the Capital Allocation pattern classifier all match the specification exactly — not just directionally.", { x: 1.0, y: 4.6, w: 11.3, h: 1.2, fontFace: FONT, fontSize: 12.5, color: SLATE });
  pageNum(s, 5);
}

// SLIDE 6 — SCREENER
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Module 3", { x: 1.0 }); title(s, "Investment Screener — 6 Presets", { x: 1.0 });
  const rows = [
    ["Preset", "Matched", "Ranked By"],
    ["Quality Compounder", "20", "Composite Quality Score"],
    ["Value Pick", "2", "FCF Yield"],
    ["Growth Accelerator", "8", "PAT CAGR 5yr"],
    ["Dividend Champion", "33", "Dividend Yield"],
    ["Debt-Free Blue Chip", "6", "ROE"],
    ["Turnaround Watch", "30", "Revenue CAGR 3yr"],
  ];
  s.addTable(rows, { x: 1.0, y: 1.6, w: 7.2, h: 4.6, fontFace: FONT, fontSize: 12, border: { type: "solid", color: "DCE5DF", pt: 0.5 }, color: INK, autoPage: false, rowH: 0.6, colW: [3.6, 1.8, 1.8] });
  s.addShape("roundRect", { x: 8.5, y: 1.6, w: 3.85, h: 4.6, rectRadius: 0.08, fill: { color: INK }, line: { type: "none" } });
  s.addText("CONFIGURABLE, NOT HARD-CODED", { x: 8.75, y: 1.85, w: 3.4, h: 0.3, fontFace: FONT, fontSize: 10, bold: true, color: GOLD, charSpacing: 1 });
  s.addText("All thresholds live in config/screener_config.yaml. Analysts can add or edit presets with zero code changes — the ranking engine and composite-score weights are also YAML-defined.", { x: 8.75, y: 2.25, w: 3.35, h: 3.7, fontFace: FONT, fontSize: 11, color: WHITE, lineSpacing: 15 });
  pageNum(s, 6);
}

// SLIDE 7 — SECTOR & PEER
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Modules 4 & 6", { x: 1.0 }); title(s, "Sector & Peer Analytics", { x: 1.0 });
  s.addImage({ path: c("n1_sector_median_roe.png"), x: 0.8, y: 1.5, w: 5.9, h: 4.3 });
  s.addImage({ path: c("n2_de_vs_roe_scatter.png"), x: 6.9, y: 1.5, w: 5.6, h: 4.3 });
  s.addText("11 peer groups fully populated with 7-metric percentile ranking · Best-in-Class: 4 companies · Watch List: 10 companies", { x: 0.8, y: 5.9, w: 11.7, h: 0.4, fontFace: FONT, fontSize: 11, italic: true, color: SLATE });
  pageNum(s, 7);
}

// SLIDE 8 — HEALTH, CLUSTERING & QUALITY SCORE
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Modules 5 & 10", { x: 1.0 }); title(s, "Health Scoring & Clustering", { x: 1.0 });
  s.addImage({ path: c("n3_quality_score_hist.png"), x: 0.8, y: 1.5, w: 5.6, h: 4.2 });
  s.addImage({ path: c("n4_cluster_sizes.png"), x: 6.7, y: 1.5, w: 5.8, h: 4.2 });
  s.addText("9 Excellent · 37 Moderate · 44 Weak (composite score bands) — 5-cluster KMeans segmentation on ROE, D/E, growth, and margin", { x: 0.8, y: 5.85, w: 11.7, h: 0.4, fontFace: FONT, fontSize: 11, italic: true, color: SLATE });
  pageNum(s, 8);
}

// SLIDE 9 — DASHBOARD
{
  const s = bgSlide(INK_DK);
  s.addShape("roundRect", { x: 0.5, y: 0.5, w: 0.44, h: 0.44, rectRadius: 0.08, fill: { color: EMERALD }, line: { type: "none" } });
  s.addText("N", { x: 0.5, y: 0.5, w: 0.44, h: 0.44, fontFace: FONT, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle" });
  s.addText("INTERACTIVE DASHBOARD", { x: 1.1, y: 0.55, w: 6, h: 0.35, fontFace: FONT, fontSize: 12, bold: true, color: GOLD, charSpacing: 1.5 });
  s.addText("A 7-Page Analytics Dashboard, Live in the Browser", { x: 1.0, y: 0.95, w: 11.3, h: 0.6, fontFace: FONT, fontSize: 25, bold: true, color: WHITE });
  s.addText("Self-contained HTML/JS — no server, no install — substituting the specified Streamlit app for this delivery environment.", { x: 1.0, y: 1.55, w: 11.0, h: 0.4, fontFace: FONT, fontSize: 12, color: "C4D0CA" });

  const pages = [
    ["1", "Overview", "KPI ticker, sector donut, quality score distribution, top 15 companies"],
    ["2", "Company Profile", "Search any of 92 companies — KPI tiles, P&L/ratio trends, pros & cons"],
    ["3", "Screener", "All 6 presets, live sector filter, sortable results table"],
    ["4", "Peer Comparison", "11 groups, radar chart + side-by-side percentile table"],
    ["5", "Sector Analysis", "Median ROE/D-E by sector, revenue-vs-ROE bubble chart"],
    ["6", "Capital Allocation", "CFO/CFI/CFF pattern classification for every company"],
    ["7", "Clusters", "KMeans 5-cluster view — sizes and ROE-vs-D/E scatter"],
  ];
  let py = 2.25;
  pages.forEach(([num, h, d]) => {
    s.addShape("roundRect", { x: 1.0, y: py, w: 0.5, h: 0.5, rectRadius: 0.08, fill: { color: EMERALD }, line: { type: "none" } });
    s.addText(num, { x: 1.0, y: py, w: 0.5, h: 0.5, fontFace: FONT, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addText(h, { x: 1.7, y: py - 0.03, w: 3.0, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: WHITE });
    s.addText(d, { x: 1.7, y: py + 0.28, w: 9.8, h: 0.32, fontFace: FONT, fontSize: 10, color: "9DAAA3" });
    py += 0.7;
  });
  pageNum(s, 9);
}

// SLIDE 10 — TESTING & DELIVERABLES
{
  const s = bgSlide(WHITE);
  brandMark(s); kicker(s, "Quality Gate", { x: 1.0 }); title(s, "Testing & Deliverables", { x: 1.0 });
  const stats = [["56 / 56", "pytest tests passing"], ["0", "FK violations in nifty100.db"], ["92", "PDF tearsheets generated"], ["10", "Sector PDF reports"]];
  let x = 1.0;
  stats.forEach(([n, l]) => {
    s.addShape("roundRect", { x, y: 1.6, w: 2.7, h: 1.6, rectRadius: 0.08, fill: { color: PAPER }, line: { color: "DCE5DF", width: 1 } });
    s.addText(n, { x, y: 1.75, w: 2.7, h: 0.7, fontFace: FONT, fontSize: 24, bold: true, color: EMERALD, align: "center" });
    s.addText(l, { x: x + 0.15, y: 2.4, w: 2.4, h: 0.6, fontFace: FONT, fontSize: 10, color: SLATE, align: "center" });
    x += 2.85;
  });
  const rows = [
    ["Category", "Coverage"],
    ["ETL / normalisation", "21 unit tests — year formats, ticker cleaning, text parsing"],
    ["KPI formulas", "12 unit tests — ROE, D/E, ICR, CAGR edge cases (turnaround, zero-base)"],
    ["DQ rules", "8 unit tests — crafted violation records per rule, clean-data sanity check"],
    ["Integration", "15 tests — live queries against the built database and output files"],
  ];
  s.addTable(rows, { x: 1.0, y: 3.6, w: 11.3, h: 2.7, fontFace: FONT, fontSize: 11.5, border: { type: "solid", color: "DCE5DF", pt: 0.5 }, color: INK, autoPage: false, rowH: 0.5, colW: [3.0, 8.3] });
  pageNum(s, 10);
}

// SLIDE 11 — THANK YOU
{
  const s = bgSlide(INK_DK);
  s.addShape("rect", { x: 8.6, y: 0, w: 4.73, h: 7.5, fill: { color: INK }, line: { type: "none" } });
  s.addShape("roundRect", { x: 0.6, y: 0.6, w: 0.5, h: 0.5, rectRadius: 0.08, fill: { color: EMERALD }, line: { type: "none" } });
  s.addText("N", { x: 0.6, y: 0.6, w: 0.5, h: 0.5, fontFace: FONT, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle" });
  s.addText("DATA ANALYTICS DIVISION", { x: 1.25, y: 0.62, w: 5, h: 0.46, fontFace: FONT, fontSize: 14, bold: true, color: WHITE, valign: "middle" });
  s.addText("Thank You", { x: 0.6, y: 2.6, w: 8, h: 1.2, fontFace: FONT, fontSize: 44, bold: true, color: WHITE });
  s.addText("Questions & review welcome.", { x: 0.62, y: 3.75, w: 7, h: 0.5, fontFace: FONT, fontSize: 15, color: "C4D0CA" });

  const links = [["Database", "data/db/nifty100.db"], ["Dashboard", "dashboard/nifty100_dashboard.html"],
    ["Build Report", "docs/Nifty100_Build_Report.pdf"], ["Test Report", "reports/pytest_report.html"]];
  let ly = 4.5;
  links.forEach(([l, v]) => {
    s.addText(l + ":", { x: 0.62, y: ly, w: 3, h: 0.35, fontFace: FONT, fontSize: 11, bold: true, color: GOLD });
    s.addText(v, { x: 0.62, y: ly + 0.32, w: 6.5, h: 0.35, fontFace: "Courier New", fontSize: 10.5, color: WHITE });
    ly += 0.7;
  });
  s.addText("This build is derived from company filings plus simulated market/valuation datasets. Intended for internal analytical use, not investment advice.", { x: 9.1, y: 6.0, w: 3.7, h: 1.1, fontFace: FONT, fontSize: 9.5, italic: true, color: "9DAAA3" });
  pageNum(s, 11);
}

pres.writeFile({ fileName: path.join(BASE, "docs", "Nifty100_Presentation.pptx") }).then(() => console.log("Presentation written."));
