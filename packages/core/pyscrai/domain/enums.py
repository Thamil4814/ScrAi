from enum import StrEnum


class DomainType(StrEnum):
    FICTION = "fiction"
    GEOPOLITICAL = "geopolitical"
    SOCIAL = "social"
    HISTORICAL = "historical"
    HYBRID = "hybrid"


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPILED = "compiled"


class SessionPhase(StrEnum):
    BOOTSTRAP = "bootstrap"
    INTENT_FRAMING = "intent_framing"
    ONTOLOGY_SELECTION = "ontology_selection"
    WORLD_POPULATION = "world_population"
    RULES_AND_KNOWLEDGE_BOUNDARIES = "rules_and_knowledge_boundaries"
    VALIDATION_PASS = "validation_pass"
    COMPILE = "compile"
    BRANCH_SCENARIO_AUTHORING = "branch_scenario_authoring"
    RUNTIME_INSTANTIATION = "runtime_instantiation"


class SessionStatus(StrEnum):
    ACTIVE = "active"
    COMPLETE = "complete"


class ValidationState(StrEnum):
    DRAFT = "draft"
    NEEDS_ATTENTION = "needs_attention"
    READY_TO_COMPILE = "ready_to_compile"
    COMPILED = "compiled"


class OperatorMode(StrEnum):
    OBSERVER = "observer"
    ENTITY_POSSESSION = "entity_possession"
    POLITY_POSSESSION = "polity_possession"
    ZEUS = "zeus"
    DIRECTOR = "director"


class ProvenanceKind(StrEnum):
    OPERATOR_DEFINED = "operator_defined"
    INGESTED_SOURCE = "ingested_source"
    MODEL_INFERRED = "model_inferred"
    CONTESTED = "contested"
    UNRESOLVED = "unresolved"
