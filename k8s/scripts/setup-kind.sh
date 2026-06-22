#!/usr/bin/env bash
# Script to create a kind cluster for the Ledger project
# with 1 control-plane + 1 worker node and MetalLB for LoadBalancer
set -euo pipefail

CLUSTER_NAME="${1:-ledger}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CONFIG_PATH="${PROJECT_DIR}/k8s/overlays/kind/kind-config.yaml"

echo "=== Creating kind cluster: ${CLUSTER_NAME} ==="

# Check if cluster already exists
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo "Cluster '${CLUSTER_NAME}' already exists. Skipping creation."
    echo "To recreate, run: kind delete cluster --name ${CLUSTER_NAME}"
    exit 0
fi

# Create cluster using config file
kind create cluster \
    --name "${CLUSTER_NAME}" \
    --config "${CONFIG_PATH}"

echo "=== Cluster '${CLUSTER_NAME}' created successfully ==="
echo ""

# Set kubectl context
kubectl cluster-info --context "kind-${CLUSTER_NAME}"

echo ""
echo "=== Installing MetalLB ==="
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-native.yaml

# Wait for MetalLB controller and speaker to be ready
echo "Waiting for MetalLB pods to be ready..."
kubectl wait --namespace metallb-system \
    --for=condition=ready pod \
    --selector=app=metallb \
    --timeout=120s

echo "=== MetalLB installed ==="
echo ""
echo "=== Next step: Configure MetalLB IP pool ==="
echo "Run: kubectl apply -f ${PROJECT_DIR}/k8s/overlays/kind/metallb-ippool.yaml"