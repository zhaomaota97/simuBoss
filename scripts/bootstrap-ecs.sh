#!/usr/bin/env bash
set -euo pipefail

install_package() {
  if command -v dnf >/dev/null 2>&1; then
    dnf install -y "$@"
  elif command -v yum >/dev/null 2>&1; then
    yum install -y "$@"
  elif command -v apt-get >/dev/null 2>&1; then
    apt-get update
    apt-get install -y "$@"
  else
    echo "No supported package manager found. Install these packages manually: $*" >&2
    exit 1
  fi
}

if ! command -v docker >/dev/null 2>&1; then
  install_package docker
  systemctl enable docker
  systemctl start docker
fi

if ! docker compose version >/dev/null 2>&1; then
  install_package docker-compose-plugin || true
fi

if ! command -v git >/dev/null 2>&1; then
  install_package git
fi

if ! docker compose version >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
  echo "Docker Compose is missing. Install docker-compose-plugin or docker-compose, then rerun deploy." >&2
  exit 1
fi
