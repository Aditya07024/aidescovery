from typing import List
from pydantic import BaseModel, Field


class QualificationResponse(BaseModel):
    """
    Structured response output by AI Qualifier evaluating entity against SearchPlan criteria.
    """
    match: bool = Field(description="True if entity meets search criteria")
    score: float = Field(ge=0.0, le=100.0, description="Match score out of 100")
    reasons: List[str] = Field(default_factory=list, description="Specific factual match/mismatch justifications")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in qualification score")
