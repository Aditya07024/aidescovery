import logging
from typing import Any, Dict, Optional
from app.ai.base import AIProvider
from app.ai.factory import get_ai_provider
from app.schemas.qualification import QualificationResponse
from app.schemas.query_plan import SearchPlan

logger = logging.getLogger(__name__)

QUALIFICATION_SYSTEM_PROMPT = """
You are an objective AI Entity Auditor. Your task is to evaluate a candidate entity against search criteria.
CRITICAL RULE: Rely strictly on observed source facts provided in the entity profile.
Do NOT hallucinate missing experience, credentials, or locations.
If a required criterion cannot be verified from the profile, state it as "unknown" in the reasons and adjust the score accordingly.
"""


class AIQualifier:
    """
    AI Qualification Engine.
    Scores and qualifies entities against SearchPlan criteria with fact-based justification.
    """

    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or get_ai_provider()

    async def qualify(self, entity_data: Dict[str, Any], plan: SearchPlan) -> QualificationResponse:
        logger.info(f"[AIQualifier] Qualifying entity '{entity_data.get('name')}' against plan")

        prompt = (
            f"Search Criteria:\n"
            f"- Entity Type: {plan.entity_type}\n"
            f"- Profession/Role: {', '.join(plan.profession)}\n"
            f"- Target Location: {plan.location.city or 'Any'}, {plan.location.country or 'India'}\n"
            f"- Required Min Experience: {plan.filters.minimum_experience_years or 'N/A'} years\n"
            f"- Rating Filter: {plan.filters.rating_below or 'N/A'}\n\n"
            f"Entity Observed Record:\n"
            f"- Name: {entity_data.get('name')}\n"
            f"- Type: {entity_data.get('entity_type')}\n"
            f"- Description: {entity_data.get('description')}\n"
            f"- Location: {entity_data.get('location_summary')}\n"
            f"- Attributes: {entity_data.get('attributes', {})}\n"
            f"- Provenance Facts: {entity_data.get('raw_provenance', [])}\n"
        )

        try:
            res = await self.provider.structured_output(
                prompt=prompt,
                response_schema=QualificationResponse,
                system_prompt=QUALIFICATION_SYSTEM_PROMPT,
                temperature=0.1,
            )
            return res
        except Exception as e:
            logger.warning(f"AI qualification prompt failed: {e}. Executing deterministic qualification fallback.")
            return self._deterministic_qualify(entity_data, plan)

    def _deterministic_qualify(self, entity_data: Dict[str, Any], plan: SearchPlan) -> QualificationResponse:
        reasons = []
        score = 80.0
        match = True

        name_desc = (str(entity_data.get("name")) + " " + str(entity_data.get("description"))).lower()

        # Location check
        if plan.location.city:
            if plan.location.city.lower() in name_desc or plan.location.city.lower() in str(entity_data.get("location_summary", "")).lower():
                reasons.append(f"Located in target city ({plan.location.city})")
                score += 10
            else:
                reasons.append(f"Location in {plan.location.city} is unknown from observed facts")
                score -= 15

        # Profession check
        if plan.profession:
            found_prof = [p for p in plan.profession if p.lower() in name_desc]
            if found_prof:
                reasons.append(f"Matches profession criteria ({', '.join(found_prof)})")
                score += 10
            else:
                reasons.append("Target profession role not explicitly verified")
                score -= 10

        # Min experience check
        if plan.filters.minimum_experience_years:
            exp_val = entity_data.get("attributes", {}).get("experience_years")
            if exp_val and float(exp_val) >= plan.filters.minimum_experience_years:
                reasons.append(f"Experience years verified ({exp_val} years >= {plan.filters.minimum_experience_years})")
            else:
                reasons.append(f"Minimum experience of {plan.filters.minimum_experience_years} years unknown or unverified")

        final_score = max(0.0, min(100.0, score))
        return QualificationResponse(
            match=final_score >= 60.0,
            score=final_score,
            reasons=reasons,
            confidence=0.90,
        )
