from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_create_plan_from_text_returns_grouped_plan() -> None:
    response = client.post(
        "/plans/from-text",
        json={
            "text": "Create a production deployment plan for a 5-node Kubernetes cluster with monitoring and backup enabled.",
            "source": "text",
            "allow_clarification": False,
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
        json={
            "text": "Create a staging Kubernetes deployment plan for a 2-node cluster.",
            "source": "text",
            "allow_clarification": False,
        },
    )
    plan_id = create_response.json()["plan_metadata"]["plan_id"]

    response = client.get(f"/plans/{plan_id}")
    assert response.status_code == 200
    assert response.json()["plan_metadata"]["plan_id"] == plan_id


def test_ambiguous_request_returns_clarification() -> None:
    response = client.post(
        "/plans/from-text",
        json={
            "text": "Create a staging deployment plan for a 3-node Kubernetes cluster with monitoring, backup, and rollback.",
            "source": "text",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "needs_clarification"
    assert payload["session_id"]
    assert "intent" in payload["missing_fields"]


def test_session_answers_finalize_plan() -> None:
    initial = client.post(
        "/plans/from-text",
        json={"text": "Create a Kubernetes deployment plan for production.", "source": "text"},
    )

    initial_payload = initial.json()
    assert initial_payload["status"] == "needs_clarification"

    default_answers = {
        "intent": "create_deployment_plan",
        "cluster_size": "5",
        "rollback_required": "yes",
        "environment": "production",
        "target_platform": "kubernetes",
    }
    answers = [
        {"question_id": question["id"], "answer": default_answers[question["field_name"]]}
        for question in initial_payload["questions"]
    ]

    response = client.post(
        f"/plans/sessions/{initial_payload['session_id']}/answer",
        json={"answers": answers},
    )

    assert response.status_code == 200
    payload = response.json()
    if payload.get("status") == "needs_clarification":
        second_answers = [
            {"question_id": question["id"], "answer": default_answers[question["field_name"]]}
            for question in payload["questions"]
        ]
        response = client.post(
            f"/plans/sessions/{initial_payload['session_id']}/answer",
            json={"answers": second_answers},
        )
        payload = response.json()

    assert payload["target_environment"] == "production"
    assert payload["entities"]["target_platform"] == "kubernetes"
    assert payload["entities"]["cluster_size"] == 5
    assert payload["strategy_source"] in {"template", "retrieval_hybrid"}
