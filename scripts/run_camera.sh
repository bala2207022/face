#!/usr/bin/env bash
set -euo pipefail
# Run the realtime camera verify script using conda env or .venv if present
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT_DIR/.venv"

if command -v conda >/dev/null 2>&1; then
  if conda env list | grep -q "face_env"; then
    echo "Activating conda env: face_env"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate face_env
    python "$ROOT_DIR/src/verify_realtime.py"
    exit 0
  fi
fi

if [ -d "$VENV" ]; then
  echo "Activating virtualenv at $VENV"
  source "$VENV/bin/activate"
  python "$ROOT_DIR/src/verify_realtime.py"
  exit 0
fi

echo "No conda env 'face_env' and no .venv found. Run 'bash scripts/setup.sh' first." >&2
exit 2
