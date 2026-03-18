import os
import sys
from typing import Optional

import streamlit as st

from pyscrai.application.services import ProjectService
from pyscrai.contracts.models import (
    ProjectBootstrapRequest,
    ProjectManifestApprovalRequest,
    ProjectManifestDraftUpdateRequest,
)

# Try to import Agent Zero bridge, but don't fail if not available
try:
    from pyscrai.a0.agent_zero_bridge import AgentZeroBridge, A2AClient
    AGENT_ZERO_AVAILABLE = True
except ImportError:
    AGENT_ZERO_AVAILABLE = False
    # Create mock classes for when Agent Zero is not available
    class AgentZeroBridge:
        pass
    class A2AClient:
        pass


def init_service() -> ProjectService:
    if "project_service" not in st.session_state:
        st.session_state.project_service = ProjectService()
    return st.session_state.project_service


def init_agent_zero_bridge() -> Optional[AgentZeroBridge]:
    """Initialize the Agent Zero bridge if available."""
    if "agent_zero_bridge" not in st.session_state and AGENT_ZERO_AVAILABLE:
        st.session_state.agent_zero_bridge = AgentZeroBridge()
    return st.session_state.get("agent_zero_bridge")


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


def _render_agent_zero_status(bridge: Optional[AgentZeroBridge]) -> None:
    """Render Agent Zero connection status and health."""
    st.header("🤖 Agent Zero Status")
    
    if not AGENT_ZERO_AVAILABLE:
        st.error("Agent Zero bridge module not available. Please ensure pyscrai.a0 module is installed.")
        return
    
    if bridge is None:
        st.warning("Agent Zero bridge not initialized.")
        return
    
    # Mock health check - in real implementation this would check A2A connection
    st.success("✅ Agent Zero bridge module loaded")
    
    # Show subordinate profiles
    with st.expander("Available Subordinate Profiles", expanded=True):
        profiles = [
            {"name": "pyscrai-architect", "description": "Project setup, goal intake, manifest creation"},
            {"name": "pyscrai-author", "description": "Entity creation, relationship mapping, rule definition"},
            {"name": "pyscrai-runtime", "description": "Scenario execution, event logging, state management"},
            {"name": "pyscrai-ingest", "description": "Document processing, entity extraction, knowledge graph building"},
        ]
        for profile in profiles:
            st.markdown(f"**{profile['name']}**: {profile['description']}")
    
    # Mock connection info
    st.info("🔌 **Connection**: Mock mode (A2A protocol not yet connected)")
    
    # Show integration status
    st.subheader("Integration Status")
    st.markdown("""
    ✅ **Phase 1**: Documentation & bridge module  
    ✅ **Phase 2**: Subordinate profiles defined  
    ✅ **Phase 3**: Skills registry complete  
    🔄 **Phase 4**: Streamlit integration (in progress)  
    """)


def _render_subordinate_management(bridge: Optional[AgentZeroBridge]) -> None:
    """Render subordinate management interface."""
    st.header("👥 Subordinate Management")
    
    if not AGENT_ZERO_AVAILABLE or bridge is None:
        st.error("Agent Zero bridge not available.")
        return
    
    st.info("Manage and interact with PyScrAI subordinate agents.")
    
    # Mock subordinate list
    subordinates = [
        {
            "id": "pyscrai-architect",
            "name": "PyScrAI Architect",
            "status": "idle",
            "last_active": "N/A",
            "tasks_completed": 0
        },
        {
            "id": "pyscrai-author",
            "name": "PyScrAI World Author",
            "status": "idle",
            "last_active": "N/A",
            "tasks_completed": 0
        },
        {
            "id": "pyscrai-runtime",
            "name": "PyScrAI Runtime",
            "status": "idle",
            "last_active": "N/A",
            "tasks_completed": 0
        },
        {
            "id": "pyscrai-ingest",
            "name": "PyScrAI Ingestion",
            "status": "idle",
            "last_active": "N/A",
            "tasks_completed": 0
        },
    ]
    
    for subordinate in subordinates:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{subordinate['name']}** (`{subordinate['id']}`)")
                st.caption(f"Status: {subordinate['status']} | Tasks: {subordinate['tasks_completed']}")
            with col2:
                st.write(f"Last active: {subordinate['last_active']}")
            with col3:
                if st.button(f"Run {subordinate['id']}", key=f"run_{subordinate['id']}"):
                    st.success(f"Would invoke {subordinate['name']} (mock)")
            st.divider()


def _render_skill_invocation(bridge: Optional[AgentZeroBridge]) -> None:
    """Render skill invocation interface."""
    st.header("🛠️ Skill Invocation")
    
    if not AGENT_ZERO_AVAILABLE or bridge is None:
        st.error("Agent Zero bridge not available.")
        return
    
    st.info("Invoke PyScrAI skills through Agent Zero.")
    
    # Mock skill list
    skills = [
        {
            "name": "pyscrai-forge",
            "description": "Project creation, goal intake, architect interview flow",
            "procedures": ["bootstrap_project", "compile_worldmatrix", "create_branch"]
        },
        {
            "name": "pyscrai-world-authoring",
            "description": "Entity creation, relationship mapping, rule definition",
            "procedures": ["add_entity", "define_relationship", "create_scenario"]
        },
        {
            "name": "pyscrai-runtime",
            "description": "Scenario execution, event logging, state management",
            "procedures": ["run_scenario", "get_run_status", "get_run_report"]
        },
        {
            "name": "pyscrai-ingest",
            "description": "Document ingestion, entity extraction, knowledge graph building",
            "procedures": ["ingest_document", "extract_entities", "build_knowledge_graph"]
        },
    ]
    
    selected_skill = st.selectbox(
        "Select a skill",
        options=[skill["name"] for skill in skills],
        format_func=lambda x: next(skill["description"] for skill in skills if skill["name"] == x)
    )
    
    if selected_skill:
        skill = next(s for s in skills if s["name"] == selected_skill)
        st.markdown(f"### {skill['name']}")
        st.write(skill["description"])
        
        st.subheader("Available Procedures")
        for proc in skill["procedures"]:
            if st.button(f"Run: {proc}", key=f"proc_{selected_skill}_{proc}"):
                st.success(f"Would execute {proc} from {selected_skill} (mock)")


