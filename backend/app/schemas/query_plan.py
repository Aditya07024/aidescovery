from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LocationFilter(BaseModel):
    city: Optional[str] = Field(default=None, description="City name (e.g. Mathura, Delhi)")
    state: Optional[str] = Field(default=None, description="State name")
    country: Optional[str] = Field(default="India", description="Country name")


class SearchFilters(BaseModel):
    minimum_experience_years: Optional[float] = Field(default=None, description="Minimum required experience in years")
    employee_count: Optional[Dict[str, int]] = Field(default=None, description="Employee count range min and max")
    rating_below: Optional[float] = Field(default=None, description="Maximum star rating cutoff")
    rating_above: Optional[float] = Field(default=None, description="Minimum star rating cutoff")
    has_instagram: Optional[bool] = Field(default=None, description="Active Instagram presence required")
    min_followers: Optional[int] = Field(default=None, description="Minimum social followers count")
    owns_clinic: Optional[bool] = Field(default=None, description="Owns a clinic or business venue")
    current_role: Optional[str] = Field(default=None, description="Job title or role required")
    extra_criteria: Dict[str, Any] = Field(default_factory=dict)


class SearchPlan(BaseModel):
    """
    Structured specification output by the AI Query Planner from a natural language request.
    """
    entity_type: str = Field(default="person", description="One of: person, company, business, place, professional, creator, organization")
    profession: List[str] = Field(default_factory=list, description="Target profession or job roles")
    location: LocationFilter = Field(default_factory=LocationFilter)
    filters: SearchFilters = Field(default_factory=SearchFilters)
    sources: List[str] = Field(default_factory=lambda: ["web", "google_maps"], description="Sources to query: web, google_maps, reddit, youtube, crawler")
    limit: int = Field(default=50, ge=1, le=500)
    keywords: List[str] = Field(default_factory=list, description="Extracted search keywords")
