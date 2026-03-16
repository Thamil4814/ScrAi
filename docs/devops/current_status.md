# PyScrAI Milestone Implementation Plan

**Date:** 2026-03-16  
**Status:** Active Implementation  
**Source of Truth:** `docs/devops/pyscrai_blueprint.md`

## Executive Summary

The PyScrAI repository currently has a working vertical slice covering all 3 blueprint milestones in a thin scaffolded form. This plan outlines enhancements to deepen each milestone's implementation while preserving the existing architecture.

## Current State Assessment

### Milestone 1: World Setup Spine — COMPLETE (Enhancement Needed)
- ✅ Project creation with domain inference
- ✅ SetupSession with phase progression
- ✅ WorldMatrixDraft with live updates
- ✅ Deterministic interview mapper
- ⚠️ Missing: LLM-backed architect intelligence
- ⚠️ Missing: Richer question generation

### Milestone 2: Compile and Branch — SUBSTANTIALLY COMPLETE
- ✅ Draft validation with structured reports
- ✅ Compile produces WorldMatrix artifact
- ✅ WorldBranch creation
- ✅ Scenario creation
- ⚠️ Missing: Advanced validation rules
- ⚠️ Missing: Branch derivation intelligence

### Milestone 3: Runtime MVP — STARTED (Needs Enhancement)
- ✅ Basic deterministic turn loop
- ✅ Event logging and state snapshots
- ✅ Result summary with stability score
- ⚠️ Missing: Proper action validation against rules
- ⚠️ Missing: Knowledge layer enforcement
- ⚠️ Missing: Multi-agent decision making
- ⚠️ Missing: Trace viewer endpoint

## Implementation Plan

### Phase 1: Enhance Milestone 1 — World Setup Spine

**Goal:** Add LLM-backed architect intelligence while preserving deterministic fallback.

#### 1.1 Create Architect Orchestrator Service
- **File:** `packages/core/pyscrai/agents/orchestrator.py`
- **Purpose:** Role-scoped prompt management for architect roles
- **Features:**
  - Interview Architect: Generate contextual follow-up questions
  - Schema Architect: Map responses to WorldMatrix fields
  - Validation Architect: Check consistency and completeness

#### 1.2 Enhance Setup Interview Mapper
- **File:** `packages/core/pyscrai/application/setup_mapper.py`
- **Enhancements:**
  - Add LLM-backed entity extraction
  - Add relationship inference
  - Add goal/capability extraction for entities
  - Add resource inference

#### 1.3 Add LLM Adapter Layer
- **File:** `packages/core/pyscrai/adapters/llm/base.py`
- **Purpose:** Abstract LLM backend interface
- **Features:**
  - Support for OpenRouter API
  - Support for local models (Ollama/vLLM)
  - Structured output parsing
  - Token/cost tracking

### Phase 2: Enhance Milestone 2 — Compile and Branch

**Goal:** Add sophisticated validation and branch derivation intelligence.

#### 2.1 Enhanced Validation Engine
- **File:** `packages/core/pyscrai/application/validation.py`
- **Features:**
  - Cross-reference entity-polity relationships
  - Validate knowledge layer consistency
  - Check rule conflicts
  - Verify resource constraints
  - Assess simulation readiness

#### 2.2 Branch Derivation Intelligence
- **File:** `packages/core/pyscrai/application/branch_derivation.py`
- **Features:**
  - Suggest branch modifications based on WorldMatrix
  - Generate initial conditions from entities/polities
  - Propose scenario objectives
  - Create actor bindings automatically

#### 2.3 Scenario Template System
- **File:** `packages/core/pyscrai/application/scenario_templates.py`
- **Features:**
  - Pre-built scenario templates by domain type
  - Configurable stop conditions
  - Evaluator configuration presets
  - Runtime profile suggestions

### Phase 3: Enhance Milestone 3 — Runtime MVP

**Goal:** Transform smoke-test runtime into proper multi-agent simulation.

#### 3.1 Enhanced Runtime Engine
- **File:** `packages/core/pyscrai/runtime/engine.py` (rewrite)
- **Features:**
  - Proper action validation against rules
  - Knowledge layer enforcement per actor
  - State transition logic
  - Relationship-aware decision making
  - Resource consumption tracking

#### 3.2 Agent Decision System
- **File:** `packages/core/pyscrai/runtime/agents.py`
- **Features:**
  - Per-actor visible state calculation
  - Goal-directed action selection
  - Relationship influence on decisions
  - Knowledge-constrained reasoning

#### 3.3 Action Validation System
- **File:** `packages/core/pyscrai/runtime/validation.py`
- **Features:**
  - Rule-based action filtering
  - Forbidden action enforcement
  - Resource constraint checking
  - Relationship impact calculation

#### 3.4 Trace Viewer Endpoint
- **File:** `packages/core/pyscrai/interfaces/api.py` (add endpoint)
- **Endpoint:** `GET /runs/{run_id}/trace`
- **Features:**
  - Detailed turn-by-turn trace
  - Actor decision reasoning
  - State transition visualization
  - Provenance tracking

## Implementation Order

### Week 1: Milestone 1 Enhancements
1. Create LLM adapter layer
2. Create architect orchestrator service
3. Enhance setup mapper with LLM capabilities
4. Add fallback to deterministic behavior

### Week 2: Milestone 2 Enhancements
1. Create enhanced validation engine
2. Create branch derivation intelligence
3. Create scenario template system
4. Update API endpoints

### Week 3: Milestone 3 Enhancements
1. Rewrite runtime engine with proper validation
2. Create agent decision system
3. Create action validation system
4. Add trace viewer endpoint
5. Update tests

## Success Criteria

### Milestone 1 Success Criteria
- [ ] LLM-backed architect generates contextual questions
- [ ] Entity extraction includes goals and capabilities
- [ ] Relationship inference works from natural language
- [ ] Deterministic fallback works when LLM unavailable
- [ ] All existing tests pass

### Milestone 2 Success Criteria
- [ ] Validation catches cross-reference inconsistencies
- [ ] Branch derivation suggests relevant modifications
- [ ] Scenario templates reduce manual configuration
- [ ] Compile produces richer WorldMatrix artifacts
- [ ] All existing tests pass

### Milestone 3 Success Criteria
- [ ] Actions validated against rules before execution
- [ ] Each actor sees only their knowledge layer
- [ ] State transitions follow defined rules
- [ ] Trace viewer shows detailed execution
- [ ] All existing tests pass
- [ ] New tests cover enhanced functionality

## Risk Mitigation

### Risk: LLM Integration Complexity
- **Mitigation:** Maintain deterministic fallback for all LLM features
- **Mitigation:** Use structured output parsing with validation
- **Mitigation:** Add comprehensive error handling

### Risk: Breaking Existing Functionality
- **Mitigation:** All enhancements are additive, not replacements
- **Mitigation:** Run full test suite after each change
- **Mitigation:** Preserve existing API contracts

### Risk: Performance Degradation
- **Mitigation:** Cache LLM responses where appropriate
- **Mitigation:** Use async operations for LLM calls
- **Mitigation:** Add performance monitoring

## Documentation Updates

### Files to Update
- `docs/devops/current_status.md` — Update milestone status
- `docs/devops/changelog.md` — Add implementation notes
- `docs/devops/issues_comments.md` — Track any issues encountered
- `README.md` — Update with new features

### New Documentation
- `docs/devops/architect_roles.md` — Document architect role system
- `docs/devops/runtime_guide.md` — Document runtime behavior
- `docs/devops/validation_rules.md` — Document validation logic