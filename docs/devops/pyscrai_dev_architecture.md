# PyScrAI Forge — Architecture Draft

## 1. Architectural intent

PyScrAI Forge is the top-level shell for assembling, configuring, and launching a PyScrAI instance.

The architecture should support three realities at once:

1. a dev-first, rapidly changing internal platform
2. a local-first ingestion and ML workflow
3. a future-facing agent lab and simulation environment

The system therefore needs clean boundaries. It must avoid turning into one entangled application where platform configuration, world content, ingestion logic, and runtime semantics all collapse into the same layer.

## 2. System model

PyScrAI should be treated as a layered platform.

### Layer A — Forge Shell

The operator-facing entry surface.

Responsibilities:

* project creation and loading
* goal intake
* architect interview
* core module selection
* manifest editing / approval
* launch points into authoring, ingestion, lab, and runtime

Initial implementation:

* Streamlit

### Layer B — Agent Substrate

The orchestration layer that interprets goals, routes actions, and coordinates tool use.

Responsibilities:

* architect interview flow
* intent analysis
* module recommendation
* handoffs between workflows
* tool routing
* policy-aware orchestration
* future multi-agent coordination

Initial implementation:

* Agent Zero

### Layer C — Provider Bus

The abstraction layer between PyScrAI logic and actual model providers.

Responsibilities:

* provider normalization
* model routing
* local vs remote provider handling
* capability metadata
* fallback policies
* future observability hooks

Initial implementation:

* LiteLLM

Primary providers:

* OpenRouter
* LM Studio

### Layer D — Module Registry / Capability Graph

The layer that defines what modules exist, what they require, and what they expose.

Responsibilities:

* module metadata registry
* dependency declarations
* config schemas
* exposed services and UI surfaces
* lifecycle hooks
* artifact contracts

Initial implementation:

* static/internal registry
* explicit config models
* no dynamic plugin loading required initially

### Layer E — Project Artifacts

The persistent declarative state for a PyScrAI instance.

Primary artifacts:

* Project Manifest
* WorldMatrix

These should remain separate.

### Layer F — Operational Surfaces

The actual working subsystems that perform specialized work.

Initial operational surfaces:

* world authoring
* ingestion / extraction
* memory / retrieval
* prompt / agent lab
* runtime / simulation
* tool / MCP integration

## 3. Artifact model

### 3.1 Project Manifest

The Project Manifest describes what the instance is capable of and how it is configured.

Suggested top-level sections:

* metadata
* enabled_modules
* providers
* routing_policy
* storage
* vectors
* graph
* mcp_servers
* memory
* runtime_profile
* policies
* ui_surfaces

The Project Manifest should be editable by both the operator and the architect agent.

### 3.2 WorldMatrix

The WorldMatrix describes scenario and world content.

Suggested concerns:

* entities
* relations
* rules
* knowledge boundaries
* geographic or structural scope
* branches
* scenarios
* initial conditions
* timeline state

The WorldMatrix should be produced and updated through the authoring subsystem, not treated as the same thing as the platform manifest.

## 4. Core module classes

PyScrAI should start with a small set of first-class module categories.

### 4.1 Core / platform modules

These support the existence of the platform itself.

Examples:

* agent substrate
* provider registry
* manifest manager
* module registry
* project storage manager

### 4.2 Authoring modules

These support world/scenario construction.

Examples:

* setup interview mapper
* world draft compiler
* validation engine
* scenario and branch manager

### 4.3 Ingestion modules

These support document and knowledge intake.

Examples:

* file ingestion
* chunking
* embedding pipeline
* entity extraction
* relation extraction
* dedup / canonicalization
* graph handoff

### 4.4 Memory / retrieval modules

These support recall and contextual access.

Examples:

* vector retrieval
* chunk store
* document registry
* session memory
* long-term memory interfaces

### 4.5 Tool / MCP modules

These support external and internal tool access.

Examples:

* MCP server registry
* tool capability descriptors
* tool safety / policy wrappers
* execution adapters

### 4.6 Lab modules

These support prompt and agent experimentation.

Examples:

* prompt playground
* provider comparison
* trace inspection
* agent workflow evaluation
* benchmark suite runner

### 4.7 Runtime / simulation modules

These support execution of scenarios.

Examples:

* runtime state loader
* actor model
* rule engine
* scheduler
* event log
* divergence controls
* state checkpointing

## 5. Local-first ingestion architecture

Ingestion should default to local processing wherever practical.

