#!/usr/bin/env bash
# sanity_check.sh: Run basic checks before commit/push

set -e

# 1. Run smoke tests (pytest)
echo "Running pytest (venv)..."
"$(pwd)/.venv/Scripts/python.exe" -m pytest --maxfail=1 --disable-warnings -v

# 2. Run flake8 for linting
echo "Running flake8 (venv)..."
"$(pwd)/.venv/Scripts/flake8" .

# 3. Run black in check mode
echo "Running black --check (venv)..."
"$(pwd)/.venv/Scripts/black" --check .

# 4. (Optional) Tiny integration test for Firebase endpoint
echo "Running Firebase integration test (venv)..."
"$(pwd)/.venv/Scripts/python.exe" sanity_firebase_check.py || echo "[WARN] Firebase integration test failed (optional)"

echo "Sanity check complete."
