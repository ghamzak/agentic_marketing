"""
Utility to fetch leads joined with business info for persona and marketing agent input.
"""
from typing import List, Dict
from agentic_marketing.models import Lead, Business
from agentic_marketing.database import SessionLocal
from sqlalchemy.orm import joinedload

def get_leads_with_business_info(lead_ids: List[int]) -> List[Dict]:
    """
    Fetches leads by id, joined with their business info, returns dicts for persona agent.
    """
    import logging
    logger = logging.getLogger("persona_input_debug")
    logger.warning(f"get_leads_with_business_info called with lead_ids: {lead_ids}")
    with SessionLocal() as session:
        leads = session.query(Lead).filter(Lead.id.in_(lead_ids)).all()
        business_ids = [lead.business_id for lead in leads]
        businesses = {b.id: b for b in session.query(Business).filter(Business.id.in_(business_ids)).all()}
        logger.warning(f"Fetched {len(leads)} leads and {len(businesses)} businesses from DB.")
        results = []
        for lead in leads:
            business = businesses.get(lead.business_id)
            logger.warning(f"Lead: id={lead.id}, business_id={lead.business_id}, business={business}")
            if business:
                logger.warning(f"Business fields: name={business.name}, industry={business.industry}, region={business.region}, description={business.description}, yelp_description={getattr(business, 'yelp_description', None)}, trends={getattr(business, 'trends', None)}")
            else:
                logger.warning(f"No business found for lead id={lead.id}")
            results.append({
                "id": lead.id,
                "reasoning": lead.reasoning,
                "predicted_probability": lead.predicted_probability,
                "name": business.name if business else None,
                "industry": business.industry if business else None,
                "region": business.region if business else None,
                "description": business.description if business else None,
                "yelp_description": getattr(business, "yelp_description", None) if business else None,
                "trends": getattr(business, "trends", None) if business else None,
            })
        logger.warning(f"Returning {len(results)} results from get_leads_with_business_info.")
        return results
