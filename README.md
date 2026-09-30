# AWS CI/CD 전자책 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 검증 가능한 FastAPI 예제 저장소와 GitHub·AWS CI/CD 실습을 먼저 완성하고, 그 결과를 바탕으로 5부 16장의 유료 전자책 원고와 출간 파일을 제작한다.

**Architecture:** 하나의 FastAPI 애플리케이션을 GitHub에서 CodePipeline과 CodeBuild로 검증한다. 첫 배포 경로는 S3 Artifact와 CodeDeploy를 통해 EC2의 systemd 서비스로 연결하고, 두 번째 경로는 Docker 이미지를 ECR에 등록해 ECS Fargate의 자체 Blue/Green 배포로 연결한다. 원고는 검증된 저장소 태그와 실제 로그·상태값을 기준으로 작성한다.

**Tech Stack:** Python 3.13, FastAPI, Uvicorn, pytest, Ruff, Docker, GitHub, AWS CodeConnections, CodePipeline, CodeBuild, CodeDeploy, EC2, systemd, S3, ECR, ECS Fargate, ALB, IAM, Systems Manager, CloudWatch

**Spec:** `docs/superpowers/specs/2026-09-22-aws-cicd-ebook-design.md`

## Global Constraints

- 목표 독자는 AWS 사용 경험은 있지만 AWS Code 시리즈를 사용하지 않은 개발자와 인프라 담당자다.
- 본문 목표 분량은 210~235쪽이다.
- 예제 애플리케이션은 Python 3.13, FastAPI, Uvicorn, pytest를 사용한다.
- 기준 리전은 서울 `ap-northeast-2`다.
- 학습 환경은 퍼블릭 서브넷 2개를 사용하고 NAT Gateway를 만들지 않는다.
- EC2는 SSH를 열지 않고 Systems Manager Session Manager를 사용한다.
- 워크로드 보안 그룹은 ALB 보안 그룹에서 오는 애플리케이션 트래픽만 허용한다.
- EC2 배포는 CodeDeploy, ECS 배포는 ECS 자체 Blue/Green을 사용한다.
- 데이터베이스, EKS, 멀티 리전, GitHub Actions 및 Jenkins 전체 실습은 범위에서 제외한다.
- 모든 장은 설명식 목표로 시작하고 실행 확인·이해 확인·장애 질문으로 끝낸다.
- 모든 AWS 실습은 장별 비용, 유지 리소스와 삭제 리소스를 명시한다.

## Review Focus

- `APP_VERSION`이 없거나 잘못된 값일 때 앱이 안전한 기본값으로 실행되고 `/api/version`이 문자열을 반환하는지 확인한다.
- `/health`가 외부 서비스에 의존하지 않고 ALB 헬스 체크에 적합한 빠른 200 응답을 반환하는지 확인한다.
- EC2 배포 스크립트를 여러 번 실행해도 같은 결과가 되며 실패 시 0이 아닌 종료 코드를 반환하는지 확인한다.
- ECR 이미지 태그가 `latest`에만 의존하지 않고 Git commit SHA로 추적되는지 확인한다.
- 삭제 절차가 `Project=cicd-book` 범위 밖의 리소스를 건드리지 않으며 삭제 후 과금 리소스가 남지 않는지 확인한다.

---

## 파일 구조

```text
aws-cicd-ebook/
├── app/
│   ├── __init__.py
│   ├── config.py
│   └── main.py
├── tests/
│   ├── test_config.py
│   └── test_main.py
├── deploy/
│   ├── ec2/
│   │   ├── appspec.yml
│   │   ├── cicd-book.service
│   │   └── scripts/
│   │       ├── install.sh
│   │       ├── start.sh
│   │       ├── stop.sh
│   │       └── validate.sh
│   ├── ecs/
│   │   ├── task-definition.json
│   │   ├── service-definition.json
│   │   └── deployment-configuration.json
│   └── iam/
│       ├── role-map.md
│       └── policies/
├── build/
│   ├── buildspec-ec2.yml
│   └── buildspec-ecs.yml
├── scripts/
│   ├── verify-local.sh
│   ├── verify-aws.sh
│   └── list-billable-resources.sh
├── manuscript/
│   ├── 00-frontmatter.md
│   ├── part-01/
│   ├── part-02/
│   ├── part-03/
│   ├── part-04/
│   ├── part-05/
│   └── appendices/
├── docs/
│   ├── lab-runbook.md
│   ├── version-matrix.md
│   └── beta-test-checklist.md
├── Dockerfile
├── .dockerignore
├── pyproject.toml
├── requirements.lock
└── README.md
```

