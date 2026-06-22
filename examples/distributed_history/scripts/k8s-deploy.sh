#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOYMENTS=(
  database-service
  queue-service
  account-service
  cart-service
  checkout-service
  worker-service
  gateway-service
)

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required for k3d mode" >&2
  exit 1
fi

restart_existing=false
if kubectl -n ecommerce-history get deployment/gateway-service >/dev/null 2>&1; then
  restart_existing=true
fi

kubectl apply -f "$ROOT/deploy/k8s/ecommerce.yaml"
if [ "$restart_existing" = true ]; then
  for deployment in "${DEPLOYMENTS[@]}"; do
    kubectl -n ecommerce-history rollout restart "deployment/$deployment"
  done
fi
for deployment in "${DEPLOYMENTS[@]}"; do
  kubectl -n ecommerce-history rollout status "deployment/$deployment" --timeout=90s
done
for _ in $(seq 1 60); do
  if ! kubectl -n ecommerce-history get pods --no-headers | awk '$3 == "Terminating" { found = 1 } END { exit found ? 0 : 1 }'; then
    break
  fi
  sleep 1
done
kubectl -n ecommerce-history get pods -o wide
