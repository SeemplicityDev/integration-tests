#!/usr/bin/env bash

set -euo pipefail


while [[ $# -gt 0 ]]; do
  key="$1"
  shift
  case $key in
    --profile-name)
      PROFILE_NAME="$1"
      shift
      ;;
  esac
done

aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID" --profile "$PROFILE_NAME"
aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY" --profile "$PROFILE_NAME"
aws configure set aws_session_token "$AWS_SESSION_TOKEN" --profile "$PROFILE_NAME"
