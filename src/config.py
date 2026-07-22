from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/startup_assistant"
    debug: bool = False
    llm_api_key: str = ""
    ollama_base_url: str = ""
    llm_model: str = "llama3.2:1b"
    embedding_model: str = "nomic-embed-text"

    model_config = {"env_prefix": "SA_", "env_file": ".env"}


settings = Settings()
