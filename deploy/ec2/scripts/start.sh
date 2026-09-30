#!/usr/bin/env bash
set -euo pipefail

systemctl daemon-reload
systemctl enable --now cicd-book.service

