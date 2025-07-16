"""
Entry point for the Agentic Marketing backend API.
"""
from fastapi import FastAPI
from . import config

app = FastAPI(title="Agentic Marketing API", description="Multi-agent sales and marketing automation platform.")

@app.get("/")
def root():
    return {"message": "Agentic Marketing API is running."}
