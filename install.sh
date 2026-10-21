#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"

mkdir -p "${BIN_DIR}"

BINS=(
  "ai-profile"
  "claude-profile"
  "agy-profile"
  "codex-profile"
  "chatgpt-profile"
  "grok-profile"
  "cursor-profile"
)

for b in "${BINS[@]}"; do
  chmod +x "${REPO_DIR}/bin/${b}"
  cp "${REPO_DIR}/bin/${b}" "${BIN_DIR}/${b}"
  chmod +x "${BIN_DIR}/${b}"
done

# Ensure Pillow is available for high-contrast badge rendering
if ! python3 -c "import PIL" >/dev/null 2>&1; then
  echo "📦 Installing Pillow for icon badge rendering..."
  python3 -m pip install --user --quiet Pillow 2>/dev/null || python3 -m pip install --break-system-packages --user --quiet Pillow || true
fi

# Install Agent Skill across Claude Code, Google Antigravity, Codex, and shared .agents
for skill_name in multi-ai-profile claude-multiprofile; do
  for skill_root in \
    "${HOME}/.claude/skills/${skill_name}" \
    "${HOME}/.gemini/config/skills/${skill_name}" \
    "${HOME}/.agents/skills/${skill_name}" \
    "${HOME}/.codex/skills/${skill_name}"; do
    mkdir -p "${skill_root}"
    cp "${REPO_DIR}/skills/multi-ai-profile/SKILL.md" "${skill_root}/SKILL.md"
  done
done

echo "✅ Installed universal CLI & shortcuts to ${BIN_DIR}:"
echo "   • ai-profile       (Universal: claude, antigravity, codex, chatgpt, codex-web, grok, cursor, windsurf, cline, custom)"
echo "   • claude-profile   (Claude Desktop shortcut)"
echo "   • agy-profile      (Google Antigravity shortcut)"
echo "   • codex-profile    (OpenAI Codex Desktop shortcut)"
echo "   • chatgpt-profile  (OpenAI ChatGPT Desktop shortcut)"
echo "   • grok-profile     (xAI Grok Desktop shortcut)"
echo "   • cursor-profile   (Cursor AI IDE shortcut)"
echo "✅ Installed multi-ai-profile Agent Skill for Claude Code, Antigravity & Codex"
echo ""
"${BIN_DIR}/ai-profile" doctor
