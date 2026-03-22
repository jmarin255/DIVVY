#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_DIR="$(cd "${BACKEND_DIR}/.." && pwd)"

if [[ ! -f "${REPO_DIR}/.env" ]]; then
	echo "Missing ${REPO_DIR}/.env"
	echo "Create it from .env.example before running the backend:"
	echo "  cp ${REPO_DIR}/.env.example ${REPO_DIR}/.env"
	exit 1
fi

cd "${BACKEND_DIR}"
uvicorn app.main:app --reload
