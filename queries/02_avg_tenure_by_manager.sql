-- =====================================================================
-- REPORT 2: Average Tenure by Manager
-- =====================================================================
-- CLIENT REQUIREMENT:
-- "People Ops suspects that certain managers have much higher
-- turnover on their teams than others, and wants average tenure
-- (years at company) broken out by manager so they can flag
-- low-tenure teams for a manager-effectiveness review."
--
-- WHY THIS QUERY:
-- Forces a JOIN from employees -> managers (a true dimension-table
-- JOIN, not just merging two halves of the same entity like
-- compensation/performance do). Also demonstrates HAVING, since the
-- client only cares about managers with enough direct reports for the
-- average to be statistically meaningful (filtering on an aggregate,
-- which is exactly what HAVING is for and WHERE cannot do).
-- =====================================================================

SELECT
    m.manager_name,
    e.department,
    COUNT(*)                          AS team_size,
    ROUND(AVG(e.years_at_company), 1) AS avg_tenure_years,
    SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) AS team_attrition_count
FROM employees e
JOIN managers m ON e.manager_id = m.manager_id
GROUP BY m.manager_id, m.manager_name, e.department
HAVING COUNT(*) >= 5          -- ignore managers with too few reports to be meaningful
ORDER BY avg_tenure_years ASC;
