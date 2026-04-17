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