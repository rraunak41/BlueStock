"""
Nifty 100 Financial Intelligence Platform
Module 8: Automated PDF Report Generator — Company Tearsheet (2-page)

Generates a 2-page tearsheet PDF per company: KPI tiles, revenue/profit
trend, ROE/ROCE trend, balance sheet composition, cash flow, pros/cons.

Run with no args to generate tearsheets for a representative sample
(top 10 by Composite Quality Score) — pass --all for all 90 companies.
"""
import sys
import argparse
from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                 Spacer, Image, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "src"))
DB_PATH = BASE / "data" / "db" / "nifty100.db"
OUT_DIR = BASE / "reports" / "tearsheets"
CHART_DIR = BASE / "reports" / "charts" / "_tearsheet_tmp"
OUT_DIR.mkdir(exist_ok=True, parents=True)
CHART_DIR.mkdir(exist_ok=True, parents=True)

NAVY = colors.HexColor("#101A16")
EMERALD = colors.HexColor("#0F9D58")
GOLD = colors.HexColor("#C9A227")
LIGHT = colors.HexColor("#F4F7F5")

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TS_Title", parent=styles["Heading1"], fontSize=20, textColor=NAVY, spaceAfter=2)
sub_style = ParagraphStyle("TS_Sub", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#48534D"))
h2_style = ParagraphStyle("TS_H2", parent=styles["Heading2"], fontSize=13, textColor=EMERALD, spaceBefore=10, spaceAfter=4)
body_style = ParagraphStyle("TS_Body", parent=styles["Normal"], fontSize=9, leading=13)


def make_charts(cid, pl, ratios, bs):
    pl_c = pl[pl.company_id == cid].sort_values("year").tail(10)
    fig, ax = plt.subplots(figsize=(5.2, 2.4))
    ax.bar(pl_c["year"], pl_c["sales"], color="#0F9D58", label="Sales")
    ax2 = ax.twinx()
    ax2.plot(pl_c["year"], pl_c["net_profit"], color="#C9A227", marker="o", markersize=3, label="Net Profit")
    ax.set_xticklabels(pl_c["year"], rotation=45, ha="right", fontsize=6)
    ax.set_title("Revenue & Net Profit (₹ Cr)", fontsize=9)
    fig.tight_layout()
    p1 = CHART_DIR / f"{cid}_pl.png"
    fig.savefig(p1, dpi=140); plt.close(fig)

    r_c = ratios[ratios.company_id == cid].sort_values("year").tail(10)
    fig, ax = plt.subplots(figsize=(5.2, 2.4))
    ax.plot(r_c["year"], r_c["return_on_equity_pct"], color="#0F9D58", marker="o", markersize=3, label="ROE")
    ax.plot(r_c["year"], r_c["return_on_capital_pct"], color="#C9A227", marker="s", markersize=3, label="ROCE")
    ax.set_xticklabels(r_c["year"], rotation=45, ha="right", fontsize=6)
    ax.set_title("ROE / ROCE Trend (%)", fontsize=9)
    ax.legend(fontsize=7)
    fig.tight_layout()
    p2 = CHART_DIR / f"{cid}_ratios.png"
    fig.savefig(p2, dpi=140); plt.close(fig)

    bs_c = bs[bs.company_id == cid].sort_values("year").tail(1)
    if len(bs_c):
        row = bs_c.iloc[0]
        labels = ["Equity+Reserves", "Borrowings", "Other Liab."]
        vals = [row["equity_capital"] + row["reserves"], row["borrowings"], row["other_liabilities"]]
        fig, ax = plt.subplots(figsize=(5.2, 2.4))
        ax.bar(labels, vals, color=["#0F9D58", "#D6484A", "#8A968F"])
        ax.set_title("Balance Sheet Composition — Latest Year (₹ Cr)", fontsize=9)
        plt.xticks(fontsize=7)
        fig.tight_layout()
        p3 = CHART_DIR / f"{cid}_bs.png"
        fig.savefig(p3, dpi=140); plt.close(fig)
    else:
        p3 = None

    return p1, p2, p3


def build_tearsheet(cid, companies, ratios_latest, cagr, health, cf_intel, pros_cons, pl, ratios, bs):
    co = companies[companies.company_id == cid]
    if co.empty:
        return None
    co = co.iloc[0]
    r = ratios_latest[ratios_latest.company_id == cid]
    r = r.iloc[0] if len(r) else {}
    cg = cagr[cagr.company_id == cid]
    cg = cg.iloc[0] if len(cg) else {}
    hs = health[health.company_id == cid]
    hs = hs.iloc[0] if len(hs) else {}
    cf = cf_intel[cf_intel.company_id == cid]
    cf = cf.iloc[0] if len(cf) else {}

    out_path = OUT_DIR / f"{cid}_tearsheet.pdf"
    doc = SimpleDocTemplate(str(out_path), pagesize=A4,
                             topMargin=1.4 * cm, bottomMargin=1.4 * cm,
                             leftMargin=1.6 * cm, rightMargin=1.6 * cm)
    story = []

    story.append(Paragraph(f"{co.get('company_name', cid)}", title_style))
    story.append(Paragraph(f"{cid} &nbsp;·&nbsp; {co.get('broad_sector','-')} / {co.get('sub_sector','-')} &nbsp;·&nbsp; Nifty 100 Financial Intelligence Platform", sub_style))
    story.append(Spacer(1, 8))

    def g(x, default="-", pct=False, fmt="{:.1f}"):
        try:
            v = x if not hasattr(x, "get") else x
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return default
            return fmt.format(v) + ("%" if pct else "")
        except Exception:
            return default

    kpi_data = [
        ["ROE", g(r.get("return_on_equity_pct") if hasattr(r, "get") else None, pct=True),
         "ROCE", g(r.get("return_on_capital_pct") if hasattr(r, "get") else None, pct=True)],
        ["D/E", g(r.get("debt_to_equity") if hasattr(r, "get") else None, fmt="{:.2f}"),
         "NPM", g(r.get("net_profit_margin_pct") if hasattr(r, "get") else None, pct=True)],
        ["Rev CAGR 5Y", g(cg.get("revenue_cagr_5yr_pct") if hasattr(cg, "get") else None, pct=True),
         "PAT CAGR 5Y", g(cg.get("pat_cagr_5yr_pct") if hasattr(cg, "get") else None, pct=True)],
        ["Quality Score", g(hs.get("composite_quality_score") if hasattr(hs, "get") else None, fmt="{:.0f}"),
         "Health Band", g(hs.get("health_band") if hasattr(hs, "get") else None, fmt="{}")],
    ]
    t = Table(kpi_data, colWidths=[3.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY), ("TEXTCOLOR", (2, 0), (2, -1), NAVY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    p1, p2, p3 = make_charts(cid, pl, ratios, bs)
    img_row = [Image(str(p1), width=8.2 * cm, height=3.7 * cm), Image(str(p2), width=8.2 * cm, height=3.7 * cm)]
    story.append(Table([img_row], colWidths=[8.5 * cm, 8.5 * cm]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("About", h2_style))
    about = str(co.get("about_company", ""))[:400]
    story.append(Paragraph(about if about and about != "nan" else "No description available.", body_style))

    story.append(Paragraph("Capital Allocation", h2_style))
    ca = str(cf.get("cfo_quality_label", "-")) if hasattr(cf, "get") else "-"
    capex_tier = str(cf.get("capex_tier", "-")) if hasattr(cf, "get") else "-"
    story.append(Paragraph(f"CFO Quality: <b>{ca}</b> &nbsp;·&nbsp; CapEx Intensity: <b>{capex_tier}</b>", body_style))

    story.append(PageBreak())
    story.append(Paragraph(f"{co.get('company_name', cid)} — Financial Detail", title_style))
    story.append(Spacer(1, 6))
    if p3:
        story.append(Image(str(p3), width=12 * cm, height=5.5 * cm))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Pros", h2_style))
    pros = pros_cons[(pros_cons.company_id == cid) & (pros_cons.type == "pro")]["text"].head(5).tolist()
    for p in pros:
        story.append(Paragraph(f"• {p}", body_style))

    story.append(Paragraph("Cons", h2_style))
    cons = pros_cons[(pros_cons.company_id == cid) & (pros_cons.type == "con")]["text"].head(5).tolist()
    for c in cons:
        story.append(Paragraph(f"• {c}", body_style))

    doc.build(story)
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Generate for all companies (default: top 10 sample)")
    parser.add_argument("--n", type=int, default=10)
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    companies_raw = pd.read_sql("SELECT id AS company_id, company_name, about_company FROM companies", conn)
    sectors = pd.read_sql("SELECT company_id, broad_sector, sub_sector FROM sectors", conn)
    companies = companies_raw.merge(sectors, on="company_id", how="left")

    ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
    ratios_latest = ratios.sort_values("year").groupby("company_id").tail(1)
    cagr = pd.read_sql("SELECT * FROM growth_cagr", conn)
    health = pd.read_sql("SELECT * FROM health_scores", conn)
    cf_intel = pd.read_excel(BASE / "reports" / "cashflow_intelligence.xlsx")
    pros_cons = pd.read_csv(BASE / "reports" / "pros_cons_generated.csv")
    pl = pd.read_sql("SELECT * FROM profitandloss", conn)
    bs = pd.read_sql("SELECT * FROM balancesheet", conn)

    if args.all:
        targets = companies["company_id"].tolist()
    else:
        top = health.sort_values("composite_quality_score", ascending=False).head(args.n)
        targets = top["company_id"].tolist()

    print(f"Generating {len(targets)} tearsheets...")
    generated = []
    for cid in targets:
        path = build_tearsheet(cid, companies, ratios_latest, cagr, health, cf_intel, pros_cons, pl, ratios, bs)
        if path:
            generated.append(path)
            print(f"  {path.name}")

    print(f"\n{len(generated)} tearsheets written -> reports/tearsheets/")
    conn.close()
