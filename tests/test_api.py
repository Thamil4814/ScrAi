from fastapi.testclient import TestClient

from pyscrai.interfaces.api import app

client = TestClient(app)


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
    session_id = session_response.json()["id"]

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
    assert "Time scope: near-future" in session_payload["extracted_facts"]
    assert "Spatial scope: the Persian Gulf" in session_payload["extracted_facts"]

    draft_response = client.get(f"/projects/{project_id}/worldmatrix-draft")
    assert draft_response.status_code == 200
    draft_payload = draft_response.json()
    assert draft_payload["domain"]["time_scope"] == "near-future"
    assert draft_payload["domain"]["spatial_scope"] == "the Persian Gulf"
    assert draft_payload["environment"]["locations"] == ["the Persian Gulf"]

    validate_response = client.post(f"/projects/{project_id}/worldmatrix-draft/validate")
    assert validate_response.status_code == 200
    assert validate_response.json()["compile_readiness"] is True

    compile_response = client.post(f"/projects/{project_id}/worldmatrix-draft/compile")
    assert compile_response.status_code == 200
    assert compile_response.json()["project_id"] == project_id


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
    session_id = session_response.json()["id"]
    assert session_response.json()["phase"] == "intent_framing"

    message_response = client.post(
        f"/setup-sessions/{session_id}/messages",
        json={
            "role": "operator",
            "content": (
                "The world is a near-future crisis in the Persian Gulf. "
                "Actors include Admiral Rana and Mossad Liaison. "
                "Polities include Iran, Israel, and the United States. "
                "Rules include avoid open war. "
                "Forbidden actions: nuclear first strike. "
                "Operator role is director. "
                "Public knows shipping lanes are threatened. "
                "Contested claims: who sabotaged the tanker."
            ),
        },
    )
    assert message_response.status_code == 200
    session_payload = message_response.json()
    assert session_payload["phase"] == "validation_pass"
    assert "Entities: Admiral Rana, Mossad Liaison" in session_payload["extracted_facts"]
    assert "Polities: Iran, Israel, the United States" in session_payload["extracted_facts"]

    draft_response = client.get(f"/projects/{project_id}/worldmatrix-draft")
    assert draft_response.status_code == 200
    draft_payload = draft_response.json()

    assert draft_payload["operator_role"]["mode"] == "director"
    assert [entity["name"] for entity in draft_payload["entities"]] == ["Admiral Rana", "Mossad Liaison"]
    assert [polity["name"] for polity in draft_payload["polities"]] == ["Iran", "Israel", "the United States"]
    assert len(draft_payload["rules"]) == 2
    assert draft_payload["knowledge_layers"]["public_knowledge"] == ["shipping lanes are threatened"]
    assert draft_payload["knowledge_layers"]["contested_claims"] == ["who sabotaged the tanker"]
