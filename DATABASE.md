# Database Architecture

The platform uses **PostgreSQL + pgvector** (or SQLite for light development/testing).

## Core Tables

- `entities`: Generic normalized entity model (id, entity_type, name, description, location_summary, website, email, phone, attributes).
- `people`: Specific profile for person/professional entities (experience_years, current_role, company_name).
- `companies`: Specific profile for company entities (industry, employee count min/max, domain).
- `businesses`: Business profile (rating, review_count, address, price_range).
- `sources`: External data source definitions.
- `entity_sources`: **Data Provenance Table** tracking field_name, value_raw, source_url, source_type, collected_at, verification_status (`observed` vs `inferred`).
- `searches`: Search jobs execution metadata and progress tracking.
- `search_results`: Search job to entity mapping with match_score, is_qualified, qualification_reasons, rank.
- `qualification_results`: AI qualification audit details.
- `embeddings`: pgvector embeddings for semantic similarity search.
- `api_keys`: SHA-256 hashed application API keys.

---

## Running Migrations

```bash
cd backend
alembic upgrade head
```
