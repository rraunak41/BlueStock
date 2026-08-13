# Bluestock MF Analytics — Data Dictionary

## dim_fund (40 rows)
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT (PK) | AMFI unique scheme code |
| fund_house | TEXT | AMC name |
| scheme_name | TEXT | Full official AMFI scheme name |
| category | TEXT | Equity / Debt |
| sub_category | TEXT | Large Cap / Mid Cap / Small Cap / Liquid / etc. |
| plan | TEXT | Regular or Direct |
| launch_date | DATE | Fund launch date |
| benchmark | TEXT | Official benchmark index |
| expense_ratio_pct | REAL | Annual expense ratio (%) |
| exit_load_pct | REAL | Exit load (%) |
| min_sip_amount | REAL | Minimum SIP investment (INR) |
| min_lumpsum_amount | REAL | Minimum lumpsum investment (INR) |
| fund_manager | TEXT | Primary fund manager |
| risk_category | TEXT | SEBI risk category |
| sebi_category_code | TEXT | Internal SEBI code |

## dim_date (1,608 rows)
Standard date dimension: date_id, date, year, month, month_name, quarter, is_weekday.

## fact_nav (46,000 rows)
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT (FK) | Fund reference |
| date | DATE | NAV date (business day, holiday-filled) |
| nav | REAL | Net Asset Value (INR) |
| daily_return_pct | REAL | Day-over-day % change in NAV |

## fact_transactions (32,778 rows)
Investor-level SIP / Lumpsum / Redemption transactions with demographics
(investor_id, transaction_date, amfi_code, transaction_type, amount_inr, state,
city, city_tier, age_group, gender, annual_income_lakh, payment_mode, kyc_status).

## fact_performance (40 rows)
Pre-computed and derived performance/risk metrics per scheme: 1/3/5yr returns,
benchmark 3yr return, alpha, beta, Sharpe, Sortino, annualised std dev, max
drawdown, AUM, expense ratio, Morningstar rating, risk grade.

## fact_portfolio (322 rows)
Top equity holdings per fund: stock_symbol, stock_name, sector, weight_pct,
market_value_cr, current_price_inr, portfolio_date.

## fact_aum (90 rows)
Quarterly AUM by fund house: date, fund_house, aum_lakh_crore, aum_crore, num_schemes.

## fact_sip_industry (48 rows)
Monthly industry SIP metrics: month, sip_inflow_crore, active_sip_accounts_crore,
new_sip_accounts_lakh, sip_aum_lakh_crore, yoy_growth_pct (recomputed where AMFI
data had blanks in first 12 months).

## fact_category_inflows (144 rows)
Monthly net inflow by fund category (Large Cap, Mid Cap, Small Cap, ELSS, Liquid, etc.).

## fact_folio_count (21 rows)
Industry folio counts (in crore) split by Equity / Debt / Hybrid / Others.

## fact_benchmark (8,050 rows)
Daily closing values for NIFTY50, NIFTY100, NIFTY Midcap 150, BSE SmallCap,
CRISIL Liquid & Gilt indices.

## Data Quality Notes
- NAV history reindexed to full business-day calendar; missing (holiday) values forward-filled.
- 0 invalid (≤0 or null) NAV rows found.
- 0 negative Sharpe ratios; 0 out-of-range expense ratios (0.1%–2.5%) found.
- 0 transactions with non-positive amounts.
- All AMFI codes in nav_history, scheme_performance, investor_transactions, and
  portfolio_holdings validated against fund_master — 100% match, no orphan codes.
