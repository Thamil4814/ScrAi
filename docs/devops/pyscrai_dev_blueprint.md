# PyScrAI Forge — Primary Development Document

## Purpose

PyScrAI is evolving from a narrow world-authoring vertical slice into a broader, dev-first AI sandbox and simulation platform. The correct entry point for that platform is **PyScrAI Forge**.

Forge should be the application the operator opens first. It is the shell that helps define what a PyScrAI instance is, what capabilities it has, and how the operator moves into authoring, ingestion, experimentation, and runtime.

## Working decisions

### Product / shell

* **Entry point name:** PyScrAI Forge
* **Near-term posture:** closed, internal, dev-first
* **Priority:** feature velocity, architecture clarity, and fast iteration over polish

### UI

* **Initial GUI framework:** Streamlit

Rationale:

* fastest path to a usable internal UI
* low overhead while architecture is still changing
* approachable for semi-technical collaborators
* lets development focus stay on engine, orchestration, and workflows rather than frontend polish

### Agent substrate

* **Initial orchestration framework:** Agent Zero

Rationale:

* fast to stand up for the architect/interview flow
* suitable for tools, handoffs, and agent orchestration
* provides a clean initial substrate without forcing a heavier full-stack abstraction too early

### Provider strategy

* **Primary AI API providers:** OpenRouter and LM Studio
* **Recommended provider bus:** LiteLLM

Rationale:

* normalizes remote and local model access through one interface
* keeps provider choice decoupled from agent logic
* reduces custom adapter work across the platform

### Prompt / eval / lab stack

* **Recommended internal lab surface:** Open WebUI
* **Recommended tracing / prompt management / eval stack:** Langfuse or Agenta
* **Recommended regression / benchmark tooling:** Promptfoo

Rationale:

* Open WebUI can act as a temporary internal experimentation surface while Forge matures
* Langfuse or Agenta can provide prompt management, traces, and evaluation workflows
* Promptfoo gives structured testing for prompts, agents, and RAG behavior

## What the repo is today

The current repo already contains a usable nucleus. It is strongest at:

* project bootstrap
* guided setup/interview flow
* structured draft creation
* validation and compile flow
* branch and scenario creation
* thin deterministic runtime scaffolding

This is valuable and should be preserved.

## What the repo is not yet

The current repo is not yet the broader PyScrAI platform vision.

Current gaps:

* no top-level Forge shell
* no formal project manifest above the world artifacts
* no mature module registry
* no platform-wide agent substrate
* no robust local-first ingestion layer
* no production-ready memory/RAG stack
* no durable prompt/eval lab
* no true multi-agent runtime system

## Product direction

Forge should not be limited to world creation.

Forge should help assemble a **PyScrAI instance**.

That means Forge should do four things:

1. accept the operator’s goal in natural language
2. run an architect-style interview
3. recommend and enable modules/capabilities
4. scaffold the project, storage, tools, and authoring/runtime surfaces

Initially, this should stay focused on setting up the **core modules only**. That narrower scope is desirable. It gives Forge a disciplined first role and lets the team use it as a living MVP that evolves alongside the platform.

## Core design stance

Do **not** make the agent system just another module.

The agent system should be the substrate that helps configure, coordinate, and route across the rest of the platform.

Recommended layering:

* Forge shell
* agent substrate
* module registry / capability graph
* project artifacts
* authoring / ingestion / runtime surfaces

## Required artifact split

PyScrAI should maintain two primary artifacts.

### 1. Project Manifest

This defines what a specific PyScrAI instance can do.

Examples:

* enabled modules
* provider/model registry
* local vs remote routing policy
* memory settings
* vector backend settings
* graph backend settings
* MCP/tool servers
* storage backends
* runtime mode
* policy flags

### 2. WorldMatrix

This defines what a particular world or scenario contains.

Examples:

* entities
* relationships
* rules
* knowledge boundaries
* branches
* scenarios
* initial conditions
* timeline state

This separation is essential. Platform capability must not be tightly fused to simulation content.

## Ingestion and reasoning strategy

PyScrAI should be **local-first** in ingestion.

Recommended principle:

* use local embedders and task-specific ML models first
* reserve higher-cost LLMs for semantic reasoning, contextual synthesis, ambiguity resolution, and agent-level cognition

