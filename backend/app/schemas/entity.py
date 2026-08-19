from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class EntityProvenanceResponse(BaseModel):
    id: str
    field_name: str
    value_raw: Optional[str]
    source_url: str
    source_type: str
    collected_at: datetime
    verification_status: str


class EntityDetailResponse(BaseModel):
    id: str
    entity_type: str
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location_summary: Optional[str] = None
    attributes: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    sources: List[EntityProvenanceResponse] = []
