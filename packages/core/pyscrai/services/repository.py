from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from pyscrai.contracts.models import (
    Project,
    Scenario,
    SetupSession,
    SimulationRun,
    WorldBranch,
    WorldMatrix,
    WorldMatrixDraft,
)


class NotFoundError(FileNotFoundError):
    pass


class ArtifactRepository:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[4] / "artifacts" / "projects"
        self.root.mkdir(parents=True, exist_ok=True)

    def save_project(self, project: Project) -> None:
        self._write_model(self.project_path(project.id), project)

    def load_project(self, project_id: str) -> Project:
        return self._read_model(self.project_path(project_id), Project)

    def list_projects(self) -> list[Project]:
        projects: list[Project] = []
        for project_file in self.root.glob("*/project.json"):
            projects.append(self._read_model(project_file, Project))
        projects.sort(key=lambda project: project.created_at, reverse=True)
        return projects

    def update_project_status(self, project_id: str, status: str) -> Project:
        project = self.load_project(project_id)
        project.status = status
        self.save_project(project)
        return project

    def save_draft(self, draft: WorldMatrixDraft) -> None:
        self._write_model(self.draft_path(draft.project_id), draft)

    def load_draft(self, project_id: str) -> WorldMatrixDraft:
        return self._read_model(self.draft_path(project_id), WorldMatrixDraft)

    def save_session(self, session: SetupSession) -> None:
        self._write_model(self.session_path(session.project_id, session.id), session)

    def load_session(self, session_id: str) -> SetupSession:
        session_file = next(self.root.glob(f"*/sessions/{session_id}.json"), None)
        if session_file is None:
            raise NotFoundError(f"Setup session {session_id} was not found.")
        return self._read_model(session_file, SetupSession)

    def save_worldmatrix(self, worldmatrix: WorldMatrix) -> None:
        self._write_model(self.worldmatrix_path(worldmatrix.project_id, worldmatrix.id), worldmatrix)

    def load_worldmatrix(self, worldmatrix_id: str) -> WorldMatrix:
        worldmatrix_file = next(self.root.glob(f"*/worldmatrices/{worldmatrix_id}.json"), None)
        if worldmatrix_file is None:
            raise NotFoundError(f"WorldMatrix {worldmatrix_id} was not found.")
        return self._read_model(worldmatrix_file, WorldMatrix)

    def save_worldbranch(self, project_id: str, worldbranch: WorldBranch) -> None:
        self._write_model(self.worldbranch_path(project_id, worldbranch.id), worldbranch)

    def load_worldbranch(self, branch_id: str) -> WorldBranch:
        branch_file = next(self.root.glob(f"*/worldbranches/{branch_id}.json"), None)
        if branch_file is None:
            raise NotFoundError(f"WorldBranch {branch_id} was not found.")
        return self._read_model(branch_file, WorldBranch)

    def save_scenario(self, project_id: str, scenario: Scenario) -> None:
        self._write_model(self.scenario_path(project_id, scenario.id), scenario)

    def load_scenario(self, scenario_id: str) -> Scenario:
        scenario_file = next(self.root.glob(f"*/scenarios/{scenario_id}.json"), None)
        if scenario_file is None:
            raise NotFoundError(f"Scenario {scenario_id} was not found.")
        return self._read_model(scenario_file, Scenario)

    def save_simulation_run(self, project_id: str, run: SimulationRun) -> None:
        self._write_model(self.simulation_run_path(project_id, run.id), run)

    def load_simulation_run(self, run_id: str) -> SimulationRun:
        run_file = next(self.root.glob(f"*/simulation-runs/{run_id}.json"), None)
        if run_file is None:
            raise NotFoundError(f"SimulationRun {run_id} was not found.")
        return self._read_model(run_file, SimulationRun)

    def project_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "project.json"

    def draft_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "worldmatrix_draft.json"

    def session_path(self, project_id: str, session_id: str) -> Path:
        return self.project_dir(project_id) / "sessions" / f"{session_id}.json"

    def worldmatrix_path(self, project_id: str, worldmatrix_id: str) -> Path:
        return self.project_dir(project_id) / "worldmatrices" / f"{worldmatrix_id}.json"

    def worldbranch_path(self, project_id: str, branch_id: str) -> Path:
        return self.project_dir(project_id) / "worldbranches" / f"{branch_id}.json"

    def scenario_path(self, project_id: str, scenario_id: str) -> Path:
        return self.project_dir(project_id) / "scenarios" / f"{scenario_id}.json"

    def simulation_run_path(self, project_id: str, run_id: str) -> Path:
        return self.project_dir(project_id) / "simulation-runs" / f"{run_id}.json"

    def compile_bundle_dir(self, project_id: str, worldmatrix_id: str) -> Path:
        return self.project_dir(project_id) / "compiled" / worldmatrix_id

    def project_dir(self, project_id: str) -> Path:
        return self.root / project_id

    @staticmethod
    def _read_model(path: Path, model_type: type[BaseModel]):
        if not path.exists():
            raise NotFoundError(f"Artifact not found: {path}")
        return model_type.model_validate_json(path.read_text())

    @staticmethod
    def _write_model(path: Path, model: BaseModel) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(model.model_dump(mode="json"), indent=2))

    @staticmethod
    def write_json(path: Path, payload: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2))
