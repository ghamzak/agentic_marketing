# Agentic Marketing System Setup Guide

## 1. Clone the Repository
```
git clone https://github.com/ghamzak/agentic_marketing.git
cd agentic_marketing
```

## 2. Python Environment
- Use Python 3.12.x (recommended)
- Create and activate a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Requirements
```
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Install Playwright Browsers (required for scraping features)
```
playwright install
```

## 5. Database Setup
- Start PostgreSQL and create user/database:
  ```sh
  psql postgres
  CREATE USER yourusername WITH PASSWORD 'yourpassword';
  CREATE DATABASE agentic_marketing OWNER yourusername;
  GRANT ALL PRIVILEGES ON DATABASE agentic_marketing TO yourusername;
  \q
  ```
- Copy `.env.example` to `.env` and update with your database credentials and API keys (OpenAI, Tavily, etc.).
- Update `config.py` and `alembic.ini` with your credentials if needed.

## 6. Run Alembic Migrations
- **First-time setup:**
  - If you are starting from scratch (no migrations exist), generate the initial migration:
    ```sh
    alembic revision --autogenerate -m "Initial tables"
    alembic upgrade head
    ```
- **If you cloned the repo and migrations are present:**
  - Just apply all migrations:
    ```sh
    alembic upgrade head
    ```
- **When you make schema changes:**
  - Generate a new migration and apply it:
    ```sh
    alembic revision --autogenerate -m "Describe your change"
    alembic upgrade head
    ```

## 7. Launch the UI
```
PYTHONPATH=. streamlit run agentic_marketing/ui.py
```

## 8. Using the UI
- Enter region, sector, and number of results.
- Click "Run Scraper" to test the agent and save results to the database.
- Lead scoring results are saved to the database and displayed in the UI.
- The UI and agent code are fully synchronous and robust for Streamlit.


## 9. Scraping & Data Collection
- The agent will:
  - Scrape Google Maps for businesses.
  - Perform second-level scraping to check for websites.
  - Use DuckDuckGo to find Instagram accounts.
  - Scrape Yelp for business descriptions.
  - Save results to the database.

## 10. Debugging & Logs
- All process steps and errors are logged to the terminal via Python logging.

## 11. Troubleshooting
- If Streamlit forms or buttons disappear after agent runs, this is due to Streamlit reruns. The UI now uses `st.session_state` to persist generated data and keep forms visible for editing and saving.
---
*This guide will be updated as new features and agents are added.*
