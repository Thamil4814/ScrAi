# PyScrAI Development Architecture

## 1. Architectural intent

PyScrAI is a project-oriented, operator-first platform for building, configuring, validating, and executing structured world and scenario systems.

The architecture must support five realities simultaneously:

1. rapid internal development and changing implementation details
2. local-first and hybrid ingestion, extraction, and model workflows
3. strong operator control with manual-first interaction as a first-class principle
4. Agent Zero as an integrated assistant and automation substrate, not the sole center of the system
5. future expansion from Forge-based data and world construction into downstream runtime and execution surfaces

The result should be a layered platform with hard separation between:

* project and platform configuration
* reusable project-scoped presets and templates
* world and scenario content
* module capabilities and lifecycle
* agent orchestration
* downstream execution/runtime concerns

PyScrAI must not collapse into a single entangled application where project setup, ingestion, database editing, visualization, prompting, agent orchestration, and runtime logic all live in one indistinct surface.

## 2. Core platform stance

### 2.1 Operator-first control

Manual operator control is first-class.

Automation, agent assistance, and orchestration exist to accelerate and extend the operator, not to replace the operator as the authoritative controller of the system. In practical terms, PyScrAI should always allow the operator to:

* create and bootstrap projects directly
* inspect and edit configurations directly
* launch and stop services explicitly
* enter or modify data manually
* choose when Agent Zero assists, answers questions, or automates a workflow
* override or bypass agent recommendations when required

### 2.2 Project-oriented system model

PyScrAI is fundamentally project-oriented.

A project is the primary boundary for configuration, data, enabled modules, artifacts, stores, agents, and operational behavior. Different projects may open into materially different experiences depending on their configured modules, presets, providers, storage backends, and data model choices.

### 2.3 Dual-system trajectory

PyScrAI should be treated as a dual-system framework:

* **Forge**: project management, data generation, ingestion, authoring, validation, and world-building surfaces that produce structured project artifacts and WorldMatrix outputs
* **Crucible**: downstream execution and utilization layer that consumes WorldMatrix and project configuration for scenario runtime, simulation, experimentation, or other applied use cases

The current repository is centered on Forge. Crucible should remain an architectural target and downstream boundary rather than being forced prematurely into the current implementation.

## 3. High-level startup and operational flow

A typical operator-driven startup flow should look like this:

1. operator starts the PyScrAI API and related application surfaces
2. operator starts the Agent Zero Podman or Docker container
3. operator boots required supporting services as needed for the active project, such as databases, MCP servers, A2A endpoints, provider adapters, AG-UI surfaces, or other APIs
4. operator enters the Forge shell
5. Forge offers project selection, start-with-last-project behavior, or new-project initialization
6. the selected project determines the opening configuration, available modules, loaded presets, data surfaces, and launch paths

This flow is intentionally explicit. PyScrAI should assume complex local and hybrid environments and should not hide all infrastructure lifecycle under opaque automation.

## 4. Layered system model

PyScrAI should be treated as a layered platform.

### Layer A — Forge Shell

The primary operator-facing entry surface.

Responsibilities:

* project selection and project loading
* start-with-last-opened-project behavior
* new-project initialization
* project bootstrap and editing
* module discovery and module loading
* project, platform, and module configuration
* preset selection and management
* launch points into DB, DV, DE, PL, PFab, and future runtime surfaces
* visibility into connected services and platform readiness

Initial implementation:

* Streamlit, with room for future migration or expansion into richer GUI surfaces

### Layer B — Agent Substrate

The integrated agent orchestration layer. 

Uses AgentZero via A2A running in a container on the host machine. 

Responsibilities:

* operator assistance and question answering
* workflow automation when explicitly invoked or authorized
* architect-style recommendation and planning flows
* handoffs between module workflows
* tool routing and policy-aware orchestration
* future multi-agent coordination
* A2A-based communication into Agent Zero

Initial implementation:

* Agent Zero running externally in a containerized environment

Architectural stance:

* Agent Zero is an integrated assistant substrate inside PyScrAI's architecture
* Agent Zero is not the entirety of PyScrAI's agent or model instantiation story
* Agent Zero configuration and settings are primarily managed through Agent Zero's own interface
* PyScrAI should interact with Agent Zero through a clean bridge/adapter boundary
* PyScrAI should be able to instantiate additional LLM- or agent-backed systems outside the Agent Zero ecosystem when required by future workflows

### Layer C — Provider Bus / Model Instantiation Fabric

The abstraction layer between PyScrAI workflows and actual models, providers, or agent runtimes.

Responsibilities:

