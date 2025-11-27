#!/bin/bash
# Full Diagnostics Script for StudioCore
# Runs all diagnostic checks and reports results

set -e  # Exit on error

echo "=========================================="
echo "StudioCore - Full Diagnostics"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run full system diagnostics (workflow checks)
echo ">>> Running full system diagnostics..."
python3 main/full_system_diagnostics.py || {
    echo "❌ Full system diagnostics failed"
    exit 1
}

# Run full project audit (compilation, OpenAPI, requirements)
echo ""
echo ">>> Running full project audit..."
python3 main/full_project_audit.py || {
    echo "❌ Full project audit failed"
    exit 1
}

echo ""
echo "=========================================="
echo "✅ All diagnostics completed successfully"
echo "=========================================="

