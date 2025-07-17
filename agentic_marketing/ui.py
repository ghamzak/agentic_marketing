"""
Streamlit UI for testing agents: allows user to input region, sector, and number of results (k).
Displays results and saves to the database using the Business model.
"""

import streamlit as st

from agentic_marketing.agents.web_scraper_agent import WebScraperAgent
from agentic_marketing.agents.lead_scoring_agent_alternative import LeadScoringAgentAlternative
from agentic_marketing.models import Business, Base
from agentic_marketing.database import engine, SessionLocal

# Ensure an event loop exists for OpenAI Agents SDK Runner.run_sync
import asyncio
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
from sqlalchemy import select, inspect


st.title("Agentic Marketing: Business Discovery & Lead Scoring")

with st.form("scraper_form"):
    region = st.text_input("Target Geography (Region/City)", "Portland, OR")
    sector = st.text_input("Business Sector", "restaurants")
    k = st.number_input("Number of results (k)", min_value=1, max_value=50, value=10)
    submitted = st.form_submit_button("Run Scraper")


def get_business_columns():
    insp = inspect(Business)
    return [col.name for col in insp.columns]


def save_businesses(businesses):
    import logging
    logger = logging.getLogger("save_businesses")
    with SessionLocal() as session:
        for b in businesses:
            cols = get_business_columns()
            filtered = {k: v for k, v in b.items() if k in cols}
            logger.info(f"Attempting to add business: {filtered}")
            try:
                business = Business(**filtered)
                session.add(business)
            except Exception as e:
                logger.error(f"Error adding business: {filtered}\nException: {e}")
        try:
            session.commit()
        except Exception as e:
            logger.error(f"Error during session.commit(): {e}")


def run_scraper(region, sector, k):
    process_log = []
    process_log.append(f"Initialized WebScraperAgent for region='{region}', sector='{sector}', k={k}")
    agent = WebScraperAgent(region=region, sector=sector, max_results=k)
    process_log.append("Calling find_businesses_without_websites()...")
    businesses = agent.find_businesses_without_websites()
    import types
    if isinstance(businesses, types.CoroutineType):
        raise RuntimeError("WebScraperAgent.find_businesses_without_websites() returned a coroutine. This method must be synchronous and return a list.")
    process_log.append(f"Scraping complete. {len(businesses)} businesses found.")
    process_log.append("Saving businesses to database...")
    save_businesses(businesses)
    process_log.append("Database save complete.")
    return businesses



def get_event_loop():
    pass  # No longer needed


def fetch_businesses():
    with SessionLocal() as session:
        result = session.execute(select(Business.id, Business.name, Business.website, Business.region, Business.industry, Business.description, Business.yelp_description, Business.trends))
        return result.fetchall()

def select_businesses_ui(businesses):
    st.markdown("### Select Businesses for Lead Scoring")
    selected = []
    for b in businesses:
        label = f"{b.name} ({b.website or 'no website'})"
        if st.checkbox(label, key=f"select_{b.id}"):
            selected.append(b)
    return selected

def run_lead_scoring(selected_businesses):
    st.markdown("### Lead Scoring Progress")
    progress_bars = [st.progress(0, text=f"Scoring {b.name}") for b in selected_businesses]
    agent = LeadScoringAgentAlternative([b._asdict() for b in selected_businesses])
    # Optionally show progress, but use process_and_save_leads for DB save
    for idx, business in enumerate(selected_businesses):
        progress_bars[idx].progress(10, text=f"Scoring {business.name}...")
        # The actual scoring is done in process_and_save_leads
        progress_bars[idx].progress(100, text=f"Done: {business.name}")
    results = agent.process_and_save_leads()
    return results

if submitted:
    with st.spinner("Running web scraper agent..."):
        results = run_scraper(region, sector, k)
        import types
        if isinstance(results, types.CoroutineType):
            raise RuntimeError("run_scraper() returned a coroutine. This method must be synchronous and return a list.")
    st.success(f"Found {len(results)} businesses.")
    st.write(results)

# --- Lead Scoring UI ---
st.markdown("---")
st.header("Lead Scoring Agent (Alternative)")

businesses = fetch_businesses()
if not businesses:
    st.info("No businesses found in the database. Run the scraper first.")
else:
    selected = select_businesses_ui(businesses)
    if selected:
        if st.button("Run Lead Scoring on Selected Businesses"):
            scoring_results = run_lead_scoring(selected)
            st.success("Lead scoring complete!")
            st.markdown("### Lead Scoring Results")
            st.dataframe(scoring_results)
