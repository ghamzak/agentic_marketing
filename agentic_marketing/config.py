"""
Configuration loader for environment variables and settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://ghamz:LoomLoom@localhost:5432/agentic_marketing")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY", "")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
