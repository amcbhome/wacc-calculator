import math
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# Page setup
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WACC Calculator (Academic Version)",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("💸 Weighted Average Cost of Capital (WACC) Calculator")
st.markdown("""
This app reproduces the **WACC model** from the accompanying LaTeX report.  
It supports both *CAPM* and *Dividend Growth (Gordon)* models for the **Cost of Equity**,  
and allows for **multi-tranche debt** to compute weighted cost of debt.

### Formulae
\\[
\\text{WACC} = \\frac{E}{V}K_E + \\frac{D}{V}K_D(1-T)
\\quad \\text{where} \\quad V = E + D
\\]
""")

# ──────────────────────────────────────────────────────────────
# Sidebar Inputs
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Input Parameters")

    currency = st.selectbox("Currency", ["£", "$", "€", "Other"], index=0)
    if currency == "Other":
        currency = st.text_input("Custom symbol", value="£")

    st.subheader("Capital Structure")
    E = st.number_input("Equity value (E)", min_value=0.0, value=120.0, step=10.0)
    D_mode = st.radio("Debt input", ["Single value", "Multiple tranches"], index=0)

    tranche_df = None
    if D_mode == "Single value":
        D = st.number_input("Debt value (D)", min_value=0.0, value=80.0, step=10.0)
    else:
        default_tranches = pd.DataFrame([
            {"Instrument": "Loan", "Market Value": 40.0, "Rate (%)": 6.0, "Tax shield?": True},
            {"Instrument": "Bond 2029", "Market Value": 60.0, "Rate (%)": 5.2, "Tax shield?": True},
        ])
        tranche_df = st.data_editor(default_tranches, num_rows="dynamic", use_container_width=True)
        D = tranche_df["Market Value"].sum()

    tax_rate = st.number_input("Corporate tax rate (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.25)

    st.subheader("Cost of Equity (Kₑ)")
    ke_method = st.radio("Method", ["Manual", "CAPM", "Dividend Growth (Gordon)"], index=1)

    if ke_method == "Manual":
        ke_percent = st.number_input("Kₑ (%)", value=10.0, step=0.25)
    elif ke_method == "CAPM":
        st.caption("CAPM:  Kₑ = R_f + β × (E[Rₘ] − R_f)")
        rf = st.number_input("Risk-free rate R_f (%)", value=3.0, step=0.1)
        beta = st.number_input("Equity beta β", value=1.1, step=0.05)
        mrp = st.number_input("Market risk premium (%)", value=5.0, step=0.1)
        ke_percent = rf + beta * mrp
    else:
        st.caption("Gordon growth:  Kₑ = D₁ / P₀ + g")
        D1 = st.number_input("Next dividend D₁", value=4.0, step=0.1)
        P0 = st.number_input("Current price P₀", value=80.0, step=1.0)
        g_percent = st.number_input("Growth rate g (%)", value=2.0, step=0.1)
        ke_percent = (D1 / max(P0, 1e-9)) * 100 + g_percent

    st.subheader("Cost of Debt (K_d)")
    kd_mode = st.radio("Input", ["Single rate", "From tranches"], index=0)
    kd_percent_pre_tax = st.number_input("Pre-tax K_d (%)", value=5.5, step=0.1)

# ──────────────────────────────────────────────────────────────
# Computation Functions
# ──────────────────────────────────────────────────────────────
def compute_weighted_kd(df, tax_rate_pct):
    if df is None or df.empty:
        return 0.0, 0.0, 0.0
    df["Market Value"] = pd.to_numeric(df["Market Value"], errors="coerce").fillna(0.0)
    df["Rate (%)"] = pd.to_numeric(df["Rate (%)"], errors="coerce").fillna(0.0)
    total = df["Market Value"].sum()
    if total <= 0:
        return 0.0, 0.0, 0.0
    df["weight"] = df["Market Value"] / total
    pre_tax_kd = (df["weight"] * df["Rate (%)"]).sum()
    after_tax_kd = (df["weight"] * df.apply(lambda r: r["Rate (%)"] * (1 - tax_rate_pct/100) if r["Tax shield?"] else r["Rate (%)"], axis=1)).sum()
    return pre_tax_kd, after_tax_kd, total

if kd_mode == "From tranches" and tranche_df is not None:
    kd_percent_pre_tax, kd_percent_after_tax, D = compute_weighted_kd(tranche_df, tax_rate)
else:
    kd_percent_after_tax = kd_percent_pre_tax * (1 - tax_rate / 100)

V = E + D
wE = E / V if V else 0
wD = D / V if V else 0
wacc = wE * (ke_percent / 100) + wD * (kd_percent_after_tax / 100)

# ──────────────────────────────────────────────────────────────
# Output
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("📊 Results")

col1, col2, col3 = st.columns(3)
col1.metric("WACC", f"{wacc*100:.2f}%")
col2.metric("Cost of Equity Kₑ", f"{ke_percent:.2f}%")
col3.metric("After-Tax Cost of Debt K_d", f"{kd_percent_after_tax:.2f}%")

st.caption(f"Weighted by market values:  wₑ = {wE:.2f},  w_d = {wD:.2f},  V = {currency}{V:,.2f}")

with st.expander("Show workings and formulae"):
    st.latex(r"\text{WACC} = \frac{E}{V}K_E + \frac{D}{V}K_D(1 - T)")
    st.write(f"WACC = {wE:.4f} × {ke_percent:.2f}% + {wD:.4f} × {kd_percent_after_tax:.2f}% = **{wacc*100:.2f}%**")

# ──────────────────────────────────────────────────────────────
# Download
# ──────────────────────────────────────────────────────────────
summary = {
    "Currency": currency,
    "Equity (E)": E,
    "Debt (D)": D,
    "wE": wE,
    "wD": wD,
    "K_E (%)": ke_percent,
    "K_D (after-tax %)": kd_percent_after_tax,
    "Tax rate (%)": tax_rate,
    "WACC (%)": wacc * 100,
    "Method_Equity": ke_method,
    "Method_Debt": kd_mode,
    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}
csv = pd.DataFrame([summary]).to_csv(index=False).encode("utf-8")

st.download_button("⬇️ Download Summary (CSV)", csv, file_name="wacc_results.csv", use_container_width=True)
st.markdown("---")
st.caption("Generated by AI (ChatGPT) under supervision of A. McBride — academic version (LaTeX-aligned)")

