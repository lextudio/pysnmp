#!/usr/bin/env python3
"""
Script to build Python packages for pysmi.
Equivalent to Build-Packages.ps1
"""

import os
import shutil
import subprocess


def main():
    """Main function to build packages."""
    # Check if the dist directory exists and remove it
    if os.path.isdir("dist"):
        print("Removing existing dist directory...")
        shutil.rmtree("dist")
    else:
        print("dist directory not found. Skipping removal.")

    # Build the packages
    print("Building packages...")
    subprocess.run(["uv", "build"], check=True)

    print("Build process completed.")


if __name__ == "__main__":
    main()
