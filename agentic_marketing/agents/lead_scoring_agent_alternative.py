"""
LeadScoringAgentAlternative: Uses OpenAI Agents SDK to score businesses for likelihood to benefit from a website, predicts probability of conversion, and ranks leads.
"""
import logging
from typing import List, Dict
from agentic_marketing.models import Lead
from agentic_marketing.database import AsyncSessionLocal
from agentic_marketing.config import OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# OpenAI Agents SDK imports
from agents import Agent, Runner
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

class LeadScoreSchema(BaseModel):
    reasoning: str = Field(..., description="LLM reasoning about business potential ROI and probability of conversion.")    
    predicted_probability: float = Field(..., ge=0, le=1, description="Probability of conversion (0-1)")

class LeadScoringAgentAlternative:
    def __init__(self, businesses: List[Dict]):
        self.businesses = businesses

    def build_prompt(self, business: Dict) -> str:
        return f"""
        Given the following business info:
        Name: {business.get('name')}
        Region: {business.get('region')}
        Industry: {business.get('industry')}
        Description: {business.get('description', '')}
        Yelp Description: {business.get('yelp_description', '')}
        Recent Trends in this sector: {business.get('trends', '')}
        Reason about how much this business would benefit from having a website for their business. Predict the probability (0-1) that they would benefit, based on market trends and interests. Explain your reasoning.
        Return a JSON object with keys: reasoning, predicted_probability.
        """

    def score_business(self, business: Dict) -> Dict:
        prompt = self.build_prompt(business)
        agent = Agent(
            name="LeadScorer",
            instructions="You are a business analyst. Reason about the probability for website benefit.",
            output_type=LeadScoreSchema
        )
        result = Runner.run_sync(agent, prompt)
        try:
            # result.final_output is already validated by Pydantic
            parsed = result.final_output
            return {
                "reasoning": parsed.reasoning,                
                "predicted_probability": parsed.predicted_probability
            }
        except ValidationError as ve:
            logger.error(f"Pydantic validation error: {ve}")
            return {
                "reasoning": "Validation error",                
                "predicted_probability": 0.0
            }
        except Exception as e:
            logger.error(f"Agent SDK scoring error: {e}")
            return {
                "reasoning": "Agent SDK error",                
                "predicted_probability": 0.0
            }

    def process_and_save_leads(self):
        from agentic_marketing.database import SessionLocal
        results = []
        scored_leads = []
        for business in self.businesses:
            result = self.score_business(business)
            lead = Lead(
                business_id=business.get('id'),
                score=result["predicted_probability"],                
                predicted_probability=result["predicted_probability"],
                reasoning=result["reasoning"]                
            )
            scored_leads.append(lead)
            results.append({
                "business_id": business.get('id'),
                "name": business.get('name'),
                "reasoning": result["reasoning"],                
                "predicted_probability": result["predicted_probability"]
            })
        # Rank by predicted_probability
        scored_leads.sort(key=lambda l: l.predicted_probability, reverse=True)
        # Save to DB synchronously
        with SessionLocal() as session:
            for lead in scored_leads:
                session.add(lead)
            session.commit()
        logger.info(f"Saved {len(scored_leads)} leads to database.")
        return results
