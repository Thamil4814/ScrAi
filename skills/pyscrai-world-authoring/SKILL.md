# PyScrAI World Authoring Skill

## Overview
This skill provides procedures for creating and managing worlds and scenarios in PyScrAI. It handles entity creation, relationship mapping, rule definition, and WorldMatrix compilation.

## Prerequisites
- PyScrAI core package installed (`pyscrai`)
- Agent Zero bridge module available (`pyscrai.agents.agent_zero_bridge`)
- Access to project artifacts directory

## Procedures

### 1. Compile WorldMatrix
**Objective**: Compile a WorldMatrix from a draft.

**Steps**:
1. Use `AgentZeroBridge` to compile the world matrix for a given project.
2. The bridge will delegate to the `pyscrai-author` subordinate.
3. Return the compiled WorldMatrix ID.

**Example**:
```python
from pyscrai.agents.agent_zero_bridge import AgentZeroBridge

bridge = AgentZeroBridge()
result = bridge.compile_worldmatrix(project_id="project-123")
print(f"WorldMatrix compiled: {result['worldmatrix_id']}")
```

### 2. Create World Branch
**Objective**: Create a new branch from a WorldMatrix.

**Steps**:
1. Use `AgentZeroBridge` to create a branch.
2. The bridge will delegate to the `pyscrai-author` subordinate.
3. Return the branch ID.

**Example**:
```python
result = bridge.create_branch(worldmatrix_id="wm-123", name="Baseline branch")
print(f"Branch created: {result['branch_id']}")
```

### 3. Add Entity to World
**Objective**: Add an entity to a WorldMatrix.

**Steps**:
1. Use `AgentZeroBridge` to add an entity.
2. The bridge will delegate to the `pyscrai-author` subordinate.
3. Return the entity ID.

**Example**:
```python
result = bridge.add_entity(
    worldmatrix_id="wm-123",
    entity_type="person",
    name="Admiral Johnson",
    attributes={"role": "commander", "rank": "admiral"}
)
print(f"Entity added: {result['entity_id']}")
```

### 4. Define Relationship
**Objective**: Define a relationship between two entities.

**Steps**:
1. Use `AgentZeroBridge` to define a relationship.
2. The bridge will delegate to the `pyscrai-author` subordinate.
3. Return the relationship ID.

**Example**:
```python
result = bridge.define_relationship(
    worldmatrix_id="wm-123",
    source_entity_id="entity-123",
    target_entity_id="entity-456",
    relationship_type="commands",
    attributes={"since": "2024"}
)
print(f"Relationship defined: {result['relationship_id']}")
```

### 5. Create Scenario
**Objective**: Create a scenario within a branch.

**Steps**:
1. Use `AgentZeroBridge` to create a scenario.
2. The bridge will delegate to the `pyscrai-author` subordinate.
3. Return the scenario ID.

**Example**:
```python
result = bridge.create_scenario(
    branch_id="branch-123",
    bindings=["lead=admiral"],
    initial_state=["tension=high"],
    stop_conditions=["turn_limit=8"]
)
print(f"Scenario created: {result['scenario_id']}")
```

## Scripts

### `scripts/create_entity.py`
A command-line script for creating an entity.

**Usage**:
```bash
python /path/to/skill/scripts/create_entity.py --worldmatrix-id wm-123 --type person --name "Admiral Johnson"
```

### `scripts/list_entities.py`
Lists all entities in a WorldMatrix.

**Usage**:
```bash
python /path/to/skill/scripts/list_entities.py --worldmatrix-id wm-123
```

### `scripts/validate_world.py`
Validates a WorldMatrix for completeness and correctness.

**Usage**:
```bash
python /path/to/skill/scripts/validate_world.py --worldmatrix-id wm-123
```

## Integration Points
- **Agent Zero Bridge**: All procedures go through the bridge module.
- **ArtifactRepository**: The bridge uses the repository for persistence.
- **Author Subordinate**: Handles entity creation, relationship mapping, and rule definition.

## Error Handling
- If the bridge is unavailable, fall back to direct CLI calls.
- If a subordinate is not responding, check Agent Zero logs.
- Validate WorldMatrix IDs and entity IDs before operations.

## Notes
- This skill is designed to be used by Agent Zero agents and subordinates.
- Always use the bridge module for consistency and to preserve contracts.
- The bridge abstracts the underlying A2A protocol and subordinate delegation.
