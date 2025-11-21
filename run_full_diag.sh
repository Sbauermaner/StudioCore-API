#!/usr/bin/env bash
set -euo pipefail

# Resolve project root
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$ROOT_DIR"

python -m pip install --upgrade pip
pip install -r requirements.txt

pytest
