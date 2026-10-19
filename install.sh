#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"

mkdir -p "${BIN_DIR}"
cp "${REPO_DIR}/bin/ai-profile" "${BIN_DIR}/ai-profile"
cp "${REPO_DIR}/bin/claude-profile" "${BIN_DIR}/claude-profile"
cp "${REPO_DIR}/bin/agy-profile" "${BIN_DIR}/agy-profile"
cp "${REPO_DIR}/bin/codex-profile" "${BIN_DIR}/codex-profile"
cp "${REPO_DIR}/bin/grok-profile" "${BIN_DIR}/grok-profile"
chmod +x "${BIN_DIR}/ai-profile" "${BIN_DIR}/claude-profile" "${BIN_DIR}/agy-profile" "${BIN_DIR}/codex-profile" "${BIN_DIR}/grok-profile"

# Install Agent Skill for Claude Code & Google Antigravity
for skill_name in multi-ai-profile claude-multiprofile; do
  for skill_root in "${HOME}/.claude/skills/${skill_name}" "${HOME}/.gemini/config/skills/${skill_name}"; do
    mkdir -p "${skill_root}"
    cp "${REPO_DIR}/skills/multi-ai-profile/SKILL.md" "${skill_root}/SKILL.md"
  done
done

echo "✅ Installed universal CLI & shortcuts to ${BIN_DIR}:"
echo "   • ai-profile      (Universal: claude, antigravity, codex, chatgpt, grok, cursor, windsurf, cline, --app)"
echo "   • claude-profile  (Claude Desktop shortcut)"
echo "   • agy-profile     (Google Antigravity shortcut)"
echo "   • codex-profile   (OpenAI Codex / ChatGPT Desktop shortcut)"
echo "   • grok-profile    (xAI Grok Desktop shortcut)"
echo "✅ Installed multi-ai-profile Agent Skill for Claude Code & Antigravity"
echo ""
echo "Try creating your first isolated profiles:"
echo "  ai-profile create claude Work --color blue"
echo "  ai-profile create antigravity Work --color blue"
echo "  ai-profile create codex Work --color blue"
echo "  ai-profile create grok Work --color blue"
