"""
Nifty 100 Financial Intelligence Platform
Module 1: ETL — Normalisation utilities (ticker, year).
"""
import re
import pandas as pd


def normalize_ticker(raw) -> str:
    """Strip whitespace and upper-case an NSE ticker. Returns '' for missing/invalid."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    s = str(raw).strip().upper()
    return s


_MONTHS = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06",
    "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12",
    "JANUARY": "01", "FEBRUARY": "02", "MARCH": "03", "APRIL": "04", "JUNE": "06",
    "JULY": "07", "AUGUST": "08", "SEPTEMBER": "09", "OCTOBER": "10",
    "NOVEMBER": "11", "DECEMBER": "12",
}


def normalize_year(raw) -> str:
    """
    Standardise a financial-year label to 'YYYY-MM'.
    Handles: 'Mar-23', 'Mar 23', 'March-2023', 'FY23', 'FY2023', '2023',
    'Dec-22', 'Jun-23', already-normalised 'YYYY-MM'. Returns 'PARSE_ERROR'
    for unrecognised formats.
    """
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return "PARSE_ERROR"
    s = str(raw).strip()

    # Already normalised
    if re.match(r"^\d{4}-\d{2}$", s):
        return s

    # Pure integer year -> assume March FY close
    if re.match(r"^\d{4}$", s):
        return f"{s}-03"

    # FY23 / FY2023
    m = re.match(r"^FY\s*(\d{2,4})$", s, re.IGNORECASE)
    if m:
        yy = m.group(1)
        yyyy = f"20{yy}" if len(yy) == 2 else yy
        return f"{yyyy}-03"

    # Mon-YY / Mon YY / Month-YYYY  (e.g. Mar-23, Mar 23, March-2023, Dec-22)
    m = re.match(r"^([A-Za-z]+)[\s\-]+(\d{2,4})$", s)
    if m:
        mon_raw, yy = m.group(1).upper(), m.group(2)
        mon = _MONTHS.get(mon_raw)
        if mon:
            yyyy = f"20{yy}" if len(yy) == 2 else yy
            return f"{yyyy}-{mon}"

    return "PARSE_ERROR"


def normalize_company_name(raw) -> str:
    """Strip embedded newlines/whitespace from a company legal name."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    return re.sub(r"\s+", " ", str(raw)).strip()


def parse_analysis_text(raw):
    """
    Parse strings like '10 Years: 21%' from analysis.xlsx into (period_years, value_pct).
    Returns (None, None) if unparseable.
    """
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None, None
    m = re.match(r"(\d+)\s*Years?:?\s*([\d.]+)%", str(raw).strip())
    if not m:
        return None, None
    return int(m.group(1)), float(m.group(2))
