#!/usr/bin/env python3
"""
Script to build documentation for the project.
Uses sphinx-polyversion to generate multi-version docs.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main():
    """Run documentation build using sphinx-polyversion."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Build documentation for this project."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Run with verbose output"
    )
    args = parser.parse_args()

    print("Building documentation with sphinx-polyversion...", file=sys.stderr)

    # Check if virtual environment is active
    if not Path(".venv").exists():
        print("No virtual environment found. Creating one...", file=sys.stderr)
        subprocess.run(["uv", "venv"], check=True)

        print("Installing dependencies...", file=sys.stderr)
        subprocess.run(["uv", "pip", "install", "-e", ".[dev]"], check=True)

    # Make sure uv and sphinx-polyversion are installed in the venv
    try:
        subprocess.run(["uv", "pip", "install", "uv"], check=True)
        subprocess.run(["uv", "pip", "install", "sphinx-polyversion"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}", file=sys.stderr)
        sys.exit(1)

    # Build the command
    command = ["uv", "run", "sphinx-polyversion", "docs/poly.py"]

    if args.verbose:
        command.append("--verbose")

    # Display the command being run
    print(f"Executing: {' '.join(command)}", file=sys.stderr)

    # Run the command
    try:
        subprocess.run(command, check=True)
        print("Documentation built successfully!", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error building documentation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
