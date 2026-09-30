# GitHub와 AWS로 완성하는 실전 CI/CD

전자책 독자를 위한 예제 저장소입니다. 하나의 FastAPI 애플리케이션을 GitHub와 AWS Code 서비스를 이용해 EC2에 배포한 뒤 ECS Fargate의 자체 Blue/Green 배포로 확장합니다.

이 저장소에서 예제를 내려받고, **본인의 GitHub 저장소에 올려 실습**하세요. 내려받은 코드는 자유롭게 수정할 수 있으며, 이 공개 저장소의 원본은 쓰기 권한이 있는 관리자만 직접 수정할 수 있습니다.

## 실습 범위

- Python 3.13, FastAPI, Uvicorn, pytest, Ruff
- GitHub App 기반 AWS CodeConnections
- CodePipeline과 CodeBuild
- CodeDeploy를 이용한 EC2 배포
- Docker, ECR, ECS Fargate
- ECS 자체 Blue/Green 및 Canary 배포
- IAM, ALB, Systems Manager, CloudWatch

## 1. 예제 다운로드

아래 **두 방법 중 하나**를 선택하세요. 모두 같은 `main` 브랜치의 예제를 내려받습니다.

### 방법 A. GitHub 페이지에서 수동 다운로드

1. [예제 저장소](https://github.com/Cloud-Lab-Note/aws-cicd-book-examples)를 엽니다.
2. 초록색 **Code → Download ZIP**을 선택합니다.
3. 받은 ZIP 파일을 우클릭하고 **모두 추출**을 누릅니다.
4. 압축 해제 위치를 `C:\temp\aws-cicd-reader`로 지정합니다.
5. 그 안의 `aws-cicd-book-examples-main` 폴더를 엽니다.

`app`, `tests`, `pyproject.toml`, `uv.lock`이 보이는 폴더가 프로젝트 루트입니다. 폴더 이름이나 압축 해제 위치가 다르면 이후 명령의 경로도 맞춰 바꾸세요.

### 방법 B. PowerShell로 다운로드

PowerShell을 열고 아래 명령을 순서대로 실행합니다. 파일을 저장하고 압축을 풀기만 하며, 예제 코드를 실행하지 않습니다.

```powershell
New-Item -ItemType Directory -Path C:\temp\aws-cicd-reader -Force

Invoke-WebRequest -Uri "https://github.com/Cloud-Lab-Note/aws-cicd-book-examples/archive/refs/heads/main.zip" -OutFile "C:\temp\aws-cicd-reader\example.zip"

Expand-Archive -Path "C:\temp\aws-cicd-reader\example.zip" -DestinationPath "C:\temp\aws-cicd-reader"

cd C:\temp\aws-cicd-reader\aws-cicd-book-examples-main
```

이미 같은 예제를 압축 해제한 폴더가 있다면 별도 경로를 사용하세요.

## 2. 본인의 GitHub 저장소에 업로드

Git과 GitHub 계정을 준비합니다. Git 설치는 [Git for Windows](https://git-scm.com/downloads/win)를 참고하세요.

### 빈 저장소 만들기

GitHub에서 **New repository**를 열어 다음처럼 생성합니다.

| 항목 | 설정 |
|---|---|
| Repository name | `aws-cicd-book` |
| Visibility | **Private** |
| Add README | Off |
| Add .gitignore | No .gitignore |
| Add license | No license |

README와 `.gitignore`는 예제에 이미 있으므로 생성 화면에서는 추가하지 않습니다.

### 파일 올리기

PowerShell에서 아래 명령을 실행합니다. `YOUR_GITHUB_NAME`은 본인 계정명으로, `YOUR_NOREPLY_EMAIL`은 GitHub **Settings → Emails**에 표시된 비공개 이메일 주소로 바꾸세요.

```powershell
cd C:\temp\aws-cicd-reader\aws-cicd-book-examples-main

git init
git branch -M main
git config user.name "YOUR_GITHUB_NAME"
git config user.email "YOUR_NOREPLY_EMAIL"

git add .
git diff --cached --name-only
```

파일 목록에 `.venv/`, `.env`나 실제 비밀값이 포함되지 않았는지 확인한 뒤 업로드합니다.

```powershell
git commit -m "Add CI/CD example project"
git remote add origin https://github.com/YOUR_GITHUB_NAME/aws-cicd-book.git
git push -u origin main
```

인증 창이 열리면 GitHub 로그인을 완료합니다. 본인 저장소의 **Code** 탭에서 `main` 브랜치와 프로젝트 파일이 보이면 업로드가 끝났습니다.

이 절차는 ZIP을 처음 내려받아 새 저장소에 올릴 때 사용합니다. 이미 업로드했다면 초기화와 첫 커밋을 반복할 필요가 없습니다.

## 3. 책의 실습 이어가기

**3장**에서 예제 실행과 로컬 테스트를 진행하고, **4장**에서 본인 저장소 업로드와 AWS CodeConnections 연결을 확인합니다. **5장**부터 CodeBuild와 CodePipeline을 구성합니다.

AWS에 연결할 저장소는 **본인이 만든 `aws-cicd-book`**입니다. `aws-cicd-book-examples`는 예제 다운로드용입니다. 이후 코드 수정과 배포 실습도 본인 저장소에서 진행하세요.
