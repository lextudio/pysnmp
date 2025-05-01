#!/usr/bin/env python3
"""
Script to bump version numbers for pysmi.
Uses bump2version to increment version.
"""

import argparse
import subprocess
import sys


def main():
    """Main function to run bump2version with different options."""
    parser = argparse.ArgumentParser(description="Bump version for the project.")

    # Version part to bump (mutually exclusive options)
    part_group = parser.add_mutually_exclusive_group(required=True)
    part_group.add_argument("--major", action="store_true", help="Bump major version")
    part_group.add_argument("--minor", action="store_true", help="Bump minor version")
    part_group.add_argument("--patch", action="store_true", help="Bump patch version")

    # Optional flags
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't actually change any files"
    )
    parser.add_argument(
        "--tag", action="store_true", help="Create a git tag for the new version"
    )
    parser.add_argument(
        "--tag-message", metavar="MSG", help="Tag message (default: version number)"
    )

    args = parser.parse_args()

    # Determine which part to bump
    bump_part = "patch"  # Default
    if args.major:
        bump_part = "major"
    elif args.minor:
        bump_part = "minor"

    # Build the command
    cmd = ["bump2version"]

    # Add appropriate flags
    cmd.append("--allow-dirty")

    if args.dry_run:
        cmd.append("--dry-run")

    if args.tag:
        cmd.append("--tag")

    if args.tag_message:
        cmd.extend(["--tag-message", args.tag_message])

    # Add the part to bump
    cmd.append(bump_part)

    # Execute the bump2version command
    print(f"Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)

        if result.stderr:
            print("Errors/Warnings:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
