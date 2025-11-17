#!/usr/bin/env bash
# Generate SLSA-style provenance attestation for release artifacts
# Documents build context, workflow, and artifact checksums

set -euo pipefail

# Ensure out directory exists
mkdir -p out

echo "📋 Generating provenance attestation..."

# Get environment variables (with defaults for local testing)
GITHUB_RUN_ID="${GITHUB_RUN_ID:-local}"
GITHUB_RUN_NUMBER="${GITHUB_RUN_NUMBER:-0}"
GITHUB_WORKFLOW="${GITHUB_WORKFLOW:-local-build}"
GITHUB_REPOSITORY="${GITHUB_REPOSITORY:-120git/tinyllama-x}"
GITHUB_SERVER_URL="${GITHUB_SERVER_URL:-https://github.com}"
GITHUB_SHA="${GITHUB_SHA:-$(git rev-parse HEAD 2>/dev/null || echo 'unknown')}"
GITHUB_REF="${GITHUB_REF:-$(git symbolic-ref HEAD 2>/dev/null || echo 'unknown')}"
GITHUB_ACTOR="${GITHUB_ACTOR:-local-user}"

# Build URL for the workflow run
BUILDER_URL="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"

# Get timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Start JSON structure
cat > out/provenance.json <<EOF
{
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildType": "https://github.com/Attestations/GitHubActionsWorkflow@v1",
    "builder": {
      "id": "${BUILDER_URL}",
      "version": {
        "github_run_id": "${GITHUB_RUN_ID}",
        "github_run_number": "${GITHUB_RUN_NUMBER}"
      }
    },
    "invocation": {
      "configSource": {
        "uri": "${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}",
        "digest": {
          "sha1": "${GITHUB_SHA}"
        },
        "entryPoint": ".github/workflows/${GITHUB_WORKFLOW}.yml"
      },
      "parameters": {
        "ref": "${GITHUB_REF}",
        "workflow": "${GITHUB_WORKFLOW}",
        "actor": "${GITHUB_ACTOR}"
      },
      "environment": {
        "github_run_id": "${GITHUB_RUN_ID}",
        "github_run_number": "${GITHUB_RUN_NUMBER}"
      }
    },
    "metadata": {
      "buildInvocationId": "${GITHUB_RUN_ID}",
      "buildStartedOn": "${TIMESTAMP}",
      "buildFinishedOn": "${TIMESTAMP}",
      "completeness": {
        "parameters": true,
        "environment": false,
        "materials": false
      },
      "reproducible": false
    },
    "materials": [
      {
        "uri": "${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}",
        "digest": {
          "sha1": "${GITHUB_SHA}"
        }
      }
    ]
  },
  "subject": [
EOF

# Add artifact checksums
first_artifact=true
shopt -s nullglob
for pattern in "out/*.deb" "out/*.rpm" "out/*.AppImage" "dist/*.whl"; do
    for file in $pattern; do
        if [[ -f "$file" ]]; then
            basename=$(basename "$file")
            sha256=$(sha256sum "$file" | cut -d' ' -f1)
            
            if [[ "$first_artifact" == "true" ]]; then
                first_artifact=false
            else
                echo "," >> out/provenance.json
            fi
            
            cat >> out/provenance.json <<EOF
    {
      "name": "${basename}",
      "digest": {
        "sha256": "${sha256}"
      }
    }
EOF
        fi
    done
done
shopt -u nullglob

# Close JSON structure
cat >> out/provenance.json <<EOF

  ]
}
EOF

echo "✅ Provenance generated: out/provenance.json"
echo "   Builder: ${BUILDER_URL}"
echo "   Commit: ${GITHUB_SHA}"
echo "   Workflow: ${GITHUB_WORKFLOW}"
