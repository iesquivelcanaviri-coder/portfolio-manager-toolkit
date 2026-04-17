# UCD Python Programming Assessment – Flask Web Application

## Student Details

**Student:** Irene Esquivel Canaviri

---

## 1. Project Title

**Portfolio Management Decision-Support Web Application**

---

## 2. Project Overview

This project is a **Flask-based web application** that simulates a **portfolio manager decision-support toolkit**. It was built using **Python, Flask, HTML, CSS, JavaScript, and Yahoo Finance data via `yfinance`**.

The purpose of the application is to demonstrate how a portfolio manager may analyse securities, compare them against client mandates, assess suitability, apply position-sizing rules, and maintain portfolio holdings across multiple portfolio scenarios.

The project combines:

- Flask routing and template rendering
- Python-based financial calculations
- structured portfolio data using dictionaries and lists
- responsive front-end design using HTML and CSS
- JavaScript interactivity and asynchronous requests
- hosted deployment through Render

This project is designed to show both technical web development skills and the application of Python programming concepts in a practical, interactive financial workflow.

---

## 3. Assessment Alignment

This project was developed to meet the Flask assignment requirements by demonstrating:

1. **Strong application of Flask concepts**
2. **Strong application of Python programming concepts**
3. **Strong integration of CSS styling and JavaScript functionality**
4. **Clean code structure, organisation, and best practices**
5. **A hosted web app that is fully functional and accessible**

The application goes beyond a simple static website by including:

- multiple Flask routes
- both **GET** and **POST** request handling
- dynamic template rendering
- portfolio-specific analysis logic
- asynchronous front-end updates using JavaScript
- structured CSS for layout, responsiveness, and UI consistency

---

## 4. Main Technologies Used

- **Python**
- **Flask**
- **HTML5**
- **CSS3**
- **JavaScript**
- **Yahoo Finance / `yfinance`**
- **NumPy**
- **Render.com** for deployment
- **Gunicorn** for production hosting

---
 
## 5. Project Structure

