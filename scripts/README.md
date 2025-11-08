# Scripts for SBOM Generation and Artifact Signing

This directory contains scripts for generating Software Bill of Materials (SBOM), signing release artifacts, and creating provenance attestations.

## Prerequisites

- [Syft](https://github.com/anchore/syft) - For SBOM generation
- [Cosign](https://github.com/sigstore/cosign) - For artifact signing

## Setup for GitHub Actions

### 1. Generate Cosign Keypair

A Cosign keypair has already been generated for this project:
- **Public key**: `resources/keys/cosign.pub` (committed to repository)
- **Private key**: Must be stored in GitHub Secrets

### 2. Add COSIGN_KEY to GitHub Secrets

To enable artifact signing in GitHub Actions, you must add the private key as a repository secret:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `COSIGN_KEY`
5. Value: Paste the contents of the private key file

**Note**: The private key file is NOT in this repository for security reasons. If you need to regenerate it:

```bash
# Generate new keypair (use empty password for CI)
cd resources/keys
COSIGN_PASSWORD="" cosign generate-key-pair

# Add cosign.key to GitHub Secrets (then delete the local file)
# Keep cosign.pub in the repository
```

## Scripts Overview

### `generate_sbom.sh`

Generates Software Bill of Materials (SBOM) in SPDX JSON format for all release artifacts:

- `sbom-wheel.spdx.json` - Python wheel packages
- `sbom-deb.spdx.json` - Debian packages
- `sbom-rpm.spdx.json` - RPM packages
- `sbom-appimage.spdx.json` - AppImage packages
- `sbom-source.spdx.json` - Source code

**Usage:**
```bash
bash scripts/generate_sbom.sh
```

### `sign_artifacts.sh`

Signs all release artifacts using Cosign and creates attestations with SBOM information.

Generates for each artifact:
- `.sig` - Cryptographic signature
- `.att` - SBOM attestation

**Requirements:**
- `COSIGN_KEY` environment variable must be set

**Usage:**
```bash
export COSIGN_KEY=$(cat path/to/cosign.key)
export COSIGN_PASSWORD=""
bash scripts/sign_artifacts.sh
```

### `generate_provenance.sh`

Generates SLSA-style provenance attestation documenting the build context.

Output: `out/provenance.json`

Contains:
- GitHub Actions workflow run URL
- Commit SHA and branch reference
- Workflow name and build timestamp
- SHA-256 checksums of all artifacts

**Usage:**
```bash
bash scripts/generate_provenance.sh
```

## Local Testing

To test the scripts locally:

```bash
# 1. Create mock artifacts
mkdir -p dist out
echo "test" > dist/tinyllamax-0.1.0-py3-none-any.whl
echo "test" > out/tinyllamax_0.1.0_amd64.deb

# 2. Generate SBOMs
bash scripts/generate_sbom.sh

# 3. Sign artifacts (requires COSIGN_KEY)
export COSIGN_KEY=$(cat /path/to/cosign.key)
export COSIGN_PASSWORD=""
bash scripts/sign_artifacts.sh

# 4. Generate provenance
bash scripts/generate_provenance.sh

# 5. Verify a signature
cosign verify-blob --key resources/keys/cosign.pub \
  --signature out/tinyllamax_0.1.0_amd64.deb.sig \
  --insecure-ignore-tlog=true --insecure-ignore-sct=true \
  out/tinyllamax_0.1.0_amd64.deb
```

## Workflow Integration

These scripts are integrated into `.github/workflows/release.yml`:

1. Build artifacts (wheels, debs, rpms, AppImages)
2. Install Syft and Cosign
3. Generate SBOMs → `scripts/generate_sbom.sh`
4. Sign artifacts → `scripts/sign_artifacts.sh`
5. Generate provenance → `scripts/generate_provenance.sh`
6. Verify signatures
7. Upload all artifacts and metadata to GitHub Release

## Security Notes

- Private keys should NEVER be committed to the repository
- The `--tlog-upload=false` flag is used to skip transparency log uploads (suitable for internal use)
- For production use, consider enabling transparency log uploads and TUF verification
- Signatures provide integrity and authenticity verification
- SBOMs enable supply chain transparency and vulnerability tracking
- Provenance attestations provide build reproducibility evidence

## Troubleshooting

**"COSIGN_KEY environment variable not set"**
- Ensure you've exported the COSIGN_KEY variable before running `sign_artifacts.sh`
- In GitHub Actions, verify the secret is properly configured

**"No .deb/.rpm/.AppImage files found"**
- Ensure you've built the packages before running the scripts
- Check that files are in the correct directories (`dist/` for wheels, `out/` for other packages)

**Network errors with Syft/Cosign**
- These tools may try to fetch updates from the internet
- The errors are usually non-fatal and can be ignored
- Artifacts will still be generated correctly
