from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from app.api.deps import get_current_api_key
from app.core.config import settings

router = APIRouter()


@router.get("/providers", response_model=List[Dict[str, Any]])
async def list_ai_providers(api_key=Depends(get_current_api_key)):
    """
    Returns available AI provider integrations and current configured active default.
    """
    return [
        {
            "name": "huggingface",
            "active": settings.DEFAULT_AI_PROVIDER.lower() == "huggingface",
            "model": settings.HF_MODEL,
            "configured": bool(settings.HF_TOKEN),
        },
        {
            "name": "openai",
            "active": settings.DEFAULT_AI_PROVIDER.lower() in ("openai", "openai_compatible"),
            "model": settings.OPENAI_MODEL,
            "configured": bool(settings.OPENAI_API_KEY),
        },
        {
            "name": "ollama",
            "active": settings.DEFAULT_AI_PROVIDER.lower() == "ollama",
            "model": settings.OLLAMA_MODEL,
            "configured": True,
        },
        {
            "name": "mock",
            "active": settings.DEFAULT_AI_PROVIDER.lower() == "mock",
            "model": "deterministic-mock-v1",
            "configured": True,
        },
    ]
