from fastapi.testclient import TestClient
from pathlib import Path

from pyscrai.interfaces.api import app

client = TestClient(app)


def test_bootstrap_project_from_prompt() -> None:
    bootstrap_response = client.post(
        "/projects/bootstrap",
        json={
            "prompt": "Build a near-future Gulf crisis simulation in the Persian Gulf with maritime escalation.",
            "operator": "architect",
        },
    )
    assert bootstrap_response.status_code == 200
    payload = bootstrap_response.json()

    assert payload["project"]["domain_type"] == "geopolitical"
    assert payload["project"]["name"].startswith(
        "near-future Gulf crisis simulation in the Persian Gulf"
    )
    assert payload["project"]["name"].endswith("...")
    assert payload["setup_session"]["phase"] == "world_population"
    assert payload["setup_session"]["transcript"][-1]["role"] == "architect"
    assert payload["draft"]["environment"]["description"].startswith(
        "Build a near-future Gulf crisis"
    )
    assert payload["draft"]["domain"]["time_scope"] == "near-future"
    assert payload["draft"]["domain"]["spatial_scope"] == "the Persian Gulf"
    assert payload["draft"]["validation"]["compile_readiness"] is False
    assert any(
        item["source"] == "bootstrap.domain_inference"
        for item in payload["draft"]["provenance"]
    )


