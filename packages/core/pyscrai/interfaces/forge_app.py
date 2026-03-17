import os
import sys

import streamlit as st

from pyscrai.application.services import ProjectService
from pyscrai.contracts.models import (
    ProjectBootstrapRequest,
    ProjectManifestApprovalRequest,
    ProjectManifestDraftUpdateRequest,
)


def init_service() -> ProjectService:
    if "project_service" not in st.session_state:
        st.session_state.project_service = ProjectService()
    return st.session_state.project_service


def main() -> None:
    import subprocess

    script_path = os.path.abspath(__file__)
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_path], check=False)


def _provider_id(reference: str) -> str:
    return reference.split("/", 1)[0]


def _render_manifest_review(service: ProjectService, project_id: str) -> None:
    project = service.get_project(project_id)
    draft = service.get_manifest_draft(project_id)
    modules = service.list_manifest_modules()
    module_ids = [module.id for module in modules]
    module_labels = {
        module.id: f"{module.name} ({module.id})"
        for module in modules
    }
    module_map = {module.id: module for module in modules}
    provider_registry = draft.payload.providers.registry
    provider_options = [entry.id for entry in provider_registry]

    st.header("Manifest Review")
    st.caption("Review the architect draft, edit what you need, then approve before setup continues.")

    with st.expander("Module Registry", expanded=True):
        for module_id in draft.payload.enabled_modules:
            module = module_map[module_id]
            st.markdown(f"**{module.name}**")
            st.write(module.purpose)
            st.caption(
                f"Dependencies: {', '.join(module.dependencies) or 'none'} | Surfaces: {', '.join(module.ui_surfaces) or 'none'}"
            )

    with st.form("manifest_review_form"):
        name = st.text_input("Project Name", value=draft.payload.metadata.name)
        description = st.text_area(
            "Goal / Description", value=draft.payload.metadata.description, height=120
        )
        enabled_modules = st.multiselect(
            "Enabled Modules",
            options=module_ids,
            default=draft.payload.enabled_modules,
            format_func=lambda module_id: module_labels[module_id],
        )

        provider_col1, provider_col2, provider_col3 = st.columns(3)
        with provider_col1:
            chat_provider_id = st.selectbox(
                "Chat Provider",
                options=provider_options,
                index=provider_options.index(
                    _provider_id(draft.payload.providers.defaults.chat)
                ),
            )
        with provider_col2:
            reasoning_provider_id = st.selectbox(
                "Reasoning Provider",
                options=provider_options,
                index=provider_options.index(
                    _provider_id(draft.payload.providers.defaults.reasoning)
                ),
            )
        with provider_col3:
            embedding_provider_id = st.selectbox(
                "Embedding Provider",
                options=provider_options,
                index=provider_options.index(
                    _provider_id(draft.payload.providers.defaults.embedding)
                ),
            )

        routing_col1, routing_col2 = st.columns(2)
        with routing_col1:
            default_route = st.selectbox(
                "Default Route",
                options=["local", "remote"],
                index=["local", "remote"].index(draft.payload.routing_policy.default_route),
            )
        with routing_col2:
            provider_bus = st.text_input(
                "Provider Bus", value=draft.payload.providers.provider_bus
            )

        allow_remote_reasoning = st.checkbox(
            "Allow Remote Reasoning",
            value=draft.payload.routing_policy.allow_remote_reasoning,
        )
        allow_remote_ingestion_assist = st.checkbox(
            "Allow Remote Ingestion Assist",
            value=draft.payload.routing_policy.allow_remote_ingestion_assist,
        )

        storage_col1, storage_col2 = st.columns(2)
        with storage_col1:
            artifact_backend = st.selectbox(
                "Artifact Backend",
                options=["local_fs"],
                index=0,
            )
        with storage_col2:
            relational_backend = st.selectbox(
                "Relational Backend",
                options=["sqlite"],
                index=0,
            )

        operator_approval_required = st.checkbox(
            "Operator Approval Required",
            value=draft.payload.policies.operator_approval_required,
        )
        allow_auto_scaffold = st.checkbox(
            "Allow Auto Scaffold",
            value=draft.payload.policies.allow_auto_scaffold,
        )

        save_clicked = st.form_submit_button("Save Manifest Draft")
        approve_clicked = st.form_submit_button(
            "Approve And Launch World Authoring"
        )

    if save_clicked or approve_clicked:
        updated_registry = []
        for entry in provider_registry:
            enabled = entry.enabled
            if entry.id in {
                chat_provider_id,
                reasoning_provider_id,
                embedding_provider_id,
            }:
                enabled = True
            if entry.id == "openrouter" and not allow_remote_reasoning and default_route != "remote":
                enabled = False
            updated_registry.append(entry.model_copy(update={"enabled": enabled}))

        payload = draft.payload.model_copy(
            update={
                "metadata": draft.payload.metadata.model_copy(
                    update={"name": name, "description": description}
                ),
                "enabled_modules": enabled_modules,
                "providers": draft.payload.providers.model_copy(
                    update={
                        "provider_bus": provider_bus,
                        "registry": updated_registry,
                        "defaults": draft.payload.providers.defaults.model_copy(
                            update={
                                "chat": f"{chat_provider_id}/default-chat",
                                "reasoning": f"{reasoning_provider_id}/default-reasoning",
                                "embedding": f"{embedding_provider_id}/default-embedding",
                            }
                        ),
                    }
                ),
                "routing_policy": draft.payload.routing_policy.model_copy(
                    update={
                        "local_first": default_route == "local",
                        "default_route": default_route,
                        "allow_remote_reasoning": allow_remote_reasoning,
                        "allow_remote_ingestion_assist": allow_remote_ingestion_assist,
                    }
                ),
                "storage": draft.payload.storage.model_copy(
                    update={
                        "artifact_backend": artifact_backend,
                        "relational_backend": relational_backend,
                    }
                ),
                "policies": draft.payload.policies.model_copy(
                    update={
                        "operator_approval_required": operator_approval_required,
                        "allow_auto_scaffold": allow_auto_scaffold,
                    }
                ),
            }
        )
        service.update_manifest_draft(
            project_id,
            ProjectManifestDraftUpdateRequest(payload=payload),
        )
        if approve_clicked:
            approval = service.approve_manifest_draft(
                project_id, ProjectManifestApprovalRequest()
            )
            st.session_state.active_setup_session_id = approval.setup_session.id
            st.success("Manifest approved. World authoring setup is now active.")
        else:
            st.success("Manifest draft updated.")
        st.rerun()

    st.subheader("Current Draft")
    col1, col2 = st.columns(2)
    with col1:
        st.json(draft.payload.enabled_modules)
        st.json(draft.payload.providers.model_dump())
        st.json(draft.payload.routing_policy.model_dump())
    with col2:
        st.json(draft.payload.storage.model_dump())
        st.json(draft.payload.runtime_profile.model_dump())
        st.json(draft.payload.policies.model_dump())

    if project.status != "draft":
        session_id = st.session_state.get("active_setup_session_id")
        if session_id:
            session = service.get_setup_session(session_id)
            st.divider()
            st.header("World Authoring Handoff")
            st.caption(f"Current phase: {session.phase}")
            if session.pending_questions:
                st.write(session.pending_questions[0].prompt)
            if session.transcript:
                st.code(session.transcript[-1].content)


