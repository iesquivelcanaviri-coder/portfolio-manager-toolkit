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


# ============================================================  
# HELPERS  # This section contains reusable helper functions used across routes and analysis logic
# ============================================================  

def get_portfolio_display_name(portfolio):  # Defines a helper function that returns the best display name for a portfolio dictionary
    identity = portfolio.get("identity", {})  # Safely gets the nested "identity" dictionary; returns empty dict if missing to avoid errors
    return (  # Starts a grouped return statement that will return the first non-empty value it finds
        identity.get("name")  # First tries to return the client's personal name if this is an individual portfolio
        or identity.get("company_name")  # If no personal name exists, tries the company name for corporate/entity portfolios
        or portfolio.get("client_id", "Unknown Portfolio")  # If neither exists, falls back to client_id, or "Unknown Portfolio" if missing
    ) 

def get_portfolio_choices():  # Defines a helper function to build portfolio options for the HTML dropdown menu
    return [  # Returns a list comprehension containing one dictionary per portfolio
        {"key": key, "name": get_portfolio_display_name(portfolio)}  # Creates a small dictionary with the scenario key and cleaned display name
        for key, portfolio in PORTFOLIOS.items()  # Loops through the global PORTFOLIOS dictionary to process every portfolio scenario
    ] 

def safe_div(a, b):  # Defines a helper function for safe division so the app does not crash on divide-by-zero or None
    return a / b if b not in (0, 0.0, None) else 0.0  # Divides a by b only if b is valid; otherwise returns 0.0 as a safe fallback

def parse_weight_to_decimal(weight_text):  # Defines a helper function to convert text like "6%" or "1-2%" into decimal portfolio weights
    if not weight_text:  # Checks whether the input is empty, None, or otherwise falsey
        return 0.0  # Returns 0.0 because there is no usable weight to convert

    numbers = re.findall(r"\d+\.?\d*", str(weight_text))  # Uses regex to extract all numbers from the text after converting input to string
    if not numbers:  # Checks whether the regex found any numeric values
        return 0.0  # Returns 0.0 because the text did not contain a usable number

    values = [float(num) for num in numbers]  # Converts all extracted numeric strings into float values

    if len(values) == 1:  # Checks whether only one number was found, for example "6%"
        return values[0] / 100.0  # Converts the percentage into decimal form, e.g. 6 becomes 0.06

    return (sum(values) / len(values)) / 100.0  # If a range like "1-2%" exists, averages the numbers and converts result to decimal

def get_effective_max_weight(portfolio):  # Defines a helper function that finds the strictest position-size limit for a portfolio
    limits = []  # Creates an empty list to store all possible maximum-weight constraints found
    constraints = portfolio.get("constraints", {})  # Safely gets the portfolio constraints dictionary or an empty dict if missing

    if portfolio.get("max_weight") is not None:  # Checks whether the base top-level max_weight exists
        limits.append(float(portfolio["max_weight"]))  # Adds the top-level maximum weight to the list after converting it to float

    if constraints.get("max_stock_weight_percent") is not None:  # Checks whether a stock-specific max weight exists in constraints
        limits.append(float(constraints["max_stock_weight_percent"]))  # Adds that stock weight limit to the list

    if constraints.get("max_asset_weight_percent") is not None:  # Checks whether a general asset-level max weight exists
        limits.append(float(constraints["max_asset_weight_percent"]))  # Adds that asset-level limit to the list

    if constraints.get("max_issuer_weight_percent") is not None:  # Checks whether an issuer concentration limit exists
        limits.append(float(constraints["max_issuer_weight_percent"]))  # Adds that issuer limit to the list

    if limits:  # Checks whether at least one limit was collected
        return min(limits)  # Returns the smallest limit because the strictest limit is the effective one

    return None  # Returns None if no limits were found at all

def calculate_portfolio_summary(stocks):  # Defines a helper function that calculates summary statistics for one portfolio's selected holdings
    if not stocks:  # Checks whether the portfolio currently has no selected holdings
        return {  # Returns a default summary dictionary for an empty portfolio
            "position_count": 0,  # States that there are zero positions
            "total_allocated_percent": 0.0,  # States that 0% of capital is allocated
            "remaining_cash_percent": 100.0,  # States that 100% remains as cash
            "average_beta": None  # Average beta is unknown because there are no holdings
        }  

    total_allocated = sum(stock.get("weight_decimal", 0.0) for stock in stocks)  # Sums the decimal weights of all holdings to get total allocation
    betas = [stock["beta"] for stock in stocks if stock.get("beta") is not None]  # Builds a list of all non-null beta values from holdings

    average_beta = round(sum(betas) / len(betas), 2) if betas else None  # Calculates average beta rounded to 2 decimals, or None if no betas exist

    return {  # Returns the portfolio summary dictionary
        "position_count": len(stocks),  # Number of holdings currently in the portfolio
        "total_allocated_percent": round(total_allocated * 100, 2),  # Converts total allocated weight to percentage form
        "remaining_cash_percent": round(max(0.0, 1.0 - total_allocated) * 100, 2),  # Calculates remaining unallocated cash as a percentage
        "average_beta": average_beta  # Includes the previously calculated average beta
    } 

def build_grouped_portfolio_payload():  # Defines a helper function to build all portfolio holdings grouped by scenario for the frontend
    grouped = {}  # Creates an empty dictionary that will hold each portfolio's grouped output

    for key, portfolio in PORTFOLIOS.items():  # Loops through each scenario key and its portfolio definition
        stocks = selected_stocks.get(key, [])  # Gets the selected holdings for that scenario, or an empty list if none exist
        sorted_stocks = sorted(  # Starts sorting the holdings before sending them to the frontend
            stocks,  # The list of holdings to sort
            key=lambda stock: stock.get("weight_decimal", 0.0),  # Sort key uses weight_decimal so biggest positions appear first
            reverse=True  # Sorts from highest weight to lowest weight
        ) 

        grouped[key] = {  # Adds one entry to the grouped dictionary for this scenario
            "portfolio_name": get_portfolio_display_name(portfolio),  # Stores a clean portfolio name for display
            "stocks": sorted_stocks,  # Stores the sorted holdings list
            "summary": calculate_portfolio_summary(sorted_stocks)  # Stores the calculated summary for those holdings
        } 

    return grouped  # Returns the full grouped portfolio payload to be used in JSON responses or template rendering

