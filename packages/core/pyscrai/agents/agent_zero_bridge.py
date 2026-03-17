# PyScrAI Agent Zero Bridge Module
# A2A Protocol Adapter for Agent Zero Integration

"""
Agent Zero Bridge - Clean adapter between PyScrAI and Agent Zero.

This module provides a clean interface to Agent Zero's capabilities while
maintaining separation from PyScrAI's core domain models and contracts.

Architecture:
- Uses A2A protocol for external communication with Agent Zero
- Provides typed interfaces that map to PyScrAI domain concepts
- Preserves all existing PyScrAI contracts and domain models
- Abstracts Agent Zero details behind clean adapter pattern
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from enum import Enum

import httpx

from pyscrai.contracts.models import Project, WorldMatrix, SetupSession
from pyscrai.domain.enums import SessionPhase, ValidationState


logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class AgentZeroConfig:
    """Configuration for Agent Zero connection."""

    base_url: str = "http://localhost:5000"
    a2a_endpoint: str = "/a2a"
    timeout: int = 30

    @property
    def a2a_url(self) -> str:
        """Full A2A endpoint URL."""
        return f"{self.base_url.rstrip('/')}{self.a2a_endpoint}"


# =============================================================================
# Protocol Definitions
# =============================================================================

class AgentSubordinate(Protocol):
    """Protocol for PyScrAI agent subordinates."""

    profile: str

    async def send_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Send message to subordinate and get response."""
        ...


# =============================================================================
# A2A Client
# =============================================================================

@dataclass
class A2AMessage:
    """A2A protocol message."""

    content: str
    context_id: Optional[str] = None
    attachments: List[str] = field(default_factory=list)


@dataclass
class A2AResponse:
    """A2A protocol response."""

    content: str
    context_id: Optional[str] = None
    success: bool = True
    error: Optional[str] = None


