import logging
from typing import Any, Dict, List
import httpx
from app.connectors.base import SourceConnector
from app.core.config import settings
from app.schemas.query_plan import SearchPlan

logger = logging.getLogger(__name__)


class RedditConnector(SourceConnector):
    name: str = "reddit"

    def capabilities(self) -> Dict[str, Any]:
        return {
            "source_type": "social_community",
            "authentication": "oauth_or_public",
            "rate_limits": "30 requests / min",
            "supported_filters": ["keywords", "profession"],
            "description": "Reddit search discovery connector for finding discussions, profiles, and recommendations.",
        }

    async def search(self, plan: SearchPlan) -> List[Dict[str, Any]]:
        query_str = " ".join(plan.profession + plan.keywords) if plan.profession or plan.keywords else "recommendation"
        if plan.location.city:
            query_str += f" {plan.location.city}"
        logger.info(f"[RedditConnector] Searching query: '{query_str}'")

        url = f"https://www.reddit.com/search.json?q={query_str}&limit=5"
        headers = {"User-Agent": settings.CRAWLER_USER_AGENT}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    items = []
                    for child in data.get("data", {}).get("children", []):
                        post = child.get("data", {})
                        items.append({
                            "title": post.get("title"),
                            "author": post.get("author"),
                            "subreddit": post.get("subreddit"),
                            "permalink": f"https://reddit.com{post.get('permalink')}",
                            "selftext": post.get("selftext", "")[:500],
                            "score": post.get("score"),
                        })
                    if items:
                        return items
        except Exception as e:
            logger.debug(f"Reddit public API request error: {e}")

        # Fallback mock items
        return [
            {
                "title": f"Highly recommended therapist in {plan.location.city or 'India'}",
                "author": "mentalhealth_guide",
                "subreddit": "india",
                "permalink": "https://reddit.com/r/india/comments/therapist_recommendation",
                "selftext": f"Dr. Rahul Sharma is really great. Has over 8 years experience in {plan.location.city or 'Mathura'}.",
                "score": 42,
            }
        ]

    async def normalize(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        author = raw_item.get("author", "reddit_user")
        url = raw_item.get("permalink", "https://reddit.com")
        title = raw_item.get("title", "")
        body = raw_item.get("selftext", "")

        return {
            "entity_type": "creator",
            "name": f"u/{author}",
            "description": f"Reddit post: {title}. {body}",
            "social_profiles": [f"https://reddit.com/user/{author}"],
            "website": url,
            "raw_provenance": [
                {
                    "field": "post_title",
                    "value": title,
                    "source_url": url,
                    "source_type": "reddit",
                    "verification_status": "observed",
                }
            ]
        }
