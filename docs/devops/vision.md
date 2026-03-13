# PyScrAI Vision

**Status:** Product vision and architectural principles. This document is non-normative wherever `pyscrai_blueprint.md` defines concrete contracts, schemas, routes, state transitions, or milestone sequencing.

## Product Thesis

PyScrAI is a human-in-the-loop, architect-guided world-authoring platform for agentic simulation.

Its purpose is not merely to scrape data, manage documents, or host a sandbox UI. Its purpose is to guide an operator from an initial high-level concept into a structured, validated world representation that can be turned into runnable scenarios for a multi-agent runtime.

The central artifact of the system is the **WorldMatrix**.

PyScrAI should help an operator:

1. describe a world, situation, or social space in natural language,
2. refine that world through a guided setup interview,
3. ingest supporting material where useful,
4. translate that information into structured simulation-grade state,
5. validate the resulting world for consistency and readiness,
6. derive scenarios or branches from that world,
7. instantiate those artifacts into a runtime for testing and execution.

## Core Principle

PyScrAI must be **HIL-first, not HIL-later**.

The operator is not a passive source of input and not merely a reviewer of model output. The operator is an active co-author of the world. From the first step, the system should function as a structured design partner that interviews, clarifies, proposes, validates, and compiles.

That means the primary abstraction is not:

> ingest first, review later

It is:

> conduct guided world formation through an interactive interview while progressively compiling a WorldMatrix.

## Forge as World Authoring

Forge should begin as an interactive world-authoring system, not a scrape-first ingestion tool with human review layered on later.

The setup process should behave like a collaborative design session with three tracks happening in parallel:

* the operator speaks in natural language,
* architect agents interpret and clarify,
* the system writes structured state into the evolving WorldMatrix.

This is the correct foundation because it:

* keeps the operator in control from the beginning,
* reduces ontology drift,
* supports incomplete or ambiguous source material,
* allows targeted ingestion rather than indiscriminate ingestion,
* naturally supports role configuration, possession modes, and authority boundaries.

## WorldMatrix-First

The WorldMatrix should be treated as a structured substrate for simulation rather than a passive file.

It should be capable of representing at minimum:

* metadata and domain framing,
* environment and spatial scope,
* entities and polities,
* relationships,
* resources and values,
* rules and constraints,
* knowledge visibility layers,
* operator role bindings and permissions,
* provenance and uncertainty,
* validation status,
* scenario hooks or branch points.

The WorldMatrix should be built incrementally during setup. The operator should be able to see it taking shape as they answer questions and refine assumptions.

## Guided Setup, Not Flat Intake

World setup should be progressive rather than flat.

The system should begin with broad framing questions, propose an initial world skeleton, ask increasingly specific follow-up questions based on that skeleton, and update the WorldMatrix continuously.

This is preferable to static forms or front-loaded questionnaires because it allows the ontology, interview path, and level of detail to adapt to the actual world being built.

A fictional setting, a geopolitical crisis model, and a three-person social simulation should not all ask the same setup questions or use the same emphasis.

## Agentic by Default

PyScrAI should be architected as an agentic system from the beginning, even if the MVP initially uses one orchestrator model with role-scoped outputs.

The important behavior is that the system acts like a small architect council with separable responsibilities, such as:

* interview guidance,
* schema mapping,
* consistency checking,
* ingestion and source handling,
* authority and role modeling,
* compile and validation tracking,
* runtime translation.

These roles do not all need to be separate infrastructure services on day one, but the conceptual separation should be preserved because it keeps the design extensible and prevents a single monolithic prompt from owning every concern.

## Truth, Belief, and Authority Separation

One of the non-negotiable conceptual boundaries in PyScrAI is that the system must distinguish between:

* world truth,
* entity belief,
* faction or polity knowledge,
* operator visibility,
* operator permissions,
* simulation authority state.

Without these boundaries, possession mode becomes ambiguous, omniscience leaks into bounded play, and the simulation loses integrity.

This separation is especially important for:

* entity possession,
* polity possession,
* observer mode,
* Zeus mode,
* any future director or scenario-editing mode.

## Structured Uncertainty

The system should preserve uncertainty explicitly rather than forcing premature canon.

World elements may originate from:

* operator-authored canon,
* ingested source evidence,
* model inference,
* contested claims,
* placeholders,
* unresolved hypotheses.

These should remain structurally visible. PyScrAI should favor traceable ambiguity over false certainty.

## Targeted Ingestion

Ingestion remains important, but it should be subordinate to world modeling.

The system should first determine what kind of world is being built, who the relevant actors are, what the scope is, what truth model applies, and what the operator wants to control.

Only then should ingestion be routed to gather or structure the most relevant supporting information.

This means PyScrAI should prefer:

* targeted source acquisition,
* scoped extraction,
* provenance-aware synthesis,
* confirmation of important assumptions,

rather than broad scraping followed by attempted reconstruction of the intended world.

## MVP Philosophy

The first version should prove the full end-to-end loop rather than overbuilding any single subsystem.

The MVP should be narrow, but complete enough to show:

* project creation from a high-level prompt,
* guided interview and setup,
* live WorldMatrix drafting,
* validation and compile,
* scenario or branch derivation,
* runtime instantiation,
* a basic multi-agent execution trace.

The system does not need a massive scraping surface, a broad GUI workbench, or a deep persistent simulation in order to prove the architecture.

## Platform Direction

PyScrAI should assume a Linux-first development and runtime environment, with WSL2 Ubuntu as the immediate baseline.

Paths, scripts, tooling, local services, packaging assumptions, and startup flows should reflect that baseline directly.

## Document Roles

This file defines the product vision, architectural intent, and non-negotiable conceptual boundaries for PyScrAI.

The implementation source of truth for the MVP is:

* `pyscrai_blueprint.md`

That blueprint should govern:

* concrete object models,
* schema definitions,
* API routes,
* setup-state transitions,
* repository structure,
* milestone sequencing,
* runtime MVP scope.

When this vision document and the blueprint differ in implementation detail, the blueprint wins.

## Final Direction

PyScrAI should be built as a guided world-authoring and scenario-instantiation platform centered on the WorldMatrix.

Its defining characteristic is not that it can scrape or simulate in isolation, but that it can help an operator move from vague intent to structured world construction to runnable agentic execution with clarity, control, and traceable assumptions.
