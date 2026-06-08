#!/usr/bin/env bash
set -euo pipefail

FAILED_VERSION="${1:?failed version is required}"
TARGET_VERSION="${2:?target version is required}"
REASON="${3:-Automatic rollback triggered by CI/CD failure}"
DEPLOYMENT_NAME="${DEPLOYMENT_NAME:-rollback-demo}"
IMAGE_NAME="${IMAGE_NAME:-rollback-cicd-demo}"

echo "Rollback started"
echo "Failed version: ${FAILED_VERSION}"
echo "Target version: ${TARGET_VERSION}"
echo "Reason: ${REASON}"

echo "kubectl set image deployment/${DEPLOYMENT_NAME} app=${IMAGE_NAME}:${TARGET_VERSION} --record"
echo "kubectl rollout status deployment/${DEPLOYMENT_NAME} --timeout=120s"
echo "kubectl annotate deployment/${DEPLOYMENT_NAME} rollback.reason=\"${REASON}\" --overwrite"

echo "Rollback completed"
