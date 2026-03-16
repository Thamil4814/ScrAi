# PyScrAI  — WorldMatrix-First MVP Blueprint

## 1. Product Thesis

PyScrAI is a **world-construction and scenario-instantiation platform** for agentic simulation.

It is not primarily a scraper, not primarily a sandbox UI, and not primarily a simulator.

It is a system that:

1. guides an operator through a structured world-creation process,
2. ingests and synthesizes supporting source material,
3. compiles a validated **WorldMatrix**,
4. derives runnable **Scenarios** or **WorldBranches**,
5. instantiates those into a multi-agent runtime for testable execution.

The MVP must support the full path:

**Project Creation -> Guided Interview / Setup -> WorldMatrix Draft -> Validation -> WorldMatrix Compile -> Scenario/Branch Creation -> Runtime Instantiation -> Test Run**

---

## 2. Core Design Principles

### 2.1 HIL-first, not HIL-later

The operator is part of the authoring loop from the beginning.
Natural-language interview, confirmations, edits, and approvals are first-class system behavior.

### 2.2 WorldMatrix-first

The central artifact is the **WorldMatrix**, not raw ingested data and not an opaque runtime save.
Everything should point toward producing a structured world contract.

### 2.3 Agentic by default

The system should assume multiple cooperating AI roles from day one, even uses one orchestrator model with role prompts with early implementation.

### 2.4 Narrow MVP path

The first version must only implement the minimum path that produces a runnable simulation artifact.
Avoid broad ingestion, broad UI surface area, and broad ontology complexity.

### 2.5 WSL2 Ubuntu-first

The development and runtime baseline is **Ubuntu on WSL2**, not Windows-native.
All tooling, paths, scripts, startup instructions, and service assumptions should target Linux first.

### 2.6 Structured uncertainty

The system should preserve provenance, confidence, and unresolved gaps rather than flatten uncertainty into fake canon.

---

## 3. MVP Scope

### In scope

* Create a project from a high-level description
* Guided interview with operator
* Build a live WorldMatrix draft during interview
* Support manual input plus optional source ingestion
* Validate WorldMatrix completeness and consistency
* Compile a verified WorldMatrix artifact
* Create Scenario / WorldBranch from WorldMatrix
* Instantiate a simple agent runtime with entities/polities
* Run a basic simulation/test loop
* Inspect logs, decisions, and state transitions

### Out of scope for MVP

* Full autonomous web research swarm
* Rich GUI workbench with many pages
* Large-scale knowledge graph visualization
* Complex game-engine rendering
* Full long-horizon persistent simulation
* Heavy RL or large-scale distributed orchestration
* Deep multimodal ingestion pipelines beyond basic hooks

---

## 4. MVP User Journey

### Step 1 — Project Creation

Operator provides a high-level prompt such as:

* "Build a geopolitical crisis sim around Iran, Israel, the US, and proxy escalation"
* "Build a social simulation around three friends with hidden tensions"
* "Build a Middle-earth regional simulation in the late Third Age"

System creates:

* Project
* SetupSession
* Initial domain guess
* Initial ontology/template guess

### Step 2 — Guided Interview

Architect system asks progressive questions to determine:

* world type
* time scope
* environment / locations
* key entities / polities
* rules / constraints
* resources / values
* operator role and authority
* knowledge/visibility boundaries
* desired simulation style

### Step 3 — Live WorldMatrix Drafting

Each answer is translated into:

* structured fields
* human-readable summary
* unresolved questions
* provisional confidence / provenance labels

### Step 4 — Validation

System checks:

* required sections present
* internal consistency
* role/authority conflicts
* missing key entities or locations
* invalid rule structures
* incompatible scenario assumptions

### Step 5 — WorldMatrix Compile

System emits:

* `worldmatrix.json`
* validation report
* provenance manifest
* compile metadata

### Step 6 — Scenario / WorldBranch Creation

Operator derives a runnable branch from the WorldMatrix:

* branch from baseline world
* alter assumptions
* set initial event conditions
* define runtime objective or evaluation target

### Step 7 — Runtime Instantiation

System creates a runtime-ready package:

* agent roster
* role bindings
* initial visible state per actor
* allowed action schema
* event loop parameters
* stopping conditions

### Step 8 — Test Run

Run a basic multi-agent execution and expose:

* turn logs
* action traces
* world state transitions
* branch outcome summary

---

## 5. Primary System Artifacts

## 5.1 Project

Container for all work related to one world family.

Fields:

* id
* name
* description
* domain_type
* created_at
* updated_at
* status

## 5.2 SetupSession

Represents a guided authoring interview.

Fields:

* id
* project_id
* phase
* transcript
* extracted_facts
* pending_questions
* draft_worldmatrix_id
* status

## 5.3 WorldMatrixDraft

Mutable structured world under construction.

Fields:

* id
* project_id
* version
* metadata
* environment
* entities
* polities
* relationships
* resources
* rules
* knowledge_layers
* operator_role
* unresolved_items
* provenance
* validation_state

## 5.4 WorldMatrix

Verified compiled world artifact.

Fields:

* id
* project_id
* version
* draft_source_id
* compiled_at
* compatibility_version
* payload
* validation_report
* provenance_manifest

## 5.5 WorldBranch

Derived branch from a compiled WorldMatrix.

Fields:

* id
* worldmatrix_id
* parent_branch_id
* title
* modifications
* initial_conditions
* branch_notes

## 5.6 Scenario

Runnable instantiation contract.

Fields:

* id
* worldbranch_id
* runtime_profile
* actor_bindings
* initial_state
* stop_conditions
* evaluator_config

## 5.7 SimulationRun

Execution record for a test or run.

Fields:

* id
* scenario_id
* started_at
* completed_at
* runtime_trace
* event_log
* state_snapshots
* result_summary

---

## 6. Agentic Architecture for MVP

The MVP should act like a multi-agent system even if implemented initially through a single orchestrator plus role prompts.

### 6.1 Architect Roles

#### Interview Architect

Drives the conversation with the operator.
Determines next best question.
Produces natural-language summaries.

#### Schema Architect

Maps interview content into structured WorldMatrix fields.

#### Validation Architect

Checks consistency, missing required fields, role conflicts, and rule coherence.

#### Ingestion Architect

Handles optional URLs, documents, notes, datasets, and converts them into candidate facts/artifacts.

#### Runtime Architect

Transforms WorldMatrix/Branch into Scenario and runtime initialization data.

#### Trace Architect

Records provenance, confidence, decisions, and model/tool usage.

### 6.2 MVP Implementation Strategy

Phase 1 implementation can use:

* one orchestrator service,
* one LLM backend,
* role-scoped prompts,
* typed contracts for each role output.

This keeps the code simple while preserving future expansion into real multi-agent execution.

---

## 7. WorldMatrix v1 Schema Shape

The MVP WorldMatrix should be explicit and narrow.

```json
{
  "metadata": {},
  "domain": {},
  "environment": {},
  "entities": [],
  "polities": [],
  "relationships": [],
  "resources": [],
  "rules": [],
  "knowledge_layers": {},
  "operator_role": {},
  "simulation_profile": {},
  "provenance": [],
  "validation": {}
}
```

### 7.1 metadata

* title
* description
* author/operator
* version
* created_at
* updated_at

### 7.2 domain

* domain_type (`fiction`, `geopolitical`, `social`, `historical`, `hybrid`)
* ontology_pack
* time_scope
* spatial_scope
* realism_mode

### 7.3 environment

* world description
* map/regions/locations
* environmental attributes
* macro conditions

### 7.4 entities

For individuals or major agents.

* id
* name
* type
* description
* goals
* capabilities
* affiliations
* visible_knowledge_refs
* hidden_state

### 7.5 polities

For factions, groups, states, organizations.

* id
* name
* category
* leadership
* resources
* objectives
* constraints

### 7.6 relationships

* source
* target
* type
* strength
* trust/hostility/alignment
* provenance

### 7.7 resources

* owner
* resource_type
* quantity/value
* access constraints

### 7.8 rules

* physical/social/geopolitical/narrative rules
* action constraints
* forbidden actions
* trigger rules

### 7.9 knowledge_layers

* world_truth
* public_knowledge
* polity_private
* entity_private
* contested_claims
* operator_visibility

### 7.10 operator_role

* mode (`observer`, `entity_possession`, `polity_possession`, `zeus`, `director`)
* bindings
* permissions
* visibility_scope

### 7.11 simulation_profile

* simulation style
* turn cadence
* branching policy
* abstraction level
* evaluation mode

### 7.12 provenance

* operator_defined
* ingested_source
* model_inferred
* contested
* unresolved

### 7.13 validation

* required section completeness
* unresolved blockers
* warnings
* compile readiness

---

## 8. Setup Wizard State Machine

### Phase 0 — Bootstrap

Create project and setup session.

### Phase 1 — Intent Framing

Determine what kind of world is being built.

### Phase 2 — Ontology Selection

Choose domain pack and initial schema emphasis.

### Phase 3 — World Population

Add environment, entities, polities, resources, and relationships.

### Phase 4 — Rules and Knowledge Boundaries

Define rules, visibility, and operator role.

### Phase 5 — Validation Pass

Resolve blockers and contradictions.

