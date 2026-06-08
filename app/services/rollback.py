from uuid import uuid4

from app.models import (
    Deployment,
    DeploymentStatus,
    RollbackPlan,
    RollbackRequest,
    RollbackResult,
    RollbackStrategy,
)


class RollbackManager:
    def __init__(self) -> None:
        self._deployments: list[Deployment] = [
            Deployment(
                version="v1.4.2",
                image="registry.example.com/rollback-demo:v1.4.2",
                status=DeploymentStatus.failed,
                deployed_at="2026-06-09T01:10:00Z",
                smoke_tests_passed=False,
                error_rate=14.2,
                notes="Checkout latency regression detected after release.",
            ),
            Deployment(
                version="v1.4.1",
                image="registry.example.com/rollback-demo:v1.4.1",
                status=DeploymentStatus.healthy,
                deployed_at="2026-06-08T18:35:00Z",
                smoke_tests_passed=True,
                error_rate=0.8,
                notes="Last known stable production release.",
            ),
            Deployment(
                version="v1.4.0",
                image="registry.example.com/rollback-demo:v1.4.0",
                status=DeploymentStatus.healthy,
                deployed_at="2026-06-07T22:05:00Z",
                smoke_tests_passed=True,
                error_rate=1.1,
                notes="Previous stable release.",
            ),
        ]
        self._active_version = "v1.4.2"

    def list_deployments(self) -> list[Deployment]:
        return self._deployments

    def active_deployment(self) -> Deployment:
        return self._find_deployment(self._active_version)

    def create_plan(self, request: RollbackRequest) -> RollbackPlan:
        self._find_deployment(request.failed_version)
        target = self._resolve_target(request.target_version, request.failed_version)

        return RollbackPlan(
            failed_version=request.failed_version,
            target_version=target.version,
            strategy=request.strategy,
            commands=self._commands(request.strategy, target),
            checks=[
                "Run smoke tests against the restored version.",
                "Check production error rate and latency dashboards.",
                "Verify the deployment audit trail contains the rollback record.",
            ],
            estimated_minutes=self._estimated_minutes(request.strategy),
        )

    def execute_rollback(self, request: RollbackRequest) -> RollbackResult:
        plan = self.create_plan(request)
        failed = self._find_deployment(request.failed_version)
        target = self._find_deployment(plan.target_version)

        failed.status = DeploymentStatus.rolled_back
        self._active_version = target.version

        return RollbackResult(
            rollback_id=f"rb-{uuid4().hex[:10]}",
            status="completed",
            failed_version=failed.version,
            active_version=target.version,
            strategy=request.strategy,
            reason=request.reason,
            requested_by=request.requested_by,
            commands=plan.commands,
            verification=plan.checks,
        )

    def _resolve_target(
        self,
        target_version: str | None,
        failed_version: str,
    ) -> Deployment:
        if target_version:
            target = self._find_deployment(target_version)
            if target.version == failed_version:
                raise ValueError("Rollback target must be different from the failed version.")
            if target.status not in {DeploymentStatus.healthy, DeploymentStatus.rolled_back}:
                raise ValueError("Rollback target must be a healthy or previously rolled back version.")
            return target

        for deployment in self._deployments:
            if deployment.version != failed_version and deployment.status == DeploymentStatus.healthy:
                return deployment

        raise ValueError("No healthy rollback target is available.")

    def _find_deployment(self, version: str) -> Deployment:
        for deployment in self._deployments:
            if deployment.version == version:
                return deployment
        raise ValueError(f"Unknown deployment version: {version}")

    def _commands(self, strategy: RollbackStrategy, target: Deployment) -> list[str]:
        if strategy == RollbackStrategy.blue_green:
            return [
                f"kubectl set image deployment/rollback-demo app={target.image} --record",
                "kubectl rollout status deployment/rollback-demo",
                "kubectl patch service rollback-demo -p '{\"spec\":{\"selector\":{\"slot\":\"green\"}}}'",
            ]
        if strategy == RollbackStrategy.canary:
            return [
                f"kubectl set image deployment/rollback-demo-canary app={target.image} --record",
                "kubectl rollout status deployment/rollback-demo-canary",
                "kubectl scale deployment/rollback-demo --replicas=0",
                "kubectl scale deployment/rollback-demo-canary --replicas=3",
            ]
        return [
            f"kubectl set image deployment/rollback-demo app={target.image} --record",
            "kubectl rollout undo deployment/rollback-demo",
            "kubectl rollout status deployment/rollback-demo",
        ]

    def _estimated_minutes(self, strategy: RollbackStrategy) -> int:
        estimates = {
            RollbackStrategy.immediate: 3,
            RollbackStrategy.blue_green: 8,
            RollbackStrategy.canary: 12,
        }
        return estimates[strategy]
