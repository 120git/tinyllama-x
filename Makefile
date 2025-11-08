.PHONY: help build clean test lint deb rpm appimage all

VERSION ?= 0.1.0
OUT_DIR ?= $(PWD)/out

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build wheel and sdist
	@echo "Building wheel and sdist..."
	@bash scripts/build_wheel.sh

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf dist/ build/ *.egg-info out/ AppDir/ AppImageBuilder.yml
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true

test: ## Run tests with pytest
	@echo "Running tests..."
	@pytest -q tests/

lint: ## Run linters (ruff + mypy)
	@echo "Running ruff..."
	@ruff check .
	@echo "Running mypy..."
	@mypy tinyllamax

deb: build ## Build .deb package
	@echo "Building .deb package..."
	@VERSION=$(VERSION) OUT_DIR=$(OUT_DIR) bash scripts/make_deb.sh

rpm: build ## Build .rpm package
	@echo "Building .rpm package..."
	@VERSION=$(VERSION) OUT_DIR=$(OUT_DIR) bash scripts/make_rpm.sh

appimage: build ## Build AppImage
	@echo "Building AppImage..."
	@VERSION=$(VERSION) OUT_DIR=$(OUT_DIR) bash scripts/make_appimage.sh

all: deb rpm appimage ## Build all packages (deb, rpm, appimage)
	@echo "All packages built successfully!"
	@echo "Artifacts in $(OUT_DIR):"
	@ls -lh $(OUT_DIR)/
