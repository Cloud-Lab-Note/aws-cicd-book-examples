# AWS 실습 실행 기록

실습을 실행할 때마다 아래 표를 복사해 한 회차의 기록으로 사용합니다. 실제 계정 번호, Access Key, Secret, 토큰과 비밀값은 기록하지 않습니다.

리소스 삭제 전후에는 `AWS_REGION=ap-northeast-2 bash scripts/list-billable-resources.sh`를 실행해 프로젝트 태그가 붙은 리소스를 비교합니다. 이 스크립트는 조회만 수행하고 리소스를 삭제하지 않습니다.

## 실행 정보

| 항목 | 값 |
|---|---|
| 실행 회차 | 001 |
| 계정 별칭 |  |
| 리전 | `ap-northeast-2` |
| 시작 시각 |  |
| 종료 시각 |  |
| Git commit |  |
| 실습 범위 |  |

## 생성 리소스

| 서비스 | 리소스 이름 | 프로젝트 태그 | 생성 시각 | 삭제 시각 | 삭제 확인 |
|---|---|---|---|---|---|
|  |  | `Project=cicd-book` |  |  |  |

## 배포 검증

| 단계 | 실행 ID 또는 버전 | 예상 결과 | 실제 결과 | 로그 위치 | 판정 |
|---|---|---|---|---|---|
| Source |  | GitHub 변경 감지 |  | CodePipeline |  |
| Build |  | 테스트 및 Artifact 성공 |  | CodeBuild |  |
| Deploy |  | 새 버전 정상 응답 |  | CodeDeploy 또는 ECS |  |
| Health |  | HTTP 200 |  | ALB Target Health |  |
| Version |  | commit과 일치 |  | `/api/version` |  |

## 실패 및 복구 기록

| 증상 | 최초 실패 단계 | 확인한 로그 | 원인 | 수정 | 복구 검증 |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 비용 확인

| 확인 시각 | Billing 화면의 금액 | 비용 발생 리소스 | 확인 결과 |
|---|---:|---|---|
|  |  |  |  |

## 종료 확인

- [ ] ALB와 Target Group을 확인했다.
- [ ] EC2 Instance와 연결된 볼륨을 확인했다.
- [ ] ECS Service, Task와 Cluster를 확인했다.
- [ ] ECR Repository와 이미지를 확인했다.
- [ ] S3 Artifact Bucket을 확인했다.
- [ ] CodePipeline, CodeBuild와 CodeDeploy 리소스를 확인했다.
- [ ] NAT Gateway가 생성되지 않았음을 확인했다.
- [ ] `Project=cicd-book` 태그의 남은 리소스를 확인했다.
- [ ] Billing과 Budget 알림 상태를 확인했다.
