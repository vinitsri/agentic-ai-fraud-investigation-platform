from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    ai_service_host: str = "0.0.0.0"
    ai_service_port: int = 8000
    database_url: str = "postgresql://fraud_user:change_me@localhost:5432/fraud_platform"
    redis_url: str = "redis://localhost:6379/0"
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:7b"


settings = Settings()
