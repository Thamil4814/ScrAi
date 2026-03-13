# AGENTS.md

## Purpose

This repository is being built with AI-assisted development from the beginning. This file defines how a ChatGPT Codex-style development assistant should operate inside this codebase.

At this stage, the only source documents in the repository are:

* `docs/devops/pyscrai_blueprint.md`
* `docs/devops/vision.md`

These two files are the entire current design context.

## Source of Truth

The assistant must treat the documents with the following priority:

1. `docs/devops/pyscrai_blueprint.md` is the current implementation source of truth.
2. `docs/devops/vision.md` defines product vision, architectural intent, and non-negotiable conceptual boundaries.

When there is ambiguity:

* Use `docs/devops/pyscrai_blueprint.md` for implementation decisions.
* Use `docs/devops/vision.md` to preserve design philosophy and product direction.
* If the two appear to conflict, the blueprint wins on concrete implementation detail.

The assistant should not invent a parallel architecture that conflicts with these files.

## Product Framing

PyScrAI is not primarily a scraper, not primarily a generic UI shell, and not primarily a simulator in isolation.

The system being built is a **human-in-the-loop, architect-guided world-authoring and scenario-instantiation platform** centered on the **WorldMatrix**.

The intended MVP path is:

* Project creation from high-level prompt
* Guided setup / interview
* Live WorldMatrix drafting
* Validation
* WorldMatrix compile
* WorldBranch / Scenario derivation
* Runtime instantiation
* Basic multi-agent test run

All implementation work should reinforce that path.

## Development Environment Baseline

The baseline development environment is:

* **Host:** Windows
* **Primary dev/runtime environment:** **WSL2 Ubuntu**
* **Package and environment manager:** **uv**
* **Primary language:** Python

The repository should be treated as **Linux-first**.

The assistant must:

* prefer Linux/WSL2-compatible commands,
* prefer POSIX paths and shell behavior,
* avoid Windows-native path assumptions,
* avoid PowerShell-specific workflows unless explicitly requested,
* assume local development and execution happen inside WSL2 Ubuntu.

## Python and Dependency Management

Use `uv` for environment and dependency management.

Preferred patterns:

* `uv venv`
* `uv sync`
* `uv add`
* `uv remove`
* `uv run`
* `uv pip install` only when necessary

The assistant should avoid introducing alternative environment managers unless explicitly requested.

If creating setup instructions, prefer a flow like:

```bash
uv venv
source .venv/bin/activate
uv sync
```

If there is not yet a lockfile or dependency set, the assistant may propose one, but it should keep the initial environment minimal and aligned with the MVP.

## GPU / CUDA / PyTorch Expectations

This repository is expected to run in WSL2 Ubuntu with working CUDA support already available or nearly available.

The assistant should operate under these assumptions:

* WSL2 GPU passthrough is intended to be available.
* CUDA-capable local inference may be used.
* PyTorch and other ML dependencies should be installed in a way compatible with the active CUDA stack.
* The assistant should not casually replace GPU-capable installs with CPU-only fallbacks unless explicitly requested.

When working with Torch or related dependencies, the assistant should:

* preserve GPU support where possible,
* avoid dependency suggestions that are known to break common WSL2 CUDA setups,
* prefer explicit, reproducible installation steps,
* keep heavyweight ML dependencies optional unless required for the current milestone.

If environment validation steps are needed, prefer checks such as:

```bash
uv run python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.device_count())"
```

and, where relevant:

```bash
nvidia-smi
```

The assistant should distinguish between:

* base application dependencies,
* optional local inference dependencies,
* optional GPU-accelerated extras.

## Current Repo State Assumption

At the moment, assume the repository is nearly empty except for the design documents under `docs/`.

Therefore, the assistant should optimize for:

* clean initial structure,
* minimal but correct scaffolding,
* strong contracts early,
* fast path to an end-to-end MVP,
* low-friction local setup inside WSL2.

Do not assume legacy folders, services, schemas, or code are present unless they have actually been created.

## Primary Build Priorities

The assistant should prioritize work in this order:

1. Establish repo scaffolding aligned with the blueprint.
2. Establish Python project structure and `uv`-based environment setup.
3. Define core domain contracts.
4. Stand up the API / CLI foundation.
5. Implement setup-session and WorldMatrix draft flow.
6. Implement validation and compile flow.
7. Implement Scenario / WorldBranch derivation.
8. Implement a minimal runtime instantiation and test loop.
9. Add supporting UI only after contracts and flows are stable enough.

The assistant should resist expanding into broad scraping, broad UI work, or speculative subsystems before the MVP path works end to end.

