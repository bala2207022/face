#!/usr/bin/env bash
set -euo pipefail

# Robust setup script for Linux / macOS to create a venv and install requirements.
# Usage: ./scripts/setup.sh [--detach]
#   --detach : run the long pip installs in background (nohup) so terminal can be closed

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
REQ_FILE="$ROOT_DIR/requirements.txt"
MODEL_REQ="$ROOT_DIR/models/requirements.txt"

DETACH=0
USE_CONDA=0
for arg in "$@"; do
  case "$arg" in
    --detach) DETACH=1 ;;
    --use-conda) USE_CONDA=1 ;;
    -h|--help)
      echo "Usage: $0 [--detach] [--use-conda]"; exit 0 ;;
  esac
done

echo "Project root: $ROOT_DIR"

find_python_cmd() {
  if command -v python3 >/dev/null 2>&1; then
    echo python3
  elif command -v python >/dev/null 2>&1; then
    echo python
  else
    echo ""
  fi
}

PYCMD=$(find_python_cmd)
if [ -z "$PYCMD" ]; then
  echo "ERROR: Could not find Python on PATH. Install Python 3.8+ and retry." >&2
  exit 2
fi

echo "Using Python command: $PYCMD"

if [ "$USE_CONDA" -eq 1 ]; then
  if command -v conda >/dev/null 2>&1 || command -v mamba >/dev/null 2>&1; then
    echo "Conda/mamba detected. Installing heavy packages via conda-forge..."
    CONDA_CMD=conda
    if command -v mamba >/dev/null 2>&1; then
      CONDA_CMD=mamba
    fi
    echo "Creating conda env 'face_env' with Python (if not exists) and installing packages..."
    $CONDA_CMD create -y -n face_env python
    echo "To activate the conda env: 'conda activate face_env'"
    echo "Installing packages via conda-forge (insightface, onnxruntime, onnx, opencv, numpy, scipy, pillow)..."
    $CONDA_CMD install -y -n face_env -c conda-forge insightface onnxruntime onnx opencv numpy scipy pillow openpyxl flask python-docx
    echo "Conda install complete. Activate env with: 'conda activate face_env' and then run 'python src/bootstrap.py'"
    exit 0
  else
    echo "--use-conda requested but conda/mamba not found on PATH. Install Miniconda/Miniforge and retry or run without --use-conda." >&2
    exit 3
  fi
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment in $VENV_DIR..."
  $PYCMD -m venv "$VENV_DIR"
else
  echo "Virtual environment already exists at $VENV_DIR"
fi

echo "Activating virtual environment..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Upgrading pip, setuptools and wheel..."
pip install --upgrade pip setuptools wheel || true

install_requirements() {
  local file="$1"
  if [ -f "$file" ]; then
    echo "Installing from $file"
    # Try up to 3 times to mitigate transient network failures
    local i
    for i in 1 2 3; do
      if pip install -r "$file" --no-input; then
        echo "Installed requirements from $file"
        return 0
      else
        echo "Attempt $i failed. Retrying in 5s..."
        sleep 5
      fi
    done
    echo "Failed to install from $file after multiple attempts." >&2
    echo "Trying one more time with --prefer-binary (may succeed on systems that can't build wheels)."
    if pip install --prefer-binary -r "$file" --no-input; then
      echo "Installed requirements (prefer-binary) from $file"
      return 0
    fi
    echo "Still failed. If 'insightface' fails, prefer using conda/mamba: 'bash scripts/setup.sh --use-conda' or install Miniconda/Miniforge and run 'conda install -c conda-forge insightface'" >&2
    return 1
  else
    echo "No requirements file at $file — skipping.";
    return 0
  fi
}

if [ "$DETACH" -eq 1 ]; then
  echo "Running installs in background. Output will be written to $ROOT_DIR/setup-install.log"
  # Create a small script to run inside the venv so background process picks up the right interpreter
  BG_SCRIPT="$ROOT_DIR/.setup_background.sh"
  cat > "$BG_SCRIPT" <<EOT
#!/usr/bin/env bash
set -e
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel
install_ok=0
if [ -f "$REQ_FILE" ]; then
  pip install -r "$REQ_FILE" --no-input || exit 20
fi
if [ -f "$MODEL_REQ" ]; then
  pip install -r "$MODEL_REQ" --no-input || exit 21
fi
python3 "$ROOT_DIR/src/bootstrap.py" || exit 22
echo "SETUP_COMPLETE"
EOT
  chmod +x "$BG_SCRIPT"
  # Run in background with nohup so closing terminal does not kill it
  nohup bash "$BG_SCRIPT" > "$ROOT_DIR/setup-install.log" 2>&1 &
  echo "Background install started (PID $!). Check $ROOT_DIR/setup-install.log for progress." 
  exit 0
fi

# Not detached — run interactively
echo "Installing main requirements..."
install_requirements "$REQ_FILE"

if [ -f "$MODEL_REQ" ]; then
  echo "Installing model requirements..."
  install_requirements "$MODEL_REQ"
fi

echo "Running bootstrap to create folders and metadata..."
python3 "$ROOT_DIR/src/bootstrap.py" || python "$ROOT_DIR/src/bootstrap.py"

echo "Setup finished successfully."
echo "Next steps: activate venv and run the dashboard or camera mode:" 
echo "  source $VENV_DIR/bin/activate"
echo "  python3 src/index.py    # or python src/index.py on Windows"

exit 0
