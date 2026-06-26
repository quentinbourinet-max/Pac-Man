#!/usr/bin/env bash
# Build a standalone Linux binary with PyInstaller and prepare for itch.io upload.
#
# Usage:
#   ./packaging/build.sh              (build only)
#   ./packaging/build.sh --push       (build + butler push)
#
# Requirements:
#   - A .venv activated, or uv available
#   - mazegenerator-*.whl present at repo root (same as `make install`)
#   - butler in PATH for --push

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/dist/linux-x86_64"
APP_DIR="$OUT/pac-man"
ITCH_USER="sayca"
ITCH_GAME="pac-man"
ITCH_CHANNEL="linux-x86_64"

# -- 1. Dependencies ------------------------------------------------------------

echo "[build] Installing mazegenerator wheel..."
pip install "$ROOT"/mazegenerator-*.whl --quiet

echo "[build] Installing PyInstaller..."
pip install pyinstaller --quiet

# -- 2. PyInstaller -------------------------------------------------------------

echo "[build] Running PyInstaller..."
pyinstaller \
    --name pac-man \
    --distpath "$OUT" \
    --workpath "$ROOT/build/pyinstaller-work" \
    --specpath "$ROOT/build" \
    --add-data "$ROOT/data:data" \
    --paths "$ROOT/src" \
    --onedir \
    --noconfirm \
    "$ROOT/packaging/main_binary.py"

# -- 3. itch manifest -----------------------------------------------------------

echo "[build] Copying itch manifest..."
cp "$ROOT/packaging/.itch.toml" "$APP_DIR/.itch.toml"

echo ""
echo "Build complete → $APP_DIR"
echo ""

# -- 4. Optional butler push ---------------------------------------------------

if [[ "${1:-}" == "--push" ]]; then
    if ! command -v butler &> /dev/null; then
        echo "Error: butler not found in PATH. Download from https://itch.io/docs/butler/"
        exit 1
    fi
    echo "[push] Pushing to itch.io: $ITCH_USER/$ITCH_GAME:$ITCH_CHANNEL"
    butler push "$APP_DIR" "$ITCH_USER/$ITCH_GAME:$ITCH_CHANNEL"
else
    echo "To push to itch.io, run:"
    echo "  butler push $APP_DIR $ITCH_USER/$ITCH_GAME:$ITCH_CHANNEL"
    echo ""
    echo "Or rerun with:  ./packaging/build.sh --push"
fi
