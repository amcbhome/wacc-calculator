import math
import numpy as np
import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────────────────────
# Page setup
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WACC Calculator",
    layout="centered",           # keep a neat, narrow layout by default
    initial_sidebar_state="expanded"
)

st.title("💸 Weighted Average Cost of Capital (WACC) Calculator")

st.markdown(
    """
This app computes **WACC** with transparent workings.  
Use **CAPM** or **Dividend Growth (Gordon)** for *Cost of Equity*, and supply either a **single pre-tax Cost of Debt**  
or build it from **multiple debt tranches**.

**Formula:**  
\\[
\\text{WACC} = w_E\\,K_E + w_D\\,K_D (1 - T)
\\]
where \(w_E = \\frac{E}{E + D}\) and \(w_D = \\frac{D}{E + D}\\).
"""
)

# ──────────────────────────────────────────────────────────────
# Sidebar — Inputs
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Inputs")

    currency = st.selectbox("Currency", ["£", "$", "€", "Other"], index=0)
    if currency == "Other":
        currency = st.text_input("Custom currency symbol", value="£")

    st.subheader("Capital Structure (Market Values)")
    E = st.number_input("Equity value (E)", min_value=0.0, value=120.0, step=10.0, help="Market value of equity")
    D_mode = st.radio(
        "Debt input",
        ["Single debt value", "Build from tranches"],
        index=0
    )

    tranche_df = None
    if D_mode == "Single debt value":
        D = st.number_input("Debt value (D)", min_value=0.0, value=80.0, step=10.0, help="Market value of interest-bearing debt")
    else:
        st.caption("Enter debt tranches (market value and pre-tax effective rate).")
        default_tranches = pd.DataFrame(
            [
                {"Instrument": "Term Loan", "Market Value": 40.0, "Rate (%)": 6.0, "Tax shield?": True},
                {"Instrument": "Bond 2029", "Market Value": 60.0, "Rate (%)": 5.2, "Tax shield?": True},
            ]
        )
        tranche_df = st.data_editor(
            default_tranches,
            num_rows="dynamic",
            use_container_width=True,
            key="debt_tranches"
        )

    st.subheader("Tax")
    tax_rate = st.number_input("Corporate tax rate (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.25)

    st.subheader("Cost of Equity (K_E)")
    ke_method = st.radio(
        "Choose method",
        ["Manual entry", "CAPM", "Dividend Growth (Gordon)"],
        index=1
    )

    if ke_method == "Manual entry":
        ke_percent = st.number_input("Cost of Equity K_E (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.25)
    elif ke_method == "CAPM":
        st.caption("CAPM:  K_E = R_f + β × (E[R_m] − R_f)")
        rf = st.number_input("Risk-free rate R_f (%)", min_value=-10.0, max_value=100.0, value=3.0, step=0.1)
        beta = st.number_input("Equity beta β", min_value=-5.0, max_value=10.0, value=1.1, step=0.05)
        premium_mode = st.radio("Market input", ["Market risk premium (E[R_m]−R_f)", "Expected market return E[R_m]"], index=0)
        if premium_mode == "Market risk premium (E[R_m]−R_f)":
            mrp = st.number_input("Market risk premium (%)", min_value=-10.0, max_value=50.0, value=5.0, step=0.1)
            ke_percent = rf + beta * mrp
        else:
            erm = st.number_input("Expected market return E[R_m] (%)", min_value=-10.0, max_value=100.0, value=8.0, step=0.1)
            ke_percent = rf + beta * (erm - rf)
    else:
        st.caption("Gordon growth:  K_E = D₁ / P₀ + g")
        D1 = st.number_input("Next year dividend D₁ (in currency)", min_value=0.0, value=4.0, step=0.1)
        P0 = st.number_input("Current price P₀ (in currency)", min_value=0.0001, value=80.0, step=1.0)
        g_percent = st.number_input("Growth rate g (%)", min_value=-50.0, max_value=100.0, value=2.0, step=0.1)
        ke_percent = (D1 / max(P0, 1e-9)) * 100.0 + g_percent  # convert first term to %

    st.subheader("Cost of Debt (K_D)")
    kd_mode = st.radio("Choose K_D input", ["Manual single rate", "From tranches"], index=0)

    if kd_mode == "Manual single rate":
        kd_percent_pre_tax = st.number_input("Pre-tax K_D (%)", min_value=0.0, max_value=100.0, value=5.5, step=0.1)
    else:
        st.caption("Weighted by market value. Tranches marked 'Tax shield?' get the (1−T) adjustment.")
        # This will be computed later from tranche_df

# ──────────────────────────────────────────────────────────────
# Calculations
# ──────────────────────────────────────────────────────────────
def compute_weighted_kd_from_tranches(df: pd.DataFrame, tax_rate_pct: float):
    """
    Returns (pre_tax_kd_pct, after_tax_kd_pct_effective, D_total)
    - pre_tax_kd_pct = Σ(w_i * r_i)
    - after_tax_kd_pct_effective applies tax shield only to rows with Tax shield? == True,
      i.e., Σ(w_i * r_i * (1−T_i)) with T_i either tax rate or 0 per row.
    """
    if df is None or df.empty:
        return 0.0, 0.0, 0.0

    df = df.copy()
    df["Market Value"] = pd.to_numeric(df["Market Value"], errors="coerce").fillna(0.0)
    df["Rate (%)"] = pd.to_numeric(df["Rate (%)"], errors="coerce").fillna(0.0)
    df["Tax shield?"] = df["Tax shield?"].fillna(True)

    total = df["Market Value"].sum()
    if total <= 0:
        return 0.0, 0.0, 0.0

    df["weight"] = df["Market Value"] / total
    pre_tax_kd = (df["weight"] * df["Rate (%)"]).sum()

    # Per-row tax shield
    tax_shield_factor = np.where(df["Tax shield?"].values, (1 - tax_rate_pct / 100.0), 1.0)
    after_tax_kd = (df["weight"] * df["Rate (%)"] * tax_shield_factor).sum()

    return float(pre_tax_kd), float(after_tax_kd), float(total)

# Determine D, Kd
if D_mode == "Build from tranches":
    pre_kd_from_tranches, post_kd_from_tranches, D_calc = compute_weighted_kd_from_tranches(tranche_df, tax_rate)
    D = D_calc
else:
    pre_kd_from_tranches = None
    post_kd_from_tranches = None

if kd_mode == "From tranches":
    kd_percent_pre_tax = pre_kd_from_tranches or 0.0
    kd_percent_after_tax_effective = post_kd_from_tranches or 0.0
else:
    kd_percent_after_tax_effective = kd_percent_pre_tax * (1 - tax_rate / 100.0)

# Weights
V = E + D
wE = (E / V) if V > 0 else 0.0
wD = (D / V) if V > 0 else 0.0

# WACC
if kd_mode == "From tranches":
    # Already applied row-level tax shields in kd_percent_after_tax_effective
    wacc = wE * (ke_percent / 100.0) + wD * (kd_percent_after_tax_effective / 100.0)
else:
    wacc = wE * (ke_percent / 100.0) + wD * (kd_percent_pre_tax / 100.0) * (1 - tax_rate / 100.0)

# ──────────────────────────────────────────────────────────────
# Output — Metrics and workings
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("Results")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("WACC", f"{wacc*100:.2f} %")
col2.metric("Cost of Equity (K_E)", f"{ke_percent:.2f} %")
col3.metric("Cost of Debt (pre-tax K_D)", f"{kd_percent_pre_tax:.2f} %")
if kd_mode == "From tranches":
    col4.metric("Cost of Debt (after-tax, effective)", f"{kd_percent_after_tax_effective:.2f} %")
else:
    col4.metric("Cost of Debt (after-tax)", f"{kd_percent_after_tax_effective:.2f} %")
col5.metric("Tax rate", f"{tax_rate:.2f} %")

st.caption("Weights by market value")
c1, c2, c3 = st.columns(3)
c1.metric("Equity weight w_E", f"{wE:.4f}")
c2.metric("Debt weight w_D", f"{wD:.4f}")
c3.metric("Total capital (E + D)", f"{currency}{V:,.2f}")

# Workings detail
with st.expander("Show detailed workings"):
    if ke_method == "CAPM":
        if 'mrp' in locals():
            st.write(f"**CAPM**:  K_E = R_f + β × MRP = {rf:.2f}% + {beta:.2f} × {mrp:.2f}% = **{ke_percent:.2f}%**")
        else:
            st.write(f"**CAPM**:  K_E = R_f + β × (E[R_m]−R_f) = {rf:.2f}% + {beta:.2f} × ({erm:.2f}%−{rf:.2f}%) = **{ke_percent:.2f}%**")
    elif ke_method == "Dividend Growth (Gordon)":
        st.write(
            f"**Gordon**:  K_E = D₁/P₀ + g = {currency}{D1:.2f}/{currency}{P0:.2f} + {g_percent:.2f}% = **{ke_percent:.2f}%**"
        )
    else:
        st.write(f"**Manual K_E** provided: **{ke_percent:.2f}%**")

    if D_mode == "Build from tranches":
        st.write("**Debt tranches (market-value weights):**")
        show_df = tranche_df.copy()
        # add weights preview
        if D > 0:
            show_df["Weight"] = show_df["Market Value"] / D
        st.dataframe(show_df, use_container_width=True)
        st.write(
            f"Pre-tax weighted K_D = **{kd_percent_pre_tax:.2f}%**; "
            + ("Row-level after-tax effective K_D = **{:.2f}%**".format(kd_percent_after_tax_effective)
               if kd_mode == "From tranches" else "")
        )
    else:
        st.write(f"Debt value (D) = {currency}{D:,.2f}  |  Pre-tax K_D = **{kd_percent_pre_tax:.2f}%**")

    st.latex(r"""
    \text{WACC} = w_E K_E + w_D K_D (1 - T)
    """)
    if kd_mode == "From tranches":
        st.write(
            f"Using row-level tax shields:  WACC = {wE:.4f} × {ke_percent:.2f}% + "
            f"{wD:.4f} × {kd_percent_after_tax_effective:.2f}% = **{wacc*100:.2f}%**"
        )
    else:
        st.write(
            f"WACC = {wE:.4f} × {ke_percent:.2f}% + {wD:.4f} × {kd_percent_pre_tax:.2f}% × (1−{tax_rate:.2f}%) "
            f"= **{wacc*100:.2f}%**"
        )

# Download summary
summary = {
    "currency": currency,
    "Equity_E": E,
    "Debt_D": D,
    "wE": wE,
    "wD": wD,
    "Ke_percent": ke_percent,
    "Kd_percent_pre_tax": kd_percent_pre_tax,
    "Kd_percent_after_tax_effective": kd_percent_after_tax_effective,
    "tax_rate_percent": tax_rate,
    "WACC_percent": wacc * 100.0,
    "Ke_method": ke_method,
    "Kd_method": kd_mode,
}
summary_df = pd.DataFrame([summary])
csv = summary_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download summary (CSV)",
    csv,
    file_name="wacc_summary.csv",
    mime="text/csv",
    use_container_width=True
)

st.caption("Tip: Save different scenarios as separate CSVs to compare across projects.")