## Task 1: 프로젝트 저장소와 검증 기준 만들기

**Files:**
- Create: `README.md`
- Create: `pyproject.toml`
- Create: `docs/version-matrix.md`
- Create: `docs/lab-runbook.md`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: 승인된 기획서
- Produces: 모든 후속 작업이 사용하는 디렉터리 구조, Python 명령과 AWS 실습 기록 형식

- [ ] **Step 1: Git 저장소를 초기화하고 기본 디렉터리를 만든다**

Run: `git init && mkdir -p app tests deploy/ec2/scripts deploy/ecs deploy/iam/policies build scripts manuscript/{part-01,part-02,part-03,part-04,part-05,appendices} docs`

Expected: `git status --short --branch`가 초기 브랜치와 빈 작업 트리를 표시한다.

- [ ] **Step 2: Python 프로젝트 설정을 작성한다**

`pyproject.toml`에 Python `>=3.13,<3.14`, FastAPI, Uvicorn, pytest, httpx, Ruff를 선언한다. Ruff는 `E`, `F`, `I`, `B` 규칙을 사용하고 pytest test path는 `tests`로 고정한다.

- [ ] **Step 3: 버전 매트릭스와 실습 기록 형식을 작성한다**

`docs/version-matrix.md` 표의 열을 `구성 요소 | 고정 버전 | 확인 명령 | 최종 검증일`로 만든다. `docs/lab-runbook.md`에는 각 실행의 계정 별칭, 리전, 시작·종료 시각, 생성 리소스, 비용 확인, 삭제 확인을 기록하는 표를 만든다.

- [ ] **Step 4: 기본 정적 검사를 실행한다**

Run: `python3 -m tomllib pyproject.toml`

Expected: 구문 오류 없이 종료 코드 0.

- [ ] **Step 5: 커밋한다**

Run: `git add . && git commit -m "chore: initialize ebook example project"`

## Task 2: FastAPI 예제 애플리케이션을 TDD로 구현하기

**Files:**
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `app/main.py`
- Create: `tests/test_config.py`
- Create: `tests/test_main.py`

**Interfaces:**
- Produces: `app.main:app`, `Settings.from_env() -> Settings`, `/health`, `/api/version`, `/api/config`

- [ ] **Step 1: 설정 기본값 테스트를 작성한다**

```python
def test_settings_use_safe_defaults(monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    settings = Settings.from_env()
    assert settings.version == "dev"
    assert settings.environment == "local"
```

- [ ] **Step 2: 테스트가 실패하는지 확인한다**

Run: `pytest tests/test_config.py -v`

Expected: `ModuleNotFoundError` 또는 `Settings` 미정의로 FAIL.

- [ ] **Step 3: 최소 설정 구현을 작성한다**

`Settings`는 `version: str`, `environment: str` 필드를 가진 frozen dataclass로 만들고 `from_env()`가 `APP_VERSION`, `APP_ENV`를 읽게 한다.

- [ ] **Step 4: API 계약 테스트를 작성한다**

```python
def test_health_is_independent_and_healthy(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_version_is_a_string(client):
    response = client.get("/api/version")
    assert response.status_code == 200
    assert isinstance(response.json()["version"], str)
```

- [ ] **Step 5: API 테스트가 실패하는지 확인한다**

Run: `pytest tests/test_main.py -v`

Expected: `app.main` 또는 endpoint 미정의로 FAIL.

- [ ] **Step 6: FastAPI endpoint를 구현한다**

`/health`는 외부 의존성을 호출하지 않고 고정 200을 반환한다. `/api/version`은 설정의 버전, `/api/config`는 환경 이름만 반환하며 비밀값은 반환하지 않는다.

- [ ] **Step 7: 전체 품질 검사를 통과시킨다**

Run: `pytest -q && ruff check .`

