from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_create_plan_from_text_returns_grouped_plan() -> None:
    response = client.post(
        "/plans/from-text",
        json={
            "text": "Create a production deployment plan for a 5-node Kubernetes cluster with monitoring and backup enabled.",
            "source": "text",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"]["intent"] == "create_deployment_plan"
    assert payload["target_environment"] == "production"
    assert payload["risk_level"] == "high"
    assert len(payload["groups"]) >= 5
    assert len(payload["tasks"]) >= 5
    assert payload["dependencies"]


def test_get_plan_returns_saved_plan() -> None:
    create_response = client.post(
        "/plans/from-text",
        json={"text": "Create a staging deployment plan for a 2-node cluster.", "source": "text"},
    )
    plan_id = create_response.json()["plan_metadata"]["plan_id"]

    response = client.get(f"/plans/{plan_id}")
    assert response.status_code == 200
    assert response.json()["plan_metadata"]["plan_id"] == plan_id
