import pandas as pd
import numpy as np
import random
from datetime import timedelta

print("🚀 INITIATING PHASE 2: FINANCIAL, LOGISTICS & BANKING ENGINE...")

# LOAD PHASE 1 DATA
try:
    stores_df = pd.read_csv("DIM_STORE_MASTER.csv")
    skus_df = pd.read_csv("DIM_SKU_MASTER.csv")
    sales_df = pd.read_csv("FACT_SALES_REGISTER.csv")
except FileNotFoundError:
    print("❌ ERROR: Phase 1 CSVs not found.")
    exit()

sales_df['Invoice_Date'] = pd.to_datetime(sales_df['Invoice_Date'])
catalog = skus_df.set_index('SKU_ID').to_dict('index')
store_states = stores_df.set_index('Store_Name')['State_Code'].to_dict()

positive_sales = sales_df[sales_df['Quantity'] > 0].copy()
positive_sales['Month_Start'] = positive_sales['Invoice_Date'].dt.to_period('M').dt.to_timestamp()

# 1. FACT_OPENING_STOCK (Look-Ahead Logic)
monthly_max = positive_sales.groupby(['Store_Name', 'SKU_ID', 'Month_Start'])['Quantity'].sum().reset_index()
max_demand = monthly_max.groupby(['Store_Name', 'SKU_ID'])['Quantity'].max().reset_index()

opening_records = []
for _, row in max_demand.iterrows():
    qty = max(int(row['Quantity'] * 1.5), 15) 
    cost = catalog[row['SKU_ID']]['COGS_VALUE']
    opening_records.append({'Date': '2022-03-01', 'Transaction_Type': 'OPENING_STOCK', 'Store_Name': row['Store_Name'], 'SKU_ID': row['SKU_ID'], 'Qty_In': qty, 'Unit_Cost': cost, 'Total_Value': round(qty * cost, 2), 'Inventory_Link_Key': f"OPEN_{row['Store_Name']}_{row['SKU_ID']}"})

ho_demand = max_demand.groupby('SKU_ID')['Quantity'].sum().reset_index()
for _, row in ho_demand.iterrows():
    qty = max(int(row['Quantity'] * 2.0), 100) 
    cost = catalog[row['SKU_ID']]['COGS_VALUE']
    opening_records.append({'Date': '2022-03-01', 'Transaction_Type': 'OPENING_STOCK', 'Store_Name': 'HO_WAREHOUSE', 'SKU_ID': row['SKU_ID'], 'Qty_In': qty, 'Unit_Cost': cost, 'Total_Value': round(qty * cost, 2), 'Inventory_Link_Key': f"OPEN_HO_{row['SKU_ID']}"})

pd.DataFrame(opening_records).to_csv("FACT_OPENING_STOCK.csv", index=False)

# 2. FACT_PURCHASES_AND_EXPENSES & 3. BANK LEDGER
purchase_expense_records = []
bank_records = [] 
monthly_ho_demand = positive_sales.groupby(['Month_Start', 'SKU_ID'])['Quantity'].sum().reset_index()

pinv_counter = 100000
for _, row in monthly_ho_demand.iterrows():
    buy_qty = int(row['Quantity'] * 1.15) 
    if buy_qty == 0: continue
    purch_date = row['Month_Start'] + timedelta(days=2) 
    total_inv = round((buy_qty * catalog[row['SKU_ID']]['COGS_VALUE']) * 1.03, 2)
    pinv = f"PINV{pinv_counter}"
    
    purchase_expense_records.append({'Date': purch_date.strftime('%Y-%m-%d'), 'Invoice_Number': pinv, 'Vendor_Name': "Master Jewelers Hub", 'Category': 'Inventory Purchase', 'Item_Type': 'Inventory', 'Store_Name': 'HO_WAREHOUSE', 'SKU_ID': row['SKU_ID'], 'Quantity': buy_qty, 'Total_Amount': total_inv, 'Payment_Terms': '30 Days', 'Bank_Link_Key': f"PAY_{pinv}"})
    bank_records.append({'Date': (purch_date + timedelta(days=30)).strftime('%Y-%m-%d'), 'Transaction_Type': 'Money OUT', 'Category': 'Vendor Payment', 'Reference': pinv, 'Store_Name': 'HO_WAREHOUSE', 'Amount': -total_inv, 'Bank_Link_Key': f"PAY_{pinv}"})
    pinv_counter += 1