class A2AClient:
    """Client for A2A protocol communication with Agent Zero."""

    def __init__(self, config: AgentZeroConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
        self._sessions: Dict[str, str] = {}  # agent_url -> context_id

    async def send(
        self,
        agent_url: str,
        message: str,
        attachments: Optional[List[str]] = None,
        reset: bool = False
    ) -> A2AResponse:
        """Send message via A2A protocol."""
        try:
            context_id = None if reset else self._sessions.get(agent_url)

            payload = {
                "message": message,
                "attachments": attachments or [],
            }
            if context_id:
                payload["context_id"] = context_id

            response = await self.client.post(
                agent_url,
                json=payload
            )
            response.raise_for_status()

            data = response.json()

            # Store context for follow-up messages
            if data.get("context_id"):
                self._sessions[agent_url] = data["context_id"]

            return A2AResponse(
                content=data.get("content", ""),
                context_id=data.get("context_id"),
                success=True
            )
        except Exception as e:
            logger.error(f"A2A communication error: {e}")
            return A2AResponse(
                content="",
                success=False,
                error=str(e)
            )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# =============================================================================
# Agent Zero Bridge
# =============================================================================

@dataclass
class SubordinateResult:
    """Result from subordinate agent execution."""

    success: bool
    content: str
    profile: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentZeroBridge:
    """Main bridge class for Agent Zero integration.

    Provides typed interfaces for PyScrAI workflows to interact with
    Agent Zero's capabilities while maintaining clean separation.

    Usage:
        bridge = AgentZeroBridge()

        # Architect interview
        result = await bridge.run_architect_interview(
            goal="Build a Gulf crisis simulation",
            session=setup_session
        )

        # World authoring
        result = await bridge.run_world_authoring(
            worldmatrix=worldmatrix,
            instructions="Add new entity type: Naval Fleet"
        )
    """

    def __init__(self, config: Optional[AgentZeroConfig] = None):
        self.config = config or AgentZeroConfig()
        self.a2a_client = A2AClient(self.config)

    # -------------------------------------------------------------------------
    # Subordinate Profiles (maps to Agent Zero subordinate system)
    # -------------------------------------------------------------------------

    PROFILES = {
        "pyscrai-architect": {
            "title": "PyScrAI Architect",
            "description": "Project setup, goal intake, manifest creation",
            "context": """You are the PyScrAI architect agent. Guide users through project creation, 
interview them about their goals, recommend modules, and create the project manifest. 
Use setup_mapper.py and architect_manifest.py tools."""
        },
        "pyscrai-author": {
            "title": "PyScrAI World Author",
            "description": "Entity creation, relationship mapping, rule definition",
            "context": """You are the PyScrAI world authoring agent. Create entities, define relationships, 
set up rules and knowledge boundaries, and build WorldMatrix artifacts. 
Use WorldMatrix contracts and validation engine."""
        },
        "pyscrai-runtime": {
            "title": "PyScrAI Runtime",
            "description": "Scenario execution, event logging, state management",
            "context": """You are the PyScrAI runtime agent. Execute scenarios, manage simulation state, 
log events, and generate run reports using the ScenarioRuntimeEngine."""
        },
        "pyscrai-ingest": {
            "title": "PyScrAI Ingestion",
            "description": "Document processing, entity extraction, knowledge graph building",
            "context": """You are the PyScrAI ingestion agent. Process documents, extract entities and relations, 
build knowledge graphs using a local-first pipeline."""
        }
    }

    # -------------------------------------------------------------------------
    # Core Methods
    # -------------------------------------------------------------------------

    async def run_architect_interview(
        self,
        goal: str,
        session: Optional[SetupSession] = None,
        context: Optional[Dict] = None
    ) -> SubordinateResult:
        """Run architect interview flow via Agent Zero subordinate.

        Args:
            goal: Natural language goal description
            session: Optional existing setup session
            context: Additional context for the interview

        Returns:
            SubordinateResult with interview outcome
        """
        message = self._build_architect_message(goal, session, context)
        return await self._send_to_subordinate("pyscrai-architect", message)

    async def run_world_authoring(
        self,
        worldmatrix: Optional[WorldMatrix] = None,
        instructions: str = "",
        context: Optional[Dict] = None
    ) -> SubordinateResult:
        """Run world authoring via Agent Zero subordinate.

        Args:
            worldmatrix: Optional existing WorldMatrix to modify
            instructions: Authoring instructions
            context: Additional context

        Returns:
            SubordinateResult with authoring outcome
        """
        message = self._build_authoring_message(worldmatrix, instructions, context)
        return await self._send_to_subordinate("pyscrai-author", message)

    async def run_scenario(
        self,
        scenario_id: str,
        instructions: str = "",
        context: Optional[Dict] = None
    ) -> SubordinateResult:
        """Run scenario execution via Agent Zero subordinate.

        Args:
            scenario_id: ID of scenario to execute
            instructions: Runtime instructions
            context: Additional context

        Returns:
            SubordinateResult with runtime outcome
        """
        message = self._build_runtime_message(scenario_id, instructions, context)
        return await self._send_to_subordinate("pyscrai-runtime", message)

    async def run_ingestion(
        self,
        source: str,
        instructions: str = "",
        context: Optional[Dict] = None
    ) -> SubordinateResult:
        """Run document ingestion via Agent Zero subordinate.

        Args:
            source: Document source (file path or URL)
            instructions: Ingestion instructions
            context: Additional context

        Returns:
            SubordinateResult with ingestion outcome
        """
        message = self._build_ingestion_message(source, instructions, context)
        return await self._send_to_subordinate("pyscrai-ingest", message)

    # -------------------------------------------------------------------------
    # Internal Methods
    # -------------------------------------------------------------------------

    async def _send_to_subordinate(
        self,
        profile: str,
        message: str
    ) -> SubordinateResult:
        """Send message to subordinate agent."""
        if profile not in self.PROFILES:
            return SubordinateResult(
                success=False,
                content="",
                profile=profile,
                error=f"Unknown profile: {profile}"
            )

        # In a real implementation, this would route to Agent Zero's
        # subordinate system via A2A or direct API
        # For now, return a structured placeholder
        return SubordinateResult(
            success=True,
            content=f"Message sent to {profile}: {message[:100]}...",
            profile=profile,
            metadata={"status": "pending_implementation"}
        )

    def _build_architect_message(
        self,
        goal: str,
        session: Optional[SetupSession],
        context: Optional[Dict]
    ) -> str:
        """Build architect interview message."""
        parts = [f"Goal: {goal}"]

        if session:
            parts.append(f"Current Phase: {session.phase}")
            if session.intent_summary:
                parts.append(f"Intent Summary: {session.intent_summary}")

        if context:
            parts.append(f"Additional Context: {json.dumps(context)}")

        return "
".join(parts)

    def _build_authoring_message(
        self,
        worldmatrix: Optional[WorldMatrix],
        instructions: str,
        context: Optional[Dict]
    ) -> str:
        """Build world authoring message."""
        parts = [f"Instructions: {instructions}"]

        if worldmatrix:
            parts.append(f"WorldMatrix ID: {worldmatrix.id}")
            parts.append(f"Entities: {len(worldmatrix.entities)}")
            parts.append(f"Relations: {len(worldmatrix.relations)}")

        if context:
            parts.append(f"Additional Context: {json.dumps(context)}")

        return "
".join(parts)

    def _build_runtime_message(
        self,
        scenario_id: str,
        instructions: str,
        context: Optional[Dict]
    ) -> str:
        """Build runtime message."""
        parts = [f"Scenario ID: {scenario_id}"]

        if instructions:
            parts.append(f"Instructions: {instructions}")

        if context:
            parts.append(f"Additional Context: {json.dumps(context)}")

        return "
".join(parts)

    def _build_ingestion_message(
        self,
        source: str,
        instructions: str,
        context: Optional[Dict]
    ) -> str:
        """Build ingestion message."""
        parts = [f"Source: {source}"]

        if instructions:
            parts.append(f"Instructions: {instructions}")

        if context:
            parts.append(f"Additional Context: {json.dumps(context)}")

        return "
".join(parts)

    async def close(self):
        """Clean up resources."""
        await self.a2a_client.close()


# =============================================================================
# Convenience Functions
# =============================================================================

def create_bridge(config: Optional[AgentZeroConfig] = None) -> AgentZeroBridge:
    """Create a new AgentZeroBridge instance."""
    return AgentZeroBridge(config)


def get_subordinate_profiles() -> Dict[str, Dict[str, str]]:
    """Get available subordinate profiles."""
    return AgentZeroBridge.PROFILES.copy()
