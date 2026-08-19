import logging
from typing import Any, Dict, List, Protocol, runtime_checkable
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


@runtime_checkable
class SearchProvider(Protocol):
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Executes a search query.
        Returns list of items: [{"title": ..., "snippet": ..., "url": ..., "source": ...}]
        """
        ...


class GoogleSearchProvider(SearchProvider):
    """
    Google Custom Search JSON API Provider.
    """

    def __init__(self, api_key: str = "", engine_id: str = ""):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.engine_id = engine_id or settings.GOOGLE_SEARCH_ENGINE_ID

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.api_key or not self.engine_id:
            logger.info("Google Search credentials missing; falling back to MockSearchProvider.")
            return await MockSearchProvider().search(query, limit)

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.engine_id,
            "q": query,
            "num": min(limit, 10),
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, params=params)
                res.raise_for_status()
                data = res.json()
                items = []
                for item in data.get("items", []):
                    items.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "url": item.get("link", ""),
                        "source": "google_search",
                    })
                return items
        except Exception as e:
            logger.warning(f"Google Search API error: {e}. Falling back to MockSearchProvider.")
            return await MockSearchProvider().search(query, limit)


class SerperSearchProvider(SearchProvider):
    """
    Serper.dev Google Search API Provider.
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or settings.SERPER_API_KEY

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.api_key:
            return await DuckDuckGoSearchProvider().search(query, limit)

        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {"q": query, "num": limit}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    results = []
                    for item in data.get("organic", []):
                        results.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("snippet", ""),
                            "url": item.get("link", ""),
                            "source": "serper_google",
                        })
                    if results:
                        logger.info(f"[SerperSearchProvider] Discovered {len(results)} live Google results for '{query}'")
                        return results
        except Exception as e:
            logger.warning(f"Serper API search error: {e}. Falling back to DuckDuckGo/Mock.")

        return await DuckDuckGoSearchProvider().search(query, limit)


class DuckDuckGoSearchProvider(SearchProvider):
    """
    DuckDuckGo Instant Answer / HTML Search Provider.
    """

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": settings.CRAWLER_USER_AGENT}
        data = {"q": query}

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                res = await client.post(url, headers=headers, data=data)
                if res.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(res.text, "lxml")
                    results = []
                    for a in soup.find_all("a", class_="result__url", href=True):
                        title_elem = a.find_parent("div", class_="result__body")
                        snippet = ""
                        title = a.get_text().strip()
                        if title_elem:
                            snip_elem = title_elem.find("a", class_="result__snippet")
                            if snip_elem:
                                snippet = snip_elem.get_text().strip()
                        results.append({
                            "title": title,
                            "snippet": snippet,
                            "url": a["href"],
                            "source": "duckduckgo",
                        })
                        if len(results) >= limit:
                            break
                    if results:
                        return results
        except Exception as e:
            logger.debug(f"DuckDuckGo search error: {e}")

        return await MockSearchProvider().search(query, limit)


class MockSearchProvider(SearchProvider):
    """
    Deterministic Mock Search Provider for tests and offline execution.
    """

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        logger.info(f"[MockSearchProvider] Searching query: '{query}'")
        q_lower = query.lower()

        if "therapist" in q_lower or "mathura" in q_lower:
            return [
                {
                    "title": "Dr. Rahul Sharma - Clinical Psychologist & Therapist",
                    "snippet": "Dr. Rahul Sharma has 8 years of clinical experience in Mathura providing therapy for anxiety, depression, and relationships. Phone: +91 9876543210. Email: contact@rahulsharma.in",
                    "url": "https://rahulsharma-psychology.in",
                    "source": "web_search",
                },
                {
                    "title": "Mathura Wellness Clinic - Mind & Behavioral Therapy",
                    "snippet": "Leading mental health clinic in Mathura. Experienced counselors and therapists with over 6+ years experience. Located near Station Road, Mathura.",
                    "url": "https://mathurawellness.org",
                    "source": "web_search",
                },
                {
                    "title": "Priya Verma - Licensed Psychotherapist Mathura",
                    "snippet": "Priya Verma (M.Phil Clinical Psychology, 7 years exp) offers individual therapy sessions in Mathura.",
                    "url": "https://priyaverma-therapy.com",
                    "source": "web_search",
                },
            ][:limit]

        elif "cto" in q_lower or "saas" in q_lower:
            return [
                {
                    "title": "Aarav Patel - CTO at CloudScale Technologies",
                    "snippet": "Aarav Patel is the CTO of CloudScale Technologies (B2B SaaS with 80 employees in Bengaluru). Expertise in Distributed Systems and AI.",
                    "url": "https://cloudscale.io/team/aarav-patel",
                    "source": "web_search",
                },
                {
                    "title": "DevTech India SaaS Leaders Directory",
                    "snippet": "Sneha Gupta, Chief Technology Officer at DataFlow AI (SaaS startup with 45 employees). Contact: sneha@dataflow.ai",
                    "url": "https://devtechindia.org/cto-list",
                    "source": "web_search",
                },
                {
                    "title": "DevTech India SaaS Leaders Directory",
                    "snippet": "Sneha Gupta, Chief Technology Officer at DataFlow AI (SaaS startup with 45 employees). Contact: sneha@dataflow.ai",
                    "url": "https://devtechindia.org/cto-list",
                    "source": "web_search",
                },
            ][:limit]

        # Generic search mock
        return [
            {
                "title": f"Result for {query} - Official Site",
                "snippet": f"Leading entity matching query '{query}'. Phone: +91 9999988888. Email: info@example.org. Address: Main St, Delhi, India.",
                "url": "https://example.org/entity-profile",
                "source": "web_search",
            }
        ][:limit]


def get_search_provider() -> SearchProvider:
    if settings.SERPER_API_KEY:
        return SerperSearchProvider()
    if settings.GOOGLE_API_KEY and settings.GOOGLE_SEARCH_ENGINE_ID:
        return GoogleSearchProvider()
    return DuckDuckGoSearchProvider()
