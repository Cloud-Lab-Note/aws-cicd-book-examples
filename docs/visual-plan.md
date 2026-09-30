# 전자책 그림·화면 캡처 제작 기준

## 편집 원칙

- 긴 설명 앞에는 전체 구조를 보여주는 그림을 배치한다.
- 한 그림에는 하나의 관계만 담고 가로 구성 요소를 5개 이하로 제한한다.
- AWS 콘솔 전체 화면보다 독자가 확인할 필드가 보이는 영역을 확대한다.
- 캡처에는 번호 표시와 1~2문장의 해설을 붙인다.
- 계정 번호, 이메일, ARN의 계정 부분, 도메인과 개인 저장소 정보는 가린다.
- 성공 화면과 실패 화면을 같은 크기로 제시해 상태 차이를 비교할 수 있게 한다.
- 콘솔 UI가 바뀌어도 찾을 수 있도록 메뉴 이름, 리소스 이름, 상태값을 본문에 함께 쓴다.

## 장별 시각 자료 계획

| 장 | 구조도·그림 | 실제 화면 캡처 |
|---:|---|---|
| 1 | 전체 CI/CD 흐름, EC2/ECS 비교, 장애 진단 순서 | CodePipeline 단계 화면 예고 |
| 2 | IAM 역할 관계, VPC 구조, 보안 그룹 관계 | Budget 알림, 보안 그룹 규칙 |
| 3 | API endpoint 지도, 환경 변수 흐름, 테스트 차단 | 로컬 테스트 성공·실패 터미널 |
| 4 | GitHub App 권한 흐름 | CodeConnections 연결과 저장소 범위 |
| 5 | CodeBuild phase 흐름, Artifact 내부 구조 | Build 성공 로그와 테스트 실패 로그 |
| 6 | Pipeline Artifact 전달 흐름 | 전체 Pipeline 성공과 실패 Action |
| 7 | ALB·Target Group·EC2 관계 | Target Health, Session Manager |
| 8 | CodeDeploy 수명주기 | Deployment Group과 Hook 실행 상태 |
| 9 | Release 디렉터리와 symlink | systemd 상태와 journal 로그 |
| 10 | 장애 원인 분기표 | 실패 이벤트와 롤백 결과 |
| 11 | Docker image layer와 ECR 흐름 | ECR 이미지 태그와 digest |
| 12 | Cluster·Service·Task 관계 | ECS Service와 Task stopped reason |
| 13 | Blue/Green 트래픽 전환 | 두 Target Group과 deployment 단계 |
| 14 | Canary 전환 타임라인 | CloudWatch Alarm과 자동 롤백 |
| 15 | dev 승인 prod 승격 흐름 | Manual approval Action |
| 16 | 로그 위치 지도와 삭제 순서 | 비용 리소스 조회 전후 |

## 캡처 파일 이름

`ch{장번호}-{순번}-{짧은설명}.png` 형식을 사용한다.

예:

```text
ch02-01-budget-alert.png
ch05-02-codebuild-test-failed.png
ch13-03-ecs-green-taskset.png
```

