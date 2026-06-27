-- =====================================================================
-- REPORT 5: Attrition Rate by Job Role vs. Company Benchmark
-- =====================================================================
-- CLIENT REQUIREMENT:
-- "Leadership doesn't just want attrition by role -- they want to
-- immediately see which roles are ABOVE or BELOW the company-wide
-- average, without having to mentally compare two separate numbers."
--
-- WHY THIS QUERY:
-- Demonstrates a second window function pattern: an aggregate window
-- function with NO PARTITION BY, which computes one company-wide
-- value (the overall attrition rate) and repeats it on every row so
-- it can be compared directly against each role's own rate in the
-- same SELECT -- something a plain GROUP BY alone cannot do, since
-- GROUP BY collapses rows and loses the ability to also show the
-- ungrouped, company-wide total side-by-side.
-- =====================================================================

WITH role_stats AS (
    SELECT
        e.job_role,
        COUNT(*) AS headcount,
        SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) AS left_count
    FROM employees e
    GROUP BY e.job_role
)
SELECT
    job_role,
    headcount,
    left_count,
    ROUND(100.0 * left_count / headcount, 1) AS role_attrition_rate_pct,
    ROUND(
        100.0 * SUM(left_count) OVER () / SUM(headcount) OVER (),
        1
    ) AS company_attrition_rate_pct,
    ROUND(
        (100.0 * left_count / headcount)
        - (100.0 * SUM(left_count) OVER () / SUM(headcount) OVER ()),
        1
    ) AS pct_points_vs_company
FROM role_stats
ORDER BY pct_points_vs_company DESC;