### Phase 6 — Compile

Emit verified WorldMatrix.

### Phase 7 — Branch/Scenario Authoring

Create scenario-ready derivative artifact.

### Phase 8 — Runtime Instantiation

Generate runnable scenario package.

---

## 9. Recommended MVP Tech Stack

### Platform Baseline

* WSL2 Ubuntu
* Python 3.11 or 3.12 (pick one and standardize)
* uv for environment/package management
* FastAPI for API
* Pydantic v2 for contracts
* Typer for CLI
* Postgres or SQLite for MVP metadata/state
* Redis optional, only if needed later

### Storage

* Local filesystem for artifacts
* JSON files for WorldMatrix / Scenario / traces
* SQLite first for speed unless you already know Postgres is needed

### UI

For speed, start with one of:

* lightweight React frontend, or

Recommendation for fast MVP: **FastAPI + minimal React/Tailwind UI + CLI fallback**

### LLM / Agent Backends

* Local model option via LM Studio / Ollama / vLLM-compatible endpoint
* Full openrouter support 
* Strict capability registry from day one

### Observability

* structured trace records in JSON
* per-step logs
* model/provider used
* token/cost/latency metadata where applicable

---

## 10. Repository Shape for PyScrAi

```text
pyscrai/
  apps/
    api/
    web/
    cli/
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
    projects/
  docs/
  tests/
```
---

## 11. Fast MVP API Surface

### Project / Setup

* `POST /projects`
* `POST /projects/{id}/setup-sessions`
* `POST /setup-sessions/{id}/messages`
* `GET /setup-sessions/{id}`

### WorldMatrix

* `GET /projects/{id}/worldmatrix-draft`
* `POST /projects/{id}/worldmatrix-draft/validate`
* `POST /projects/{id}/worldmatrix-draft/compile`
* `GET /worldmatrices/{id}`

### Branch / Scenario

* `POST /worldmatrices/{id}/branches`
* `POST /branches/{id}/scenarios`
* `GET /scenarios/{id}`

### Runtime

* `POST /scenarios/{id}/instantiate`
* `POST /runs`
* `GET /runs/{id}`
* `GET /runs/{id}/trace`

---

## 12. MVP Runtime Model

The runtime should be intentionally simple at first.

### Inputs

* Scenario
* actor bindings
* visible state slices
* action schema
* ruleset

### Runtime loop

1. build visible state for each actor
2. ask actor for action proposal
3. validate action against rules
4. apply action to state
5. log event and provenance
6. evaluate stop conditions
7. continue or terminate

### First runtime constraint

Use discrete turns and simple state transitions.
Do not start with continuous simulation.

---

## 13. First Three Milestones

## Milestone 1 — World Setup Spine

Goal: create Project -> SetupSession -> WorldMatrixDraft

Deliverables:

* project creation
* setup session model
* interview loop endpoint
* schema architect output mapping
* live world draft persistence
* basic validation

## Milestone 2 — Compile and Branch

Goal: compile verified WorldMatrix and derive WorldBranch/Scenario

Deliverables:

* validation report
* compile contract
* worldmatrix artifact
* branch creation
* scenario creation

## Milestone 3 — Runtime MVP

Goal: instantiate scenario and run a basic multi-agent turn loop

Deliverables:

* agent bindings
* visible state slicing
* turn loop
* action validation
* event log
* trace viewer/log endpoint

---

## 14. What to Avoid

* Building a huge scraping framework before the setup wizard works
* Overbuilding ontology for every possible domain at once
* Mixing simulator concerns into setup-session contracts too early
* Building a complex GUI before the API/contracts stabilize
* Using uncontrolled free-form LLM outputs without typed schemas
* Treating ingestion output as truth without provenance and confirmation

---

## 15. Immediate Next Build Order

1. Define core contracts:

   * Project
   * SetupSession
   * WorldMatrixDraft
   * WorldMatrix
   * WorldBranch
   * Scenario
   * SimulationRun

2. Build FastAPI endpoints for:

   * create project
   * start setup session
   * send interview message
   * get/update worldmatrix draft
   * validate/compile

3. Implement architect orchestrator service with role-scoped outputs.

4. Build a basic persistence layer using SQLite + artifact JSON.

5. Add scenario derivation and runtime instantiation.

6. Implement a minimal multi-agent discrete turn loop.

7. Add lightweight web UI for the setup wizard and trace inspection.

---

## 16. Final Direction

The correct MVP is not “rebuild everything.”
The correct MVP is:

**a guided world-authoring system that can produce a validated WorldMatrix and run at least one simple branch/scenario end-to-end.**

That is narrow enough to ship quickly and strong enough to prove the architecture.
