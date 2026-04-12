# UCD Python Programming Assessment – Flask Project

## Student Details

**Student:** Irene Esquivel Canaviri

---

## 1. Project Overview

This project is a Flask-based web application that simulates a **Portfolio Manager Decision-Support Toolkit**. It was built using **Python, Flask, HTML, CSS, JavaScript, and Yahoo Finance data via `yfinance`**.

The application is designed to reflect how a portfolio manager may:

- evaluate securities
- assess risk and return
- validate investments against portfolio mandates
- determine position sizing
- manage multiple portfolio scenarios

The project combines:

- predefined portfolio mandates and constraints  
- market data analysis using Yahoo Finance  
- portfolio screening and ranking logic  
- position sizing and suitability checks  
- interactive front-end dashboards  

---

## 2. Project Structure

The application follows a standard Flask project layout:

### Local Development Workflow



### Project Structure

portfolio-manager-toolkit/
│
├── app.py               → Main Flask application
├── .gitignore           → Prevents uploading .venv and cache files
├── README.md            → Project documentation
│
├── templates/           → HTML templates
│   ├── _navbar.html
│   ├── index.html
│   ├── criteria.html
│   ├── market_dashboard.html
│   ├── portfolio_profiles.html
│   ├── contact.html
│
└── static/              → CSS and JS assets
      ├── css/style.css
      └── js/script.js

### Deployment Workflow (GitHub → Render)

GitHub Repository
   │
   ├── Contains project files (but NOT .venv)
   ├── requirements.txt tells Render what to install
   ├── Procfile tells Render how to run the app
   │
   ▼
Render Deployment
   │
   ├── Pulls code from GitHub
   ├── Installs dependencies
   ├── Starts app using Gunicorn
   │
   ▼
Live Web Application



### Structure Explanation

- **app.py** → Main Flask application with routes and logic  
- **templates/** → HTML files rendered using Jinja  
- **static/** → CSS and JavaScript files  
- **_navbar.html** → Reusable navigation component  
- **portfolio_profiles.html** → Portfolio analysis and workflow page  
- **criteria.html** → Core portfolio decision engine  
- **market_dashboard.html** → Screening and ranking dashboard  
- **.venv/** → Virtual environment (not deployed)  
- **__pycache__/** → Python compiled files  

---

## 3. Main Features

### 3.1 Portfolio-Based Security Analysis

On the **Criteria** page, the user selects:

- a portfolio scenario  
- a stock or ETF ticker  

The application evaluates the selected security relative to the portfolio.

The analysis includes:

- beta vs benchmark  
- score and ranking  
- decision classification  
- recommended position weight  
- sector and industry classification  

It also provides two analysis windows:

- **1-year analysis**
- **3-month analysis**

For each period:

- annualised expected return  
- annualised volatility  
- Sharpe-like ratio  
- latest price  
- observation count  

A simplified **forward-looking quarterly forecast** is also included.

---

### 3.2 Portfolio Construction Workflow

Users can add securities to a portfolio after analysis.

When **Add / Update Portfolio** is triggered:

- rules and constraints are validated  
- positions are added or updated  
- portfolio metrics are recalculated  

Portfolio summary includes:

- number of positions  
- total allocation (%)  
- remaining cash (%)  
- average beta  

---

### 3.3 Market Dashboard

The **Market Dashboard** acts as a screening tool.

It uses a predefined universe grouped into:

- fixed income  
- defensive equities  
- core equities  
- growth equities  
- international equities  
- alternatives  

For each asset:

- expected return  
- volatility  
- Sharpe-like ratio  
- score  
- decision  
- suggested weight  
- ranking score  

Features include:

- filtering options  
- preset strategy buttons  
- sortable tables  
- highlighted scoring bands  

---

### 3.4 Portfolio Profiles Page

The **Portfolio Profiles** page introduces a professional workflow layer.

It provides:

- full breakdown of each client portfolio  
- compliance, risk, and constraint review  
- financial and behavioural analysis  
- mandate validation  

It also includes:

#### Portfolio Manager Workflow
Step-by-step decision process used in real-world portfolio management.

#### Checklist
A structured validation list before executing any investment.

This section demonstrates:

- understanding of investment suitability  
- alignment with IPS (Investment Policy Statement)  
- application of institutional portfolio review logic  

---

### 3.5 Dashboard Performance Optimisation

To improve performance:

#### Batch Data Download
Uses:

```python
yf.download(...)