* provider normalization
* local versus remote provider routing
* capability metadata and model selection
* fallback and escalation policy
* future observability and evaluation hooks

Near-term implementation:

* LiteLLM or equivalent provider abstraction for conventional LLM routing
* explicit support for OpenRouter and LM Studio
* future room for direct local model runners, task-specific ML pipelines, or alternative agent systems

This layer exists precisely because PyScrAI should not couple all intelligent behavior to a single external agent framework.

### Layer D — Module Registry / Capability Graph

The layer defining what modules exist, what they require, and what they expose.

Responsibilities:

* module metadata registry
* dependency declarations
* config schemas
* lifecycle hooks
* UI exposure metadata
* storage and service requirements
* artifact contracts
* operator-launchable surfaces

Initial implementation:

* static or internal registry
* explicit config models
* no requirement for dynamic plugin loading in the earliest phases

Longer term:

* module/plugin packaging and controlled extension mechanisms
* module editing and testing through the PreFab surface

### Layer E — Project Artifacts

The persistent declarative and semi-declarative state for a PyScrAI project.

This includes, at minimum:

* project metadata and identity
* project configuration
* project-scoped presets and templates
* module configuration state
* ingested raw and transformed artifacts
* structured stores and database outputs
* WorldMatrix and related authoring artifacts

These artifacts must remain separated by concern rather than flattened into one file or one store.

### Layer F — Operational Surfaces

The actual working subsystems that perform specialized work.

Primary operational surfaces in Forge should include:

* Configuration Module
* DataBase Module
* DataViz & Verify Module
* DataExtract Module
* Prompt Lab Module
* PreFab Module

Crucible and runtime surfaces remain downstream consumers rather than being allowed to dominate Forge.

## 5. Project, preset, and template hierarchy

This hierarchy is essential and must remain explicit.

### 5.1 Project level

The project level determines the global what, where, and how for a PyScrAI instance.

A project should own or define:

* project identity and metadata
* enabled modules
* storage targets and database choices
* provider and routing choices
* loaded interfaces and service endpoints
* project-level policies
* project-level data directories and artifact locations
* default launch behavior

Projects store data. Depending on configuration, this may include:

* raw sources
* extracted datasets
* databases and indexes
* relationship charts
* entities and environments
* agents and their project bindings
* scenario or world artifacts
* maps, geospatial layers, and rules

### 5.2 Preset / template level

Presets and templates are managed within the Configuration Module and are locked to their parent project.

Their purpose is to group and reapply coherent configuration sets for a given project, such as:

* module settings bundles
* workflow-specific provider choices
* extraction pipeline profiles
* DB and DV views or validation profiles
* scenario authoring or runtime preparation configurations

A preset is not the same thing as a project. It is a project-scoped configuration bundle that allows multiple operating modes or specialized workflows within the same project.

### 5.3 Why the separation matters

Without this separation, PyScrAI risks conflating:

* instance identity
  n- operational mode
* content artifacts
* module tuning
* workflow presets

The project is the durable container. Presets are reusable operating modes inside that container.

## 6. Artifact model

### 6.1 Project manifest and project configuration

The project configuration layer should describe what the project is capable of and how it is wired.

Suggested top-level concerns include:

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
* service_bindings
* startup_expectations
* preset_registry

Whether this is represented as a single manifest or a small family of project-level artifacts is an implementation detail. Architecturally, the concern is the same: it describes platform and project capability, not world content.

### 6.2 WorldMatrix

The WorldMatrix represents structured world, scenario, or simulation content.

Suggested concerns:

* entities
* relations
* environments
* locations
* spatial structures
* rules and constraints
* knowledge boundaries
* timelines and branches
* scenarios
* initial conditions
* context overlays

The WorldMatrix should be authored, transformed, and validated through operational surfaces such as DB Mod and DV Mod. It must not be treated as interchangeable with project/platform configuration.

### 6.3 Ingestion and transformation artifacts

The ingestion pipeline should generate intermediate artifacts before they become durable structured world data.

Examples:

* source registry records
* normalized text artifacts
* chunks
* embeddings
* extraction candidates
* entity and relation proposals
* deduplication and canonicalization reports
* graph handoff artifacts
* validation queues

These should remain explicit so the operator can inspect, verify, and correct the transformation path.

## 7. Core Forge module architecture

Forge is centered on a small set of primary modules.

### 7.1 Configuration Module (Conf Mod)

The Configuration Module is the platform management workbench.

Responsibilities:

* create, bootstrap, edit, and manage projects
* load existing modules into a project
* manage PyScrAI-wide, project-level, and module-level configuration
* create, manage, and load project-scoped presets
* manage startup behaviors such as start-with-last-project
* expose service readiness and loaded-surface state

