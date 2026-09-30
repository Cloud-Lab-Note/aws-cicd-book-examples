#!/usr/bin/env bash
set -euo pipefail

APP_ROOT=/opt/cicd-book
STAGING_DIR="$APP_ROOT/staging"
RELEASE_ID="${DEPLOYMENT_ID:-manual}"
RELEASE_DIR="$APP_ROOT/releases/$RELEASE_ID"
UV_VERSION=0.12.17
UV_BIN=/usr/local/bin/uv

if ! id cicdbook >/dev/null 2>&1; then
  useradd --system --home-dir "$APP_ROOT" --shell /sbin/nologin cicdbook
fi

install -d -o cicdbook -g cicdbook "$APP_ROOT/releases"
rm -rf "$RELEASE_DIR"
install -d -o cicdbook -g cicdbook "$RELEASE_DIR"
cp -a "$STAGING_DIR/app" "$STAGING_DIR/requirements.lock" "$RELEASE_DIR/"
chown -R cicdbook:cicdbook "$RELEASE_DIR"

if [[ ! -x "$UV_BIN" ]]; then
  curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" \
    | env UV_INSTALL_DIR=/usr/local/bin sh
fi

sudo -u cicdbook env UV_PYTHON_INSTALL_DIR="$APP_ROOT/python" \
  "$UV_BIN" venv --python 3.13 "$RELEASE_DIR/.venv"
sudo -u cicdbook "$UV_BIN" pip install \
  --python "$RELEASE_DIR/.venv/bin/python" \
  --requirement "$RELEASE_DIR/requirements.lock"

ln -sfn "$RELEASE_DIR" "$APP_ROOT/current"
install -m 0644 "$STAGING_DIR/cicd-book.service" /etc/systemd/system/cicd-book.service
cat > /etc/cicd-book.env <<EOF
APP_ENV=dev
APP_VERSION=$RELEASE_ID
EOF
chmod 0640 /etc/cicd-book.env

