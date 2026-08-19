# System Architecture

The Universal AI Discovery Platform executes an 11-stage processing pipeline from natural language input to ranked entity intelligence.

```
Natural Language Query
        ↓
AI Query Planner (HuggingFace / OpenAI / Ollama / Mock)
        ↓
Structured Search Specification (SearchPlan)
        ↓
Source Connector Selection (Web, Google Maps, Reddit, YouTube, Crawler)
        ↓
Async Discovery Jobs (ARQ + Redis Job Queue)
        ↓
Raw Data Collection & Anti-SSRF Crawler
        ↓
Normalization & Provenance Attachment
        ↓
Entity Resolution & Deduplication (Multi-Signal Matcher)
        ↓
AI Qualification & Match Confidence Scoring
        ↓
PostgreSQL + pgvector Database
        ↓
REST API (FastAPI) + Next.js Web Application
```

---

## Processing Pipeline Stages

1. **Natural Language Query**: The user inputs a query like `"Find therapists in Mathura with at least 5 years of experience"`.
2. **AI Query Planner**: Converts text into a validated `SearchPlan` Pydantic model with retry logic.
3. **Source Connector Selection**: Dynamically selects connectors from `ConnectorRegistry` based on plan requirements.
4. **Async Discovery Job**: Enqueues job to background ARQ worker for asynchronous execution.
5. **Raw Data Collection**: Connectors fetch public data; web crawler applies SSRF IP range validation.
6. **Normalization**: Standardizes fields (name, email, phone, domain, location) and creates `EntitySource` records.
7. **Entity Resolution**: Compares candidates against confidence thresholds (email, phone, domain, social profile).
8. **AI Qualification**: Evaluates resolved entities against criteria, scoring 0-100% with justification.
9. **Persistence**: Saves entities, provenance, search results, and vector embeddings to PostgreSQL.
10. **Delivery**: Results are delivered via REST API endpoints (`/api/v1/search/{id}/results`) and rendered in Next.js UI.
