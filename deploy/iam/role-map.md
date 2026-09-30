# CI/CD IAM 역할 지도

정책 파일의 `${...}` 값은 실습 계정의 ARN으로 치환합니다. 정책을 한 역할에 합치지 않고 실행 주체별로 분리합니다.

| 역할 | 신뢰 주체 | 사용하는 장 | 접근 범위 | 실패 시 먼저 확인할 곳 |
|---|---|---:|---|---|
| CodePipeline 서비스 역할 | `codepipeline.amazonaws.com` | 4~6, 15 | GitHub 연결, Artifact, Build, EC2·ECS 배포 | CodePipeline 실행 이력 |
| CodeBuild EC2 역할 | `codebuild.amazonaws.com` | 5~6 | Build 로그와 EC2 Artifact | CodeBuild phase 로그 |
| CodeBuild ECS 역할 | `codebuild.amazonaws.com` | 11 | Build 로그, Artifact, ECR Push | CodeBuild 및 ECR 이벤트 |
| CodeDeploy 서비스 역할 | `codedeploy.amazonaws.com` | 8~10 | EC2 대상과 ALB 상태 | CodeDeploy deployment events |
| EC2 Instance Profile | `ec2.amazonaws.com` | 7~10 | Artifact 읽기, SSM, 로그 | SSM Agent와 Instance Profile |
| ECS Task Execution 역할 | `ecs-tasks.amazonaws.com` | 12~14 | ECR Pull과 CloudWatch Logs | ECS Task stopped reason |
| ECS Task 역할 | `ecs-tasks.amazonaws.com` | 12~15 | 앱이 호출하는 AWS API | 애플리케이션 로그 |
| ECS Infrastructure 역할 | `ecs.amazonaws.com` | 13~14 | Listener rule과 Target Group 전환 | ECS deployment details |

FastAPI 예제는 AWS API를 호출하지 않으므로 ECS Task 역할에는 권한 정책을 붙이지 않습니다. Execution 역할은 컨테이너 시작 전 ECR과 로그에 접근하고, Task 역할은 실행 중인 애플리케이션을 위한 역할이라는 차이를 본문에서 강조합니다.

CodeDeploy 서비스 역할은 AWS 관리형 `AWSCodeDeployRole`을 시작점으로 사용하고, EC2 Instance Profile과 혼동하지 않도록 별도로 생성합니다.
