import requests
from bs4 import BeautifulSoup
import logging

class WebScraperMCP:
    """MCP for scraping web content."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_url(self, url: str) -> str:
        """
        Scrapes and extracts text content from a webpage URL.
        
        Use this tool when you need to read the content of a website.
        It fetches the page, removes navigation/scripts, and returns clean text.
        
        Args:
            url: The full URL to scrape (must include http:// or https://)
            
        Returns:
            Extracted text content from the webpage, or an error message if scraping fails
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit length to avoid token limits (approx 10k chars)
            return text[:10000]
            
        except Exception as e:
            return f"Error scraping URL: {str(e)}"
