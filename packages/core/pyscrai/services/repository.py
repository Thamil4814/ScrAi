from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from pyscrai.contracts.models import Project, SetupSession, WorldMatrix, WorldMatrixDraft


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

    def project_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "project.json"

    def draft_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "worldmatrix_draft.json"

    def session_path(self, project_id: str, session_id: str) -> Path:
        return self.project_dir(project_id) / "sessions" / f"{session_id}.json"

    def worldmatrix_path(self, project_id: str, worldmatrix_id: str) -> Path:
        return self.project_dir(project_id) / "worldmatrices" / f"{worldmatrix_id}.json"

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