## Architectural Guardrails

The assistant must preserve the following architectural guardrails.

### 1. HIL-first

The operator is an active co-author from the beginning.
The setup flow must be interview-driven, not just post-hoc review of machine output.

### 2. WorldMatrix-first

The central artifact is the WorldMatrix.
Ingestion, extraction, validation, branching, and runtime preparation should all point toward structured WorldMatrix creation and use.

### 3. Agentic by default

Even if the MVP initially uses a single orchestrator implementation, the design should preserve separable agent roles such as interview, schema mapping, validation, ingestion, runtime translation, and tracing.

### 4. Structured uncertainty

The system should preserve provenance, confidence, unresolved gaps, and contested information instead of flattening all inputs into false canon.

### 5. Truth / belief / authority separation

The system must distinguish between:

* world truth,
* actor belief,
* polity or faction knowledge,
* operator visibility,
* operator permissions,
* simulation authority state.

These are not optional details. They are core design boundaries.

### 6. Linux-first implementation

Paths, scripts, startup instructions, and service assumptions should target WSL2 Ubuntu first.

## Expected Core Domain Objects

Unless the blueprint changes, the assistant should assume that the first-class MVP artifacts include:

* `Project`
* `SetupSession`
* `WorldMatrixDraft`
* `WorldMatrix`
* `WorldBranch`
* `Scenario`
* `SimulationRun`

The assistant should avoid inventing alternative central artifacts unless explicitly directed.

## Expected MVP Stack

Unless changed by the operator, prefer a lean stack consistent with the blueprint:

* Python 3.11 or 3.12
* FastAPI
* Pydantic v2
* Typer
* SQLite for early metadata/state
* JSON artifacts for WorldMatrix / Scenario / traces
* minimal web UI later

The assistant should keep optional components optional.

## How the Assistant Should Work

When asked to implement features, the assistant should:

1. map the request back to the blueprint and vision,
2. preserve the MVP path,
3. propose the smallest coherent implementation that advances the end-to-end system,
4. keep contracts explicit,
5. avoid unnecessary abstraction when the repo is still young,
6. produce code and structure that can scale into the later agentic architecture.

When making design choices, the assistant should favor:

* clarity over cleverness,
* explicit contracts over implicit conventions,
* composable services over monoliths,
* deterministic validation over vague heuristics,
* traceability over hidden magic.

## What the Assistant Should Avoid

The assistant should avoid:

* designing around a legacy repo that no longer exists,
* building a large scraping framework before the setup flow works,
* overcomplicating the first runtime,
* mixing runtime concerns too early into setup-session contracts,
* creating large speculative abstractions with no immediate MVP use,
* introducing Windows-specific assumptions into the main dev path,
* silently changing the product center away from guided WorldMatrix creation.

## Suggested Initial Repository Shape

Unless the operator requests otherwise, early scaffolding should trend toward:

```text
pyscrai/
  docs/
    AGENTS.md
    devops/
        pyscrai_blueprint.md
        vision.md
  apps/
    api/
    cli/
    web/
  packages/
    core/
      domain/
      application/
      contracts/
      services/
    agents/
      interview/
      schema/
      validation/
      ingestion/
      runtime/
      tracing/
    adapters/
      llm/
      storage/
      scraping/
      databases/
    runtime/
      scenario/
      state/
      turn_loop/
      actions/
      evaluators/
  artifacts/
  tests/
```

This structure may be adapted, but only if the core blueprint intent remains intact.

## Environment Setup Guidance for the Assistant

When bootstrapping the repo, the assistant should prefer a simple, reproducible setup path.

A typical baseline should look like:

```bash
uv venv
source .venv/bin/activate
uv sync
```

If dependencies are not yet defined, the assistant may scaffold them incrementally.

For CUDA-sensitive local ML dependencies, the assistant should separate them from the base app environment when possible, for example through optional dependency groups or clear install steps.

## Definition of Success

The assistant should optimize toward the earliest realistic end-to-end MVP where a user can:

1. create a project from a high-level description,
2. go through a guided setup interview,
3. inspect a live WorldMatrix draft,
4. validate and compile the WorldMatrix,
5. derive a Scenario or WorldBranch,
6. instantiate it into a simple multi-agent runtime,
7. execute a basic test run with traceable outputs.

That path matters more than any isolated subsystem.

## Operating Rule

If the assistant is uncertain what to build next, it should ask:

**Does this directly strengthen the path from project creation to runnable scenario instantiation described in `docs/devops/pyscrai_blueprint.md`?**

If not, it is probably not the right priority yet.
