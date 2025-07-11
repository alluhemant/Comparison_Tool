# Comparison_Tool

# 🔍 XML Comparison App

A web-based tool for comparing XML responses from two different sources (e.g., TIBCO and Python).  
Built with **FastAPI**, **Streamlit**, **SQLite**, and **httpx** — designed for extensibility, API-driven workflows, and visual diffs.

---

##  Tech Stack

- [FastAPI]– Backend API
- [Streamlit] –Dashboard UI
- [httpx] – Async HTTP client
- [SQLite] –Lightweight DB for comparisons
- [Pydantic]– `.env`-based config
- [dotenv]– Environment loading

---

##  Features

-  Compare two XML services (e.g., TIBCO vs Python)
-  Detect added, removed, and changed fields
-  Save comparisons to SQLite and view history
-  Visual diff with unified and split view (GitHub-style)
-  Built-in API tester and documentation (via Streamlit sidebar)
-  All config (URLs, ports, DB path) via `.env`

---

##  Project Structure

xml_comparison/
├── app/
│ ├── config.py # Pydantic settings loader
│ ├── models.py # Pydantic models
│ ├── comparisons.db # SQLite DB (generated at runtime)
│ ├── core/
│ │ ├── comparator.py # Diff engine
│ │ └── engine.py # Comparison runner
│ ├── data/
│ │ ├── db.py # DB operations
│ │ └── cache.py # Table schemas
│ ├── api/
│ │ └── endpoints.py # FastAPI routes
│ └── services/
│ └── fetcher.py # External HTTP fetch logic
├── ui/
│ └── dashboard.py # Streamlit UI
├── tests/ # Unit tests
├── main.py # FastAPI entry point
├── run_server.py # Uvicorn run script with env config
├── requirements.txt # All dependencies
├── .env.template # Sample env vars
└── README.md # You are here 📄

1. Set Up Python Virtual Environment

    python -m venv .venv
    source .venv/bin/activate       # macOS/Linux
    # OR
    .venv\Scripts\activate # Windows

2. Install Dependencies
    pip install -r requirements.txt

3. Configure Environment
    cp .env.template .env

Run the Application
    Directly via uvicorn
        uvicorn main:app --host ${APP_HOST} --port ${APP_PORT} --reload
    
    Make sure .env is loaded and variables are available

Launch the Streamlit Dashboard
    streamlit run ui/dashboard.py
    Communicates with FastAPI at: API_BASE_URL from .env

API Endpoints
    
    POST /api/v1/compare → Run a new comparison

    GET /api/v1/latest → Get latest comparison result

    GET /api/v1/ → Root documentation

API Endpoints
    
    Do not commit .env to version control.

    Use pathlib.Path in config for file paths (e.g., DB).

    Use settings = Settings() from config.py across all layers.

    Keep external service URLs configurable.
