# GitHub와 AWS로 완성하는 실전 CI/CD

유료 전자책의 실습을 검증하기 위한 예제 저장소입니다. 하나의 FastAPI 애플리케이션을 GitHub와 AWS Code 서비스를 이용해 EC2에 배포한 뒤 ECS Fargate의 자체 Blue/Green 배포로 발전시킵니다.

## 실습 범위

- Python 3.13, FastAPI, Uvicorn, pytest
- GitHub App 기반 AWS CodeConnections
- CodePipeline과 CodeBuild
- CodeDeploy를 이용한 EC2 배포
- Docker, ECR, ECS Fargate
- ECS 자체 Blue/Green 및 Canary 배포
- IAM, ALB, Systems Manager, CloudWatch

## 기본 명령

```bash
uv sync --dev
uv run python -m pytest
uv run ruff check .
```

전체 로컬 검증은 다음 명령으로 실행합니다.

```bash
bash scripts/verify-local.sh
```

Docker가 없는 문서 편집 환경에서는 `SKIP_DOCKER=1 bash scripts/verify-local.sh`로 정적 검사와 테스트만 실행할 수 있습니다. 출간 후보본은 반드시 Docker 검증까지 통과해야 합니다.

AWS 읽기 전용 상태 검증은 환경 이름을 지정한 뒤 실행합니다.

```bash
AWS_REGION=ap-northeast-2 \
PIPELINE_NAME=cicd-book-dev \
APPLICATION_URL=http://example-alb.ap-northeast-2.elb.amazonaws.com \
bash scripts/verify-aws.sh
```

AWS 실습의 실행 기록은 `docs/lab-runbook.md`, 검증 버전은 `docs/version-matrix.md`에 기록합니다.
