from __future__ import annotations

from pyscrai.contracts.models import ModuleConfigContract, ModuleRegistryEntry


class StaticModuleRegistry:
    def __init__(self) -> None:
        self._entries = {
            entry.id: entry
            for entry in [
                ModuleRegistryEntry(
                    id="setup_session",
                    name="Setup Session",
                    purpose="Runs the architect-guided interview that frames the world before compile.",
                    config_contract=ModuleConfigContract(
                        manifest_sections=["providers", "routing_policy", "memory"],
                        required_provider_roles=["chat", "reasoning"],
                        enables_session_memory=True,
                    ),
                    lifecycle_hooks=["draft_manifest", "start_setup_session"],
                    ui_surfaces=["forge_goal_intake", "world_authoring"],
                    artifact_contracts=["project_manifest", "setup_session"],
                ),
                ModuleRegistryEntry(
                    id="worldmatrix_authoring",
                    name="WorldMatrix Authoring",
                    purpose="Captures setup outputs into the draft WorldMatrix authoring flow.",
                    dependencies=["setup_session"],
                    config_contract=ModuleConfigContract(
                        manifest_sections=["storage", "runtime_profile"],
                        required_provider_roles=["chat"],
                        runtime_modes=["authoring_only"],
                    ),
                    lifecycle_hooks=["launch_world_authoring", "persist_worldmatrix_draft"],
                    ui_surfaces=["world_authoring"],
                    artifact_contracts=["worldmatrix_draft"],
                ),
                ModuleRegistryEntry(
                    id="validation",
                    name="Validation",
                    purpose="Applies compile readiness checks and keeps unresolved items visible.",
                    dependencies=["worldmatrix_authoring"],
                    config_contract=ModuleConfigContract(
                        manifest_sections=["policies", "runtime_profile"],
                        required_provider_roles=["reasoning"],
                        runtime_modes=["authoring_only"],
                    ),
                    lifecycle_hooks=["validate_worldmatrix", "compile_worldmatrix"],
                    ui_surfaces=["world_authoring"],
                    artifact_contracts=["validation_summary", "provenance_manifest"],
                ),
                ModuleRegistryEntry(
                    id="scenario_runtime",
                    name="Scenario Runtime",
                    purpose="Creates branches, scenarios, and thin deterministic runtime test runs.",
                    dependencies=["validation"],
                    config_contract=ModuleConfigContract(
                        manifest_sections=["runtime_profile", "storage"],
                        runtime_modes=["authoring_and_runtime"],
                    ),
                    lifecycle_hooks=["create_branch", "create_scenario", "run_scenario"],
                    ui_surfaces=["runtime"],
                    artifact_contracts=["worldbranch", "scenario", "simulation_run"],
                ),
            ]
        }

    def list_modules(self) -> list[ModuleRegistryEntry]:
        return list(self._entries.values())

    def get(self, module_id: str) -> ModuleRegistryEntry:
        try:
            return self._entries[module_id]
        except KeyError as exc:
            raise ValueError(f"Unknown module id: {module_id}") from exc

    def resolve(self, module_ids: list[str]) -> list[ModuleRegistryEntry]:
        resolved: list[ModuleRegistryEntry] = []
        seen: set[str] = set()

        def add_module(module_id: str) -> None:
            if module_id in seen:
                return
            entry = self.get(module_id)
            for dependency_id in entry.dependencies:
                add_module(dependency_id)
            seen.add(module_id)
            resolved.append(entry)

        for module_id in module_ids:
            add_module(module_id)
        return resolved
