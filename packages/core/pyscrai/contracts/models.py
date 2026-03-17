from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from pyscrai.domain.enums import (
    DomainType,
    OperatorMode,
    ProjectStatus,
    ProvenanceKind,
    SessionPhase,
    SessionStatus,
    ValidationState,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


class ModelBase(BaseModel):
    model_config = {"use_enum_values": True}


class ProjectCreateRequest(ModelBase):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    domain_type: DomainType
    operator: str | None = None


class ProjectBootstrapRequest(ModelBase):
    prompt: str = Field(min_length=1)
    operator: str | None = None
    name: str | None = None
    domain_type_hint: DomainType | None = None


class SetupSessionCreateRequest(ModelBase):
    phase: SessionPhase = SessionPhase.INTENT_FRAMING


class SetupMessageRequest(ModelBase):
    role: Literal["operator", "architect"] = "operator"
    content: str = Field(min_length=1)


class ValidationIssue(ModelBase):
    severity: Literal["warning", "blocker"]
    code: str
    message: str


class ValidationSummary(ModelBase):
    required_section_completeness: dict[str, bool] = Field(default_factory=dict)
    unresolved_blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    compile_readiness: bool = False
    issues: list[ValidationIssue] = Field(default_factory=list)


class ProvenanceRecord(ModelBase):
    kind: ProvenanceKind
    source: str
    detail: str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    recorded_at: datetime = Field(default_factory=utc_now)


class CompileMetadata(ModelBase):
    compatibility_version: str = "worldmatrix.v1"
    compiled_at: datetime | None = None


class MetadataProfile(ModelBase):
    title: str
    description: str
    author_operator: str | None = None
    version: int = 1
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class DomainProfile(ModelBase):
    domain_type: DomainType
    ontology_pack: str = "baseline"
    time_scope: str = "unspecified"
    spatial_scope: str = "unspecified"
    realism_mode: str = "mixed"


class EnvironmentProfile(ModelBase):
    description: str = ""
    locations: list[str] = Field(default_factory=list)
    environmental_attributes: list[str] = Field(default_factory=list)
    macro_conditions: list[str] = Field(default_factory=list)


class Entity(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    type: str
    description: str = ""
    goals: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    affiliations: list[str] = Field(default_factory=list)
    visible_knowledge_refs: list[str] = Field(default_factory=list)
    hidden_state: dict[str, str] = Field(default_factory=dict)


class Polity(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    category: str
    leadership: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    objectives: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class Relationship(ModelBase):
    source: str
    target: str
    type: str
    strength: float = 0.5
    alignment: str = "neutral"
    provenance: list[ProvenanceRecord] = Field(default_factory=list)


class Resource(ModelBase):
    owner: str
    resource_type: str
    quantity_or_value: str
    access_constraints: list[str] = Field(default_factory=list)


class Rule(ModelBase):
    category: str
    description: str
    forbidden_actions: list[str] = Field(default_factory=list)
    trigger_rules: list[str] = Field(default_factory=list)


class KnowledgeLayers(ModelBase):
    world_truth: list[str] = Field(default_factory=list)
    public_knowledge: list[str] = Field(default_factory=list)
    polity_private: dict[str, list[str]] = Field(default_factory=dict)
    entity_private: dict[str, list[str]] = Field(default_factory=dict)
    contested_claims: list[str] = Field(default_factory=list)
    operator_visibility: list[str] = Field(
        default_factory=lambda: ["world_truth", "public_knowledge"]
    )


class OperatorRole(ModelBase):
    mode: OperatorMode = OperatorMode.OBSERVER
    bindings: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(
        default_factory=lambda: ["view_worldmatrix", "compile_worldmatrix"]
    )
    visibility_scope: list[str] = Field(
        default_factory=lambda: ["world_truth", "public_knowledge"]
    )


class SimulationProfile(ModelBase):
    simulation_style: str = "turn_based"
    turn_cadence: str = "discrete"
    branching_policy: str = "manual"
    abstraction_level: str = "mvp"
    evaluation_mode: str = "qualitative"


class WorldBranchCreateRequest(ModelBase):
    title: str = Field(min_length=1)
    parent_branch_id: str | None = None
    modifications: list[str] = Field(default_factory=list)
    initial_conditions: list[str] = Field(default_factory=list)
    branch_notes: str = ""


class ScenarioCreateRequest(ModelBase):
    runtime_profile: SimulationProfile = Field(default_factory=SimulationProfile)
    actor_bindings: dict[str, str] = Field(default_factory=dict)
    initial_state: dict[str, str] = Field(default_factory=dict)
    stop_conditions: list[str] = Field(default_factory=list)
    evaluator_config: dict[str, str] = Field(default_factory=dict)


class SimulationRunRequest(ModelBase):
    turn_limit: int | None = Field(default=None, ge=1, le=50)
    objective: str = "stability_probe"
    inject_events: list[str] = Field(default_factory=list)


class WorldMatrixPayload(ModelBase):
    metadata: MetadataProfile
    domain: DomainProfile
    environment: EnvironmentProfile = Field(default_factory=EnvironmentProfile)
    entities: list[Entity] = Field(default_factory=list)
    polities: list[Polity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    resources: list[Resource] = Field(default_factory=list)
    rules: list[Rule] = Field(default_factory=list)
    knowledge_layers: KnowledgeLayers = Field(default_factory=KnowledgeLayers)
    operator_role: OperatorRole = Field(default_factory=OperatorRole)
    simulation_profile: SimulationProfile = Field(default_factory=SimulationProfile)
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
    validation: ValidationSummary = Field(default_factory=ValidationSummary)


class Project(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    domain_type: DomainType
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    status: ProjectStatus = ProjectStatus.DRAFT


class ManifestMetadata(ModelBase):
    project_id: str
    name: str
    description: str
    created_by: str | None = None
    domain_type: DomainType
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ManifestProviderDefaults(ModelBase):
    chat: str = "lmstudio/default-chat"
    reasoning: str = "openrouter/default-reasoning"
    embedding: str = "lmstudio/default-embedding"


class ManifestProviderRegistryEntry(ModelBase):
    id: str
    provider: str
    transport: Literal["local", "remote"]
    enabled: bool = True
    base_url: str | None = None
    models: list[str] = Field(default_factory=list)


class ManifestProviders(ModelBase):
    provider_bus: str = "litellm"
    registry: list[ManifestProviderRegistryEntry] = Field(
        default_factory=lambda: [
            ManifestProviderRegistryEntry(
                id="openrouter",
                provider="openrouter",
                transport="remote",
                models=["default-chat", "default-reasoning"],
            ),
            ManifestProviderRegistryEntry(
                id="lmstudio",
                provider="lmstudio",
                transport="local",
                base_url="http://127.0.0.1:1234",
                models=["default-chat", "default-embedding"],
            ),
        ]
    )
    defaults: ManifestProviderDefaults = Field(default_factory=ManifestProviderDefaults)


class ManifestRoutingPolicy(ModelBase):
    local_first: bool = True
    default_route: Literal["local", "remote"] = "local"
    allow_remote_reasoning: bool = True
    allow_remote_ingestion_assist: bool = True
    fallback_order: list[str] = Field(
        default_factory=lambda: ["lmstudio", "openrouter"]
    )


class ManifestStorage(ModelBase):
    artifact_backend: str = "local_fs"
    artifact_root: str = "artifacts/projects"
    relational_backend: str = "sqlite"
    relational_dsn: str = "sqlite:///artifacts/projects/pyscrai.db"


class ManifestVectors(ModelBase):
    enabled: bool = False
    backend: str | None = None
    collection: str | None = None


class ManifestGraph(ModelBase):
    enabled: bool = False
    backend: str | None = None
    namespace: str | None = None


class ManifestMCPServer(ModelBase):
    id: str
    transport: Literal["stdio", "http"]
    enabled: bool = True
    command: str | None = None
    url: str | None = None


class ManifestMemory(ModelBase):
    session_enabled: bool = True
    long_term_enabled: bool = False
    retrieval_enabled: bool = False


class ManifestRuntimeProfile(ModelBase):
    mode: str = "authoring_only"
    default_surface: str = "world_authoring"
    trace_enabled: bool = True


class ManifestPolicies(ModelBase):
    operator_approval_required: bool = True
    allow_auto_scaffold: bool = False


class ProjectManifestPayload(ModelBase):
    metadata: ManifestMetadata
    enabled_modules: list[str] = Field(
        default_factory=lambda: [
            "setup_session",
            "worldmatrix_authoring",
            "validation",
            "scenario_runtime",
        ]
    )
    providers: ManifestProviders = Field(default_factory=ManifestProviders)
    routing_policy: ManifestRoutingPolicy = Field(default_factory=ManifestRoutingPolicy)
    storage: ManifestStorage = Field(default_factory=ManifestStorage)
    vectors: ManifestVectors = Field(default_factory=ManifestVectors)
    graph: ManifestGraph = Field(default_factory=ManifestGraph)
    mcp_servers: list[ManifestMCPServer] = Field(default_factory=list)
    memory: ManifestMemory = Field(default_factory=ManifestMemory)
    runtime_profile: ManifestRuntimeProfile = Field(
        default_factory=ManifestRuntimeProfile
    )
    policies: ManifestPolicies = Field(default_factory=ManifestPolicies)


class ProjectManifestDraft(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    version: int = 1
    compatibility_version: str = "project_manifest.v1"
    payload: ProjectManifestPayload


class ProjectManifest(ProjectManifestDraft):
    compiled_at: datetime = Field(default_factory=utc_now)


class PendingQuestion(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    prompt: str
    rationale: str


class SetupMessage(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: Literal["operator", "architect"]
    content: str
    created_at: datetime = Field(default_factory=utc_now)


class SetupSession(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    phase: SessionPhase = SessionPhase.INTENT_FRAMING
    transcript: list[SetupMessage] = Field(default_factory=list)
    extracted_facts: list[str] = Field(default_factory=list)
    pending_questions: list[PendingQuestion] = Field(default_factory=list)
    draft_worldmatrix_id: str
    status: SessionStatus = SessionStatus.ACTIVE


class WorldMatrixDraft(WorldMatrixPayload):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    version: int = 1
    unresolved_items: list[str] = Field(default_factory=list)
    validation_state: ValidationState = ValidationState.DRAFT


class ProjectBootstrapResponse(ModelBase):
    project: Project
    manifest_draft: ProjectManifestDraft
    setup_session: SetupSession
    draft: WorldMatrixDraft


class WorldMatrix(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    version: int = 1
    draft_source_id: str
    compiled_at: datetime = Field(default_factory=utc_now)
    compatibility_version: str = "worldmatrix.v1"
    payload: WorldMatrixPayload
    validation_report: ValidationSummary
    provenance_manifest: list[ProvenanceRecord] = Field(default_factory=list)


class WorldBranch(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    worldmatrix_id: str
    parent_branch_id: str | None = None
    title: str
    modifications: list[str] = Field(default_factory=list)
    initial_conditions: list[str] = Field(default_factory=list)
    branch_notes: str = ""


class Scenario(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    worldbranch_id: str
    runtime_profile: SimulationProfile = Field(default_factory=SimulationProfile)
    actor_bindings: dict[str, str] = Field(default_factory=dict)
    initial_state: dict[str, str] = Field(default_factory=dict)
    stop_conditions: list[str] = Field(default_factory=list)
    evaluator_config: dict[str, str] = Field(default_factory=dict)


class SimulationRun(ModelBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    scenario_id: str
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    runtime_trace: list[dict[str, str]] = Field(default_factory=list)
    event_log: list[dict[str, str]] = Field(default_factory=list)
    state_snapshots: list[dict[str, str]] = Field(default_factory=list)
    result_summary: dict[str, str] = Field(default_factory=dict)
