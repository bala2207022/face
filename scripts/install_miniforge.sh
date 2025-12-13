#!/usr/bin/env bash
set -euo pipefail

# Installs Miniforge (conda-forge Miniforge) for Linux or macOS and then
# creates a conda env and installs heavy packages used by this project.
# Usage: bash scripts/install_miniforge.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="$HOME/miniforge3"

echo "Detecting platform..."
OS=$(uname -s)
ARCH=$(uname -m)

if [ "$OS" = "Darwin" ]; then
  PLATFORM=MacOSX
elif [ "$OS" = "Linux" ]; then
  PLATFORM=Linux
else
  echo "Unsupported OS: $OS" >&2
  exit 1
fi

if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then
  ARCH_TAG=x86_64
elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
  ARCH_TAG=arm64
else
  echo "Unsupported architecture: $ARCH" >&2
  exit 1
fi

echo "Platform: $OS, Arch: $ARCH"

RELEASE_BASE="https://github.com/conda-forge/miniforge/releases/latest/download"
if [ "$PLATFORM" = "MacOSX" ]; then
  if [ "$ARCH_TAG" = "arm64" ]; then
    FNAME=Miniforge3-MacOSX-arm64.sh
  else
    FNAME=Miniforge3-MacOSX-x86_64.sh
  fi
else
  FNAME=Miniforge3-Linux-${ARCH_TAG}.sh
fi

URL="$RELEASE_BASE/$FNAME"

echo "Downloading Miniforge installer: $URL"
TMPFILE="/tmp/$FNAME"
curl -L "$URL" -o "$TMPFILE"
chmod +x "$TMPFILE"

echo "Running Miniforge installer (non-interactive) to $INSTALL_DIR"
bash "$TMPFILE" -b -p "$INSTALL_DIR"

echo "Installing conda env and packages (this may take several minutes)..."
CONDA_BIN="$INSTALL_DIR/bin/conda"
if [ ! -x "$CONDA_BIN" ]; then
  echo "Conda binary not found at $CONDA_BIN" >&2
  exit 2
fi

echo "Creating conda env 'face_env' with Python 3.10"
"$CONDA_BIN" create -y -n face_env python=3.10

echo "Installing heavy packages from conda-forge into 'face_env'"
"$CONDA_BIN" install -y -n face_env -c conda-forge insightface onnxruntime onnx opencv numpy scipy pillow openpyxl flask python-docx

echo
echo "Miniforge installed to: $INSTALL_DIR"
echo "To use the environment run:" 
echo "  source $INSTALL_DIR/bin/activate" 
echo "  conda activate face_env" 
echo "Or open a new terminal and run: conda activate face_env"
echo "Then run: python src/bootstrap.py && python src/index.py"

exit 0
