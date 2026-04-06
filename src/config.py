from pydantic_settings import BaseSettings
from pydantic import Field


class AppConfig(BaseSettings):
    # Infrastructure
    database_url: str = Field(..., env="DATABASE_URL")
    qdrant_url: str = Field("http://qdrant:6333", env="QDRANT_URL")
    qdrant_api_key: str | None = Field(None, env="QDRANT_API_KEY")
    searxng_url: str = Field("http://searxng:8080", env="SEARXNG_URL")

    # AI Providers
    groq_api_key: str | None = Field(None, env="GROQ_API_KEY")
    anthropic_api_key: str | None = Field(None, env="ANTHROPIC_API_KEY")

    # Observability
    langfuse_public_key: str | None = Field(None, env="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = Field(None, env="LANGFUSE_SECRET_KEY")
    langfuse_host: str | None = Field(None, env="LANGFUSE_HOST")

    # Model defaults
    default_model: str = "llama-3.3-70b-versatile"
    default_fast_model: str = "llama-3.1-8b-instant"
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Upload
    upload_dir: str = "data/uploads"
    max_upload_mb: int = 50
    ocr_dpi: int = 300

    class Config:
        env_file = ".env"
        extra = "ignore"


# Lista canónica de modelos — fuente única de verdad para backend y frontend
GROQ_MODELS = [
    {"id": "llama-3.3-70b-versatile",                   "name": "Llama 3.3 70B (Versatile)"},
    {"id": "llama-3.1-8b-instant",                      "name": "Llama 3.1 8B (Fast)"},
    {"id": "meta-llama/llama-4-scout-17b-16e-instruct", "name": "Llama 4 Scout 17B"},
    {"id": "qwen/qwen3-32b",                            "name": "Qwen3 32B"},
]

settings = AppConfig()
