# PyScrAI Forge Skill

## Overview
This skill provides procedures for interacting with PyScrAI Forge, the operator-facing shell for the PyScrAI platform. It handles project creation, goal intake, architect interview flow, and module selection.

## Prerequisites
- PyScrAI core package installed (`pyscrai`)
- Agent Zero bridge module available (`pyscrai.agents.agent_zero_bridge`)
- Access to project artifacts directory

## Procedures

### 1. Bootstrap a New Project
**Objective**: Create a new PyScrAI project from a natural language goal.

**Steps**:
1. Use `AgentZeroBridge` to create a project with the given goal.
2. The bridge will delegate to the `pyscrai-architect` subordinate.
3. Return the project ID and initial manifest draft.

**Example**:
```python
from pyscrai.agents.agent_zero_bridge import AgentZeroBridge

bridge = AgentZeroBridge()
result = bridge.create_project(goal="Build a near-future Gulf crisis simulation in the Persian Gulf.")
print(f"Project created: {result['project_id']}")
```

### 2. Compile WorldMatrix
**Objective**: Compile a project's world matrix from the draft.

**Steps**:
1. Use `AgentZeroBridge` to compile the world matrix for a given project.
2. The bridge will delegate to the `pyscrai-author` subordinate.
3. Return the compiled WorldMatrix ID.

**Example**:
```python
result = bridge.compile_worldmatrix(project_id="project-123")
print(f"WorldMatrix compiled: {result['worldmatrix_id']}")
```

### 3. Create World Branch
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

### 4. Create Scenario
**Objective**: Create a scenario within a branch with specific bindings and stop conditions.

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

### 5. Run Scenario
**Objective**: Execute a scenario with a given turn limit.

**Steps**:
1. Use `AgentZeroBridge` to run a scenario.
2. The bridge will delegate to the `pyscrai-runtime` subordinate.
3. Return the simulation run ID.

**Example**:
```python
result = bridge.run_scenario(scenario_id="scenario-123", turn_limit=6)
print(f"Simulation run: {result['run_id']}")
```

## Scripts

### `scripts/bootstrap_project.py`
A command-line script for bootstrapping a project.

**Usage**:
```bash
python /path/to/skill/scripts/bootstrap_project.py "Your project goal here"
```

### `scripts/list_projects.py`
Lists all existing projects.

**Usage**:
```bash
python /path/to/skill/scripts/list_projects.py
```

## Integration Points
- **Agent Zero Bridge**: All procedures go through the bridge module.
- **ArtifactRepository**: The bridge uses the repository for persistence.
- **Architect Subordinate**: Handles the interview flow and manifest creation.

## Error Handling
- If the bridge is unavailable, fall back to direct CLI calls.
- If a subordinate is not responding, check Agent Zero logs.
- Validate project IDs and scenario IDs before operations.

## Notes
- This skill is designed to be used by Agent Zero agents and subordinates.
- Always use the bridge module for consistency and to preserve contracts.
- The bridge abstracts the underlying A2A protocol and subordinate delegation.