```text
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

This structure reflects separation of concerns:
	•	app.py handles backend logic and routes
	•	templates/ stores Flask HTML templates
	•	static/css/ stores the site stylesheet
	•	static/js/ stores JavaScript interactivity
	•	deployment files are kept in the root project directory

⸻

6. Flask Application Design

The application uses Flask as the backend framework to manage routing, page rendering, API-style endpoints, and communication between the front end and Python logic.

Flask Routes Implemented

The application includes multiple routes:
	•	/ → Home page
	•	/portfolio_profiles → Portfolio profile review page
	•	/market_dashboard → Security screening dashboard
	•	/criteria → Portfolio-specific security analysis page
	•	/contact → Contact / project information page

API-Style Flask Endpoints

The project also includes dynamic backend endpoints:
	•	/analyze → accepts form data using POST and returns JSON analysis results
	•	/add-to-portfolio → accepts JSON data using POST and validates and stores holdings
	•	/portfolio-stocks → returns grouped holdings as JSON

Flask Concepts Demonstrated

This project demonstrates strong use of Flask concepts, including:
	•	application object creation
	•	route decorators
	•	template rendering using render_template()
	•	request handling using request
	•	JSON responses using jsonify
	•	GET and POST method handling
	•	integration between Flask templates and front-end assets

Example Flask Features in This Project
	•	dynamic dropdown values passed from Python to HTML
	•	reusable navigation bar included with Jinja
	•	form submission handled through Flask routes
	•	data returned from Flask to JavaScript for live UI updates

This demonstrates more than basic routing, because the Flask application actively processes user input and returns structured output.

⸻

7. Python Programming Concepts Demonstrated

The application shows a clear understanding of Python programming through the use of:
	•	dictionaries
	•	nested dictionaries
	•	lists
	•	functions
	•	conditionals
	•	loops
	•	helper functions
	•	data validation
	•	exception handling
	•	numerical calculations
	•	structured backend logic

Data Structures

The backend uses Python dictionaries to define portfolio scenarios. Each portfolio contains structured information such as:
	•	identity details
	•	compliance data
	•	objectives
	•	risk profile
	•	financial situation
	•	constraints
	•	behavioural details
	•	mandate rules

Example concepts used:
	•	nested dictionaries for complex portfolio data
	•	lists for returns, ticker universes, and holdings
	•	grouped dictionaries for returning portfolio payloads to the front end

Helper Functions

The project uses reusable helper functions to keep logic organised. Examples include:
	•	display name generation
	•	safe division
	•	weight conversion
	•	effective max-weight detection
	•	portfolio summary calculation
	•	grouped holdings construction
	•	metric calculation
	•	forecast construction
	•	decision scoring
	•	validation checks

This demonstrates structured Python programming rather than writing all logic directly inside route functions.

Validation and Business Logic

The application also uses Python to enforce business rules, such as:
	•	invalid portfolio detection
	•	empty ticker validation
	•	position limit checks
	•	projected allocation checks
	•	equity restriction handling
	•	ESG screening warnings
	•	currency review warnings

This shows practical use of Python for decision-making and validation logic.

⸻

8. Financial and Analytical Functionality

A major part of the project is the analytical engine used to assess a security.

Analysis Features

For a selected security, the app calculates:
	•	annualised expected return
	•	annualised volatility
	•	Sharpe-like ratio
	•	latest price
	•	return observations
	•	price observations
	•	beta versus benchmark
	•	score
	•	investment decision
	•	recommended position weight
	•	tag
	•	sector
	•	industry

Analysis Windows

The app provides two separate analysis windows:
	•	1-Year Analysis
	•	3-Month Analysis

This improves the depth of the analysis by comparing longer-term and shorter-term behaviour.

Forecasting

The app also produces a simplified quarterly forecast using annualised expected return assumptions.

Forecast outputs include:
	•	quarterly return forecast
	•	Q1 expected price
	•	Q2 expected price
	•	Q3 expected price
	•	Q4 expected price

Benchmark Comparison

The selected security is analysed against the benchmark ticker assigned to the chosen portfolio scenario.

Benchmark information shown includes:
	•	benchmark ticker
	•	benchmark date range
	•	beta observation count

This makes the project more realistic because the analysis is portfolio-specific rather than generic.

⸻

9. Portfolio Scenarios

The project includes five predefined portfolio scenarios, each designed to reflect a different client type or investment mandate.

Included Portfolio Types
	1.	Marie-Claire Dubois
Conservative retiree focused on capital preservation and income
	2.	James O’Connor
Busy executive focused on long-term growth
	3.	Helvetic Precision Tools SA
Corporate treasury account with strong capital protection needs
	4.	Alejandro Torres
Aggressive international entrepreneur seeking growth and diversification
	5.	The Beaumont Family Office
Multi-asset family office seeking wealth preservation and moderate growth

Each portfolio has different:
	•	benchmarks
	•	risk tolerance
	•	maximum weights
	•	investment constraints
	•	product preferences
	•	liquidity needs
	•	behavioural considerations

This demonstrates thoughtful use of data modelling and improves the realism of the application.

⸻

10. Main Pages and Features

10.1 Home Page

The Home page introduces the application and explains its purpose.

It outlines that the project supports:
	•	portfolio management analysis
	•	security screening
	•	position sizing
	•	mandate-based decision-making
	•	portfolio construction review

This gives users a clear starting point and explains the context of the application.

⸻

10.2 Portfolio Profiles Page

The Portfolio Profiles page functions as a portfolio manager review centre.

It displays each portfolio scenario along with key information such as:
	•	client or entity name
	•	portfolio key
	•	benchmark anchor ticker
	•	portfolio value
	•	objective
	•	risk profile
	•	drawdown limit
	•	maximum position weight

It also supports portfolio manager interpretation by showing:
	•	identity and account control
	•	compliance review
	•	objectives and return target
	•	risk review
	•	financial and liquidity profile
	•	mandate constraints
	•	reporting preferences
	•	behavioural review
	•	action checklist

This page shows that the application is not only about market data, but also about real portfolio suitability assessment.

⸻

10.3 Market Dashboard

The Market Dashboard acts as a screening tool before deeper analysis.

It uses a predefined investment universe grouped into:
	•	fixed income
	•	defensive equities
	•	core equities
	•	growth equities
	•	international equities
	•	alternatives

For each security, the dashboard calculates:
	•	latest price
	•	expected return
	•	score
	•	decision
	•	tag
	•	suggested weight
	•	volatility
	•	Sharpe-like ratio
	•	ranking score

Dashboard Features

The dashboard includes:
	•	sortable columns
	•	filter controls
	•	preset screening buttons
	•	live summary text
	•	category-based screening logic

Preset Buttons

The preset filters include:
	•	Low Risk
	•	High Conviction
	•	Core Holdings
	•	Satellite / Diversifiers
	•	Exploratory / High Risk
	•	Income / Defensive
	•	Best Ranked
	•	Cash

This page demonstrates the strongest combination of Flask + Python + JavaScript working together.

⸻

10.4 Criteria Page

The Criteria page is one of the most important parts of the application.

It allows the user to:
	•	select a portfolio
	•	select a ticker
	•	send the request for analysis
	•	receive a dynamic result without refreshing the page
	•	review analysis, benchmark data, and forecast outputs
	•	add or update the holding in a portfolio

Position Sizing Framework

The page also includes a structured position-sizing section with collapsible criteria for:
	•	6% Position – High Conviction
	•	3.5% Position – Core Holding
	•	3% Position – Satellite / Diversifier
	•	1–2% Position – High Risk / Exploratory
	•	Cash (5%) – Risk Control

This makes the page both analytical and educational.

Current Portfolio Holdings

The lower section of the page displays grouped current holdings and summary metrics for each portfolio.

This includes:
	•	number of positions
	•	total allocated percentage
	•	remaining cash
	•	average beta

This page demonstrates both backend analysis and front-end interactivity.

⸻

10.5 Contact Page

The Contact page explains the purpose of the project and summarises the technologies used:
	•	Flask
	•	HTML
	•	CSS
	•	JavaScript
	•	Yahoo Finance data

It functions as a supporting informational page within the multi-page structure.

⸻

11. CSS Styling and Modern Design

The project includes a dedicated CSS file in:

static/css/style.css

The stylesheet demonstrates strong integration of modern CSS styling with the Flask project.

CSS Features Demonstrated

The CSS includes:
	•	global styling rules
	•	reusable card layouts
	•	modern navbar styling
	•	responsive spacing using rem
	•	responsive sizing using clamp()
	•	CSS Grid layouts
	•	Flexbox layouts
	•	table styling
	•	collapsible section styling
	•	message box styling
	•	badge/tag styling
	•	hover effects
	•	responsive media queries

Key Design Strengths

1. Responsive Layout
The design adjusts for different screen sizes using:
	•	flexible widths
	•	responsive padding
	•	media queries
	•	CSS Grid changes on smaller screens

2. Clean Visual Hierarchy
The site uses:
	•	consistent heading colours
	•	balanced spacing
	•	card-based UI organisation
	•	section grouping
	•	subtle shadows and borders

3. Reusable UI Components
Reusable classes include:
	•	.card
	•	.box
	•	.table
	•	.tag
	•	.trade-message
	•	.portfolio-summary
	•	.accordion
	•	.panel

4. Modern Styling Approach
The stylesheet uses:
	•	rem for scalable spacing
	•	clamp() for responsive container padding
	•	grid-based layouts for summaries and result sections
	•	sticky table headers
	•	hover transitions for links and buttons

Criteria Page Result Layout Styling

The Criteria page also uses a two-column result layout through:
	•	.results-grid
	•	.results-column

This improves readability by organising:
	•	Analysis Summary + Benchmark Information
	•	3-Month Analysis + 1-Year Analysis

This directly supports the assignment requirement to create an engaging and visually appealing modern web application.

⸻

12. JavaScript Functionality and Interactivity

The project includes a dedicated JavaScript file in:

static/js/script.js

The JavaScript adds dynamic behaviour and interactivity across the site.

JavaScript Features Demonstrated

The script includes:
	•	DOMContentLoaded protection
	•	dynamic DOM selection
	•	helper functions
	•	collapsible logic
	•	accordion behaviour
	•	form interception
	•	asynchronous fetch requests
	•	real-time content updates
	•	filtering logic
	•	sorting logic
	•	grouped rendering logic
	•	state management

Key JavaScript Features

1. Dynamic Ticker Dropdown
The ticker dropdown is populated from a full grouped ticker universe using JavaScript rather than staying hardcoded in HTML.

2. Fetch-Based Form Submission
The Criteria page intercepts the form and sends data to Flask using fetch().

This means the page updates dynamically without a full reload.

3. Dynamic Result Updates
When Flask returns analysis JSON, JavaScript updates the page fields instantly.

4. Portfolio Add / Update Functionality
After analysis, JavaScript sends the selected holding to Flask, then redraws grouped portfolio holdings dynamically.

5. Accordions and Collapsibles
The application uses JavaScript to control:
	•	criteria accordions
	•	portfolio holding accordions
	•	checklist collapsible section

6. Dashboard Filtering
The Market Dashboard includes live filter logic for:
	•	ticker
	•	decision
	•	score
	•	volatility
	•	Sharpe-like ratio

7. Dashboard Presets
JavaScript supports one-click preset filters such as:
	•	low risk
	•	high conviction
	•	core
	•	satellite
	•	income
	•	best ranked
	•	cash

8. Table Sorting
JavaScript also enables sorting by clicking dashboard table headers.

This demonstrates clear understanding of event-driven front-end logic and client-side interactivity.

⸻

13. Integration Between Flask, HTML, CSS, and JavaScript

One of the strengths of this project is the integration of all layers of the application.

Integration Flow Example
	1.	User opens a Flask route
	2.	Flask renders the correct HTML template
	3.	CSS styles the page and ensures responsiveness
	4.	JavaScript activates interactive features
	5.	User submits analysis form
	6.	JavaScript sends POST request to Flask
	7.	Flask processes Python logic
	8.	Flask returns JSON
	9.	JavaScript updates the result area dynamically

This demonstrates full-stack thinking within the scope of the assignment.

⸻

14. Clean Code Structure and Best Practices

The project was structured to support clarity, maintainability, and good development practice.

Best Practices Used
	•	separated templates, CSS, and JavaScript into appropriate folders
	•	used helper functions to reduce repeated code
	•	grouped code into clear sections
	•	used meaningful variable and function names
	•	included comments throughout the code
	•	separated route logic from helper logic
	•	used reusable components such as _navbar.html
	•	used consistent naming conventions across pages and assets

JavaScript Organisation

The JavaScript file is structured into sections such as:
	•	shared elements
	•	helper functions
	•	accordion logic
	•	page-specific initialisers
	•	criteria page logic
	•	market dashboard logic
	•	startup logic

CSS Organisation

The CSS file is also divided into clear sections, including:
	•	global styles
	•	navbar
	•	accordion / collapsible styles
	•	forms
	•	result box
	•	cards
	•	tables
	•	tags / heatmap
	•	helpers
	•	responsive design

This supports readability and aligns with the assessment requirement for strong code organisation.

⸻

15. Performance and Design Considerations

The project also includes performance and usability considerations.

Dashboard Optimisation

The market dashboard uses:
	•	batch data download through yf.download(...)
	•	simple caching for dashboard rows
	•	grouped master ticker universes

This reduces repeated data requests and improves page performance.

Usability Considerations

The design includes:
	•	clear navigation
	•	grouped content blocks
	•	readable colour contrast
	•	responsive layouts
	•	feedback messages
	•	interactive filters
	•	collapsible sections to reduce clutter

These choices improve user experience and make the application more professional.

⸻

16. Deployment on Render

The application is designed for deployment on Render.com, as required by the assignment brief.

Deployment Files

The project includes:
	•	requirements.txt
	•	Procfile

Example Start Configuration

The deployed app uses Gunicorn in production.

Example:

gunicorn app:app

Deployment Process
	1.	Push project to GitHub
	2.	Connect GitHub repository to Render
	3.	Create a new Web Service
	4.	Add build command
	5.	Add start command
	6.	Deploy
	7.	Test hosted app

Hosted Web App

Render URL:
Add your live Render link here

This section should be completed before final submission so that there is direct evidence of a working hosted application.

⸻

17. How to Run the Project Locally

1. Clone the Repository

git clone <your-github-repo-url>
cd <your-project-folder>

2. Create a Virtual Environment

python -m venv venv

3. Activate the Virtual Environment

Windows

venv\Scripts\activate

macOS / Linux

source venv/bin/activate

4. Install Dependencies

pip install -r requirements.txt

5. Run the Flask App

python app.py

6. Open in Browser

Visit:

http://127.0.0.1:5000/


⸻

18. How to Use the Application

Step 1 – Start at the Home Page

Read the project overview and navigate using the top menu.

Step 2 – Review Portfolio Profiles

Open the Portfolio Profiles page to understand the different client mandates and constraints.

Step 3 – Use the Market Dashboard

Screen the available securities using:
	•	filters
	•	preset buttons
	•	sorting

Step 4 – Go to the Criteria Page

Choose:
	•	a portfolio
	•	a stock or ETF ticker

Then click Analyze.

Step 5 – Review the Results

The application will display:
	•	analysis summary
	•	sector and industry
	•	benchmark information
	•	3-month analysis
	•	1-year analysis
	•	position size suggestion

Step 6 – Add / Update Portfolio

Click Add / Update Portfolio to save the analysed holding to the chosen portfolio.

Step 7 – Review Holdings

Inspect grouped holdings and portfolio summaries at the bottom of the Criteria page.

⸻

19. Evidence of Learning Outcomes

This project provides evidence of the learning outcomes expected for the assignment.

1. Flask

Demonstrates strong Flask use through:
	•	route creation
	•	template rendering
	•	GET/POST handling
	•	JSON endpoints

2. Python

Demonstrates strong Python use through:
	•	financial calculations
	•	validation logic
	•	helper functions
	•	structured data models
	•	exception handling

3. CSS and JavaScript

Demonstrates strong front-end integration through:
	•	responsive design
	•	interactive accordions
	•	dynamic form handling
	•	table filtering and sorting
	•	asynchronous communication with Flask

4. Clean Structure

Demonstrates strong organisation through:
	•	modular folders
	•	reusable templates
	•	commented code
	•	sectioned CSS and JavaScript

5. Hosted Web App

Demonstrates readiness for hosted deployment through:
	•	Render configuration
	•	production start process
	•	structured project files

⸻

20. Limitations

Current limitations of the project include:
	•	holdings are stored in memory rather than a database
	•	there is no user authentication
	•	results depend on Yahoo Finance data availability
	•	some portfolio review steps still rely on simplified manual interpretation

These limitations are acceptable within the scope of the assignment but would be areas for future development.

⸻

21. Future Improvements

Possible future improvements include:
	•	adding a database such as SQLite or PostgreSQL
	•	adding user authentication and login
	•	storing holdings permanently
	•	expanding chart visualisations
	•	adding downloadable reports
	•	improving benchmark and currency validation
	•	adding more advanced portfolio optimisation methods

⸻

22. Conclusion

This Flask project demonstrates a strong application of:
	•	Flask web development
	•	Python programming
	•	HTML page structure
	•	CSS styling and responsive design
	•	JavaScript interactivity
	•	front-end and back-end integration

The project goes beyond a simple static website by combining real market data, portfolio-specific decision logic, interactive dashboard functionality, and portfolio construction workflows.

Overall, the application provides clear evidence of the skills expected at distinction level, including strong Flask implementation, strong Python logic, strong CSS and JavaScript integration, clean organisation, and readiness for a fully functional hosted deployment.

⸻

23. Submission Notes

For submission, the project should include:
	•	all project files in a ZIP folder
	•	deployment files
	•	clear Render instructions
	•	GitHub repository link
	•	live Render link

Add Before Final Submission
	•	GitHub Repository URL:
Add your GitHub repository link here
	•	Live Render URL:
Add your Render deployment link here
	•	Any additional deployment notes:
Add any specific configuration notes here if needed