Expected: 모든 테스트 PASS, Ruff 오류 0.

- [ ] **Step 8: 커밋한다**

Run: `git add app tests pyproject.toml && git commit -m "feat: add deployable FastAPI demo service"`

## Task 3: EC2 배포 Artifact와 systemd 스크립트 만들기

**Files:**
- Create: `deploy/ec2/appspec.yml`
- Create: `deploy/ec2/cicd-book.service`
- Create: `deploy/ec2/scripts/install.sh`
- Create: `deploy/ec2/scripts/start.sh`
- Create: `deploy/ec2/scripts/stop.sh`
- Create: `deploy/ec2/scripts/validate.sh`
- Create: `build/buildspec-ec2.yml`
- Create: `tests/test_ec2_artifact.py`

**Interfaces:**
- Consumes: `app.main:app`, `requirements.lock`
- Produces: CodeDeploy가 소비하는 ZIP Artifact와 `/opt/cicd-book/current`의 systemd 서비스

- [ ] **Step 1: Artifact 계약 테스트를 작성한다**

테스트는 `appspec.yml`에 `ApplicationStop`, `AfterInstall`, `ApplicationStart`, `ValidateService` Hook이 있는지, 모든 스크립트 경로가 실제 파일인지, systemd의 `ExecStart`가 `app.main:app`을 실행하는지 검사한다.

- [ ] **Step 2: 계약 테스트 실패를 확인한다**

Run: `pytest tests/test_ec2_artifact.py -v`

Expected: 배포 파일 누락으로 FAIL.

- [ ] **Step 3: AppSpec과 systemd unit을 작성한다**

설치 위치는 `/opt/cicd-book/releases/${DEPLOYMENT_ID}`로 하고 `/opt/cicd-book/current` symlink를 현재 릴리스로 전환한다. 서비스 사용자는 `cicdbook`, 실행 포트는 `8000`, 재시작 정책은 `on-failure`로 고정한다.

- [ ] **Step 4: 멱등 배포 스크립트를 작성한다**

모든 스크립트는 `set -euo pipefail`을 사용한다. `install.sh`는 사용자와 디렉터리가 이미 있어도 성공해야 하며, `stop.sh`는 서비스가 아직 없어도 성공해야 한다. `validate.sh`는 `curl --fail --silent http://127.0.0.1:8000/health` 실패를 그대로 반환한다.

- [ ] **Step 5: EC2 CodeBuild 설정을 작성한다**

설치, `ruff check .`, `pytest -q`, Artifact 조립 순서로 실행하고 ZIP 루트에 `appspec.yml`이 위치하게 한다.

- [ ] **Step 6: 배포 계약과 shell 구문을 검증한다**

Run: `pytest tests/test_ec2_artifact.py -v && bash -n deploy/ec2/scripts/*.sh`

Expected: PASS 및 shell 구문 오류 0.

- [ ] **Step 7: 커밋한다**

Run: `git add deploy/ec2 build/buildspec-ec2.yml tests/test_ec2_artifact.py && git commit -m "feat: add EC2 CodeDeploy artifact"`

## Task 4: 컨테이너 이미지와 ECS 배포 정의 만들기

**Files:**
- Create: `Dockerfile`
- Create: `.dockerignore`
- Create: `build/buildspec-ecs.yml`
- Create: `deploy/ecs/task-definition.json`
- Create: `deploy/ecs/service-definition.json`
- Create: `deploy/ecs/deployment-configuration.json`
- Create: `tests/test_ecs_definitions.py`

**Interfaces:**
- Consumes: `app.main:app`, 환경 변수 `APP_VERSION`, `APP_ENV`, CodeBuild의 `CODEBUILD_RESOLVED_SOURCE_VERSION`
- Produces: commit SHA 태그의 ECR 이미지와 ECS 자체 Blue/Green 서비스 입력 파일

- [ ] **Step 1: ECS 정의 계약 테스트를 작성한다**

테스트는 컨테이너 포트 `8000`, `awslogs` 로그 드라이버, 읽기 전용 root filesystem, non-root 실행, `/health` 헬스 체크, `BLUE_GREEN` 배포 전략, Bake time, 두 Target Group placeholder가 존재하는지 검사한다.

