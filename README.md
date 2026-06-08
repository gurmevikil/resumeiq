# Rollback CI/CD Automation

Rollback CI/CD Automation is a FastAPI project that demonstrates how a delivery pipeline can detect a bad release, select the last stable deployment, generate a rollback plan, and execute a controlled rollback. It is designed as a practical DevOps portfolio project with application code, automated tests, Docker support, a GitHub Actions workflow, sample rollback payloads, and clear documentation.

## Project Description

Modern CI/CD pipelines should not stop at building and deploying code. They also need a recovery path when a deployment causes failed smoke tests, high error rates, latency spikes, or broken user journeys. This project models that recovery process with a small rollback service.

The API stores a sample deployment history, identifies healthy and failed versions, creates rollback commands for different strategies, and records the active version after rollback execution. The included workflow shows the full delivery path:

1. Run automated tests.
2. Build the Docker image.
3. Deploy the new version.
4. Run smoke checks.
5. Trigger rollback automatically if deployment verification fails.

## Features

- FastAPI backend for deployment and rollback operations
- Deployment history with version, image, status, smoke-test result, and error-rate data
- Automatic rollback target selection using the latest healthy release
- Rollback planning endpoint that returns commands, checks, and estimated duration
- Rollback execution endpoint that updates the active deployment
- Supports immediate, blue-green, and canary rollback strategies
- Dockerfile for containerized deployment
- GitHub Actions workflow for test, build, deploy, smoke test, and rollback stages
- Shell rollback script that mirrors Kubernetes rollback commands
- Unit and API tests with Pytest

## Tech Stack

- Python 3.12
- FastAPI
- Pydantic
- Pytest
- Docker
- GitHub Actions
- Kubernetes-style deployment commands

## Project Structure

```text
.github/
  workflows/
    cicd-rollback.yml      CI/CD workflow with rollback stage
app/
  main.py                  FastAPI routes
  models.py                API request and response schemas
  services/
    rollback.py            Rollback planning and execution logic
samples/
  deployment-history.json  Example deployment history
  rollback-request.json    Example rollback request payload
scripts/
  rollback.sh              Rollback command script for CI/CD
tests/
  test_api.py              API endpoint tests
  test_rollback.py         Rollback service tests
Dockerfile
requirements.txt
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run The API

```powershell
uvicorn app.main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

```http
GET /health
```

### List Deployments

```http
GET /deployments
```

### Get Active Deployment

```http
GET /deployments/active
```

### Create Rollback Plan

```http
POST /rollback/plan
```

Example request:

```json
{
  "failed_version": "v1.4.2",
  "target_version": "v1.4.1",
  "strategy": "immediate",
  "reason": "Smoke tests failed and production error rate exceeded the rollback threshold.",
  "requested_by": "github-actions"
}
```

### Execute Rollback

```http
POST /rollback/execute
```

This endpoint validates the failed version, chooses the requested or latest healthy target version, marks the failed deployment as rolled back, and returns the rollback record.

## Try With PowerShell

```powershell
$body = Get-Content .\samples\rollback-request.json -Raw
Invoke-RestMethod -Uri http://127.0.0.1:8000/rollback/plan -Method Post -Body $body -ContentType "application/json"
```

```powershell
$body = Get-Content .\samples\rollback-request.json -Raw
Invoke-RestMethod -Uri http://127.0.0.1:8000/rollback/execute -Method Post -Body $body -ContentType "application/json"
```

## Run Tests

```powershell
pytest
```

## Run With Docker

```powershell
docker build -t rollback-cicd-demo .
docker run --rm -p 8000:8000 rollback-cicd-demo
```

## CI/CD Rollback Flow

The workflow in `.github/workflows/cicd-rollback.yml` demonstrates a production-style pipeline:

1. `test`: installs dependencies and runs Pytest.
2. `build`: builds a Docker image tagged with the commit SHA.
3. `deploy`: captures the previous stable version, deploys the new image, and runs smoke tests.
4. `rollback`: if deployment verification fails, the workflow calls `scripts/rollback.sh` with the failed version, target version, and rollback reason.

The workflow uses `echo` for Kubernetes commands so the project can run safely without a real cluster. In a production setup, replace those lines with real `kubectl`, Helm, Argo CD, or Terraform commands and configure secrets such as `KUBE_CONFIG`, registry credentials, and environment-specific URLs.

## Rollback Strategies

- `immediate`: quickly restores the stable image on the existing deployment.
- `blue_green`: deploys the stable image to the alternate slot, verifies it, and switches traffic.
- `canary`: restores a stable canary deployment, verifies it, then scales traffic back to the stable version.

## Future Improvements

- Persist deployment history in a database
- Add Prometheus or Datadog metrics checks
- Integrate Slack or email rollback notifications
- Add approval gates for production rollbacks
- Connect to Helm, Argo CD, or GitOps pull request rollback flows