def default_metrics(period_label: str):  # Defines a helper function that returns a default metrics dictionary for failed or missing price data
    return {  # Returns a standardised dictionary so the rest of the app always receives the same structure
        "annualised_expected_return": 0.0,  # Default expected return is 0.0 when no data exists
        "annualised_volatility": 0.0,  # Default volatility is 0.0 when no data exists
        "sharpe_like": 0.0,  # Default Sharpe-like ratio is 0.0 when no data exists
        "latest_price": 0.0,  # Default latest price is 0.0 when no data exists
        "price_start_date": "N/A",  # No valid price start date is available
        "price_end_date": "N/A",  # No valid price end date is available
        "price_observations": 0,  # No price observations were found
        "return_start_date": "N/A",  # No valid return series start date is available
        "return_end_date": "N/A",  # No valid return series end date is available
        "return_observations": 0,  # No return observations were found
        "returns_series": None,  # No return series is available
        "period_label": period_label,  # Stores the period label passed into the function, such as "1y" or "3mo"
    }  
    
def compute_metrics_from_batch(batch_data, ticker: str):  # Defines a helper function to compute metrics for one ticker using already-downloaded batch data
    try:  # Starts a try block so dashboard processing does not crash if one ticker has issues
        if batch_data is None or batch_data.empty:  # Checks whether the batch download returned no usable data
            return default_metrics("1y")  # Returns default 1-year metrics if batch data is missing

        if hasattr(batch_data.columns, "nlevels") and batch_data.columns.nlevels > 1:  # Checks whether yfinance returned multi-level columns for multi-ticker data
            if ticker not in batch_data.columns.get_level_values(0):  # Checks whether the requested ticker exists in the top-level columns
                return default_metrics("1y")  # Returns defaults if the ticker is not present in batch data
            ticker_data = batch_data[ticker].copy()  # Extracts only this ticker's DataFrame and copies it for safe processing
        else:  # Runs if the data is not multi-indexed
            ticker_data = batch_data.copy()  # Uses the whole dataset directly because there is no top-level ticker split

        if "Close" not in ticker_data.columns:  # Checks whether a Close price column exists
            return default_metrics("1y")  # Returns defaults if Close prices are unavailable

        close_prices = ticker_data["Close"].dropna()  # Selects the Close column and removes missing values
        if close_prices.empty or len(close_prices) < 2:  # Checks whether there are enough price points to calculate returns
            return default_metrics("1y")  # Returns defaults if there are fewer than 2 prices

        returns = close_prices.pct_change().dropna()  # Calculates daily percentage returns from closing prices and removes NaN values

        if returns.empty:  # Checks whether return calculation produced no valid values
            return {  # Returns a partial metrics dictionary with price info but zero return-based statistics
                "annualised_expected_return": 0.0,  # Sets expected return to zero because returns could not be computed
                "annualised_volatility": 0.0,  # Sets volatility to zero for same reason
                "sharpe_like": 0.0,  # Sets Sharpe-like value to zero because return/risk data is incomplete
                "latest_price": float(close_prices.iloc[-1]),  # Still returns latest valid close price
                "price_start_date": close_prices.index[0].strftime("%Y-%m-%d"),  # Returns first available price date
                "price_end_date": close_prices.index[-1].strftime("%Y-%m-%d"),  # Returns last available price date
                "price_observations": int(len(close_prices)),  # Returns count of available price observations
                "return_start_date": "N/A",  # No valid return start date exists
                "return_end_date": "N/A",  # No valid return end date exists
                "return_observations": 0,  # Return observation count is zero
                "returns_series": None,  # No valid returns series to pass onward
                "period_label": "1y",  # Labels this metric block as 1-year data
            } 

        annualised_volatility = float(returns.std() * np.sqrt(252))  # Converts daily return standard deviation into annualised volatility using 252 trading days
        annualised_expected_return = float(returns.mean() * 252)  # Converts average daily return into annualised expected return
        sharpe_like = safe_div(annualised_expected_return, annualised_volatility)  # Calculates simple Sharpe-like ratio using helper to avoid division errors
        latest_price = float(close_prices.iloc[-1])  # Stores the latest available closing price

        return {  # Returns the fully computed metrics dictionary
            "annualised_expected_return": annualised_expected_return,  # Annualised expected return value
            "annualised_volatility": annualised_volatility,  # Annualised volatility value
            "sharpe_like": sharpe_like,  # Sharpe-like ratio value
            "latest_price": latest_price,  # Latest market price
            "price_start_date": close_prices.index[0].strftime("%Y-%m-%d"),  # First valid date in price series
            "price_end_date": close_prices.index[-1].strftime("%Y-%m-%d"),  # Last valid date in price series
            "price_observations": int(len(close_prices)),  # Number of valid closing price observations
            "return_start_date": returns.index[0].strftime("%Y-%m-%d"),  # First valid date in returns series
            "return_end_date": returns.index[-1].strftime("%Y-%m-%d"),  # Last valid date in returns series
            "return_observations": int(len(returns)),  # Number of valid return observations
            "returns_series": returns,  # Returns the full pandas returns series for later beta calculations
            "period_label": "1y",  # Labels this metric block as 1-year
        } 

    except Exception:  # Catches any unexpected error during metric calculation
        return default_metrics("1y")  # Returns default 1-year metrics instead of crashing the dashboard

