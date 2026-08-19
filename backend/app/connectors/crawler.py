import logging
from typing import Any, Dict, List
from app.connectors.base import SourceConnector
from app.connectors.web_crawler import SafeWebCrawler
from app.schemas.query_plan import SearchPlan

logger = logging.getLogger(__name__)


class GenericCrawlerConnector(SourceConnector):
    name: str = "crawler"

    def __init__(self):
        self.crawler = SafeWebCrawler()

    def capabilities(self) -> Dict[str, Any]:
        return {
            "source_type": "deep_web_crawler",
            "authentication": "none",
            "rate_limits": "30 requests / min",
            "supported_filters": ["url_target"],
            "description": "Deep HTML website crawler with SSRF protection.",
        }

    async def search(self, plan: SearchPlan) -> List[Dict[str, Any]]:
        target_urls = plan.filters.extra_criteria.get("target_urls", [])
        if not target_urls and plan.keywords:
            target_urls = [k for k in plan.keywords if k.startswith("http://") or k.startswith("https://")]

        if not target_urls:
            return []

        logger.info(f"[GenericCrawlerConnector] Crawling target URLs: {target_urls}")
        results = []
        for url in target_urls:
            page_data = await self.crawler.fetch_page(url)
            if page_data:
                results.append(page_data)
        return results

    async def normalize(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        url = raw_item.get("url", "")
        title = raw_item.get("title", "")
        text = raw_item.get("text", "")
        emails = raw_item.get("emails", [])
        phones = raw_item.get("phones", [])
        socials = raw_item.get("social_links", [])

        name = title if title else "Crawled Site Entity"

        return {
            "entity_type": "organization",
            "name": name,
            "description": text[:300],
            "website": url,
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "social_profiles": socials,
            "raw_provenance": [
                {
                    "field": "crawled_url",
                    "value": url,
                    "source_url": url,
                    "source_type": "web_crawler",
                    "verification_status": "observed",
                }
            ]
        }
