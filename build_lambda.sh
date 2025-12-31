#!/bin/bash
set -euo pipefail

PYTHON_VERSION="3.10"
ZIP_NAME="deployment-package.zip"
PKG_DIR="package"

echo "Building Lambda deployment package..."

rm -rf "$PKG_DIR" "$ZIP_NAME" .venv requirements.lock.txt
mkdir -p "$PKG_DIR"

echo "Syncing dependencies with uv (from uv.lock/pyproject.toml)..."
uv sync --python "$PYTHON_VERSION" --frozen

echo "Exporting locked requirements..."
uv export --format requirements-txt --frozen --no-dev -o requirements.lock.txt

echo "Installing dependencies into package/..."
uv pip install \
  --python "$PYTHON_VERSION" \
  --target "$PKG_DIR" \
  -r requirements.lock.txt

echo "Copying application code..."
cp -r daily_word_bot "$PKG_DIR/"
cp lambda_webhook.py "$PKG_DIR/"
cp lambda_scheduler.py "$PKG_DIR/"

if [ -f "service-account.json" ]; then
  cp service-account.json "$PKG_DIR/"
  echo "Included service-account.json"
else
  echo "WARNING: service-account.json not found!"
fi

echo "Creating zip..."
(
  cd "$PKG_DIR"
  zip -r "../$ZIP_NAME" . -x "*.pyc" -x "__pycache__/*"
)

echo "Cleaning up..."
rm -rf "$PKG_DIR" requirements.lock.txt

echo "Created $ZIP_NAME"
ls -lh "$ZIP_NAME"
