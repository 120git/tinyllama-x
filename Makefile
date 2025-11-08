# Makefile for TinyLlama-X
# Includes container image build, push, and verification targets

.PHONY: help install test lint type-check clean
.PHONY: image image-dev push-image verify-image

# Default target
help:
	@echo "TinyLlama-X Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install package in development mode"
	@echo "  test          - Run tests with pytest"
	@echo "  lint          - Run ruff linter"
	@echo "  type-check    - Run mypy type checker"
	@echo "  clean         - Remove build artifacts"
	@echo ""
	@echo "Container targets:"
	@echo "  image         - Build local Docker image (single-arch)"
	@echo "  image-dev     - Build development Docker image with test tools"
	@echo "  push-image    - Build and push multi-arch image to registry"
	@echo "  verify-image  - Verify Cosign signature and attestations"
	@echo ""

# Installation
install:
	pip install -e .

# Testing
test:
	pytest -q tests

# Linting
lint:
	ruff check .

# Type checking
type-check:
	mypy tinyllamax

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

# Container image targets
image:
	@./scripts/build_image.sh

image-dev:
	@./scripts/build_image.sh --dev

push-image:
	@./scripts/push_image.sh

verify-image:
	@echo "Verifying image signature and attestations..."
	@echo ""
	@echo "Image: ghcr.io/120git/tinyllama-x:latest"
	@echo ""
	@echo "1. Verifying signature (keyless):"
	@COSIGN_EXPERIMENTAL=1 cosign verify ghcr.io/120git/tinyllama-x:latest || echo "Signature verification failed"
	@echo ""
	@echo "2. Verifying SBOM attestation:"
	@COSIGN_EXPERIMENTAL=1 cosign verify-attestation --type spdx ghcr.io/120git/tinyllama-x:latest | jq '.payload | @base64d | fromjson' || echo "SBOM attestation verification failed"
	@echo ""
	@echo "3. Verifying provenance attestation:"
	@COSIGN_EXPERIMENTAL=1 cosign verify-attestation --type slsaprovenance ghcr.io/120git/tinyllama-x:latest | jq '.payload | @base64d | fromjson' || echo "Provenance attestation verification failed"
	@echo ""
	@echo "✓ Verification complete"
