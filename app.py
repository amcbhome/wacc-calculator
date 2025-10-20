# app.py — WACC Data Model (Dynamic Recalculation)
# Author: A. McBride | Generated with GPT-5 | October 2025

import streamlit as st
import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Page Setup
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="💸 Weighted Average Cost of Capital (WACC) Calculator",
    layout="centered"
)

st.title("💸 Weighted Average Cost of Capital (WACC) Calculator")

st.markdown("""
This app calculates **WACC** dynamically.  
It uses the **CAPM** model for the cost of equity, the **Dividend/Price** model for preference shares,  
and the **Bond Yield models** for debt instruments.

Edit parameters or table values below — results update instantly.
""")

# ──────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────
def cost_of_equity(rf, rm, beta):
    return rf + beta * (rm - rf)

def cost_of_pref(div, price):
    return div / price

def cost_of_irredeemable(coupon, price, tax):
    return (coupon / price) * (1 - tax)

def cost_of_redeemable(coupon, redeem, price, years, tax):
    return ((coupon + (redeem - price) / years) / ((redeem + price) / 2)) * (1 - tax)

def cost_of_loan(rate, tax):
    return rate * (1 - tax)

def recalc(df, params):
    rf, rm, tax = params["risk_free_rate"], params["market_return"], params["tax_rate"]
    df = df.copy()

    costs = []
    for _, row in df.iterrows():
        t = row["Type"]
        if t == "equity":
            c = cost_of_equity(rf, rm, row["Beta"])
        elif t == "pref":
            c = cost_of_pref(row["Coupon"], row["Price"])
        elif t == "bond_irredeemable":
            c = cost_of_irredeemable(row["Coupon"], row["Price"], tax)
        elif t == "bond_redeemable":
            c = cost_of_redeemable(row["Coupon"], row["Redeem"], row["Price"], row["Years"], tax)
        elif t == "loan":
            c = cost_of_loan(row["Coupon"], tax)
        else:
            c = np.nan
        costs.append(c)

    df["Cost_%"] = np.round(np.array(costs) * 100, 2)
    df["Market_Value"] = np.where(df["Price"].notna(), df["Nominal"] * df["Price"], df["Nominal"])
    df["Weight"] = df["Market_Value"] / df["Market_Value"].sum()
    df["Weighted_Cost_%"] = np.round(df["Weight"] * df["Cost_%"], 2)
    wacc = np.sum(df["Weighted_Cost_%"])
    return df, wacc

# ──────────────────────────────────────────────
# Sidebar Inputs
# ──────────────────────────────────────────────
st.sidebar.header("Global Parameters")

rf = st.sidebar.number_input("Risk-Free Rate (Rf)", 0.0, 1.0, 0.05, 0.005)
rm = st.sidebar.number_input("Market Return (Rm)", 0.0, 1.0, 0.11, 0.005)
tax = st.sidebar.number_input("Corporation Tax Rate", 0.0, 1.0, 0.30, 0.01)

params = {"risk_free_rate": rf, "market_return": rm, "tax_rate": tax}

st.sidebar.markdown("---")
st.sidebar.write("Edit any table cell or parameter to recalculate automatically.")

# ──────────────────────────────────────────────
# Step 1 – Base Data
# ──────────────────────────────────────────────
default_data = [
    ["Ordinary Shares", "equity", 130000, 1.90, None, None, None, 1.5],
    ["Preference Shares", "pref", 90000, 0.89, 0.10, None, None, None],
    ["Irredeemable Bonds", "bond_irredeemable", 180000, 70, 0.11, None, None, None],
    ["Redeemable Bonds", "bond_redeemable", 90000, 96, 0.09, 100, 4, None],
    ["Bank Loan", "loan", 70000, None, 0.07, None, None, None],
]

cols = ["Source", "Type", "Nominal", "Price", "Coupon", "Redeem", "Years", "Beta"]
df = pd.DataFrame(default_data, columns=cols)

st.subheader("Step 1 – Input Capital Structure")

# Editable data table (compatible version)
edited_df = st.data_editor(df, num_rows="fixed", use_container_width=True)

st.caption("💡 Tip: Adjust any value to see the WACC recalculate automatically.")

# ──────────────────────────────────────────────
# Step 2 – Recalculation
# ──────────────────────────────────────────────
df_out, wacc = recalc(edited_df, params)

st.subheader("Step 2 – Calculated Costs and Weights")
st.dataframe(
    df_out[["Source", "Cost_%", "Market_Value", "Weight", "Weighted_Cost_%"]],
    use_container_width=True
)

# ──────────────────────────────────────────────
# Step 3 – Results Summary
# ──────────────────────────────────────────────
st.subheader("Step 3 – WACC Summary")

col1, col2 = st.columns(2)
col1.metric("Total Market Value", f"£{df_out['Market_Value'].sum():,.0f}")
col2.metric("Weighted Average Cost of Capital", f"{wacc:.2f}%")

st.markdown("""
---
### Notes
- **Cost of Equity:** \( K_e = R_f + \beta (R_m - R_f) \)  
- **Cost of Preference Shares:** \( K_p = D / P_0 \)  
- **Cost of Irredeemable Debt:** \( K_d = i(1 - T) / P_0 \)  
- **Cost of Redeemable Debt:** \( K_d = \frac{I + (R - P)/n}{(R + P)/2} (1 - T) \)  
- **WACC:** \( \text{WACC} = \sum w_i K_i \)
""")

st.caption("Generated dynamically from user inputs. Project supervised by A. McBride.")
