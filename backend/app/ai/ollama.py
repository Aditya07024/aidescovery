import json
import logging
from typing import Type, TypeVar
import httpx
from pydantic import BaseModel
from app.ai.base import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class OllamaProvider(AIProvider):
    """
    Local Ollama API Provider.
    """

    def __init__(self, base_url: str = "", model: str = ""):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.2,
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                res.raise_for_status()
                return res.json().get("response", "").strip()
        except Exception as e:
            logger.warning(f"Ollama connection error: {e}. Falling back to Mock AI Provider.")
            from app.ai.mock import MockAIProvider
            return await MockAIProvider().generate(prompt, system_prompt, max_tokens, temperature)

    async def structured_output(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> T:
        schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
        full_system = f"{system_prompt}\nReturn JSON matching schema:\n{schema_json}"
        raw_text = await self.generate(prompt, system_prompt=full_system, max_tokens=max_tokens, temperature=temperature)
        try:
            parsed = json.loads(raw_text)
            return response_schema.model_validate(parsed)
        except Exception:
            from app.ai.mock import MockAIProvider
            return await MockAIProvider().structured_output(prompt, response_schema)

    async def embed(self, text: str) -> list[float]:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(f"{self.base_url}/api/embeddings", json={"model": self.model, "prompt": text})
                if res.status_code == 200:
                    return res.json().get("embedding", [])
        except Exception:
            pass
        from app.ai.mock import MockAIProvider
        return await MockAIProvider().embed(text)
