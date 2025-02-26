# Commands for Development

## Initialize Poetry

```bash
poetry init
poetry self add poetry-bumpversion
poetry add --group dev pre-commit=2.21.0
poetry run pre-commit install
```

## Change Poetry Venv Python Version

```bash
pyenv local 3.11
poetry env use 3.11
poetry env info --path
poetry env list
```

## Bump Version Number

1. Bump the version

   ```bash
   poetry lock
   poetry version patch
   ```

1. Edit `CHANGES.rst`

1. Edit `docs/poly.py` if the new version tag needs to be added to the list.

1. Modify nginx rule to route traffic to the latest version.

1. Update Roadmap in `ROADMAP.md`.

## Build Documentation

Build current version documentation to find and fix issues:

```bash
poetry run make html -C docs
```

Build multiple versions documentation for deployment:

```bash
poetry run sphinx-polyversion docs/poly.py
```

## Check Port number

```bash
netstat -anp udp | grep 1611
```

## Test Coverage

```bash
poetry run pytest --cov=pysnmp --cov-report=xml:coverage.xml
```
