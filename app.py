# ============================================================  
# IMPORTS  # Section title showing all imported libraries and Flask tools
# ============================================================  

from flask import Flask, render_template, request, jsonify  # Imports Flask app object plus render_template for HTML pages, request for form/JSON data, and jsonify for API responses
import yfinance as yf  # Imports yfinance and gives it the short name yf so Yahoo Finance data can be downloaded more easily
import numpy as np  # Imports NumPy and gives it the short name np so mathematical functions like square root can be used
import re  # Imports Python's regular expressions module so text like "3.5%" can be cleaned and parsed
import time  # Imports time module so dashboard results can be cached for a number of seconds

app = Flask(__name__)  # Creates the Flask application instance; __name__ tells Flask where this file is located

# ============================================================  
# GLOBAL STORAGE  # Section title for variables stored in memory while the app is running
# ============================================================  

selected_stocks = {  # Dictionary used to store the stocks added by the user for each portfolio scenario
    "scenario1": [],  # Empty list for holdings added to portfolio scenario 1
    "scenario2": [],  # Empty list for holdings added to portfolio scenario 2
    "scenario3": [],  # Empty list for holdings added to portfolio scenario 3
    "scenario4": [],  # Empty list for holdings added to portfolio scenario 4
    "scenario5": [],  # Empty list for holdings added to portfolio scenario 5
}  

dashboard_cache = {  # Dictionary used to cache market dashboard output so it does not rebuild on every page load
    "rows": None,  # Stores the cached dashboard rows; starts as None because nothing has been built yet
    "timestamp": 0  # Stores the time when the cache was last updated; starts at 0
}  

DASHBOARD_CACHE_SECONDS = 300  # Cache duration in seconds; 300 seconds equals 5 minutes

# ============================================================  
# PORTFOLIO CONFIGURATION  # Section title for all predefined portfolio scenarios
# ============================================================  

PORTFOLIO_1 = {  # Dictionary defining the first client portfolio
    "client_id": "portfolio_1_conservative_retiree",  # Unique internal ID for this portfolio
    "identity": {  # Nested dictionary containing client identity details
        "name": "Marie-Claire Dubois",  # Client full name
        "date_of_birth": "1958-03-12",  # Client date of birth
        "nationality": "French",  # Client nationality
        "tax_residency": "France",  # Country where the client is tax resident
        "address": "Lyon, France",  # Client location/address summary
        "identification": "French passport",  # Main ID document used for KYC
    },  
    "compliance": {  # Nested dictionary for compliance and onboarding details
        "kyc": "Completed",  # Know Your Customer check status
        "aml": "No red flags",  # Anti-money laundering screening result
        "source_of_wealth": "Pension and inheritance",  # Where the client’s wealth came from
        "source_of_funds": "Retirement savings",  # Where the invested money specifically came from
        "fatca_crs": "CRS only",  # Tax reporting classification
        "pep": False,  # Politically exposed person flag; False means no
    },  
    "objectives": {  # Nested dictionary for investment goals
        "goals": "Capital preservation and stable income",  # Main investment objective
        "time_horizon_years": "5-7",  # Time horizon in years
        "expected_return_percent": "2-3",  # Expected return range in percentage terms
        "benchmark": "Eurozone government bond index",  # Benchmark used for comparison
    },  
    "risk_profile": {  # Nested dictionary describing client risk profile
        "risk_tolerance": "Conservative",  # Client willingness to accept risk
        "risk_capacity": "Low",  # Client ability to absorb losses
        "max_drawdown_percent": -8,  # Maximum acceptable portfolio decline
    },  
    "financials": {  # Nested dictionary for financial situation
        "net_worth": 850000,  # Total net worth
        "investments": 500000,  # Amount already invested or available for investment
        "real_estate": "Primary residence",  # Property situation
        "liabilities": 0,  # Total liabilities
        "income_monthly": 2200,  # Monthly income
        "expenses_monthly": 1800,  # Monthly expenses
        "liquidity_needs_monthly": 3000,  # Monthly cash need requirement
    },  
    "constraints": {  # Nested dictionary for mandate restrictions
        "legal": "UCITS-compliant",  # Legal restriction or framework
        "esg": "No tobacco",  # ESG restriction
        "max_equity_allocation_percent": 20,  # Maximum equity exposure allowed
        "currency": "EUR only",  # Allowed currency exposure
    },  
    "preferences": {  # Nested dictionary for client preferences
        "investment_style": "Income-focused",  # Preferred investment style
        "products": ["Bond funds", "Money-market funds"],  # Preferred product types
        "communication": "Monthly, simplified reports",  # Preferred reporting style
    },  
    "behavioural": {  # Nested dictionary for behavioural observations
        "past_reactions": "Panicked during 2020 market crash",  # Historical behaviour in stress periods
        "decision_style": "Hands-off",  # How involved the client likes to be
        "biases": ["Loss aversion"],  # Behavioural biases observed
    },  
    "mandate": {  # Nested dictionary for formal portfolio management rules
        "type": "Discretionary",  # Mandate type means manager can act on behalf of client
        "fees_percent": 0.8,  # Management fee percentage
        "rebalancing_frequency": "Quarterly",  # How often the portfolio should be rebalanced
        "ips": "Preserve capital, generate income, minimize volatility",  # Investment policy statement summary
    },  
    "portfolio_value": 500000,  # Total portfolio value used in sizing logic
    "max_weight": 20,  # Absolute maximum weight per position
    "volatility": 8.0,  # Example portfolio or benchmark volatility input
    "returns": [0.2, 0.1, 0.15, 0.05, 0.1],  # Example returns list used as embedded scenario data
    "ticker": "IEF",  # Default benchmark/reference ticker for this portfolio
}  

