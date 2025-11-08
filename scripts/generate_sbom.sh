#!/usr/bin/env bash
# Generate Software Bill of Materials (SBOM) for all release artifacts
# Uses Syft to create SPDX-JSON format SBOMs

set -euo pipefail

# Ensure out directory exists
mkdir -p out

echo "🔍 Generating SBOMs for TinyLlama-X artifacts..."

# Generate SBOM for Python wheel packages
if compgen -G "dist/*.whl" > /dev/null; then
    echo "  → Scanning Python wheel packages..."
    for whl in dist/*.whl; do
        syft scan "file:$whl" -o spdx-json > out/sbom-wheel.spdx.json
        break
    done
    echo "    ✓ out/sbom-wheel.spdx.json"
else
    echo "  ⚠ No .whl files found in dist/"
fi

# Generate SBOM for .deb packages
if compgen -G "out/*.deb" > /dev/null; then
    echo "  → Scanning .deb packages..."
    for deb in out/*.deb; do
        syft scan "file:$deb" -o spdx-json > out/sbom-deb.spdx.json
        break
    done
    echo "    ✓ out/sbom-deb.spdx.json"
else
    echo "  ⚠ No .deb files found in out/"
fi

# Generate SBOM for .rpm packages
if compgen -G "out/*.rpm" > /dev/null; then
    echo "  → Scanning .rpm packages..."
    for rpm in out/*.rpm; do
        syft scan "file:$rpm" -o spdx-json > out/sbom-rpm.spdx.json
        break
    done
    echo "    ✓ out/sbom-rpm.spdx.json"
else
    echo "  ⚠ No .rpm files found in out/"
fi

# Generate SBOM for AppImage packages
if compgen -G "out/*.AppImage" > /dev/null; then
    echo "  → Scanning AppImage packages..."
    for appimage in out/*.AppImage; do
        syft scan "file:$appimage" -o spdx-json > out/sbom-appimage.spdx.json
        break
    done
    echo "    ✓ out/sbom-appimage.spdx.json"
else
    echo "  ⚠ No .AppImage files found in out/"
fi

# Generate SBOM for source code
echo "  → Scanning source directory..."
syft scan dir:. -o spdx-json > out/sbom-source.spdx.json
echo "    ✓ out/sbom-source.spdx.json"

echo "✅ SBOM generation complete!"
