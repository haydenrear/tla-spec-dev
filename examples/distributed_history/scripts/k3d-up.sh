#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="${ECOMMERCE_K3D_CLUSTER:-ecommerce-history}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required for k3d mode" >&2
  exit 1
fi
if ! command -v k3d >/dev/null 2>&1; then
  echo "k3d is required for k3d mode" >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "docker daemon is not available" >&2
  exit 1
fi

if ! k3d cluster list "$CLUSTER_NAME" >/dev/null 2>&1; then
  k3d cluster create --config "$ROOT/deploy/k3d-config.yaml"
fi

docker build -t ecommerce-history:local -f "$ROOT/deploy/Dockerfile" "$ROOT"
k3d image import ecommerce-history:local -c "$CLUSTER_NAME"
