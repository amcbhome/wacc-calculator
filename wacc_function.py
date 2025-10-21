"""
WACC Calculator Function
------------------------
Reusable function for financial modelling or integration with Streamlit apps.

Author: A. McBride
Generated with ChatGPT (GPT-5) under user supervision.
"""

def calculate_cost_of_equity(method="direct", **kwargs):
    """Calculate cost of equity using Direct, CAPM, or Gordon models."""
    if method == "direct":
        return kwargs.get("cost_of_equity")

    elif method == "capm":
        rf = kwargs.get("risk_free_rate")
        beta = kwargs.get("beta")
        rm = kwargs.get("market_return")
        return rf + beta * (rm - rf)

    elif method == "gordon":
        d1 = kwargs.get("dividend_next")
        p0 = kwargs.get("price_now")
        g = kwargs.get("growth_rate")
        return (d1 / p0) + g

    else:
        raise ValueError("Invalid method. Choose 'direct', 'capm', or 'gordon'.")


def calculate_wacc(
    equity_value: float,
    debt_value: float,
    cost_of_equity: float = None,
    cost_of_debt: float = None,
    tax_rate: float = 0.0,
    equity_method: str = "direct",
    **kwargs
) -> float:
    """Compute Weighted Average Cost of Capital (WACC) as a percentage."""
    ke = calculate_cost_of_equity(
        method=equity_method,
        cost_of_equity=cost_of_equity,
        **kwargs
    )

    total_value = equity_value + debt_value
    w_e = equity_value / total_value
    w_d = debt_value / total_value

    wacc = (w_e * ke) + (w_d * cost_of_debt * (1 - tax_rate))
    return round(wacc * 100, 2)