def compute_metrics(ticker: str, period: str):  # Defines a helper function to download price data for a single ticker and compute metrics
    try:  # Starts try block to safely handle download errors
        data = yf.download(ticker, period=period, auto_adjust=True, progress=False)  # Downloads historical market data from Yahoo Finance for the chosen ticker and period
    except Exception:  # Catches download failures
        return default_metrics(period)  # Returns default metrics for the requested period

    if data is None or data.empty:  # Checks whether the download returned nothing useful
        return default_metrics(period)  # Returns defaults if no data was downloaded

    if hasattr(data.columns, "nlevels") and data.columns.nlevels > 1:  # Checks whether returned columns are multi-level
        data.columns = data.columns.get_level_values(0)  # Flattens multi-level columns to single-level names like Close, Open, High

    if "Close" not in data.columns:  # Verifies that closing prices are available
        return default_metrics(period)  # Returns defaults if there is no Close column

    close_prices = data["Close"].dropna()  # Extracts the Close price series and removes missing values

    if close_prices.empty or len(close_prices) < 2:  # Checks whether there are enough price points to calculate returns
        return default_metrics(period)  # Returns defaults if there are too few points

    returns = close_prices.pct_change().dropna()  # Computes percentage returns and removes first NaN row

    if returns.empty:  # Checks whether returns series ended up empty
        return {  # Returns a partial metrics dictionary with valid price details but zero return metrics
            "annualised_expected_return": 0.0,  # No valid annualised expected return
            "annualised_volatility": 0.0,  # No valid annualised volatility
            "sharpe_like": 0.0,  # No valid Sharpe-like ratio
            "latest_price": float(close_prices.iloc[-1]),  # Still returns latest available price
            "price_start_date": close_prices.index[0].strftime("%Y-%m-%d"),  # First valid price date
            "price_end_date": close_prices.index[-1].strftime("%Y-%m-%d"),  # Last valid price date
            "price_observations": int(len(close_prices)),  # Number of price observations
            "return_start_date": "N/A",  # No return start date available
            "return_end_date": "N/A",  # No return end date available
            "return_observations": 0,  # No return observations
            "returns_series": None,  # No return series stored
            "period_label": period,  # Keeps the original period label
        } 

    annualised_volatility = float(returns.std() * np.sqrt(252))  # Converts daily standard deviation into annualised volatility
    annualised_expected_return = float(returns.mean() * 252)  # Converts daily average return into annualised expected return
    sharpe_like = safe_div(annualised_expected_return, annualised_volatility)  # Calculates return per unit of volatility safely
    latest_price = float(close_prices.iloc[-1])  # Stores the latest available close price

    return {  # Returns the full single-ticker metrics dictionary
        "annualised_expected_return": annualised_expected_return,  # Stores annualised expected return
        "annualised_volatility": annualised_volatility,  # Stores annualised volatility
        "sharpe_like": sharpe_like,  # Stores Sharpe-like ratio
        "latest_price": latest_price,  # Stores latest price
        "price_start_date": close_prices.index[0].strftime("%Y-%m-%d"),  # First date in price series
        "price_end_date": close_prices.index[-1].strftime("%Y-%m-%d"),  # Last date in price series
        "price_observations": int(len(close_prices)),  # Number of valid prices
        "return_start_date": returns.index[0].strftime("%Y-%m-%d"),  # First return date
        "return_end_date": returns.index[-1].strftime("%Y-%m-%d"),  # Last return date
        "return_observations": int(len(returns)),  # Number of valid returns
        "returns_series": returns,  # Stores the full returns series for later use such as beta
        "period_label": period,  # Keeps the input period label
    }  

def build_quarterly_forecast(latest_price: float, annualised_expected_return: float):  # Defines a helper function that projects quarterly prices based on annualised return
    adjusted_return = max(annualised_expected_return, -0.95)  # Caps downside at -95% to prevent invalid math when raising negative values to fractional powers
    quarterly_return = (1 + adjusted_return) ** 0.25 - 1  # Converts annual return assumption into an equivalent quarterly compounded return

    q1_price = latest_price * (1 + quarterly_return)  # Forecasts end-of-quarter-1 price
    q2_price = q1_price * (1 + quarterly_return)  # Forecasts end-of-quarter-2 price based on prior quarter
    q3_price = q2_price * (1 + quarterly_return)  # Forecasts end-of-quarter-3 price
    q4_price = q3_price * (1 + quarterly_return)  # Forecasts end-of-quarter-4 price

    return {  # Returns all forecast outputs in one dictionary
        "quarterly_return": quarterly_return,  # The implied quarterly expected return
        "q1_expected_price": q1_price,  # Forecasted Q1 price
        "q2_expected_price": q2_price,  # Forecasted Q2 price
        "q3_expected_price": q3_price,  # Forecasted Q3 price
        "q4_expected_price": q4_price,  # Forecasted Q4 price
    }  # Ends the forecast dictionary

def score_and_decide(expected_return: float, volatility: float, sharpe_like: float, beta):  # Defines a scoring model that maps analytics into an investment decision and position size
    score = 0  # Starts the score at zero before rules are applied

    if expected_return >= 0.02:  # Checks whether annualised expected return is at least 2%
        score += 2  # Adds 2 points for acceptable expected return
    if volatility <= 0.08:  # Checks whether volatility is very low at 8% or below
        score += 3  # Adds 3 points for very low volatility
    elif volatility <= 0.12:  # Checks whether volatility is moderate at 12% or below
        score += 1  # Adds 1 point for acceptable but not excellent volatility
    if sharpe_like > 0.6:  # Checks whether risk-adjusted return is strong
        score += 2  # Adds 2 points for strong Sharpe-like ratio
    elif sharpe_like > 0.3:  # Checks whether Sharpe-like ratio is decent but not outstanding
        score += 1  # Adds 1 point for moderate risk-adjusted return
    if beta is not None:  # Only evaluates beta if it exists
        if beta <= 0.9:  # Checks whether beta is defensively below market
            score += 2  # Adds 2 points for low market sensitivity
        elif beta <= 1.1:  # Checks whether beta is close to market-neutral
            score += 1  # Adds 1 point for acceptable beta

    if score >= 7:  # Highest score bucket
        decision = "YES — high conviction"  # Sets decision to strongest buy-type category
        weight = "6%"  # Sets recommended position size to 6%
        tag = "High conviction"  # Sets frontend tag
    elif score >= 5:  # Second-best score bucket
        decision = "YES — core holding"  # Sets decision to core portfolio holding
        weight = "3.5%"  # Sets recommended size to 3.5%
        tag = "Core holding"  # Sets frontend tag
    elif score >= 3:  # Mid-tier score bucket
        decision = "YES — satellite"  # Sets decision to satellite/differentiated position
        weight = "3%"  # Sets recommended size to 3%
        tag = "Diversifier"  # Sets frontend tag
    elif score >= 1:  # Low but still investable score bucket
        decision = "LIMITED — high risk / exploratory"  # Sets decision to small speculative allocation
        weight = "1–2%"  # Sets recommended range size
        tag = "Exploratory"  # Sets frontend tag
    else:  # Lowest score bucket
        decision = "NO — hold as cash instead"  # Rejects the security and suggests staying in cash
        weight = "Cash (5%)"  # Shows fallback cash position wording
        tag = "Cash / Risk Control"  # Sets frontend tag

    return {  # Returns all scoring outputs in a dictionary
        "score": score,  # Final numeric score
        "decision": decision,  # Final recommendation text
        "recommended_weight": weight,  # Suggested portfolio weight
        "tag": tag  # Short label for UI display
    }  