if __name__ == "__main__":
    st.set_page_config(page_title="PyScrAI Forge", layout="wide")
    service = init_service()

    st.title("PyScrAI Forge")

    with st.sidebar:
        st.header("Project Selection")
        action = st.radio("Action", ["New Project", "Open Project"])

    if action == "New Project":
        st.subheader("Goal Intake")
        with st.form("new_project_form"):
            prompt = st.text_area(
                "Describe your world generating goal:",
                placeholder="Build a near-future Gulf crisis simulation in the Persian Gulf.",
            )
            submitted = st.form_submit_button("Draft Manifest")

        if submitted and prompt:
            with st.spinner("Drafting Project Manifest..."):
                response = service.bootstrap_project(
                    ProjectBootstrapRequest(prompt=prompt)
                )
                st.session_state.active_project_id = response.project.id
                st.success(
                    f"Project '{response.project.name}' drafted. Review the manifest before setup begins."
                )

    elif action == "Open Project":
        projects = service.list_projects()
        if not projects:
            st.info("No existing projects found.")
        else:
            project_options = {p.id: f"{p.name} ({p.status})" for p in projects}
            selected_id = st.selectbox(
                "Select a Project",
                options=list(project_options.keys()),
                format_func=lambda x: project_options[x],
            )
            if st.button("Load"):
                st.session_state.active_project_id = selected_id

    if "active_project_id" in st.session_state:
        st.divider()
        active_project = service.get_project(st.session_state.active_project_id)
        st.header(f"Active Stack Summary: {active_project.name}")
        st.caption(
            f"Project status: {active_project.status} | Domain: {active_project.domain_type}"
        )
        _render_manifest_review(service, st.session_state.active_project_id)
