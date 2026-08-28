#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_DIR="$(git -C "$ROOT" rev-parse --git-dir)/hooks"

mkdir -p "$HOOKS_DIR"
cp "$ROOT/scripts/git-hooks/commit-msg" "$HOOKS_DIR/commit-msg"
chmod +x "$HOOKS_DIR/commit-msg"

echo "Installed commit-msg hook (blocks Cursor co-author trailers)."
