"""Integration tests — validate the built nifty100.db and analytics outputs."""
import sys
from pathlib import Path
import sqlite3
import pandas as pd
import pytest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))
DB_PATH = BASE / "data" / "db" / "nifty100.db"

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="nifty100.db not built yet — run src/etl/run_etl.py first")


@pytest.fixture(scope="module")
def conn():
    c = sqlite3.connect(DB_PATH)
    yield c
    c.close()


def test_companies_table_has_92_or_fewer(conn):
    n = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    assert 0 < n <= 92


def test_no_duplicate_company_ids(conn):
    n_total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    n_distinct = conn.execute("SELECT COUNT(DISTINCT id) FROM companies").fetchone()[0]
    assert n_total == n_distinct


def test_fk_integrity_zero_violations(conn):
    conn.execute("PRAGMA foreign_keys = ON;")
    issues = conn.execute("PRAGMA foreign_key_check;").fetchall()
    assert len(issues) == 0


def test_financial_ratios_table_populated(conn):
    n = conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    assert n >= 1000


def test_financial_ratios_has_no_duplicate_company_year(conn):
    df = pd.read_sql("SELECT company_id, year FROM financial_ratios", conn)
    assert not df.duplicated().any()


def test_peer_percentiles_covers_11_groups(conn):
    n = conn.execute("SELECT COUNT(DISTINCT peer_group_name) FROM peer_percentiles").fetchone()[0]
    assert n == 11


def test_quality_score_bounded_0_100(conn):
    df = pd.read_sql("SELECT composite_quality_score FROM quality_score", conn)
    assert df["composite_quality_score"].between(0, 100).all()


def test_health_scores_all_have_band(conn):
    df = pd.read_sql("SELECT health_band FROM health_scores", conn)
    assert df["health_band"].notna().all()


def test_debt_to_equity_non_negative(conn):
    df = pd.read_sql("SELECT debt_to_equity FROM financial_ratios WHERE debt_to_equity IS NOT NULL", conn)
    assert (df["debt_to_equity"] >= 0).all()


def test_screener_output_file_exists():
    assert (BASE / "reports" / "screener_output.xlsx").exists()


def test_peer_comparison_file_exists():
    assert (BASE / "reports" / "peer_comparison.xlsx").exists()


def test_cashflow_intelligence_file_exists():
    assert (BASE / "reports" / "cashflow_intelligence.xlsx").exists()


def test_pros_cons_covers_all_companies():
    df = pd.read_csv(BASE / "reports" / "pros_cons_generated.csv")
    coverage = df.groupby("company_id")["type"].apply(lambda x: set(x))
    full = coverage.apply(lambda s: "pro" in s and "con" in s)
    assert full.all()


def test_cluster_labels_no_nulls():
    df = pd.read_csv(BASE / "reports" / "cluster_labels.csv")
    assert df["cluster_id"].notna().all()


def test_load_audit_zero_rejections_for_companies():
    df = pd.read_csv(BASE / "reports" / "load_audit.csv")
    companies_row = df[df.table == "companies"].iloc[0]
    assert companies_row["rejected"] == 0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
