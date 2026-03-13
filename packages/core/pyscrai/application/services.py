from __future__ import annotations

from pyscrai.application.setup_mapper import SetupInterviewMapper
from pyscrai.contracts.models import (
    PendingQuestion,
    Project,
    ProjectCreateRequest,
    ProvenanceRecord,
    SetupMessage,
    SetupMessageRequest,
    SetupSession,
    SetupSessionCreateRequest,
    ValidationIssue,
    ValidationSummary,
    WorldMatrix,
    WorldMatrixDraft,
    WorldMatrixPayload,
)
from pyscrai.domain.enums import ProjectStatus, ProvenanceKind, SessionPhase, ValidationState
from pyscrai.services.repository import ArtifactRepository


class ProjectService:
    def __init__(self, repository: ArtifactRepository | None = None) -> None:
        self.repository = repository or ArtifactRepository()
        self.mapper = SetupInterviewMapper()

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

    def create_setup_session(self, project_id: str, request: SetupSessionCreateRequest | None = None) -> SetupSession:
        draft = self.repository.load_draft(project_id)
        session_phase = request.phase if request is not None else self.phase_for(draft)
        session = SetupSession(
            project_id=project_id,
            phase=session_phase,
            draft_worldmatrix_id=draft.id,
            pending_questions=self.build_pending_questions(draft),
        )
        self.repository.save_session(session)
        return session

    def add_setup_message(self, session_id: str, request: SetupMessageRequest) -> SetupSession:
        session = self.repository.load_session(session_id)
        draft = self.repository.load_draft(session.project_id)
        message = SetupMessage(role=request.role, content=request.content)
        session.transcript.append(message)

        if request.role == "operator":
            mapping_result = self.mapper.apply_operator_message(draft, request.content)
            draft.validation = self.validate_draft_model(draft)
            draft.unresolved_items = self.compute_unresolved_items(draft)
            draft.validation_state = self.validation_state_for(draft.validation)
            session.extracted_facts = mapping_result.extracted_facts
            session.phase = self.phase_for(draft)
            session.pending_questions = self.build_pending_questions(draft)
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

    def extract_facts(self, draft: WorldMatrixDraft) -> list[str]:
        return self.mapper.extract_facts(draft)

    def build_pending_questions(self, draft: WorldMatrixDraft) -> list[PendingQuestion]:
        questions: list[PendingQuestion] = []
        if not draft.environment.description:
            questions.append(
                PendingQuestion(
                    prompt="What is the core environment or situation this world should model?",
                    rationale="The WorldMatrix cannot compile without a concrete world description.",
                )
            )
        if draft.domain.time_scope == "unspecified":
            questions.append(
                PendingQuestion(
                    prompt="What time scope should govern this world?",
                    rationale="Scenario framing depends on an explicit temporal boundary.",
                )
            )
        if draft.domain.spatial_scope == "unspecified":
            questions.append(
                PendingQuestion(
                    prompt="What locations or spatial boundaries matter for this simulation?",
                    rationale="The setup flow needs explicit spatial scope before scenario derivation.",
                )
            )
        if not draft.entities and not draft.polities:
            questions.append(
                PendingQuestion(
                    prompt="Who are the key actors, entities, or polities in this world?",
                    rationale="Scenario authoring needs a first pass of participants before branching or runtime work.",
                )
            )
        if not draft.rules:
            questions.append(
                PendingQuestion(
                    prompt="What rules, constraints, or forbidden actions should govern the world?",
                    rationale="Validation should capture action boundaries before compile hardens the draft.",
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
        if not draft.environment.description:
            return SessionPhase.INTENT_FRAMING
        if not draft.entities and not draft.polities:
            return SessionPhase.WORLD_POPULATION
        if not draft.rules:
            return SessionPhase.RULES_AND_KNOWLEDGE_BOUNDARIES
        return SessionPhase.VALIDATION_PASS
