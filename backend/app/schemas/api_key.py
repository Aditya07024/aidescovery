from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class APIKeyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Application or client name")


class APIKeyCreateResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    raw_api_key: str
    created_at: datetime


class APIKeyItem(BaseModel):
    id: str
    name: str
    key_prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
