#!/usr/bin/bash
set -euo pipefail

docker login ghcr.io -u justforjan

docker tag klp_pipeline_tests:latest ghcr.io/justforjan/klp_pipeline_tests:latest
docker push ghcr.io/justforjan/klp_pipeline_tests:latest