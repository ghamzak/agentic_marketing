"""
WebScraperAgent: Discovers small businesses without websites in a given region or sector.
- Uses Playwright for browser automation and BeautifulSoup for parsing.
- Returns a list of business dicts: name, contact info, description, etc.
"""
import asyncio
from playwright.async_api import async_playwright
import re
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Optional
import logging
from .social_media_finding_agent import find_instagram_page, find_yelp_page, find_description

logger = logging.getLogger(__name__)

class WebScraperAgent:
    def __init__(self, region: str, sector: str, max_results: int = 20):
        self.region = region
        self.sector = sector
        self.max_results = max_results
        logger.info(f"Initialized WebScraperAgent for region='{self.region}', sector='{self.sector}', k={self.max_results}")
    
    async def search_google_maps(self, query: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f"https://www.google.com/maps")
            try:
                await page.wait_for_selector("#searchboxinput", timeout=15000)
                await page.fill("#searchboxinput", query)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(5000)
                html = await page.content()
            except Exception as e:
                logger.error(f"Scraping error: {e}")
                html = ""
            await browser.close()
            return html

    # async def get_instagram_account(self, business_name: str) -> dict:
    #     query = f"{business_name} {self.sector} {self.region}"
    #     return find_instagram_page(query)

    async def get_yelp_page(self, business_name: str) -> dict:
        query = f"{business_name} {self.sector}, {self.region}"
        return find_yelp_page(query)

    async def get_description(self, business_name: str) -> dict:
        query = f"Tell me a little bit about {business_name} {self.sector} in {self.region}"
        description = find_description(query)
        return description

    async def get_business_details(self, page, business_name: str, item) -> Dict:
        details: Dict[str, str] = {"website": "", "contact_phone": ""}
        a_tag = None
        for a in item.select("a.hfpxzc"):
            if a.get("aria-label", "") == business_name and a.get("href"):
                a_tag = a
                break
        if not a_tag:
            return details
        href = a_tag.get("href")
        if not isinstance(href, str):
            return details
        try:
            await page.goto(href)
            await page.wait_for_timeout(3000)
            details_html = await page.content()
            details_soup = BeautifulSoup(details_html, "lxml")
            website_section = details_soup.select_one("div.rogA2c.ITvuef")
            if website_section:
                website_div = website_section.select_one("div.Io6YTe.fontBodyMedium.kR99db.fdkmkc")
                if website_div and website_div.text:
                    details["website"] = website_div.text.strip()
            phone_btn = details_soup.select_one('button.CsEnBe[data-tooltip="Copy phone number"]')
            if phone_btn:
                aria_label = phone_btn.get("aria-label", "")
                if isinstance(aria_label, str):
                    match = re.search(r"Phone:\s*([+\d\-(). ]+)", aria_label)
                    if match:
                        details["contact_phone"] = str(match.group(1)).strip()
        except Exception as e:
            logger.error(f"Second-level details scrape error for {business_name}: {e}")
        return details

    async def parse_businesses(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "lxml")
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            for item in soup.select(".Nv2PK"):
                name = item.select_one(".qBF1Pd")
                business_name = name.text if name else None
                email = None
                details = {"website": None, "contact_phone": None}
                if business_name:
                    details = await self.get_business_details(page, business_name, item)
                    yelp_page = await self.get_yelp_page(business_name)
                    yelp_url = yelp_page.get("yelp_url")
                    yelp_description = yelp_page.get("yelp_description")
                    # insta_page = await self.get_instagram_account(business_name)
                    # insta_url = insta_page.get("url")
                    # insta_description = insta_page.get("description")
                    desc_obj = await self.get_description(business_name)
                    description = desc_obj.get("description") if desc_obj else None
                # keeping all businesses and filtering only inside the database
                # if not details["website"]:
                    results.append({
                        "name": business_name,
                        "description": description,
                        "contact_phone": details["contact_phone"],
                        "contact_email": email,
                        # "insta_url": insta_url,
                        # "insta_description": insta_description,
                        "yelp_url": yelp_url,
                        "yelp_description": yelp_description,
                        "region": self.region,
                        "industry": self.sector,
                        "website": details["website"],
                    })
                    if len(results) >= self.max_results:
                        break
            await browser.close()
        logger.info(f"Found {len(results)} businesses without websites.")
        return results

    async def find_businesses_without_websites(self) -> List[Dict]:
        logger.info("Calling find_businesses_without_websites()...")
        query = f"{self.sector} in {self.region}"
        html = await self.search_google_maps(query)
        businesses = await self.parse_businesses(html)
        logger.info(f"Found {len(businesses)} businesses without websites.")
        return businesses