PORTFOLIO_2 = {
    "client_id": "portfolio_2_busy_executive",
    "identity": {
        "name": "James O'Connor",
        "date_of_birth": "1981-07-04",
        "nationality": "Irish",
        "tax_residency": "Ireland",
        "address": "Dublin, Ireland",
        "identification": "Irish passport",
    },
    "compliance": {
        "kyc": "Completed",
        "aml": "No issues",
        "source_of_wealth": "Salary and bonuses",
        "source_of_funds": "Corporate employment",
        "fatca_crs": "CRS only",
        "pep": False,
    },
    "objectives": {
        "goals": "Long-term growth",
        "time_horizon_years": "15+",
        "expected_return_percent": "6-8",
        "benchmark": "MSCI World",
    },
    "risk_profile": {
        "risk_tolerance": "Growth",
        "risk_capacity": "High",
        "max_drawdown_percent": -20,
    },
    "financials": {
        "net_worth": 1400000,
        "investments": 600000,
        "real_estate": "Home and rental property",
        "liabilities": 200000,
        "income_yearly": 180000,
        "expenses_yearly": 70000,
        "liquidity_needs": "Low",
    },
    "constraints": {
        "legal": "UCITS",
        "esg": "Required",
        "max_stock_weight_percent": 10,
        "currency": "EUR base, FX allowed",
    },
    "preferences": {
        "investment_style": "Passive",
        "products": ["ETFs only"],
        "communication": "Quarterly",
    },
    "behavioural": {
        "past_reactions": "Stayed invested during downturns",
        "decision_style": "Hands-off",
        "biases": ["Home bias toward Irish equities"],
    },
    "mandate": {
        "type": "Discretionary",
        "fees_percent": 0.6,
        "rebalancing_frequency": "Semi-annual",
        "ips": "Global equity exposure with ESG screening",
    },
    "portfolio_value": 600000,
    "max_weight": 10,
    "volatility": 22.0,
    "returns": [0.6, -0.3, 0.8, 0.4, 0.5],
    "ticker": "ACWI",
}

PORTFOLIO_3 = {
    "client_id": "portfolio_3_corporate_treasury",
    "identity": {
        "company_name": "Helvetic Precision Tools SA",
        "incorporation_year": 2012,
        "residency": "Geneva, Switzerland",
        "ownership": "Family-owned",
        "signatories": ["CFO", "CEO"],
    },
    "compliance": {
        "kyc": "Completed",
        "aml": "Clean",
        "source_of_wealth": "Operating profits",
        "source_of_funds": "Corporate cash reserves",
        "fatca_crs": "Corporate CRS",
        "pep": False,
    },
    "objectives": {
        "goals": "Preserve capital and earn yield",
        "time_horizon_years": "1-3",
        "expected_return_percent": "1-2",
        "benchmark": "CHF money-market index",
    },
    "risk_profile": {
        "risk_tolerance": "Very low",
        "risk_capacity": "Medium",
        "max_drawdown_percent": -3,
    },
    "financials": {
        "assets_cash": 5000000,
        "liabilities": 0,
        "income": "Business revenue",
        "expenses": "Operational",
        "liquidity_needs": 1000000,
    },
    "constraints": {
        "legal": "Corporate policy prohibits equities",
        "esg": "Neutral",
        "max_issuer_weight_percent": 5,
        "currency": "CHF only",
    },
    "preferences": {
        "investment_style": "Capital protection",
        "products": ["Money-market funds", "Short-duration bonds"],
        "communication": "Monthly, detailed",
    },
    "behavioural": {
        "past_reactions": "CFO is extremely risk-averse",
        "decision_style": "Very involved",
        "biases": ["Cash bias"],
    },
    "mandate": {
        "type": "Advisory",
        "fees_percent": 0.4,
        "rebalancing_frequency": "Monthly liquidity checks",
        "ips": "No equities, short-duration fixed income only",
    },
    "portfolio_value": 5000000,
    "max_weight": 5,
    "volatility": 3.0,
    "returns": [0.05, 0.03, 0.04, 0.02, 0.03],
    "ticker": "SHY",
}