def test_project_setup_flow() -> None:
    project_response = client.post(
        "/projects",
        json={
            "name": "Regional crisis sim",
            "description": "A constrained geopolitical crisis setup.",
            "domain_type": "geopolitical",
            "operator": "architect",
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    session_response = client.post(f"/projects/{project_id}/setup-sessions")
    assert session_response.status_code == 200
    session_payload = session_response.json()
    session_id = session_payload["id"]
    assert session_payload["phase"] == "intent_framing"
    assert session_payload["transcript"][-1]["role"] == "architect"

    compile_response = client.post(f"/projects/{project_id}/worldmatrix-draft/compile")
    assert compile_response.status_code == 409

    message_response = client.post(
        f"/setup-sessions/{session_id}/messages",
        json={
            "role": "operator",
            "content": "The world is a near-future Gulf crisis in the Persian Gulf centered on maritime escalation.",
        },
    )
    assert message_response.status_code == 200
    session_payload = message_response.json()
    assert session_payload["phase"] == "world_population"
    assert "Time scope: near-future" in session_payload["extracted_facts"]
    assert "Spatial scope: the Persian Gulf" in session_payload["extracted_facts"]
    assert session_payload["transcript"][-1]["role"] == "architect"
    assert (
        "Who are the key actors or entities"
        in session_payload["transcript"][-1]["content"]
    )

    draft_response = client.get(f"/projects/{project_id}/worldmatrix-draft")
    assert draft_response.status_code == 200
    draft_payload = draft_response.json()
    assert draft_payload["domain"]["time_scope"] == "near-future"
    assert draft_payload["domain"]["spatial_scope"] == "the Persian Gulf"
    assert draft_payload["environment"]["locations"] == ["the Persian Gulf"]

    validate_response = client.post(
        f"/projects/{project_id}/worldmatrix-draft/validate"
    )
    assert validate_response.status_code == 200
    assert validate_response.json()["compile_readiness"] is False

    population_response = client.post(
        f"/setup-sessions/{session_id}/messages",
        json={
            "role": "operator",
            "content": "Actors include Admiral Rana. Polities include Iran and the United States.",
        },
    )
    assert population_response.status_code == 200
    assert population_response.json()["phase"] == "rules_and_knowledge_boundaries"

    rules_response = client.post(
        f"/setup-sessions/{session_id}/messages",
        json={
            "role": "operator",
            "content": "Rules include avoid open war. Public knows shipping lanes are threatened.",
        },
    )
    assert rules_response.status_code == 200
    assert rules_response.json()["phase"] == "validation_pass"

    validate_response = client.post(
        f"/projects/{project_id}/worldmatrix-draft/validate"
    )
    assert validate_response.status_code == 200
    assert validate_response.json()["compile_readiness"] is True

    compile_response = client.post(f"/projects/{project_id}/worldmatrix-draft/compile")
    assert compile_response.status_code == 200
    worldmatrix_payload = compile_response.json()
    assert worldmatrix_payload["project_id"] == project_id
    worldmatrix_id = worldmatrix_payload["id"]

    project_get_response = client.get(f"/projects/{project_id}")
    assert project_get_response.status_code == 200
    assert project_get_response.json()["id"] == project_id

    projects_response = client.get("/projects")
    assert projects_response.status_code == 200
    assert any(project["id"] == project_id for project in projects_response.json())

    bundle_dir = Path("artifacts/projects") / project_id / "compiled" / worldmatrix_id
    assert (bundle_dir / "worldmatrix.json").exists()
    assert (bundle_dir / "validation_report.json").exists()
    assert (bundle_dir / "provenance_manifest.json").exists()
    assert (bundle_dir / "compile_metadata.json").exists()


def test_setup_mapper_populates_multiple_worldmatrix_sections() -> None:
    project_response = client.post(
        "/projects",
        json={
            "name": "Escalation ladder sim",
            "description": "A compact regional escalation model.",
            "domain_type": "geopolitical",
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    session_response = client.post(f"/projects/{project_id}/setup-sessions")
    assert session_response.status_code == 200
    session_payload = session_response.json()
    session_id = session_payload["id"]
    assert session_payload["phase"] == "intent_framing"
    assert (
        "What is the core environment or situation"
        in session_payload["transcript"][-1]["content"]
    )

    framing_response = client.post(
        f"/setup-sessions/{session_id}/messages",
        json={
            "role": "operator",
            "content": "The world is a near-future crisis in the Persian Gulf.",
        },
    )
    assert framing_response.status_code == 200
    framing_payload = framing_response.json()
    assert framing_payload["phase"] == "world_population"
    assert (
        "Who are the key actors or entities"
        in framing_payload["transcript"][-1]["content"]
    )

    population_response = client.post(
        f"/setup-sessions/{session_id}/messages",
        json={
            "role": "operator",
            "content": "Actors include Admiral Rana and Mossad Liaison. Polities include Iran, Israel, and the United States.",
        },
    )
    assert population_response.status_code == 200
    population_payload = population_response.json()
    assert population_payload["phase"] == "rules_and_knowledge_boundaries"
    assert (
        "Entities: Admiral Rana, Mossad Liaison"
        in population_payload["extracted_facts"]
    )
    assert (
        "Polities: Iran, Israel, the United States"
        in population_payload["extracted_facts"]
    )
    assert (
        "What rules, constraints, or forbidden actions"
        in population_payload["transcript"][-1]["content"]
    )

    rules_response = client.post(
        f"/setup-sessions/{session_id}/messages",
        json={
            "role": "operator",
            "content": (
                "Rules include avoid open war. "
                "Forbidden actions: nuclear first strike. "
                "Operator role is director. "
                "Public knows shipping lanes are threatened. "
                "Contested claims: who sabotaged the tanker."
            ),
        },
    )
    assert rules_response.status_code == 200
    rules_payload = rules_response.json()
    assert rules_payload["phase"] == "validation_pass"
    assert (
        "The current draft is compile-ready"
        in rules_payload["transcript"][-1]["content"]
    )

    draft_response = client.get(f"/projects/{project_id}/worldmatrix-draft")
    assert draft_response.status_code == 200
    draft_payload = draft_response.json()

    assert draft_payload["operator_role"]["mode"] == "director"
    assert [entity["name"] for entity in draft_payload["entities"]] == [
        "Admiral Rana",
        "Mossad Liaison",
    ]
    assert [polity["name"] for polity in draft_payload["polities"]] == [
        "Iran",
        "Israel",
        "the United States",
    ]
    assert len(draft_payload["rules"]) == 2
    assert draft_payload["knowledge_layers"]["public_knowledge"] == [
        "shipping lanes are threatened"
    ]
    assert draft_payload["knowledge_layers"]["contested_claims"] == [
        "who sabotaged the tanker"
    ]


def test_worldmatrix_branch_scenario_vertical_slice() -> None:
    project_response = client.post(
        "/projects",
        json={
            "name": "Milestone 2 scenario derivation",
            "description": "Thin vertical slice for branch and scenario creation.",
            "domain_type": "social",
        },
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    session_response = client.post(f"/projects/{project_id}/setup-sessions")
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    message_response = client.post(
        f"/setup-sessions/{session_id}/messages",
        json={
            "role": "operator",
            "content": "The world is a present-day social conflict in Boston.",
        },
    )
    assert message_response.status_code == 200

    population_response = client.post(
        f"/setup-sessions/{session_id}/messages",
        json={
            "role": "operator",
            "content": "Actors include Alice and Bob. Polities include Harbor Union.",
        },
    )
    assert population_response.status_code == 200

    rules_response = client.post(
        f"/setup-sessions/{session_id}/messages",
        json={
            "role": "operator",
            "content": "Rules include avoid public violence. Public knows tensions are rising.",
        },
    )
    assert rules_response.status_code == 200

    compile_response = client.post(f"/projects/{project_id}/worldmatrix-draft/compile")
    assert compile_response.status_code == 200
    worldmatrix_id = compile_response.json()["id"]

    worldmatrix_response = client.get(f"/worldmatrices/{worldmatrix_id}")
    assert worldmatrix_response.status_code == 200
    assert worldmatrix_response.json()["id"] == worldmatrix_id

    branch_response = client.post(
        f"/worldmatrices/{worldmatrix_id}/branches",
        json={
            "title": "Escalation branch",
            "modifications": ["Increase social media misinformation velocity."],
            "initial_conditions": ["A leaked recording goes viral."],
            "branch_notes": "Used for high-tension rehearsal.",
        },
    )
    assert branch_response.status_code == 200
    branch_payload = branch_response.json()
    assert branch_payload["worldmatrix_id"] == worldmatrix_id
    branch_id = branch_payload["id"]

    scenario_response = client.post(
        f"/branches/{branch_id}/scenarios",
        json={
            "actor_bindings": {"protagonist": "alice", "antagonist": "bob"},
            "initial_state": {"tension": "high"},
            "stop_conditions": ["de-escalation reached", "turn_limit=10"],
            "evaluator_config": {"metric": "stability"},
        },
    )
    assert scenario_response.status_code == 200
    scenario_payload = scenario_response.json()
    scenario_id = scenario_payload["id"]
    assert scenario_payload["worldbranch_id"] == branch_id
    assert scenario_payload["initial_state"]["tension"] == "high"

    scenario_get_response = client.get(f"/scenarios/{scenario_id}")
    assert scenario_get_response.status_code == 200
    assert scenario_get_response.json()["id"] == scenario_id

    run_response = client.post(
        f"/scenarios/{scenario_id}/runs",
        json={
            "turn_limit": 5,
            "objective": "stability_test",
            "inject_events": ["Initial diplomatic warning issued."],
        },
    )
    assert run_response.status_code == 200
    run_payload = run_response.json()
    run_id = run_payload["id"]
    assert run_payload["scenario_id"] == scenario_id
    assert run_payload["result_summary"]["objective"] == "stability_test"
    assert run_payload["result_summary"]["stop_reason"] == "turn_limit_reached"
    assert run_payload["state_snapshots"][-1]["turn"] == "5"
    assert run_payload["event_log"][0]["turn"] == "0"
    assert "stability_score" in run_payload["result_summary"]
    assert int(run_payload["result_summary"]["stability_score"]) >= 0

    run_get_response = client.get(f"/runs/{run_id}")
    assert run_get_response.status_code == 200
    assert run_get_response.json()["id"] == run_id
