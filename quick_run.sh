#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

OUTPUTS_DIR="$ROOT/outputs"
SERVER_LOG="$OUTPUTS_DIR/server.log"
PLAN_RESPONSE_PATH="$OUTPUTS_DIR/plan_response.json"
PLAN_SAVED_PATH="$OUTPUTS_DIR/plan_saved.json"
RECOMMENDATIONS_PATH="$OUTPUTS_DIR/recommendations.json"

mkdir -p "$OUTPUTS_DIR"

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT

echo "Installing minimal runtime dependencies..."
python3 -m pip install --user fastapi httpx starlette anyio pytest scikit-learn uvicorn

echo "Running baseline training..."
python3 training/train_intent_model.py
python3 training/train_recommendation_model.py

echo "Starting API server..."
python3 -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 >"$SERVER_LOG" 2>&1 &
SERVER_PID=$!

echo "Waiting for API health endpoint..."
for _ in $(seq 1 20); do
  if curl -sf "http://127.0.0.1:8000/health" >/dev/null; then
    break
  fi
  sleep 1
done

if ! curl -sf "http://127.0.0.1:8000/health" >/dev/null; then
  echo "API server did not become ready in time. Check outputs/server.log."
  exit 1
fi

echo "Generating example deployment plan..."
curl -sf -X POST "http://127.0.0.1:8000/plans/from-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create a production deployment plan for a 5-node Kubernetes cluster with monitoring and backup enabled.",
    "source": "text"
  }' >"$PLAN_RESPONSE_PATH"

PLAN_ID="$(python3 - <<'PY'
import json
from pathlib import Path

payload = json.loads(Path("outputs/plan_response.json").read_text(encoding="utf-8"))
print(payload["plan_metadata"]["plan_id"])
PY
)"

echo "Fetching stored in-memory plan for ${PLAN_ID}..."
curl -sf "http://127.0.0.1:8000/plans/${PLAN_ID}" >"$PLAN_SAVED_PATH"

echo "Generating recommendations..."
curl -sf -X POST "http://127.0.0.1:8000/plans/${PLAN_ID}/recommendations" >"$RECOMMENDATIONS_PATH"

echo
echo "Done. Review these files:"
echo " - outputs/plan_response.json"
echo " - outputs/plan_saved.json"
echo " - outputs/recommendations.json"
echo " - outputs/server.log"
echo " - artifacts/intent/metrics.json"
echo " - artifacts/intent/metadata.json"
echo " - artifacts/recommendations/metrics.json"
echo " - artifacts/recommendations/retrieval_index.pkl"
