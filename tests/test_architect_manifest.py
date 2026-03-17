from pyscrai.application.architect_manifest import (
    ArchitectManifestService,
    HeuristicArchitectAgentAdapter,
)
from pyscrai.contracts.models import Project
from pyscrai.domain.enums import DomainType


def _service() -> ArchitectManifestService:
    adapter = HeuristicArchitectAgentAdapter()
    return ArchitectManifestService(adapter=adapter, fallback_adapter=adapter)


def test_manifest_drafting_is_deterministic_for_simulation_goals() -> None:
    project = Project(
        name="Gulf crisis rehearsal",
        description="Build a near-future Gulf crisis simulation in the Persian Gulf.",
        domain_type=DomainType.GEOPOLITICAL,
    )

    response = _service().draft_manifest(project, project.description)
    payload = response.manifest_draft.payload

    assert [module.id for module in response.selected_modules] == [
        "setup_session",
        "worldmatrix_authoring",
        "validation",
        "scenario_runtime",
    ]
    assert payload.enabled_modules == [
        "setup_session",
        "worldmatrix_authoring",
        "validation",
        "scenario_runtime",
    ]
    assert payload.providers.defaults.chat == "lmstudio/default-chat"
    assert payload.providers.defaults.reasoning == "openrouter/default-reasoning"
    assert payload.routing_policy.default_route == "local"
    assert payload.routing_policy.allow_remote_reasoning is True
    assert payload.runtime_profile.mode == "authoring_and_runtime"


def test_manifest_drafting_is_deterministic_for_local_only_goals() -> None:
    project = Project(
        name="Offline fiction authoring",
        description="Create an offline, local only fantasy world authoring workspace.",
        domain_type=DomainType.FICTION,
    )

    response = _service().draft_manifest(project, project.description)
    payload = response.manifest_draft.payload

    assert [module.id for module in response.selected_modules] == [
        "setup_session",
        "worldmatrix_authoring",
        "validation",
    ]
    assert payload.providers.defaults.reasoning == "lmstudio/default-reasoning"
    assert payload.routing_policy.default_route == "local"
    assert payload.routing_policy.allow_remote_reasoning is False
    assert payload.providers.registry[0].id == "openrouter"
    assert payload.providers.registry[0].enabled is False
    assert payload.runtime_profile.mode == "authoring_only"
