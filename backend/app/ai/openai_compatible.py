import json
import logging
from typing import Type, TypeVar
import httpx
from pydantic import BaseModel
from app.ai.base import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class OpenAICompatibleProvider(AIProvider):
    """
    OpenAI-compatible Chat Completions API Provider.
    """

    def __init__(self, api_key: str = "", model: str = "", base_url: str = ""):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.base_url = (base_url or settings.OPENAI_BASE_URL).rstrip("/")

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.2,
    ) -> str:
        if not self.api_key:
            logger.warning("OPENAI_API_KEY missing; falling back to Mock AI Provider.")
            from app.ai.mock import MockAIProvider
            return await MockAIProvider().generate(prompt, system_prompt, max_tokens, temperature)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            res_data = response.json()
            return res_data["choices"][0]["message"]["content"].strip()

    async def structured_output(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> T:
        schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
        full_system = (
            f"{system_prompt}\n"
            f"You MUST respond strictly with a valid JSON object adhering to this schema:\n{schema_json}"
        )
        raw_text = await self.generate(prompt, system_prompt=full_system, max_tokens=max_tokens, temperature=temperature)
        
        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        try:
            parsed = json.loads(clean_text)
            return response_schema.model_validate(parsed)
        except Exception as e:
            logger.warning(f"Structured JSON parsing failed in OpenAI provider: {e}")
            from app.ai.mock import MockAIProvider
            return await MockAIProvider().structured_output(prompt, response_schema)

    async def embed(self, text: str) -> list[float]:
        if not self.api_key:
            from app.ai.mock import MockAIProvider
            return await MockAIProvider().embed(text)

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": "text-embedding-3-small", "input": text}

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(f"{self.base_url}/embeddings", headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data["data"][0]["embedding"]
        from app.ai.mock import MockAIProvider
        return await MockAIProvider().embed(text)