- [ ] **Step 2: 테스트 실패를 확인한다**

Run: `pytest tests/test_ecs_definitions.py -v`

Expected: Dockerfile 및 JSON 정의 누락으로 FAIL.

- [ ] **Step 3: 최소 권한 컨테이너 이미지를 작성한다**

Python 3.13 slim 이미지를 고정하고 전용 사용자로 실행한다. Port `8000`을 expose하고 Uvicorn의 graceful shutdown을 사용할 수 있도록 exec form `CMD`를 작성한다.

- [ ] **Step 4: ECR 빌드 설정을 작성한다**

이미지 태그는 `CODEBUILD_RESOLVED_SOURCE_VERSION` 앞 12자를 사용한다. ECR 로그인, build, 테스트 실행, push 후 `image-detail.json`을 Artifact로 출력한다. `latest`는 편의 태그로만 추가하고 배포 입력은 commit SHA 태그를 사용한다.

- [ ] **Step 5: ECS 정의 파일을 작성한다**

실제 계정별 값은 `${AWS_ACCOUNT_ID}`, `${AWS_REGION}`, `${ECR_REPOSITORY}`, `${TASK_EXECUTION_ROLE_ARN}`, `${TASK_ROLE_ARN}` placeholder로 표현하고 배포 준비 스크립트에서 치환한다.

- [ ] **Step 6: 로컬 컨테이너와 정의 파일을 검증한다**

Run: `docker build -t cicd-book:test . && docker run --rm -d --name cicd-book-test -p 18000:8000 cicd-book:test`

Run: `curl --fail http://127.0.0.1:18000/health && docker stop cicd-book-test && pytest tests/test_ecs_definitions.py -v`

Expected: HTTP 200, 컨테이너 정상 종료, 테스트 PASS.

- [ ] **Step 7: 커밋한다**

Run: `git add Dockerfile .dockerignore build/buildspec-ecs.yml deploy/ecs tests/test_ecs_definitions.py && git commit -m "feat: add ECS Fargate deployment artifacts"`

## Task 5: IAM 역할 지도와 정책 예제 만들기

**Files:**
- Create: `deploy/iam/role-map.md`
- Create: `deploy/iam/policies/codepipeline.json`
- Create: `deploy/iam/policies/codebuild-ec2.json`
- Create: `deploy/iam/policies/codebuild-ecs.json`
- Create: `deploy/iam/policies/ec2-instance.json`
- Create: `deploy/iam/policies/ecs-task-execution.json`
- Create: `deploy/iam/policies/ecs-infrastructure.json`
- Create: `tests/test_iam_policies.py`

**Interfaces:**
- Produces: 각 서비스 주체, trust principal, 허용 action과 resource 범위를 설명하는 정책 묶음

- [ ] **Step 1: IAM 정책 안전성 테스트를 작성한다**

테스트는 모든 파일이 유효한 JSON인지, `Action: "*"`와 `Resource: "*"`의 조합이 없는지, CodeBuild ECS 역할에만 ECR push 권한이 있는지, EC2 역할에 SSH 관련 권한이 없는지 확인한다.

- [ ] **Step 2: 테스트 실패를 확인한다**

Run: `pytest tests/test_iam_policies.py -v`

Expected: 정책 파일 누락으로 FAIL.

- [ ] **Step 3: 서비스별 정책과 역할 지도를 작성한다**

`role-map.md`에는 주체, 신뢰 정책, 사용하는 장, 접근 리소스, 실패 시 확인할 로그를 표로 기록한다. 리소스 ARN은 프로젝트·리전·계정 placeholder로 제한한다.

- [ ] **Step 4: IAM 계약 테스트를 통과시킨다**

Run: `pytest tests/test_iam_policies.py -v`

Expected: PASS.

- [ ] **Step 5: 커밋한다**

Run: `git add deploy/iam tests/test_iam_policies.py && git commit -m "feat: document least-privilege CI/CD roles"`

## Task 6: 전체 로컬 검증과 AWS 실행 Runbook 만들기

