"""
Nifty 100 Financial Intelligence Platform
Module 8: Portfolio Summary PDF + Sector Reports
"""
import sys
from pathlib import Path
from datetime import date
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / "data" / "db" / "nifty100.db"
OUT_PORTFOLIO = BASE / "reports" / "portfolio"
OUT_SECTOR = BASE / "reports" / "sector"
OUT_PORTFOLIO.mkdir(exist_ok=True, parents=True)
OUT_SECTOR.mkdir(exist_ok=True, parents=True)

NAVY = colors.HexColor("#101A16")
EMERALD = colors.HexColor("#0F9D58")
LIGHT = colors.HexColor("#F4F7F5")

styles = getSampleStyleSheet()
title_style = ParagraphStyle("P_Title", parent=styles["Heading1"], fontSize=18, textColor=NAVY)
sub_style = ParagraphStyle("P_Sub", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#48534D"))


def trend_arrow(cagr):
    if pd.isna(cagr):
        return "→"
    return "↑" if cagr > 3 else ("↓" if cagr < -3 else "→")


def build_portfolio_summary(universe: pd.DataFrame):
    out_path = OUT_PORTFOLIO / f"portfolio_summary_{date.today().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(str(out_path), pagesize=landscape(A4),
                             topMargin=1.2 * cm, bottomMargin=1.2 * cm, leftMargin=1.2 * cm, rightMargin=1.2 * cm)
    story = [Paragraph("Nifty 100 Portfolio Summary", title_style),
             Paragraph(f"All {len(universe)} tracked companies · Generated {date.today().isoformat()}", sub_style),
             Spacer(1, 10)]

    header = ["Company", "Sector", "ROE %", "ROCE %", "D/E", "Rev CAGR 5Y", "Trend", "Quality Score"]
    rows = [header]
    for _, r in universe.sort_values("composite_quality_score", ascending=False).iterrows():
        rows.append([
            str(r.get("company_name", ""))[:32], str(r.get("broad_sector", ""))[:18],
            f"{r['return_on_equity_pct']:.1f}" if pd.notna(r.get("return_on_equity_pct")) else "-",
            f"{r['return_on_capital_pct']:.1f}" if pd.notna(r.get("return_on_capital_pct")) else "-",
            f"{r['debt_to_equity']:.2f}" if pd.notna(r.get("debt_to_equity")) else "-",
            f"{r['revenue_cagr_5yr_pct']:.1f}" if pd.notna(r.get("revenue_cagr_5yr_pct")) else "-",
            trend_arrow(r.get("revenue_cagr_5yr_pct")),
            f"{r['composite_quality_score']:.0f}" if pd.notna(r.get("composite_quality_score")) else "-",
        ])

    # Paginate ~30 rows per page
    chunk = 32
    for i in range(0, len(rows) - 1, chunk):
        page_rows = [header] + rows[1 + i: 1 + i + chunk]
        t = Table(page_rows, colWidths=[5.5 * cm, 3.8 * cm, 2 * cm, 2 * cm, 1.8 * cm, 2.5 * cm, 1.5 * cm, 2.5 * cm], repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DCE5DF")),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        story.append(PageBreak())

    doc.build(story[:-1])  # drop trailing page break
    return out_path


def build_sector_reports(universe: pd.DataFrame, sector_bench: pd.DataFrame):
    paths = []
    for sector, g in universe.groupby("broad_sector"):
        safe_name = str(sector).replace("/", "-").replace(" ", "_")
        out_path = OUT_SECTOR / f"{safe_name}_report_{date.today().strftime('%Y%m%d')}.pdf"
        doc = SimpleDocTemplate(str(out_path), pagesize=A4,
                                 topMargin=1.4 * cm, bottomMargin=1.4 * cm, leftMargin=1.6 * cm, rightMargin=1.6 * cm)
        story = [Paragraph(f"{sector} — Sector Report", title_style),
                 Paragraph(f"{len(g)} companies · Generated {date.today().isoformat()}", sub_style),
                 Spacer(1, 10)]

        bench_row = sector_bench[sector_bench.broad_sector == sector]
        if len(bench_row):
            b = bench_row.iloc[0]
            story.append(Paragraph(
                f"Sector Median — ROE {b['return_on_equity_pct']:.1f}% · ROCE {b['return_on_capital_pct']:.1f}% · "
                f"D/E {b['debt_to_equity']:.2f} · P/E {b['pe_ratio']:.1f}× · Rev CAGR 5Y {b['revenue_cagr_5yr_pct']:.1f}%",
                sub_style))
            story.append(Spacer(1, 10))

        header = ["Company", "ROE %", "ROCE %", "D/E", "Rev CAGR 5Y", "Quality Score"]
        rows = [header]
        gs = g.sort_values("composite_quality_score", ascending=False)
        for _, r in gs.iterrows():
            rows.append([
                str(r.get("company_name", ""))[:34],
                f"{r['return_on_equity_pct']:.1f}" if pd.notna(r.get("return_on_equity_pct")) else "-",
                f"{r['return_on_capital_pct']:.1f}" if pd.notna(r.get("return_on_capital_pct")) else "-",
                f"{r['debt_to_equity']:.2f}" if pd.notna(r.get("debt_to_equity")) else "-",
                f"{r['revenue_cagr_5yr_pct']:.1f}" if pd.notna(r.get("revenue_cagr_5yr_pct")) else "-",
                f"{r['composite_quality_score']:.0f}" if pd.notna(r.get("composite_quality_score")) else "-",
            ])
        t = Table(rows, colWidths=[6.5 * cm, 2.2 * cm, 2.2 * cm, 2 * cm, 2.8 * cm, 2.8 * cm], repeatRows=1)
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DCE5DF")),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
        if len(gs) >= 1:
            style.append(("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#D6F1E2")))  # best in sector
        t.setStyle(TableStyle(style))
        story.append(t)
        doc.build(story)
        paths.append(out_path)
    return paths


if __name__ == "__main__":
    sys.path.insert(0, str(BASE / "src"))
    from analytics.screener import build_screener_universe

    conn = sqlite3.connect(DB_PATH)
    universe = build_screener_universe(conn)
    sector_bench = pd.read_csv(BASE / "reports" / "sector_benchmarks.csv")

    print("Building portfolio summary PDF...")
    p = build_portfolio_summary(universe)
    print(f"  {p}")

    print("\nBuilding sector reports...")
    sector_paths = build_sector_reports(universe, sector_bench)
    for sp in sector_paths:
        print(f"  {sp.name}")
    print(f"\n{len(sector_paths)} sector reports written -> reports/sector/")
    conn.close()
