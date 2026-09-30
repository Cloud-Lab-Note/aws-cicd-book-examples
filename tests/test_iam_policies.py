import json
from pathlib import Path

POLICY_DIR = Path(__file__).parents[1] / "deploy" / "iam" / "policies"
EXPECTED_POLICIES = {
    "codepipeline.json",
    "codebuild-ec2.json",
    "codebuild-ecs.json",
    "ec2-instance.json",
    "ecs-task-execution.json",
    "ecs-infrastructure.json",
}
ECR_PUSH_ACTIONS = {
    "ecr:BatchCheckLayerAvailability",
    "ecr:CompleteLayerUpload",
    "ecr:InitiateLayerUpload",
    "ecr:PutImage",
    "ecr:UploadLayerPart",
}


def policies() -> dict[str, dict]:
    return {path.name: json.loads(path.read_text()) for path in POLICY_DIR.glob("*.json")}


def actions(document: dict) -> set[str]:
    result = set()
    for statement in document["Statement"]:
        value = statement["Action"]
        result.update([value] if isinstance(value, str) else value)
    return result


def test_all_role_policies_are_valid_json_documents():
    """Catch missing role examples or malformed policy documents."""
    documents = policies()

    assert set(documents) == EXPECTED_POLICIES
    assert all(document["Version"] == "2012-10-17" for document in documents.values())


def test_no_statement_grants_unbounded_actions_and_resources():
    """Catch examples that teach administrator-style wildcard permissions."""
    for name, document in policies().items():
        for statement in document["Statement"]:
            assert not (
                statement["Action"] == "*" and statement["Resource"] == "*"
            ), name


def test_only_ecs_build_role_can_push_images():
    """Catch accidental ECR write access in pipeline, EC2, or runtime roles."""
    documents = policies()

    assert ECR_PUSH_ACTIONS <= actions(documents["codebuild-ecs.json"])
    for name, document in documents.items():
        if name != "codebuild-ecs.json":
            assert actions(document).isdisjoint(ECR_PUSH_ACTIONS), name


def test_ec2_instance_role_does_not_enable_remote_ssh():
    """Catch EC2 permissions that conflict with the Session Manager-only design."""
    ec2_actions = actions(policies()["ec2-instance.json"])

    assert all("ssh" not in action.casefold() for action in ec2_actions)
    assert "ssmmessages:CreateControlChannel" in ec2_actions
