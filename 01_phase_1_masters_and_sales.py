import pandas as pd
import numpy as np
import random
import math
from datetime import timedelta

print("🚀 INITIATING PHASE 1: ENTERPRISE DATA PIPELINE...")

# 1. BUILD: DIM_STORE_MASTER
states_data = [('Maharashtra', '27', ['Mumbai', 'Pune', 'Nagpur']), ('Delhi', '07', ['New Delhi']), ('Karnataka', '29', ['Bangalore', 'Mysore']), ('Gujarat', '24', ['Ahmedabad', 'Surat']), ('Rajasthan', '08', ['Jaipur', 'Udaipur']), ('West Bengal', '19', ['Kolkata']), ('Tamil Nadu', '33', ['Chennai', 'Coimbatore']), ('Uttar Pradesh', '09', ['Noida', 'Lucknow']), ('Telangana', '36', ['Hyderabad']), ('Haryana', '06', ['Gurgaon'])]
stores = [{'Store_Name': 'HO_WAREHOUSE', 'Sales_Channel': 'Warehouse', 'Store_City': 'Mumbai', 'Place_of_Supply': 'Maharashtra', 'State_Code': '27'}]
for i in range(1, 41):
    state_name, state_code, cities = random.choice(states_data)
    stores.append({'Store_Name': f'Retail_STR_{str(i).zfill(3)}_{random.choice(cities)}', 'Sales_Channel': 'Retail Store', 'Store_City': random.choice(cities), 'Place_of_Supply': state_name, 'State_Code': state_code})
for channel in ['Amazon', 'Flipkart', 'Myntra', 'Ajio', 'Nykaa', 'Blinkit', 'Website D2C']:
    stores.append({'Store_Name': f'{channel}_Virtual_Store', 'Sales_Channel': channel, 'Store_City': 'Mumbai', 'Place_of_Supply': 'Maharashtra', 'State_Code': '27'})
store_df = pd.DataFrame(stores)
store_df.to_csv("DIM_STORE_MASTER.csv", index=False)

# 2. BUILD: DIM_SKU_MASTER
catalog = []
for i in range(1, 121):
    raw_mrp = random.uniform(1500, 12000)
    mrp = math.ceil(raw_mrp / 500) * 500 - 1 
    std_cost = round(mrp * round(random.uniform(0.25, 0.45), 4), 2)
    catalog.append({
        'SKU_ID': f'JW{str(i).zfill(3)}',
        'Product_Name': f"Jewelry Item {i}",
        'Category': random.choice(['Ring', 'Necklace', 'Earrings', 'Bracelet', 'Bangles']),
        'HSN_Code': '71179090', 'GST_Rate': 3, 'Standard_Cost': std_cost, 'MRP': mrp, 'COGS_VALUE': std_cost,
        'Launch_Date': '2022-03-01', 'Status': 'Active'
    })
catalog_df = pd.DataFrame(catalog)
catalog_df.to_csv("DIM_SKU_MASTER.csv", index=False)

# 3. BUILD: FACT_SALES_REGISTER
sales_records = []
START_DATE = pd.to_datetime("2022-03-01")
active_skus = catalog_df[catalog_df['Status'] == 'Active']

for i in range(1, 10000): # Generating sample rows for GitHub
    inv_date = START_DATE + timedelta(days=random.randint(0, 1500))
    item = active_skus.sample(1).iloc[0]
    store = store_df[store_df['Store_Name'] != 'HO_WAREHOUSE'].sample(1).iloc[0]
    is_online = 'Virtual_Store' in store['Store_Name']
    
    qty = random.choices([1, 2], weights=[0.8, 0.2])[0]
    gross_amount = item['MRP'] * qty
    invoice_value = gross_amount
    taxable_value = round(invoice_value / 1.03, 2)
    
    if is_online:
        marketplace_fee = round(invoice_value * 0.10, 2)
        net_realization = round(invoice_value - marketplace_fee, 2)
    else:
        marketplace_fee, net_realization = 0, invoice_value
        
    inv_num = f"INV{inv_date.strftime('%y%m')}{str(i).zfill(6)}"
    
    sales_records.append({
        'Invoice_Date': inv_date.strftime('%Y-%m-%d'),
        'Invoice_Number': inv_num,
        'Store_Name': store['Store_Name'],
        'SKU_ID': item['SKU_ID'],
        'Quantity': qty,
        'Gross_Amount': gross_amount,
        'Taxable_Value': taxable_value,
        'Invoice_Value': invoice_value,
        'Net_Realization': net_realization,
        'Payment_Mode': 'Payment Gateway' if is_online else 'UPI',
        'Bank_Link_Key': f"BNK_{inv_num}"
    })

pd.DataFrame(sales_records).to_csv("FACT_SALES_REGISTER.csv", index=False)
print("✅ Phase 1 complete. Base data generated.")