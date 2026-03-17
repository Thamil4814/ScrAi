from __future__ import annotations

import json
import os
from typing import Protocol

from pyscrai.application.module_registry import StaticModuleRegistry
from pyscrai.contracts.models import (
    ArchitectManifestDraftRequest,
    ArchitectManifestDraftResponse,
    ArchitectManifestRecommendation,
    ArchitectModuleSelection,
    ManifestGraph,
    ManifestMemory,
    ManifestMetadata,
    ManifestPolicies,
    ManifestProviderDefaults,
    ManifestProviderRegistryEntry,
    ManifestProviders,
    ManifestRoutingPolicy,
    ManifestRuntimeProfile,
    ManifestStorage,
    ManifestVectors,
    ModuleRegistryEntry,
    Project,
    ProjectManifestDraft,
    ProjectManifestPayload,
)


class ArchitectAgentAdapter(Protocol):
    def recommend_manifest(
        self,
        request: ArchitectManifestDraftRequest,
        available_modules: list[ModuleRegistryEntry],
    ) -> ArchitectManifestRecommendation: ...


class HeuristicArchitectAgentAdapter:
    AUTHORING_MODULES = ["setup_session", "worldmatrix_authoring", "validation"]
    RUNTIME_KEYWORDS = (
        "scenario",
        "simulation",
        "runtime",
        "test run",
        "wargame",
        "exercise",
    )
    LOCAL_ONLY_KEYWORDS = (
        "local only",
        "local-first only",
        "offline",
        "air-gapped",
        "airgapped",
        "on-device",
    )

    def recommend_manifest(
        self,
        request: ArchitectManifestDraftRequest,
        available_modules: list[ModuleRegistryEntry],
    ) -> ArchitectManifestRecommendation:
        del available_modules
        goal = " ".join(request.goal.split())
        lowered = goal.casefold()
        module_ids = list(self.AUTHORING_MODULES)
        notes = [
            "Drafted the manifest from the goal against the static internal module registry."
        ]

        if any(keyword in lowered for keyword in self.RUNTIME_KEYWORDS):
            module_ids.append("scenario_runtime")
            notes.append("Enabled scenario runtime because the goal implies executable scenarios.")

        local_only = any(keyword in lowered for keyword in self.LOCAL_ONLY_KEYWORDS)
        if local_only:
            notes.append("Pinned routing to local execution because the goal asks for local-only operation.")

        module_selections = [
            ArchitectModuleSelection(
                module_id=module_id,
                rationale=self._module_rationale(module_id, "scenario_runtime" in module_ids),
            )
            for module_id in module_ids
        ]
        return ArchitectManifestRecommendation(
            goal_summary=self._summarize_goal(goal),
            module_selections=module_selections,
            chat_provider_id="lmstudio",
            reasoning_provider_id="lmstudio" if local_only else "openrouter",
            embedding_provider_id="lmstudio",
            default_route="local",
            allow_remote_reasoning=not local_only,
            allow_remote_ingestion_assist=not local_only,
            artifact_backend="local_fs",
            relational_backend="sqlite",
            operator_approval_required=True,
            allow_auto_scaffold=False,
            notes=notes,
            open_questions=[],
            draft_source="heuristic_fallback",
        )

    @staticmethod
    def _summarize_goal(goal: str) -> str:
        if len(goal) <= 140:
            return goal
        return f"{goal[:137].rstrip()}..."

    @staticmethod
    def _module_rationale(module_id: str, runtime_enabled: bool) -> str:
        rationales = {
            "setup_session": "Needed to preserve the architect-guided setup interview before world authoring.",
            "worldmatrix_authoring": "Needed to carry approved manifest decisions into the existing WorldMatrix draft flow.",
            "validation": "Needed to keep compile-readiness and unresolved items explicit in the authoring path.",
            "scenario_runtime": (
                "Needed because the goal mentions scenario execution beyond authoring."
                if runtime_enabled
                else "Available for later runtime expansion."
            ),
        }
        return rationales[module_id]