def validate_portfolio_addition(portfolio_key, ticker, recommended_weight, sector, industry):  # Defines a helper to check whether a proposed position respects the selected portfolio rules
    portfolio = PORTFOLIOS[portfolio_key]  # Retrieves the chosen portfolio definition from the global dictionary
    errors = []  # Starts an empty list for hard validation failures
    warnings = []  # Starts an empty list for softer review warnings

    weight_decimal = parse_weight_to_decimal(recommended_weight)  # Converts text weight such as "3.5%" into decimal form
    weight_percent = weight_decimal * 100  # Converts decimal back to percentage for human-readable validation messages

    max_weight_allowed = get_effective_max_weight(portfolio)  # Finds the strictest max-weight rule for this portfolio
    if max_weight_allowed is not None and weight_percent > max_weight_allowed:  # Checks whether proposed weight breaches allowed limit
        errors.append(  # Adds a hard validation error message
            f"Recommended weight of {weight_percent:.2f}% exceeds the portfolio limit of {max_weight_allowed:.2f}%."  # Creates readable error text
        ) 

    current_total_excluding_same_ticker = sum(  # Starts calculation of current total allocation while excluding this ticker if already present
        stock.get("weight_decimal", 0.0)  # Uses each existing holding's decimal weight
        for stock in selected_stocks[portfolio_key]  # Loops through all selected holdings in this portfolio
        if stock.get("ticker") != ticker  # Excludes the same ticker so updates do not double-count existing allocation
    )  

    projected_total = current_total_excluding_same_ticker + weight_decimal  # Calculates what total allocation would become after adding/updating this position
    if projected_total > 1.0:  # Checks whether projected portfolio weight would exceed 100%
        errors.append(  # Adds a hard validation error
            f"Projected total allocation would be {projected_total * 100:.2f}%, which exceeds 100%."  # User-friendly explanation of over-allocation
        )  

    legal_rule = str(portfolio.get("constraints", {}).get("legal", "")).lower()  # Reads the legal constraint text safely and converts it to lowercase for matching
    if "prohibits equities" in legal_rule:  # Checks whether the mandate bans equity exposure
        fixed_income_tickers = {"IEF", "SHY", "AGG", "BND", "TIP"}  # Defines a simple approved set of fixed-income-style tickers
        if ticker not in fixed_income_tickers:  # Checks whether proposed ticker falls outside allowed fixed-income list
            errors.append("This mandate prohibits equities. Only fixed-income style instruments should be added.")  # Adds hard compliance-style error

    esg_rule = str(portfolio.get("constraints", {}).get("esg", "")).lower()  # Reads ESG constraint text safely in lowercase form
    if "no tobacco" in esg_rule:  # Checks whether portfolio excludes tobacco exposure
        sector_text = str(sector).lower()  # Converts sector text to lowercase for matching
        industry_text = str(industry).lower()  # Converts industry text to lowercase for matching
        if "tobacco" in sector_text or "tobacco" in industry_text:  # Checks whether sector or industry suggests tobacco exposure
            errors.append("This mandate excludes tobacco-related exposure.")  # Adds hard ESG validation error

    currency_rule = portfolio.get("constraints", {}).get("currency")  # Reads currency restriction from portfolio constraints
    if currency_rule in ["EUR only", "CHF only"]:  # Checks whether the mandate allows only one currency
        warnings.append(f"Manual currency review recommended because this mandate states {currency_rule}.")  # Adds warning because ticker currency is not fully validated in code

    if portfolio.get("constraints", {}).get("esg") == "Required":  # Checks whether ESG compliance is required more generally
        warnings.append("Manual ESG review recommended before final approval.")  # Adds soft warning for human review

    return {  # Returns all validation outputs in one dictionary
        "errors": errors,  # Hard validation failures
        "warnings": warnings,  # Soft review warnings
        "weight_decimal": weight_decimal  # Parsed weight value to reuse later without recalculating
    } 

# ============================================================  # Decorative separator to make the code easier to read in sections
# STOCK ANALYSIS ENGINE  # This section contains the main function that analyses a selected ticker
# ============================================================  # Decorative separator ending the section title

