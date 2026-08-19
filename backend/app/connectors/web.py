import logging
from typing import Any, Dict, List
from app.connectors.base import SourceConnector
from app.connectors.search_engine import get_search_provider
from app.connectors.web_crawler import SafeWebCrawler
from app.schemas.query_plan import SearchPlan

logger = logging.getLogger(__name__)


class WebSearchConnector(SourceConnector):
    name: str = "web"

    def __init__(self):
        self.search_provider = get_search_provider()
        self.crawler = SafeWebCrawler(max_concurrency=3)

    def capabilities(self) -> Dict[str, Any]:
        return {
            "source_type": "web_search",
            "authentication": "none_or_api_key",
            "rate_limits": "100 requests / min",
            "supported_filters": ["keywords", "location", "profession"],
            "description": "Public web search engine discovery connector with deep page fetching.",
        }

    async def search(self, plan: SearchPlan) -> List[Dict[str, Any]]:
        # Formulate search queries based on plan
        query_parts = []
        if plan.profession:
            query_parts.append(" ".join(plan.profession))
        if plan.location.city:
            query_parts.append(plan.location.city)
        if plan.location.country:
            query_parts.append(plan.location.country)
        if plan.filters.minimum_experience_years:
            query_parts.append(f"{int(plan.filters.minimum_experience_years)} years experience")
        if plan.keywords:
            query_parts.extend(plan.keywords[:3])

        query_str = " ".join(query_parts) if query_parts else "professional contact email"
        logger.info(f"[WebSearchConnector] Executing search query: '{query_str}'")

        results = await self.search_provider.search(query_str, limit=plan.limit)
        
        # Deep fetch top pages for contact details
        raw_entities = []
        for res in results[:5]:
            fetched = await self.crawler.fetch_page(res["url"])
            if fetched:
                res.update(fetched)
            raw_entities.append(res)

        return raw_entities

    async def normalize(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        title = raw_item.get("title", "")
        url = raw_item.get("url", "")
        snippet = raw_item.get("snippet", "")
        text = raw_item.get("text", "")
        
        emails = raw_item.get("emails", [])
        phones = raw_item.get("phones", [])
        social_links = raw_item.get("social_links", [])

        # Clean name from title
        name = title.split("-")[0].split("|")[0].strip() if title else "Web Entity"

        return {
            "entity_type": "person",
            "name": name,
            "description": snippet or text[:300],
            "website": url,
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "location_summary": raw_item.get("location_summary"),
            "social_profiles": social_links,
            "raw_provenance": [
                {
                    "field": "website",
                    "value": url,
                    "source_url": url,
                    "source_type": "web_search",
                    "verification_status": "observed",
                },
                {
                    "field": "description",
                    "value": snippet,
                    "source_url": url,
                    "source_type": "web_search",
                    "verification_status": "observed",
                }
            ]
        }
