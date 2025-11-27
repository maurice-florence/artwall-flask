#!/usr/bin/env bash
# sanity_check.sh: Run basic checks before commit/push

set -e

# 1. Run smoke tests (pytest)
echo "Running pytest..."
pytest --maxfail=1 --disable-warnings -v

# 2. Run flake8 for linting
echo "Running flake8..."
flake8 .

# 3. Run black in check mode
echo "Running black --check..."
black --check .

# 4. (Optional) Tiny integration test for Firebase endpoint
echo "Running Firebase integration test..."
python sanity_firebase_check.py || echo "[WARN] Firebase integration test failed (optional)"

echo "Sanity check complete."
