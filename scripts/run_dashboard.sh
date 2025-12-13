#!/usr/bin/env bash
set -euo pipefail
# Run the dashboard: prefer conda env 'face_env' if present, otherwise use .venv
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT_DIR/.venv"

if command -v conda >/dev/null 2>&1; then
  if conda env list | grep -q "face_env"; then
    echo "Activating conda env: face_env"
    # shellcheck source=/dev/null
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate face_env
    python "$ROOT_DIR/src/index.py"
    exit 0
  fi
fi

if [ -d "$VENV" ]; then
  echo "Activating virtualenv at $VENV"
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  python "$ROOT_DIR/src/index.py"
  exit 0
fi

echo "No conda env 'face_env' and no .venv found. Run 'bash scripts/setup.sh' first." >&2
exit 2
