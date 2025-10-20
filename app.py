# app.py — WACC Three-Step Data Model (Final Version)
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
This model follows a **three-step structure**:

1️⃣ **Component Costs** – Calculate \(K_e, K_p, K_{d1}, K_{d2}, K_{d3}\)  
2️⃣ **Capital Structure** – Compute Units × Price and weightings  
3️⃣ **Weighted Analysis** – Relate weighted costs back to component rates and total **WACC**
""")

# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────
def cost_of_equity(rf, rm, beta): 
    return rf + beta * (rm - rf)

def cost_of_pref(div, price): 
    return div / price

def cost_of_irredeemable(coupon, price, tax): 
    return ((coupon * 100) / price) * (1 - tax)

def cost_of_redeemable(coupon, redeem, price, years, tax):
    I = coupon * 100
    return ((I + (redeem - price) / years) / ((redeem + price) / 2)) * (1 - tax)

def cost_of_loan(rate, tax): 
    return rate * (1 - tax)

# ──────────────────────────────────────────────
# Sidebar Parameters
# ──────────────────────────────────────────────
st.sidebar.header("Global Parameters")
rf = st.sidebar.number_input("Risk-Free Rate (Rf)", 0.0, 1.0, 0.05, 0.005)
rm = st.sidebar.number_input("Market Return (Rm)", 0.0, 1.0, 0.11, 0.005)
tax = st.sidebar.number_input("Corporation Tax Rate (T)", 0.0, 1.0, 0.30, 0.01)
beta = st.sidebar.number_input("Equity Beta (β)", 0.0, 5.0, 1.5, 0.1)

# Prefs / Bonds / Loan parameters
pref_div, pref_price = 0.10, 0.89
irr_coupon, irr_price = 0.11, 70
red_coupon, red_price, red_redeem, red_years = 0.09, 96, 100, 4
loan_rate = 0.07

# ──────────────────────────────────────────────
# STEP 1 – Component Cost Calculations
# ──────────────────────────────────────────────
st.subheader("Step 1 – Component Cost Calculations")

ke = cost_of_equity(rf, rm, beta) * 100
kp = cost_of_pref(pref_div, pref_price) * 100
kd_ir = cost_of_irredeemable(irr_coupon, irr_price, tax) * 100
kd_red = cost_of_redeemable(red_coupon, red_redeem, red_price, red_years, tax) * 100
kd_loan = cost_of_loan(loan_rate, tax) * 100

step1 = pd.DataFrame({
    "Source": [
        "Ordinary Shares (Ke)",
        "Preference Shares (Kp)",
        "Irredeemable Bonds (Kd₁)",
        "Redeemable Bonds (Kd₂)",
        "Bank Loan (Kd₃)"
    ],
    "Cost_%": [round(x, 2) for x in [ke, kp, kd_ir, kd_red, kd_loan]]
})

st.dataframe(step1, use_container_width=True)
st.caption("Step 1 computes the five component costs from the given parameters.")

# ──────────────────────────────────────────────
# STEP 2 – Capital Structure (Units × Price)
# ──────────────────────────────────────────────
st.subheader("Step 2 – Capital Structure (Units × Price = Cost)")

structure = [
    ["Ordinary Shares (Ke)", 260000, 1.90],
    ["Preference Shares (Kp)", 90000, 0.89],
    ["Irredeemable Bonds (Kd₁)", 1800, 70.0],
    ["Redeemable Bonds (Kd₂)", 900, 96.0],
    ["Bank Loan (Kd₃)", 70000, 1.0],
]

df2 = pd.DataFrame(structure, columns=["Source", "Units", "Price"])
df2["Cost"] = df2["Units"] * df2["Price"]
df2["Weighted_Cost"] = df2["Cost"] / df2["Cost"].sum() * 100

st.dataframe(df2, use_container_width=True)
st.caption("Step 2 computes each source’s total cost and its weighted share of total capital employed.")

# ──────────────────────────────────────────────
# STEP 3 – Weighted Cost Analysis and Totals
# ──────────────────────────────────────────────
st.subheader("Step 3 – Weighted Cost Analysis and Totals")

# Merge Step 1 and Step 2 data
step3 = pd.merge(step1, df2[["Source", "Weighted_Cost"]], on="Source", how="left")
step3["Weighted_Cost ÷ Cost_%"] = np.round(step3["Weighted_Cost"] / step3["Cost_%"], 4)

# Calculate total WACC
wacc_total = (step3["Weighted_Cost"] / 100 * step3["Cost_%"]).sum()

# Add total row
total_row = pd.DataFrame({
    "Source": ["Total / WACC"],
    "Cost_%": [""],
    "Weighted_Cost": [""],
    "Weighted_Cost ÷ Cost_%": [f"{wacc_total:.2f}%"]
})

step3_display = pd.concat([step3, total_row], ignore_index=True)

# Display full Step 3 table (no markdown dependency)
st.dataframe(step3_display, use_container_width=True)

# Bold WACC summary
st.markdown(f"### ✅ **Overall WACC: {wacc_total:.2f}%**")

st.markdown("""
---
### Interpretation
**Step 1:** Calculates the component rates  
**Step 2:** Derives total and weighted capital values  
**Step 3:** Relates weighted costs to component rates and totals **WACC**
""")

