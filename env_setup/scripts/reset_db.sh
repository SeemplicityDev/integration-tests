#!/usr/bin/env bash

BOLDGREEN=$'\e[1;32m'
REGULARCYAN=$'\e[36m'
CLEARCOLOR=$'\e[0m'

set -euo pipefail

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$( realpath -- "${SCRIPT_DIR}/../.." )"
SEEDING_JSON=${REPO_DIR}/env_setup/scripts/config/seeding.json

source "${REPO_DIR}/env_setup/.env.scripts"

services=(postgres)
if ! [[ -z $(docker compose -f "${REPO_DIR}/env_setup/docker-compose.yml" --env-file "${REPO_DIR}/env_setup/.env.docker" ps --services --filter "status=running" | grep data-api-server) ]]; then
  services+=(data-api-server)
fi
docker compose -f "${REPO_DIR}/env_setup/docker-compose.yml" --env-file "${REPO_DIR}/env_setup/.env.docker" kill "${services}"
docker compose -f "${REPO_DIR}/env_setup/docker-compose.yml" --env-file "${REPO_DIR}/env_setup/.env.docker" rm -f "${services}"
docker compose -f "${REPO_DIR}/env_setup/docker-compose.yml" --env-file "${REPO_DIR}/env_setup/.env.docker" up -d "${services}"

# wait for connection to db and data-api-server
echo "Connecting to DB"
for (( i=0; i<20; i++ )); do
  if nc -z localhost "$POSTGRES_PORT"; then
    break
  else
    sleep 0.5
  fi
done
if ! nc -z localhost "$POSTGRES_PORT"; then
  echo "Couldn't Connect to DB, please try again"
  exit 1
fi
echo "Connected to DB!"

pushd "${REPO_DIR}" >/dev/null
docker compose -f "${REPO_DIR}/env_setup/docker-compose.yml" --env-file "${REPO_DIR}/env_setup/.env.docker" run --rm -T -e PYTHONPATH=/app data-api-server python data_api_server/scripts/bootstrap.py create-and-seed default < ${SEEDING_JSON}
popd >/dev/null

echo "Connecting to Data API Server"
for (( i=0; i<20; i++ )); do
  if nc -z localhost "$DATA_API_SERVER_PORT" >/dev/null; then
    break
  fi
  sleep 1
done
if ! nc -z localhost "$DATA_API_SERVER_PORT"; then
  echo "Couldn't Connect to Data API Server, please try again"
  exit 1
fi
echo "Connected to Data API Server!"