exp_counter = 500000
for store_idx, store in stores_df[stores_df['Store_Name'] != 'HO_WAREHOUSE'].iterrows():
    for month_date in pd.date_range(start='2022-03-01', end='2026-04-30', freq='MS'):
        inflation_mult = (1.06 ** (month_date.year - 2022 + (1 if month_date.month >= 4 else 0))) 
        expenses = {'Rent & CAM': round(85000 * inflation_mult, 2), 'Electricity': round(12000 * inflation_mult, 2), 'Advertising (Meta/Google)': round(40000, 2) if 'Virtual' in store['Store_Name'] else 0}
        
        for exp_name, amt in expenses.items():
            if amt == 0: continue
            einv = f"EXP{exp_counter}"
            total_amt = round(amt * 1.18, 2)
            purchase_expense_records.append({'Date': month_date.strftime('%Y-%m-%d'), 'Invoice_Number': einv, 'Vendor_Name': f"Vendor_{exp_name}", 'Category': exp_name, 'Item_Type': 'OpEx', 'Store_Name': store['Store_Name'], 'Quantity': 1, 'Total_Amount': total_amt, 'Payment_Terms': 'Immediate', 'Bank_Link_Key': f"PAY_{einv}"})
            bank_records.append({'Date': (month_date + timedelta(days=4)).strftime('%Y-%m-%d'), 'Transaction_Type': 'Money OUT', 'Category': exp_name, 'Reference': einv, 'Store_Name': store['Store_Name'], 'Amount': -total_amt, 'Bank_Link_Key': f"PAY_{einv}"})
            exp_counter += 1

pd.DataFrame(purchase_expense_records).to_csv("FACT_PURCHASES_AND_EXPENSES.csv", index=False)

# 4. FACT_STOCK_TRANSFERS
transfer_records = []
trn_counter = 10000
store_demand = positive_sales[positive_sales['Store_Name'] != 'HO_WAREHOUSE'].groupby(['Store_Name', 'Month_Start', 'SKU_ID'])['Quantity'].sum().reset_index()

for _, row in store_demand.iterrows():
    trn_qty = int(row['Quantity'] * 1.10) 
    if trn_qty == 0: continue
    tvch = f"TRN{trn_counter}"
    freight = 1450 # Default avg freight
    transfer_records.append({'Date': row['Month_Start'].strftime('%Y-%m-%d'), 'Transfer_Voucher': tvch, 'From_Location': 'HO_WAREHOUSE', 'To_Location': row['Store_Name'], 'SKU_ID': row['SKU_ID'], 'Quantity': trn_qty, 'Freight_Charges': freight, 'Status': 'Completed', 'Transfer_Link_Key': f"TRN_{tvch}"})
    bank_records.append({'Date': (row['Month_Start'] + timedelta(days=1)).strftime('%Y-%m-%d'), 'Transaction_Type': 'Money OUT', 'Category': 'Logistics & Freight', 'Reference': tvch, 'Store_Name': row['Store_Name'], 'Amount': -freight, 'Bank_Link_Key': f"FRT_{tvch}"})
    trn_counter += 1

pd.DataFrame(transfer_records).to_csv("FACT_STOCK_TRANSFERS.csv", index=False)

# 5. RECONCILE REVENUE TO BANK
for _, row in sales_df.iterrows():
    actual_settlement = pd.to_datetime(row['Invoice_Date']) + timedelta(days=random.randint(30, 60) if row['Payment_Mode'] == 'Payment Gateway' else 1)
    bank_records.append({'Date': actual_settlement.strftime('%Y-%m-%d'), 'Transaction_Type': 'Money IN', 'Category': 'Sales Settlement', 'Reference': row['Invoice_Number'], 'Store_Name': row['Store_Name'], 'Amount': row['Net_Realization'], 'Bank_Link_Key': row['Bank_Link_Key']})

bank_df = pd.DataFrame(bank_records)
bank_df.sort_values(by='Date', inplace=True)
bank_df.to_csv("FACT_BANK_LEDGER.csv", index=False)
print("✅ Phase 2 complete. Financials generated.")