import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
ECS = ROOT / "deploy" / "ecs"


def read_json(name: str) -> dict:
    return json.loads((ECS / name).read_text())


def test_task_definition_runs_hardened_fastapi_container():
    """Catch task revisions that expose the wrong port or run with writable root access."""
    task = read_json("task-definition.json")
    container = task["containerDefinitions"][0]

    assert task["requiresCompatibilities"] == ["FARGATE"]
    assert task["networkMode"] == "awsvpc"
    assert container["name"] == "cicd-book-api"
    assert container["portMappings"] == [{"containerPort": 8000, "protocol": "tcp"}]
    assert container["readonlyRootFilesystem"] is True
    assert container["user"] == "10001"
    assert container["healthCheck"]["command"][0] == "CMD-SHELL"
    assert "http://127.0.0.1:8000/health" in container["healthCheck"]["command"][-1]
    assert container["logConfiguration"]["logDriver"] == "awslogs"


def test_service_uses_ecs_native_blue_green_with_two_target_groups():
    """Catch services that silently fall back to rolling or omit the green target group."""
    service = read_json("service-definition.json")
    deployment = service["deploymentConfiguration"]
    load_balancer = service["loadBalancers"][0]
    advanced = load_balancer["advancedConfiguration"]

    assert service["deploymentController"] == {"type": "ECS"}
    assert deployment["strategy"] == "BLUE_GREEN"
    assert deployment["bakeTimeInMinutes"] == 2
    assert load_balancer["targetGroupArn"] == "${BLUE_TARGET_GROUP_ARN}"
    assert advanced["alternateTargetGroupArn"] == "${GREEN_TARGET_GROUP_ARN}"
    assert advanced["productionListenerRule"] == "${PRODUCTION_LISTENER_RULE_ARN}"
    assert advanced["testListenerRule"] == "${TEST_LISTENER_RULE_ARN}"


def test_image_is_traceable_to_a_git_commit():
    """Catch deployments that use only the mutable latest image tag."""
    task = read_json("task-definition.json")
    image = task["containerDefinitions"][0]["image"]

    assert image == (
        "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/"
        "${ECR_REPOSITORY}:${IMAGE_TAG}"
    )
    assert "latest" not in image


def test_deployment_configuration_enables_automatic_rollback():
    """Catch blue/green deployments that detect failures but cannot restore blue."""
    deployment = read_json("deployment-configuration.json")

    assert deployment["strategy"] == "BLUE_GREEN"
    assert deployment["deploymentCircuitBreaker"] == {"enable": True, "rollback": True}
    assert deployment["alarms"]["enable"] is True
    assert deployment["alarms"]["rollback"] is True