def _render_memory_browser(bridge: Optional[AgentZeroBridge]) -> None:
    """Render memory browser interface."""
    st.header("🧠 Memory Browser")
    
    if not AGENT_ZERO_AVAILABLE or bridge is None:
        st.error("Agent Zero bridge not available.")
        return
    
    st.info("Search and browse PyScrAI's long-term memory system.")
    
    # Mock memory search
    search_query = st.text_input("Search memory", placeholder="Enter keywords to search...")
    
    if st.button("Search") and search_query:
        st.success(f"Would search memory for: {search_query} (mock)")
        
        # Mock search results
        mock_results = [
            {
                "id": "mem_1",
                "content": f"Project bootstrap for '{search_query[:20]}...' created successfully",
                "timestamp": "2026-03-17 04:30:00",
                "tags": ["project", "bootstrap"]
            },
            {
                "id": "mem_2",
                "content": f"World matrix compiled for scenario involving '{search_query[:20]}...'",
                "timestamp": "2026-03-17 04:25:00",
                "tags": ["worldmatrix", "scenario"]
            },
            {
                "id": "mem_3",
                "content": f"Entity extraction completed for '{search_query[:20]}...'",
                "timestamp": "2026-03-17 04:20:00",
                "tags": ["ingestion", "entities"]
            },
        ]
        
        st.subheader(f"Results for '{search_query}'")
        for result in mock_results:
            with st.expander(f"{result['content'][:50]}..."):
                st.write(result["content"])
                st.caption(f"Timestamp: {result['timestamp']} | Tags: {', '.join(result['tags'])}")
                if st.button(f"View details {result['id']}", key=f"mem_{result['id']}"):
                    st.json({"id": result["id"], "full_content": result["content"]})


if __name__ == "__main__":
    st.set_page_config(page_title="PyScrAI Forge", layout="wide", page_icon="🔥")
    service = init_service()
    bridge = init_agent_zero_bridge()

    st.title("🔥 PyScrAI Forge")
    st.caption("WorldMatrix-first, human-in-the-loop world-authoring platform")

    with st.sidebar:
        st.header("Navigation")
        mode = st.radio(
            "Select Mode",
            ["🏗️ Forge (Projects)", "🤖 Agent Zero", "📊 System Info"],
            index=0
        )
        
        st.divider()
        
        if mode == "🏗️ Forge (Projects)":
            st.header("Project Selection")
            action = st.radio("Action", ["New Project", "Open Project"])
        else:
            action = None

    # Main content based on selected mode
    if mode == "🏗️ Forge (Projects)":
        # Original Forge functionality
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
            
    elif mode == "🤖 Agent Zero":
        # Agent Zero integration mode
        st.subheader("Agent Zero Integration")
        
        if not AGENT_ZERO_AVAILABLE:
            st.error("""
            ❌ **Agent Zero bridge module not found**
            
            Please ensure the following:
            1. The `pyscrai.a0` module is properly installed
            2. Dependencies are updated: `pip install httpx a2a`
            3. The bridge module exists at `packages/core/pyscrai/a0/agent_zero_bridge.py`
            """)
        else:
            # Agent Zero tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "Status", 
                "Subordinates", 
                "Skills", 
                "Memory"
            ])
            
            with tab1:
                _render_agent_zero_status(bridge)
            
            with tab2:
                _render_subordinate_management(bridge)
            
            with tab3:
                _render_skill_invocation(bridge)
            
            with tab4:
                _render_memory_browser(bridge)
    
    elif mode == "📊 System Info":
        # System information mode
        st.subheader("System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Architecture")
            st.markdown("""
            **PyScrAI Architecture**:
            - Layer A: Forge Shell (Streamlit) ✅
            - Layer B: Agent Substrate (Agent Zero) ✅
            - Layer C: Provider Bus (LiteLLM) ✅
            - Layer D: Module Registry (Static) ✅
            - Layer E: Project Artifacts (File-backed) ✅
            - Layer F: Operational Surfaces (Skills) ✅
            """)
            
            st.markdown("### Integration Status")
            st.markdown("""
            **Agent Zero Integration**:
            - Phase 1: Documentation & bridge module ✅
            - Phase 2: Subordinate profiles ✅
            - Phase 3: Skills registry ✅
            - Phase 4: Streamlit integration 🔄
            """)
        
        with col2:
            st.markdown("### Tech Stack")
            st.markdown("""
            **Core Technologies**:
            - Python 3.12+
            - Pydantic (contracts)
            - FastAPI (API)
            - Streamlit (UI)
            - Agent Zero (orchestration)
            - LiteLLM (provider bus)
            - A2A Protocol (communication)
            """)
            
            st.markdown("### Project Info")
            st.markdown(f"""
            **Current Project**: {st.session_state.get('active_project_id', 'None')}
            **Agent Zero Available**: {'✅ Yes' if AGENT_ZERO_AVAILABLE else '❌ No'}
            **Working Directory**: `{os.getcwd()}`
            """)
