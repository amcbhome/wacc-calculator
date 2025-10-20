# app.py — Dynamic WACC Three-Step Model (with dual-column inputs + Calculate button)
# Author: A. McBride | GPT-5 | Oct 2025

import streamlit as st
import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Page Setup
# ──────────────────────────────────────────────
st.set_page_config(page_title="💸 WACC Three-Step Model", layout="wide")
st.title("💸 Weighted Average Cost of Capital (WACC) — Dynamic Three-Step Model")

st.markdown("""
This model calculates **WACC** interactively from your data.  
Follow the three steps below and click **Calculate** to update results.
""")

# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────
def cost_of_equity(rf, rm, beta): return rf + beta * (rm - rf)
def cost_of_pref(d, p): return d / p
def cost_of_irredeemable(i, p, t): return ((i * 100) / p) * (1 - t)
def cost_of_redeemable(i, r, p, n, t):
    I = i * 100
    return ((I + (r - p) / n) / ((r + p) / 2)) * (1 - t)
def cost_of_loan(i, t): return i * (1 - t)

# ──────────────────────────────────────────────
# Sidebar — Input Data
# ──────────────────────────────────────────────
st.sidebar.header("Input Data")

# Market parameters
st.sidebar.subheader("Market & Financial Parameters")
rf = st.sidebar.number_input("Risk-Free Rate (Rf)", 0.0, 1.0, 0.05, 0.005)
rm = st.sidebar.number_input("Market Return (Rm)", 0.0, 1.0, 0.11, 0.005)
tax = st.sidebar.number_input("Corporation Tax Rate (T)", 0.0, 1.0, 0.30, 0.01)
beta = st.sidebar.number_input("Equity Beta (β)", 0.0, 5.0, 1.5, 0.1)

st.sidebar.subheader("Instruments (Units & Price)")

# Create two side-by-side input columns inside sidebar
col_units, col_price = st.sidebar.columns(2)

with col_units:
    eq_units = st.number_input("Ordinary Shares", 0, 1000000, 260000, 1000)
    pref_units = st.number_input("Pref. Shares", 0, 500000, 90000, 1000)
    irr_units = st.number_input("Irredeemable Bonds", 0, 10000, 1800, 100)
    red_units = st.number_input("Redeemable Bonds", 0, 10000, 900, 100)
    loan_balance = st.number_input("Loan (£)", 0, 500000, 70000, 1000)

with col_price:
    eq_price = st.number_input("£/Share", 0.01, 10.0, 1.90, 0.01)
    pref_price = st.number_input("£/Pref", 0.01, 10.0, 0.89, 0.01)
    irr_price = st.number_input("£/100", 1.0, 200.0, 70.0, 0.5)
    red_price = st.number_input("£/100", 1.0, 200.0, 96.0, 0.5)
    loan_rate = st.number_input("Loan Rate", 0.0, 1.0, 0.07, 0.005)

# Additional bond and pref inputs
st.sidebar.subheader("Other Inputs")
pref_div = st.sidebar.number_input("Pref Dividend per £1", 0.0, 1.0, 0.10, 0.01)
irr_coupon = st.sidebar.number_input("Irredeemable Bond Coupon", 0.0, 1.0, 0.11, 0.005)
red_coupon = st.sidebar.number_input("Redeemable Bond Coupon", 0.0, 1.0, 0.09, 0.005)
red_redeem = st.sidebar.number_input("Redeem Value (per £100)", 50.0, 200.0, 100.0, 1.0)
red_years = st.sidebar.number_input("Years to Redemption", 1, 50, 4)

# Green calculate button
calculate = st.sidebar.button("✅ Calculate WACC", type="primary")

# ──────────────────────────────────────────────
# CALCULATION LOGIC
# ──────────────────────────────────────────────
if calculate:
    try:
        # Step 1: Component Costs
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

        # Step 2: Capital Structure
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

        if df2["Cost"].sum() == 0:
            st.error("⚠️ Total capital value cannot be zero. Please enter valid Units and Prices.")
        else:
            df2["Weighted_Cost"] = df2["Cost"] / df2["Cost"].sum() * 100
            st.dataframe(df2, use_container_width=True)

            # Step 3: Combine + WACC
            st.subheader("Step 3 – Weighted Cost Analysis and Totals")
            step3 = pd.merge(step1, df2[["Source", "Weighted_Cost"]], on="Source", how="left")
            step3["Weighted_Cost ÷ Cost_%"] = np.round(step3["Weighted_Cost"] / step3["Cost_%"], 4)
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
    except Exception as e:
        st.error(f"⚠️ An error occurred during calculation: {e}")
else:
    st.info("Enter input values and click **Calculate WACC** to begin.")

