# Enterprise Retail Data Simulator

Python-based data generator that simulates a ₹100 Crore retail business.

## Project Overview

- Generates realistic retail data: SKUs, stores, sales, purchases, bank ledger, payroll, marketing ROI, and store footfall.
- Output: 10 reconciled CSV files ready for Power BI, Tableau, or SQL.

## How to Run

1. **Step 1 – Master Data & Sales**  
   Run: `01_phase_1_masters_and_sales.py`  
   - Creates SKU Master, Store Master, and base Sales Register.

2. **Step 2 – Financials & Supply Chain**  
   Run: `02_phase_2_purchases_and_bank.py`  
   - Generates Opening Stock, Purchases, Freight Transfers, and Bank Ledger.

3. **Step 3 – Advanced BI & Payroll**  
   Run: `03_phase_3_advanced_bi_and_payroll.py`  
   - Breaks bulk expenses into HR payroll, creates Marketing Campaign ROI, and Store Footfall data.

## Tech Stack

- Language: Python
- Output: CSV files for BI tools (Power BI, Tableau) and SQL databases.

## How Recruiters Can Use This

- Review the Python scripts for data logic.
- Import the CSVs into BI tools to see the end-to-end retail analytics workflow.
