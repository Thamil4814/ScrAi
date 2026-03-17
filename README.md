# PyScrAI

PyScrAI is a WorldMatrix-first, human-in-the-loop world-authoring and scenario-instantiation platform.

This repository now contains a thin but runnable MVP vertical slice:

- core Pydantic contracts for MVP artifacts
- a file-backed project/setup/worldmatrix service
- a FastAPI app for setup and validation flow
- deterministic scenario runtime test loop with trace artifacts
- a Typer CLI for local bootstrap and run operations

Primary development docs live in `docs/devops/`:

- `pyscrai_dev_blueprint.md` is the primary development document and implementation plan.
- `pyscrai_dev_architecture.md` defines the target architectural boundaries, layers, and system model.
- `changelog.md` tracks concise dated change notes.

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

## Run PyScrAI Forge (Streamlit Shell)

```bash
uv run pyscrai-forge
```

## Run the CLI

```bash
uv run pyscrai --help
```

## Developer checks

Use these commands for the most common linting and type-check workflows:

```bash
uv run ruff check .        # Run lint checks across the workspace
uv run ruff format .       # Apply Ruff formatting to the workspace
uv run mypy packages/core  # Run static type checking on the core package
uv run pyright             # Run Pyright type analysis using project config/defaults
```

## Quick MVP CLI path

```bash
uv run pyscrai bootstrap-project "Build a near-future Gulf crisis simulation in the Persian Gulf."
uv run pyscrai compile-worldmatrix <project_id>
uv run pyscrai create-branch <worldmatrix_id> "Baseline branch"
uv run pyscrai create-scenario <branch_id> --binding lead=admiral --state tension=high --stop-condition turn_limit=8
uv run pyscrai run-scenario <scenario_id> --turn-limit 6
```