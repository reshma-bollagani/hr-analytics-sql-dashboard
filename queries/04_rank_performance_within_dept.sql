-- =====================================================================
-- REPORT 4: Rank Employees by Performance Within Department
-- =====================================================================
-- CLIENT REQUIREMENT:
-- "For calibration season, the Talent team wants every employee
-- ranked against peers in their OWN department by performance rating
-- and job satisfaction -- not ranked company-wide, since comparing a
-- Sales rep to an R&D scientist on the same scale isn't meaningful."
--
-- WHY THIS QUERY:
-- This is the textbook use case for a window function. A naive
-- approach would need a self-join or a correlated subquery to rank
-- "within a group" -- both slower and harder to read. RANK() OVER
-- (PARTITION BY ... ORDER BY ...) does it in one pass:
--   PARTITION BY department  -> restart the ranking for each department
--   ORDER BY performance_rating DESC, job_satisfaction DESC -> the
--     ranking criteria, with satisfaction as a tiebreaker
-- RANK() (vs ROW_NUMBER()) intentionally allows tied ranks when two
-- employees have identical scores, which is the fairer choice for a
-- performance calibration use case.
-- =====================================================================

SELECT
    e.department,
    e.job_role,
    e.employee_id,
    p.performance_rating,
    p.job_satisfaction,
    RANK() OVER (
        PARTITION BY e.department
        ORDER BY p.performance_rating DESC, p.job_satisfaction DESC
    ) AS dept_performance_rank
FROM employees e
JOIN performance p ON e.employee_id = p.employee_id
ORDER BY e.department, dept_performance_rank;
