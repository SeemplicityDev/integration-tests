#!/usr/bin/env bash

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "${SCRIPT_DIR}"
REPO_DIR="$( realpath -- "${SCRIPT_DIR}/.." )"
echo "${REPO_DIR}"

source "${REPO_DIR}/.env.scripts"

docker compose -f "${REPO_DIR}/docker-compose.yml" --env-file "${REPO_DIR}/.env.docker" kill
docker compose -f "${REPO_DIR}/docker-compose.yml" --env-file "${REPO_DIR}/.env.docker" rm -f
