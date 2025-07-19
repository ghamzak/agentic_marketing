"""
PersonaAndMarketingAgent: Accepts selected leads, generates a marketing persona and personalized email content for each lead.
"""
from typing import List, Dict
from pydantic import BaseModel, Field
from agents import Agent, Runner, AgentOutputSchema
import logging



# Strict schema for persona_json

from typing import List, Dict

class PersonaSchema(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    age: int
    interests: List[str]
    pain_points: List[str]
    goals: List[str]
    preferred_channels: List[str]

class PersonaAndContentSchema(BaseModel):
    model_config = {"extra": "forbid"}
    persona_json: PersonaSchema = Field(..., description="LLM-generated marketing persona for the business.")
    channel_contents: Dict[str, str] = Field(..., description="Dict mapping channel name (email, instagram, tiktok, etc.) to generated content.")

class PersonaAndMarketingAgent:
    def __init__(self, leads: List[Dict]):
        self.leads = leads

    def build_prompt(self, lead: Dict) -> str:
        return f"""
        Given the following business info and reasoning:
        Business Name: {lead.get('name')}
        Industry: {lead.get('industry')}
        Region: {lead.get('region')}
        Description: {lead.get('description', '')}
        Reasoning: {lead.get('reasoning', '')}

        1. Generate a marketing persona for the business's ideal customer (as a JSON object with keys: name, age, interests, pain_points, goals, preferred_channels).
        2. Write personalized outreach content for the following channels: email, instagram, tiktok. For each channel, generate content tailored to that channel and the business context.

        Return a JSON object with keys: persona_json, channel_contents. channel_contents should be a dict mapping channel name (email, instagram, tiktok) to the generated content string for that channel.
        """

    def generate_persona_and_content(self, lead: Dict) -> Dict:
        import traceback
        prompt = self.build_prompt(lead)
        print("We're in generate_persona_and_content!!!")
        agent = Agent(
            name="PersonaAndMarketingGenerator",
            instructions="You are a marketing strategist. Generate a persona and personalized outreach content for each channel.",
            output_type=AgentOutputSchema(PersonaAndContentSchema, strict_json_schema=False)
        )
        print("Agent created successfully.")
        try:
            result = Runner.run_sync(agent, prompt)
            print("Agent run completed successfully.")
        except Exception as e:
            print("Error running agent:", e)
            traceback.print_exc()
            raise
        logging.info('Persona and content generation result: %s', result)
        parsed = result.final_output
        return {
            "lead_id": lead.get('id'),
            "persona_json": parsed.persona_json.model_dump() if hasattr(parsed.persona_json, 'model_dump') else dict(parsed.persona_json),
            "channel_contents": parsed.channel_contents
        }

    def run(self) -> List[Dict]:
        results = []
        for lead in self.leads:
            try:
                results.append(self.generate_persona_and_content(lead))
            except Exception as e:
                results.append({
                    "lead_id": lead.get('id'),
                    "persona_json": {},
                    "channel_contents": {"error": f"Error: {e}"}
                })
        return results
