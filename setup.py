"""
BizTracker — One-click setup script.
Run this once to install dependencies and launch the app.
"""

import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run(cmd, desc):
    print(f"\n  [{desc}]")
    print(f"  > {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"  [WARN] Step finished with code {result.returncode}")
    return result


def main():
    print("=" * 60)
    print("   BizTracker — Setup")
    print("=" * 60)

    # ── Check Python ──
    py = sys.executable
    print(f"\n  Python: {sys.version}")

    # ── Install pip deps ──
    run(f'"{py}" -m pip install -r requirements.txt', "Installing Python packages")

    # ── Install Playwright Chromium ──
    run(f'"{py}" -m playwright install chromium', "Installing Playwright Chromium")

    # ── Launch app ──
    print("\n" + "=" * 60)
    print("   Setup complete! Launching BizTracker...")
    print("=" * 60 + "\n")
    run(f'"{py}" main.py', "Starting app")


if __name__ == "__main__":
    main()
