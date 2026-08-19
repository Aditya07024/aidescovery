import logging
from typing import Optional
from app.ai.base import AIProvider
from app.ai.huggingface import HuggingFaceProvider
from app.ai.mock import MockAIProvider
from app.ai.ollama import OllamaProvider
from app.ai.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    name = (provider_name or settings.DEFAULT_AI_PROVIDER).lower()

    if name == "huggingface":
        if settings.HF_TOKEN:
            return HuggingFaceProvider()
        logger.info("HF_TOKEN missing; using MockAIProvider")
        return MockAIProvider()

    elif name in ("openai", "openai_compatible"):
        if settings.OPENAI_API_KEY:
            return OpenAICompatibleProvider()
        logger.info("OPENAI_API_KEY missing; using MockAIProvider")
        return MockAIProvider()

    elif name == "ollama":
        return OllamaProvider()

    elif name == "mock":
        return MockAIProvider()

    logger.warning(f"Unknown AI provider requested: '{name}'. Falling back to MockAIProvider.")
    return MockAIProvider()
