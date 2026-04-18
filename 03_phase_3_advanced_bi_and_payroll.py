import pandas as pd
import numpy as np
import random
from datetime import timedelta
from pandas.tseries.offsets import MonthEnd

print("🚀 INITIATING PHASE 3: HR PAYROLL, MARKETING & ADVANCED BI...")

try:
    sales_df = pd.read_csv("FACT_SALES_REGISTER.csv")
    stores_df = pd.read_csv("DIM_STORE_MASTER.csv")
    expenses_df = pd.read_csv("FACT_PURCHASES_AND_EXPENSES.csv")
    bank_df = pd.read_csv("FACT_BANK_LEDGER.csv")
except FileNotFoundError:
    print("❌ ERROR: Missing Phase 1 or 2 files.")
    exit()

# 1. DIM_EMPLOYEE_MASTER (Strict Counts)
employees = []
emp_id_counter = 1000
base_salaries = {'CEO': 350000, 'CFO': 250000, 'Head of Operations': 180000, 'HR Head': 120000, 'Senior Accountant': 80000, 'Junior Accountant': 40000, 'Warehouse Manager': 60000, 'Asst Warehouse Manager': 35000, 'Packing Staff': 22000, 'E-com Head': 150000, 'Store Manager': 55000, 'Sales Executive': 30000, 'E-commerce Manager': 80000, 'Performance Marketer': 60000, 'Customer Support': 35000}

ho_roles = ['CEO', 'CFO', 'Head of Operations', 'HR Head', 'Senior Accountant'] + ['Junior Accountant']*2 + ['Warehouse Manager'] + ['Asst Warehouse Manager']*2 + ['Packing Staff']*14 + ['E-com Head']
for role in ho_roles:
    employees.append({'Employee_ID': f"EMP{emp_id_counter}", 'Employee_Name': f"HO_{role.replace(' ', '')}_{emp_id_counter}", 'Role': role, 'Team': 'HO Operations', 'Store_Name': 'HO_WAREHOUSE', 'Base_Salary': base_salaries[role]})
    emp_id_counter += 1

for _, store in stores_df[stores_df['Store_Name'] != 'HO_WAREHOUSE'].iterrows():
    is_online = 'Virtual_Store' in store['Store_Name']
    roles = ['E-commerce Manager', 'Performance Marketer', 'Customer Support'] if is_online else ['Store Manager', 'Sales Executive', 'Sales Executive']
    team = 'Website & Digital Team' if is_online else 'Retail Store Team'
    for role in roles:
        employees.append({'Employee_ID': f"EMP{emp_id_counter}", 'Employee_Name': f"{store['Store_Name'].split('_')[0]}_{role.split(' ')[0]}_{emp_id_counter}", 'Role': role, 'Team': team, 'Store_Name': store['Store_Name'], 'Base_Salary': base_salaries[role]})
        emp_id_counter += 1

emp_df = pd.DataFrame(employees)
emp_df.to_csv("DIM_EMPLOYEE_MASTER.csv", index=False)

# 2. UPGRADE SALES REGISTER & PAYROLL (Overwriting V1 with Employee Links)
sales_execs = emp_df[emp_df['Role'] == 'Sales Executive']
sales_df['Sales_Executive_ID'] = sales_df['Store_Name'].map(lambda x: random.choice(sales_execs[sales_execs['Store_Name'] == x]['Employee_ID'].tolist()) if x in sales_execs['Store_Name'].values else "")
sales_df.to_csv("FACT_SALES_REGISTER_V2.csv", index=False)

new_expense_records = []
new_bank_records = []
inv_counter = 100000

