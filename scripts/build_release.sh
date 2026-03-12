#!/usr/bin/env bash
set -euo pipefail

# Build and package dwarp binary for Linux using PyInstaller

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
DIST_DIR="$ROOT_DIR/dist"
BUILD_DIR="$ROOT_DIR/build"
OUT_NAME="dwarp"
TARBALL_NAME="${OUT_NAME}-linux.tar.gz"

echo "==> Cleaning previous build artifacts"
rm -rf "$BUILD_DIR/$OUT_NAME" "$DIST_DIR/$OUT_NAME" "$DIST_DIR/$TARBALL_NAME" || true

echo "==> Building wheel/sdist (optional)"
if command -v python &>/dev/null; then
  python -m pip -q install --upgrade build >/dev/null 2>&1 || true
  python -m build || true
fi

echo "==> Building PyInstaller binary"
pyinstaller --clean --noconfirm "$ROOT_DIR/dwarp.spec"

echo "==> Preparing release directory"
RELEASE_DIR="$DIST_DIR/${OUT_NAME}-linux"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

# Move binary and include helper files
if [[ -f "$DIST_DIR/dwarp" ]]; then
  install -m 755 "$DIST_DIR/dwarp" "$RELEASE_DIR/$OUT_NAME"
elif [[ -f "$DIST_DIR/dwarp/dwarp" ]]; then
  install -m 755 "$DIST_DIR/dwarp/dwarp" "$RELEASE_DIR/$OUT_NAME"
else
  echo "ERROR: Built binary not found. Expected PyInstaller dist outputs under $DIST_DIR."
  ls -l "$DIST_DIR" || true
  exit 1
fi

cp -f "$ROOT_DIR/README.md" "$RELEASE_DIR/" || true
cp -f "$ROOT_DIR/LICENSE" "$RELEASE_DIR/" 2>/dev/null || true
cp -f "$ROOT_DIR/scripts/install.sh" "$RELEASE_DIR/install.sh"
cp -f "$ROOT_DIR/scripts/uninstall.sh" "$RELEASE_DIR/uninstall.sh"
chmod +x "$RELEASE_DIR/install.sh" "$RELEASE_DIR/uninstall.sh"

echo "==> Creating tar.gz"
(
  cd "$DIST_DIR"
  tar -czf "$TARBALL_NAME" "${OUT_NAME}-linux"
)

echo "==> Done: $DIST_DIR/$TARBALL_NAME"

