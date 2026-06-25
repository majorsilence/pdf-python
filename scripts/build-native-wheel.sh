#!/usr/bin/env bash
# =============================================================================
# build-native-wheel.sh — Build and smoke-test a local wheel with bundled
#                          pdfnative libraries.
#
# Usage:
#   ./scripts/build-native-wheel.sh [RELEASE_TAG]
#
#   RELEASE_TAG  GitHub release tag to download native libs from.
#                Defaults to the latest release of majorsilence/Reporting.
#
# Examples:
#   ./scripts/build-native-wheel.sh           # use latest pdfnative release
#   ./scripts/build-native-wheel.sh 26.0.1    # use a specific release
#
# Prerequisites:
#   pip install build wheel
#   gh (GitHub CLI) — https://cli.github.com — must be authenticated
#
# What this script does:
#   1. Downloads the pdfnative zip for your platform from majorsilence/Reporting
#   2. Unpacks native libs into src/majorsilence_pdf/native/
#   3. Builds the wheel and verifies native libs are inside it
#   4. Creates a temporary venv, installs the wheel
#   5. Runs tests/test_pdf_native.py as a smoke test
#
# To install the built wheel in your own project afterwards:
#   pip install dist/majorsilence_pdf-*.whl --force-reinstall
# =============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NATIVE_DIR="$REPO_ROOT/src/majorsilence_pdf/native"
WORK_DIR="/tmp/pdfnative-build-$$"
TEST_VENV="$WORK_DIR/test-venv"

cleanup() { rm -rf "$WORK_DIR"; }
trap cleanup EXIT

# ── Resolve release tag ───────────────────────────────────────────────────────
echo "=== Resolving pdfnative release ==="
if [[ $# -ge 1 ]]; then
    RELEASE_TAG="$1"
else
    echo "No release tag specified — fetching latest from majorsilence/Reporting..."
    RELEASE_TAG=$(gh release view --repo majorsilence/Reporting --json tagName -q .tagName)
fi
echo "Using release: $RELEASE_TAG"

# ── Detect platform asset and RID ─────────────────────────────────────────────
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux)
        case "$ARCH" in
            x86_64)  ASSET_PATTERN="*-majorsilence-pdfnative-linux-x64.zip";  RID="linux-x64"  ;;
            aarch64) ASSET_PATTERN="*-majorsilence-pdfnative-linux-arm64.zip"; RID="linux-arm64" ;;
            *)       echo "Unsupported Linux arch: $ARCH"; exit 1 ;;
        esac ;;
    Darwin)
        # macOS zip bundles both osx-x64 and osx-arm64 subdirs
        ASSET_PATTERN="*-majorsilence-pdfnative-osx.zip"
        case "$ARCH" in
            x86_64) RID="osx-x64"  ;;
            arm64)  RID="osx-arm64" ;;
            *)      echo "Unsupported macOS arch: $ARCH"; exit 1 ;;
        esac ;;
    *)
        echo "Unsupported OS: $OS (run this script on Linux or macOS)"
        exit 1 ;;
esac
echo "Asset pattern: $ASSET_PATTERN  (RID: $RID)"

# ── Download native libs ──────────────────────────────────────────────────────
echo ""
echo "=== Downloading native libs ==="
mkdir -p "$WORK_DIR"
gh release download "$RELEASE_TAG" \
    --repo majorsilence/Reporting \
    --pattern "$ASSET_PATTERN" \
    --dir "$WORK_DIR"

# ── Extract ───────────────────────────────────────────────────────────────────
mkdir -p "$WORK_DIR/unpacked"
ASSET=$(ls "$WORK_DIR"/*.zip | head -1)
echo "Extracting: $(basename "$ASSET")"
unzip -q "$ASSET" -d "$WORK_DIR/unpacked"
echo "Zip contents:"
find "$WORK_DIR/unpacked" -type f

# ── Copy the right RID subdirectory into the package ─────────────────────────
echo ""
echo "=== Copying native libs into package (RID=$RID) ==="
find "$NATIVE_DIR" -maxdepth 1 -type f ! -name '.gitkeep' ! -name '.gitignore' -delete

# The zip layout is: majorsilence-pdfnative/<RID>/<library files>
RID_DIR=$(find "$WORK_DIR/unpacked" -type d -name "$RID" | head -1)
if [[ -z "$RID_DIR" ]]; then
    echo "ERROR: No directory named '$RID' found in the zip. Available dirs:"
    find "$WORK_DIR/unpacked" -type d
    exit 1
fi
echo "Copying from: $RID_DIR"
find "$RID_DIR" -type f -exec cp -v {} "$NATIVE_DIR/" \;

echo "native/ contents:"
ls -lh "$NATIVE_DIR/"

# ── Create venv with build tools ─────────────────────────────────────────────
echo ""
echo "=== Setting up build venv ==="
python3 -m venv "$TEST_VENV"
"$TEST_VENV/bin/pip" install --quiet build wheel

# ── Build wheel ───────────────────────────────────────────────────────────────
echo ""
echo "=== Building wheel ==="
cd "$REPO_ROOT"
mkdir -p dist
"$TEST_VENV/bin/python" -m build --wheel --outdir dist/

# ── Verify wheel contains native libs ────────────────────────────────────────
echo ""
echo "=== Verifying wheel ==="
WHEEL=$(ls dist/majorsilence_pdf-*.whl | tail -1)
NATIVE_FILES=$("$TEST_VENV/bin/python" -m zipfile -l "$WHEEL" | grep native/ || true)
if [[ -z "$NATIVE_FILES" ]]; then
    echo "ERROR: no native/ files found in wheel — packaging fix needed"
    exit 1
fi
echo "$NATIVE_FILES"
echo "Wheel: $WHEEL ($(du -sh "$WHEEL" | cut -f1))"

# ── Install wheel into the same venv for smoke test ──────────────────────────
echo ""
echo "=== Installing wheel ==="
"$TEST_VENV/bin/pip" install --quiet "$WHEEL"

echo ""
echo "=== Running smoke test (tests/test_pdf_native.py) ==="
echo "─────────────────────────────────────────────────────────"
"$TEST_VENV/bin/python" -m pytest "$REPO_ROOT/tests/test_pdf_native.py" -v
echo "─────────────────────────────────────────────────────────"

echo ""
echo "All done. Smoke test passed."
echo ""
echo "To install in your own project:"
echo "  pip install \"$WHEEL\" --force-reinstall"
