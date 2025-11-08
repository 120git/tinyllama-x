#!/usr/bin/env bash
# Multi-arch image build and push script using Docker buildx
# Usage: ./scripts/push_image.sh [--registry REGISTRY] [--tag TAG] [--platforms PLATFORMS]

set -euo pipefail

# Default values
REGISTRY="${CONTAINER_REGISTRY:-ghcr.io/120git}"
TAG="${IMAGE_TAG:-latest}"
PLATFORMS="${DOCKER_PLATFORMS:-linux/amd64,linux/arm64}"
DOCKERFILE="Dockerfile"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --platforms)
            PLATFORMS="$2"
            shift 2
            ;;
        --dev)
            DOCKERFILE="Dockerfile.dev"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--registry REGISTRY] [--tag TAG] [--platforms PLATFORMS] [--dev]"
            exit 1
            ;;
    esac
done

IMAGE="${REGISTRY}/tinyllamax:${TAG}"

echo "Building and pushing multi-arch Docker image..."
echo "  Dockerfile: ${DOCKERFILE}"
echo "  Registry:   ${REGISTRY}"
echo "  Image:      ${IMAGE}"
echo "  Platforms:  ${PLATFORMS}"
echo ""

# Ensure buildx is available
if ! docker buildx version &>/dev/null; then
    echo "Error: docker buildx is not available"
    exit 1
fi

# Create builder if it doesn't exist
if ! docker buildx inspect tinyllamax-builder &>/dev/null; then
    echo "Creating buildx builder 'tinyllamax-builder'..."
    docker buildx create --name tinyllamax-builder --use --bootstrap
else
    echo "Using existing buildx builder 'tinyllamax-builder'..."
    docker buildx use tinyllamax-builder
fi

# Build and push multi-arch image
docker buildx build \
    --file "${DOCKERFILE}" \
    --platform "${PLATFORMS}" \
    --tag "${IMAGE}" \
    --push \
    --progress=plain \
    .

echo ""
echo "✓ Multi-arch image pushed: ${IMAGE}"
echo ""
echo "Verify with:"
echo "  docker pull ${IMAGE}"
echo "  docker run --rm -it ${IMAGE}"
