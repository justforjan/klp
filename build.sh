#!/usr/bin/env bash
set -euo pipefail

# Wrapper script: delegate the actual pipeline build to pipeline/build.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_BUILD="$SCRIPT_DIR/pipeline/build.sh"

if [[ ! -f "$PIPELINE_BUILD" ]]; then
  echo "Error: pipeline build script not found at $PIPELINE_BUILD" >&2
  exit 1
fi

bash "$PIPELINE_BUILD" "$@"
