from __future__ import annotations

import json

import typer

from pyscrai.application.services import ProjectService
from pyscrai.contracts.models import (
    ProjectBootstrapRequest,
    ProjectCreateRequest,
    ScenarioCreateRequest,
    SetupMessageRequest,
    SetupSession,
    SimulationRunRequest,
    WorldBranchCreateRequest,
)
from pyscrai.domain.enums import DomainType

app = typer.Typer(add_completion=False, help="PyScrAI CLI")
service = ProjectService()


def _emit(payload: object) -> None:
    typer.echo(json.dumps(payload, indent=2))


def _parse_key_values(items: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise typer.BadParameter(f"Expected key=value input, got: {item}")
        key, value = item.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def _session_summary_payload(session: SetupSession) -> dict[str, object]:
    data = session.model_dump(mode="json")
    next_question = (
        data["pending_questions"][0]["prompt"] if data["pending_questions"] else None
    )
    return {
        "session_id": data["id"],
        "phase": data["phase"],
        "next_question": next_question,
        "extracted_facts": data["extracted_facts"],
    }


@app.command("create-project")
def create_project(name: str, description: str, domain_type: DomainType) -> None:
    project = service.create_project(
        ProjectCreateRequest(
            name=name, description=description, domain_type=domain_type
        )
    )
    _emit(project.model_dump(mode="json"))


@app.command("list-projects")
def list_projects() -> None:
    projects = service.list_projects()
    _emit([project.model_dump(mode="json") for project in projects])


@app.command("show-project")
def show_project(project_id: str) -> None:
    project = service.get_project(project_id)
    _emit(project.model_dump(mode="json"))


@app.command("bootstrap-project")
def bootstrap_project(
    prompt: str,
    operator: str | None = typer.Option(default=None, help="Optional operator label."),
    name: str | None = typer.Option(
        default=None, help="Override generated project name."
    ),
    domain_type_hint: DomainType | None = typer.Option(
        default=None, help="Optional domain override."
    ),
) -> None:
    response = service.bootstrap_project(
        ProjectBootstrapRequest(
            prompt=prompt,
            operator=operator,
            name=name,
            domain_type_hint=domain_type_hint,
        )
    )
    _emit(response.model_dump(mode="json"))


@app.command("start-session")
def start_session(project_id: str) -> None:
    session = service.create_setup_session(project_id)
    _emit(session.model_dump(mode="json"))


@app.command("add-setup-message")
def add_setup_message(session_id: str, content: str) -> None:
    session = service.add_setup_message(
        session_id, SetupMessageRequest(role="operator", content=content)
    )
    _emit(session.model_dump(mode="json"))


@app.command("show-session")
def show_session(session_id: str) -> None:
    session = service.get_setup_session(session_id)
    _emit(session.model_dump(mode="json"))


@app.command("guided-setup")
def guided_setup(
    session_id: str,
    max_turns: int = typer.Option(default=5, min=1, max=50),
    exit_word: str = typer.Option(
        default="done", help="Type this answer to stop early."
    ),
) -> None:
    session = service.get_setup_session(session_id)
    for _ in range(max_turns):
        summary = _session_summary_payload(session)
        _emit(summary)
        if not summary["next_question"]:
            break
        answer = typer.prompt(str(summary["next_question"]))
        if answer.strip().casefold() == exit_word.casefold():
            break
        session = service.add_setup_message(
            session_id, SetupMessageRequest(role="operator", content=answer)
        )
    _emit(session.model_dump(mode="json"))


@app.command("show-draft")
def show_draft(project_id: str) -> None:
    draft = service.get_worldmatrix_draft(project_id)
    _emit(draft.model_dump(mode="json"))


@app.command("validate-draft")
def validate_draft(project_id: str) -> None:
    validation = service.validate_worldmatrix_draft(project_id)
    _emit(validation.model_dump(mode="json"))


@app.command("compile-worldmatrix")
def compile_worldmatrix(project_id: str) -> None:
    worldmatrix = service.compile_worldmatrix(project_id)
    _emit(worldmatrix.model_dump(mode="json"))


@app.command("create-branch")
def create_branch(
    worldmatrix_id: str,
    title: str,
    modification: list[str] | None = typer.Option(
        default=None, help="Repeatable branch modification."
    ),
    initial_condition: list[str] | None = typer.Option(
        default=None, help="Repeatable initial condition."
    ),
    branch_notes: str = typer.Option(default="", help="Branch note."),
) -> None:
    branch = service.create_worldbranch(
        worldmatrix_id,
        WorldBranchCreateRequest(
            title=title,
            modifications=modification or [],
            initial_conditions=initial_condition or [],
            branch_notes=branch_notes,
        ),
    )
    _emit(branch.model_dump(mode="json"))


@app.command("create-scenario")
def create_scenario(
    branch_id: str,
    binding: list[str] | None = typer.Option(
        default=None, help="Repeatable role=actor mapping."
    ),
    state: list[str] | None = typer.Option(
        default=None, help="Repeatable key=value initial state."
    ),
    stop_condition: list[str] | None = typer.Option(
        default=None, help="Repeatable stop condition."
    ),
) -> None:
    scenario = service.create_scenario(
        branch_id,
        ScenarioCreateRequest(
            actor_bindings=_parse_key_values(binding or []),
            initial_state=_parse_key_values(state or []),
            stop_conditions=stop_condition or [],
        ),
    )
    _emit(scenario.model_dump(mode="json"))


@app.command("run-scenario")
def run_scenario(
    scenario_id: str,
    turn_limit: int | None = typer.Option(default=None, min=1, max=50),
    objective: str = typer.Option(default="stability_probe"),
    inject_event: list[str] | None = typer.Option(
        default=None, help="Repeatable injected event."
    ),
) -> None:
    run = service.run_scenario(
        scenario_id,
        SimulationRunRequest(
            turn_limit=turn_limit, objective=objective, inject_events=inject_event or []
        ),
    )
    _emit(run.model_dump(mode="json"))


@app.command("show-run")
def show_run(run_id: str) -> None:
    run = service.get_simulation_run(run_id)
    _emit(run.model_dump(mode="json"))


def main() -> None:
    app()
