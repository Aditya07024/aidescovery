from typing import Any, Dict, List, Protocol, runtime_checkable
from app.schemas.query_plan import SearchPlan


@runtime_checkable
class SourceConnector(Protocol):
    """
    Pluggable connector interface for all external data sources.
    """
    name: str

    async def search(self, plan: SearchPlan) -> List[Dict[str, Any]]:
        """
        Executes a raw discovery search using the given SearchPlan.
        Returns a list of raw entity items.
        """
        ...

    async def normalize(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes raw source payload into a standardized entity dictionary.
        Must preserve observed provenance facts.
        """
        ...

    def capabilities(self) -> Dict[str, Any]:
        """
        Returns metadata describing supported filters, rate limits, and authentication mode.
        """
        ...