for month_date in pd.date_range(start='2022-03-01', end='2026-04-30', freq='MS'):
    inflation_mult = (1.06 ** (month_date.year - 2022 + (1 if month_date.month >= 4 else 0))) 
    for _, emp in emp_df.iterrows():
        current_salary = round(emp['Base_Salary'] * inflation_mult, 2)
        inv_ref = f"PAYROLL_{inv_counter}"
        pay_date = month_date + MonthEnd(0) if emp['Team'] == 'HO Operations' else month_date
        
        new_expense_records.append({'Date': pay_date.strftime('%Y-%m-%d'), 'Invoice_Number': inv_ref, 'Vendor_Name': f"Employee: {emp['Employee_ID']} - {emp['Employee_Name']}", 'Category': 'Salaries & Incentives', 'Item_Type': 'Payroll', 'Store_Name': emp['Store_Name'], 'Quantity': 1, 'Total_Amount': current_salary, 'Payment_Terms': 'Immediate', 'Bank_Link_Key': f"BNK_{inv_ref}"})
        new_bank_records.append({'Date': pay_date.strftime('%Y-%m-%d'), 'Transaction_Type': 'Money OUT', 'Category': f"Payroll ({emp['Team']})", 'Reference': inv_ref, 'Store_Name': emp['Store_Name'], 'Amount': -current_salary, 'Bank_Link_Key': f"BNK_{inv_ref}"})
        inv_counter += 1

pd.concat([expenses_df, pd.DataFrame(new_expense_records)], ignore_index=True).to_csv("FACT_PURCHASES_AND_EXPENSES_V2.csv", index=False)
bank_df = pd.concat([bank_df, pd.DataFrame(new_bank_records)], ignore_index=True)
bank_df.sort_values(by='Date', inplace=True)
bank_df.to_csv("FACT_BANK_LEDGER_V2.csv", index=False)

# 3. REPORT: EMPLOYEE ROI
payroll_df = pd.DataFrame(new_expense_records)
payroll_df['Employee_ID'] = payroll_df['Vendor_Name'].apply(lambda x: x.split(" - ")[0].replace("Employee: ", ""))
emp_costs = payroll_df.groupby('Employee_ID')['Total_Amount'].sum().reset_index()

emp_sales = sales_df.groupby('Sales_Executive_ID')['Net_Realization'].sum().reset_index()
roi_report = emp_df.merge(emp_costs, on='Employee_ID', how='left').merge(emp_sales, left_on='Employee_ID', right_on='Sales_Executive_ID', how='left').fillna(0)
roi_report['ROI_Multiplier'] = np.where(roi_report['Total_Amount'] > 0, round(roi_report['Net_Realization'] / roi_report['Total_Amount'], 2), 0)
roi_report.to_csv("REPORT_EMPLOYEE_ROI.csv", index=False)

# 4. MARKETING & FOOTFALL
ads_df = expenses_df[expenses_df['Category'] == 'Advertising (Meta/Google)']
marketing_records = [{'Campaign_Month': pd.to_datetime(row['Date']).strftime('%Y-%m'), 'Campaign_Name': f"{pd.to_datetime(row['Date']).strftime('%b %Y')} - Ads", 'Target_Store': row['Store_Name'], 'Total_Spend_INR': row['Total_Amount'], 'Impressions': int(row['Total_Amount'] * 120), 'Clicks': int(row['Total_Amount'] * 120 * 0.02)} for _, row in ads_df.iterrows()]
pd.DataFrame(marketing_records).to_csv("FACT_MARKETING_CAMPAIGNS.csv", index=False)

daily_invoices = sales_df[sales_df['Quantity'] > 0].groupby(['Store_Name', 'Invoice_Date']).size().reset_index(name='Invoice_Count')
footfall_records = [{'Date': row['Invoice_Date'], 'Store_Name': row['Store_Name'], 'Total_Visitors': int(row['Invoice_Count'] * (60 if 'Virtual' in row['Store_Name'] else 10)), 'Converted_Invoices': row['Invoice_Count']} for _, row in daily_invoices.iterrows()]
pd.DataFrame(footfall_records).to_csv("FACT_STORE_FOOTFALL.csv", index=False)

print("✅ Phase 3 complete. Advanced BI generated.")