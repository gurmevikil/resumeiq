from enum import StrEnum

from pydantic import BaseModel, Field


class DeploymentStatus(StrEnum):
    healthy = "healthy"
    degraded = "degraded"
    failed = "failed"
    rolled_back = "rolled_back"


class RollbackStrategy(StrEnum):
    immediate = "immediate"
    blue_green = "blue_green"
    canary = "canary"


class HealthResponse(BaseModel):
    status: str
    service: str


class Deployment(BaseModel):
    version: str = Field(..., examples=["v1.4.2"])
    image: str = Field(..., examples=["registry.example.com/orders:v1.4.2"])
    status: DeploymentStatus
    deployed_at: str = Field(..., examples=["2026-06-09T01:10:00Z"])
    smoke_tests_passed: bool
    error_rate: float = Field(..., ge=0, le=100)
    notes: str = ""


class RollbackRequest(BaseModel):
    failed_version: str = Field(..., examples=["v1.4.2"])
    target_version: str | None = Field(
        default=None,
        description="Optional stable version. When omitted, the latest healthy version is used.",
        examples=["v1.4.1"],
    )
    strategy: RollbackStrategy = RollbackStrategy.immediate
    reason: str = Field(..., min_length=8, examples=["Smoke tests failed after release."])
    requested_by: str = Field(..., min_length=2, examples=["release-engineer"])


class RollbackPlan(BaseModel):
    failed_version: str
    target_version: str
    strategy: RollbackStrategy
    commands: list[str]
    checks: list[str]
    estimated_minutes: int


class RollbackResult(BaseModel):
    rollback_id: str
    status: str
    failed_version: str
    active_version: str
    strategy: RollbackStrategy
    reason: str
    requested_by: str
    commands: list[str]
    verification: list[str]