### 5.1 Preferred local-first pipeline

1. input acquisition
2. normalization
3. chunking
4. local embeddings
5. local task-specific extraction
6. candidate graph assembly
7. optional LLM escalation
8. manifest/world handoff

### 5.2 Local responsibilities

Prefer local models for:

* embeddings
* document segmentation
* entity extraction
* relation extraction
* classification
* candidate linking

### 5.3 LLM escalation points

Use provider-backed LLMs when needed for:

* semantic disambiguation
* contextual synthesis
* narrative reasoning
* ambiguity resolution
* architect-level decision support
* simulation cognition where local methods are insufficient

This preserves cost control and architectural discipline.

## 6. Prompt lab / agent lab architecture

The prompt lab and agent lab should initially be treated as adjacent operational surfaces, not as fully fused core subsystems.

### Near-term recommendation

Use an external/internal bootstrap stack while the native PyScrAI lab matures.

Suggested bootstrap tools:

* Open WebUI for internal experimentation surface
* Langfuse or Agenta for prompt management, traces, and evals
* Promptfoo for systematic testing and regression checks

### Native long-term direction

Eventually, Forge should expose:

* prompt set management
* provider/model comparison
* agent workflow graph inspection
* tool routing tests
* eval suites
* scenario-specific benchmark packs

## 7. Data and storage stance

Storage should remain abstracted behind contracts until usage patterns harden.

### Near-term storage posture

* file-backed artifacts for manifests and world data
* SQLite where structured local persistence is sufficient
* optional vector backend only when retrieval workflows become real
* graph backend behind an abstraction layer

### Delayed commitments

Do not lock too early into a final graph or system-state backend before the workloads are clearer.

This is especially important for:

* Neo4j
* PostgreSQL
* Redis
* large vector DB commitments

## 8. Runtime boundary

The runtime must remain downstream of Forge and the manifest.

Forge should define:

* what modules exist
* what providers are enabled
* what policies apply
* what world/scenario is being launched

The runtime should consume that configuration and execute accordingly.

This prevents the runtime from becoming the hidden center of the entire system.

## 9. Suggested request flow

### 9.1 New project flow

1. operator opens Forge
2. enters a goal in natural language
3. architect agent interviews operator
4. agent recommends core modules
5. Project Manifest is drafted
6. operator reviews/edits manifest
7. Forge scaffolds project structure and enabled surfaces
8. operator launches authoring / ingestion / lab / runtime

### 9.2 Ingestion flow

1. operator selects ingestion surface
2. files or sources are registered
3. local extraction pipeline runs
4. optional LLM escalation occurs where needed
5. extracted artifacts are stored and indexed
6. memory / graph / authoring surfaces receive outputs

### 9.3 Runtime launch flow

1. operator chooses scenario/world
2. Forge resolves the manifest and runtime profile
3. runtime loads required modules and state
4. agents/tools/providers are bound according to policy
5. execution begins with traceable state boundaries

## 10. Near-term implementation map

### Phase 1 — shell and contracts

* minimal Streamlit Forge shell
* Project Manifest schema
* internal module registry
* architect agent flow
* adapter into existing world-authoring pipeline

### Phase 2 — ingestion and lab groundwork

* local ingestion contracts
* provider bus integration
* prompt/eval bootstrap integration
* document and chunk registry
* extraction model routing

### Phase 3 — runtime redesign

* runtime state contract
* actor and rule abstractions
* event and checkpoint models
* divergence mitigation strategy
* simulation-specific LLM/tool routing

## 11. Architecture principles

1. **Local-first where practical**
2. **Providers abstracted from workflows**
3. **Manifest separate from world content**
4. **Agent substrate beneath modules, not beside them**
5. **Modules should declare contracts before dynamic loading exists**
6. **Runtime should consume configuration, not define the platform**
7. **Use external OSS to bootstrap selectively, not to replace architecture**

## 12. Bottom line

PyScrAI Forge should become the product shell that assembles a PyScrAI instance. The current repo should be preserved as the first major internal subsystem rather than treated as the whole platform.

The architecture should therefore center on:

* Forge as shell
* Agents SDK as orchestration substrate
* LiteLLM as provider bus
* OpenRouter + LM Studio as primary providers
* Project Manifest as platform contract
* WorldMatrix as scenario/world contract
* local-first ingestion as the data backbone
* an evolving agent lab as the experimentation surface

That structure gives PyScrAI a disciplined foundation for growth without prematurely freezing the wrong layers.
