import pytest
from app.ai.planner import AIQueryPlanner
from app.ai.mock import MockAIProvider


@pytest.mark.asyncio
async def test_ai_planner_therapists_mathura():
    planner = AIQueryPlanner(provider=MockAIProvider())
    plan = await planner.plan("Find therapists in Mathura with at least 5 years of experience.")
    
    assert plan.entity_type in ("person", "professional")
    assert plan.location.city == "Mathura"
    assert plan.filters.minimum_experience_years == 5.0
    assert "therapist" in plan.profession or "psychologist" in plan.profession


@pytest.mark.asyncio
async def test_ai_planner_saas_cto():
    planner = AIQueryPlanner(provider=MockAIProvider())
    plan = await planner.plan("Find SaaS CTOs in India working at companies with 20–200 employees.")
    
    assert plan.location.country == "India"
    assert "CTO" in plan.profession or "Chief Technology Officer" in plan.profession
