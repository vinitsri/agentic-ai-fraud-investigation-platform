#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Checking PostgreSQL..."
docker compose exec -T postgres pg_isready -U fraud_user -d fraud_platform

echo "Checking Redis..."
docker compose exec -T redis redis-cli ping

echo "All infrastructure health checks passed."
