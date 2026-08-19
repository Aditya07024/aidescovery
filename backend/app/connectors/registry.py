import logging
from typing import Dict, List, Optional
from app.connectors.base import SourceConnector

logger = logging.getLogger(__name__)


class ConnectorRegistry:
    """
    Registry for managing available SourceConnector instances.
    """

    def __init__(self):
        self._connectors: Dict[str, SourceConnector] = {}

    def register(self, connector: SourceConnector) -> None:
        name = connector.name.lower()
        self._connectors[name] = connector
        logger.info(f"Registered source connector: '{name}'")

    def get(self, name: str) -> Optional[SourceConnector]:
        return self._connectors.get(name.lower())

    def list_connectors(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": conn.name,
                "capabilities": conn.capabilities(),
            }
            for conn in self._connectors.values()
        ]

    def select_connectors_for_plan(self, selected_sources: List[str]) -> List[SourceConnector]:
        if not selected_sources or "auto" in selected_sources or "all" in selected_sources:
            return list(self._connectors.values())

        matched = []
        for name in selected_sources:
            conn = self.get(name)
            if conn:
                matched.append(conn)
        return matched if matched else list(self._connectors.values())


# Global singleton registry instance
connector_registry = ConnectorRegistry()
