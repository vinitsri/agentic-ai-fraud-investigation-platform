#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CUSTOMERS="${1:-1000}"
TRANSACTIONS="${2:-10000}"
SEED="${3:-42}"

echo "Generating synthetic data (customers=$CUSTOMERS, transactions=$TRANSACTIONS, seed=$SEED)..."

cd "$ROOT/data-generator"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"

python scripts/generate_data.py \
  --customers "$CUSTOMERS" \
  --transactions "$TRANSACTIONS" \
  --seed "$SEED" \
  --load

echo "Data loaded successfully."
