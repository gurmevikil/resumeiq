from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_endpoint() -> None:
    response = client.post(
        "/analyze",
        json={
            "resume_text": (
                "Python backend developer with FastAPI, NLP, machine learning, "
                "Scikit-learn, REST APIs, and similarity scoring experience."
            ),
            "job_description": (
                "Hiring Python developer with FastAPI, NLP, Scikit-learn, "
                "REST APIs, keyword extraction, and resume matching experience."
            ),
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["match_score"] > 0
    assert "recommendations" in body
