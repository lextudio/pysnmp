#!/usr/bin/env python3
"""
Prepare local development environment by pinning a Python version with `uv` and
ensuring the virtual environment matches that pin.

Usage examples:
    ./run_prepare.py 3.14   # Pin to latest 3.14.x and reuse/recreate venv
    ./run_prepare.py 3.13.2 # Pin exact patch (requires that version available)

If no argument is given, uses the version in `.python-version`.
This script does NOT use pyenv anymore.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def resolve_requested_version(arg_version: Optional[str]) -> str:
    """Determine requested Python version from CLI arg or .python-version file.

    Leaves the version string untouched (user may specify major.minor or full semver).
    """
    python_version_file = Path(".python-version")
    file_version = None
    if python_version_file.exists():
        file_version = python_version_file.read_text(encoding="utf-8").strip()
    chosen = arg_version or file_version
    if not chosen:
        print(
            "Error: No Python version specified and .python-version not found.",
            file=sys.stderr,
        )
        sys.exit(1)
    return chosen.strip()


def get_existing_venv_python_version(venv_path: Path) -> Optional[str]:
    """Return full version (major.minor.patch) of existing venv interpreter or None on failure."""
    exe = venv_path / "bin" / "python"
    if not exe.exists():  # On Windows the path would differ; not handled here.
        return None
    try:
        out = subprocess.check_output(
            [
                str(exe),
                "-c",
                "import sys; print('.'.join(map(str, sys.version_info[:3])))",
            ],
            text=True,
        )
        return out.strip()
    except subprocess.CalledProcessError:
        return None


def versions_match(requested: str, existing_full: str) -> bool:
    """Compare requested vs existing venv version.

    If requested is '3.14' we match any '3.14.x'. If requested includes patch, require exact.
    """
    req_parts = requested.split(".")
    exist_parts = existing_full.split(".")
    if len(req_parts) == 2:
        return req_parts[0] == exist_parts[0] and req_parts[1] == exist_parts[1]
    if len(req_parts) >= 3:
        return (
            req_parts[0] == exist_parts[0]
            and req_parts[1] == exist_parts[1]
            and req_parts[2] == exist_parts[2]
        )
    return False


def ensure_venv(pinned_version: str) -> bool:
    """Ensure .venv interpreter matches pin.

    Returns True if a new venv was created, False if existing reused.
    Avoids unnecessary rebuild if uv already recreated it during pin.
    """
    venv_path = Path(".venv")
    existing_version = (
        get_existing_venv_python_version(venv_path) if venv_path.exists() else None
    )
    if existing_version and versions_match(pinned_version, existing_version):
        print(f"Venv OK: Python {existing_version} matches pin {pinned_version}")
        return False
    # If venv exists but mismatch/broken, remove then recreate.
    if venv_path.exists():
        print("Recreating venv: existing interpreter mismatch or broken...")
        shutil.rmtree(venv_path)
    print(f"Creating venv for Python {pinned_version}...")
    subprocess.run(["uv", "venv", f"--python={pinned_version}"], check=True)
    return True


def main():
    """Main function to switch Python versions."""
    parser = argparse.ArgumentParser(
        description="Switch Python version for development."
    )
    parser.add_argument(
        "python_version", nargs="?", help="Python version to switch to (e.g., 3.12)"
    )

    args = parser.parse_args()

    requested_version = resolve_requested_version(args.python_version)
    previous_version = resolve_requested_version(
        None
    )  # current .python-version before pin
    changed = requested_version != previous_version if previous_version else True
    print(f"Requested Python version: {requested_version}")
    if changed:
        print(f"Pinning Python version via uv: {requested_version}")
        subprocess.run(["uv", "python", "pin", requested_version], check=True)
    else:
        print("Requested version already pinned; skipping pin step.")

    # After pin, read back the (possibly normalized) pinned version
    pinned_version = resolve_requested_version(None)
    if previous_version and pinned_version != previous_version:
        print(f".python-version updated: {previous_version} -> {pinned_version}")

    # Check if uv already satisfied the venv (it may rebuild automatically on pin)
    recreated = ensure_venv(pinned_version)
    if recreated:
        print("Installing development dependencies (editable + dev extras)...")
        subprocess.run(["uv", "pip", "install", "-e", ".[dev]"], check=True)
    else:
        print("Ensuring dependencies are up-to-date (sync dev extras)...")
        subprocess.run(["uv", "sync", "--extra", "dev"], check=True)

    final_version = get_existing_venv_python_version(Path(".venv"))
    if final_version:
        print(f"Active venv Python version: {final_version} (pin: {pinned_version})")
    print("Environment ready.")
    print("To activate this environment manually, run:")
    print("  source .venv/bin/activate  # macOS/Linux")
    print("  .venv\\Scripts\\activate    # Windows")


if __name__ == "__main__":
    main()
