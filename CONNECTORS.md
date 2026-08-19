# Data Source Connectors

The platform implements a pluggable `SourceConnector` protocol managed by `ConnectorRegistry`.

## Implemented Connectors

| Connector Name | Source Type | Authentication | Capabilities |
| :--- | :--- | :--- | :--- |
| `web` | Web Search | Public / API Key | Multi-engine web search with deep page crawling |
| `google_maps` | Places Directory | Public / API Key | Business ratings, reviews, operating hours, addresses |
| `reddit` | Social Community | Public / OAuth | Community discussions, post authors, recommendation threads |
| `youtube` | Video Platform | Public / API Key | Creator channel discovery, video descriptions, subscriber counts |
| `crawler` | Deep Crawler | None | Safe HTML extraction with anti-SSRF IP filtering |

---

## Adding a New Connector

Implement the `SourceConnector` protocol in `app/connectors/`:
```python
from app.connectors.base import SourceConnector

class CustomConnector(SourceConnector):
    name = "custom_platform"
    async def search(self, plan): ...
    async def normalize(self, raw_item): ...
    def capabilities(self): ...
```
Then register it in `app/connectors/__init__.py`:
```python
connector_registry.register(CustomConnector())
```
