"""Configure a local key via a macOS hidden-input dialog, without echoing it."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.platform != "darwin":
        print("This helper needs macOS. Edit the ignored .env file locally instead.")
        return 1
    path = ROOT / ".env"
    if path.is_symlink():
        print("Refusing to write a symlink. Configure a regular project-local .env file.")
        return 1
    dialog = '''text returned of (display dialog "请输入 OpenAI API Key。输入内容将隐藏，仅写入本项目的 .env，不会显示在聊天或终端中。" with title "澄序 · 配置 OpenAI" default answer "" with hidden answer buttons {"取消", "保存"} default button "保存" cancel button "取消")'''
    try:
        result = subprocess.run(["osascript", "-e", dialog], capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        print("The key-entry dialog could not complete. No configuration was changed.")
        return 1
    if result.returncode:
        print("Key setup cancelled or dialog unavailable. No configuration was changed.")
        return 1
    key = result.stdout.strip()
    if not key.startswith("sk-") or any(c.isspace() for c in key) or len(key) < 20:
        print("The value does not look like an OpenAI API key. No configuration was changed.")
        return 1
    lines = path.read_text().splitlines() if path.exists() else (ROOT / ".env.example").read_text().splitlines()
    updated = []
    inserted = False
    for line in lines:
        if line.strip().removeprefix("export ").startswith("OPENAI_API_KEY="):
            if not inserted:
                updated.append("OPENAI_API_KEY=" + key)
                inserted = True
        else:
            updated.append(line)
    if not inserted:
        updated.append("OPENAI_API_KEY=" + key)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=ROOT, prefix=".env.", delete=False) as stream:
            temp_path = Path(stream.name)
            os.fchmod(stream.fileno(), 0o600)
            stream.write("\n".join(updated) + "\n")
        os.replace(temp_path, path)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
    print("OpenAI key saved to the project-local .env with owner-only permissions. Key value was not printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
