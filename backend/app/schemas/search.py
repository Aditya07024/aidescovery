from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SearchCreateRequest(BaseModel):
    query: str = Field(min_length=3, description="Natural language search query")
    entity_type: Optional[str] = Field(default=None, description="Optional entity type override")
    sources: List[str] = Field(default_factory=lambda: ["auto"], description="Selected sources or 'auto'")
    limit: int = Field(default=50, ge=1, le=500)


class SearchJobResponse(BaseModel):
    search_id: str
    status: str
    progress: int
    discovered: int
    qualified: int
    created_at: datetime
    finished_at: Optional[datetime] = None
    structured_plan: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class SearchResultItem(BaseModel):
    entity_id: str
    rank: int
    name: str
    entity_type: str
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location_summary: Optional[str] = None
    description: Optional[str] = None
    match_score: float
    is_qualified: bool
    qualification_reasons: List[str]
    attributes: Dict[str, Any] = {}
