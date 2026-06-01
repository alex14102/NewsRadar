#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

echo "═══════════════════════════════════"
echo "  NewsRadar — Start"
echo "═══════════════════════════════════"

# Backend
cd "$BACKEND"
if [ ! -d ".venv" ]; then
  echo "[1/2] Tworzę venv i instaluję zależności backendowe..."
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt -q
fi

echo "[backend] Uruchamiam FastAPI na :8000"
.venv/bin/uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend
cd "$FRONTEND"
echo "[frontend] Uruchamiam Next.js na :3000"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✓ Backend:   http://localhost:8000/docs"
echo "✓ Frontend:  http://localhost:3000"
echo ""
echo "Naciśnij Ctrl+C aby zatrzymać"

cleanup() {
  echo ""
  echo "Zatrzymuję procesy..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM

wait
