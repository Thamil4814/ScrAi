from __future__ import annotations

import re

from pyscrai.application.setup_mapper import SetupInterviewMapper
from pyscrai.contracts.models import (
    PendingQuestion,
    Project,
    ProjectBootstrapRequest,
    ProjectBootstrapResponse,
    ProjectCreateRequest,
    ProvenanceRecord,
    Scenario,
    ScenarioCreateRequest,
    SetupMessage,
    SetupMessageRequest,
    SetupSession,
    SetupSessionCreateRequest,
    SimulationRun,
    SimulationRunRequest,
    ValidationIssue,
    ValidationSummary,
    WorldBranch,
    WorldBranchCreateRequest,
    WorldMatrix,
    WorldMatrixDraft,
    WorldMatrixPayload,
)
from pyscrai.domain.enums import DomainType, ProjectStatus, ProvenanceKind, SessionPhase, ValidationState
from pyscrai.runtime.engine import ScenarioRuntimeEngine
from pyscrai.services.repository import ArtifactRepository


class ProjectService:
    TITLE_PREFIX_PATTERN = re.compile(r"^(build|create|make|generate|design)\s+(?:a|an|the)?\s*", re.IGNORECASE)
    DOMAIN_KEYWORDS: dict[DomainType, tuple[str, ...]] = {
        DomainType.GEOPOLITICAL: (
            "geopolitical",
            "diplomatic",
            "state",
            "military",
            "sanction",
            "proxy",
            "crisis",
            "embassy",
            "treaty",
        ),
        DomainType.SOCIAL: (
            "social",
            "friend",
            "family",
            "relationship",
            "workplace",
            "school",
            "community",
            "neighborhood",
        ),
        DomainType.HISTORICAL: (
            "historical",
            "history",
            "empire",
            "ancient",
            "medieval",
            "ww1",
            "ww2",
            "century",
        ),
        DomainType.FICTION: (
            "fiction",
            "fantasy",
            "sci-fi",
            "science fiction",
            "magic",
            "dragon",
            "space",
            "alien",
            "kingdom",
        ),
    }

    def __init__(self, repository: ArtifactRepository | None = None) -> None:
        self.repository = repository or ArtifactRepository()
        self.mapper = SetupInterviewMapper()
        self.runtime_engine = ScenarioRuntimeEngine()

    def create_project(self, request: ProjectCreateRequest) -> Project:
        project = Project(
            name=request.name,
            description=request.description,
            domain_type=request.domain_type,
            status=ProjectStatus.ACTIVE,
        )
        draft = WorldMatrixDraft(
            project_id=project.id,
            metadata={
                "title": request.name,
                "description": request.description,
                "author_operator": request.operator,
            },
            domain={
                "domain_type": request.domain_type,
            },
            provenance=[
                ProvenanceRecord(
                    kind=ProvenanceKind.OPERATOR_DEFINED,
                    source="project.create",
                    detail="Initial project framing supplied by operator.",
                    confidence=1.0,
                )
            ],
        )
        draft.validation = self.validate_draft_model(draft)
        draft.unresolved_items = self.compute_unresolved_items(draft)
        draft.validation_state = self.validation_state_for(draft.validation)
        self.repository.save_project(project)
        self.repository.save_draft(draft)
        return project

    def bootstrap_project(self, request: ProjectBootstrapRequest) -> ProjectBootstrapResponse:
        domain_type = request.domain_type_hint or self.infer_domain_type(request.prompt)
        project_name = request.name or self.project_name_from_prompt(request.prompt, domain_type)
        project = self.create_project(
            ProjectCreateRequest(
                name=project_name,
                description=request.prompt,
                domain_type=domain_type,
                operator=request.operator,
            )
        )
        if request.domain_type_hint is None:
            draft = self.repository.load_draft(project.id)
            draft.provenance.append(
                ProvenanceRecord(
                    kind=ProvenanceKind.MODEL_INFERRED,
                    source="bootstrap.domain_inference",
                    detail=f"Domain inferred as {domain_type}.",
                    confidence=0.6,
                )
            )
            self.repository.save_draft(draft)
        session = self.create_setup_session(project.id)
        session = self.add_setup_message(session.id, SetupMessageRequest(role="operator", content=request.prompt))
        draft = self.get_worldmatrix_draft(project.id)
        return ProjectBootstrapResponse(project=project, setup_session=session, draft=draft)

    def create_setup_session(self, project_id: str, request: SetupSessionCreateRequest | None = None) -> SetupSession:
        draft = self.repository.load_draft(project_id)
        session_phase = request.phase if request is not None else self.phase_for(draft)
        session = SetupSession(
            project_id=project_id,
            phase=session_phase,
            draft_worldmatrix_id=draft.id,
            pending_questions=self.build_pending_questions(draft, session_phase),
        )
        self._append_architect_follow_up(session, draft, captured_updates=[])
        self.repository.save_session(session)
        return session

    def add_setup_message(self, session_id: str, request: SetupMessageRequest) -> SetupSession:
        session = self.repository.load_session(session_id)
        draft = self.repository.load_draft(session.project_id)
        message = SetupMessage(role=request.role, content=request.content)
        session.transcript.append(message)

        if request.role == "operator":
            current_phase = session.phase
            mapping_result = self.mapper.apply_operator_message(draft, request.content, current_phase)
            draft.validation = self.validate_draft_model(draft)
            draft.unresolved_items = self.compute_unresolved_items(draft)
            draft.validation_state = self.validation_state_for(draft.validation)
            session.extracted_facts = mapping_result.extracted_facts
            session.phase = self.phase_for(draft)
            session.pending_questions = self.build_pending_questions(draft, session.phase)
            self._append_architect_follow_up(session, draft, mapping_result.captured_updates)
            self.repository.save_draft(draft)

        self.repository.save_session(session)
        return session

    def get_setup_session(self, session_id: str) -> SetupSession:
        return self.repository.load_session(session_id)

    def get_worldmatrix_draft(self, project_id: str) -> WorldMatrixDraft:
        draft = self.repository.load_draft(project_id)
        draft.validation = self.validate_draft_model(draft)
        draft.unresolved_items = self.compute_unresolved_items(draft)
        draft.validation_state = self.validation_state_for(draft.validation)
        self.repository.save_draft(draft)
        return draft

    def validate_worldmatrix_draft(self, project_id: str) -> ValidationSummary:
        draft = self.repository.load_draft(project_id)
        validation = self.validate_draft_model(draft)
        draft.validation = validation
        draft.unresolved_items = self.compute_unresolved_items(draft)
        draft.validation_state = self.validation_state_for(validation)
        self.repository.save_draft(draft)
        return validation

    def compile_worldmatrix(self, project_id: str) -> WorldMatrix:
        draft = self.repository.load_draft(project_id)
        validation = self.validate_draft_model(draft)
        if not validation.compile_readiness:
            raise ValueError("WorldMatrix draft is not ready to compile.")

        worldmatrix = WorldMatrix(
            project_id=project_id,
            version=draft.version,
            draft_source_id=draft.id,
            payload=WorldMatrixPayload(
                metadata=draft.metadata,
                domain=draft.domain,
                environment=draft.environment,
                entities=draft.entities,
                polities=draft.polities,
                relationships=draft.relationships,
                resources=draft.resources,
                rules=draft.rules,
                knowledge_layers=draft.knowledge_layers,
                operator_role=draft.operator_role,
                simulation_profile=draft.simulation_profile,
                provenance=draft.provenance,
                validation=validation,
            ),
            validation_report=validation,
            provenance_manifest=draft.provenance,
        )
        draft.validation = validation
        draft.unresolved_items = self.compute_unresolved_items(draft)
        draft.validation_state = ValidationState.COMPILED
        self.repository.save_draft(draft)
        self.repository.save_worldmatrix(worldmatrix)
        self.repository.update_project_status(project_id, ProjectStatus.COMPILED)
        return worldmatrix

    def get_worldmatrix(self, worldmatrix_id: str) -> WorldMatrix:
        return self.repository.load_worldmatrix(worldmatrix_id)

    def create_worldbranch(self, worldmatrix_id: str, request: WorldBranchCreateRequest) -> WorldBranch:
        worldmatrix = self.repository.load_worldmatrix(worldmatrix_id)
        branch = WorldBranch(
            worldmatrix_id=worldmatrix_id,
            parent_branch_id=request.parent_branch_id,
            title=request.title,
            modifications=request.modifications,
            initial_conditions=request.initial_conditions,
            branch_notes=request.branch_notes,
        )
        self.repository.save_worldbranch(worldmatrix.project_id, branch)
        return branch

    def create_scenario(self, branch_id: str, request: ScenarioCreateRequest) -> Scenario:
        branch = self.repository.load_worldbranch(branch_id)
        worldmatrix = self.repository.load_worldmatrix(branch.worldmatrix_id)
        scenario = Scenario(
            worldbranch_id=branch_id,
            runtime_profile=request.runtime_profile,
            actor_bindings=request.actor_bindings,
            initial_state=request.initial_state,
            stop_conditions=request.stop_conditions,
            evaluator_config=request.evaluator_config,
        )
        self.repository.save_scenario(worldmatrix.project_id, scenario)
        return scenario

    def get_scenario(self, scenario_id: str) -> Scenario:
        return self.repository.load_scenario(scenario_id)

    def run_scenario(self, scenario_id: str, request: SimulationRunRequest | None = None) -> SimulationRun:
        scenario = self.repository.load_scenario(scenario_id)
        branch = self.repository.load_worldbranch(scenario.worldbranch_id)
        worldmatrix = self.repository.load_worldmatrix(branch.worldmatrix_id)
        run = self.runtime_engine.run(scenario=scenario, branch=branch, worldmatrix=worldmatrix, request=request)
        self.repository.save_simulation_run(worldmatrix.project_id, run)
        return run

    def get_simulation_run(self, run_id: str) -> SimulationRun:
        return self.repository.load_simulation_run(run_id)

    def extract_facts(self, draft: WorldMatrixDraft) -> list[str]:
        return self.mapper.extract_facts(draft)

    @classmethod
    def infer_domain_type(cls, prompt: str) -> DomainType:
        lowered = prompt.casefold()
        best_domain = DomainType.HYBRID
        best_score = 0
        for domain_type, keywords in cls.DOMAIN_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in lowered)
            if score > best_score:
                best_domain = domain_type
                best_score = score
        return best_domain

    @staticmethod
    def project_name_from_prompt(prompt: str, domain_type: DomainType) -> str:
        trimmed = " ".join(prompt.split()).strip(" \"'")
        if not trimmed:
            return f"{domain_type.value.title()} World"
        trimmed = ProjectService.TITLE_PREFIX_PATTERN.sub("", trimmed)
        trimmed = trimmed.strip(" .!?")
        if not trimmed:
            return f"{domain_type.value.title()} World"
        if len(trimmed) <= 72:
            return trimmed
        return f"{trimmed[:69].rstrip()}..."

    def build_pending_questions(
        self,
        draft: WorldMatrixDraft,
        phase: SessionPhase | None = None,
    ) -> list[PendingQuestion]:
        active_phase = phase or self.phase_for(draft)
        questions: list[PendingQuestion] = []
        if active_phase == SessionPhase.INTENT_FRAMING and not draft.environment.description:
            questions.append(
                PendingQuestion(
                    prompt="What is the core environment or situation this world should model?",
                    rationale="The WorldMatrix cannot compile without a concrete world description.",
                )
            )
        if active_phase == SessionPhase.INTENT_FRAMING and draft.domain.time_scope == "unspecified":
            questions.append(
                PendingQuestion(
                    prompt="What time scope should govern this world?",
                    rationale="Scenario framing depends on an explicit temporal boundary.",
                )
            )
        if active_phase == SessionPhase.INTENT_FRAMING and draft.domain.spatial_scope == "unspecified":
            questions.append(
                PendingQuestion(
                    prompt="What locations or spatial boundaries matter for this simulation?",
                    rationale="The setup flow needs explicit spatial scope before scenario derivation.",
                )
            )
        if active_phase == SessionPhase.WORLD_POPULATION and not draft.entities:
            questions.append(
                PendingQuestion(
                    prompt="Who are the key actors or entities in this world?",
                    rationale="The setup flow needs named actors before scenario derivation can bind roles cleanly.",
                )
            )
        if active_phase == SessionPhase.WORLD_POPULATION and not draft.polities:
            questions.append(
                PendingQuestion(
                    prompt="Which polities, factions, or organizations matter most here?",
                    rationale="World population should include the major collective actors before rules are finalized.",
                )
            )
        if active_phase == SessionPhase.RULES_AND_KNOWLEDGE_BOUNDARIES and not draft.rules:
            questions.append(
                PendingQuestion(
                    prompt="What rules, constraints, or forbidden actions should govern the world?",
                    rationale="Validation should capture action boundaries before compile hardens the draft.",
                )
            )
        if (
            active_phase == SessionPhase.RULES_AND_KNOWLEDGE_BOUNDARIES
            and not draft.knowledge_layers.public_knowledge
        ):
            questions.append(
                PendingQuestion(
                    prompt="What should be public knowledge versus private or contested knowledge?",
                    rationale="The WorldMatrix should separate truth, public knowledge, and contested claims before compile.",
                )
            )
        if active_phase == SessionPhase.VALIDATION_PASS:
            if draft.domain.time_scope == "unspecified":
                questions.append(
                    PendingQuestion(
                        prompt="Do you want to lock an explicit time scope before compile?",
                        rationale="Time scope is still a validation warning and may affect scenario assumptions.",
                    )
                )
            if draft.domain.spatial_scope == "unspecified":
                questions.append(
                    PendingQuestion(
                        prompt="Do you want to lock an explicit spatial scope before compile?",
                        rationale="Spatial scope is still a validation warning and may affect scenario boundaries.",
                    )
                )
            if not questions:
                questions.append(
                    PendingQuestion(
                        prompt="The current draft is compile-ready. Do you want to compile now or refine any assumptions first?",
                        rationale="Validation should explicitly confirm the handoff from setup to compile.",
                    )
                )
        return questions

    def compute_unresolved_items(self, draft: WorldMatrixDraft) -> list[str]:
        unresolved: list[str] = []
        if draft.domain.time_scope == "unspecified":
            unresolved.append("time_scope")
        if draft.domain.spatial_scope == "unspecified":
            unresolved.append("spatial_scope")
        if not draft.environment.description:
            unresolved.append("environment.description")
        if not draft.entities:
            unresolved.append("entities")
        if not draft.polities:
            unresolved.append("polities")
        if not draft.rules:
            unresolved.append("rules")
        if not draft.knowledge_layers.public_knowledge:
            unresolved.append("knowledge_layers.public_knowledge")
        return unresolved

    def validate_draft_model(self, draft: WorldMatrixDraft) -> ValidationSummary:
        completeness = {
            "metadata": bool(draft.metadata.title and draft.metadata.description),
            "domain": bool(draft.domain.domain_type),
            "environment": bool(draft.environment.description),
            "operator_role": bool(draft.operator_role.mode),
        }
        issues: list[ValidationIssue] = []
        unresolved_blockers: list[str] = []
        warnings: list[str] = []

        if not completeness["environment"]:
            issues.append(
                ValidationIssue(
                    severity="blocker",
                    code="missing_environment",
                    message="Environment description is required before compile.",
                )
            )
            unresolved_blockers.append("environment.description")

        if not draft.entities:
            issues.append(
                ValidationIssue(
                    severity="blocker",
                    code="missing_entities",
                    message="At least one entity is required before compile.",
                )
            )
            unresolved_blockers.append("entities")

        if not draft.polities:
            issues.append(
                ValidationIssue(
                    severity="blocker",
                    code="missing_polities",
                    message="At least one polity is required before compile.",
                )
            )
            unresolved_blockers.append("polities")

        if not draft.rules:
            issues.append(
                ValidationIssue(
                    severity="blocker",
                    code="missing_rules",
                    message="At least one world rule or constraint is required before compile.",
                )
            )
            unresolved_blockers.append("rules")

        if not draft.knowledge_layers.public_knowledge:
            issues.append(
                ValidationIssue(
                    severity="blocker",
                    code="missing_public_knowledge",
                    message="Public knowledge must contain at least one claim before compile.",
                )
            )
            unresolved_blockers.append("knowledge_layers.public_knowledge")

        if draft.domain.time_scope == "unspecified":
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="missing_time_scope",
                    message="Time scope is still unspecified.",
                )
            )
            warnings.append("time_scope is unspecified")

        if draft.domain.spatial_scope == "unspecified":
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="missing_spatial_scope",
                    message="Spatial scope is still unspecified.",
                )
            )
            warnings.append("spatial_scope is unspecified")

        return ValidationSummary(
            required_section_completeness=completeness,
            unresolved_blockers=unresolved_blockers,
            warnings=warnings,
            compile_readiness=not unresolved_blockers,
            issues=issues,
        )

    @staticmethod
    def validation_state_for(validation: ValidationSummary) -> ValidationState:
        if validation.compile_readiness:
            return ValidationState.READY_TO_COMPILE
        return ValidationState.NEEDS_ATTENTION

    @staticmethod
    def phase_for(draft: WorldMatrixDraft) -> SessionPhase:
        if (
            not draft.environment.description
            or draft.domain.time_scope == "unspecified"
            or draft.domain.spatial_scope == "unspecified"
        ):
            return SessionPhase.INTENT_FRAMING
        if not draft.entities and not draft.polities:
            return SessionPhase.WORLD_POPULATION
        if not draft.rules or not draft.knowledge_layers.public_knowledge:
            return SessionPhase.RULES_AND_KNOWLEDGE_BOUNDARIES
        return SessionPhase.VALIDATION_PASS

    @staticmethod
    def _append_architect_follow_up(
        session: SetupSession,
        draft: WorldMatrixDraft,
        captured_updates: list[str],
    ) -> None:
        if session.pending_questions:
            next_question = session.pending_questions[0].prompt
        else:
            next_question = "The draft is ready for compile review."

        if captured_updates:
            summary = f"Captured {', '.join(captured_updates)}."
        elif draft.environment.description:
            summary = "Draft loaded."
        else:
            summary = "Starting setup."

        session.transcript.append(
            SetupMessage(
                role="architect",
                content=f"{summary} Next question: {next_question}",
            )
        )
