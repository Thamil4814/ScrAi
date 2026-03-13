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
            "content": "The world is a near-future Gulf crisis centered on maritime escalation.",
        },
    )
    assert message_response.status_code == 200

    validate_response = client.post(f"/projects/{project_id}/worldmatrix-draft/validate")
    assert validate_response.status_code == 200
    assert validate_response.json()["compile_readiness"] is True

    compile_response = client.post(f"/projects/{project_id}/worldmatrix-draft/compile")
    assert compile_response.status_code == 200
    assert compile_response.json()["project_id"] == project_id
