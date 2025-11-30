from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from src.config import get_retry_config
import json

from google.adk.tools import FunctionTool
from src.mcp.web_scraper_mcp import WebScraperMCP

def create_deadline_parser_agent():
    """Agent specialized in parsing URLs and text to extract deadline information."""
    
    # Initialize tools
    scraper = WebScraperMCP()
    scrape_tool = FunctionTool(func=scraper.scrape_url)
    
    return LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=get_retry_config()),
        name="deadline_parser",
        description="Extracts deadline information from URLs and text descriptions",
        instruction="""You are a deadline extraction specialist.
        
        Your job:
        1. If a URL is provided, use the scrape_url tool to get the content.
        2. Analyze the text (provided or scraped) to extract opportunity details.
        3. Identify the deadline date, title, and requirements.
        
        Return information in this JSON format:
        {
            "title": "Opportunity name",
            "deadline_date": "YYYY-MM-DD",
            "description": "Brief description",
            "requirements": ["Requirement 1", "Requirement 2", ...],
            "category": "scholarship/internship/competition/other",
            "priority": 1-5 (based on urgency and importance)
        }
        
        Be thorough in extracting requirements. If date is not explicitly stated,
        use context clues. If information is missing, mark it as "Not specified".
        """,
        tools=[scrape_tool]
    )