def analyze_stock(ticker: str, benchmark_ticker: str, portfolio_key: str):  # Defines a function that analyses one ticker against a chosen benchmark and portfolio
    metrics_1y = compute_metrics(ticker, "1y")  # Calls the helper function to calculate 1-year metrics for the selected ticker
    metrics_3m = compute_metrics(ticker, "3mo")  # Calls the helper function to calculate 3-month metrics for the selected ticker
    benchmark_metrics = compute_metrics(benchmark_ticker, "1y")  # Calculates 1-year metrics for the benchmark so beta can be compared against it

    beta = 0.0  # Sets a default beta value in case beta cannot be calculated later
    benchmark_start_date = benchmark_metrics.get("return_start_date", "N/A")  # Gets the benchmark return start date for display, or N/A if missing
    benchmark_end_date = benchmark_metrics.get("return_end_date", "N/A")  # Gets the benchmark return end date for display, or N/A if missing
    beta_observations = 0  # Starts the counter for how many aligned return observations were used in beta calculation

    if metrics_1y["returns_series"] is not None and benchmark_metrics["returns_series"] is not None:  # Only continue with beta calculation if both return series exist
        stock_aligned, bench_aligned = metrics_1y["returns_series"].align(  # Aligns the stock and benchmark return series so both have the same dates
            benchmark_metrics["returns_series"],  # Uses the benchmark return series as the series to align against
            join="inner"  # Keeps only the dates that appear in both series so the comparison is mathematically valid
        )

        beta_observations = int(len(stock_aligned))  # Stores how many matching observations exist after alignment

        if len(stock_aligned) > 1 and bench_aligned.var() != 0:  # Checks that there is enough data and the benchmark variance is not zero
            beta = float(stock_aligned.cov(bench_aligned) / bench_aligned.var())  # Calculates beta as covariance of stock and benchmark divided by benchmark variance

    decision_pack = score_and_decide(  # Sends the calculated metrics into the scoring model to get a decision and recommended weight
        expected_return=metrics_1y["annualised_expected_return"],  # Passes 1-year annualised expected return into the scoring function
        volatility=metrics_1y["annualised_volatility"],  # Passes 1-year annualised volatility into the scoring function
        sharpe_like=metrics_1y["sharpe_like"],  # Passes 1-year Sharpe-like ratio into the scoring function
        beta=beta  # Passes the calculated beta into the scoring function
    )  

    try:  # Starts a try block because Yahoo Finance metadata requests can sometimes fail
        info = yf.Ticker(ticker).info or {}  # Requests metadata for the ticker from yfinance and falls back to an empty dictionary if nothing is returned
        sector = (  # Starts a grouped fallback expression for sector
            info.get("sector")  # First tries to get the standard sector field
            or info.get("category")  # If sector is missing, tries category which is common for ETFs or funds
            or info.get("fundCategory")  # If category is missing, tries fundCategory as another fallback
            or "Unknown"  # If none of the above exist, uses "Unknown" as a safe default
        ) 
        industry = (  # Starts a grouped fallback expression for industry
            info.get("industry")  # First tries to get the standard industry field
            or info.get("quoteType")  # If industry is missing, tries quoteType as a fallback
            or info.get("fundFamily")  # If quoteType is missing, tries fundFamily for fund-based instruments
            or "Unknown"  # If none of the above exist, uses "Unknown" as the fallback
        ) 
    except Exception:  # Catches any error thrown by the metadata request so the app does not crash
        sector = "Unknown"  # Uses a default sector value when metadata lookup fails
        industry = "Unknown"  # Uses a default industry value when metadata lookup fails

    forecast_1y = build_quarterly_forecast(  # Calls the forecast helper to create a 1-year based quarterly forecast
        latest_price=metrics_1y["latest_price"],  # Uses the latest price from the 1-year metrics as the starting price
        annualised_expected_return=metrics_1y["annualised_expected_return"]  # Uses the 1-year annualised expected return to build the forecast
    )  

    forecast_3m = build_quarterly_forecast(  # Calls the forecast helper to create a 3-month based quarterly forecast
        latest_price=metrics_3m["latest_price"],  # Uses the latest price from the 3-month metrics as the starting price
        annualised_expected_return=metrics_3m["annualised_expected_return"]  # Uses the 3-month annualised expected return to build the forecast
    )  

    portfolio = PORTFOLIOS[portfolio_key]  # Looks up the selected portfolio dictionary from the global PORTFOLIOS object using the chosen key

    return {  # Starts the final dictionary returned to the Flask route and then to the frontend as JSON
        "ticker": ticker.upper(),  # Returns the ticker in uppercase so it displays cleanly in the browser
        "portfolio_key": portfolio_key,  # Returns the selected portfolio key so the frontend knows which scenario was analysed
        "portfolio_name": get_portfolio_display_name(portfolio),  # Returns the cleaned display name of the selected portfolio using the helper function
        "beta": beta,  # Returns the calculated beta value
        "score": decision_pack["score"],  # Returns the numeric score produced by the scoring model
        "decision": decision_pack["decision"],  # Returns the decision text produced by the scoring model
        "recommended_weight": decision_pack["recommended_weight"],  # Returns the recommended portfolio weight from the scoring model
        "sector": sector,  # Returns the sector metadata found from Yahoo Finance or the fallback value
        "industry": industry,  # Returns the industry metadata found from Yahoo Finance or the fallback value
        "tag": decision_pack["tag"],  # Returns the short tag label from the scoring model
        "benchmark_ticker": benchmark_ticker,  # Returns the benchmark ticker used in the comparison
        "benchmark_start_date": benchmark_start_date,  # Returns the benchmark return series start date for the frontend display
        "benchmark_end_date": benchmark_end_date,  # Returns the benchmark return series end date for the frontend display
        "beta_observations": beta_observations,  # Returns the number of aligned observations used in beta calculation
        "one_year": {  # Starts the nested dictionary for 1-year analysis results
            "annualised_expected_return": metrics_1y["annualised_expected_return"],  # Stores the 1-year annualised expected return
            "annualised_volatility": metrics_1y["annualised_volatility"],  # Stores the 1-year annualised volatility
            "sharpe_like": metrics_1y["sharpe_like"],  # Stores the 1-year Sharpe-like ratio
            "latest_price": metrics_1y["latest_price"],  # Stores the most recent price in the 1-year data
            "price_start_date": metrics_1y["price_start_date"],  # Stores the first date in the 1-year price series
            "price_end_date": metrics_1y["price_end_date"],  # Stores the last date in the 1-year price series
            "price_observations": metrics_1y["price_observations"],  # Stores how many price observations exist in the 1-year series
            "return_start_date": metrics_1y["return_start_date"],  # Stores the first date in the 1-year return series
            "return_end_date": metrics_1y["return_end_date"],  # Stores the last date in the 1-year return series
            "return_observations": metrics_1y["return_observations"],  # Stores how many return observations exist in the 1-year series
            "forecast": {  # Starts the nested forecast block inside the 1-year analysis block
                "quarterly_return": forecast_1y["quarterly_return"],  # Stores the quarterly return implied by the 1-year expected return
                "q1_expected_price": forecast_1y["q1_expected_price"],  # Stores the projected price for quarter 1
                "q2_expected_price": forecast_1y["q2_expected_price"],  # Stores the projected price for quarter 2
                "q3_expected_price": forecast_1y["q3_expected_price"],  # Stores the projected price for quarter 3
                "q4_expected_price": forecast_1y["q4_expected_price"],  # Stores the projected price for quarter 4
            }
        },  
        "three_month": {  # Starts the nested dictionary for 3-month analysis results
            "annualised_expected_return": metrics_3m["annualised_expected_return"],  # Stores the 3-month annualised expected return
            "annualised_volatility": metrics_3m["annualised_volatility"],  # Stores the 3-month annualised volatility
            "sharpe_like": metrics_3m["sharpe_like"],  # Stores the 3-month Sharpe-like ratio
            "latest_price": metrics_3m["latest_price"],  # Stores the most recent price in the 3-month data
            "price_start_date": metrics_3m["price_start_date"],  # Stores the first date in the 3-month price series
            "price_end_date": metrics_3m["price_end_date"],  # Stores the last date in the 3-month price series
            "price_observations": metrics_3m["price_observations"],  # Stores how many price observations exist in the 3-month series
            "return_start_date": metrics_3m["return_start_date"],  # Stores the first date in the 3-month return series
            "return_end_date": metrics_3m["return_end_date"],  # Stores the last date in the 3-month return series
            "return_observations": metrics_3m["return_observations"],  # Stores how many return observations exist in the 3-month series
            "forecast": {  # Starts the nested forecast block inside the 3-month analysis block
                "quarterly_return": forecast_3m["quarterly_return"],  # Stores the quarterly return implied by the 3-month expected return
                "q1_expected_price": forecast_3m["q1_expected_price"],  # Stores the projected price for quarter 1
                "q2_expected_price": forecast_3m["q2_expected_price"],  # Stores the projected price for quarter 2
                "q3_expected_price": forecast_3m["q3_expected_price"],  # Stores the projected price for quarter 3
                "q4_expected_price": forecast_3m["q4_expected_price"],  # Stores the projected price for quarter 4
            } 
        }  
    }  

# ============================================================  
# MARKET DASHBOARD DATA  # This section defines the ticker universe and dashboard-building logic
# ============================================================  

