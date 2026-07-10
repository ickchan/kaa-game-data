#!/usr/bin/env bash
set -euo pipefail
BACKEND="${1:-gom}"
FORCE="${FORCE:-false}"
ARGS=(build --backend "$BACKEND")
if [[ "$FORCE" == "true" ]]; then
  ARGS+=(--force)
fi
kaa-data "${ARGS[@]}"