-- Bluestock Fintech | Mutual Fund Analytics Platform
-- 10 Core Analytical SQL Queries

-- 1. Top 5 funds by AUM
SELECT scheme_name, fund_house, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month for a given fund (example: HDFC Top 100, amfi_code 125497)
SELECT strftime('%Y-%m', date) AS month, ROUND(AVG(nav), 2) AS avg_nav
FROM fact_nav
WHERE amfi_code = '125497'
GROUP BY month
ORDER BY month;

-- 3. SIP inflow YoY growth (industry level)
SELECT month, sip_inflow_crore, ROUND(yoy_growth_pct, 2) AS yoy_growth_pct
FROM fact_sip_industry
ORDER BY month;

-- 4. Transactions by state
SELECT state, COUNT(*) AS num_transactions, ROUND(SUM(amount_inr), 0) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense_ratio < 1%
SELECT scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct;

-- 6. Category-wise average Sharpe ratio
SELECT category, ROUND(AVG(sharpe_ratio), 3) AS avg_sharpe, COUNT(*) AS num_funds
FROM fact_performance
GROUP BY category
ORDER BY avg_sharpe DESC;

-- 7. Top 5 funds by 3-year CAGR within each risk grade
SELECT risk_grade, scheme_name, return_3yr_pct
FROM fact_performance p
WHERE return_3yr_pct >= (
    SELECT return_3yr_pct FROM fact_performance p2
    WHERE p2.risk_grade = p.risk_grade
    ORDER BY return_3yr_pct DESC
    LIMIT 1 OFFSET 2
)
ORDER BY risk_grade, return_3yr_pct DESC;

-- 8. Monthly transaction volume by type (SIP / Lumpsum / Redemption)
SELECT strftime('%Y-%m', transaction_date) AS month, transaction_type,
       COUNT(*) AS num_tx, ROUND(SUM(amount_inr), 0) AS total_amount
FROM fact_transactions
GROUP BY month, transaction_type
ORDER BY month, transaction_type;

-- 9. Top holding sectors by aggregate weight across all equity funds
SELECT sector, ROUND(AVG(weight_pct), 2) AS avg_weight_pct, COUNT(DISTINCT amfi_code) AS num_funds
FROM fact_portfolio
GROUP BY sector
ORDER BY avg_weight_pct DESC;

-- 10. AUM growth by fund house, latest quarter vs. first quarter on record
SELECT fund_house,
       MIN(aum_crore) AS aum_first_qtr,
       MAX(aum_crore) AS aum_latest_qtr,
       ROUND((MAX(aum_crore) - MIN(aum_crore)) * 100.0 / MIN(aum_crore), 1) AS pct_growth
FROM fact_aum
GROUP BY fund_house
ORDER BY pct_growth DESC;
