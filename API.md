# REST API Documentation (`/api/v1`)

All API endpoints are documented with OpenAPI at `/docs`.

## Core Endpoints

### 1. Submit Search Job
- **POST** `/api/v1/search`
- **Headers**: `X-API-Key: uadp_live_...`
- **Request Body**:
  ```json
  {
    "query": "Find therapists in Mathura with at least 5 years of experience",
    "sources": ["auto"],
    "limit": 50
  }
  ```
- **Response**: `202 Accepted`
  ```json
  {
    "search_id": "8f3b1a20-...",
    "status": "queued",
    "progress": 0,
    "discovered": 0,
    "qualified": 0
  }
  ```

### 2. Get Search Status
- **GET** `/api/v1/search/{id}`
- **Response**: `200 OK`
  ```json
  {
    "search_id": "8f3b1a20-...",
    "status": "running",
    "progress": 60,
    "discovered": 12,
    "qualified": 8
  }
  ```

### 3. Get Search Results
- **GET** `/api/v1/search/{id}/results?qualified_only=false`
- **Response**: List of `SearchResultItem` objects.

### 4. Entity Provenance
- **GET** `/api/v1/entities/{id}/sources`
- **Response**: Data provenance records linking observed facts to original URLs and collection timestamps.

### 5. Data Export
- **GET** `/api/v1/export/{id}?format=csv`
- **Response**: Streamed CSV download.
