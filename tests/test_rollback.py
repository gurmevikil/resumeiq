import pytest

from app.models import RollbackRequest, RollbackStrategy
from app.services.rollback import RollbackManager


def test_plan_uses_latest_healthy_version_when_target_is_omitted() -> None:
    manager = RollbackManager()

    plan = manager.create_plan(
        RollbackRequest(
            failed_version="v1.4.2",
            strategy=RollbackStrategy.immediate,
            reason="Smoke tests failed after deployment.",
            requested_by="ci-pipeline",
        )
    )

    assert plan.target_version == "v1.4.1"
    assert plan.estimated_minutes == 3
    assert any("kubectl" in command for command in plan.commands)


def test_execute_rollback_changes_active_version() -> None:
    manager = RollbackManager()

    result = manager.execute_rollback(
        RollbackRequest(
            failed_version="v1.4.2",
            target_version="v1.4.0",
            strategy=RollbackStrategy.blue_green,
            reason="Error rate exceeded the production rollback threshold.",
            requested_by="release-manager",
        )
    )

    assert result.status == "completed"
    assert result.active_version == "v1.4.0"
    assert manager.active_deployment().version == "v1.4.0"


def test_rejects_failed_version_as_rollback_target() -> None:
    manager = RollbackManager()

    with pytest.raises(ValueError, match="target must be different"):
        manager.create_plan(
            RollbackRequest(
                failed_version="v1.4.2",
                target_version="v1.4.2",
                reason="Rollback target was entered incorrectly.",
                requested_by="ci-pipeline",
            )
        )
