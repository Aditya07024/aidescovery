import logging
from typing import Optional
from app.ai.base import AIProvider
from app.ai.factory import get_ai_provider
from app.schemas.query_plan import SearchPlan

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """
You are an expert AI Query Planner for a Universal Entity Intelligence Engine.
Your task is to take a natural language discovery request and convert it into a structured SearchPlan object.

Valid entity_types:
- person
- professional
- company
- business
- place
- creator
- organization

Valid sources:
- web
- google_maps
- reddit
- youtube
- crawler

Analyze the user's intent carefully, extract location entity criteria, numeric filters (experience years, follower counts, ratings, employee numbers), and relevant query keywords.
"""


class AIQueryPlanner:
    """
    AI Query Planner module.
    Converts natural language prompts into validated structured SearchPlan specifications.
    Includes automated prompt retry on schema validation failures.
    """

    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or get_ai_provider()

    async def plan(self, natural_language_query: str) -> SearchPlan:
        logger.info(f"Planning search for query: '{natural_language_query}'")

        # Attempt 1: Standard structured output call
        try:
            plan_obj = await self.provider.structured_output(
                prompt=f"Convert this request into a SearchPlan: '{natural_language_query}'",
                response_schema=SearchPlan,
                system_prompt=PLANNER_SYSTEM_PROMPT,
                temperature=0.1,
            )
            logger.info(f"Successfully generated SearchPlan: {plan_obj.entity_type} for {plan_obj.location.city or 'global'}")
            return plan_obj
        except Exception as e1:
            logger.warning(f"SearchPlan generation Attempt 1 failed: {e1}. Retrying with constrained prompt...")

        # Attempt 2: Constrained retry prompt
        try:
            constrained_prompt = (
                f"STRICT RETRY: Parse query into valid SearchPlan JSON object ONLY.\n"
                f"Query: '{natural_language_query}'"
            )
            plan_obj = await self.provider.structured_output(
                prompt=constrained_prompt,
                response_schema=SearchPlan,
                system_prompt=PLANNER_SYSTEM_PROMPT,
                temperature=0.0,
            )
            return plan_obj
        except Exception as e2:
            logger.error(f"SearchPlan generation Attempt 2 failed: {e2}. Falling back to default SearchPlan.")
            # Fallback safe plan
            return SearchPlan(
                entity_type="person",
                keywords=[k for k in natural_language_query.split() if len(k) > 2][:5],
            )