MASTER_TICKERS = {  # Creates a dictionary that groups tickers into categories for the dashboard universe
    "fixed_income": [  # Starts the fixed income category list
        "SHY", "IEF", "TLT", "BND", "AGG", "TIP", "LQD", "HYG", "VGIT", "VCIT",  # Treasury, aggregate bond, credit, and duration-related ETFs
        "MINT", "BIL", "JPST", "SCHR", "SCHZ", "IGIB", "SPTI", "GOVT", "BSV", "VGSH"  # More bond and short-duration fixed income ETFs
    ], 

    "defensive_equities": [
        "XLP", "XLV", "XLU", "PG", "KO", "PEP", "JNJ", "MRK", "PFE",
        "WMT", "MCD", "CL", "KMB", "DUK", "SO", "NEE", "GIS", "MDT", "HSY", "EL"
    ],

    "core_equities": [
        "AAPL", "MSFT", "AMZN", "GOOGL", "META", "JPM", "V", "MA", "UNH",
        "HD", "ADBE", "CRM", "ORCL", "CSCO", "INTU", "AVGO", "NFLX",
        "QCOM", "LIN", "TXN", "HON", "CAT", "IBM", "AMGN", "NOW", "BKNG",
        "AXP", "GS", "BLK", "SPGI"
    ],

    "growth_equities": [
        "TSLA", "NVDA", "AMD", "SHOP", "SQ", "UBER", "PANW", "CRWD", "SNOW", "PLTR",
        "MDB", "DDOG", "NET", "ZS", "TEAM", "ABNB", "MELI", "SE", "TTD", "ROKU",
        "ARKK", "QQQ", "SMH", "SOXX", "IWF", "VUG", "XLK", "FTEC", "SCHG", "MGK"
    ],

    "international_equities": [
        "VEA", "IEFA", "EWG", "EWQ", "EWI", "EWJ", "EWS", "EWA", "EWU", "EWP",
        "VGK", "EZU", "FEZ", "AAXJ", "VWO", "EEM", "INDA", "EWY", "MCHI", "FXI",
        "EWZ", "EWT", "EIDO", "EPHE", "EZA", "ERUS", "EWC", "EWL", "EWD", "EWN"
    ],

    "alternatives": [
        "GLD", "SLV", "VNQ", "REET", "SCHH", "REM", "DBC", "PDBC", "USO", "IAU",
        "VNQI", "RWO", "FTGC", "COMT", "GSG", "DBA", "UUP", "FXE", "FXF", "FXY",
        "BITO", "ETHE", "PALL", "PLTM", "URA", "COPX", "WOOD", "HACK", "CIBR", "KWEB"
    ]
}


def build_market_rows():  # Defines a function that builds the full list of dashboard rows shown in market_dashboard.html
    dashboard_tickers = sorted({  # Creates a sorted list of unique tickers from all categories in MASTER_TICKERS
        ticker  # This is the individual ticker symbol that will be collected
        for group in MASTER_TICKERS.values()  # Loops through each list of tickers in the dictionary values
        for ticker in group  # Loops through each ticker inside each category list
    }) 

    rows = []  # Creates an empty list that will store one processed dashboard row per ticker

    batch_data = yf.download(  # Starts a batch Yahoo Finance download so all tickers are downloaded together for efficiency
        tickers=dashboard_tickers,  # Sends the full ticker universe to yfinance in one call
        period="1y",  # Requests one year of historical data for all dashboard tickers
        auto_adjust=True,  # Uses adjusted prices so splits and dividends are reflected in the price series
        progress=False,  # Hides the download progress bar so terminal output stays cleaner
        group_by="ticker",  # Organises downloaded columns by ticker, which is useful for multi-ticker downloads
        threads=True  # Allows parallel requests internally, which can improve speed
    )  

    for ticker in dashboard_tickers:  # Loops through every ticker in the dashboard universe so each one gets its own dashboard row
        metrics_1y = compute_metrics_from_batch(batch_data, ticker)  # Calculates annualised return, volatility, Sharpe-like ratio, and other metrics from the batch data for this ticker

        sector = "Unknown"  # Sets a default sector value because the dashboard is running in fast mode and is not fetching .info metadata
        industry = "Unknown"  # Sets a default industry value for the same reason
        market_cap = None  # Sets raw market cap to None because market-cap metadata is not being fetched here
        market_cap_display = "N/A"  # Sets display-friendly market-cap text to N/A so the table still has a consistent value
        beta = None  # Sets beta to None because the dashboard fast mode does not calculate or fetch beta metadata
        pe_ratio = None  # Sets P/E ratio to None because valuation metadata is not being fetched in this version
        dividend_yield = None  # Sets dividend yield to None because dividend metadata is also being skipped
        # Fast mode: skip slow per-ticker metadata requests from yfinance .info  # Explains that individual metadata lookups were intentionally removed to make the dashboard faster
        # The default values set above will be used instead.  # Explains that placeholder values such as Unknown and N/A remain active in the table

        decision_pack = score_and_decide(  # Calls the scoring function to translate the ticker's 1-year metrics into a score, decision, weight, and tag
            expected_return=metrics_1y["annualised_expected_return"],  # Passes the annualised expected return into the scoring model
            volatility=metrics_1y["annualised_volatility"],  # Passes the annualised volatility into the scoring model
            sharpe_like=metrics_1y["sharpe_like"],  # Passes the Sharpe-like ratio into the scoring model
            beta=beta  # Passes beta into the scoring model, which is currently None in fast mode
        ) 

        expected_return_percent = round(metrics_1y["annualised_expected_return"] * 100, 2)  # Converts expected return from decimal format to percentage format and rounds to 2 decimals
        volatility_percent = round(metrics_1y["annualised_volatility"] * 100, 2)  # Converts volatility from decimal format to percentage format and rounds to 2 decimals
        sharpe_like_value = round(metrics_1y["sharpe_like"], 2)  # Rounds the Sharpe-like ratio to 2 decimal places for cleaner display

        ranking_score = (  # Starts a custom ranking formula used to sort securities in the dashboard
            (metrics_1y["annualised_expected_return"] * 0.50)  # Gives 50% weight to expected return so higher-return securities rank better
            + (metrics_1y["sharpe_like"] * 0.30)  # Gives 30% weight to risk-adjusted return so efficient names rank better
            - (metrics_1y["annualised_volatility"] * 0.20)  # Subtracts 20% of volatility so riskier names are penalised
        ) 

        is_low_risk = (  # Starts the logic for the low-risk preset filter used in the market dashboard
            (beta is not None and beta <= 1.0)  # Requires beta to exist and be less than or equal to 1.0, meaning market sensitivity is not above the benchmark
            and metrics_1y["annualised_volatility"] <= 0.18  # Also requires volatility to be 18% or below
            and decision_pack["decision"] != "NO — hold as cash instead"  # Excludes securities that were rejected by the scoring model
        ) 

        is_high_conviction = (  # Starts the logic for the high-conviction preset filter
            decision_pack["decision"] == "YES — high conviction"  # Requires the scoring model to classify the security as a high-conviction idea
            and decision_pack["score"] >= 7  # Also requires the score to be at least 7
        ) 

        is_income_candidate = (  # Starts the logic for the income/defensive preset filter
            (dividend_yield is not None and dividend_yield >= 1.5)  # Includes names with a dividend yield of at least 1.5% if dividend data exists
            or ticker in {"IEF", "SHY", "AGG", "BND", "TIP", "XLP", "XLV", "XLU"}  # Also manually includes bond and defensive ETFs that are logically income/defensive candidates
        ) 

        is_best_ranked = (  # Starts the logic for identifying best-ranked securities
            decision_pack["score"] >= 5  # Requires a score of at least 5
            and metrics_1y["sharpe_like"] >= 0.3  # Requires a Sharpe-like ratio of at least 0.3
        ) 

        is_core_holding = (  # Starts the logic for the core-holding preset
            decision_pack["decision"] == "YES — core holding"  # Returns True only when the decision says the security is a core holding
        ) 

        is_satellite = (  # Starts the logic for the satellite preset
            decision_pack["decision"] == "YES — satellite"  # Returns True only when the decision says the security is a satellite position
        ) 

        is_exploratory = (  # Starts the logic for the exploratory preset
            decision_pack["decision"] == "LIMITED — high risk / exploratory"  # Returns True only when the decision says the position is exploratory or high risk
        ) 

        is_cash_candidate = (  # Starts the logic for the cash preset
            decision_pack["decision"] == "NO — hold as cash instead"  # Returns True only when the security is rejected and cash is preferred
        ) 

        rows.append({  # Appends one completed row dictionary to the rows list so it can later be sent to the template
            "ticker": ticker,  # Stores the ticker symbol for this dashboard row
            "sector": sector,  # Stores the sector value, currently Unknown in fast mode
            "industry": industry,  # Stores the industry value, currently Unknown in fast mode
            "market_cap": market_cap,  # Stores raw market-cap value, currently None in fast mode
            "market_cap_display": market_cap_display,  # Stores user-friendly market-cap text shown in the HTML table
            "beta": None if beta is None else round(beta, 2),  # Stores beta as None if missing, otherwise rounds it to 2 decimals
            "pe_ratio": None if pe_ratio is None else round(pe_ratio, 2),  # Stores P/E as None if missing, otherwise rounds it to 2 decimals
            "dividend_yield": dividend_yield,  # Stores dividend yield value, currently None in fast mode
            "score": decision_pack["score"],  # Stores the numeric score returned by the scoring model
            "decision": decision_pack["decision"],  # Stores the full investment decision text
            "tag": decision_pack["tag"],  # Stores the short label used for display, such as High conviction or Diversifier
            "suggested_weight": decision_pack["recommended_weight"],  # Stores the recommended weight text such as 6%, 3.5%, 3%, or Cash (5%)
            "expected_return_percent": expected_return_percent,  # Stores expected return in percentage form for table display
            "volatility": volatility_percent,  # Stores volatility in percentage form for table display
            "sharpe_like": sharpe_like_value,  # Stores the rounded Sharpe-like ratio for display
            "ranking_score": round(ranking_score, 3),  # Stores the ranking score rounded to 3 decimals so sorting is cleaner
            "is_low_risk": is_low_risk,  # Stores boolean used by the Low Risk smart preset
            "is_high_conviction": is_high_conviction,  # Stores boolean used by the High Conviction smart preset
            "is_core_holding": is_core_holding,  # Stores boolean used by the Core Holdings smart preset
            "is_satellite": is_satellite,  # Stores boolean used by the Satellite / Diversifiers smart preset
            "is_exploratory": is_exploratory,  # Stores boolean used by the Exploratory / High Risk smart preset
            "is_income_candidate": is_income_candidate,  # Stores boolean used by the Income / Defensive smart preset
            "is_best_ranked": is_best_ranked,  # Stores boolean used by the Best Ranked smart preset
            "is_cash_candidate": is_cash_candidate,  # Stores boolean used by the Cash smart preset
        })

    rows.sort(key=lambda row: row["ranking_score"], reverse=True)  # Sorts all dashboard rows from highest ranking score to lowest so strongest names appear first
    return rows  # Returns the fully built list of dashboard rows to the calling function