Examples of local-first responsibilities:

* chunking
* embeddings
* entity extraction
* relation extraction
* candidate deduplication
* classification
* graph construction assistance

Examples of LLM-assisted responsibilities:

* semantic normalization
* contextual inference
* narrative synthesis
* policy-aware reasoning
* tool routing under ambiguity
* higher-order scenario interpretation

## Agent lab direction

Forge should eventually connect to a broader **agent lab**.

The agent lab should support:

* prompt experimentation
* provider comparison
* tool and MCP testing
* agent workflow evaluation
* scenario-specific agent prototypes
* observability and trace inspection
* future module and workflow incubation

Near-term, this does not need to be a polished native PyScrAI subsystem. It can be partially bootstrapped using external OSS tooling while Forge matures.

## Bootstrap stack recommendation

The recommended bootstrap stack is:

* **Forge shell:** Streamlit
* **Agent orchestration substrate:** Agent Zero
* **Provider bus:** LiteLLM
* **Providers:** OpenRouter + LM Studio
* **Temporary internal lab surface:** Open WebUI
* **Tracing / prompt management / eval:** Langfuse or Agenta
* **Regression testing:** Promptfoo
* **Local ingestion / KG pipeline:** custom PyScrAI subsystem

This gives PyScrAI a practical starting stack without forcing the final architecture prematurely.

## Backend stance

Do not hard-commit too early to the final persistence stack before the manifest and module contract exist.

Recommended near-term posture:

* use file-backed artifacts and/or SQLite where sufficient
* introduce vector storage only when needed for real workflows
* keep graph access behind an abstraction layer
* delay Redis unless real coordination or ephemeral state pressure appears
* delay a full database commitment until module boundaries and workload patterns are clearer

## First development moves

### Move 1 — stand up Forge as the shell

Create a minimal Streamlit shell with a few core sections:

* New Project / Open Project
* Goal Intake
* Recommended Modules
* Active Stack Summary
* Launch World Authoring
* Launch Runtime
* Agent Lab / Prompt Lab entry

This is not a polish task. It is a product-shape task.

### Move 2 — define the Project Manifest

Before adding many more systems, define the manifest contract.

Minimum initial sections:

* project metadata
* enabled modules
* provider registry
* routing policy
* storage backends
* vector config
* graph config
* MCP/tool server config
* memory config
* runtime profile
* policy flags

### Move 3 — add a simple module registry

Start with metadata and configuration contracts only.

Each module should declare:

* id
* name
* purpose
* dependencies
* config schema
* lifecycle hooks
* exposed UI surfaces
* artifact contracts

Avoid a fully dynamic plugin loader in the first pass.

### Move 4 — implement the architect agent in Forge

Use the Agent Zero for the initial interview/orchestration layer.

Its first duties:

* interpret operator intent
* recommend core modules
* draft the initial Project Manifest
* hand off into the existing setup/world-authoring flow

### Move 5 — wrap the current WorldMatrix flow

Do not rewrite the current setup/compile/branch pipeline immediately.

Treat it as subsystem A inside Forge.

### Move 6 — build the local-first ingestion subsystem next

Focus on:

* ingestion contracts
* local extractor routing
* embedding pipeline
* document/chunk registry
* candidate entity/relation pipeline
* graph handoff
* optional LLM escalation points

### Move 7 — defer major runtime redesign until boundaries are stable

The runtime should be redesigned only after Forge, the manifest, and the module boundaries are established.

## What not to do next

Avoid the following in the next cycle:

* polishing UI too early
* forcing a heavy plugin architecture before module contracts are stable
* overcommitting to one database stack prematurely
* tightly coupling project configuration to WorldMatrix content
* redesigning the runtime before the shell and manifest are defined
* assuming one OSS framework should become the whole platform

## Bottom line

The current repo is a real foundation, but it is too narrow to remain the top-level product shape.

The correct move is to place **PyScrAI Forge** above it, define the **Project Manifest**, preserve the current WorldMatrix flow as an internal subsystem, and bootstrap the broader agent-lab and local-first ingestion architecture around those boundaries.

That gives PyScrAI a disciplined MVP that can evolve into the broader AI sandbox, simulation, and agent laboratory vision without forcing premature commitments.
