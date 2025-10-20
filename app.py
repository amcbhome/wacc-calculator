# app.py — Full WACC Model with Step 1 Cost Calculations + Step 2 Structure + Step 3 WACC
# Author: A. McBride | GPT-5 | Oct 2025

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="💸 Weighted Average Cost of Capital (WACC) Calculator",
                   layout="centered")

st.title("💸 Weighted Average Cost of Capital (WACC) Calculator")

st.markdown("""
This version follows the textbook three-step process:

1️⃣ **Calculate component costs** (Equity, Prefs, Irredeemable, Redeemable, Loan)  
2️⃣ **Build capital structure** using Units × Price and computed costs  
3️⃣ **Compute WACC**
""")

# ──────────────────────────────────────────────
# Functions
# ──────────────────────────────────────────────
def cost_of_equity(rf, rm, beta):
    return rf + beta * (rm - rf)

def cost_of_pref(div_per_share, price_per_share):
    return div_per_share / price_per_share

def cost_of_irredeemable(coupon_rate, price_per_100, tax):
    pretax = (coupon_rate * 100.0) / price_per_100
    return pretax * (1.0 - tax)

def cost_of_redeemable(coupon_rate, redeem_per_100, price_per_100, years, tax):
    I = coupon_rate * 100.0
    pretax = (I + (redeem_per_100 - price_per_100) / years) / ((redeem_per_100 + price_per_100) / 2.0)
    return pretax * (1.0 - tax)

def cost_of_loan(rate, tax):
    return rate * (1.0 - tax)

# ──────────────────────────────────────────────
# Sidebar Global Inputs
# ──────────────────────────────────────────────
st.sidebar.header("Global Parameters")

rf = st.sidebar.number_input("Risk-Free Rate (Rf)", 0.0, 1.0, 0.05, 0.005)
rm = st.sidebar.number_input("Market Return (Rm)", 0.0, 1.0, 0.11, 0.005)
tax = st.sidebar.number_input("Corporation Tax Rate", 0.0, 1.0, 0.30, 0.01)
beta = st.sidebar.number_input("Equity Beta (β)", 0.0, 5.0, 1.5, 0.1)

st.sidebar.markdown("---")
st.sidebar.caption("Adjust parameters to recompute component costs.")

# ──────────────────────────────────────────────
# STEP 1 – Component Cost Calculations
# ──────────────────────────────────────────────
st.subheader("Step 1 – Calculate Component Costs")

col1, col2, col3 = st.columns(3)
with col1:
    pref_div = st.number_input("Pref Dividend per £1", 0.0, 1.0, 0.10, 0.01)
    pref_price = st.number_input("Pref Share Price (£)", 0.1, 10.0, 0.89, 0.01)
    kd_loan_rate = st.number_input("Bank Loan Interest Rate", 0.0, 1.0, 0.07, 0.005)
with col2:
    kd_ir_coupon = st.number_input("Irredeemable Bond Coupon", 0.0, 1.0, 0.11, 0.005)
    kd_ir_price = st.number_input("Irredeemable Bond Price (£ per 100)", 1.0, 200.0, 70.0, 0.5)
    kd_red_coupon = st.number_input("Redeemable Bond Coupon", 0.0, 1.0, 0.09, 0.005)
with col3:
    kd_red_price = st.number_input("Redeemable Bond Price (£ per 100)", 1.0, 200.0, 96.0, 0.5)
    kd_red_redeem = st.number_input("Redeem Value (£ per 100)", 50.0, 200.0, 100.0, 1.0)
    kd_red_years = st.number_input("Years to Redemption", 1, 50, 4)

# Compute each cost
ke = cost_of_equity(rf, rm, beta) * 100
kp = cost_of_pref(pref_div, pref_price) * 100
kd_ir = cost_of_irredeemable(kd_ir_coupon, kd_ir_price, tax) * 100
kd_red = cost_of_redeemable(kd_red_coupon, kd_red_redeem, kd_red_price, kd_red_years, tax) * 100
kd_loan = cost_of_loan(kd_loan_rate, tax) * 100

costs_df = pd.DataFrame({
    "Source": [
        "Ordinary Shares (Ke)", "Preference Shares (Kp)",
        "Irredeemable Bonds (Kd₁)", "Redeemable Bonds (Kd₂)", "Bank Loan (Kd₃)"
    ],
    "Formula": [
        "Rf + β(Rm–Rf)", "D / P₀", "i(1–T)/P₀", "[I + (R–P)/n]/[(R+P)/2] × (1–T)", "i(1–T)"
    ],
    "Cost_%": [round(ke,2), round(kp,2), round(kd_ir,2), round(kd_red,2), round(kd_loan,2)]
})

st.dataframe(costs_df, use_container_width=True)
st.caption("💡 These component costs feed automatically into Step 2.")

# ──────────────────────────────────────────────
# STEP 2 – Capital Structure Input
# ──────────────────────────────────────────────
st.subheader("Step 2 – Input Capital Structure (Units × Price + Cost %)")

structure = [
    ["Ordinary Shares", "equity", 260000, 1.90, round(ke,2)],
    ["Preference Shares", "pref", 90000, 0.89, round(kp,2)],
    ["Irredeemable Bonds", "bond_irredeemable", 1800, 70.0, round(kd_ir,2)],
    ["Redeemable Bonds", "bond_redeemable", 900, 96.0, round(kd_red,2)],
    ["Bank Loan", "loan", 70000, 1.0, round(kd_loan,2)],
]
cols = ["Source","Type","Units","Price","Cost_%"]
df_in = pd.DataFrame(structure, columns=cols)

edited_df = st.data_editor(df_in, num_rows="fixed", use_container_width=True)
st.caption("💡 Adjust Units, Prices, or override any Cost % to test sensitivities.")

# ──────────────────────────────────────────────
# STEP 3 – Weighted Average Cost of Capital
# ──────────────────────────────────────────────
st.subheader("Step 3 – WACC Calculation")

df = edited_df.copy()
df["Market_Value"] = df["Units"] * df["Price"]
df["Weight"] = df["Market_Value"] / df["Market_Value"].sum()
df["Weighted_Cost_%"] = df["Weight"] * df["Cost_%"]

total_mv = df["Market_Value"].sum()
wacc = df["Weighted_Cost_%"].sum()

st.dataframe(df[["Source","Cost_%","Market_Value","Weight","Weighted_Cost_%"]],
             use_container_width=True)

col1, col2 = st.columns(2)
col1.metric("Total Market Value", f"£{total_mv:,.0f}")
col2.metric("Weighted Average Cost of Capital", f"{wacc:.2f}%")

st.markdown("""
---
### Formulae
- **Equity:** \( K_e = R_f + β(R_m - R_f) \)
- **Preference:** \( K_p = D / P₀ \)
- **Irredeemable debt:** \( K_d = (i×100/P₀)(1–T) \)
- **Redeemable debt:** \( K_d = [I + (R–P)/n]/[(R+P)/2](1–T) \)
- **Loan:** \( K_d = i(1–T) \)
- **WACC:** \( \text{WACC} = \sum w_i K_i \)
""")

st.caption("Generated dynamically from user inputs. Project supervised by A. McBride.")
