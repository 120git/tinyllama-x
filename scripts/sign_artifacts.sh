#!/usr/bin/env bash
# Sign release artifacts using Cosign
# Creates .sig (signature) and .att (attestation) files for each artifact

set -euo pipefail

# Check for COSIGN_KEY environment variable
if [[ -z "${COSIGN_KEY:-}" ]]; then
    echo "❌ Error: COSIGN_KEY environment variable not set"
    echo "   Set it with: export COSIGN_KEY=\$(cat cosign.key)"
    echo "   Or in CI: use GitHub Secrets"
    exit 1
fi

echo "🔐 Signing TinyLlama-X artifacts with Cosign..."

# Function to sign a single artifact
sign_artifact() {
    local file="$1"
    local basename=$(basename "$file")
    local ext="${basename##*.}"
    
    echo "  → Signing: $basename"
    
    # Generate signature
    cosign sign-blob --key env://COSIGN_KEY --yes --tlog-upload=false "$file" > "$file.sig"
    echo "    ✓ Created $basename.sig"
    
    # Find corresponding SBOM file
    local sbom_file=""
    case "$ext" in
        whl)
            sbom_file="out/sbom-wheel.spdx.json"
            ;;
        deb)
            sbom_file="out/sbom-deb.spdx.json"
            ;;
        rpm)
            sbom_file="out/sbom-rpm.spdx.json"
            ;;
        AppImage)
            sbom_file="out/sbom-appimage.spdx.json"
            ;;
    esac
    
    # Generate attestation if SBOM exists
    if [[ -f "$sbom_file" ]]; then
        cosign attest-blob --key env://COSIGN_KEY --yes --tlog-upload=false \
            --predicate "$sbom_file" \
            --type spdx \
            "$file" > "$file.att"
        echo "    ✓ Created $basename.att (with SBOM attestation)"
    else
        echo "    ⚠ SBOM not found: $sbom_file (skipping attestation)"
    fi
}

# Sign .deb packages
shopt -s nullglob
for file in out/*.deb; do
    [[ -f "$file" ]] && sign_artifact "$file"
done

# Sign .rpm packages
for file in out/*.rpm; do
    [[ -f "$file" ]] && sign_artifact "$file"
done

# Sign .AppImage packages
for file in out/*.AppImage; do
    [[ -f "$file" ]] && sign_artifact "$file"
done

# Sign .whl packages
for file in dist/*.whl; do
    [[ -f "$file" ]] && sign_artifact "$file"
done
shopt -u nullglob

echo "✅ Artifact signing complete!"
