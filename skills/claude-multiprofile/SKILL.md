---
name: claude-multiprofile
description: Create and manage isolated multi-profile Claude Desktop instances on macOS with distinct names, badged icons, dedicated data directories, and separate MCP server configurations.
---

# Claude Multi-Profile Workflow & CLI

Use this skill whenever you need to create, manage, or debug separate Claude Desktop profiles on macOS.

Each created profile has:
1. **Dedicated macOS Standalone Bundle:** Cloned via instant APFS copy-on-write to `~/Applications/Claude <Name>.app`.
2. **Distinct App & Window Identity:** Own `CFBundleDisplayName` and `CFBundleIdentifier` so AltTab, Mission Control, Cmd+Tab, and Menubar show the exact profile name (e.g. `Claude Work`, `Claude Extra`) instead of generic `Claude`.
3. **Badged Custom Icon:** Built-in Pillow + `iconutil` pipeline badges the official Claude icon with a high-contrast pill tag (`WORK`, `EXTRA`, etc.) and custom color.
4. **Isolated Storage & Credentials:** Data stored at `~/Library/Application Support/Claude-<Name>`.
5. **Separate MCP Servers:** Independent `claude_desktop_config.json` per profile.

---

## 1. Quick CLI Usage

A CLI tool is installed at `~/.local/bin/claude-profile`.

### Create a Profile
```bash
claude-profile create <Name> [--color <color>]
```
- Available colors: `blue`, `purple`, `green`, `emerald`, `orange`, `amber`, `red`, `pink`, `cyan`, `teal`, `gray`, `dark`.
- Examples:
  ```bash
  claude-profile create Work --color blue
  claude-profile create Extra --color purple
  claude-profile create Personal --color emerald
  claude-profile create Dev --color orange
  ```

### List Profiles
```bash
claude-profile list
```

### Delete Profile App
```bash
claude-profile delete <Name>
```
*(Preserves user data directory so no chats/credentials are lost unintentionally).*

---

## 2. Profile Paths Reference

- **Profile 1 (Default):**
  - App: `/Applications/Claude.app`
  - Data: `~/Library/Application Support/Claude`
  - MCP: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Profile N (`Claude <Name>`):**
  - App: `~/Applications/Claude <Name>.app`
  - Data: `~/Library/Application Support/Claude-<Name>`
  - MCP: `~/Library/Application Support/Claude-<Name>/claude_desktop_config.json`

---

## 3. Architecture Details

When building manually without the CLI:
1. **APFS Clone:** `cp -cR /Applications/Claude.app ~/Applications/"Claude <Name>.app"`
2. **Rename Framework Helpers:** In `Contents/Frameworks/`, rename `Claude Helper*.app` to `Claude <Name> Helper*.app` and update inner `Info.plist` (both CFBundleDisplayName, CFBundleName, and CFBundleExecutable).
3. **Info.plist:** Set `CFBundleDisplayName`, `CFBundleName`, `CFBundleIdentifier`, remove `CFBundleIconName` and `Assets.car`.
4. **Launcher:** Replace `Contents/MacOS/Claude` with a native Mach-O C binary that invokes `Claude.real --user-data-dir="$HOME/Library/Application Support/Claude-<Name>"` with `execv()`.
5. **Icon:** Place badged `.icns` at `Contents/Resources/electron.icns`.
6. **Codesign & Register:** `codesign --force --deep --sign - ...` and `lsregister -f -r ...`.

---

## 4. Antigravity Multi-Profile CLI (`agy-profile`)

An equivalent CLI tool is installed at `~/.local/bin/agy-profile` for creating isolated **Antigravity.app** instances:

### Create an Antigravity Profile
```bash
# Mode 1: Isolated Google Account + isolated conversations + symlinked global skills/agents/rules
agy-profile create Work --color blue
agy-profile create Extra --color purple

# Mode 2: Share the default Google Account login while isolating windows & conversation state
agy-profile create Second --color emerald --share-auth
```

### How Antigravity Multi-Profile Works Under the Hood
Unlike Claude Desktop (which only needs `--user-data-dir` on the Electron binary), Antigravity has two layers:
1. **Electron Frontend (`Contents/MacOS/Antigravity`):** Wrapped with a Mach-O launcher passing `--user-data-dir="$HOME/Library/Application Support/Antigravity-<Name>"` to bypass `requestSingleInstanceLock()` and isolate window/UI state, plus `CFBundleDisplayName` / `CFBundleIdentifier` and badged `icon.icns`.
2. **Go Backend (`Contents/Resources/bin/language_server`):** Wrapped with a Mach-O launcher passing `--gemini_dir="$HOME/.gemini-profiles/<Name>"` (which isolates `jetski-standalone-oauth-token` and `antigravity/` state while symlinking `GEMINI.md`, `config/skills`, `config/agents`, and `config/plugins` from `~/.gemini`).
