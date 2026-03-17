# AGENTS.md
# Agent Zero Integration Documentation

## Overview

PyScrAI has integrated **Agent Zero** as the **Layer B (Agent Substrate)**, replacing the OpenAI Agents SDK.

### Key Changes
- **Agent Zero** provides hierarchical multi-agent orchestration
- **A2A protocol** for external communication
- **Subordinate system** for internal agent delegation
- **Skills** for PyScrAI module functionality
- **Memory** for long-term project state
- **Task scheduler** for automated scenarios

## Architecture Integration

### Agent Zero in PyScrAI's Layered Architecture

```
┌─────────────────────────────────────────────┐
│        Layer A: Forge Shell (Streamlit)      │
├─────────────────────────────────────────────┤
│        Layer B: Agent Zero (Substrate)       │ ← NEW
├─────────────────────────────────────────────┤
│        Layer C: Provider Bus (LiteLLM)       │
├─────────────────────────────────────────────┤
│        Layer D: Module Registry              │
├─────────────────────────────────────────────┤
│        Layer E: Project Artifacts            │
├─────────────────────────────────────────────┤
│        Layer F: Operational Surfaces         │
└─────────────────────────────────────────────┘
```

## Agent Zero Bridge Module

### Location
`packages/core/pyscrai/agents/agent_zero_bridge.py`

### Key Components

#### 1. AgentZeroBridge Class
Main bridge class providing typed interfaces for PyScrAI workflows.

```python
from pyscrai.agents.agent_zero_bridge import AgentZeroBridge, create_bridge

# Create bridge instance
bridge = create_bridge()

# Run architect interview
result = await bridge.run_architect_interview(
    goal="Build a Gulf crisis simulation",
    session=current_session
)
```

#### 2. A2AClient
Handles A2A protocol communication with Agent Zero.

```python
from pyscrai.agents.agent_zero_bridge import A2AClient, AgentZeroConfig

config = AgentZeroConfig(
    base_url="http://localhost:5000",
    timeout=30
)

client = A2AClient(config)
response = await client.send(
    agent_url="http://agent-zero:5000/a2a",
    message="Process this document...",
    attachments=["file:///path/to/document.pdf"]
)
```

#### 3. Subordinate Profiles

PyScrAI defines four subordinate profiles:

| Profile | Purpose | Key Tools |
|---------|---------|------------|
| `pyscrai-architect` | Project setup, goal intake, manifest creation | setup_mapper.py, architect_manifest.py |
| `pyscrai-author` | Entity creation, relationship mapping | WorldMatrix contracts, validation engine |
| `pyscrai-runtime` | Scenario execution, state management | ScenarioRuntimeEngine |
| `pyscrai-ingest` | Document processing, knowledge extraction | Local-first pipeline |

### Usage Patterns

#### 1. Direct Bridge Usage
```python
import asyncio
from pyscrai.agents.agent_zero_bridge import create_bridge

async def example_usage():
    bridge = create_bridge()

    # Architect interview
    architect_result = await bridge.run_architect_interview(
        goal="Create a historical simulation of Cold War",
        context={"period": "1947-1991", "focus": "diplomacy"}
    )

    if architect_result.success:
        # World authoring
        author_result = await bridge.run_world_authoring(
            instructions="Add key historical figures",
            context={"entities": ["Kennedy", "Khrushchev"]}
        )

    # Cleanup
    await bridge.close()
    return architect_result, author_result
```

#### 2. Integration with Existing PyScrAI Workflows

```python
# In forge_app.py or other Streamlit components
from pyscrai.agents.agent_zero_bridge import get_subordinate_profiles

# Get available profiles for UI display
profiles = get_subordinate_profiles()
for profile_name, profile_data in profiles.items():
    st.sidebar.write(f"**{profile_data['title']}**: {profile_data['description']}")
```

## Agent Zero Communication Patterns

### 1. A2A Protocol (External)
- Used for communication from Streamlit Forge to Agent Zero
- RESTful HTTP endpoints
- Supports file attachments
- Context preservation across messages

### 2. Subordinate System (Internal)
- Used for internal agent orchestration within Agent Zero
- Hierarchical delegation (superior → subordinate)
- Profile-based specialization
- Context passing between agents

### 3. Skills (Functionality)
- PyScrAI modules mapped to Agent Zero skills
- Each skill has SKILL.md with instructions
- Executable via code_execution_tool

## Integration Points

### 1. Streamlit Forge Integration
```python
# In forge_app.py
import streamlit as st
from pyscrai.agents.agent_zero_bridge import AgentZeroConfig

# Agent Zero connection status
if "agent_zero" not in st.session_state:
    st.session_state.agent_zero = {
        "connected": False,
        "config": AgentZeroConfig()
    }

# Check connection
if st.button("Connect to Agent Zero"):
    # Test connection logic
    st.session_state.agent_zero.connected = True
    st.success("Connected to Agent Zero")
```

