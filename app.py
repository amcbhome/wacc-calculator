# app.py — WACC Data Model (Dynamic Recalculation, corrected Units × Price logic)
# Author: A. McBride | Generated with GPT-5 | Oct 2025

import streamlit as st
import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Page Setup
# ──────────────────────────────────────────────
st.set_page_config(page_title="💸 Weighted Average Cost of Capital (WACC) Calculator",
                   layout="centered")

st.title("💸 Weighted Average Cost of Capital (WACC) Calculator")

st.markdown("""
This app calculates **WACC** dynamically from **market values** (Units × Price).
- **Equity/Prefs:** Units = number of shares, Price = price per share.
- **Bonds:** Units = number of £100 bonds, Price = price per £100 nominal.
- **Loan:** Units = loan balance, Price = 1.

Costs:
- **Equity (CAPM):** \(K_e = R_f + \beta (R_m - R_f)\)
- **Prefs:** \(K_p = D / P_0\)
- **Irredeemable debt:** \(K_d = \frac{i \times 100}{P_0} (1-T)\)
- **Redeemable debt:** \(K_d = \frac{I + \frac{R-P}{n}}{\frac{R+P}{2}} (1-T)\), with \(I=i\times100\)
""")

# ──────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────
def cost_of_equity(rf, rm, beta):
    return rf + beta * (rm - rf)

def cost_of_pref(div_per_share, price_per_share):
    return div_per_share / price_per_share

def cost_of_irredeemable(coupon_rate, price_per_100, tax):
    # coupon_rate given as decimal of nominal (e.g., 0.11). Price quoted per £100.
    pretax = (coupon_rate * 100.0) / price_per_100
    return pretax * (1.0 - tax)

def cost_of_redeemable(coupon_rate, redeem_per_100, price_per_100, years, tax):
    # All per £100 terms; coupon_rate as decimal of nominal (e.g., 0.09).
    I = coupon_rate * 100.0
    pretax = (I + (redeem_per_100 - price_per_100) / years) / ((redeem_per_100 + price_per_100) / 2.0)
    return pretax * (1.0 - tax)

def cost_of_loan(rate, tax):
    return rate * (1.0 - tax)

def recalc(df, params):
    rf, rm, tax = params["risk_free_rate"], params["market_return"], params["tax_rate"]
    out = df.copy()

    costs = []
    for _, r in out.iterrows():
        t = r["Type"]
        if t == "equity":
            c = cost_of_equity(rf, rm, r["Beta"])
        elif t == "pref":
            c = cost_of_pref(r["Dividend"], r["Price"])
        elif t == "bond_irredeemable":
            c = cost_of_irredeemable(r["Coupon_rate"], r["Price"], tax)
        elif t == "bond_redeemable":
            c = cost_of_redeemable(r["Coupon_rate"], r["Redeem"], r["Price"], r["Years"], tax)
        elif t == "loan":
            c = cost_of_loan(r["Rate"], tax)
        else:
            c = np.nan
        costs.append(c)

    out["Cost_%"] = np.round(np.array(costs) * 100.0, 2)

    # Market value = Units × Price (loan uses Units as balance and Price=1)
    out["Market_Value"] = out["Units"] * out["Price"]
    total_mv = out["Market_Value"].sum()
    out["Weight"] = out["Market_Value"] / total_mv
    out["Weighted_Cost_%"] = np.round(out["Weight"] * out["Cost_%"], 2)

    wacc = float(out["Weighted_Cost_%"].sum())
    return out, wacc, total_mv

# ──────────────────────────────────────────────
# Sidebar Inputs
# ──────────────────────────────────────────────
st.sidebar.header("Global Parameters")
rf = st.sidebar.number_input("Risk-Free Rate (Rf)", 0.0, 1.0, 0.05, 0.005)
rm = st.sidebar.number_input("Market Return (Rm)", 0.0, 1.0, 0.11, 0.005)
tax = st.sidebar.number_input("Corporation Tax Rate", 0.0, 1.0, 0.30, 0.01)
params = {"risk_free_rate": rf, "market_return": rm, "tax_rate": tax}

st.sidebar.markdown("---")
st.sidebar.write("Edit any table value; WACC updates instantly.")

# ──────────────────────────────────────────────
# Step 1 – Input Capital Structure (Units × Price)
# ──────────────────────────────────────────────
# Columns:
# Source, Type, Units, Price, Coupon_rate, Dividend, Rate, Redeem, Years, Beta
default_data = [
    # Equity: Units=number of shares, Price=£/share, Dividend ignored, Coupon_rate ignored
    ["Ordinary Shares",   "equity",            260000, 1.90, None, None, None, None, None, 1.5],
    # Prefs: Dividend per share provided; Units & Price per share used
    ["Preference Shares", "pref",               90000, 0.89, None, 0.10, None, None, None, None],
    # Irredeemable bonds: Units=number of £100 bonds; Price per £100; coupon_rate decimal
    ["Irredeemable Bonds","bond_irredeemable",   1800, 70.0, 0.11, None, None, None, None, None],
    # Redeemable bonds (4y to redeem at £100): Units, Price per £100, coupon_rate decimal
    ["Redeemable Bonds",  "bond_redeemable",     900, 96.0, 0.09, None, None, 100.0, 4, None],
    # Bank loan: Units = outstanding balance; Price=1; Rate is loan interest
    ["Bank Loan",         "loan",              70000, 1.0,  None, None, 0.07, None, None, None],
]

cols = ["Source","Type","Units","Price","Coupon_rate","Dividend","Rate","Redeem","Years","Beta"]
df_in = pd.DataFrame(default_data, columns=cols)

st.subheader("Step 1 – Input Capital Structure (Units × Price)")
edited = st.data_editor(df_in, num_rows="fixed", use_container_width=True)
st.caption("💡 Equity/Prefs: Units = shares; Bonds: Units = number of £100 bonds; Loan: Units = balance, Price=1.")

# ──────────────────────────────────────────────
# Step 2 – Calculated Costs & Weights
# ──────────────────────────────────────────────
df_out, wacc, total_mv = recalc(edited, params)

st.subheader("Step 2 – Calculated Costs and Weights")
show_cols = ["Source","Cost_%","Market_Value","Weight","Weighted_Cost_%"]
st.dataframe(df_out[show_cols], use_container_width=True)

# ──────────────────────────────────────────────
# Step 3 – Results Summary
# ──────────────────────────────────────────────
st.subheader("Step 3 – WACC Summary")
c1, c2 = st.columns(2)
c1.metric("Total Market Value", f"£{total_mv:,.0f}")
c2.metric("Weighted Average Cost of Capital", f"{wacc:.2f}%")

st.markdown("""
---
### Formulae
- **Equity:** \( K_e = R_f + \beta (R_m - R_f) \)  
- **Prefs:** \( K_p = D / P_0 \)  
- **Irredeemable debt:** \( K_d = \frac{i \cdot 100}{P_0}(1-T) \)  
- **Redeemable debt:** \( K_d = \frac{I + \frac{R - P}{n}}{\frac{R + P}{2}}(1-T) \) where \( I = i \cdot 100 \)  
- **WACC:** \( \text{WACC} = \sum w_i K_i \)
""")

st.caption("Generated dynamically from user inputs. Project supervised by A. McBride.")

