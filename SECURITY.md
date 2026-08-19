# Security Audit & Policy

## 1. Credentials & Secrets Management
- All API keys, tokens, and database passwords MUST be loaded exclusively from environment variables.
- Raw API keys are hashed with SHA-256 before storage in the database.
- `.env` files are excluded from git via `.gitignore`.
- `.env.example` provides safe templates with no hardcoded credentials.

## 2. Anti-SSRF (Server-Side Request Forgery) Protection
Web crawlers validate all target URLs using `is_ssrf_safe_url()`:
- Blocks resolution to loopback (`127.0.0.0/8`, `::1`).
- Blocks private IPv4 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- Blocks link-local metadata endpoints (`169.254.169.254`).
- Blocks `.local` and `.internal` hostnames.

## 3. Database Security & Network Isolation
- PostgreSQL and Redis are bound exclusively to private internal networks in Docker Compose and are not exposed to the public Internet.
- Parameterized queries managed strictly via SQLAlchemy 2.x ORM prevent SQL injection.

## 4. API Authentication & Security
- REST API supports application API key authentication (`X-API-Key`).
- Unified JSON error responses prevent exposure of internal stack traces.
