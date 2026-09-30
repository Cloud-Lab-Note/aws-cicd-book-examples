#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON=.venv/bin/python
RUFF=.venv/bin/ruff
CONTAINER_NAME=cicd-book-local-verify

cleanup() {
  if command -v docker >/dev/null 2>&1; then
    docker rm --force "$CONTAINER_NAME" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

[[ -x "$PYTHON" ]] || {
  echo "Missing .venv. Run: uv sync --python 3.13 --dev" >&2
  exit 1
}

echo "[1/4] Ruff"
"$RUFF" check .

echo "[2/4] pytest"
"$PYTHON" -m pytest -q

echo "[3/4] shell syntax"
bash -n deploy/ec2/scripts/*.sh scripts/*.sh

if [[ "${SKIP_DOCKER:-0}" == "1" ]]; then
  echo "[4/4] Docker skipped because SKIP_DOCKER=1"
  exit 0
fi

command -v docker >/dev/null 2>&1 || {
  echo "Docker is required. Install Docker or rerun static checks with SKIP_DOCKER=1." >&2
  exit 1
}

echo "[4/4] Docker image and health endpoint"
docker build --tag cicd-book:test .
docker run --detach --name "$CONTAINER_NAME" --publish 18000:8000 cicd-book:test >/dev/null

for attempt in {1..30}; do
  if curl --fail --silent http://127.0.0.1:18000/health >/dev/null; then
    echo "Local verification passed"
    exit 0
  fi
  [[ "$attempt" -lt 30 ]] && sleep 1
done

docker logs "$CONTAINER_NAME" >&2 || true
echo "Container health verification failed" >&2
exit 1

