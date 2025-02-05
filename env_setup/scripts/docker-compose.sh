#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$( realpath -- "${SCRIPT_DIR}/../.." )"

source "$REPO_DIR/env_setup/.env.scripts"

# run with "logs -f" for logs
docker compose -f "$REPO_DIR/env_setup/docker-compose.yml" --env-file "$REPO_DIR/env_setup/.env.docker" $@
