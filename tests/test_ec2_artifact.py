import os
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
EC2 = ROOT / "deploy" / "ec2"


def test_appspec_declares_complete_deployment_lifecycle():
    """Catch revisions that omit a lifecycle step required for safe replacement."""
    document = yaml.safe_load((EC2 / "appspec.yml").read_text())
    hooks = document["hooks"]

    assert list(hooks) == [
        "ApplicationStop",
        "AfterInstall",
        "ApplicationStart",
        "ValidateService",
    ]


def test_appspec_hook_scripts_exist_and_are_executable():
    """Catch CodeDeploy failures caused by missing or non-executable hook scripts."""
    document = yaml.safe_load((EC2 / "appspec.yml").read_text())

    for instructions in document["hooks"].values():
        instruction = instructions[0]
        script = EC2 / instruction["location"]
        assert script.is_file(), script
        assert os.access(script, os.X_OK), script


def test_systemd_unit_runs_the_fastapi_application():
    """Catch units that point at a stale release path or wrong ASGI application."""
    unit = (EC2 / "cicd-book.service").read_text()

    assert "User=cicdbook" in unit
    assert "WorkingDirectory=/opt/cicd-book/current" in unit
    assert "app.main:app" in unit
    assert "--port 8000" in unit
    assert "Restart=on-failure" in unit


def test_buildspec_places_appspec_at_artifact_root():
    """Catch artifacts that CodeDeploy cannot recognize after CodeBuild packaging."""
    document = yaml.safe_load((ROOT / "build" / "buildspec-ec2.yml").read_text())

    assert document["artifacts"]["base-directory"] == "dist/ec2"
    assert "appspec.yml" in document["artifacts"]["files"]
