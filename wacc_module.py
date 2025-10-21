"""
WACC Calculator Module
──────────────────────────────────────────────
This module provides a clean, callable function
to compute the Weighted Average Cost of Capital (WACC)
with no user interface dependencies.
"""

def calculate_wacc(equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate):
    """
    Weighted Average Cost of Capital (WACC)

    Parameters
    ----------
    equity_value : float
        Market value of equity.
    debt_value : float
        Market value of debt.
    cost_of_equity : float
        Cost of equity as a decimal (e.g., 0.10 for 10%).
    cost_of_debt : float
        Cost of debt as a decimal (e.g., 0.06 for 6%).
    tax_rate : float
        Corporate tax rate as a decimal (e.g., 0.25 for 25%).

    Returns
    -------
    dict
        Dictionary containing the component weights and total WACC (%).
    """

    total_value = equity_value + debt_value
    if total_value == 0:
        raise ValueError("Equity + Debt cannot be zero.")

    w_e = equity_value / total_value
    w_d = debt_value / total_value

    wacc = (w_e * cost_of_equity) + (w_d * cost_of_debt * (1 - tax_rate))

    return {
        "equity_value": equity_value,
        "debt_value": debt_value,
        "cost_of_equity": cost_of_equity,
        "cost_of_debt": cost_of_debt,
        "tax_rate": tax_rate,
        "equity_weight": round(w_e, 4),
        "debt_weight": round(w_d, 4),
        "wacc_percent": round(wacc * 100, 2)
    }