class OpenAICompatibleArchitectAgentAdapter:
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.model = model or os.getenv("PYSCRAI_ARCHITECT_MODEL")
        self.base_url = base_url or os.getenv("PYSCRAI_ARCHITECT_BASE_URL")
        self.api_key = api_key if api_key is not None else os.getenv(
            "PYSCRAI_ARCHITECT_API_KEY"
        )

    def recommend_manifest(
        self,
        request: ArchitectManifestDraftRequest,
        available_modules: list[ModuleRegistryEntry],
    ) -> ArchitectManifestRecommendation:
        if not self.model:
            raise RuntimeError("PYSCRAI_ARCHITECT_MODEL is not configured.")
        if not self.base_url:
            raise RuntimeError("PYSCRAI_ARCHITECT_BASE_URL is not configured.")

        from agents import Agent, ModelSettings, OpenAIProvider, RunConfig, Runner

        provider = OpenAIProvider(
            api_key=self.api_key,
            base_url=self.base_url,
            use_responses=False,
        )

        agent = Agent(
            name="PyScrAI Architect",
            instructions=self._instructions(available_modules),
            model=self.model,
            model_settings=ModelSettings(temperature=0),
            output_type=ArchitectManifestRecommendation,
        )
        run = Runner.run_sync(
            agent,
            input=json.dumps(request.model_dump(mode="json"), indent=2),
            run_config=RunConfig(
                model_provider=provider,
                workflow_name="PyScrAI Architect Manifest Draft",
                tracing_disabled=True,
            ),
        )
        recommendation = run.final_output_as(
            ArchitectManifestRecommendation, raise_if_incorrect_type=True
        )
        recommendation.draft_source = "openai_agents_sdk"
        return recommendation

    @staticmethod
    def _instructions(available_modules: list[ModuleRegistryEntry]) -> str:
        registry_payload = json.dumps(
            [entry.model_dump(mode="json") for entry in available_modules],
            indent=2,
        )
        return (
            "You are drafting a Project Manifest for PyScrAI Forge.\n"
            "Select enabled modules only from the provided static registry.\n"
            "Do not invent module ids.\n"
            "Prefer local-first routing.\n"
            "Use LM Studio for chat and embeddings by default.\n"
            "Use OpenRouter for reasoning unless the goal clearly requires local-only operation.\n"
            "Keep storage local_fs + sqlite unless the goal requires otherwise.\n"
            "Keep operator approval required and auto scaffold disabled.\n"
            "Return concise notes and no freeform sections outside the output schema.\n"
            f"Static module registry:\n{registry_payload}"
        )


