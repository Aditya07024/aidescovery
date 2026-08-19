import json
import logging
from typing import Any, Type, TypeVar
from pydantic import BaseModel

from app.ai.base import AIProvider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class MockAIProvider(AIProvider):
    """
    Mock AI Provider that returns intelligent deterministic outputs for queries
    and qualifications when external API tokens are missing.
    """

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.2,
    ) -> str:
        logger.info(f"[MockAIProvider] Generating text for prompt: {prompt[:80]}...")
        return "Mock response: Operation completed successfully."

    async def structured_output(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> T:
        logger.info(f"[MockAIProvider] Structured output requested for schema: {response_schema.__name__}")
        prompt_lower = prompt.lower()

        # Handle SearchPlan schema request
        if response_schema.__name__ == "SearchPlan":
            entity_type = "person"
            profession = []
            city = None
            country = "India"
            min_exp = None
            employee_count = None
            rating_below = None
            sources = ["web", "google_maps"]

            if "therapist" in prompt_lower or "psychologist" in prompt_lower:
                profession = ["therapist", "psychologist"]
                entity_type = "professional"
                if "mathura" in prompt_lower:
                    city = "Mathura"
                if "5 years" in prompt_lower or "5+" in prompt_lower:
                    min_exp = 5

            elif "dermatologist" in prompt_lower or "doctor" in prompt_lower:
                profession = ["dermatologist", "doctor"]
                entity_type = "professional"
                sources = ["web", "google_maps", "social"]
                if "10,000" in prompt_lower or "10k" in prompt_lower:
                    min_followers = 10000

            elif "cto" in prompt_lower or "saas" in prompt_lower or "developer" in prompt_lower:
                profession = ["CTO", "Chief Technology Officer"]
                entity_type = "person"
                sources = ["web", "social"]
                if "20–200" in prompt_lower or "20-200" in prompt_lower:
                    employee_count = {"min": 20, "max": 200}

            elif "restaurant" in prompt_lower or "clinic" in prompt_lower:
                entity_type = "business"
                sources = ["google_maps", "web"]
                if "delhi" in prompt_lower:
                    city = "Delhi"
                if "4" in prompt_lower:
                    rating_below = 4.0

            data = {
                "entity_type": entity_type,
                "profession": profession,
                "location": {
                    "city": city or "Delhi",
                    "country": country,
                },
                "filters": {
                    "minimum_experience_years": min_exp,
                    "employee_count": employee_count,
                    "rating_below": rating_below,
                    "has_instagram": "instagram" in prompt_lower,
                },
                "sources": sources,
                "limit": 50,
                "keywords": [k for k in prompt_lower.split() if len(k) > 3][:6],
            }
            return response_schema.model_validate(data)

        # Handle QualificationResponse schema request
        elif response_schema.__name__ == "QualificationResponse":
            data = {
                "match": True,
                "score": 92.0,
                "reasons": [
                    "Entity matches requested target entity type",
                    "Location requirement satisfied",
                    "Required credentials/attributes present in source record"
                ],
                "confidence": 0.92,
            }
            return response_schema.model_validate(data)

        # Fallback default instantiation
        return response_schema.model_construct()

    async def embed(self, text: str) -> list[float]:
        # Return a standard 384-dim mock vector
        val = (len(text) % 100) / 100.0
        return [val] * 384
