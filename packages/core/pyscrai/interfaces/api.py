from __future__ import annotations

from fastapi import FastAPI, HTTPException

from pyscrai.application.services import ProjectService
from pyscrai.contracts.models import (
    Project,
    ProjectCreateRequest,
    SetupMessageRequest,
    SetupSession,
    SetupSessionCreateRequest,
    ValidationSummary,
    WorldMatrix,
    WorldMatrixDraft,
)
from pyscrai.services.repository import NotFoundError

service = ProjectService()
app = FastAPI(title="PyScrAI API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/projects", response_model=Project)
def create_project(request: ProjectCreateRequest) -> Project:
    return service.create_project(request)


@app.post("/projects/{project_id}/setup-sessions", response_model=SetupSession)
def create_setup_session(project_id: str, request: SetupSessionCreateRequest | None = None) -> SetupSession:
    try:
        return service.create_setup_session(project_id, request)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/setup-sessions/{session_id}/messages", response_model=SetupSession)
def add_setup_message(session_id: str, request: SetupMessageRequest) -> SetupSession:
    try:
        return service.add_setup_message(session_id, request)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/setup-sessions/{session_id}", response_model=SetupSession)
def get_setup_session(session_id: str) -> SetupSession:
    try:
        return service.get_setup_session(session_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/projects/{project_id}/worldmatrix-draft", response_model=WorldMatrixDraft)
def get_worldmatrix_draft(project_id: str) -> WorldMatrixDraft:
    try:
        return service.get_worldmatrix_draft(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/projects/{project_id}/worldmatrix-draft/validate", response_model=ValidationSummary)
def validate_worldmatrix_draft(project_id: str) -> ValidationSummary:
    try:
        return service.validate_worldmatrix_draft(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/projects/{project_id}/worldmatrix-draft/compile", response_model=WorldMatrix)
def compile_worldmatrix_draft(project_id: str) -> WorldMatrix:
    try:
        return service.compile_worldmatrix(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def run() -> None:
    import uvicorn

    uvicorn.run("pyscrai.interfaces.api:app", host="127.0.0.1", port=8000, reload=False)
