"""
Builds the HR Attrition Dashboard workbook:
  Sheet 1: RawData        - flattened employee data (pivot-table source)
  Sheet 2: Dept_Summary   - SUMIFS/COUNTIFS summary table + bar chart
  Sheet 3: Salary_Summary - CASE-equivalent IF-based salary band lookup
                            + COUNTIFS summary + bar chart
  Sheet 4: Satisfaction   - satisfaction vs attrition summary + line chart
  Sheet 5: README_Pivot   - instructions for adding a native Excel
                            PivotTable on top of RawData

WHY FORMULAS, NOT HARDCODED NUMBERS (per the xlsx skill's core rule):
Every summary number below is an Excel formula referencing RawData,
not a value computed in Python and pasted in. That means if you paste
the real Kaggle CSV into RawData later, every summary table and chart
recalculates automatically -- this is what makes it a real "dashboard"
instead of a static snapshot.
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.utils import get_column_letter

df = pd.read_csv("/home/claude/hr-analytics-sql-dashboard/data/flattened_for_excel.csv")

wb = Workbook()

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(name="Arial", bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(name="Arial", bold=True, size=14, color="1F4E78")
LABEL_FONT = Font(name="Arial", bold=True, size=11)
BODY_FONT = Font(name="Arial", size=10)
THIN = Side(style="thin", color="B7C6D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def style_header_row(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center")
        cell.border = BORDER

def autosize(ws, ncols, min_width=10, max_width=32):
    for c in range(1, ncols + 1):
        col_letter = get_column_letter(c)
        max_len = min_width
        for cell in ws[col_letter]:
            if cell.value is not None:
                max_len = max(max_len, len(str(cell.value)) + 2)
        ws.column_dimensions[col_letter].width = min(max_len, max_width)

# =====================================================================
# SHEET 1: RawData
# =====================================================================
ws = wb.active
ws.title = "RawData"
cols = list(df.columns)
for j, col in enumerate(cols, start=1):
    ws.cell(row=1, column=j, value=col)
style_header_row(ws, 1, len(cols))

for i, record in enumerate(df.itertuples(index=False), start=2):
    for j, val in enumerate(record, start=1):
        ws.cell(row=i, column=j, value=val).font = BODY_FONT

ws.freeze_panes = "A2"
autosize(ws, len(cols))
N_ROWS = len(df)  # data rows, header is row 1, data is rows 2..N_ROWS+1
LAST_ROW = N_ROWS + 1

# Named ranges for readability in formulas across sheets
def colnum(name):
    return cols.index(name) + 1

dept_col = get_column_letter(colnum("department"))
attr_col = get_column_letter(colnum("attrition"))
income_col = get_column_letter(colnum("monthly_income"))
overtime_col = get_column_letter(colnum("overtime"))
jobsat_col = get_column_letter(colnum("job_satisfaction"))

# =====================================================================
# SHEET 2: Dept_Summary
# =====================================================================
ws2 = wb.create_sheet("Dept_Summary")
ws2["A1"] = "Headcount & Attrition by Department"
ws2["A1"].font = TITLE_FONT
ws2["A2"] = "Source: RawData sheet (live SUMIFS/COUNTIFS formulas, not hardcoded)"
ws2["A2"].font = Font(name="Arial", italic=True, size=9, color="666666")

headers = ["Department", "Headcount", "Employees Left", "Attrition Rate %"]
for j, h in enumerate(headers, start=1):
    ws2.cell(row=4, column=j, value=h)
style_header_row(ws2, 4, len(headers))

departments = sorted(df["department"].unique().tolist())
for i, dept in enumerate(departments, start=5):
    ws2.cell(row=i, column=1, value=dept).font = BODY_FONT
    ws2.cell(row=i, column=2,
             value=f'=COUNTIF(RawData!{dept_col}2:{dept_col}{LAST_ROW},A{i})').font = BODY_FONT
    ws2.cell(row=i, column=3,
             value=f'=COUNTIFS(RawData!{dept_col}2:{dept_col}{LAST_ROW},A{i},'
                   f'RawData!{attr_col}2:{attr_col}{LAST_ROW},"Yes")').font = BODY_FONT
    ws2.cell(row=i, column=4, value=f'=ROUND(100*C{i}/B{i},1)').font = BODY_FONT
    ws2.cell(row=i, column=4).number_format = '0.0"%"'

last_data_row = 4 + len(departments)
for r in range(5, last_data_row + 1):
    for c in range(1, 5):
        ws2.cell(row=r, column=c).border = BORDER

autosize(ws2, 4)

chart = BarChart()
chart.title = "Attrition Rate % by Department"
chart.y_axis.title = "Attrition Rate %"
chart.x_axis.title = "Department"
data = Reference(ws2, min_col=4, min_row=4, max_row=last_data_row)
cats = Reference(ws2, min_col=1, min_row=5, max_row=last_data_row)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.width = 16
chart.height = 9
ws2.add_chart(chart, f"F4")

# =====================================================================
# SHEET 3: Salary_Summary  (CASE/lookup logic -> IF-based band column
#                            on RawData, then COUNTIFS summary)
# =====================================================================
# Add a derived "salary_band" helper column directly on RawData so the
# logic is visible and auditable (this is the Excel equivalent of the
# SQL CASE statement in query 03).
band_col_idx = len(cols) + 1
band_col_letter = get_column_letter(band_col_idx)
ws["AA1" if band_col_idx > 26 else f"{band_col_letter}1"] = "salary_band"
ws.cell(row=1, column=band_col_idx, value="salary_band")
ws.cell(row=1, column=band_col_idx).fill = HEADER_FILL
ws.cell(row=1, column=band_col_idx).font = HEADER_FONT
for r in range(2, LAST_ROW + 1):
    formula = (
        f'=IF({income_col}{r}<3000,"1. Under 3,000",'
        f'IF({income_col}{r}<6000,"2. 3,000-5,999",'
        f'IF({income_col}{r}<10000,"3. 6,000-9,999",'
        f'IF({income_col}{r}<15000,"4. 10,000-14,999","5. 15,000+"))))'
    )
    ws.cell(row=r, column=band_col_idx, value=formula).font = BODY_FONT

ws3 = wb.create_sheet("Salary_Summary")
ws3["A1"] = "Attrition Rate by Salary Band"
ws3["A1"].font = TITLE_FONT
ws3["A2"] = "salary_band column on RawData uses nested IF logic (Excel equivalent of SQL CASE)"
ws3["A2"].font = Font(name="Arial", italic=True, size=9, color="666666")

headers3 = ["Salary Band", "Headcount", "Employees Left", "Attrition Rate %"]
for j, h in enumerate(headers3, start=1):
    ws3.cell(row=4, column=j, value=h)
style_header_row(ws3, 4, len(headers3))

bands = ["1. Under 3,000", "2. 3,000-5,999", "3. 6,000-9,999", "4. 10,000-14,999", "5. 15,000+"]
for i, band in enumerate(bands, start=5):
    ws3.cell(row=i, column=1, value=band).font = BODY_FONT
    ws3.cell(row=i, column=2,
             value=f'=COUNTIF(RawData!{band_col_letter}2:{band_col_letter}{LAST_ROW},A{i})').font = BODY_FONT
    ws3.cell(row=i, column=3,
             value=f'=COUNTIFS(RawData!{band_col_letter}2:{band_col_letter}{LAST_ROW},A{i},'
                   f'RawData!{attr_col}2:{attr_col}{LAST_ROW},"Yes")').font = BODY_FONT
    ws3.cell(row=i, column=4, value=f'=ROUND(100*C{i}/B{i},1)').font = BODY_FONT
    ws3.cell(row=i, column=4).number_format = '0.0"%"'

last3 = 4 + len(bands)
for r in range(5, last3 + 1):
    for c in range(1, 5):
        ws3.cell(row=r, column=c).border = BORDER
autosize(ws3, 4)

chart3 = BarChart()
chart3.title = "Attrition Rate % by Salary Band"
chart3.y_axis.title = "Attrition Rate %"
chart3.x_axis.title = "Salary Band"
data3 = Reference(ws3, min_col=4, min_row=4, max_row=last3)
cats3 = Reference(ws3, min_col=1, min_row=5, max_row=last3)
chart3.add_data(data3, titles_from_data=True)
chart3.set_categories(cats3)
chart3.width = 16
chart3.height = 9
ws3.add_chart(chart3, "F4")

# =====================================================================
# SHEET 4: Satisfaction_Summary
# =====================================================================
ws4 = wb.create_sheet("Satisfaction_Summary")
ws4["A1"] = "Job Satisfaction vs. Attrition Rate"
ws4["A1"].font = TITLE_FONT
ws4["A2"] = "Source: RawData sheet (live COUNTIFS/AVERAGEIFS formulas)"
ws4["A2"].font = Font(name="Arial", italic=True, size=9, color="666666")

headers4 = ["Satisfaction Score", "Label", "Headcount", "Employees Left", "Attrition Rate %", "Avg Monthly Income"]
for j, h in enumerate(headers4, start=1):
    ws4.cell(row=4, column=j, value=h)
style_header_row(ws4, 4, len(headers4))

labels = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
for i, score in enumerate(range(1, 5), start=5):
    ws4.cell(row=i, column=1, value=score).font = BODY_FONT
    ws4.cell(row=i, column=2, value=labels[score]).font = BODY_FONT
    ws4.cell(row=i, column=3,
             value=f'=COUNTIF(RawData!{jobsat_col}2:{jobsat_col}{LAST_ROW},A{i})').font = BODY_FONT
    ws4.cell(row=i, column=4,
             value=f'=COUNTIFS(RawData!{jobsat_col}2:{jobsat_col}{LAST_ROW},A{i},'
                   f'RawData!{attr_col}2:{attr_col}{LAST_ROW},"Yes")').font = BODY_FONT
    ws4.cell(row=i, column=5, value=f'=ROUND(100*D{i}/C{i},1)').font = BODY_FONT
    ws4.cell(row=i, column=5).number_format = '0.0"%"'
    ws4.cell(row=i, column=6,
             value=f'=ROUND(AVERAGEIF(RawData!{jobsat_col}2:{jobsat_col}{LAST_ROW},A{i},'
                   f'RawData!{income_col}2:{income_col}{LAST_ROW}),0)').font = BODY_FONT

last4 = 4 + 4
for r in range(5, last4 + 1):
    for c in range(1, 7):
        ws4.cell(row=r, column=c).border = BORDER
autosize(ws4, 6)

chart4 = LineChart()
chart4.title = "Attrition Rate % by Job Satisfaction Level"
chart4.y_axis.title = "Attrition Rate %"
chart4.x_axis.title = "Satisfaction Level"
data4 = Reference(ws4, min_col=5, min_row=4, max_row=last4)
cats4 = Reference(ws4, min_col=2, min_row=5, max_row=last4)
chart4.add_data(data4, titles_from_data=True)
chart4.set_categories(cats4)
chart4.width = 16
chart4.height = 9
ws4.add_chart(chart4, "H4")

# =====================================================================
# SHEET 5: README_Pivot  (instructions for native pivot table)
# =====================================================================
ws5 = wb.create_sheet("README_PivotInstructions")
ws5["A1"] = "How to add a native Excel PivotTable (optional, 60 seconds)"
ws5["A1"].font = TITLE_FONT
instructions = [
    "",
    "This workbook's summary tables use live SUMIFS/COUNTIFS/AVERAGEIFS",
    "formulas pointed at the RawData sheet (Excel's equivalent of SQL",
    "CASE + GROUP BY). To also include a true native Excel PivotTable",
    "object for your portfolio/demo, do this in Excel/Google Sheets:",
    "",
    "1. Click any cell inside the RawData sheet.",
    "2. Insert -> PivotTable -> New Worksheet.",
    "3. Drag 'department' to Rows.",
    "4. Drag 'attrition' to Columns.",
    "5. Drag 'employee_id' to Values -> set to Count.",
    "6. Right-click any value -> Show Values As -> % of Row Total",
    "   to get the same attrition % shown in Dept_Summary.",
    "7. Insert -> Recommended Charts to add a chart from the pivot.",
    "",
    "Repeat with 'salary_band' or 'job_satisfaction' in Rows to",
    "reproduce the Salary_Summary / Satisfaction_Summary views",
    "as native pivot tables instead of formula tables.",
]
for i, line in enumerate(instructions, start=2):
    ws5.cell(row=i, column=1, value=line).font = BODY_FONT
ws5.column_dimensions["A"].width = 75

# Reorder sheets: RawData first, then summaries, README last
wb._sheets = [wb["RawData"], wb["Dept_Summary"], wb["Salary_Summary"],
              wb["Satisfaction_Summary"], wb["README_PivotInstructions"]]

OUT_PATH = "/home/claude/hr-analytics-sql-dashboard/reports/HR_Attrition_Dashboard.xlsx"
wb.save(OUT_PATH)
print("Saved:", OUT_PATH)
