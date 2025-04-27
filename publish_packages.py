#!/usr/bin/env python3
"""
Script to publish Python packages for pysmi.
Equivalent to Publish-Packages.ps1
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def main():
    """Main function to publish packages."""
    # Define the path to the .pypirc file
    pypirc_path = Path.home() / ".pypirc"

    # Initialize credential variables
    pypi_username = None
    pypi_password = None

    # Check if the .pypirc file exists
    if not pypirc_path.is_file():
        print(f"Error: ~/.pypirc file not found at '{pypirc_path}'.", file=sys.stderr)
        sys.exit(1)

    print(f"Reading credentials from {pypirc_path}...")

    # Read the file content and parse for [pypi] credentials
    try:
        pypirc_content = pypirc_path.read_text()
        # Simple parsing assuming [pypi] section and username/password lines
        if "[pypi]" in pypirc_content:
            # Parse username
            username_match = re.search(r"(?m)^\s*username\s*=\s*(.+)$", pypirc_content)
            if username_match:
                pypi_username = username_match.group(1).strip()

            # Parse password
            password_match = re.search(r"(?m)^\s*password\s*=\s*(.+)$", pypirc_content)
            if password_match:
                pypi_password = password_match.group(1).strip()
    except Exception as e:
        print(f"Error reading or parsing '{pypirc_path}': {str(e)}", file=sys.stderr)
        sys.exit(1)

    # Validate that credentials were found
    if not pypi_username or not pypi_password:
        print(
            f"Error: Could not find username and/or password under the [pypi] section in '{pypirc_path}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"Credentials found. Username: {pypi_username}"
    )  # Username is usually __token__

    # Construct and execute the uv publish command
    print("Attempting to publish packages using credentials from ~/.pypirc...")
    try:
        subprocess.run(
            ["uv", "publish", "--username", pypi_username, "--password", pypi_password],
            check=True,
        )
        print("Publish command executed.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing uv publish: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
