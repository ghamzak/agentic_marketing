# Error Report: Agentic Marketing System Setup & Usage

## 1. ModuleNotFoundError: No module named 'agentic_marketing'
**Cause:** Streamlit could not find the package because the Python path was not set correctly.
**Resolution:** Run Streamlit with the correct PYTHONPATH:
```
PYTHONPATH=. streamlit run agentic_marketing/ui.py
```

## 2. Playwright Browser Executable Not Found
**Error:**
```
playwright._impl._errors.Error: BrowserType.launch: Executable doesn't exist ...
Looks like Playwright was just installed or updated. Please run the following command to download new browsers:
playwright install
```
**Resolution:** Run the following command in your project directory:
```
playwright install
```

## 3. Alembic Migration Errors
- Missing `script.py.mako` template: Added the file manually.
- Syntax errors in template: Fixed template logic for revision variables and imports.
- Database connection errors: Updated `alembic.ini` with correct credentials.
- Alembic workflow clarified: For first-time setup, generate the initial migration; for ongoing changes, generate and apply new migrations. See `setup.md` for details.

## 4. Scraper Selector Timeout
**Error:** `Timeout exceeded waiting for locator("input[aria-label='Search Google Maps']")`  
**Resolution:** Updated selector to `#searchboxinput` after inspecting Google Maps HTML.

## 5. Database Authentication Error
**Error:** `asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "user"`  
**Resolution:** Updated `.env` (copied from `.env.example`) and `alembic.ini` with correct PostgreSQL credentials.

## 6. Scraping Logic Issues
**Error:** Businesses with websites were included; Instagram search failed due to Google blocking bots.  
**Resolution:** Added second-level scraping for website detection; switched Instagram lookup to DuckDuckGo.

## 7. Type Errors in Business Parsing
**Error:** Function with declared return type `List[Dict]` must return value on all code paths.  
**Resolution:** Ensured all parsing functions return a list, even on error.

## 8. Logging and Debugging
**Change:** Process logs are now sent to terminal via Python logging, not displayed in the UI.

---


## 9. Schema & Robustness Improvements (July 2025)
**Change:** The `leads` table now uses a `reasoning` (Text) column instead of `enriched_data` (JSON). All code and migrations have been updated accordingly. If you are migrating from an older version, ensure your data and code use the new `reasoning` field.

**Change:** The UI and agent code are now fully synchronous and robust for Streamlit. All lead scoring results are saved to the database and displayed in the UI without event loop or session errors.

**Change:** Added `.env.example` to the repo for environment variable setup. Users should copy this to `.env` and fill in their credentials and API keys.

**Change:** Streamlit UI now uses `st.session_state` to persist generated data and keep forms visible for editing and saving. If forms or buttons disappear after agent runs, this is due to Streamlit reruns and is now handled.

---

## General Advice
- Always run Streamlit and other scripts from the project root.
- Ensure all environment variables and database credentials are set up before running migrations or agents.
- All scraping selectors and logic are updated per latest HTML structures.
- All errors and fixes are logged for future reference.