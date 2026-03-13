# PyScrAI

PyScrAI is a WorldMatrix-first, human-in-the-loop world-authoring and scenario-instantiation platform.

This repository now contains a thin but runnable MVP vertical slice:

- core Pydantic contracts for MVP artifacts
- a file-backed project/setup/worldmatrix service
- a FastAPI app for setup and validation flow
- deterministic scenario runtime test loop with trace artifacts
- a Typer CLI for local bootstrap and run operations

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

## Quick MVP CLI path

```bash
uv run pyscrai bootstrap-project "Build a near-future Gulf crisis simulation in the Persian Gulf."
uv run pyscrai compile-worldmatrix <project_id>
uv run pyscrai create-branch <worldmatrix_id> "Baseline branch"
uv run pyscrai create-scenario <branch_id> --binding lead=admiral --state tension=high --stop-condition turn_limit=8
uv run pyscrai run-scenario dcaaf4b8-e3ee-4609-8b38-509f2c0eae01 --turn-limit 6
```
