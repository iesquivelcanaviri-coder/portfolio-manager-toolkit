# UCD Python Programming Assessment – Flask Project

## Student Details  
**Student:** Irene Esquivel Canaviri  

---

# 1. Project Overview

This project is a Flask-based web application designed as a **Portfolio Manager Decision-Support Toolkit**.

It demonstrates the practical application of **Python, Flask, HTML, CSS, and JavaScript** to build a structured, data-driven web application aligned with real-world financial workflows.

The application simulates how a portfolio manager:

- evaluates securities  
- assesses risk and return  
- validates investments against portfolio mandates  
- determines position sizing  
- constructs and monitors portfolios  

The project integrates:

- structured portfolio data (Python dictionaries)  
- live market data via `yfinance`  
- decision-making logic (scoring and classification engine)  
- dynamic front-end rendering using JavaScript  
- responsive UI using modern HTML and CSS  

---

# 2. Assignment Requirements Mapping

This project directly addresses all assignment requirements:

## A. Flask Environment
- Flask application created using `app.py`
- Virtual environment used (`.venv`)
- Dependencies managed via `requirements.txt`

## B. Flask Application
Routes implemented:
- `/` → Home  
- `/criteria` → Analysis engine  
- `/market_dashboard` → Screening tool  
- `/portfolio_profiles` → Portfolio overview  
- `/contact` → Project information  

## C. HTML Files
The project includes multiple HTML templates:

- `index.html`
- `criteria.html`
- `market_dashboard.html`
- `portfolio_profiles.html`
- `contact.html`
- `_navbar.html` (reusable component)

All pages:
- follow a consistent layout  
- use semantic HTML structure  
- are rendered using Flask (`render_template`)  

## D. CSS Styling
- Centralised styling in `static/css/style.css`
- Modern UI design:
  - cards layout  
  - responsive grid  
  - navbar navigation  
  - tables and visual hierarchy  

## E. JavaScript Functionality
- Implemented in `static/js/script.js`
- Provides:
  - dynamic table rendering  
  - filtering and sorting  
  - API interaction with Flask  
  - portfolio updates without page reload  
  - accordion and collapsible UI components  

## F. Integration
- CSS linked via `<link>` in all HTML files  
- JavaScript loaded via `<script>` before closing `</body>`  
- Flask routes return dynamic data (JSON + templates)  

## G. Flask Data & Logic
- Uses dictionaries for:
  - portfolios  
  - constraints  
  - market universe  
- Implements:
  - GET routes (page rendering)  
  - POST routes (analysis + portfolio updates)  
- Includes validation, scoring, and decision logic  

## H. Testing
- All routes tested locally  
- Front-end interactions verified  
- API responses validated  

## I. Deployment (Render)
- Hosted on Render.com  
- GitHub repository connected  
- Live application accessible  

---

# 3. Project Structure

```
portfolio-manager-toolkit/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── templates/
│   ├── _navbar.html
│   ├── index.html
│   ├── criteria.html
│   ├── market_dashboard.html
│   ├── portfolio_profiles.html
│   ├── contact.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

---

# 4. Architecture and Design Approach

The application follows a **clear separation of concerns**:

| Layer | Responsibility |
|------|--------|
| Flask (Python) | Data processing, business logic, API responses |
| HTML (Jinja) | Page structure and layout |
| CSS | Styling and visual design |
| JavaScript | Dynamic rendering and interactivity |

### Design Decision

Dynamic content (e.g. portfolio tables) is generated using JavaScript.

This ensures:
- real-time updates  
- separation of data and UI  
- maintainable structure  

---

# 5. Core Features

## 5.1 Portfolio-Based Security Analysis

Users can:
- select a portfolio  
- select a ticker  

The system computes:
- expected return  
- volatility  
- Sharpe-like ratio  
- beta  
- decision classification  
- recommended position size  

Includes:
- 1-year analysis  
- 3-month analysis  
- quarterly forecast  

---

## 5.2 Portfolio Construction Workflow

Users can:
- add securities  
- update positions  

Validation includes:
- weight constraints  
- allocation limits  
- mandate rules  

Portfolio summary:
- positions count  
- total allocation  
- remaining cash  
- average beta  

---

## 5.3 Market Dashboard

Acts as a screening tool with:

- large asset universe  
- ranking system  
- sortable table  
- preset filters:
  - low risk  
  - high conviction  
  - core  
  - satellite  
  - exploratory  
  - income  
  - best ranked  
  - cash  

---

## 5.4 Portfolio Profiles

Provides:
- portfolio descriptions  
- constraints  
- investment guidelines  

Demonstrates:
- understanding of mandates  
- structured decision workflows  

---

## 5.5 Performance Optimisation

### Batch Data Download
```python
yf.download(...)
```

### Caching Mechanism
Improves performance and reduces API calls.

---

# 6. JavaScript Design Approach

JavaScript is used for:

- API communication (`fetch`)  
- DOM manipulation  
- dynamic table generation  
- filtering and sorting  

Dynamic elements are built using:
- `createElement()`  
- template literals (controlled usage)  

---

# 7. Deployment

**Live Application:**  
https://portfolio-manager-toolkit.onrender.com

### Process

1. Code pushed to GitHub  
2. Render pulls repository  
3. Dependencies installed  
4. App deployed  
5. Public URL generated  

---

# 8. How to Run Locally

```bash
python -m venv venv

# Activate
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
python app.py
```

Open:
```
http://127.0.0.1:5000/
```

---

# 9. Conclusion

This project demonstrates:

- strong Flask implementation  
- structured Python logic  
- integration of front-end technologies  
- clean architecture  
- real-world financial modelling  

It represents a complete **decision-support system** aligned with both academic and professional standards.