PORTFOLIO_4 = {
    "client_id": "portfolio_4_international_entrepreneur",
    "identity": {
        "name": "Alejandro Torres",
        "date_of_birth": "1986-11-22",
        "nationality": "Spanish",
        "residency": "Dubai",
        "identification": "Spanish passport",
    },
    "compliance": {
        "kyc": "Completed",
        "aml": "No issues",
        "source_of_wealth": "Tech company founder",
        "source_of_funds": "Business sale and dividends",
        "fatca_crs": "CRS",
        "pep": False,
    },
    "objectives": {
        "goals": "Growth and diversification",
        "time_horizon_years": "10+",
        "expected_return_percent": "8-12",
        "benchmark": "MSCI ACWI",
    },
    "risk_profile": {
        "risk_tolerance": "Aggressive",
        "risk_capacity": "Very high",
        "max_drawdown_percent": -30,
    },
    "financials": {
        "net_worth": 12000000,
        "investments": 4000000,
        "real_estate": "Three properties",
        "liabilities": 0,
        "income": "Irregular business income",
        "expenses_yearly": 200000,
        "liquidity_needs": "Medium",
    },
    "constraints": {
        "legal": "None",
        "esg": "Prefers clean energy",
        "concentration": "Avoids competitor industries",
        "currency": ["USD", "EUR", "CHF"],
    },
    "preferences": {
        "investment_style": "Thematic and opportunistic",
        "products": ["Direct equities", "Thematic ETFs"],
        "communication": "Weekly",
    },
    "behavioural": {
        "past_reactions": "Buys aggressively during market dips",
        "decision_style": "Collaborative",
        "biases": ["Overconfidence"],
    },
    "mandate": {
        "type": "Advisory",
        "fees_percent": 1.0,
        "rebalancing_frequency": "Opportunistic",
        "ips": "High-growth, multi-currency, thematic focus",
    },
    "portfolio_value": 4000000,
    "max_weight": 15,
    "volatility": 35.0,
    "returns": [1.2, -0.8, 2.0, -0.5, 1.5],
    "ticker": "QQQ",
}

PORTFOLIO_5 = {
    "client_id": "portfolio_5_family_office",
    "identity": {
        "name": "The Beaumont Family Office",
        "incorporation_year": 1998,
        "residency": "London, UK",
        "ownership": "Multi-generational family",
        "signatories": ["CIO", "Family council"],
    },
    "compliance": {
        "kyc": "Completed",
        "aml": "Clean",
        "source_of_wealth": "Real estate and private equity",
        "source_of_funds": "Family assets",
        "fatca_crs": "CRS",
        "pep": "One family member (low-risk)",
    },
    "objectives": {
        "goals": "Preserve wealth and achieve moderate growth",
        "time_horizon_years": "30+",
        "expected_return_percent": "5-7",
        "benchmark": "40/60 global portfolio",
    },
    "risk_profile": {
        "risk_tolerance": "Balanced",
        "risk_capacity": "Very high",
        "max_drawdown_percent": -15,
    },
    "financials": {
        "net_worth": 50000000,
        "investments": 30000000,
        "real_estate": 20000000,
        "liabilities": 0,
        "income": "Rental income and dividends",
        "expenses_yearly": 1000000,
        "liquidity_needs_yearly": 500000,
    },
    "constraints": {
        "legal": "Must include alternatives",
        "esg": "Required",
        "max_asset_weight_percent": 10,
        "currency": "GBP base, global exposure allowed",
    },
    "preferences": {
        "investment_style": "Diversified and institutional",
        "products": ["Hedge funds", "Private equity", "Real estate", "ETFs"],
        "communication": "Monthly plus quarterly deep-dive reports",
    },
    "behavioural": {
        "past_reactions": "Calm during crises",
        "decision_style": "Committee-based",
        "biases": ["None significant"],
    },
    "mandate": {
        "type": "Discretionary",
        "fees_percent": 1.2,
        "rebalancing_frequency": "Quarterly",
        "ips": "Multi-asset, ESG-aligned, long-term preservation",
    },
    "portfolio_value": 30000000,
    "max_weight": 10,
    "volatility": 15.0,
    "returns": [0.4, -0.1, 0.5, 0.3, 0.2],
    "ticker": "AOR",
}

PORTFOLIOS = {
    "scenario1": PORTFOLIO_1,
    "scenario2": PORTFOLIO_2,
    "scenario3": PORTFOLIO_3,
    "scenario4": PORTFOLIO_4,
    "scenario5": PORTFOLIO_5,
}