# AGENTS.md

## Purpose

This file gives repository-level instructions to an AI coding agent working in PyScrAI.

Keep this file short, concrete, and current. Do not duplicate the full product spec here. The design source of truth lives in `docs/devops/`.

## Read First

Before making meaningful changes, read these documents in this order:

1. `docs/devops/pyscrai_blueprint.md`
2. `docs/devops/vision.md`
3. `docs/devops/current_status.md`

When they differ:

- `pyscrai_blueprint.md` wins on implementation detail, contracts, milestone order, and API shape.
- `vision.md` wins on product intent and conceptual boundaries.
- `current_status.md` is a snapshot of the current state. 

## Product Center

PyScrAI is a **human-in-the-loop, architect-guided world-authoring and scenario-instantiation platform** centered on the **WorldMatrix**.

Do not recenter the product around:

- generic scraping,
- generic UI shell work,
- isolated simulation work without the WorldMatrix authoring flow.

The MVP path to reinforce is:

`Project -> SetupSession -> WorldMatrixDraft -> Validation -> WorldMatrix -> WorldBranch/Scenario -> Runtime -> Test Run`

## Current Repo Reality

Do not assume the repo is empty. The current workspace already includes:

- a Python 3.12 package under `packages/core/pyscrai/`,
- FastAPI and Typer entrypoints,
- Pydantic contracts for core MVP artifacts,
- file-backed artifact persistence under `artifacts/projects/`,
- a thin runtime loop,
- tests under `tests/`.

Prefer extending the current vertical slice over inventing a parallel structure.

## Environment And Tooling

- Primary environment: WSL2 Ubuntu
- Package manager: `uv`
- Primary language: Python
- Main stack: FastAPI, Pydantic v2, Typer
- Linux-first paths and shell behavior only unless explicitly told otherwise

Prefer:

```bash
uv venv
source .venv/bin/activate
uv sync --extra dev
```

Common commands:

```bash
uv run pyscrai --help
uv run pyscrai-api
uv run pytest -q
uv run ruff check .
uv run ruff format .
uv run mypy packages/core
uv run pyright
```

## Architectural Guardrails

Preserve these boundaries unless the blueprint changes:

1. **HIL-first**: setup must be interview-driven, not review-after-generation.
2. **WorldMatrix-first**: ingestion, validation, branching, and runtime should all point toward WorldMatrix construction and use.
3. **Agentic by default**: preserve separable roles such as interview, schema mapping, validation, ingestion, runtime, and tracing even if the implementation is still simple.
4. **Structured uncertainty**: keep provenance, confidence, unresolved items, and contested information visible.
5. **Truth / belief / authority separation**: do not collapse world truth, actor belief, polity knowledge, operator visibility, operator permissions, and simulation authority into one layer.
6. **Linux-first implementation**: avoid Windows-native assumptions in commands, paths, and setup guidance.

## Preferred Build Priorities

When choosing what to build next, follow this order:

1. strengthen the end-to-end MVP path already in the repo,
2. improve core contracts and persistence,
3. improve setup-session and WorldMatrix drafting,
4. improve validation and compile flow,
5. improve scenario derivation and runtime behavior,
6. add supporting UI only after contracts and flows are stable.

Avoid broad speculative subsystems before they directly strengthen the MVP path.

## Working Rules

When implementing changes:

- map the request back to the blueprint before adding code,
- prefer the smallest coherent change that advances the MVP,
- keep contracts explicit,
- prefer deterministic behavior over hidden magic,
- preserve extensibility for later agent-role separation,


Avoid:

- building a large scraping framework before setup flow maturity,
- overcomplicating the first runtime,
- mixing runtime concerns too early into setup-session contracts,
- introducing a new architecture that conflicts with the blueprint,
- writing instructions that assume PowerShell or Windows-native execution.

## Documentation Hygiene

When work materially changes repo state or direction, update the relevant files in `docs/devops/`:

- `current_status.md` for repo-to-blueprint position,
- `changelog.md` for concise dated change notes,
- `issues_comments.md` for dated follow-ups, issues, or operator notes.

For `changelog.md` and `issues_comments.md`:

- use reverse chronological order,
- include the date on each entry,
- add a Roman numeral suffix when multiple entries share the same date.
