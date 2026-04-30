#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/simuboss}"

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  echo "Docker Compose is missing. Run scripts/bootstrap-ecs.sh first." >&2
  exit 1
fi

cd "$APP_DIR"

if [ "${SKIP_GIT_PULL:-0}" != "1" ]; then
  git fetch --all --prune
  git reset --hard "origin/${DEPLOY_BRANCH:-main}"
fi

if [ ! -f .env.production ]; then
  echo ".env.production is missing. Create it from .env.production.example before deploying." >&2
  exit 1
fi

"${COMPOSE[@]}" up -d --build
"${COMPOSE[@]}" ps
