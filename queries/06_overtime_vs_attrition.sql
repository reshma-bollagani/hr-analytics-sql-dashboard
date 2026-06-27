-- =====================================================================
-- REPORT 6: Does Overtime Drive Attrition?
-- =====================================================================
-- CLIENT REQUIREMENT:
-- "Before approving a budget for additional headcount to reduce
-- mandatory overtime, the COO wants evidence that overtime is
-- actually correlated with people leaving -- not just an assumption."
--
-- WHY THIS QUERY:
-- A simple but high-value pattern: segmenting one yes/no flag
-- (overtime) and showing the attrition rate on each side. This is
-- the kind of query that directly supports a budget decision, which
-- is the point -- a report only matters if it changes what someone
-- does next. Pulls from employees + compensation (overtime lives in
-- the compensation table), reinforcing the JOIN requirement.
-- =====================================================================

SELECT
    c.overtime,
    COUNT(*) AS headcount,
    SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(
        100.0 * SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS attrition_rate_pct,
    ROUND(AVG(c.monthly_income), 0) AS avg_monthly_income
FROM employees e
JOIN compensation c ON e.employee_id = c.employee_id
GROUP BY c.overtime
ORDER BY attrition_rate_pct DESC;
