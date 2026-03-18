
## [2026-03-17] - Agent Zero Integration (Phase 1: Foundation)

### Changed
- **BREAKING**: Replaced OpenAI Agents SDK with Agent Zero as Layer B (Agent Substrate)
- Updated `pyscrai_dev_blueprint.md` with new agent substrate decision
- Renamed packages/core/pyscrai/agents to packages/core/pyscrai/a0 
- Moved /skills into packages/core/pyscrai/a0 

### Added
- New `packages/core/pyscrai/agents/` module with Agent Zero bridge
- `agent_zero_bridge.py` - Clean A2A protocol adapter for Agent Zero communication
- Comprehensive `AGENTS.md` documentation for Agent Zero integration patterns
- Subordinate profile definitions for PyScrAI workflows:
  - `pyscrai-architect`: Project setup, goal intake, manifest creation
  - `pyscrai-author`: Entity creation, relationship mapping, rule definition
  - `pyscrai-runtime`: Scenario execution, event logging, state management
  - `pyscrai-ingest`: Document processing, entity extraction, knowledge graph building

### Technical Details
- **A2A Protocol**: HTTP-based communication with Agent Zero
- **Subordinate System**: Internal agent delegation within Agent Zero hierarchy
- **Clean Adapter Pattern**: Bridge module abstracts Agent Zero details
- **No Breaking Changes**: All existing PyScrAI contracts and domain models preserved

### Migration Notes
- Existing PyScrAI functionality continues to work unchanged
- Agent Zero provides enhanced capabilities:
  - Hierarchical multi-agent orchestration
  - Built-in vector-backed memory
  - Rich tool ecosystem
  - Task scheduler for automated scenarios
  - Skills system maps to PyScrAI Module Registry

# Changelog

## 2026-03-17 I

- Added an architect manifest-drafting application boundary backed by an OpenAI Agents SDK adapter for OpenAI-compatible endpoints, with deterministic heuristic fallback.
- Added a static internal module registry for the current MVP modules and now derive registry-driven manifest sections such as enabled modules, memory, and runtime profile from it.
- Changed Forge goal intake to stop at a `ProjectManifestDraft`, added manifest update/approval endpoints, and gated setup-session launch on explicit manifest approval.
- Updated the Streamlit Forge shell to expose manifest review/edit plus approval-driven handoff into the existing WorldMatrix setup flow.
- Added deterministic manifest-drafting coverage and updated API tests for the new approval-first contract.

## 2026-03-16 III

- Formalized the Move 2 `ProjectManifestDraft` contract around the Forge blueprint sections: `metadata`, `enabled_modules`, `providers`, `routing_policy`, `storage`, `vectors`, `graph`, `mcp_servers`, `memory`, `runtime_profile`, and `policies`.
- Reworked manifest bootstrap defaults to reflect the current vertical slice and added explicit provider registry entries for OpenRouter and LM Studio.
- Added manifest draft access through the FastAPI and Typer interfaces and updated the Streamlit Forge shell to render the new manifest sections.
- Locked the manifest shape with API tests and validated the touched files with Ruff plus `pytest`.

## 2026-03-16 II

- Scaffolded PyScrAI Forge Streamlit app as the "Move 1" operator shell.
- Added `streamlit` dependency and `pyscrai-forge` CLI entrypoint.
- Implemented project selection, goal intake, active stack summary, and launchpad placeholders in `forge_app.py`.
- Validated with pyright, ruff, and successful Streamlit session on port 8501.

## 2026-03-16 I

- Deprecated `pyscrai_blueprint.md`, `vision.md`, and `current_status.md` by moving them to `.dep/`.
- Introduced `pyscrai_dev_blueprint.md` as the primary development document centering on PyScrAI Forge.
- Updated `AGENTS.md` and `README.md` to map to the new repository documentation state.

## 2026-03-14 I

- Added OpenAI Agents SDK and Redis-related dependencies to the workspace environment for future multi-agent work.
- Added development tooling dependencies: `ruff`, `mypy`, and `pyright`.
- Added [changelog.md](/home/dev/ScrAi/docs/devops/changelog.md) for concise workspace change tracking.
- Added [issues_comments.md](/home/dev/ScrAi/docs/devops/issues_comments.md) for dated notes, issues, and follow-up items.
- Added [current_status.md](/home/dev/ScrAi/docs/devops/current_status.md) as the living repo-to-blueprint status report.
- Rewrote [AGENTS.md](/home/dev/ScrAi/AGENTS.md) into a shorter, current-state repository instruction file.
