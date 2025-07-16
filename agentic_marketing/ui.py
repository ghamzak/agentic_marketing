"""
Streamlit UI for testing agents: allows user to input region, sector, and number of results (k).
Displays results and saves to the database using the Business model.
"""
import streamlit as st
import asyncio
from agentic_marketing.agents.web_scraper_agent import WebScraperAgent
from agentic_marketing.models import Business, Base
from agentic_marketing.database import engine, AsyncSessionLocal
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

st.title("Agentic Marketing: Business Discovery Agent Tester")

with st.form("scraper_form"):
    region = st.text_input("Target Geography (Region/City)", "Portland, OR")
    sector = st.text_input("Business Sector", "restaurants")
    k = st.number_input("Number of results (k)", min_value=1, max_value=50, value=10)
    submitted = st.form_submit_button("Run Scraper")

async def get_business_columns():
    insp = inspect(Business)
    return [col.name for col in insp.columns]

async def save_businesses(businesses):
    async with AsyncSessionLocal() as session:
        for b in businesses:
            # Only keep keys that match Business columns
            cols = await get_business_columns()
            filtered = {k: v for k, v in b.items() if k in cols}
            business = Business(**filtered)
            session.add(business)
        await session.commit()

async def run_scraper(region, sector, k):
    process_log = []
    process_log.append(f"Initialized WebScraperAgent for region='{region}', sector='{sector}', k={k}")
    agent = WebScraperAgent(region=region, sector=sector, max_results=k)
    process_log.append("Calling find_businesses_without_websites()...")
    businesses = await agent.find_businesses_without_websites()
    process_log.append(f"Scraping complete. {len(businesses)} businesses found.")
    process_log.append("Saving businesses to database...")
    await save_businesses(businesses)
    process_log.append("Database save complete.")
    return businesses

if submitted:
    with st.spinner("Running web scraper agent..."):
        results = asyncio.run(run_scraper(region, sector, k))
    st.success(f"Found {len(results)} businesses.")
    st.write(results)
    # st.markdown("### Process Log (Debug)")
    # for entry in process_log:
    #     st.write(entry)
