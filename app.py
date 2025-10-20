# app.py — Dynamic WACC Three-Step Model (Fully Variable)
# Author: A. McBride | GPT-5 | Oct 2025

import streamlit as st
import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Page Setup
# ──────────────────────────────────────────────
st.set_page_config(page_title="💸 WACC Three-Step Model", layout="centered")
st.title("💸 Weighted Average Cost of Capital (WACC) — Dynamic Three-Step Model")

st.markdown("""
This model calculates the **Weighted Average Cost of Capital (WACC)** dynamically  
from user-entered data.

1️⃣ **Step 1 – Component Costs:** calculates \(K_e, K_p, K_{d1}, K_{d2}, K_{d3}\)  
2️⃣ **Step 2 – Capital Structure:** computes Units × Price and weighting  
3️⃣ **Step 3 – Weighted Analysis:** relates weighted costs and totals **WACC**
""")

# ──────────────────────────────────────────────
# Input Data Sidebar
# ──────────────────────────────────────────────
st.sidebar.header("Input Data")

st.sidebar.markdown("#### Market & Financial Parameters")
rf = st.sidebar.number_input("Risk-Free Rate (Rf)", 0.0, 1.0, 0.05, 0.005)
rm = st.sidebar.number_input("Market Return (Rm)", 0.0, 1.0, 0.11, 0.005)
tax = st.sidebar.number_input("Corporation Tax Rate (T)", 0.0, 1.0, 0.30, 0.01)
beta = st.sidebar.number_input("Equity Beta (β)", 0.0, 5.0, 1.5, 0.1)

st.sidebar.markdown("#### Instrument Details")
# Preference
pref_div = st.sidebar.number_input("Preference Dividend per £1", 0.0, 1.0, 0.10, 0.01)
pref_price = st.sidebar.number_input("Preference Share Price (£)", 0.1, 10.0, 0.89, 0.01)
pref_units = st.sidebar.number_input("Preference Shares (Units)", 0, 500000, 90000, 1000)

# Ordinary Shares
eq_units = st.sidebar.number_input("Ordinary Shares (Units)", 0, 1000000, 260000, 1000)
eq_price = st.sidebar.number_input("Ordinary Share Price (£)", 0.1, 10.0, 1.90, 0.01)

# Irredeemable Bonds
irr_coupon = st.sidebar.number_input("Irredeemable Bond Coupon", 0.0, 1.0, 0.11, 0.005)
irr_price = st.sidebar.number_input("Irredeemable Bond Price (per £100)", 1.0, 200.0, 70.0, 0.5)
irr_units = st.sidebar.number_input("Irredeemable Bonds (£100 Units)", 0, 10000, 1800, 100)

# Redeemable Bonds
red_coupon = st.sidebar.number_input("Redeemable Bond Coupon", 0.0, 1.0, 0.09, 0.005)
red_price = st.sidebar.number_input("Redeemable Bond Price (per £100)", 1.0, 200.0, 96.0, 0.5)
red_redeem = st.sidebar.number_input("Redeem Value (per £100)", 50.0, 200.0, 100.0, 1.0)
red_years = st.sidebar.number_input("Years to Redemption", 1, 50, 4)
red_units = st.sidebar.number_input("Redeemable Bonds (£100 Units)", 0, 10000, 900, 100)

# Loan
loan_rate = st.sidebar.number_input("Bank Loan Rate", 0.0, 1.0, 0.07, 0.005)
loan_balance = st.sidebar.number_input("Bank Loan Balance (£)", 0, 500000, 70000, 1000)

# ──────────────────────────────────────────────
# Step 1 – Component Cost Calculations
# ──────────────────────────────────────────────
def cost_of_equity(rf, rm, beta): return rf + beta * (rm - rf)
def cost_of_pref(d, p): return d / p
def cost_of_irredeemable(i, p, t): return ((i * 100) / p) * (1 - t)
def cost_of_redeemable(i, r, p, n, t):
    I = i * 100
    return ((I + (r - p) / n) / ((r + p) / 2)) * (1 - t)
def cost_of_loan(i, t): return i * (1 - t)

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
st.subheader("Step 1 – Component Cost Calculations")
st.dataframe(step1, use_container_width=True)

# ──────────────────────────────────────────────
# Step 2 – Capital Structure (Units × Price)
# ──────────────────────────────────────────────
st.subheader("Step 2 – Capital Structure (Units × Price = Cost)")

structure = [
    ["Ordinary Shares (Ke)", eq_units, eq_price],
    ["Preference Shares (Kp)", pref_units, pref_price],
    ["Irredeemable Bonds (Kd₁)", irr_units, irr_price],
    ["Redeemable Bonds (Kd₂)", red_units, red_price],
    ["Bank Loan (Kd₃)", loan_balance, 1.0],
]

df2 = pd.DataFrame(structure, columns=["Source", "Units", "Price"])
df2["Cost"] = df2["Units"] * df2["Price"]
df2["Weighted_Cost"] = df2["Cost"] / df2["Cost"].sum() * 100

st.dataframe(df2, use_container_width=True)

# ──────────────────────────────────────────────
# Step 3 – Weighted Cost Analysis and Totals
# ──────────────────────────────────────────────
st.subheader("Step 3 – Weighted Cost Analysis and Totals")

step3 = pd.merge(step1, df2[["Source", "Weighted_Cost"]], on="Source", how="left")
step3["Weighted_Cost ÷ Cost_%"] = np.round(step3["Weighted_Cost"] / step3["Cost_%"], 4)

# Total WACC
wacc_total = (step3["Weighted_Cost"] / 100 * step3["Cost_%"]).sum()

total_row = pd.DataFrame({
    "Source": ["Total / WACC"],
    "Cost_%": [""],
    "Weighted_Cost": [""],
    "Weighted_Cost ÷ Cost_%": [f"{wacc_total:.2f}%"]
})

step3_display = pd.concat([step3, total_row], ignore_index=True)
st.dataframe(step3_display, use_container_width=True)

st.markdown(f"### ✅ **Overall WACC = {wacc_total:.2f}%**")

st.markdown("""
---
### Interpretation
**Step 1:** Calculates component rates  
**Step 2:** Derives total and weighted capital values from your input data  
**Step 3:** Relates weighted costs to component rates and totals **WACC**
""")

