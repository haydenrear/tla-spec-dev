#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required for k3d mode" >&2
  exit 1
fi

kubectl apply -f "$ROOT/deploy/k8s/ecommerce.yaml"
for deployment in \
  database-service \
  queue-service \
  account-service \
  cart-service \
  checkout-service \
  worker-service \
  gateway-service
do
  kubectl -n ecommerce-history rollout restart "deployment/$deployment"
done
for deployment in \
  database-service \
  queue-service \
  account-service \
  cart-service \
  checkout-service \
  worker-service \
  gateway-service
do
  kubectl -n ecommerce-history rollout status "deployment/$deployment" --timeout=90s
done
kubectl -n ecommerce-history get pods -o wide
