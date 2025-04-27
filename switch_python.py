#!/usr/bin/env python3
"""
Script to switch Python versions for pysmi development.
Equivalent to Switch-Python.ps1
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
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Switch Python version for pysmi development."
    )
    parser.add_argument(
        "python_version", help="Python version to switch to (e.g., 3.12)"
    )

    args = parser.parse_args()

    python_version = args.python_version
    print(f"Switching to Python {python_version}")

    # Set local Python version using pyenv
    subprocess.run(["pyenv", "local", python_version], check=True)
    # VS Code users: warn about terminal and interpreter
    print(
        "\n[VS Code WARNING] If you are using Visual Studio Code:\n"
        "  - Please update the default Python interpreter (Ctrl+Shift+P → 'Python: Select Interpreter') to match the new version.\n"
        "  - Also open a new terminal after switching Python versions.\n"
    )

    # Remove existing venv if it exists
    venv_path = Path(".venv")
    if venv_path.exists():
        print("Removing existing virtual environment...")
        shutil.rmtree(venv_path)

    # Create new venv with specified Python version
    python_path = get_python_path(python_version)
    subprocess.run(["uv", "venv", f"--python={python_path}"], check=True)

    # Install dependencies
    # Note: In Python, we don't need to explicitly activate the venv first
    print("Installing dependencies...")
    subprocess.run(["uv", "pip", "install", "-e", ".[dev]"], check=True)

    print(f"Successfully switched to Python {python_version}")
    print("To activate this environment manually, run:")
    print("  source .venv/bin/activate  # On macOS/Linux")
    print("  .venv\\Scripts\\activate    # On Windows")


if __name__ == "__main__":
    main()
