# WACC Calculator (Streamlit)

A clean, transparent **Weighted Average Cost of Capital** calculator with:
- **CAPM** or **Dividend Growth (Gordon)** for Cost of Equity
- Single-rate or **multi-tranche** Cost of Debt
- Explicit tax shield handling per tranche
- Full workings, metrics, and CSV export

## Quickstart

```bash
# clone
git clone https://github.com/<your-username>/wacc-calculator.git
cd wacc-calculator

# create & activate venv (optional)
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# install
pip install -r requirements.txt

# run
streamlit run app.py
