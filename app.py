import streamlit as st
import pandas as pd

st.set_page_config(page_title="WACC Calculator", page_icon="🧮")

st.title("🧮 WACC Calculator")

st.write("""
This calculator determines the Weighted Average Cost of Capital (WACC) using the equity and debt structure of a company.
Enter the values below and view the calculated results instantly.
""")

# ─────────── Inputs ─────────── #

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

# ─────────── WACC Calculation ─────────── #

total_value = equity_value + debt_value

equity_weight = equity_value / total_value
debt_weight = debt_value / total_value

weighted_cost_equity = equity_weight * cost_of_equity
weighted_cost_debt = debt_weight * cost_of_debt * (1 - tax_rate)

wacc = weighted_cost_equity + weighted_cost_debt

# ─────────── Results Table ─────────── #

wacc_df = pd.DataFrame({
    "Type": ["Equity", "Debt"],
    "Amount (£)": [equity_value, debt_value],
    "Weight": [equity_weight, debt_weight],
    "Cost_%": [cost_of_equity * 100, cost_of_debt * 100],
    "Weighted_Cost": [weighted_cost_equity, weighted_cost_debt],
    "Total_Cost": ["", ""]
})

# Add WACC to Total_Cost row
wacc_df.loc[1, "Total_Cost"] = f"{wacc*100:.3f}%"

# ─────────── Column Shading Style ─────────── #

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
        "Weight": "{:.3f}",
        "Cost_%": "{:.2f}",
        "Weighted_Cost": "{:.3f}"
    })

    return styled

# ─────────── Output ─────────── #

st.subheader("WACC Summary Table")
st.dataframe(style_pipeline(wacc_df), use_container_width=True)

st.metric("Final WACC", f"{wacc*100:.3f}%")

st.caption("Formula: (E/V × Re) + (D/V × Rd × (1 - Tax Rate))")


