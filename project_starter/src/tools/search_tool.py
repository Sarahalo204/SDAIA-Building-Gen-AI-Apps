import logging
import socket
from urllib.parse import urlparse
import ipaddress
import requests
from bs4 import BeautifulSoup
import os

from src.tools.registry import registry

logger = logging.getLogger(__name__)

def validate_url(url: str) -> bool:
    """
    Validate URL to prevent SSRF (Server-Side Request Forgery).
    Blocks localhost, private IP ranges, and non-http/https schemes.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False
        try:
            ip_address = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_address)

            if ip.is_private or ip.is_loopback or ip.is_reserved:
                return False

        except Exception:
            return False

        return True

    except Exception:
        return False


@registry.register("search_web", "Search the web for a query. Returns a list of results with title, link, and snippet.", category="research")
# NOTE: The decorator above will work once you implement the registry!
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo (HTML).
    """
    
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not set in environment variables."

    url = "https://api.tavily.com/search"

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
        "include_answer": False
    }

    try:
        logger.info(f"Searching Tavily for: '{query}'")

        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()

        formatted_results = []
        for item in data.get("results", []):
            link = item.get("url")
            if link and validate_url(link):
                result_str = (
                    f"Title: {item.get('title')}\n"
                    f"Link: {link}\n"
                    f"Snippet: {item.get('content')}\n"
                )
                formatted_results.append(result_str)

        logger.info(f"Tavily returned {len(formatted_results)} results.")

        if not formatted_results:
            return "No relevant results found."
            
        return "\n---\n".join(formatted_results)

    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return f"Error performing search: {str(e)}"


@registry.register("read_webpage", "Read the content of a webpage. Returns the text content.", category="research")
# NOTE: The decorator above will work once you implement the registry!
def read_webpage(url: str) -> str:
    """Read and extract text from a URL."""
    
    if not validate_url(url):
        return "Error: Invalid or restricted URL. Access blocked."

    try:
        logger.info(f"Reading webpage: {url}")

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unnecessary elements
        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        text = soup.get_text(separator="\n")

        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)

        content = clean_text[:10000] 
        logger.info(f"Read {len(content)} characters from {url}")

        return content

    except Exception as e:
        logger.error(f"Error reading {url}: {e}")
        return f"Error reading {url}: {str(e)}"