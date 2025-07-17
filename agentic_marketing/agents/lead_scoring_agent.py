"""
LeadScoringAgent: Scores businesses for likelihood to benefit from a website, predicts ROI and probability using LLM, and ranks leads.
"""
import asyncio
import logging
from typing import List, Dict, Any
from urllib import response
from agentic_marketing.models import Business, Lead
from agentic_marketing.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from agentic_marketing.config import OPENAI_API_KEY
from openai import OpenAI

logger = logging.getLogger(__name__)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class LeadScoringAgent:
    def __init__(self, businesses: List[Dict]):
        self.businesses = businesses

    async def score_business(self, business: Dict) -> Dict:
        """
        Use LLM to reason about ROI and probability for a business.
        """
        prompt = f"""
        Given the following business info:
        Name: {business.get('name')}
        Region: {business.get('region')}
        Industry: {business.get('industry')}
        Description: {business.get('description')}
        Social Media: {business.get('social_media', '')}
        Recent Trends: {business.get('trends', '')}
        Reason about how much this business would benefit from having a website for their business. Predict the ROI (as a float, 0-100) and the probability (0-1) that they would benefit, based on market trends and interests. Explain your reasoning.
        Return a JSON object with keys: reasoning, predicted_ROI, predicted_probability.
        """
        try:
            response = openai_client.responses.create(
                model="o4-mini",
                instructions="You are a business analyst.",
                reasoning={
                    "effort": "medium",
                    "summary": "auto"
                    },
                input=[                    
                    {"role": "user", "content": prompt}
                ],
                max_output_tokens=20000,
                temperature=0.5,
            )
            # OpenAI API returns 'choices' with 'message' or 'text'
            # content = response.choices[0].message.get('content') if hasattr(response.choices[0], 'message') else response.choices[0].get('text')
            if response.status == "incomplete" and response.incomplete_details == "max_output_tokens":
                print("Ran out of tokens")
            if response.output_text:
                print("Partial output:", response.output_text)
            else: 
                print("Ran out of tokens during reasoning")

            content = response.output_text
            import json
            result = json.loads(content)
            return {
                "reasoning": result.get("reasoning"),
                "predicted_ROI": float(result.get("predicted_ROI", 0)),
                "predicted_probability": float(result.get("predicted_probability", 0))
            }
        except Exception as e:
            logger.error(f"LLM scoring error: {e}")
            return {
                "reasoning": "LLM error",
                "predicted_ROI": 0.0,
                "predicted_probability": 0.0
            }

    async def process_and_save_leads(self):
        """
        Score all businesses, rank, and save to leads table.
        """
        scored_leads = []
        for business in self.businesses:
            result = await self.score_business(business)
            lead = Lead(
                business_id=business.get('id'),
                score=result["predicted_probability"],
                predicted_ROI=result["predicted_ROI"],
                predicted_probability=result["predicted_probability"],
                reasoning=result["reasoning"]
            )
            scored_leads.append(lead)
        # Rank by predicted_probability
        scored_leads.sort(key=lambda l: l.predicted_probability, reverse=True)
        # Save to DB
        async with AsyncSessionLocal() as session:
            for lead in scored_leads:
                session.add(lead)
            await session.commit()
        logger.info(f"Saved {len(scored_leads)} leads to database.")
        return scored_leads
