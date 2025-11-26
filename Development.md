# Commands for Development

## Environment Setup (uv-based)

We no longer use Poetry or pyenv for local development. The workflow relies on
`uv` for pinning Python versions, managing the virtual environment, syncing
dependencies, and installing standalone tools.

### 1. Pin desired Python version & (re)create venv

Use the helper script (preferred):

```bash
uv run python scripts/prepare.py 3.14    # or 3.10, 3.13, etc.
```

This will:

* `uv python pin 3.14` (updates `.python-version`)
* Reuse or recreate `.venv` targeting that version
* Install editable package + dev extras

Manual (alternative):

```bash
uv python pin 3.14
uv venv --python=3.14
uv pip install -e .[dev]
```

### 2. Install pre-commit (global tool) & set up hooks

We install `pre-commit` as a uv tool so it's always on PATH without activating
the venv:

```bash
uv tool install pre-commit
pre-commit install --overwrite
```

Run checks manually:

```bash
pre-commit run --all-files
```

If you prefer the venv-scoped binary:

```bash
uv run pre-commit install --overwrite
```

### 3. Updating Python version later

```bash
uv run python scripts/prepare.py 3.10    # switches pin & reconciles venv
```

## Version Bumping

Use `scripts/bump.py` (bump2version under uv) with patch default:

```bash
uv run python scripts/bump.py          # patch bump
uv run python scripts/bump.py --minor  # minor bump
uv run python scripts/bump.py --major  # major bump
```

It will show current -> next version (sourced from `.bumpversion.cfg`). After
that:

1. Edit `CHANGES.rst`.
2. Edit `docs/poly.py` if the new version tag needs to be added.
3. Modify nginx rule to route traffic to the latest version.
4. Update `ROADMAP.md` as needed.

## Documentation Build

## Build Documentation

Build current version documentation to find and fix issues:

```bash
uv run make -C docs html
```

Build multiple versions documentation for deployment:

```bash
uv run sphinx-polyversion docs/poly.py
```

## Check Port number

```bash
netstat -anp udp | grep 1611
```

## Test & Coverage

Run tests:

```bash
uv run pytest
```

With coverage:

```bash
uv run pytest --cov=pysnmp --cov-report=xml:coverage.xml
```

## Misc
