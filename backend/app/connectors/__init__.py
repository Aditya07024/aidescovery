from app.connectors.base import SourceConnector
from app.connectors.registry import connector_registry
from app.connectors.web import WebSearchConnector
from app.connectors.google_maps import GoogleMapsConnector
from app.connectors.reddit import RedditConnector
from app.connectors.youtube import YouTubeConnector
from app.connectors.crawler import GenericCrawlerConnector

# Register initial connectors into global registry
connector_registry.register(WebSearchConnector())
connector_registry.register(GoogleMapsConnector())
connector_registry.register(RedditConnector())
connector_registry.register(YouTubeConnector())
connector_registry.register(GenericCrawlerConnector())

__all__ = [
    "SourceConnector",
    "connector_registry",
    "WebSearchConnector",
    "GoogleMapsConnector",
    "RedditConnector",
    "YouTubeConnector",
    "GenericCrawlerConnector",
]
