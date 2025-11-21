#!/usr/bin/env bash
set -e

echo ">>> Running StudioCore FULL diagnostics..."
python3 main/full_system_diagnostics.py
echo ">>> Diagnostics complete (written to main/lgp.txt)"
