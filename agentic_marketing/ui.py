"""
Streamlit UI for testing agents: allows user to input region, sector, and number of results (k).
Displays results and saves to the database using the Business model.
"""

import streamlit as st

from agentic_marketing.agents.web_scraper_agent import WebScraperAgent
from agentic_marketing.agents.lead_scoring_agent_alternative import LeadScoringAgentAlternative
from agentic_marketing.agents.persona_and_marketing_agent import PersonaAndMarketingAgent
from agentic_marketing.utils.persona_input import get_leads_with_business_info
from agentic_marketing.models import Business, Lead, Persona, OutreachContent, Base
from agentic_marketing.database import engine, SessionLocal
import streamlit as st
from sqlalchemy import select
import logging

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
st.header("Lead Scoring Agent")

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

# --- Persona & Marketing Agent UI (Moved to bottom) ---
st.markdown("---")
st.header("Persona & Marketing Generator Agent")


# Fetch all leads and businesses separately, join in Python
logging.basicConfig(level=logging.DEBUG)
with SessionLocal() as session:
    leads = session.query(Lead).all()
    businesses = {b.id: b for b in session.query(Business).all()}

if not leads:
    st.info("No leads found. Run lead scoring first.")
else:
    # Let user select one lead at a time, show business name if available
    lead_options = {}
    for l in leads:
        b = businesses.get(l.business_id)
        label = f"{b.name if b else 'Unknown'} (Prob: {l.predicted_probability})"
        lead_options[label] = l.id
    selected_lead_id = st.selectbox("Select a lead to generate persona and marketing content:", list(lead_options.keys()), key="persona_marketing_lead_selectbox")
    lead_id = lead_options[selected_lead_id]

    # Button to run agent and store result in session_state
    if st.button("Generate Persona & Marketing Content"):
        lead_dicts = get_leads_with_business_info([lead_id])
        logging.info('lead_dicts: %s', lead_dicts)
        if not lead_dicts:
            st.error("Could not fetch lead/business info.")
        else:
            agent = PersonaAndMarketingAgent(lead_dicts)
            result = agent.run()[0]
            st.session_state["persona_marketing_result"] = result
            st.session_state["persona_marketing_lead_id"] = lead_id

    # Show the form if we have persona/content in session_state for this lead
    result = st.session_state.get("persona_marketing_result")
    session_lead_id = st.session_state.get("persona_marketing_lead_id")
    if result and session_lead_id == lead_id:
        with st.form("persona_marketing_form"):
            persona = result["persona_json"]
            persona_name = st.text_input("Persona Name", persona.get("name", ""))
            persona_age = st.text_input("Persona Age", str(persona.get("age", "")))
            persona_interests = st.text_area("Persona Interests", ", ".join(persona.get("interests", [])))
            persona_pain_points = st.text_area("Persona Pain Points", ", ".join(persona.get("pain_points", [])))
            persona_goals = st.text_area("Persona Goals", ", ".join(persona.get("goals", [])))
            persona_channels = st.text_area("Preferred Channels", ", ".join(persona.get("preferred_channels", [])))
            # Editable marketing content for each channel
            channel_contents = result["channel_contents"]
            edited_contents = {}
            for channel, content in channel_contents.items():
                edited_contents[channel] = st.text_area(f"{channel.title()} Content", content)
            submitted = st.form_submit_button("Save Persona & Content")
            print("Form submit button pressed:", submitted)
            if submitted:
                print("=== STARTING SAVE OPERATION ===")
                try:
                    persona_obj = Persona(
                        lead_id=lead_id,
                        persona_json={
                            "name": persona_name,
                            "age": persona_age,
                            "interests": [i.strip() for i in persona_interests.split(",") if i.strip()],
                            "pain_points": [i.strip() for i in persona_pain_points.split(",") if i.strip()],
                            "goals": [i.strip() for i in persona_goals.split(",") if i.strip()],
                            "preferred_channels": [i.strip() for i in persona_channels.split(",") if i.strip()]
                        }
                    )
                    with SessionLocal() as session:
                        # Check for existing persona for this lead
                        existing_persona = session.query(Persona).filter_by(lead_id=lead_id).first()
                        if existing_persona:
                            print(f"Persona for lead_id={lead_id} already exists, skipping insert.")
                        else:
                            session.add(persona_obj)
                            session.flush()
                            print(f"Persona added and flushed for lead_id={lead_id}")
                        # Save outreach content for each channel, avoid duplicates
                        for channel, content in edited_contents.items():
                            existing_outreach = session.query(OutreachContent).filter_by(lead_id=lead_id, channel=channel).first()
                            if existing_outreach:
                                print(f"OutreachContent for lead_id={lead_id}, channel={channel} already exists, skipping insert.")
                            else:
                                outreach = OutreachContent(
                                    lead_id=lead_id,
                                    channel=channel,
                                    content=content
                                )
                                session.add(outreach)
                                session.flush()
                                print(f"OutreachContent added and flushed for lead_id={lead_id}, channel={channel}")
                        session.commit()
                        print("Session committed for persona and outreach content.")
                    st.success("Persona and marketing content saved!")
                except Exception as e:
                    logging.exception("Error saving persona or outreach content to database")
                    print("EXCEPTION DURING SAVE:", e)
                    st.error(f"Error saving to database: {e}")
