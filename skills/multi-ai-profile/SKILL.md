---
name: multi-ai-profile
description: Create, audit, migrate, and manage isolated multi-profile macOS desktop app instances for Claude Desktop, Google Antigravity, OpenAI Codex / ChatGPT, xAI Grok, Cursor, Windsurf, Cline, and any Electron/Chromium AI app with distinct window names, badged Dock icons, zero APFS disk overhead, shared skill/agent symlinking, and separate MCP / CLI configurations.
---

# Universal macOS Multi-AI-Profile (`ai-profile` v2.0)

Use this skill whenever the user wants to:
- Create a second/third isolated **Claude Desktop**, **Google Antigravity**, **OpenAI Codex / ChatGPT**, **xAI Grok**, **Cursor**, **Windsurf**, or **Cline** app on macOS (`Work`, `Extra`, `Personal`, `Client`, `1`, `2`, etc.)
- Customize the app name in AltTab / Mission Control / Dock and add a high-contrast pill badge (`WORK`, `EXTRA`, etc.) to the app icon
- Isolate accounts, cookies, CLI homes (`CLAUDE_CONFIG_DIR`, `--gemini_dir`, `CODEX_HOME`, `GROK_HOME`), and MCP server configurations per profile while automatically symlinking shared global skills, agents, rules, and plugins
- Upgrade broken `osacompile` AppleScript (`applet`) wrappers to native APFS Copy-on-Write Mach-O bundles (`ai-profile migrate` / `ai-profile doctor --fix`)

## Why Not `osacompile` / `open -n -a`?

AppleScript wrappers (`osacompile`) that call `open -n -a "Claude" --args --user-data-dir=...` fail in macOS WindowServer:
1. **Duplicate Window Names:** AltTab, Mission Control, and `Cmd+Tab` read `CFBundleName` from the running process's `Info.plist` and `Contents/Frameworks/*Helper*.app`, so every window still displays as `Claude`, `Antigravity`, `ChatGPT`, or `Grok Bot`.
2. **Duplicate Icons, `Assets.car` & `NSDockTilePlugIn` Override:** macOS Sequoia prioritizes `Assets.car` (`CFBundleIconName`) over `.icns`, and `ChatGPT.app` loads `CodexDockTilePlugin.docktileplugin` (`NSDockTilePlugIn`) at runtime unless stripped on the clone.
3. **Shared Background Daemons & CLI Homes:**
   - **Antigravity:** `Contents/Resources/bin/language_server` passes `--app_data_dir antigravity` (relative to `--gemini_dir`) and defaults to `~/.gemini` unless wrapped with an `argv`-filtering Mach-O binary that overrides `--gemini_dir`, `--app_data_dir`, and `--local_chrome_user_data_dir`.
   - **OpenAI Codex / ChatGPT:** Reads `~/.codex` (`auth.json`, `config.toml`) unless `CODEX_HOME` and `CODEX_ELECTRON_USER_DATA_PATH` are injected into the native Mach-O launcher.
   - **xAI Grok Desktop:** Reads `~/.grok` and `~/.grokbot` unless `GROK_HOME`, `SAND_DATA_ROOT`, and `SAND_USER_DATA_DIR` are injected.

## Commands

### 1. Universal CLI (`ai-profile`)

```bash
# Create isolated profiles for any supported target
ai-profile create claude "Work" --color blue
ai-profile create antigravity "Work" --color blue
ai-profile create codex "Work" --color blue
ai-profile create grok "Work" --color blue
ai-profile create chatgpt "Extra" --color purple
ai-profile create cursor "Work" --color emerald

# Share primary account login while isolating windows, UI state & conversations
ai-profile create antigravity "Sandbox" --color cyan --share-auth

# Clone any custom Electron/Chromium .app on macOS
ai-profile create custom "Work" --app "/Applications/Perplexity.app" --color cyan

# List all isolated AI profiles across ~/Applications and /Applications (supports --json)
ai-profile list
ai-profile list --json

# Audit dependencies, codesign health, and legacy applets (auto-repair with --fix)
ai-profile doctor
ai-profile doctor --fix

# Migrate legacy osacompile applets to native Mach-O bundles while preserving all data
ai-profile migrate

# Remove a profile (preserves data by default; add --purge-data to wipe)
ai-profile remove codex "Work"
ai-profile remove codex "Work" --purge-data
```

### 2. Shortcut CLIs

```bash
claude-profile create "Work" --color blue
agy-profile create "Work" --color blue
codex-profile create "Work" --color blue
chatgpt-profile create "Work" --color blue
grok-profile create "Work" --color blue
cursor-profile create "Work" --color emerald
```

### Available Badge Colors
`blue`, `purple`, `emerald` (`green`), `amber` (`orange`), `rose` (`red`, `pink`), `cyan` (`teal`), `slate` (`gray`, `dark`), `terracotta`, or any 6-digit hex code (`#RRGGBB`).
