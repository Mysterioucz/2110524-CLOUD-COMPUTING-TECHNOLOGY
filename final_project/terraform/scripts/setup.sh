#!/bin/bash
set -e

# Navigate to project root relative to this script
cd "$(dirname "$0")/.."
ROOT_PATH=$(pwd)
DIST_PATH="$ROOT_PATH/dist"

echo "🧹 Cleaning previous build..."
rm -rf "$DIST_PATH"
mkdir -p "$DIST_PATH"

echo "📦 Installing requirements (Linux x86_64 compatible binaries)..."
# ต้องระบุ --platform เพื่อบังคับ pip ดาวน์โหลด binary ที่เหมาะกับ AWS Lambda Linux x86_64
# ไม่งั้น pip จะใช้ macOS binary ซึ่ง Lambda รันไม่ได้!
pip3 install -r requirements.txt -t "$DIST_PATH/" --no-cache-dir \
  --platform manylinux2014_x86_64 \
  --python-version 3.11 \
  --only-binary=:all: \
  --implementation cp

echo "📂 Copying source code..."
# Ensure the src folder structure is maintained
cp -R src "$DIST_PATH/src"

echo "✅ Build preparation complete. Ready for OpenTofu archiving!"
