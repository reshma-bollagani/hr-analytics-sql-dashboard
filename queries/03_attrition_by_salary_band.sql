-- =====================================================================
-- REPORT 3: Attrition Rate by Salary Band
-- =====================================================================
-- CLIENT REQUIREMENT:
-- "Compensation & Benefits wants to know if attrition is concentrated
-- in lower pay bands before they finalize next year's raise budget --
-- specifically, they want income grouped into bands (not exact
-- salary) since that's how the comp team thinks about pay tiers."
--
-- WHY THIS QUERY:
-- This is the textbook use case for CASE-based "lookup" logic in SQL:
-- there's no salary_band column in the source data, so we derive one
-- on the fly. This is exactly what a VLOOKUP/IFS formula does in
-- Excel, except it happens in the query layer.
-- Also requires a JOIN into compensation (separate table).
-- =====================================================================

SELECT
    CASE
        WHEN c.monthly_income < 3000  THEN '1. Under 3,000'
        WHEN c.monthly_income < 6000  THEN '2. 3,000 - 5,999'
        WHEN c.monthly_income < 10000 THEN '3. 6,000 - 9,999'
        WHEN c.monthly_income < 15000 THEN '4. 10,000 - 14,999'
        ELSE                               '5. 15,000+'
    END                                                  AS salary_band,
    COUNT(*)                                             AS headcount,
    SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(
        100.0 * SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        1
    )                                                    AS attrition_rate_pct
FROM employees e
JOIN compensation c ON e.employee_id = c.employee_id
GROUP BY salary_band
ORDER BY salary_band;
