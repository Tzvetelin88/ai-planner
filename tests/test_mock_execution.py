from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_mock_execution_success() -> None:
    response = client.post(
        "/mock/provision/infra",
        json={"plan_id": "plan-123", "task_id": "provision-infra", "payload": {"environment": "staging"}},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["resource_ids"]
    assert payload["warnings"] == []


def test_mock_execution_failure_returns_remediation() -> None:
    response = client.post(
        "/mock/backup/enable",
        json={
            "plan_id": "plan-456",
            "task_id": "enable-protection",
            "payload": {"message": "simulate timeout fail"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is False
    assert payload["warnings"]
    assert payload["dependency_issues"]
    assert payload["remediation_suggestions"]
