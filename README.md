# Universal AI Discovery Platform

A production-ready, AI-powered entity discovery and entity intelligence platform. Accepts natural language requests, plans structured searches, selects data connectors, normalizes records, deduplicates entities using multi-signal resolution, qualifies results with AI, preserves strict data provenance, and exposes ranked entity intelligence via REST API & Next.js SaaS Web UI.

---

## Key Features

- **Natural Language Query Planner**: Converts queries into validated `SearchPlan` specifications using Hugging Face, OpenAI-compatible APIs, local Ollama models, or mock providers.
- **Pluggable Data Connectors**: Supports Web Search, Google Maps, Reddit, YouTube, and deep Web Crawlers with anti-SSRF protection.
- **Multi-Signal Entity Resolution**: Deduplicates entities using email, phone, domain, social profile URLs, and name/location confidence matching.
- **Fact-Based AI Qualification**: Scores discovered entities against query criteria with explicit justification and zero hallucinated facts.
- **Strict Data Provenance**: Every observed attribute links directly to source URLs, collection timestamps, and verification status (`observed` vs `inferred`).
- **REST API + Next.js Web UI**: Full versioned OpenAPI endpoints, API key authentication, live progress dashboard, and CSV/JSON export.

---

## Quick Start (Development)

1. **Clone & Set Up Environment Variables**:
   ```bash
   cp .env.example .env
   ```

2. **Run Backend Tests**:
   ```bash
   cd backend
   pip install -e ".[dev]"
   pytest -v
   ```

3. **Start Application Services via Docker Compose**:
   ```bash
   docker compose up --build -d
   ```
   Access Web UI at `http://localhost:3000` and API Docs at `http://localhost:8000/docs`.

---

## Documentation Links

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design & pipeline workflow
- [API.md](API.md) - Versioned REST API specifications
- [CONNECTORS.md](CONNECTORS.md) - Available data connectors & capabilities
- [AI_PROVIDERS.md](AI_PROVIDERS.md) - AI provider abstraction guide
- [DATABASE.md](DATABASE.md) - PostgreSQL + pgvector entity schema
- [SECURITY.md](SECURITY.md) - SSRF protections & authentication audit
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production Ubuntu SSH server deployment
