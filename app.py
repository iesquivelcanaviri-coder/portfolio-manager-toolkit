from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd


app = Flask(__name__)

# ============================================================
# 1. PORTFOLIO DATA (SIMULATED SCENARIOS)
# ============================================================

PORTFOLIO_1 = {
    "client_id": "portfolio_1_conservative_retiree",

    # 1. Client Identity & Legal Requirements
    "identity": {
        "name": "Marie‑Claire Dubois",
        "date_of_birth": "1958-03-12",
        "nationality": "French",
        "tax_residency": "France",
        "address": "Lyon, France",
        "identification": "French passport"
    },

    "compliance": {
        "kyc": "Completed",
        "aml": "No red flags",
        "source_of_wealth": "Pension and inheritance",
        "source_of_funds": "Retirement savings",
        "fatca_crs": "CRS only",
        "pep": False
    },

    # 2. Investment Objectives
    "objectives": {
        "goals": "Capital preservation and stable income",
        "time_horizon_years": "5–7",
        "expected_return_percent": "2–3",
        "benchmark": "Eurozone government bond index"
    },

    # 3. Risk Profile
    "risk_profile": {
        "risk_tolerance": "Conservative",
        "risk_capacity": "Low",
        "max_drawdown_percent": -8
    },

    # 4. Financial Situation
    "financials": {
        "net_worth": 850000,
        "investments": 500000,
        "real_estate": "Primary residence",
        "liabilities": 0,
        "income_monthly": 2200,
        "expenses_monthly": 1800,
        "liquidity_needs_monthly": 3000
    },

    # 5. Investment Constraints
    "constraints": {
        "legal": "UCITS‑compliant",
        "esg": "No tobacco",
        "max_equity_allocation_percent": 20,
        "currency": "EUR only"
    },

    # 6. Client Preferences
    "preferences": {
        "investment_style": "Income‑focused",
        "products": ["Bond funds", "Money‑market funds"],
        "communication": "Monthly, simplified reports"
    },

    # 7. Behavioural & Psychological Factors
    "behavioural": {
        "past_reactions": "Panicked during 2020 market crash",
        "decision_style": "Hands‑off",
        "biases": ["Loss aversion"]
    },

    # 8. Mandate Agreement
    "mandate": {
        "type": "Discretionary",
        "fees_percent": 0.8,
        "rebalancing_frequency": "Quarterly",
        "ips": "Preserve capital, generate income, minimize volatility"
    },

    # Numerical fields required for your Flask calculations
    "portfolio_value": 500000,
    "max_weight": 20,
    "volatility": 8.0,
    "returns": [0.2, 0.1, 0.15, 0.05, 0.1],
    "ticker": "IEF"   # 7–10yr Treasury ETF (low‑risk)
}



PORTFOLIO_2 = {
    "client_id": "portfolio_2_busy_executive",

    "identity": {
        "name": "James O’Connor",
        "date_of_birth": "1981-07-04",
        "nationality": "Irish",
        "tax_residency": "Ireland",
        "address": "Dublin, Ireland",
        "identification": "Irish passport"
    },

    "compliance": {
        "kyc": "Completed",
        "aml": "No issues",
        "source_of_wealth": "Salary and bonuses",
        "source_of_funds": "Corporate employment",
        "fatca_crs": "CRS only",
        "pep": False
    },

    "objectives": {
        "goals": "Long‑term growth",
        "time_horizon_years": "15+",
        "expected_return_percent": "6–8",
        "benchmark": "MSCI World"
    },

    "risk_profile": {
        "risk_tolerance": "Growth",
        "risk_capacity": "High",
        "max_drawdown_percent": -20
    },

    "financials": {
        "net_worth": 1400000,
        "investments": 600000,
        "real_estate": "Home and rental property",
        "liabilities": 200000,
        "income_yearly": 180000,
        "expenses_yearly": 70000,
        "liquidity_needs": "Low"
    },

    "constraints": {
        "legal": "UCITS",
        "esg": "Required",
        "max_stock_weight_percent": 10,
        "currency": "EUR base, FX allowed"
    },

    "preferences": {
        "investment_style": "Passive",
        "products": ["ETFs only"],
        "communication": "Quarterly"
    },

    "behavioural": {
        "past_reactions": "Stayed invested during downturns",
        "decision_style": "Hands‑off",
        "biases": ["Home bias toward Irish equities"]
    },

    "mandate": {
        "type": "Discretionary",
        "fees_percent": 0.6,
        "rebalancing_frequency": "Semi‑annual",
        "ips": "Global equity exposure with ESG screening"
    },

    "portfolio_value": 600000,
    "max_weight": 10,
    "volatility": 22.0,
    "returns": [0.6, -0.3, 0.8, 0.4, 0.5],
    "ticker": "ACWI"
}


