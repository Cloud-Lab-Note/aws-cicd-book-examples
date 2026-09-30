#!/usr/bin/env bash
set -euo pipefail

if systemctl list-unit-files cicd-book.service >/dev/null 2>&1; then
  systemctl stop cicd-book.service || true
fi