# ============================================================ 
# ROUTES → HTML PAGES  # This section contains Flask routes that return HTML templates
# ============================================================ 

@app.route("/")  # Registers the root URL so visiting the site homepage triggers the home() function
def home():  # Defines the Flask view function for the home page
    return render_template("index.html")  # Renders the index.html template and sends it back to the browser

@app.route("/criteria")  # Registers the /criteria URL so Flask knows which function should handle that page
def criteria():  # Defines the Flask view function for the criteria page
    return render_template(  # Starts the template-rendering call for criteria.html
        "criteria.html",  # Tells Flask to render the criteria.html file from the templates folder
        portfolio_choices=get_portfolio_choices(),  # Passes the dropdown-ready portfolio choice list into the Jinja template
        default_portfolio_key="scenario1",  # Passes scenario1 as the default selected portfolio in the dropdown
        default_portfolio_name=get_portfolio_display_name(PORTFOLIO_1)  # Passes the display name of PORTFOLIO_1 for default page text
    )  

def get_cached_market_rows():  # Defines a helper function that returns cached dashboard rows instead of rebuilding them every time
    now = time.time()  # Stores the current Unix timestamp in seconds so cache age can be checked

    if (  # Starts the cache-validation condition
        dashboard_cache["rows"] is None  # Rebuilds the cache if no rows have ever been stored yet
        or now - dashboard_cache["timestamp"] > DASHBOARD_CACHE_SECONDS  # Rebuilds the cache if the existing cache is older than the allowed cache duration
    ):  # Ends the cache condition
        dashboard_cache["rows"] = build_market_rows()  # Recomputes the dashboard rows and stores them in the cache
        dashboard_cache["timestamp"] = now  # Updates the cache timestamp to the current time after rebuilding

    return dashboard_cache["rows"]  # Returns the cached dashboard rows whether they were freshly built or already stored
    
@app.route("/market_dashboard")  # Registers the /market_dashboard route for the market dashboard page
def market_dashboard():  # Defines the Flask view function for the dashboard page
    rows = get_cached_market_rows()  # Loads cached market rows so the page can render faster
    return render_template("market_dashboard.html", rows=rows)  # Renders market_dashboard.html and passes the rows variable into the Jinja template

@app.route("/contact")  # Registers the /contact route for the contact page
def contact():  # Defines the Flask view function for the contact page
    return render_template("contact.html")  # Renders the contact.html template and returns it to the browser


@app.route("/portfolio_profiles")  # Registers the /portfolio_profiles route for the portfolio workflow/profile page
def portfolio_profiles():  # Defines the Flask view function for the portfolio profiles page
    return render_template("portfolio_profiles.html", portfolios=PORTFOLIOS)  # Renders portfolio_profiles.html and passes the full PORTFOLIOS dictionary into the Jinja template


