"""Unit tests for src/etl/normaliser.py — mirrors the spec's test reference table."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from etl.normaliser import normalize_year, normalize_ticker, normalize_company_name, parse_analysis_text


def test_year_mar23():
    assert normalize_year("Mar-23") == "2023-03"


def test_year_mar_space_23():
    assert normalize_year("Mar 23") == "2023-03"


def test_year_march_full():
    assert normalize_year("March-2023") == "2023-03"


def test_year_int_2023():
    assert normalize_year("2023") == "2023-03"


def test_year_fy23():
    assert normalize_year("FY23") == "2023-03"


def test_year_fy2024():
    assert normalize_year("FY2024") == "2024-03"


def test_year_dec22():
    assert normalize_year("Dec-22") == "2022-12"


def test_year_jun23():
    assert normalize_year("Jun-23") == "2023-06"


def test_year_already_normalised():
    assert normalize_year("2023-03") == "2023-03"


def test_year_garbage():
    assert normalize_year("xyz") == "PARSE_ERROR"


def test_year_none():
    assert normalize_year(None) == "PARSE_ERROR"


def test_ticker_strip():
    assert normalize_ticker("  TCS  ") == "TCS"


def test_ticker_lower():
    assert normalize_ticker("tcs") == "TCS"


def test_ticker_hyphen_preserved():
    assert normalize_ticker("bajaj-auto") == "BAJAJ-AUTO"


def test_ticker_ampersand_preserved():
    assert normalize_ticker("m&m") == "M&M"


def test_ticker_missing():
    assert normalize_ticker(None) == ""
    assert normalize_ticker("") == ""


def test_company_name_strips_newlines():
    assert normalize_company_name("Tata Consultancy\nServices Ltd") == "Tata Consultancy Services Ltd"


def test_parse_analysis_text_normal():
    assert parse_analysis_text("10 Years: 21%") == (10, 21.0)


def test_parse_analysis_text_decimal():
    assert parse_analysis_text("5 Years: 6.5%") == (5, 6.5)


def test_parse_analysis_text_unparseable():
    assert parse_analysis_text("N/A") == (None, None)


def test_parse_analysis_text_none():
    assert parse_analysis_text(None) == (None, None)


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
