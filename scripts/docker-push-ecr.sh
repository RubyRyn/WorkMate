#!/usr/bin/env bash
# =============================================================================
# scripts/docker-push-ecr.sh
#
# Build the WorkMate backend Docker image and push it to AWS ECR.
#
# Required env vars:
#   AWS_ACCOUNT_ID   — your 12-digit AWS account ID
#   AWS_REGION       — target region (default: us-east-1)
#
# Optional env vars:
#   IMAGE_TAG        — tag to apply in addition to :latest (default: git SHA)
#   ECR_REPO         — ECR repository name (default: workmate-backend)
#
# Usage:
#   export AWS_ACCOUNT_ID=123456789012
#   export AWS_REGION=us-east-1
#   ./scripts/docker-push-ecr.sh
# =============================================================================
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO="${ECR_REPO:-workmate-backend}"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo "manual")}"

if [[ -z "${AWS_ACCOUNT_ID:-}" ]]; then
  echo "❌  AWS_ACCOUNT_ID is not set. Export it before running this script."
  exit 1
fi

ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FULL_IMAGE="${ECR_REGISTRY}/${ECR_REPO}"

echo "════════════════════════════════════════════════════════"
echo "  WorkMate ECR Push"
echo "  Registry : ${ECR_REGISTRY}"
echo "  Repo     : ${ECR_REPO}"
echo "  Tags     : latest, ${IMAGE_TAG}"
echo "════════════════════════════════════════════════════════"

# ── Step 1: Authenticate Docker with ECR ─────────────────────────────────────
echo ""
echo "▶ Authenticating Docker with ECR…"
aws ecr get-login-password --region "${AWS_REGION}" \
  | docker login --username AWS --password-stdin "${ECR_REGISTRY}"

# ── Step 2: Create ECR repo if it doesn't already exist ──────────────────────
echo ""
echo "▶ Ensuring ECR repo '${ECR_REPO}' exists…"
aws ecr describe-repositories \
  --region "${AWS_REGION}" \
  --repository-names "${ECR_REPO}" \
  > /dev/null 2>&1 \
|| aws ecr create-repository \
  --region "${AWS_REGION}" \
  --repository-name "${ECR_REPO}" \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256 \
  > /dev/null

# ── Step 3: Build image for linux/amd64 (EKS node arch) ──────────────────────
echo ""
echo "▶ Building image for linux/amd64…"
docker buildx build \
  --platform linux/amd64 \
  --tag "${FULL_IMAGE}:latest" \
  --tag "${FULL_IMAGE}:${IMAGE_TAG}" \
  --file Dockerfile \
  .

# ── Step 4: Push both tags ────────────────────────────────────────────────────
echo ""
echo "▶ Pushing tags to ECR…"
docker push "${FULL_IMAGE}:latest"
docker push "${FULL_IMAGE}:${IMAGE_TAG}"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "✅  Image pushed successfully."
echo ""
echo "  Full image URI (use this in k8s/deployment.yaml):"
echo "  ${FULL_IMAGE}:${IMAGE_TAG}"
echo ""
echo "  Next steps:"
echo "  1. Update k8s/deployment.yaml  →  image: ${FULL_IMAGE}:${IMAGE_TAG}"
echo "  2. kubectl apply -f k8s/"
