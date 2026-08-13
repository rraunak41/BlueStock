-- Nifty 100 Financial Intelligence Platform — Exploratory SQL Queries (Sprint 1 equivalent)

-- 1. Row counts per table
SELECT 'companies' AS tbl, COUNT(*) AS rows FROM companies
UNION ALL SELECT 'profitandloss', COUNT(*) FROM profitandloss
UNION ALL SELECT 'balancesheet', COUNT(*) FROM balancesheet
UNION ALL SELECT 'cashflow', COUNT(*) FROM cashflow
UNION ALL SELECT 'documents', COUNT(*) FROM documents
UNION ALL SELECT 'sectors', COUNT(*) FROM sectors
UNION ALL SELECT 'stock_prices', COUNT(*) FROM stock_prices
UNION ALL SELECT 'market_cap', COUNT(*) FROM market_cap
UNION ALL SELECT 'financial_ratios_src', COUNT(*) FROM financial_ratios_src
UNION ALL SELECT 'peer_groups', COUNT(*) FROM peer_groups;

-- 2. Years of P&L history per company (coverage check)
SELECT company_id, COUNT(*) AS years_of_history
FROM profitandloss
GROUP BY company_id
ORDER BY years_of_history ASC
LIMIT 15;

-- 3. Null counts in key P&L fields
SELECT
  SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END) AS null_sales,
  SUM(CASE WHEN net_profit IS NULL THEN 1 ELSE 0 END) AS null_net_profit,
  SUM(CASE WHEN eps IS NULL THEN 1 ELSE 0 END) AS null_eps
FROM profitandloss;

-- 4. Companies per broad sector
SELECT broad_sector, COUNT(*) AS num_companies
FROM sectors
GROUP BY broad_sector
ORDER BY num_companies DESC;

-- 5. Distinct year range per time-series table
SELECT 'profitandloss' AS tbl, MIN(year) AS min_year, MAX(year) AS max_year FROM profitandloss
UNION ALL SELECT 'balancesheet', MIN(year), MAX(year) FROM balancesheet
UNION ALL SELECT 'cashflow', MIN(year), MAX(year) FROM cashflow;

-- 6. Companies with fewer than 10 years of P&L history
SELECT company_id, COUNT(*) AS yrs
FROM profitandloss
GROUP BY company_id
HAVING yrs < 10
ORDER BY yrs;

-- 7. Debt-free companies (latest year)
SELECT company_id, year, debt_to_equity
FROM financial_ratios
WHERE debt_to_equity = 0
  AND year = (SELECT MAX(year) FROM financial_ratios r2 WHERE r2.company_id = financial_ratios.company_id);

-- 8. Top 10 companies by latest-year ROE
SELECT r.company_id, c.company_name, r.return_on_equity_pct
FROM financial_ratios r
JOIN companies c ON r.company_id = c.id
WHERE r.year = (SELECT MAX(year) FROM financial_ratios r2 WHERE r2.company_id = r.company_id)
ORDER BY r.return_on_equity_pct DESC
LIMIT 10;

-- 9. Peer group member counts
SELECT peer_group_name, COUNT(*) AS members
FROM peer_groups
GROUP BY peer_group_name
ORDER BY members DESC;

-- 10. Companies missing annual report documents
SELECT c.id, c.company_name, COUNT(d.Year) AS report_count
FROM companies c
LEFT JOIN documents d ON c.id = d.company_id
GROUP BY c.id
HAVING report_count = 0;
