-- =====================================================================
-- REPORT 7: Job Satisfaction Level vs. Attrition Rate
-- =====================================================================
-- CLIENT REQUIREMENT:
-- "HR Business Partners want to see, on a simple 1-4 satisfaction
-- scale, exactly how much attrition risk increases as satisfaction
-- drops -- to make the case for funding an employee-engagement
-- survey follow-up program targeted at the lowest-scoring group."
--
-- WHY THIS QUERY:
-- Brings together THREE tables in one query (employees, compensation,
-- performance) -- the most "client-realistic" query in the set, since
-- real HR questions rarely stay inside one data source. Also reuses
-- the CASE/lookup pattern to label the 1-4 numeric scale with
-- human-readable text, since a client-facing report should never
-- show a raw "2" without context.
-- =====================================================================

SELECT
    p.job_satisfaction AS satisfaction_score,
    CASE p.job_satisfaction
        WHEN 1 THEN 'Low'
        WHEN 2 THEN 'Medium'
        WHEN 3 THEN 'High'
        WHEN 4 THEN 'Very High'
    END AS satisfaction_label,
    COUNT(*) AS headcount,
    SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(
        100.0 * SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS attrition_rate_pct,
    ROUND(AVG(c.monthly_income), 0) AS avg_monthly_income
FROM employees e
JOIN performance p   ON e.employee_id = p.employee_id
JOIN compensation c  ON e.employee_id = c.employee_id
GROUP BY p.job_satisfaction
ORDER BY p.job_satisfaction;
