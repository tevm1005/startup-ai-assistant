from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/startup_assistant"
    debug: bool = False
    llm_api_key: str = ""
    llm_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    model_config = {"env_prefix": "SA_", "env_file": ".env"}


settings = Settings()
