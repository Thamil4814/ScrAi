import os
import sys

import streamlit as st

from pyscrai.application.services import ProjectService
from pyscrai.contracts.models import ProjectBootstrapRequest


def init_service() -> ProjectService:
    if "project_service" not in st.session_state:
        st.session_state.project_service = ProjectService()
    return st.session_state.project_service


def main() -> None:
    # Use streamlit run as the actual execution context
    import subprocess
    
    script_path = os.path.abspath(__file__)
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_path])


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
            submitted = st.form_submit_button("Scaffold Project")
            
        if submitted and prompt:
            with st.spinner("Scaffolding Project and Manifest..."):
                response = service.bootstrap_project(ProjectBootstrapRequest(prompt=prompt))
                st.session_state.active_project_id = response.project.id
                st.success(f"Project '{response.project.name}' scaffolded successfully.")

    elif action == "Open Project":
        projects = service.list_projects()
        if not projects:
            st.info("No existing projects found.")
        else:
            project_options = {p.id: f"{p.name} ({p.domain_type})" for p in projects}
            selected_id = st.selectbox(
                "Select a Project",
                options=list(project_options.keys()),
                format_func=lambda x: project_options[x]
            )
            if st.button("Load"):
                st.session_state.active_project_id = selected_id

    # Active Stack Summary
    if "active_project_id" in st.session_state:
        st.divider()
        project_id = st.session_state.active_project_id
        project = service.get_project(project_id)
        draft = service.repository.load_manifest_draft(project_id)
        
        st.header(f"Active Stack Summary: {project.name}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Configuration")
            st.json(draft.payload.forge.model_dump())
            
            st.subheader("Modules")
            st.json(draft.payload.modules.model_dump())
            
            st.subheader("Providers")
            st.json(draft.payload.providers.model_dump())
            
        with col2:
            st.subheader("Storage")
            st.json(draft.payload.storage.model_dump())
            
            st.subheader("Runtime Policies")
            st.json(draft.payload.policies.model_dump())
            
            st.subheader("Routing Policy")
            st.json(draft.payload.routing_policy.model_dump())

        # Launch surfaces
        st.divider()
        st.header("Launchpads")
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            st.button("Launch World Authoring", use_container_width=True, disabled=True)
            st.caption("Not yet available.")
        with lc2:
            st.button("Launch Runtime", use_container_width=True, disabled=True)
            st.caption("Not yet available.")
        with lc3:
            st.button("Agent Lab", use_container_width=True, disabled=True)
            st.caption("Not yet available.")