class ArchitectManifestService:
    def __init__(
        self,
        registry: StaticModuleRegistry | None = None,
        adapter: ArchitectAgentAdapter | None = None,
        fallback_adapter: ArchitectAgentAdapter | None = None,
    ) -> None:
        self.registry = registry or StaticModuleRegistry()
        self.adapter = adapter or OpenAICompatibleArchitectAgentAdapter()
        self.fallback_adapter = fallback_adapter or HeuristicArchitectAgentAdapter()

    def draft_manifest(
        self, project: Project, goal: str, operator: str | None = None
    ) -> ArchitectManifestDraftResponse:
        request = ArchitectManifestDraftRequest(
            project_id=project.id,
            project_name=project.name,
            goal=goal,
            domain_type=project.domain_type,
            operator=operator,
        )
        available_modules = self.registry.list_modules()
        try:
            recommendation = self.adapter.recommend_manifest(request, available_modules)
        except Exception:
            recommendation = self.fallback_adapter.recommend_manifest(
                request, available_modules
            )

        selected_ids = [
            selection.module_id for selection in recommendation.module_selections
        ] or ["setup_session", "worldmatrix_authoring", "validation"]
        selected_modules = self.registry.resolve(selected_ids)
        manifest_draft = ProjectManifestDraft(
            project_id=project.id,
            payload=self._build_manifest_payload(
                project=project,
                operator=operator,
                recommendation=recommendation,
                selected_modules=selected_modules,
            ),
        )
        return ArchitectManifestDraftResponse(
            manifest_draft=manifest_draft,
            recommendation=recommendation,
            available_modules=available_modules,
            selected_modules=selected_modules,
        )

    def validate_enabled_modules(self, module_ids: list[str]) -> list[ModuleRegistryEntry]:
        return self.registry.resolve(module_ids)

    def module_registry(self) -> list[ModuleRegistryEntry]:
        return self.registry.list_modules()

    def rebuild_payload(
        self,
        project: Project,
        operator: str | None,
        payload: ProjectManifestPayload,
    ) -> ProjectManifestPayload:
        selected_modules = self.validate_enabled_modules(payload.enabled_modules)
        fallback_order = self._fallback_order(
            payload.routing_policy.default_route,
            payload.providers.registry,
        )
        routing_policy = payload.routing_policy.model_copy(
            update={"fallback_order": fallback_order}
        )
        return self._assemble_payload(
            project=project,
            operator=operator,
            providers=payload.providers,
            routing_policy=routing_policy,
            storage=payload.storage,
            policies=payload.policies,
            selected_modules=selected_modules,
        )

    @staticmethod
    def _build_manifest_payload(
        project: Project,
        operator: str | None,
        recommendation: ArchitectManifestRecommendation,
        selected_modules: list[ModuleRegistryEntry],
    ) -> ProjectManifestPayload:
        provider_registry = [
            ManifestProviderRegistryEntry(
                id="openrouter",
                provider="openrouter",
                transport="remote",
                enabled=recommendation.allow_remote_reasoning
                or recommendation.default_route == "remote",
                models=["default-chat", "default-reasoning"],
            ),
            ManifestProviderRegistryEntry(
                id="lmstudio",
                provider="lmstudio",
                transport="local",
                enabled=True,
                base_url="http://127.0.0.1:1234",
                models=["default-chat", "default-reasoning", "default-embedding"],
            ),
        ]
        return ArchitectManifestService._assemble_payload(
            project=project,
            operator=operator,
            providers=ManifestProviders(
                provider_bus=recommendation.provider_bus,
                registry=provider_registry,
                defaults=ManifestProviderDefaults(
                    chat=f"{recommendation.chat_provider_id}/default-chat",
                    reasoning=f"{recommendation.reasoning_provider_id}/default-reasoning",
                    embedding=f"{recommendation.embedding_provider_id}/default-embedding",
                ),
            ),
            routing_policy=ManifestRoutingPolicy(
                local_first=recommendation.default_route == "local",
                default_route=recommendation.default_route,
                allow_remote_reasoning=recommendation.allow_remote_reasoning,
                allow_remote_ingestion_assist=recommendation.allow_remote_ingestion_assist,
                fallback_order=ArchitectManifestService._fallback_order(
                    recommendation.default_route, provider_registry
                ),
            ),
            storage=ManifestStorage(
                artifact_backend=recommendation.artifact_backend,
                artifact_root="artifacts/projects",
                relational_backend=recommendation.relational_backend,
                relational_dsn="sqlite:///artifacts/projects/pyscrai.db",
            ),
            policies=ManifestPolicies(
                operator_approval_required=recommendation.operator_approval_required,
                allow_auto_scaffold=recommendation.allow_auto_scaffold,
            ),
            selected_modules=selected_modules,
        )

    @staticmethod
    def _assemble_payload(
        project: Project,
        operator: str | None,
        providers: ManifestProviders,
        routing_policy: ManifestRoutingPolicy,
        storage: ManifestStorage,
        policies: ManifestPolicies,
        selected_modules: list[ModuleRegistryEntry],
    ) -> ProjectManifestPayload:
        enabled_module_ids = [entry.id for entry in selected_modules]
        requires_vectors = any(
            entry.config_contract.enables_vectors for entry in selected_modules
        )
        requires_graph = any(
            entry.config_contract.enables_graph for entry in selected_modules
        )
        session_memory = any(
            entry.config_contract.enables_session_memory for entry in selected_modules
        )
        long_term_memory = any(
            entry.config_contract.enables_long_term_memory
            for entry in selected_modules
        )
        retrieval_memory = any(
            entry.config_contract.enables_retrieval for entry in selected_modules
        )
        runtime_mode = (
            "authoring_and_runtime"
            if "scenario_runtime" in enabled_module_ids
            else "authoring_only"
        )
        default_surface = (
            "runtime" if runtime_mode == "authoring_and_runtime" else "world_authoring"
        )
        return ProjectManifestPayload(
            metadata=ManifestMetadata(
                project_id=project.id,
                name=project.name,
                description=project.description,
                created_by=operator,
                domain_type=project.domain_type,
                created_at=project.created_at,
                updated_at=project.updated_at,
            ),
            enabled_modules=enabled_module_ids,
            providers=providers,
            routing_policy=routing_policy,
            storage=storage,
            vectors=ManifestVectors(
                enabled=requires_vectors,
                backend="local_file_index" if requires_vectors else None,
                collection="pyscrai_default" if requires_vectors else None,
            ),
            graph=ManifestGraph(
                enabled=requires_graph,
                backend="networkx" if requires_graph else None,
                namespace=project.id if requires_graph else None,
            ),
            mcp_servers=[],
            memory=ManifestMemory(
                session_enabled=session_memory,
                long_term_enabled=long_term_memory,
                retrieval_enabled=retrieval_memory,
            ),
            runtime_profile=ManifestRuntimeProfile(
                mode=runtime_mode,
                default_surface=default_surface,
                trace_enabled=True,
            ),
            policies=policies,
        )

    @staticmethod
    def _fallback_order(
        default_route: str, provider_registry: list[ManifestProviderRegistryEntry]
    ) -> list[str]:
        provider_ids = [entry.id for entry in provider_registry if entry.enabled]
        if default_route == "remote" and "openrouter" in provider_ids:
            ordered = ["openrouter"]
            if "lmstudio" in provider_ids:
                ordered.append("lmstudio")
            return ordered
        ordered = ["lmstudio"] if "lmstudio" in provider_ids else []
        if "openrouter" in provider_ids:
            ordered.append("openrouter")
        return ordered
