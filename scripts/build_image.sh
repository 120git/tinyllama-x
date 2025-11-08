#!/usr/bin/env bash
# Local image build script using Docker buildx (single-arch, load to local Docker)
# Usage: ./scripts/build_image.sh [--dev] [--platform PLATFORM] [--tag TAG]

set -euo pipefail

# Default values
DOCKERFILE="Dockerfile"
PLATFORM="${DOCKER_PLATFORM:-linux/amd64}"
TAG="${IMAGE_TAG:-tinyllamax:local}"
LOAD="--load"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DOCKERFILE="Dockerfile.dev"
            TAG="${IMAGE_TAG:-tinyllamax-dev:local}"
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dev] [--platform PLATFORM] [--tag TAG]"
            exit 1
            ;;
    esac
done

echo "Building Docker image..."
echo "  Dockerfile: ${DOCKERFILE}"
echo "  Platform:   ${PLATFORM}"
echo "  Tag:        ${TAG}"
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

# Build and load image locally
docker buildx build \
    --file "${DOCKERFILE}" \
    --platform "${PLATFORM}" \
    --tag "${TAG}" \
    ${LOAD} \
    --progress=plain \
    .

echo ""
echo "✓ Build complete: ${TAG}"
echo ""
echo "Run with:"
echo "  docker run --rm -it ${TAG}"
