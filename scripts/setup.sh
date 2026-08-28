#!/usr/bin/env bash
set -euo pipefail

echo "=== Agentic AI Fraud Investigation Platform - Setup ==="

command -v docker >/dev/null 2>&1 || { echo "Docker required"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Docker Compose required"; exit 1; }

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo "Starting infrastructure (PostgreSQL, Redis)..."
docker compose up -d postgres redis

echo "Waiting for PostgreSQL..."
until docker compose exec -T postgres pg_isready -U fraud_user -d fraud_platform >/dev/null 2>&1; do
  sleep 2
done

echo "Generating synthetic data..."
"$ROOT/scripts/load-data.sh" 1000 10000 42

"$ROOT/scripts/install-git-hooks.sh"

echo ""
echo "Setup complete."
echo "  PostgreSQL: localhost:5432"
echo "  Redis:      localhost:6379"
echo ""
echo "Next: ./scripts/health-check.sh"
