import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "default-insecure-secret-key-change-me-32-chars-minimum"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./aidiscovery.db"
    SYNC_DATABASE_URL: str = "sqlite:///./aidiscovery.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Provider Defaults
    DEFAULT_AI_PROVIDER: str = "mock"  # huggingface, openai, ollama, mock
    HF_TOKEN: str = ""
    HF_MODEL: str = "meta-llama/Llama-3.2-3B-Instruct"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # Connectors API Keys
    GOOGLE_API_KEY: str = ""
    GOOGLE_SEARCH_ENGINE_ID: str = ""
    SERPER_API_KEY: str = ""
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    YOUTUBE_API_KEY: str = ""
    APIFY_API_TOKEN: str = ""

    # Crawler Settings
    CRAWLER_MAX_CONCURRENCY: int = 5
    CRAWLER_TIMEOUT_SECONDS: int = 10
    CRAWLER_USER_AGENT: str = "UniversalAIDiscoveryBot/1.0 (+https://github.com/ai-discovery)"
    SSRF_PROTECTION_ENABLED: bool = True

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
