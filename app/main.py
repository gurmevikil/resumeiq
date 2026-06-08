from fastapi import FastAPI, HTTPException

from app.models import Deployment, HealthResponse, RollbackPlan, RollbackRequest, RollbackResult
from app.services.rollback import RollbackManager

app = FastAPI(
    title="Rollback CI/CD Automation",
    description=(
        "A deployment rollback API that demonstrates how CI/CD systems can detect "
        "failed releases, choose the last stable version, and execute a controlled rollback."
    ),
    version="1.0.0",
)

rollback_manager = RollbackManager()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="rollback-cicd")


@app.get("/deployments", response_model=list[Deployment])
def list_deployments() -> list[Deployment]:
    return rollback_manager.list_deployments()


@app.get("/deployments/active", response_model=Deployment)
def active_deployment() -> Deployment:
    return rollback_manager.active_deployment()


@app.post("/rollback/plan", response_model=RollbackPlan)
def plan_rollback(payload: RollbackRequest) -> RollbackPlan:
    try:
        return rollback_manager.create_plan(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rollback/execute", response_model=RollbackResult)
def execute_rollback(payload: RollbackRequest) -> RollbackResult:
    try:
        return rollback_manager.execute_rollback(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
