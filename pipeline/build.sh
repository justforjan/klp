#!/usr/bin/env bash
set -euo pipefail

# pipeline/build.sh
# Usage:
#   ./build.sh        # from pipeline/ or anywhere -> builds using repo root as context
#   ./build.sh /path/to/context  # override the build context explicitly

# Resolve directory containing this script (works when invoked via symlink or from any cwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Repository root is the parent of the pipeline directory
DEFAULT_CONTEXT="$(cd "$SCRIPT_DIR/.." && pwd)"

BUILD_CONTEXT="${1:-$DEFAULT_CONTEXT}"

echo "Building pipeline image using pipeline/Dockerfile with context: ${BUILD_CONTEXT}"

docker build -f "$SCRIPT_DIR/Dockerfile" -t klp_pipeline_tests:latest --progress=plain "${BUILD_CONTEXT}"

echo "Build finished."
