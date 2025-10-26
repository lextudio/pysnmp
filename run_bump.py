#!/usr/bin/env python3
"""
Script to bump version numbers for pysmi.
Uses bump2version to increment version.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def main():
    """Main function to run bump2version with different options."""
    parser = argparse.ArgumentParser(description="Bump version for the project.")

    # Version part to bump (mutually exclusive options). Optional; defaults to patch.
    part_group = parser.add_mutually_exclusive_group(required=False)
    part_group.add_argument("--major", action="store_true", help="Bump major version")
    part_group.add_argument("--minor", action="store_true", help="Bump minor version")
    part_group.add_argument(
        "--patch",
        action="store_true",
        help="Bump patch version (default if no flag supplied)",
    )

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

    # Derive current & prospective versions from .bumpversion.cfg (authoritative source)
    config_path = Path(".bumpversion.cfg")
    current_version = None
    next_version = None

    def read_current_version(path: Path):  # -> Optional[str] (Python<3.10 compat)
        """Read current_version from bumpversion config, return None if not found."""
        if not path.exists():
            return None
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("current_version"):
                # current_version = 7.1.21
                parts = line.split("=", 1)
                if len(parts) == 2:
                    return parts[1].strip()
        return None

    current_version = read_current_version(config_path)
    if current_version:
        segs = current_version.split(".")
        if len(segs) == 3 and all(s.isdigit() for s in segs):
            major, minor, patch = map(int, segs)
            if bump_part == "major":
                major += 1
                minor = 0
                patch = 0
            elif bump_part == "minor":
                minor += 1
                patch = 0
            else:  # patch
                patch += 1
            next_version = f"{major}.{minor}.{patch}"
    # Build the command
    cmd = ["uv", "run", "bump2version"]

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

    # Human-friendly pre-execution summary
    if current_version and next_version:
        print(
            f"Config (.bumpversion.cfg) version: {current_version} -> {next_version} (bump: {bump_part})"
        )
    elif current_version:
        print(
            f"Config (.bumpversion.cfg) current version: {current_version} (bump: {bump_part})"
        )
    else:
        print(
            f"Config (.bumpversion.cfg) not found or missing current_version; proceeding (bump: {bump_part})"
        )

    print(f"Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)

        # After bump: re-read config for updated version
        new_version = read_current_version(config_path)
        if new_version and current_version and new_version != current_version:
            print(f"Updated config version: {current_version} -> {new_version}")
        elif new_version:
            print(f"Post-bump config current_version: {new_version}")

        if result.stderr:
            print("Errors/Warnings:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
