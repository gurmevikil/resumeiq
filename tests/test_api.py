from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "rollback-cicd"}


def test_deployments_endpoint_returns_history() -> None:
    response = client.get("/deployments")

    body = response.json()

    assert response.status_code == 200
    assert len(body) >= 2
    assert body[0]["version"] == "v1.4.2"


def test_rollback_plan_endpoint() -> None:
    response = client.post(
        "/rollback/plan",
        json={
            "failed_version": "v1.4.2",
            "strategy": "canary",
            "reason": "The new version failed smoke tests.",
            "requested_by": "github-actions",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["target_version"] == "v1.4.1"
    assert body["strategy"] == "canary"


def test_rollback_execute_endpoint() -> None:
    response = client.post(
        "/rollback/execute",
        json={
            "failed_version": "v1.4.2",
            "target_version": "v1.4.1",
            "strategy": "immediate",
            "reason": "Production error rate exceeded rollback threshold.",
            "requested_by": "release-bot",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "completed"
    assert body["active_version"] == "v1.4.1"
