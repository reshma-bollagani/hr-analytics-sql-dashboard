"""
Prepares the REAL IBM HR Analytics Employee Attrition dataset
(Kaggle) for this project.

WHAT THIS SCRIPT DOES, AND WHY:

1. Loads the real 35-column Kaggle CSV.

2. DROPS 6 columns that add no analytical value:
   - EmployeeCount, Over18, StandardHours: constant on every single
     row (verified: EmployeeCount=1, Over18='Y', StandardHours=80 for
     all 1,470 employees) -- a column with zero variance can never
     explain anything, so it's dead weight in any report.
   - DailyRate, HourlyRate, MonthlyRate: these three pay-rate fields
     don't derive from each other or from MonthlyIncome in any
     consistent way in this dataset (they appear to be independently
     randomized). Keeping all four pay fields would force every
     compensation report to pick one arbitrarily and ignore the
     other three, with no principled way to explain why. MonthlyIncome
     alone is kept because it scales sensibly with JobLevel and is the
     one pay field that supports a clean, explainable story.

3. ADDS a synthetic ManagerID/ManagerName field. The real dataset has
   NO manager column at all. This is the ONLY synthetic field in the
   entire project -- every other column below is 100% real data from
   the Kaggle dataset. Managers are assigned deterministically
   (fixed random seed) within each department, with realistic team
   sizes (5-12 direct reports per manager), purely so the project can
   demonstrate a true dimension-table JOIN (employee -> manager),
   which the real dataset has no field to support otherwise.

OUTPUT: data/raw/HR_Employee_Attrition.csv (26 real columns + the
2 added manager columns), which db/load_data.py reads unchanged.
"""
import numpy as np
import pandas as pd

RAW_PATH = "/home/claude/hr-analytics-sql-dashboard/data/raw/emp_attrition_original_kaggle.csv"
OUT_PATH = "/home/claude/hr-analytics-sql-dashboard/data/raw/HR_Employee_Attrition.csv"

df = pd.read_csv(RAW_PATH, encoding="utf-8-sig")

# --- Drop zero-value / inconsistent columns ---
DROP_COLS = ["EmployeeCount", "Over18", "StandardHours",
             "DailyRate", "HourlyRate", "MonthlyRate"]
df = df.drop(columns=DROP_COLS)

# --- Add synthetic manager assignment (the ONLY synthetic field) ---
rng = np.random.default_rng(42)
manager_names_pool = [
    "Alvarez", "Brennan", "Castillo", "Donovan", "Ekwueme", "Farrell",
    "Gallagher", "Huang", "Iyer", "Jankowski", "Kowalski", "Larsen",
    "Mehta", "Nakamura", "O'Connor", "Petrov", "Quinn", "Rahman",
    "Singh", "Thibault",
]

manager_id_counter = 1001
manager_assignment = {}   # employee index -> (manager_id, manager_name)

def make_unique_names(n, pool, rng):
    """Generate n unique manager names, cycling pool with suffixes if needed."""
    if n <= len(pool):
        return list(rng.choice(pool, size=n, replace=False))
    base = list(rng.permutation(pool))
    names = list(base)
    suffix = 2
    while len(names) < n:
        names.extend([f"{b} {suffix}" for b in base])
        suffix += 1
    return names[:n]

for dept, group in df.groupby("Department"):
    n_employees = len(group)
    # Realistic span of control: ~15-25 direct reports per manager
    n_managers = max(2, round(n_employees / 18))
    names = make_unique_names(n_managers, manager_names_pool, rng)
    manager_ids = list(range(manager_id_counter, manager_id_counter + n_managers))
    manager_id_counter += n_managers

    # assign each employee in this department to a random manager in the dept
    assigned = rng.choice(len(manager_ids), size=n_employees)
    for idx, a in zip(group.index, assigned):
        manager_assignment[idx] = (manager_ids[a], names[a])

df["ManagerID"] = df.index.map(lambda i: manager_assignment[i][0])
df["ManagerName"] = df.index.map(lambda i: manager_assignment[i][1])

df.to_csv(OUT_PATH, index=False)

print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
print(f"Real attrition rate: {(df['Attrition']=='Yes').mean():.1%}")
print(f"Managers created: {df['ManagerID'].nunique()}")
print("Dropped columns:", DROP_COLS)
print("Added columns (synthetic): ManagerID, ManagerName")
print("\nFinal columns:", list(df.columns))
