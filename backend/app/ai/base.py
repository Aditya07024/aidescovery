from typing import Any, Dict, Protocol, Type, TypeVar, runtime_checkable
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@runtime_checkable
class AIProvider(Protocol):
    """
    Common protocol interface for all AI Providers (Hugging Face, OpenAI, Ollama, Mock).
    """

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.2,
    ) -> str:
        """Generate unstructured text from prompt."""
        ...

    async def structured_output(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> T:
        """Generate validated Pydantic model instance from prompt."""
        ...

    async def embed(self, text: str) -> list[float]:
        """Generate text embedding vector."""
        ...