PORTFOLIO_3 = {
    "client_id": "portfolio_3_corporate_treasury",

    # 1. Client Identity & Legal Requirements
    "identity": {
        "company_name": "Helvetic Precision Tools SA",
        "incorporation_year": 2012,
        "residency": "Geneva, Switzerland",
        "ownership": "Family‑owned",
        "signatories": ["CFO", "CEO"]
    },
    
    "compliance": {
        "kyc": "Completed",
        "aml": "Clean",
        "source_of_wealth": "Operating profits",
        "source_of_funds": "Corporate cash reserves",
        "fatca_crs": "Corporate CRS",
        "pep": False
    },

    # 2. Investment Objectives
    "objectives": {
        "goals": "Preserve capital and earn yield",
        "time_horizon_years": "1–3",
        "expected_return_percent": "1–2",
        "benchmark": "CHF money‑market index"
    },

    # 3. Risk Profile
    "risk_profile": {
        "risk_tolerance": "Very low",
        "risk_capacity": "Medium",
        "max_drawdown_percent": -3
    },

    # 4. Financial Situation
    "financials": {
        "assets_cash": 5000000,
        "liabilities": 0,
        "income": "Business revenue",
        "expenses": "Operational",
        "liquidity_needs": 1000000
    },

    # 5. Investment Constraints
    "constraints": {
        "legal": "Corporate policy prohibits equities",
        "esg": "Neutral",
        "max_issuer_weight_percent": 5,
        "currency": "CHF only"
    },

    # 6. Client Preferences
    "preferences": {
        "investment_style": "Capital protection",
        "products": ["Money‑market funds", "Short‑duration bonds"],
        "communication": "Monthly, detailed"
    },

    # 7. Behavioural & Psychological Factors
    "behavioural": {
        "past_reactions": "CFO is extremely risk‑averse",
        "decision_style": "Very involved",
        "biases": ["Cash bias"]
    },

    # 8. Mandate Agreement
    "mandate": {
        "type": "Advisory",
        "fees_percent": 0.4,
        "rebalancing_frequency": "Monthly liquidity checks",
        "ips": "No equities, short‑duration fixed income only"
    },

    # Numerical fields required for your Flask calculations
    "portfolio_value": 5000000,
    "max_weight": 5,
    "volatility": 3.0,
    "returns": [0.05, 0.03, 0.04, 0.02, 0.03],
    "ticker": "SHY"
}

PORTFOLIO_4 = {
    "client_id": "portfolio_4_international_entrepreneur",

    # 1. Client Identity & Legal Requirements
    "identity": {
        "name": "Alejandro Torres",
        "date_of_birth": "1986-11-22",
        "nationality": "Spanish",
        "residency": "Dubai",
        "identification": "Spanish passport"
    },

    "compliance": {
        "kyc": "Completed",
        "aml": "No issues",
        "source_of_wealth": "Tech company founder",
        "source_of_funds": "Business sale and dividends",
        "fatca_crs": "CRS",
        "pep": False
    },

    # 2. Investment Objectives
    "objectives": {
        "goals": "Growth and diversification",
        "time_horizon_years": "10+",
        "expected_return_percent": "8–12",
        "benchmark": "MSCI ACWI"
    },

    # 3. Risk Profile
    "risk_profile": {
        "risk_tolerance": "Aggressive",
        "risk_capacity": "Very high",
        "max_drawdown_percent": -30
    },

    # 4. Financial Situation
    "financials": {
        "net_worth": 12000000,
        "investments": 4000000,
        "real_estate": "Three properties",
        "liabilities": 0,
        "income": "Irregular business income",
        "expenses_yearly": 200000,
        "liquidity_needs": "Medium"
    },

    # 5. Investment Constraints
    "constraints": {
        "legal": "None",
        "esg": "Prefers clean energy",
        "concentration": "Avoids competitor industries",
        "currency": ["USD", "EUR", "CHF"]
    },

    # 6. Client Preferences
    "preferences": {
        "investment_style": "Thematic and opportunistic",
        "products": ["Direct equities", "Thematic ETFs"],
        "communication": "Weekly"
    },

    # 7. Behavioural & Psychological Factors
    "behavioural": {
        "past_reactions": "Buys aggressively during market dips",
        "decision_style": "Collaborative",
        "biases": ["Overconfidence"]
    },

    # 8. Mandate Agreement
    "mandate": {
        "type": "Advisory",
        "fees_percent": 1.0,
        "rebalancing_frequency": "Opportunistic",
        "ips": "High‑growth, multi‑currency, thematic focus"
    },

    # Numerical fields required for your Flask calculations
    "portfolio_value": 4000000,
    "max_weight": 15,
    "volatility": 35.0,
    "returns": [1.2, -0.8, 2.0, -0.5, 1.5],
    "ticker": "QQQ"
}

