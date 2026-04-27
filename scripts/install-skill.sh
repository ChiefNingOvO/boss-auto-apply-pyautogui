#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SOURCE="${REPO_ROOT}/skills/boss-auto-apply"
TARGET_ROOT="${CODEX_HOME}/skills"
TARGET="${TARGET_ROOT}/boss-auto-apply"

if [[ ! -d "$SOURCE" ]]; then
  echo "Skill source not found: $SOURCE" >&2
  exit 1
fi

mkdir -p "$TARGET_ROOT"
rm -rf "$TARGET"
cp -R "$SOURCE" "$TARGET"

echo "Installed boss-auto-apply skill to $TARGET"
echo "Restart Codex or open a new session to refresh the skill list."
