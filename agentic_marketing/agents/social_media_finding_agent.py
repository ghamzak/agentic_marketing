import os
from dotenv import load_dotenv
from tavily import TavilyClient
import json

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")
if not api_key:
    raise ValueError("TAVILY_API_KEY not found in environment variables.")

tavily_client = TavilyClient(api_key=api_key)
def find_instagram_page(query):
    response = tavily_client.search(query=query, 
                                     max_results=1,
                                     include_domains=["instagram.com"],
                                     search_depth="advanced",
                                     include_raw_content=False)
    res = response.get("results", [])[0] if response.get("results") else None
    if res:
        return {"insta_url": res.get("url"), "insta_description": res.get("content")}
    return {"insta_url": None, "insta_description": None}

def find_yelp_page(query):
    response = tavily_client.search(query=query, 
                                     max_results=3,
                                     include_domains=["yelp.com/biz"],
                                     search_depth="advanced",
                                     include_raw_content=False)
    if response and "results" in response and isinstance(response["results"], list) and len(response["results"]) > 0:
        results = [x for x in response["results"] if x.get("url").startswith("https://www.yelp.com/biz/")]
        if results:
            return {"yelp_url": results[0].get("url"), "yelp_description": results[0].get("content")}
    return {"yelp_url": None, "yelp_description": None}

def find_description(query):
    response = tavily_client.search(query=query, 
                                     max_results=1,                                     
                                     search_depth="advanced",
                                     include_raw_content=True)
    res = response.get("results", [])[0] if response.get("results") else None
    if res:
        return {"description": res.get("content")}
    return {"description": None}