PORTFOLIO_5 = {
    "client_id": "portfolio_5_family_office",

    # 1. Client Identity & Legal Requirements
    "identity": {
        "name": "The Beaumont Family Office",
        "incorporation_year": 1998,
        "residency": "London, UK",
        "ownership": "Multi‑generational family",
        "signatories": ["CIO", "Family council"]
    },

    "compliance": {
        "kyc": "Completed",
        "aml": "Clean",
        "source_of_wealth": "Real estate and private equity",
        "source_of_funds": "Family assets",
        "fatca_crs": "CRS",
        "pep": "One family member (low‑risk)"
    },

    # 2. Investment Objectives
    "objectives": {
        "goals": "Preserve wealth and achieve moderate growth",
        "time_horizon_years": "30+",
        "expected_return_percent": "5–7",
        "benchmark": "40/60 global portfolio"
    },

    # 3. Risk Profile
    "risk_profile": {
        "risk_tolerance": "Balanced",
        "risk_capacity": "Very high",
        "max_drawdown_percent": -15
    },

    # 4. Financial Situation
    "financials": {
        "net_worth": 50000000,
        "investments": 30000000,
        "real_estate": 20000000,
        "liabilities": 0,
        "income": "Rental income and dividends",
        "expenses_yearly": 1000000,
        "liquidity_needs_yearly": 500000
    },

    # 5. Investment Constraints
    "constraints": {
        "legal": "Must include alternatives",
        "esg": "Required",
        "max_asset_weight_percent": 10,
        "currency": "GBP base, global exposure allowed"
    },

    # 6. Client Preferences
    "preferences": {
        "investment_style": "Diversified and institutional",
        "products": [
            "Hedge funds",
            "Private equity",
            "Real estate",
            "ETFs"
        ],
        "communication": "Monthly plus quarterly deep‑dive reports"
    },

    # 7. Behavioural & Psychological Factors
    "behavioural": {
        "past_reactions": "Calm during crises",
        "decision_style": "Committee‑based",
        "biases": ["None significant"]
    },

    # 8. Mandate Agreement
    "mandate": {
        "type": "Discretionary",
        "fees_percent": 1.2,
        "rebalancing_frequency": "Quarterly",
        "ips": "Multi‑asset, ESG‑aligned, long‑term preservation"
    },

    # Numerical fields required for your Flask calculations
    "portfolio_value": 30000000,
    "max_weight": 10,
    "volatility": 15.0,
    "returns": [0.4, -0.1, 0.5, 0.3, 0.2],
    "ticker": "AOR"
}



PORTFOLIOS = {
    "scenario1": PORTFOLIO_1,
    "scenario2": PORTFOLIO_2,
    "scenario3": PORTFOLIO_3,
    "scenario4": PORTFOLIO_4,
    "scenario5": PORTFOLIO_5


# ============================================================
# 2. ADVANCED PORTFOLIO MANAGER TOOLS
# ============================================================




# ============================================================
# 3. ROUTES (WEB PAGES)
#    Professional PM-focused endpoints with richer outputs
# ============================================================

@app.route("/")
def index():
    """
    Dashboard view:
    - Shows all portfolios
    - Allows PM to select a scenario
    """
    return render_template("index.html", portfolios=PORTFOLIOS)



# Debug mode is disabled for good security practice.
# In production environments (like Render), debug mode should always be OFF
# to prevent exposing internal application details.
# Render runs the app using Gunicorn, so debug mode is ignored anyway.


if __name__ == "__main__":
    app.run(debug=True)
 
#if __name__ == "__main__":
 #   app.run(debug=False)
