# Repository Notes

- Use `uv run` for Python commands in this repository.
- Prefer the standard repo scripts in [`scripts/`](/Users/lextm/pysnmp.com/pysnmp/scripts) over ad hoc Python commands when they cover the task.
- Use [`scripts/prepare.py`](/Users/lextm/pysnmp.com/pysnmp/scripts/prepare.py) to pin or switch Python versions and to prepare the virtual environment.
- Use [`scripts/tests.py`](/Users/lextm/pysnmp.com/pysnmp/scripts/tests.py) to run tests instead of invoking other Python test commands directly.

## Preparing a New Version

1. `uv run scripts/tests.py`
2. `uv run scripts/bump.py` (patch by default; `--minor`/`--major`), then add the release notes to `CHANGES.rst`. For a minor or major bump, do this on a new `release-X.Y` branch (switch to it if it already exists).
3. `uv run scripts/build.py`

## Publishing a New Version

1. Commit the changes (including `uv.lock`).
2. `git tag vX.Y.Z` and push the branch and tag to the `public` remote.
3. `uv run scripts/publish.py` (try `--dry-run` first).
4. `uv run move-tag.py X.Y` to move the `vX.Y` tag.
5. Fast-forward `main` and then `docs` to `release-X.Y` and push both to `public`.

Confirm with the maintainer before pushing tags or publishing.
