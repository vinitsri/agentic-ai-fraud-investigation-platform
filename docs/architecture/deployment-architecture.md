# Deployment Architecture

## Local Development (Phase 1–2)

Docker Compose services:

- `postgres` — PostgreSQL 16 with pgvector
- `redis` — Cache

Application services (ai-service, fraud-service) enabled in later phases.

## Production Target (Phase 18)

Kubernetes deployment with optional monitoring profile (Prometheus, Grafana).
