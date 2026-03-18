# PyScrAI Runtime Skill

## Overview
This skill provides procedures for running scenarios and managing simulations in PyScrAI. It handles scenario execution, event logging, state management, and run reports.

## Prerequisites
- PyScrAI core package installed (`pyscrai`)
- Agent Zero bridge module available (`pyscrai.agents.agent_zero_bridge`)
- Access to project artifacts directory

## Procedures

### 1. Run Scenario
**Objective**: Execute a scenario with a given turn limit.

**Steps**:
1. Use `AgentZeroBridge` to run a scenario.
2. The bridge will delegate to the `pyscrai-runtime` subordinate.
3. Return the simulation run ID.

**Example**:
```python
from pyscrai.agents.agent_zero_bridge import AgentZeroBridge

bridge = AgentZeroBridge()
result = bridge.run_scenario(scenario_id="scenario-123", turn_limit=6)
print(f"Simulation run: {result['run_id']}")
```

### 2. Get Run Status
**Objective**: Get the status of a simulation run.

**Steps**:
1. Use `AgentZeroBridge` to get run status.
2. The bridge will delegate to the `pyscrai-runtime` subordinate.
3. Return the run status.

**Example**:
```python
result = bridge.get_run_status(run_id="run-123")
print(f"Run status: {result['status']}")
```

### 3. Get Run Report
**Objective**: Get a detailed report of a simulation run.

**Steps**:
1. Use `AgentZeroBridge` to get a run report.
2. The bridge will delegate to the `pyscrai-runtime` subordinate.
3. Return the run report.

**Example**:
```python
result = bridge.get_run_report(run_id="run-123")
print(f"Run report: {result['report']}")
```

### 4. List Runs for Scenario
**Objective**: List all runs for a given scenario.

**Steps**:
1. Use `AgentZeroBridge` to list runs for a scenario.
2. The bridge will delegate to the `pyscrai-runtime` subordinate.
3. Return the list of runs.

**Example**:
```python
result = bridge.list_runs(scenario_id="scenario-123")
print(f"Runs: {result['runs']}")
```

## Scripts

### `scripts/run_scenario.py`
A command-line script for running a scenario.

**Usage**:
```bash
python /path/to/skill/scripts/run_scenario.py --scenario-id scenario-123 --turn-limit 6
```

### `scripts/list_runs.py`
Lists all runs for a scenario.

**Usage**:
```bash
python /path/to/skill/scripts/list_runs.py --scenario-id scenario-123
```

## Integration Points
- **Agent Zero Bridge**: All procedures go through the bridge module.
- **ArtifactRepository**: The bridge uses the repository for persistence.
- **Runtime Subordinate**: Handles scenario execution and run management.
- **ScenarioRuntimeEngine**: The underlying engine that runs the scenario.

## Error Handling
- If the bridge is unavailable, fall back to direct CLI calls.
- If a subordinate is not responding, check Agent Zero logs.
- Validate scenario IDs and run IDs before operations.

## Notes
- This skill is designed to be used by Agent Zero agents and subordinates.
- Always use the bridge module for consistency and to preserve contracts.
- The bridge abstracts the underlying A2A protocol and subordinate delegation.
