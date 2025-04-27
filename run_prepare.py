#!/usr/bin/env python3
"""
Script to switch Python versions for development.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_python_path(version):
    """Get path to Python executable from pyenv."""
    try:
        return (
            subprocess.check_output(["pyenv", "which", f"python{version}"])
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError as e:
        print(f"Error finding Python {version} with pyenv: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to switch Python versions."""
    parser = argparse.ArgumentParser(
        description="Switch Python version for development."
    )
    parser.add_argument(
        "python_version", nargs="?", help="Python version to switch to (e.g., 3.12)"
    )

    args = parser.parse_args()

    python_version_file = Path(".python-version")
    current_version = None
    if python_version_file.exists():
        with open(python_version_file) as f:
            current_version = f.read().strip()

    python_version = args.python_version or current_version
    if not python_version:
        print(
            "Error: No Python version specified and .python-version not found.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Switching to Python {python_version}")

    need_switch = current_version != python_version if current_version else True
    if need_switch:
        print(
            "\n[VS Code WARNING] If you are using Visual Studio Code:\n"
            "  - Please update the default Python interpreter (Ctrl+Shift+P → 'Python: Select Interpreter') to match the new version.\n"
            "  - Also open a new terminal after switching Python versions.\n"
        )

        subprocess.run(["pyenv", "local", python_version], check=True)

        venv_path = Path(".venv")
        if venv_path.exists():
            print("Removing existing virtual environment...")
            shutil.rmtree(venv_path)

        python_path = get_python_path(python_version)
        subprocess.run(["uv", "venv", f"--python={python_path}"], check=True)

        print("Installing dependencies...")
        subprocess.run(["uv", "pip", "install", "-e", ".[dev]"], check=True)
    else:
        print(f"Already using Python {python_version}")
        subprocess.run(["uv", "sync", "--extra", "dev"], check=True)

    print(f"Successfully switched to Python {python_version}")
    print("To activate this environment manually, run:")
    print("  source .venv/bin/activate  # On macOS/Linux")
    print("  .venv\\Scripts\\activate    # On Windows")


if __name__ == "__main__":
    main()
