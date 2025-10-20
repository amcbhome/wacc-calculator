# app.py — Three-Step WACC Model (linked tables)
# Author: A. McBride | GPT-5 | Oct 2025

import streamlit as st
import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Page Setup
# ──────────────────────────────────────────────
st.set_page_config(page_title="💸 WACC Three-Step Model", layout="centered")
st.title("💸 Weighted Average Cost of Capital (WACC) — Three-Step Model")

st.markdown("""
This model follows a **three-step data chain**:

1️⃣ Compute component costs  
2️⃣ Apply Units × Price = Cost → Weighted Cost  
3️⃣ Relate weighted costs to the component rates  
""")

# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────
def cost_of_equity(rf, rm, beta): return rf + beta*(rm - rf)
def cost_of_pref(d,p): return d/p
def cost_of_irredeemable(i,p,t): return ((i*100)/p)*(1-t)
def cost_of_redeemable(i,r,p,n,t):
    I=i*100
    return ((I+(r-p)/n)/((r+p)/2))*(1-t)
def cost_of_loan(i,t): return i*(1-t)

# ──────────────────────────────────────────────
# Sidebar Parameters
# ──────────────────────────────────────────────
st.sidebar.header("Global Parameters")
rf = st.sidebar.number_input("Risk-Free Rate (Rf)",0.0,1.0,0.05,0.005)
rm = st.sidebar.number_input("Market Return (Rm)",0.0,1.0,0.11,0.005)
tax= st.sidebar.number_input("Tax Rate (T)",0.0,1.0,0.30,0.01)
beta=st.sidebar.number_input("Equity Beta (β)",0.0,5.0,1.5,0.1)

# bond inputs
pref_div=0.10; pref_price=0.89
irr_coupon=0.11; irr_price=70
red_coupon=0.09; red_price=96; red_redeem=100; red_years=4
loan_rate=0.07

# ──────────────────────────────────────────────
# STEP 1 – Component Costs
# ──────────────────────────────────────────────
st.subheader("Step 1 – Component Cost Calculations")

ke = cost_of_equity(rf,rm,beta)*100
kp = cost_of_pref(pref_div,pref_price)*100
kd_ir = cost_of_irredeemable(irr_coupon,irr_price,tax)*100
kd_red = cost_of_redeemable(red_coupon,red_redeem,red_price,red_years,tax)*100
kd_loan = cost_of_loan(loan_rate,tax)*100

step1 = pd.DataFrame({
    "Source":[
        "Ordinary Shares (Ke)",
        "Preference Shares (Kp)",
        "Irredeemable Bonds (Kd₁)",
        "Redeemable Bonds (Kd₂)",
        "Bank Loan (Kd₃)"
    ],
    "Cost_%":[round(x,2) for x in [ke,kp,kd_ir,kd_red,kd_loan]]
})
st.dataframe(step1,use_container_width=True)

# ──────────────────────────────────────────────
# STEP 2 – Units × Price = Cost (+ Weighted Cost)
# ──────────────────────────────────────────────
st.subheader("Step 2 – Capital Structure (Units × Price = Cost)")

structure = [
    ["Ordinary Shares",260000,1.90],
    ["Preference Shares",90000,0.89],
    ["Irredeemable Bonds",1800,70.0],
    ["Redeemable Bonds",900,96.0],
    ["Bank Loan",70000,1.0],
]
df2 = pd.DataFrame(structure,columns=["Source","Units","Price"])
df2["Cost"] = df2["Units"]*df2["Price"]
df2["Weighted_Cost"] = df2["Cost"]/df2["Cost"].sum()*100  # % share of total

st.dataframe(df2,use_container_width=True)

# ──────────────────────────────────────────────
# STEP 3 – Combine and Relate Ratios
# ──────────────────────────────────────────────
st.subheader("Step 3 – Weighted Cost Analysis & Ratios")

step3 = pd.merge(step1,df2[["Source","Weighted_Cost"]],on="Source",how="left")
step3["Weighted_Cost/Cost_%"] = np.round(step3["Weighted_Cost"]/step3["Cost_%"],4)

st.dataframe(step3,use_container_width=True)

# WACC ≈ Σ(Weighted_Cost/Cost_% × Cost_%)/Σ(Weighted_Cost) simplifies to Σ(weights×rates)
weighted_sum = (step3["Weighted_Cost"]/100 * step3["Cost_%"]).sum()
st.metric("Weighted Average Cost of Capital (WACC)", f"{weighted_sum:.2f}%")

st.markdown("""
---
### Interpretation
- **Step 1**: component rates (CAPM & bond yields)  
- **Step 2**: capital employed = Units × Price  
- **Step 3**: weighted contributions & proportional comparison  
""")
