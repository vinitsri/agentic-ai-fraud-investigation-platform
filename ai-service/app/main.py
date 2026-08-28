from fastapi import FastAPI

from app.config.settings import settings

app = FastAPI(
    title="Fraud Investigation AI Service",
    description="Agentic AI service for fraud investigation",
    version="0.1.0",
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ai-service",
        "environment": settings.environment,
    }
