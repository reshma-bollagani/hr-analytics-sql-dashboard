# HR Analytics SQL Reporting Dashboard

A SQL-based HR reporting project simulating a real analytics engagement:
a normalized relational database, seven client-driven SQL reports
(including JOINs, CASE/lookup logic, and window functions), and an
Excel dashboard with formula-driven pivot-style summaries and charts.

## Why this project

This project is built to demonstrate the core skills behind a
reporting/data analyst role: writing SQL across multiple related
tables, translating vague business asks into specific queries, and
delivering results in a format non-technical stakeholders actually
use (Excel, with pivot tables and charts).

## Dataset

This project uses the real **IBM HR Analytics Employee Attrition**
dataset from Kaggle (1,470 employees, 35 original columns).

**Two changes were made to the raw file, both documented and
intentional** (see `data/prepare_real_dataset.py`):

1. **6 columns dropped**: `EmployeeCount`, `Over18`, `StandardHours`
   (constant on every row — zero analytical value), and `DailyRate`,
   `HourlyRate`, `MonthlyRate` (these three pay fields don't derive
   from each other or from `MonthlyIncome` in any consistent way in
   this dataset, so keeping all four compensation fields would force
   every report to pick one arbitrarily. `MonthlyIncome` alone is kept
   since it scales sensibly with `JobLevel` and supports a clean story).

2. **2 columns added (synthetic)**: `ManagerID` and `ManagerName`.
   **This is the one part of the dataset that is not real** — the
   original Kaggle file has no manager field at all. Managers are
   assigned deterministically (fixed seed) within each department at a
   realistic span of control (~15-25 direct reports), purely so the
   project can demonstrate a genuine dimension-table JOIN
   (`employees` to `managers`), which the real data has no field to
   support otherwise. Every other column in this project -- all
   demographics, compensation, performance, tenure, and the
   attrition outcome itself -- is the real, unmodified Kaggle data.

The result, `data/raw/HR_Employee_Attrition.csv`, has 29 real columns
plus the 2 synthetic manager columns = 31 total.

## Database design

The flat CSV is deliberately normalized into 4 related tables instead
of being loaded as one giant table, to mirror how HR data really
lives across separate systems (HRIS, payroll, performance reviews)
and to create genuine multi-table JOIN scenarios:

```
managers (manager_id PK, manager_name, department)
employees (employee_id PK, age, department, job_role, manager_id FK, ...)
compensation (employee_id PK/FK, monthly_income, overtime, ...)
performance (employee_id PK/FK, job_satisfaction, performance_rating, ...)
```

See `db/mysql/schema_mysql.sql` for full DDL with column-level
comments, and `db/mysql/load_data_mysql.sql` for the data load.

## How to run it (MySQL / MariaDB via MySQL Workbench)

This project was built and fully verified against a real MySQL-compatible
server  -- every step below was run end-to-end, including
all 7 reports, with results confirmed row-for-row.

1. **File → Open SQL Script** → select `db/mysql/schema_mysql.sql` →
   click the lightning-bolt **Execute** button. This creates the
   `hr_analytics` database and all 4 tables.
2. **File → Open SQL Script** → select `db/mysql/load_data_mysql.sql` →
   **Execute**. This populates all 4 tables (82 managers, 1,470
   employees, 1,470 compensation rows, 1,470 performance rows).
3. Open any file in `queries/` the same way and execute it directly --
   no changes needed. **All 7 queries, including the window-function
   reports (`RANK() OVER (PARTITION BY ...)`, `SUM() OVER ()`), run
   completely unmodified.**

Verify the load succeeded with:
```sql
USE hr_analytics;
SELECT 'employees' AS table_name, COUNT(*) AS row_count FROM employees
UNION ALL SELECT 'managers', COUNT(*) FROM managers
UNION ALL SELECT 'compensation', COUNT(*) FROM compensation
UNION ALL SELECT 'performance', COUNT(*) FROM performance;
-- expect: employees 1470, managers 82, compensation 1470, performance 1470
```

The original, untouched Kaggle file is preserved at
`data/raw/emp_attrition_original_kaggle.csv` for reference/audit.

## The seven reports

Each query file in `queries/` opens with a "client requirement"
comment block -- the business reason a report like this would actually
get requested -- followed by a short technical rationale.

| # | File | SQL skill demonstrated | Business question answered |
|---|------|------------------------|------------------------------|
| 1 | `01_headcount_by_department.sql` | GROUP BY, conditional SUM | Where does headcount and attrition concentrate by department? |
| 2 | `02_avg_tenure_by_manager.sql` | JOIN, GROUP BY, HAVING | Which managers have unusually low average tenure on their teams? |
| 3 | `03_attrition_by_salary_band.sql` | CASE (lookup logic), JOIN | Does attrition concentrate in lower pay bands? |
| 4 | `04_rank_performance_within_dept.sql` | Window function: `RANK() OVER (PARTITION BY ...)` | How does each employee rank on performance within their own department? |
| 5 | `05_attrition_by_role_vs_benchmark.sql` | Window function: `SUM() OVER ()`, CTE | Which job roles run above/below the company-wide attrition rate? |
| 6 | `06_overtime_vs_attrition.sql` | JOIN, conditional aggregation | Is mandatory overtime actually correlated with attrition? |
| 7 | `07_satisfaction_vs_attrition.sql` | 3-table JOIN, CASE | How sharply does attrition rise as job satisfaction drops? |

### Key findings (real data)
- **Overtime employees: 30.5% attrition vs. 10.4%** for those without overtime -- the single
  strongest driver found in the dataset.
- **Lowest salary band (under 3,000/mo): 28.6% attrition vs. 3.8%** in the top band (15,000+/mo).
- **Sales Representative** is the highest-risk role at **39.8% attrition**, nearly 2.5x the
  company-wide rate of 16.1%.
- Attrition drops steadily as job satisfaction rises: **22.8% (Low) down to 11.3% (Very High)**.
- Research & Development has the lowest departmental attrition (13.8%) despite being the
  largest department; Sales has the highest (20.6%).
- The manager-level report flagged specific outlier teams -- e.g. one 23-person R&D team
  with an average tenure of just 3.9 years and 6 departures, a clear candidate for a
  manager-effectiveness review.

## Excel dashboard

`reports/HR_Attrition_Dashboard.xlsx` contains:
- **RawData** -- the flattened, joined dataset (this is the pivot-table source).
- **Dept_Summary**, **Salary_Summary**, **Satisfaction_Summary** -- formula-driven
  summary tables (`COUNTIFS`/`SUMIFS`/`AVERAGEIFS`, plus a nested-`IF` salary-band
  lookup as the Excel equivalent of the SQL `CASE` logic) and a chart, so everything
  recalculates live if RawData changes.
- **README_PivotInstructions** -- steps to add a native Excel PivotTable on top of
  RawData in under a minute, for anyone who wants a true pivot-table object rather
  than a formula table.

All formulas verified at zero errors via LibreOffice recalculation.

## Tech used
MySQL , Python (pandas, numpy -- used for the one-time data
cleaning step in `data/prepare_real_dataset.py`), SQL (JOINs, CASE,
window functions, CTEs), Excel (formulas, charts, pivot-table-ready
raw data).

## Honest disclosure
This project uses real Kaggle data with one synthetic addition
(manager assignment -- see "Dataset" above). If asked in an interview,
this is straightforward to explain: the real dataset doesn't include
organizational/manager structure, so it was added to demonstrate a
realistic manager-rollup report and JOIN pattern that HR systems
commonly require.
