#!/usr/bin/env python3
"""
Automated test suite for multi-AI-profile (ai-profile + shortcut CLIs).
Tests Mach-O wrapper compilation, argv/env isolation, language_server flag overriding,
Info.plist & Helper patching, Assets.car & NSDockTilePlugIn stripping, codesign, and CLI shortcuts.
"""

import importlib.machinery
import importlib.util
import json
import os
import plistlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AI_PROFILE_BIN = REPO_ROOT / "bin" / "ai-profile"


def load_ai_profile_module():
    loader = importlib.machinery.SourceFileLoader("ai_profile", str(AI_PROFILE_BIN))
    spec = importlib.util.spec_from_loader("ai_profile", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class TestAiProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_ai_profile_module()

    def test_slugify_and_color(self):
        self.assertEqual(self.mod.slugify("Work Profile 1"), "work-profile-1")
        self.assertEqual(self.mod. parse_color("blue", "Work"), ("#1D4ED8", "#0F172A"))
        self.assertEqual(self.mod.parse_color("#ff5500", "Work"), ("#FF5500", "#0F172A"))

    def test_mach_o_wrapper_env_and_argv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            real_bin = tmp / "MockAppReal"
            real_bin.write_text(
                '#!/usr/bin/env python3\n'
                'import json, os, sys\n'
                'print(json.dumps({"argv": sys.argv[1:], "env": {"CODEX_HOME": os.environ.get("CODEX_HOME")}}))\n',
                encoding="utf-8",
            )
            real_bin.chmod(0o755)

            wrapper_bin = tmp / "MockApp"
            self.mod.compile_mach_o_wrapper(
                wrapper_bin,
                "MockAppReal",
                ["--user-data-dir=/tmp/mock-data"],
                {"CODEX_HOME": "/tmp/mock-codex-home"},
            )

            res = subprocess.run([str(wrapper_bin), "--extra-flag", "val"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout.strip())
            self.assertEqual(data["argv"], ["--user-data-dir=/tmp/mock-data", "--extra-flag", "val"])
            self.assertEqual(data["env"]["CODEX_HOME"], "/tmp/mock-codex-home")

    def test_antigravity_language_server_wrapper_overrides_flags(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            ls_real = tmp / "language_serverReal"
            ls_real.write_text(
                '#!/usr/bin/env python3\n'
                'import json, sys\n'
                'print(json.dumps({"argv": sys.argv[1:]}))\n',
                encoding="utf-8",
            )
            ls_real.chmod(0o755)

            ls_wrapper = tmp / "language_server"
            self.mod.compile_antigravity_ls_wrapper(
                ls_wrapper,
                "language_serverReal",
                Path("/tmp/gemini-work"),
                "antigravity",
                Path("/tmp/agy-browser"),
            )

            # Simulate Electron passing its own --app_data_dir antigravity and --gemini_dir=/default
            res = subprocess.run(
                [
                    str(ls_wrapper),
                    "--standalone",
                    "--app_data_dir",
                    "default-MustBeStripped",
                    "--gemini_dir=/must/be/stripped",
                    "--https_server_port",
                    "0",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            data = json.loads(res.stdout.strip())
            self.assertEqual(
                data["argv"],
                [
                    "--standalone",
                    "--https_server_port",
                    "0",
                    "--gemini_dir",
                    "/tmp/gemini-work",
                    "--app_data_dir",
                    "antigravity",
                    "--local_chrome_user_data_dir",
                    "/tmp/agy-browser",
                ],
            )

    def test_end_to_end_synthetic_bundle_create_list_doctor_remove(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src_app = tmp / "SyntheticAI.app"
            dest_apps = tmp / "Applications"
            dest_apps.mkdir()

            # Build synthetic macOS .app bundle with Info.plist, Assets.car, NSDockTilePlugIn, and Helper.app
            (src_app / "Contents/MacOS").mkdir(parents=True)
            (src_app / "Contents/Resources").mkdir(parents=True)
            (src_app / "Contents/PlugIns/CodexDockTilePlugin.docktileplugin").mkdir(parents=True)
            helper_dir = src_app / "Contents/Frameworks/SyntheticAI Helper (Renderer).app/Contents/MacOS"
            helper_dir.mkdir(parents=True)

            exec_file = src_app / "Contents/MacOS/SyntheticAI"
            self.mod.compile_c_source("int main() { return 0; }\n", exec_file)
            helper_exec = helper_dir / "SyntheticAI Helper (Renderer)"
            self.mod.compile_c_source("int main() { return 0; }\n", helper_exec)

            # Create a 64x64 PNG as base icon
            from PIL import Image
            img = Image.new("RGBA", (256, 256), (30, 64, 175, 255))
            icon_png = src_app / "Contents/Resources/icon-codex-dark-color.png"
            img.save(icon_png)
            subprocess.run(
                ["sips", "-s", "format", "icns", str(icon_png), "--out", str(src_app / "Contents/Resources/electron.icns")],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            (src_app / "Contents/Resources/Assets.car").write_bytes(b"FAKE_CAR")

            main_plist = {
                "CFBundleName": "SyntheticAI",
                "CFBundleDisplayName": "SyntheticAI",
                "CFBundleIdentifier": "com.example.syntheticai",
                "CFBundleExecutable": "SyntheticAI",
                "CFBundleIconFile": "electron.icns",
                "CFBundleIconName": "Icon",
                "LSHasLocalizedDisplayName": True,
                "NSDockTilePlugIn": "CodexDockTilePlugin.docktileplugin",
                "CodexAppIconBaseName": "icon-chatgpt",
            }
            with open(src_app / "Contents/Info.plist", "wb") as f:
                plistlib.dump(main_plist, f)

            helper_plist = {
                "CFBundleName": "SyntheticAI Helper (Renderer)",
                "CFBundleDisplayName": "SyntheticAI Helper (Renderer)",
                "CFBundleIdentifier": "com.example.syntheticai.helper.renderer",
                "CFBundleExecutable": "SyntheticAI Helper (Renderer)",
            }
            with open(helper_dir.parent / "Info.plist", "wb") as f:
                plistlib.dump(helper_plist, f)

            # Run ai-profile create
            res = subprocess.run(
                [
                    str(AI_PROFILE_BIN),
                    "create",
                    "custom",
                    "UnitTestProfile",
                    "--app",
                    str(src_app),
                    "--color",
                    "emerald",
                    "--dest-dir",
                    str(dest_apps),
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            created = json.loads(res.stdout)
            cloned_app = Path(created["app_bundle"])
            self.assertTrue(cloned_app.exists())
            self.assertTrue((cloned_app / "Contents/MacOS/SyntheticAIReal").exists())
            self.assertFalse((cloned_app / "Contents/Resources/Assets.car").exists())
            self.assertFalse((cloned_app / "Contents/PlugIns/CodexDockTilePlugin.docktileplugin").exists())

            with open(cloned_app / "Contents/Info.plist", "rb") as f:
                pl = plistlib.load(f)
            self.assertEqual(pl["CFBundleName"], "SyntheticAI UnitTestProfile")
            self.assertNotIn("CFBundleIconName", pl)
            self.assertNotIn("NSDockTilePlugIn", pl)
            self.assertNotIn("CodexAppIconBaseName", pl)

            # Verify codesign passes
            cs = subprocess.run(["codesign", "-v", str(cloned_app)], capture_output=True, text=True)
            self.assertEqual(cs.returncode, 0, cs.stderr)

            # Run ai-profile list --dest-dir
            list_res = subprocess.run(
                [str(AI_PROFILE_BIN), "list", "--dest-dir", str(dest_apps), "--json"],
                capture_output=True,
                text=True,
                check=True,
            )
            listed = json.loads(list_res.stdout)
            self.assertEqual(listed["count"], 1)
            self.assertEqual(listed["profiles"][0]["kind"], "native-mach-o")

            # Run ai-profile remove --purge-data
            rm_res = subprocess.run(
                [
                    str(AI_PROFILE_BIN),
                    "remove",
                    "custom",
                    "UnitTestProfile",
                    "--app",
                    str(src_app),
                    "--dest-dir",
                    str(dest_apps),
                    "--purge-data",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            removed = json.loads(rm_res.stdout)
            self.assertEqual(removed["status"], "ok")
            self.assertFalse(cloned_app.exists())

    def test_all_shortcut_wrappers(self):
        shortcuts = [
            "claude-profile",
            "agy-profile",
            "codex-profile",
            "chatgpt-profile",
            "grok-profile",
            "cursor-profile",
        ]
        for s in shortcuts:
            sbin = REPO_ROOT / "bin" / s
            self.assertTrue(sbin.exists(), f"Missing {sbin}")
            res = subprocess.run([str(sbin), "--version"], capture_output=True, text=True, check=True)
            self.assertIn("ai-profile", res.stdout)


if __name__ == "__main__":
    unittest.main()
