#!/usr/bin/env bash
set -euo pipefail

# Determine repository root (one level above this script) and use it as the Docker build context.
BUILD_CONTEXT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Building pipeline image using pipeline/Dockerfile with context: ${BUILD_CONTEXT}"

docker build -f pipeline/Dockerfile -t klp-pipeline --progress=plain "${BUILD_CONTEXT}"

echo "Build finished."