# ============================================================  
# ROUTES → API ENDPOINTS  # This section contains Flask routes that return JSON data instead of HTML
# ============================================================ 

@app.route("/analyze", methods=["POST"])  # Registers the /analyze endpoint and allows only POST requests because the frontend submits form data to it
def analyze():  # Defines the Flask view function that handles stock analysis requests
    ticker = request.form.get("ticker", "").strip().upper()  # Reads the ticker from submitted form data, removes extra spaces, and converts it to uppercase
    portfolio_key = request.form.get("portfolio_key", "scenario1")  # Reads the selected portfolio_key from form data and defaults to scenario1 if missing

    if portfolio_key not in PORTFOLIOS:  # Checks whether the submitted portfolio_key actually exists in the master portfolio dictionary
        return jsonify({"error": "Invalid portfolio selected."}), 400  # Returns a JSON error with HTTP status 400 if the portfolio key is invalid

    if not ticker:  # Checks whether the user failed to submit a ticker
        return jsonify({"error": "Please select a ticker."}), 400  # Returns a JSON error with HTTP status 400 if the ticker is empty

    try:  # Starts a try block so unexpected analysis problems do not crash the application
        benchmark_ticker = PORTFOLIOS[portfolio_key]["ticker"]  # Looks up the benchmark/reference ticker associated with the selected portfolio
        result = analyze_stock(ticker, benchmark_ticker, portfolio_key)  # Calls the main analysis function using the selected ticker, benchmark, and portfolio
        return jsonify(result)  # Returns the completed analysis result as JSON to the JavaScript frontend
    except Exception as e:  # Catches unexpected errors during analysis
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500  # Returns a JSON error with HTTP status 500 if analysis fails unexpectedly

@app.route("/add-to-portfolio", methods=["POST"])  # Registers the /add-to-portfolio endpoint and allows only POST because the frontend sends JSON data to it
def add_to_portfolio():  # Defines the Flask view function that adds or updates a holding in a selected portfolio
    data = request.get_json(force=True)  # Reads the incoming request body as JSON and forces parsing even if headers are imperfect

    ticker = data.get("ticker")  # Extracts the ticker value from the JSON payload
    portfolio_key = data.get("portfolio_key")  # Extracts the selected portfolio key from the JSON payload
    portfolio_name = data.get("portfolio_name")  # Extracts the human-readable portfolio name from the JSON payload
    recommended_weight = data.get("recommended_weight")  # Extracts the recommended weight text from the JSON payload
    decision = data.get("decision")  # Extracts the decision text from the JSON payload
    tag = data.get("tag")  # Extracts the short display tag from the JSON payload
    sector = data.get("sector")  # Extracts the sector metadata from the JSON payload
    industry = data.get("industry")  # Extracts the industry metadata from the JSON payload
    beta = data.get("beta")  # Extracts the beta value from the JSON payload

    if not ticker or not portfolio_key or portfolio_key not in PORTFOLIOS:  # Validates that the ticker exists, the portfolio key exists, and the portfolio key is valid
        return jsonify({"error": "Invalid stock or portfolio."}), 400  # Returns a JSON error with HTTP status 400 if validation fails

    validation = validate_portfolio_addition(  # Calls the portfolio-validation helper to check weight limits, mandate restrictions, and warnings
        portfolio_key=portfolio_key,  # Passes the selected portfolio key into the validation function
        ticker=ticker,  # Passes the ticker into the validation function
        recommended_weight=recommended_weight,  # Passes the suggested weight text so it can be parsed and checked
        sector=sector,  # Passes the sector so ESG and mandate checks can use it
        industry=industry  # Passes the industry so ESG and mandate checks can use it
    )  

    if validation["errors"]:  # Checks whether the validation helper found hard errors that should block the add/update action
        return jsonify({  # Starts building a JSON error response
            "error": validation["errors"],  # Returns the list of hard validation errors
            "warnings": validation["warnings"]  # Also returns any warnings found during validation
        }), 400  # Sends the JSON back with HTTP status 400 because the request is not valid

    existing_stock = next(  # Starts a search for an already-existing holding with the same ticker in the selected portfolio
        (stock for stock in selected_stocks[portfolio_key] if stock["ticker"] == ticker),  # Generator expression returns the first matching holding if it exists
        None  # Returns None if the ticker is not already in the selected portfolio
    )  

    payload = {  # Builds the holding dictionary that will be saved in selected_stocks
        "portfolio_name": portfolio_name,  # Stores the human-readable portfolio name
        "ticker": ticker,  # Stores the ticker symbol
        "recommended_weight": recommended_weight,  # Stores the suggested position-size text such as 6% or 3.5%
        "weight_decimal": validation["weight_decimal"],  # Stores the parsed decimal weight returned by the validation function
        "decision": decision,  # Stores the decision label for this holding
        "tag": tag,  # Stores the short UI tag
        "sector": sector,  # Stores the sector metadata
        "industry": industry,  # Stores the industry metadata
        "beta": beta  # Stores the beta value
    }  

    if existing_stock:  # Checks whether this ticker is already present in the selected portfolio
        existing_stock.update(payload)  # Updates the existing stored holding with the new payload values
        message = f"{ticker} updated in portfolio."  # Creates a confirmation message telling the frontend the holding was updated
    else:  # Runs when the ticker does not already exist in the selected portfolio
        selected_stocks[portfolio_key].append(payload)  # Appends the new holding payload to the selected portfolio list
        message = f"{ticker} added to portfolio."  # Creates a confirmation message telling the frontend the holding was newly added

    return jsonify({  # Starts building the success JSON response
        "message": message,  # Returns the add/update confirmation message
        "warnings": validation["warnings"],  # Returns any warnings that still need to be shown to the user
        "portfolio": build_grouped_portfolio_payload()  # Returns refreshed grouped portfolio data so the frontend can redraw current holdings immediately
    }) 

@app.route("/portfolio-stocks")  # Registers the /portfolio-stocks endpoint used by JavaScript to fetch grouped portfolio holdings
def portfolio_stocks():  # Defines the Flask view function for returning current selected holdings
    return jsonify(build_grouped_portfolio_payload())  # Returns the grouped holdings and summary metrics as JSON

# ============================================================ 
# RUN APP  # This section runs the Flask development server when the file is executed directly
# ============================================================ 
if __name__ == "__main__":  # Checks whether this file is being run directly rather than imported into another Python file
    app.run(debug=True)  # Starts the Flask development server with debug mode enabled so code changes and errors are easier to test