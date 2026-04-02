# portfolio-manager-toolkit
A Flask-based portfolio manager decision-support toolkit with risk analysis, return diagnostics, and client profiling.





### Local Development Workflow

My Computer
   │
   ├── Create virtual environment (.venv) for local testing
   ├── Install Flask and dependencies
   ├── Run app locally using: python app.py
   │
   ▼
Flask loads:
   - templates/index.html  → HTML pages
   - static/css/style.css  → styling
   - static/js/script.js   → interactions



### Project Structure

portfolio-manager-toolkit/
│
├── app.py               → Main Flask application
├── requirements.txt     → Dependencies for deployment
├── Procfile             → Tells Render how to run the app
├── .gitignore           → Prevents uploading .venv and cache files
├── README.md            → Project documentation
│
├── templates/           → HTML templates
│     └── index.html
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
