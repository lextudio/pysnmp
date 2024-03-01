# Commands for Development

## Initialize Poetry

```bash
poetry init
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

```bash
poetry lock
poetry version patch
```

## Build Documentation

```bash
poetry run make html -C docs
```

## Check Port number

```bash
netstat -anp udp | grep 1611
```
