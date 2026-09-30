# 검증 버전 매트릭스

책에 포함되는 명령과 화면은 아래 버전을 기준으로 검증합니다. 최종 검증일은 실제 전체 실습을 완료한 날짜로 갱신합니다.

| 구성 요소 | 고정 버전 | 확인 명령 | 최종 검증일 |
|---|---:|---|---|
| Python | 3.13 | `uv run python --version` | 미검증 |
| FastAPI | lock file 기준 | `uv pip show fastapi` | 미검증 |
| Uvicorn | lock file 기준 | `uv pip show uvicorn` | 미검증 |
| pytest | lock file 기준 | `uv run pytest --version` | 미검증 |
| Ruff | lock file 기준 | `uv run ruff --version` | 미검증 |
| Docker | 실행 환경 기준 | `docker version` | 미검증 |
| AWS CLI | v2 | `aws --version` | 미검증 |
| AWS 리전 | `ap-northeast-2` | `aws configure get region` | 미검증 |

## 갱신 원칙

- `uv.lock`에 기록된 실제 패키지 버전을 출간 후보본에서 표에 반영합니다.
- AWS 관리형 서비스는 버전 대신 기능 검증일을 기록합니다.
- 명령이나 콘솔 흐름이 변경되면 예제 저장소 변경 로그와 정오표를 함께 갱신합니다.

