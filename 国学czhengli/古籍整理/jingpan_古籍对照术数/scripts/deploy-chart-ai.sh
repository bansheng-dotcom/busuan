#!/usr/bin/env bash
# Deploy chart AI proxy + SPA API passthrough to production server.
# Requires: server/.env with CF_ACCOUNT_ID and CF_API_TOKEN (not committed).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${JINGPAN_HOST:-root@38.55.194.234}"
REMOTE_AI_DIR="/opt/jingpan-chart-ai"

if [[ ! -f "$ROOT/server/.env" ]]; then
  echo "Missing $ROOT/server/.env — copy server/.env.example and set CF_ACCOUNT_ID / CF_API_TOKEN"
  exit 1
fi

echo "==> Sync chart AI proxy to $HOST:$REMOTE_AI_DIR"
ssh "$HOST" "mkdir -p $REMOTE_AI_DIR"
rsync -avz \
  "$ROOT/server/chart_ai_proxy.py" \
  "$ROOT/server/.env" \
  "$HOST:$REMOTE_AI_DIR/"

echo "==> Install systemd unit"
rsync -avz "$ROOT/scripts/chart-ai-proxy.service" "$HOST:/etc/systemd/system/chart-ai-proxy.service"
ssh "$HOST" "chmod +x $REMOTE_AI_DIR/chart_ai_proxy.py && systemctl daemon-reload && systemctl enable chart-ai-proxy && systemctl restart chart-ai-proxy"

echo "==> Update SPA server (API passthrough)"
rsync -avz "$ROOT/scripts/spa-server.py" "$HOST:/usr/local/bin/jingpan-spa-server.py"
ssh "$HOST" "systemctl restart jingpan"

echo "==> Proxy health"
ssh "$HOST" "curl -sf http://127.0.0.1:8787/health && echo"

echo "Done. Build frontend with: VITE_CHART_AI_HOLOGRAPHIC_API=/api/chart-ai-holographic yarn build"
