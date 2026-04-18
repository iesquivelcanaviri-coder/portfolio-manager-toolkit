# UCD Python PORTFOLIO Assessment – Flask Web Application

## Student Details

**Student:** Irene Esquivel Canaviri

---

## Project Title

**Portfolio Management Decision-Support Web Application**

### Submission Links
* **GitHub Repository:** [https://github.com/iesquivelcanaviri-coder/portfolio-manager-toolkit.git](https://github.com/iesquivelcanaviri-coder/portfolio-manager-toolkit.git)
* **Live Render URL:** [https://portfolio-manager-toolkit.onrender.com](https://portfolio-manager-toolkit.onrender.com)

---
## Project Overview

This project is a Flask web application designed to simulate a simple portfolio manager decision-support tool.

I wanted the application to go beyond a basic multi-page website, so I built it around a practical financial workflow. The idea is that a user can review different client portfolio profiles, analyse a stock or ETF against a chosen portfolio, look at market dashboard results, and then decide whether that security is suitable for the portfolio.

The application was built using:

- Python
- Flask
- HTML
- CSS
- JavaScript
- Yahoo Finance data through `yfinance`
- NumPy

The project brings together both backend and frontend work. On the backend, Flask handles routing, rendering templates, processing requests, and running the financial logic. On the frontend, HTML, CSS, and JavaScript are used to create a clean interface, interactive filtering, and live updates without reloading the page.

Overall, this project was created to demonstrate Flask development, Python programming, and integration of web technologies in a more realistic and applied way.

---

## Assessment Alignment

This project was developed to meet the Flask assignment requirements by showing:

1. A clear understanding of Flask concepts
2. A strong application of Python programming
3. Good integration of CSS styling and JavaScript functionality
4. Clean code structure and organisation
5. A hosted web application that is accessible online

Rather than building a purely static website, I designed the project so that it includes:

- multiple Flask routes
- template rendering with Jinja
- GET and POST handling
- structured Python data
- reusable helper functions
- dynamic JavaScript behaviour
- styling for layout, responsiveness, and usability
- deployment through Render

---

## Main Technologies Used

- **Python**
- **Flask**
- **HTML5**
- **CSS3**
- **JavaScript**
- **NumPy**
- **yfinance**
- **Render**
- **Gunicorn**

---

## Project Structure
```
PORTFOLIO-MANAGEMENT-DECISION-SUPPORT-TOOL/
│
├── app.py
├── Procfile
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── templates/
    ├── _navbar.html
    ├── index.html
    ├── contact.html
    ├── criteria.html
    ├── market_dashboard.html
    └── portfolio_profiles.html


This structure helped me keep the project organised and easier to maintain:

* **app.py** contains the Flask app, routes, helper functions, and financial logic
* **templates/** contains all HTML templates used by Flask
* **static/css/** contains the stylesheet
* **static/js/** contains the JavaScript for interactivity
* **deployment files** such as `Procfile` and `requirements.txt` are stored in the root directory


## Flask Implementation

Flask is the core of the application and is used for both page rendering and backend processing.

### Main Flask routes
The application includes several page routes:
* `/`
* `/criteria`
* `/market_dashboard`
* `/portfolio_profiles`
* `/contact`

Each route uses render_template() to return the correct HTML page.

### API-style routes
In addition to standard page routes, I also created backend endpoints that return JSON:
* `/analyze`
* `/add-to-portfolio`
* `/portfolio-stocks`

These routes make the project more interactive because JavaScript can send requests and receive results without reloading the page.

### Jinja templating
I used Jinja inside the templates to:
* include a reusable navbar
* loop through portfolio and dashboard data
* display dynamic values from Python
* keep the active page highlighted in the navigation

This helped reduce repetition and made the templates more connected to the Flask backend.

---

## Python Programming and Logic

A large part of the project demonstrates Python programming rather than only Flask routing.

### Data structures
I used nested dictionaries and lists to model the portfolio scenarios. Each portfolio includes:
* identity information
* compliance details
* objectives
* risk profile
* financial data
* constraints
* preferences
* behavioural notes
* mandate information

This allowed me to build a more realistic dataset and show how Python structures can be used to support application logic.

### Helper functions
To keep the code clean and avoid repeating logic, I separated key calculations into helper functions. Examples include:
* safe division
* weight parsing
* effective maximum weight calculation
* portfolio summary calculation
* default metric handling
* financial metric computation
* quarterly forecast generation
* score and decision logic
* validation before adding securities to portfolios

This made the application easier to read, test, and extend.

### Financial calculations
The application calculates:
* annualised expected return
* annualised volatility
* Sharpe-like ratio
* beta against a benchmark
* quarterly forecast prices

These calculations are used both in the criteria analysis and in the market dashboard.

### Validation logic
When a user adds a security to a portfolio, the backend checks:
* position size limits
* projected allocation
* legal restrictions
* ESG-related restrictions
* warnings on currency and other suitability points

This shows practical Python use in business rules and validation.

---

## Frontend Design: HTML, CSS, and JavaScript

### HTML
The project includes at least five HTML pages, which meets the assignment requirement. Each page has a clear structure and supports the overall user workflow.

The main pages are:
* Home
* Portfolio Profiles
* Market Dashboard
* Criteria
* Contact

The HTML is designed to work closely with Flask and Jinja, so content can be filled dynamically from the backend.

### CSS
The CSS was written in a separate file inside `static/css/style.css`, following Flask best practice. My CSS focuses on making the application look clean, consistent, and professional. I used:
* shared global styles
* card-based layout sections
* navigation styling
* form styling
* result box styling
* table styling
* accordion and collapsible section styling
* responsive design for smaller screens

Some stronger styling choices in the project include:
* use of `clamp()` for flexible spacing
* use of `rem` units for more consistent scaling
* CSS Grid for portfolio summaries and result layouts
* consistent colour theme across headings, cards, buttons, and tables
* media queries for mobile responsiveness
* score heatmap colours, tag badges, and message states (info, success, error)

### JavaScript
The JavaScript is stored in `static/js/script.js` and is used to add interactivity across the site. Main features include:
* dynamic ticker dropdown generation
* collapsible checklist and accordion behaviour
* asynchronous form submission using `fetch()`
* real-time update of analysis results
* add/update portfolio workflow
* grouped holdings rendering
* market dashboard filtering, preset screening buttons, and sortable columns

#### Criteria page JavaScript
On the Criteria page, JavaScript:
* intercepts form submission
* sends the selected ticker and portfolio to Flask
* receives JSON analysis results
* updates the page without reloading
* enables the Add / Update Portfolio button only after successful analysis

This creates a smoother experience and demonstrates practical use of asynchronous JavaScript.

#### Market Dashboard JavaScript
On the Market Dashboard page, JavaScript handles:
* manual filters and smart preset buttons
* dynamic row visibility
* sorting by clicking table headers
* summary text updates after filtering

This helps turn the dashboard into a usable screening tool rather than just a static table.

---

## Main Features of the Application

### 1. Portfolio Profiles Page
This page introduces the portfolio scenarios used by the application. Each profile includes a summary of:
* Objective
* Risk profile
* Drawdown limit
* Maximum position weight
* Benchmark/reference ticker
* Broader portfolio context

This page helps the user understand the different client mandates before carrying out analysis.

### 2. Criteria Page
This is one of the main functional pages of the project. The user selects a portfolio and a ticker. The application then analyses that security in the context of the selected portfolio.

The output includes:
* Portfolio name
* Beta
* Score
* Decision
* Recommended weight
* Sector
* Industry
* Tag

It also includes two analysis windows: **3-Month Analysis** and **1-Year Analysis**. For both periods, the app displays:
* Expected return
* Volatility
* Sharpe-like ratio
* Latest price
* Start and end dates
* Number of observations
* Quarterly forecast values

It also shows benchmark information used in the beta calculation. After analysis, the user can add or update the security in the chosen portfolio.

### 3. Add / Update Portfolio Workflow
After a successful analysis, the user can save the position into a portfolio. When this happens, Flask validates the proposed addition and then either:
* Adds the security if it is new
* Updates the existing entry if it already exists

The grouped portfolio section then refreshes to show:
* Current holdings
* Number of positions
* Total allocated percentage
* Remaining cash percentage
* Average beta

This makes the page feel more like a real workflow rather than a single one-off calculation.

### 4. Market Dashboard
The Market Dashboard acts as a screening tool. It uses a larger predefined ticker universe grouped into categories such as:
* Fixed income
* Defensive equities
* Core equities
* Growth equities
* International equities
* Alternatives

For each security, the application calculates and displays:
* Latest price
* Expected return
* Score
* Decision
* Tag
* Suggested weight
* Volatility
* Sharpe-like ratio
* Ranking score

#### The page also includes:

* manual filters
* quick preset buttons
* sortable columns
* colour-coded score bands
* summary text after filtering

The page also includes manual filters, quick preset buttons, sortable columns, colour-coded score bands, and summary text after filtering. This is one of the stronger parts of the project because it combines backend calculations with frontend interaction.

## Performance and Data Handling

The dashboard is heavier than the other pages, so I added some optimisation logic.

### Batch download
Instead of downloading each ticker separately, the dashboard uses a batch **yfinance** request to retrieve market data more efficiently.

### Cache
The dashboard results are cached for a limited period so the app does not rebuild the full dataset every time the page loads.

python
dashboard_cache = {
    "rows": None,
    "timestamp": 0
}

DASHBOARD_CACHE_SECONDS = 300


This reduces repeated processing and improves responsiveness.

## Clean Code and Best Practices

I tried to keep the project structured and readable throughout.

Some of the practices followed in this project include:

* Separating backend, templates, styles, and scripts
* Using helper functions for repeated logic
* Keeping page-specific JavaScript grouped into sections
* Using meaningful variable names
* Keeping templates reusable with Jinja includes
* Storing static files in the correct Flask directories
* Including comments where the logic is more complex
* Separating route handling from calculation logic as much as possible

The project is not just functional, but also organised in a way that makes it easier to explain, debug, and improve.

---

## Hosting and Deployment

The application was prepared for deployment using **Render**.

Deployment-related files include:
* `requirements.txt`
* `Procfile`

The project is served in production using **Gunicorn**.

### Deployment steps followed
1. Push the project to GitHub
2. Connect the repository to Render
3. Create a new web service
4. Set the build and start commands
5. Deploy the application
6. Test the live URL after deployment

---

## Submission Links

* **GitHub Repository:** [https://github.com/iesquivelcanaviri-coder/portfolio-manager-toolkit.git](https://github.com/iesquivelcanaviri-coder/portfolio-manager-toolkit.git)
* **Live Render URL:** [https://portfolio-manager-toolkit.onrender.com](https://portfolio-manager-toolkit.onrender.com)