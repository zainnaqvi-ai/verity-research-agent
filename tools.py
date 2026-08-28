import warnings

warnings.filterwarnings("ignore")

import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for real-time information, facts, and relevant source URLs.
    Args:
        query: Specific search terms or questions.
    """
    try:
        results = []
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=4))
            if not raw_results:
                return "Search returned 0 results. Modify keywords or broaden your query."

            for idx, r in enumerate(raw_results, start=1):
                title = r.get('title', 'No Title')
                url = r.get('href', '')
                snippet = r.get('body', '')
                results.append(
                    f"[{idx}] Title: {title}\nURL: {url}\nSnippet: {snippet}\n"
                )
        return "\n---\n".join(results)
    except Exception as e:
        return f"Web search encountered an error: {str(e)}. Try an alternative query."


@tool
def fetch_page(url: str) -> str:
    """Fetch and extract readable body content from a specific webpage URL.
    Args:
        url: The full http/https webpage URL to read.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        with httpx.Client(timeout=8.0, follow_redirects=True, headers=headers) as client:
            response = client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            for element in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
                element.decompose()

            text = " ".join(soup.stripped_strings)
            return text[:3500] if text else "Webpage loaded, but no readable body content was detected."
    except httpx.HTTPStatusError as e:
        return f"HTTP error {e.response.status_code} accessing URL. Select a different source URL."
    except Exception as e:
        return f"Failed to fetch webpage ({str(e)}). Rely on search snippets or choose another URL."


TOOLS = [web_search, fetch_page]