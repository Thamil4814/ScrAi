# Agent Zero Integration Plan for PyScrAI

## Overview
Replace OpenAI Agents SDK with Agent Zero as the Layer B (Agent Substrate) in PyScrAI's architecture.

## Architecture Change

### Before:
- Layer B: OpenAI Agents SDK (standalone, provider-locked)

### After:
- Layer B: Agent Zero (provider-agnostic, hierarchical agents, built-in memory, tools, scheduler)

## Implementation Phases

### Phase 1: Foundation (Current)
1. **Update Architecture Documentation**
   - Update `pyscrai_dev_architecture.md` to reflect Agent Zero
   - Update `pyscrai_dev_blueprint.md` with new integration decisions
   - Update `AGENTS.md` with Agent Zero patterns

2. **Create Agent Zero Skill: `pyscrai-forge`**
   - Core skill wrapping PyScrAI functionality
   - Commands for bootstrap, compile, branch, scenario, run

3. **Create Agent Zero Integration Module**
   - New `pyscrai/agents/agent_zero_bridge.py`
   - A2A protocol adapter
   - Subordinate agent definitions

### Phase 2: Agent Subordinates
1. **Architect Agent Subordinate**
   - Profile: `pyscrai-architect`
   - Purpose: Goal intake, interview flow, module recommendations
   - Uses: `setup_mapper.py`, `architect_manifest.py`

2. **World Authoring Agent Subordinate**
   - Profile: `pyscrai-author`
   - Purpose: Entity creation, relationship mapping, rule definition
   - Uses: WorldMatrix contracts, validation engine

3. **Runtime Agent Subordinate**
   - Profile: `pyscrai-runtime`
   - Purpose: Scenario execution, event logging, state management
   - Uses: `ScenarioRuntimeEngine`

4. **Ingestion Agent Subordinate**
   - Profile: `pyscrai-ingest`
   - Purpose: Document processing, entity extraction, knowledge graph building
   - Uses: Local-first pipeline

### Phase 3: Skills Registry
1. **Map PyScrAI Modules → Agent Zero Skills**
   - `world_authoring` → SKILL.md with world creation procedures
   - `scenario_runtime` → SKILL.md with runtime execution procedures
   - `ingestion` → SKILL.md with document processing procedures
   - `memory_retrieval` → Leverage Agent Zero's built-in memory

### Phase 4: Streamlit Integration
1. **Update Forge Shell**
   - Add Agent Zero connection status
   - Add subordinate management UI
   - Add skill invocation interface
   - Add memory browser

## Technical Details

### Agent Zero Communication
- **A2A Protocol**: For external communication from Streamlit
- **Subordinate System**: For internal agent orchestration
- **Skills**: For PyScrAI module functionality
- **Memory**: For long-term project state

### Key Files to Create/Modify

#### New Files:
- `packages/core/pyscrai/agents/__init__.py`
- `packages/core/pyscrai/agents/agent_zero_bridge.py`
- `packages/core/pyscrai/agents/subordinates.py`
- `skills/pyscrai-forge/SKILL.md`
- `skills/pyscrai-world-authoring/SKILL.md`
- `skills/pyscrai-runtime/SKILL.md`

#### Files to Update:
- `docs/devops/pyscrai_dev_architecture.md`
- `docs/devops/pyscrai_dev_blueprint.md`
- `AGENTS.md`
- `README.md`
- `packages/core/pyscrai/interfaces/forge_app.py`
- `pyproject.toml` (add httpx, a2a dependencies)

### Subordinate Profiles to Create

```json
{
  "pyscrai-architect": {
    "title": "PyScrAI Architect",
    "description": "Agent specialized in PyScrAI project setup, goal intake, and manifest creation.",
    "context": "You are the PyScrAI architect agent. Guide users through project creation, interview them about their goals, recommend modules, and create the project manifest."
  },
  "pyscrai-author": {
    "title": "PyScrAI World Author",
    "description": "Agent specialized in world and scenario creation within PyScrAI.",
    "context": "You are the PyScrAI world authoring agent. Create entities, define relationships, set up rules and knowledge boundaries, and build WorldMatrix artifacts."
  },
  "pyscrai-runtime": {
    "title": "PyScrAI Runtime",
    "description": "Agent specialized in scenario execution and simulation management.",
    "context": "You are the PyScrAI runtime agent. Execute scenarios, manage simulation state, log events, and generate run reports using the ScenarioRuntimeEngine."
  },
  "pyscrai-ingest": {
    "title": "PyScrAI Ingestion",
    "description": "Agent specialized in document ingestion and knowledge extraction.",
    "context": "You are the PyScrAI ingestion agent. Process documents, extract entities and relations, build knowledge graphs using a local-first pipeline."
  }
}
```

## Success Criteria

1. ✅ Agent Zero replaces OpenAI Agents SDK as Layer B
2. ✅ PyScrAI functionality accessible via Agent Zero skills
3. ✅ Architect interview flow works via subordinate agent
4. ✅ World authoring works via subordinate agent
5. ✅ Scenario runtime works via subordinate agent
6. ✅ Memory system uses Agent Zero's vector-backed memory
7. ✅ Streamlit Forge can communicate with Agent Zero
8. ✅ Local-first ingestion pipeline integrated
9. ✅ Task scheduler used for automated scenarios
10. ✅ All existing PyScrAI contracts and domain models preserved

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Tight coupling to Agent Zero | Use adapter pattern with clean interfaces |
| Agent Zero API changes | Pin version, abstract behind bridge module |
| Performance overhead | Use direct Python calls for internal operations, A2A for external |
| Complexity increase | Comprehensive documentation and skill guides |

