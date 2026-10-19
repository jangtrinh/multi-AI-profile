#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$BIN_DIR"
cp "$REPO_DIR/bin/claude-profile" "$BIN_DIR/claude-profile"
cp "$REPO_DIR/bin/agy-profile" "$BIN_DIR/agy-profile"
chmod +x "$BIN_DIR/claude-profile" "$BIN_DIR/agy-profile"

# Install agent skill for Claude Code & Antigravity if directories exist
if [ -d "$HOME/.claude" ]; then
  mkdir -p "$HOME/.claude/skills/claude-multiprofile"
  cp "$REPO_DIR/skills/claude-multiprofile/SKILL.md" "$HOME/.claude/skills/claude-multiprofile/SKILL.md"
fi

if [ -d "$HOME/.gemini/config" ]; then
  mkdir -p "$HOME/.gemini/config/skills/claude-multiprofile"
  cp "$REPO_DIR/skills/claude-multiprofile/SKILL.md" "$HOME/.gemini/config/skills/claude-multiprofile/SKILL.md"
fi

echo "[✓] Installed claude-profile and agy-profile to $BIN_DIR"
echo "    Try: claude-profile create Work --color blue"
echo "    Try: agy-profile create Work --color blue"
