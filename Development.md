# Commands for Development

## Change Poetry Venv Python Version

```bash
pyenv local 3.12
poetry env use 3.12
poetry env info --path
```

## Bump Version Number

```bash
poetry version patch
```

## Build Documentation

```bash
poetry run make html -C docs
```
