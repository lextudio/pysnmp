#!/usr/bin/env python3
"""
Script to run tests for the project.
Equivalent to Run-Tests.ps1
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path


def main():
    """Main function to run tests."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run tests for this project.")
    parser.add_argument(
        "--coverage", action="store_true", help="Run with coverage report"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Run with verbose output"
    )
    parser.add_argument("--test-file", default="", help="Specific test file to run")
    parser.add_argument("--test-path", default="tests", help="Path to test directory")
    parser.add_argument("--args", default="", help="Additional pytest arguments")

    args = parser.parse_args()

    # Check if virtual environment is active
    if not Path(".venv").exists():
        print("No virtual environment found. Creating one...", file=sys.stderr)
        subprocess.run(["uv", "venv"], check=True)

        # Activate the virtual environment
        # Note: Python doesn't need to explicitly "activate" the venv like PowerShell does
        # We can use the Python from the venv directly

        print("Installing dependencies...", file=sys.stderr)
        subprocess.run(["uv", "pip", "install", "-e", ".[dev]"], check=True)

    print("Running tests for this project...", file=sys.stderr)

    # Build the command
    command = ["uv", "run", "python", "-m", "pytest"]

    if args.verbose:
        command.append("-v")

    if args.coverage:
        command.extend(["--cov=pysnmp", "--cov-report=term", "--cov-report=html"])

    if args.test_file:
        command.append(args.test_file)
    else:
        command.append(args.test_path)

    if args.args:
        command.extend(args.args.split())

    # Display the command being run
    print(f"Executing: {' '.join(command)}", file=sys.stderr)

    # Run the command
    subprocess.run(command, check=True)

    # Open coverage report if generated
    if args.coverage:
        print("\nCoverage report generated in htmlcov/index.html", file=sys.stderr)

        if platform.system() == "Windows":
            os.startfile("htmlcov\\index.html")
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", "htmlcov/index.html"], check=True)
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", "htmlcov/index.html"], check=True)


if __name__ == "__main__":
    main()
