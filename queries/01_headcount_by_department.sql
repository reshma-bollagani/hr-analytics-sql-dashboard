-- =====================================================================
-- REPORT 1: Headcount & Attrition by Department
-- =====================================================================
-- CLIENT REQUIREMENT:
-- "The VP of HR wants a single view of current headcount per
-- department alongside how many people left, so leadership can see
-- at a glance whether attrition is concentrated in one part of the
-- business before the quarterly board review."
--
-- WHY THIS QUERY:
-- This is the most common first-ask in any HR analytics engagement:
-- a baseline headcount report. It demonstrates GROUP BY, conditional
-- aggregation with CASE inside SUM(), and basic JOIN -- the building
-- blocks every later report builds on.
-- =====================================================================

SELECT
    e.department,
    COUNT(*)                                            AS total_headcount,
    SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(
        100.0 * SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        1
    )                                                    AS attrition_rate_pct
FROM employees e
GROUP BY e.department
ORDER BY attrition_rate_pct DESC;
