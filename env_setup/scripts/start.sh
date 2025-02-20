#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$( realpath -- "${SCRIPT_DIR}/../.." )"

echo 'Creating shared column directory: /tmp/engine-dbs-shared-volume'
mkdir -p /tmp/engine-dbs-shared-volume
chmod 777 /tmp/engine-dbs-shared-volume

EXTRA_FLAGS_TO_RESET_DB=

while [[ $# -gt 0 ]]; do
  key="$1"
  shift
  case $key in
    --debug)
      set -x
      ;;
    --no-bootstrap)
      EXTRA_FLAGS_TO_RESET_DB=" --no-bootstrap"
      ;;
  esac
done

source "${REPO_DIR}/env_setup/.env.scripts"

pulled_images=(postgres clickhouse rabbitmq redis dynamodb)
if [ $PULL_ENGINE = true ]; then
  pulled_images+=(data-api-server)
fi
if [ $PULL_TICKETMASTER = true ]; then
  pulled_images+=(ticketmaster)
fi
if [ $PULL_TICKETMASTER_WORKER = true ]; then
  pulled_images+=(ticketmaster-worker)
fi
if [ $PULL_REMEDIATION_SERVICE = true ]; then
  pulled_images+=(remediation-service)
fi
if [ $PULL_WORKER = true ]; then
  pulled_images+=(worker js-worker)
fi
if [ $PULL_ACTIONS_SERVICE = true ]; then
  pulled_images+=(actions-worker)
fi
if [ $PULL_COLLECTOR = true ]; then
  pulled_images+=(collector)
fi
# "${images[@]}" destructures the array to separate parameters so it can be inputted to commands
docker compose -f "${REPO_DIR}/env_setup/docker-compose.yml" \
  --env-file "${REPO_DIR}/env_setup/.env.docker" pull \
  $( [[ ${CI:-false} == 'true' ]] && echo '--quiet') "${pulled_images[@]}"

built_images=(postgres clickhouse rabbitmq redis dynamodb worker js-worker actions-worker)
if [ $COMPOSE_ENGINE = true ]; then
  built_images+=(data-api-server)
fi

if [ $COMPOSE_COLLECTOR = true ]; then
  built_images+=(collector)
fi

if [ $COMPOSE_TICKETMASTER = true ]; then
  built_images+=(ticketmaster)
fi
if [ $COMPOSE_TICKETMASTER_WORKER = true ]; then
  built_images+=(ticketmaster-worker)
fi
if [ $COMPOSE_REMEDIATION_SERVICE = true ]; then
  built_images+=(remediation-service)
fi
docker compose -f "${REPO_DIR}/env_setup/docker-compose.yml" --env-file "${REPO_DIR}/env_setup/.env.docker" up -d "${built_images[@]}"

"${REPO_DIR}/env_setup/scripts/reset_db.sh" ${EXTRA_FLAGS_TO_RESET_DB}