Notes:

* Conf Mod loads modules but does not need to be the authoring surface for module code itself
* module creation is a separate concern addressed later by PreFab

### 7.2 DataBase Module (DB Mod)

The structured data creation and editing workbench.

Responsibilities:

* create structured data from scratch
* load transformed data from DataExtract Module outputs
* edit entities, relationships, environments, locations, spatial structures, rules, and context
* inject validated data into configured storage targets such as JSON, SQL, spatial databases, graph stores, or other configured backends
* serve as the main structured world-building surface

Notes:

* DB Mod may be divided into submodules if the scope becomes too large
* it should remain operator-legible and editable rather than fully hidden behind automation

### 7.3 DataViz & Verify Module (DV Mod)

The visualization, validation, and polishing workbench.

Responsibilities:

* visualize graphs, charts, relationship maps, geospatial data, and other structured outputs
* provide custom or specialized data visualizations depending on project configuration
* support validation, verification, review, and refinement of authored or ingested data
* function as the primary polishing surface prior to downstream use

DV Mod is distinct from DB Mod. The DB surface is for structured creation and editing; DV is for seeing, checking, validating, and refining.

## 8. Secondary module architecture

### 8.1 DataExtract Module (DE Mod)

The ingestion and extraction pipeline.

Responsibilities:

* register and ingest raw sources such as URI, URL, scraped content, PDF, TXT, and other document types
* normalize and prepare source material for downstream loading
* use ML and LLM-assisted extraction where appropriate
* generate artifacts suitable for DB Mod loading and verification
* support highly customizable workflows for different project types

Architectural note:

DE Mod is highly important but not inherently core, because some projects may rely more heavily on manual entry, bespoke external tooling, or Agent Zero-assisted custom workflows.

### 8.2 Prompt Lab Module (PL Mod)

The prompt, provider, and evaluation experimentation surface.

Responsibilities:

* prompt testing
* provider and model comparison
* trace and evaluation review
* regression-style prompt checks
* workflow benchmarking when relevant

Architectural note:

This may initially be partially outsourced to existing frameworks until observability, evaluation, and prompt-management needs justify a deeper native implementation.

### 8.3 PreFab Module (PFab Mod)

The future module authoring and testing surface.

Responsibilities:

* open, edit, inspect, and test PyScrAI modules
* provide a focused GUI for module development workflows
* help evolve the module/plugin system beyond direct IDE-only editing
* expose Agent Zero assistance for module analysis or automation where useful

Architectural note:

In the near term, modules are still created in code through the normal development environment. PFab is a mid-range target for making module construction and testing more operator-accessible.

## 9. Agent Zero integration architecture

Agent Zero is now the initial Layer B substrate, but it must be integrated with discipline.

### 9.1 Required stance

* Agent Zero acts as the integrated LLM-based assistant inside PyScrAI
* it should be quickly available for answering questions, assisting operator workflows, and automating tasks where permitted
* it should not own all model instantiation or all future agent behavior in the platform
* PyScrAI must preserve the ability to stand up additional agent systems or direct provider-driven workflows outside Agent Zero

### 9.2 Integration boundary

PyScrAI should talk to Agent Zero through a dedicated bridge/adapter boundary, with A2A as the primary communication protocol.

That bridge should be responsible for:

* request and response normalization
* session/context handoff
* profile or subordinate selection
* attachment and artifact handoff
* error handling and health reporting
* clean separation from PyScrAI's domain logic

### 9.3 Configuration boundary

Most Agent Zero configuration and settings should be handled in Agent Zero's own interface.

PyScrAI should store only the minimum necessary integration state, such as:

* connection endpoints
* enabled/disabled bridge state
* project bindings if required
* policy or routing references relevant to PyScrAI workflows

This prevents redundant configuration UIs and keeps responsibility clear.

### 9.4 Agent role inside the platform

Agent Zero should be treated as an assistant substrate within an operator-governed system, not as an invisible autonomous operating center.

## 10. Local-first and hybrid intelligence architecture

### 10.1 Default posture

Ingestion and data preparation should default to local processing wherever practical.

Prefer local or project-controlled methods for:

* embeddings
* document segmentation
* entity extraction
* relation extraction
* classification
* candidate linking
* intermediate transformation

### 10.2 Escalation posture

Use provider-backed or remote LLMs selectively for:

* semantic disambiguation
* contextual synthesis
* difficult reasoning steps
* ambiguity resolution
* narrative or scenario support
* agent-assisted planning where local methods are insufficient

### 10.3 Architectural value

This preserves:

* cost control
* offline or local-first workflows
* operator trust and inspectability
* freedom to mix task-specific ML with broader LLM orchestration

## 11. Data and storage stance

Storage should remain abstracted behind contracts until usage patterns stabilize.

### Near-term posture

* file-backed artifacts where sufficient
* SQLite for lightweight structured persistence
* optional vector backends when retrieval becomes operationally real
* graph or spatial backends behind abstractions
* project-defined storage choices rather than one mandatory global backend

### Candidate storage targets

Depending on project needs, PyScrAI may write to:

* JSON and structured file artifacts
* SQLite or other SQL stores
* PostgreSQL or spatial PostgreSQL
* Redis
* graph stores
* vector stores
* node/relationship-oriented systems

The architecture should allow this diversity without forcing the entire platform to commit too early to one storage stack.

## 12. Runtime and Crucible boundary

Runtime must remain downstream of Forge and project configuration.

Forge defines:

* what modules exist
* what providers and agent surfaces are enabled
* what policies apply
* what data and world artifacts are available
* what configuration set or preset is active

Crucible or any runtime surface should consume that state and execute accordingly.

This preserves separation of concerns and prevents runtime behavior from becoming the hidden center of the platform.

## 13. Canonical operator flows

### 13.1 Initial/opening flow

1. operator starts core services
2. operator opens Forge
3. Forge optionally starts with the last opened project
4. otherwise, Forge presents an available-projects surface
5. operator selects an existing project or initializes a new one
6. if creating a new project, operator supplies name and bootstrap settings
7. Forge creates and loads the new project into the Configuration Module
8. project configuration determines available modules, presets, services, and launch paths

### 13.2 New-project bootstrap flow

1. create project identity and base directories/artifacts
2. initialize project configuration
3. register default or selected modules
4. create initial preset scaffolding where appropriate
5. bind provider and service settings
6. load the project into Conf Mod for further editing

### 13.3 Ingestion flow

1. operator enters DE Mod
2. sources are registered and normalized
3. extraction pipeline runs locally where practical
4. optional Agent Zero or external LLM assistance is used where warranted
5. intermediate artifacts are produced for inspection
6. outputs are passed into DB Mod and DV Mod for structured loading and verification

### 13.4 World/data authoring flow

1. operator enters DB Mod
2. operator creates or edits entities, relationships, locations, environments, rules, and context
3. data is written into configured stores or intermediate project artifacts
4. DV Mod is used to visualize and verify the results
5. validated outputs are promoted into durable project/world artifacts

### 13.5 Assisted workflow flow

1. operator invokes Agent Zero assistance
2. PyScrAI routes the request through the bridge
3. Agent Zero answers, recommends, or automates within policy bounds
4. operator reviews and accepts, edits, or rejects results
5. resulting artifacts remain visible within the project surfaces

## 14. Near-term implementation map

### Phase 1 — project shell and disciplined integration

* stabilize Forge as the project-oriented shell
* preserve project/preset/module separation
* integrate Agent Zero through a clean bridge
* keep Agent Zero configuration primarily external
* expose project loading, creation, and surface launch behavior clearly

### Phase 2 — module hardening

* mature Conf Mod, DB Mod, and DV Mod as the three primary Forge modules
* formalize module contracts and service requirements
* improve DE Mod handoff into DB and DV workflows
* define project-scoped preset mechanics explicitly

### Phase 3 — broader intelligence and tooling fabric

* expand provider bus support beyond Agent Zero
* enable non-Agent Zero agent or LLM instantiation where needed
* deepen prompt/eval workflows
* introduce more rigorous observability and benchmarking

### Phase 4 — PreFab and downstream runtime

* begin PFab as a module-authoring surface
* harden runtime/Crucible boundaries
* formalize how WorldMatrix and project configuration are consumed by downstream execution systems

## 15. Architecture principles

1. **Operator authority is first-class**
2. **Projects are the primary boundary of configuration and data**
3. **Presets belong to projects and are not substitutes for projects**
4. **Agent Zero is integrated, but not exclusive**
5. **Provider/model instantiation must remain abstractable**
6. **Configuration must remain separate from world content**
7. **Visualization/verification is a distinct concern from raw data editing**
8. **Local-first processing should be preferred where practical**
9. **Automation should remain inspectable and overridable**
10. **Runtime should consume platform state, not define the platform**

## 16. Bottom line

PyScrAI should remain a project-oriented, operator-governed platform in which Forge manages configuration, data construction, validation, and modular surfaces; Agent Zero serves as an integrated but bounded assistant substrate; and future runtime systems such as Crucible consume the resulting project and world artifacts without collapsing the architecture into a single opaque agent application.
