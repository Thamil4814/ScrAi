from __future__ import annotations

import json

import typer

from pyscrai.application.services import ProjectService
from pyscrai.contracts.models import ProjectCreateRequest
from pyscrai.domain.enums import DomainType

app = typer.Typer(add_completion=False, help="PyScrAI CLI")
service = ProjectService()


@app.command("create-project")
def create_project(name: str, description: str, domain_type: DomainType) -> None:
    project = service.create_project(
        ProjectCreateRequest(name=name, description=description, domain_type=domain_type)
    )
    typer.echo(json.dumps(project.model_dump(mode="json"), indent=2))


@app.command("start-session")
def start_session(project_id: str) -> None:
    session = service.create_setup_session(project_id)
    typer.echo(json.dumps(session.model_dump(mode="json"), indent=2))


@app.command("show-draft")
def show_draft(project_id: str) -> None:
    draft = service.get_worldmatrix_draft(project_id)
    typer.echo(json.dumps(draft.model_dump(mode="json"), indent=2))


def main() -> None:
    app()
