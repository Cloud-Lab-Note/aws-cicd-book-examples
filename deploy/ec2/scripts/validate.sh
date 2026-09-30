#!/usr/bin/env bash
set -euo pipefail

for attempt in {1..30}; do
  if curl --fail --silent --show-error http://127.0.0.1:8000/health >/dev/null; then
    exit 0
  fi
  if [[ "$attempt" -lt 30 ]]; then
    sleep 2
  fi
done

systemctl status cicd-book.service --no-pager || true
journalctl -u cicd-book.service --no-pager -n 50 || true
exit 1

