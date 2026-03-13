# PyScrAI

PyScrAI is a WorldMatrix-first, human-in-the-loop world-authoring and scenario-instantiation platform.

This repository currently contains a thin Milestone 1 vertical slice:

- core Pydantic contracts for MVP artifacts
- a file-backed project/setup/worldmatrix service
- a FastAPI app for setup and validation flow
- a Typer CLI for local bootstrap operations

## Baseline setup

```bash
uv venv
source .venv/bin/activate
uv sync --extra dev
```

## Run the API

```bash
uv run pyscrai-api
```

## Run the CLI

```bash
uv run pyscrai --help
```
