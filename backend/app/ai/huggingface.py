import json
import logging
from typing import Type, TypeVar
import httpx
from pydantic import BaseModel
from app.ai.base import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class HuggingFaceProvider(AIProvider):
    """
    Hugging Face Inference API Provider (supporting Serverless & Dedicated endpoints).
    """

    def __init__(self, token: str = "", model: str = ""):
        self.token = token or settings.HF_TOKEN
        self.model = model or settings.HF_MODEL
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.2,
    ) -> str:
        if not self.token:
            logger.warning("HF_TOKEN missing; falling back to Mock AI Provider text generation.")
            from app.ai.mock import MockAIProvider
            return await MockAIProvider().generate(prompt, system_prompt, max_tokens, temperature)

        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {
            "inputs": f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:",
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            res_data = response.json()
            if isinstance(res_data, list) and len(res_data) > 0:
                return res_data[0].get("generated_text", "").strip()
            elif isinstance(res_data, dict):
                return res_data.get("generated_text", "").strip()
            return str(res_data)

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
            f"You MUST respond ONLY with valid JSON matching this schema:\n{schema_json}\n"
            f"Do NOT include markdown formatting like ```json or any introductory text."
        )

        raw_text = await self.generate(prompt, system_prompt=full_system, max_tokens=max_tokens, temperature=temperature)
        
        # Clean text from backticks if present
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
            logger.warning(f"Failed to parse structured JSON from HF response: {e}. Raw text: {raw_text}")
            # Fallback to Mock provider for robustness
            from app.ai.mock import MockAIProvider
            return await MockAIProvider().structured_output(prompt, response_schema)

    async def embed(self, text: str) -> list[float]:
        if not self.token:
            from app.ai.mock import MockAIProvider
            return await MockAIProvider().embed(text)
        
        feature_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model}"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(feature_url, headers=headers, json={"inputs": text})
            if res.status_code == 200:
                res_json = res.json()
                if isinstance(res_json, list) and isinstance(res_json[0], float):
                    return res_json
                elif isinstance(res_json, list) and isinstance(res_json[0], list):
                    return res_json[0]
        from app.ai.mock import MockAIProvider
        return await MockAIProvider().embed(text)
