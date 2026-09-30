#!/usr/bin/env bash
set -euo pipefail

require() {
  local name=$1
  [[ -n "${!name:-}" ]] || {
    echo "Required environment variable is missing: $name" >&2
    exit 2
  }
}

require AWS_REGION
require PIPELINE_NAME

export AWS_DEFAULT_REGION="$AWS_REGION"

echo "AWS caller"
aws sts get-caller-identity --query '{Account:Account,Arn:Arn}' --output table

echo "Latest pipeline execution"
aws codepipeline list-pipeline-executions \
  --pipeline-name "$PIPELINE_NAME" \
  --max-results 1 \
  --query 'pipelineExecutionSummaries[0].{Id:pipelineExecutionId,Status:status,Updated:lastUpdateTime}' \
  --output table

if [[ -n "${CODEBUILD_PROJECT_NAME:-}" ]]; then
  build_id="$(aws codebuild list-builds-for-project \
    --project-name "$CODEBUILD_PROJECT_NAME" \
    --sort-order DESCENDING \
    --query 'ids[0]' --output text)"
  aws codebuild batch-get-builds --ids "$build_id" \
    --query 'builds[0].{Id:id,Status:buildStatus,Source:resolvedSourceVersion}' --output table
fi

if [[ -n "${CODEDEPLOY_APPLICATION_NAME:-}" && -n "${CODEDEPLOY_DEPLOYMENT_GROUP_NAME:-}" ]]; then
  deployment_id="$(aws deploy list-deployments \
    --application-name "$CODEDEPLOY_APPLICATION_NAME" \
    --deployment-group-name "$CODEDEPLOY_DEPLOYMENT_GROUP_NAME" \
    --include-only-statuses Succeeded Failed InProgress \
    --query 'deployments[0]' --output text)"
  aws deploy get-deployment --deployment-id "$deployment_id" \
    --query 'deploymentInfo.{Id:deploymentId,Status:status,Revision:revision}' --output table
fi

if [[ -n "${TARGET_GROUP_ARN:-}" ]]; then
  aws elbv2 describe-target-health --target-group-arn "$TARGET_GROUP_ARN" \
    --query 'TargetHealthDescriptions[].{Target:Target.Id,Port:Target.Port,State:TargetHealth.State,Reason:TargetHealth.Reason}' \
    --output table
fi

if [[ -n "${ECS_CLUSTER_NAME:-}" && -n "${ECS_SERVICE_NAME:-}" ]]; then
  aws ecs describe-services \
    --cluster "$ECS_CLUSTER_NAME" \
    --services "$ECS_SERVICE_NAME" \
    --query 'services[0].{Status:status,Desired:desiredCount,Running:runningCount,Deployments:deployments[*].{Status:status,TaskDefinition:taskDefinition}}' \
    --output json
fi

if [[ -n "${APPLICATION_URL:-}" ]]; then
  curl --fail --silent --show-error "$APPLICATION_URL/health"
  echo
  curl --fail --silent --show-error "$APPLICATION_URL/api/version"
  echo
fi

