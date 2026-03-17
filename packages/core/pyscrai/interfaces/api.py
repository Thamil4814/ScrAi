from __future__ import annotations

from fastapi import FastAPI, HTTPException

from pyscrai.application.services import ProjectService
from pyscrai.contracts.models import (
    Project,
    ProjectBootstrapRequest,
    ProjectBootstrapResponse,
    ProjectCreateRequest,
    ProjectManifestDraft,
    Scenario,
    ScenarioCreateRequest,
    SetupMessageRequest,
    SetupSession,
    SetupSessionCreateRequest,
    SimulationRun,
    SimulationRunRequest,
    ValidationSummary,
    WorldBranch,
    WorldBranchCreateRequest,
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


@app.get("/projects", response_model=list[Project])
def list_projects() -> list[Project]:
    return service.list_projects()


@app.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: str) -> Project:
    try:
        return service.get_project(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/projects/bootstrap", response_model=ProjectBootstrapResponse)
def bootstrap_project(request: ProjectBootstrapRequest) -> ProjectBootstrapResponse:
    return service.bootstrap_project(request)


@app.get("/projects/{project_id}/manifest-draft", response_model=ProjectManifestDraft)
def get_manifest_draft(project_id: str) -> ProjectManifestDraft:
    try:
        return service.get_manifest_draft(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/projects/{project_id}/setup-sessions", response_model=SetupSession)
def create_setup_session(
    project_id: str, request: SetupSessionCreateRequest | None = None
) -> SetupSession:
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


@app.post(
    "/projects/{project_id}/worldmatrix-draft/validate",
    response_model=ValidationSummary,
)
def validate_worldmatrix_draft(project_id: str) -> ValidationSummary:
    try:
        return service.validate_worldmatrix_draft(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post(
    "/projects/{project_id}/worldmatrix-draft/compile", response_model=WorldMatrix
)
def compile_worldmatrix_draft(project_id: str) -> WorldMatrix:
    try:
        return service.compile_worldmatrix(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/worldmatrices/{worldmatrix_id}", response_model=WorldMatrix)
def get_worldmatrix(worldmatrix_id: str) -> WorldMatrix:
    try:
        return service.get_worldmatrix(worldmatrix_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/worldmatrices/{worldmatrix_id}/branches", response_model=WorldBranch)
def create_worldbranch(
    worldmatrix_id: str, request: WorldBranchCreateRequest
) -> WorldBranch:
    try:
        return service.create_worldbranch(worldmatrix_id, request)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/branches/{branch_id}/scenarios", response_model=Scenario)
def create_scenario(branch_id: str, request: ScenarioCreateRequest) -> Scenario:
    try:
        return service.create_scenario(branch_id, request)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/scenarios/{scenario_id}", response_model=Scenario)
def get_scenario(scenario_id: str) -> Scenario:
    try:
        return service.get_scenario(scenario_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/scenarios/{scenario_id}/runs", response_model=SimulationRun)
def run_scenario(
    scenario_id: str, request: SimulationRunRequest | None = None
) -> SimulationRun:
    try:
        return service.run_scenario(scenario_id, request)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/runs/{run_id}", response_model=SimulationRun)
def get_run(run_id: str) -> SimulationRun:
    try:
        return service.get_simulation_run(run_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def run() -> None:
    import uvicorn

    uvicorn.run("pyscrai.interfaces.api:app", host="127.0.0.1", port=8000, reload=False)
