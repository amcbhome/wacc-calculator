import streamlit as st
import pandas as pd

# ──────────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────────
st.set_page_config(page_title="WACC Calculator", page_icon="🧮")

st.title("🧮 WACC Calculator")

st.write("""
This calculator determines the Weighted Average Cost of Capital (WACC) using the equity and debt structure of a company.
Enter the values below and view the calculated results instantly.
""")

# ──────────────────────────────────────────────
# Inputs
# ──────────────────────────────────────────────
st.subheader("Inputs")

equity_value = st.number_input("Equity Value (£)", min_value=0.0, value=12000.0)
debt_value = st.number_input("Debt Value (£)", min_value=0.0, value=2000.0)
cost_of_equity = st.number_input("Cost of Equity (%)", min_value=0.0, value=10.0, step=0.1)
cost_of_debt = st.number_input("Cost of Debt (%)", min_value=0.0, value=6.7, step=0.1)
tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=25.0)

# Convert %
cost_of_equity /= 100
cost_of_debt /= 100
tax_rate /= 100

# CAPM information (info only)
with st.expander("📌 How is Cost of Equity normally calculated? (CAPM)"):
    st.write("""
The **Cost of Equity** often uses the **Capital Asset Pricing Model (CAPM)**:

**Re = Rf + β × (Rm − Rf)**  

• **Rf** = Risk-free rate (e.g., UK Gilt yield)  
• **β (beta)** = Company volatility vs. market  
• **Rm − Rf** = Market risk premium  

Your input above can be based on CAPM if known.
""")

# ──────────────────────────────────────────────
# WACC Calculation
# ──────────────────────────────────────────────
total_value = equity_value + debt_value

equity_weight = equity_value / total_value
debt_weight = debt_value / total_value

weighted_cost_equity = equity_weight * cost_of_equity
weighted_cost_debt = debt_weight * cost_of_debt * (1 - tax_rate)

wacc = weighted_cost_equity + weighted_cost_debt

# ──────────────────────────────────────────────
# Results DataFrame
# ──────────────────────────────────────────────
wacc_df = pd.DataFrame({
    "Type": ["Equity", "Debt"],
    "Amount (£)": [equity_value, debt_value],
    "Weight": [equity_weight, debt_weight],
    "Cost_%": [cost_of_equity * 100, cost_of_debt * 100],
    "Weighted_Cost": [weighted_cost_equity, weighted_cost_debt],
    "Total_Cost": ["", ""]
})

# Format WACC
wacc_df.loc[1, "Total_Cost"] = f"{wacc*100:.2f}%"

# ──────────────────────────────────────────────
# Column Shading by Header
# ──────────────────────────────────────────────
def style_pipeline(df):
    colors = {
        "Cost_%": "#FFF7CC",         # light yellow
        "Weighted_Cost": "#E6F2FF",  # light blue
        "Total_Cost": "#E8FFE6"      # light green
    }

    def highlight(col):
        return [f'background-color: {colors.get(col.name, "")}'] * len(col)

    styled = df.style.apply(highlight)
    styled = styled.format({
        "Amount (£)": "{:,.2f}",
        "Weight": "{:.2f}",
        "Cost_%": "{:.2f}",
        "Weighted_Cost": "{:.2f}"
    })

    return styled

# ──────────────────────────────────────────────
# Output
# ──────────────────────────────────────────────
st.subheader("WACC Summary Table")
st.dataframe(style_pipeline(wacc_df), use_container_width=True)

st.metric("Final WACC", f"{wacc*100:.2f}%")

st.write("---")

st.write("""
**Weighted Average Cost of Capital (WACC)** is the average return a company must
offer investors to finance its assets.

It combines the cost of the company’s main long-term funding sources:
1️⃣ **Equity** – owners’ capital (often measured using CAPM)  
2️⃣ **Debt** – loan funding, adjusted for tax relief  
3️⃣ **Preferred Shares** – fixed-return financing  
4️⃣ **Retained Earnings** – reinvested profits  
5️⃣ **Other Long-Term Liabilities** – e.g., hybrid instruments or leasing  

A **lower WACC** means cheaper access to finance and a potentially higher company valuation.
""")

st.caption("Formula: (E/V × Re) + (D/V × Rd × (1 - Tax Rate))")