**Files:**
- Create: `scripts/verify-local.sh`
- Create: `scripts/verify-aws.sh`
- Create: `scripts/list-billable-resources.sh`
- Modify: `docs/lab-runbook.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: 앱, EC2 Artifact, Docker 이미지, ECS 정의와 IAM 정책
- Produces: 한 명령의 로컬 품질 검사와 단계별 AWS 상태 확인 절차

- [ ] **Step 1: 로컬 통합 검증 스크립트를 작성한다**

`verify-local.sh`는 Ruff, pytest, shell 구문 검사, Docker build와 `/health` 확인을 순서대로 실행하고 어느 단계가 실패했는지 표시한다. 컨테이너 cleanup은 `trap`으로 보장한다.

- [ ] **Step 2: AWS 상태 검증 스크립트를 작성한다**

`verify-aws.sh`는 호출자 계정, 리전, CodePipeline 최신 실행, CodeBuild 상태, CodeDeploy 최신 배포, EC2 Target Health, ECS deployment 상태와 `/api/version` 응답을 읽기 전용 AWS CLI 명령으로 출력한다.

- [ ] **Step 3: 과금 리소스 목록 스크립트를 작성한다**

`list-billable-resources.sh`는 `Project=cicd-book` 태그를 기준으로 ALB, Target Group, EC2, ECS Service, NAT Gateway, ECR, S3를 조회한다. 삭제 명령은 실행하지 않는다.

- [ ] **Step 4: 로컬 통합 검증을 실행한다**

Run: `bash scripts/verify-local.sh`

Expected: 모든 검사 PASS, 임시 컨테이너 없음.

- [ ] **Step 5: 커밋한다**

Run: `git add scripts docs/lab-runbook.md README.md && git commit -m "test: add local and AWS verification runbooks"`

## Task 7: AWS에서 EC2 CI/CD 경로를 검증하기

**Files:**
- Modify: `docs/lab-runbook.md`
- Modify: `docs/version-matrix.md`
- Modify: EC2 관련 파일 중 실제 실행에서 확인된 항목

**Interfaces:**
- Consumes: 실제 AWS 계정, 서울 리전, GitHub 저장소
- Produces: GitHub → CodePipeline → CodeBuild → S3 → CodeDeploy → EC2 → ALB의 검증 기록

- [ ] **Step 1: Budget와 프로젝트 태그를 먼저 설정한다**

Expected: Budget 알림 대상 이메일이 확인되고 이후 생성 리소스가 `Project=cicd-book` 태그를 가진다.

- [ ] **Step 2: VPC, 퍼블릭 서브넷 2개, ALB와 EC2를 구성한다**

Expected: SSH 22 인바운드 규칙이 없고 EC2 앱 포트는 ALB 보안 그룹에서만 허용된다.

- [ ] **Step 3: CodeConnections, CodeBuild, CodePipeline과 CodeDeploy를 구성한다**


Expected: GitHub Push가 자동 실행되고 CodeDeploy가 `Succeeded`가 된다.

- [ ] **Step 4: 정상 배포를 검증한다**

Run: `bash scripts/verify-aws.sh`

Expected: Target healthy, `/health` 200, `/api/version`이 배포 commit과 일치한다.

- [ ] **Step 5: 네 가지 실패를 재현하고 복구한다**

pytest 실패, Hook 실행 권한 오류, 잘못된 systemd 실행 경로, `/health` 실패를 각각 별도 commit으로 재현한다. 각 실패마다 최초 실패 단계, 로그 위치, 원인, 수정, 재실행 결과를 runbook에 기록한다.

- [ ] **Step 6: EC2 롤백을 검증한다**

Expected: 실패한 revision 이후 이전 정상 revision이 응답하고 `/api/version`으로 이를 증명한다.

- [ ] **Step 7: 검증 기록을 커밋한다**

Run: `git add . && git commit -m "docs: record verified EC2 CI/CD lab"`

## Task 8: AWS에서 ECS 자체 Blue/Green 경로를 검증하기

**Files:**
- Modify: `docs/lab-runbook.md`
- Modify: `docs/version-matrix.md`
- Modify: ECS 관련 파일 중 실제 실행에서 확인된 항목

**Interfaces:**
- Consumes: ECR 이미지, ECS 정의, ALB와 두 Target Group
- Produces: CodePipeline → CodeBuild → ECR → ECS Fargate native Blue/Green의 검증 기록

- [ ] **Step 1: ECR과 ECS Fargate 실행 환경을 구성한다**

Expected: Task는 Public IP를 사용하지만 인바운드는 ALB 보안 그룹에서만 허용된다.

- [ ] **Step 2: ECS 자체 Blue/Green과 두 Target Group을 구성한다**

Expected: 기존 Blue revision이 production traffic을 받고 Green revision이 test traffic으로 검증 가능하다.

- [ ] **Step 3: commit SHA 이미지 배포를 검증한다**

Expected: ECR 이미지 태그, Task Definition 이미지, `/api/version` 값이 같은 commit을 가리킨다.

- [ ] **Step 4: Canary 전환과 Bake time을 검증한다**

Expected: 일부 트래픽이 Green으로 이동하고 검증 후 100% 전환되며 Bake time 동안 Blue가 유지된다.

- [ ] **Step 5: 실패와 자동 롤백을 검증한다**

잘못된 container command와 실패하는 `/health` 버전을 각각 배포한다. CloudWatch Alarm 또는 deployment failure가 전환을 멈추고 Blue로 복귀하는 상태와 로그를 기록한다.

- [ ] **Step 6: 검증 기록을 커밋한다**

Run: `git add . && git commit -m "docs: record verified ECS blue green lab"`

## Task 9: 장별 원고 템플릿과 1~6장 작성하기

**Files:**
- Create: `manuscript/chapter-template.md`
- Create: `manuscript/part-01/ch01.md`
- Create: `manuscript/part-01/ch02.md`
- Create: `manuscript/part-02/ch03.md` through `ch06.md`

**Interfaces:**
- Consumes: 검증된 앱, GitHub 연결과 CI 기록
- Produces: CI까지 완료하는 원고 6장

- [ ] **Step 1: 장 템플릿을 작성한다**

템플릿은 `이 장에서 만드는 것`, `구조와 원리`, `비용 확인`, `단계별 구축`, `성공 검증`, `실패 실습`, `운영에서는`, `이번 장에서 완성한 것`, `완료 점검`, `다음 장으로 가기 전에`를 포함한다.

- [ ] **Step 2: 1~2장을 작성한다**

2장에는 “왜 퍼블릭 서브넷을 사용하는가?” 설계 노트와 NAT Gateway·VPC Endpoint의 비용 및 운영 대안을 넣는다.

- [ ] **Step 3: 3~6장을 검증 기록과 저장소 태그 기준으로 작성한다**

각 명령은 깨끗한 checkout에서 재실행하고, 콘솔 단계는 리소스 이름과 성공 상태를 함께 기록한다.

- [ ] **Step 4: 장 종료 질문을 검수한다**

각 장에 실행 확인 3~5개, 이해 확인 2~3개, 장애 질문 1개와 해설이 있는지 검사한다.

- [ ] **Step 5: 커밋한다**

Run: `git add manuscript && git commit -m "docs: draft foundations and CI chapters"`

## Task 10: EC2와 ECS 실습 원고 7~14장 작성하기

**Files:**
- Create: `manuscript/part-03/ch07.md` through `ch10.md`
- Create: `manuscript/part-04/ch11.md` through `ch14.md`

**Interfaces:**
- Consumes: Task 7과 8의 정상·실패·롤백 검증 기록
- Produces: EC2 및 ECS 배포 원고 8장

- [ ] **Step 1: 7~10장 EC2 원고를 작성한다**

서비스 역할, Instance Profile과 Agent의 책임을 구분하고, 실패마다 실제 로그 위치와 성공 검증 값을 포함한다.

- [ ] **Step 2: 11~14장 ECS 원고를 작성한다**

ECR commit 태그, Task Definition, 두 Target Group, test traffic, Canary, Bake time과 롤백을 실제 검증 순서로 설명한다.

- [ ] **Step 3: 기술 선택 설명란을 작성한다**

13장에 ECS 자체 배포를 선택한 이유와 기존 CodeDeploy 기반 ECS 구성이 적합한 조건을 설명한다.

- [ ] **Step 4: 명령과 응답을 재검증한다**

Run: `bash scripts/verify-local.sh`와 각 장의 읽기 전용 AWS 검증 명령.

Expected: 원고의 리소스 이름, endpoint, 상태값과 실제 결과가 일치한다.

- [ ] **Step 5: 커밋한다**

Run: `git add manuscript/part-03 manuscript/part-04 && git commit -m "docs: draft EC2 and ECS deployment chapters"`

## Task 11: 운영 장과 부록 작성하기

**Files:**
- Create: `manuscript/part-05/ch15.md`
- Create: `manuscript/part-05/ch16.md`
- Create: `manuscript/appendices/appendix-a.md` through `appendix-d.md`
- Create: `manuscript/00-frontmatter.md`

**Interfaces:**
- Consumes: 전체 실습 결과, 역할 지도, 비용 및 삭제 기록
- Produces: 완결된 16장과 부록 원고

- [ ] **Step 1: 개발·운영 분리와 승인 장을 작성한다**

동일 Artifact 승격, 환경 변수, Parameter Store와 Secrets Manager, 수동 승인, 교차 계정 확장 기준을 설명한다.

- [ ] **Step 2: 로그·비용·삭제 장을 작성한다**

서비스별 로그 위치와 `Project=cicd-book` 리소스 확인 순서를 제공하고, 삭제 전후 `list-billable-resources.sh` 결과를 비교한다.

- [ ] **Step 3: 부록 네 개를 작성한다**

AWS 기초, 오류 해결표, CI/CD 도구 선택, 명령·설정 파일을 본문 중복 없이 정리한다.

- [ ] **Step 4: 앞부분과 지원 범위를 작성한다**

독자 수준, 필요한 계정과 도구, 비용 책임, 검증일, 지원 리전, 예제 저장소 태그 사용법을 명시한다.

- [ ] **Step 5: 커밋한다**

Run: `git add manuscript && git commit -m "docs: complete operations chapters and appendices"`

## Task 12: 베타 테스트와 출간 승인본 만들기

**Files:**
- Create: `docs/beta-test-checklist.md`
- Create: `docs/errata.md`
- Modify: 원고 및 예제 중 베타 테스트에서 발견된 항목

**Interfaces:**
- Consumes: 완성 원고와 예제 저장소
- Produces: 제3자가 재현한 출간 후보본

- [ ] **Step 1: 베타 테스트 체크리스트를 작성한다**

각 장의 시작·종료 시각, 막힌 단계, 오류 메시지, 해결에 사용한 설명, 비용, 삭제 확인, 이해하기 어려운 용어를 기록하게 한다.

- [ ] **Step 2: 최소 3명의 독자 유형으로 테스트한다**

AWS 입문자 1명, AWS 사용 경험자 1명, CI/CD 실무자 1명이 독립적으로 실습한다. 저자는 실습 중 구두 설명을 제공하지 않고 막힌 지점을 기록한다.

- [ ] **Step 3: 재현 실패를 수정한다**

동일 지점에서 둘 이상 막히면 원고와 예제를 모두 수정한다. 한 명만 막힌 경우에도 명령 오류, 권한 누락, 삭제 누락이면 즉시 수정한다.

- [ ] **Step 4: 전체 검증을 다시 실행한다**

Run: `bash scripts/verify-local.sh && bash scripts/verify-aws.sh`

Expected: 로컬 검사 PASS, 최신 EC2와 ECS 배포 정상, 비용 리소스 목록 확인.

- [ ] **Step 5: 출간 후보 태그와 커밋을 만든다**

Run: `git add . && git commit -m "release: prepare ebook release candidate" && git tag ebook-rc1`

Expected: 깨끗한 작업 트리와 `ebook-rc1` 태그.

## 단계별 승인 지점

1. Task 1~2 완료 후 예제 앱과 독자 난이도 검토
2. Task 3~6 완료 후 배포 파일과 IAM 구조 기술 검토
3. Task 7 완료 후 EC2 실습 비용·재현성 검토
4. Task 8 완료 후 ECS 최신 기능과 롤백 검토
5. Task 9 완료 후 문체·설명 깊이·장 종료 질문 검토
6. Task 10~11 완료 후 전체 원고 기술 검수
7. Task 12 완료 후 편집·가격·판매 채널 결정

