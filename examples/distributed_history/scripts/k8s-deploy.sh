#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required for k3d mode" >&2
  exit 1
fi

kubectl apply -f "$ROOT/deploy/k8s/ecommerce.yaml"
kubectl -n ecommerce-history rollout status deployment/ecommerce-api --timeout=90s
kubectl -n ecommerce-history get pods -l app=ecommerce-api