### 2. Existing Module Integration
The bridge preserves all existing PyScrAI contracts:
- `Project`, `WorldMatrix`, `SetupSession` models remain unchanged
- `ScenarioRuntimeEngine` continues to work as before
- `ArtifactRepository` maintains file-backed persistence

## Subordinate Profile Definitions

### pyscrai-architect
```json
{
  "title": "PyScrAI Architect",
  "description": "Agent specialized in PyScrAI project setup, goal intake, and manifest creation.",
  "context": "You are the PyScrAI architect agent. Guide users through project creation, interview them about their goals, recommend modules, and create the project manifest. Use setup_mapper.py and architect_manifest.py tools."
}
```

### pyscrai-author
```json
{
  "title": "PyScrAI World Author",
  "description": "Agent specialized in world and scenario creation within PyScrAI.",
  "context": "You are the PyScrAI world authoring agent. Create entities, define relationships, set up rules and knowledge boundaries, and build WorldMatrix artifacts."
}
```

### pyscrai-runtime
```json
{
  "title": "PyScrAI Runtime",
  "description": "Agent specialized in scenario execution and simulation management.",
  "context": "You are the PyScrAI runtime agent. Execute scenarios, manage simulation state, log events, and generate run reports using the ScenarioRuntimeEngine."
}
```

### pyscrai-ingest
```json
{
  "title": "PyScrAI Ingestion",
  "description": "Agent specialized in document ingestion and knowledge extraction.",
  "context": "You are the PyScrAI ingestion agent. Process documents, extract entities and relations, build knowledge graphs using a local-first pipeline."
}
```

## Configuration

### Environment Variables
```bash
# .env or .env.example
AGENT_ZERO_URL=http://localhost:5000
AGENT_ZERO_TIMEOUT=30
```

### AgentZeroConfig
```python
from pyscrai.agents.agent_zero_bridge import AgentZeroConfig

config = AgentZeroConfig(
    base_url="http://localhost:5000",
    a2a_endpoint="/a2a",
    timeout=30
)
```

## Error Handling

The bridge provides structured error handling:

```python
result = await bridge.run_architect_interview(goal="...")

if result.success:
    print(f"Success: {result.content}")
else:
    print(f"Error: {result.error}")
    print(f"Profile: {result.profile}")
```

## Testing

### Unit Tests
```python
# tests/test_agent_zero_bridge.py
import pytest
from pyscrai.agents.agent_zero_bridge import AgentZeroBridge

@pytest.mark.asyncio
async def test_architect_interview():
    bridge = AgentZeroBridge()
    result = await bridge.run_architect_interview(
        goal="Test goal",
        context={"test": True}
    )
    assert result.success
    await bridge.close()
```

## Migration Guide

### From OpenAI Agents SDK to Agent Zero
1. **No breaking changes** - All existing PyScrAI functionality preserved
2. **Clean adapter pattern** - Bridge module abstracts Agent Zero details
3. **Gradual adoption** - Can use bridge incrementally
4. **Backward compatible** - Existing code continues to work

### Step-by-Step Migration
1. Import bridge module instead of OpenAI Agents
2. Use `create_bridge()` to instantiate
3. Call appropriate subordinate methods
4. Handle `SubordinateResult` objects

## Best Practices

1. **Use typed interfaces** - Leverage the bridge's typed methods
2. **Handle errors gracefully** - Check `result.success` before proceeding
3. **Clean up resources** - Call `await bridge.close()` when done
4. **Use context** - Pass relevant context for better agent performance
5. **Log interactions** - Monitor subordinate calls for debugging

## Future Enhancements

1. **WebSocket support** - Real-time communication with Agent Zero
2. **Streaming responses** - For long-running operations
3. **Batch processing** - Multiple subordinate calls in parallel
4. **Caching** - Cache frequent subordinate responses
5. **Metrics collection** - Track subordinate performance

## Troubleshooting

### Connection Issues
```python
# Test Agent Zero connectivity
import httpx

try:
    response = httpx.get("http://localhost:5000/health", timeout=5)
    print(f"Agent Zero status: {response.status_code}")
except Exception as e:
    print(f"Cannot connect to Agent Zero: {e}")
```

### Subordinate Not Responding
1. Check Agent Zero logs
2. Verify subordinate profile exists
3. Ensure A2A endpoint is correct
4. Check network connectivity

---

*This documentation is part of the PyScrAI Agent Zero integration. For more details, see the [Integration Plan](docs/devops/agent_zero_integration_plan.md).*
