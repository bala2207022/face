"""Bootstrap helper for the Face Attendance project.

When run, this script ensures necessary directories and minimal files exist:
- `data/students/`
- `models/` and files: `centroids.json`, `classes_meta.json`, `students_meta.json`
- `excel_reports/`

It also inspects current model artifacts and prints a recommendation:
- If `models/centroids.json` exists and has centroids -> recommend running `verify_realtime.py` (start attendance)
- Else if `models/embeddings.npz` exists -> recommend running `train_centroid.py` first
- Else recommend running `verify_realtime.py` to collect frames, then build embeddings and run `train_centroid.py`.

Run: python3 src/bootstrap.py
"""

import os
import json
from pathlib import Path
from datetime import datetime

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT, "data", "students")
MODELS_DIR = os.path.join(ROOT, "models")
REPORTS_DIR = os.path.join(ROOT, "excel_reports")
CENTROIDS = os.path.join(MODELS_DIR, "centroids.json")
EMB_FILE = os.path.join(MODELS_DIR, "embeddings.npz")
CLASSES_META = os.path.join(MODELS_DIR, "classes_meta.json")
STUDENTS_META = os.path.join(MODELS_DIR, "students_meta.json")

DEFAULT_CLASSES_META = {"next_id": 1, "classes": {}}
DEFAULT_STUDENTS_META = {"next_id": 1, "students": {}}


def ensure_dir(p: str):
    Path(p).mkdir(parents=True, exist_ok=True)


def write_json(path: str, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def ensure_file(path: str, default_data):
    if not os.path.exists(path):
        write_json(path, default_data)
        print(f"Created: {path}")
    else:
        print(f"OK: {path} (exists)")


def inspect_and_recommend():
    """Decide which script should be run next and explain steps."""
    centroids_ok = False
    if os.path.exists(CENTROIDS):
        try:
            with open(CENTROIDS, "r") as f:
                data = json.load(f)
            cents = data.get("centroids", {})
            if isinstance(cents, dict) and len(cents) > 0:
                centroids_ok = True
        except Exception:
            centroids_ok = False

    if centroids_ok:
        print("\nRecommendation: `models/centroids.json` contains centroids.")
        print("You can run: python3 src/verify_realtime.py  # start realtime verification / attendance")
        return

    # centroids missing or empty
    if os.path.exists(EMB_FILE):
        print("\nRecommendation: `models/embeddings.npz` exists but centroids are missing.")
        print("Run: python3 src/train_centroid.py  # to build centroids from embeddings")
        return

    # neither centroids nor embeddings exist
    print("\nRecommendation: No centroids or embeddings found.")
    print("First, run: python3 src/verify_realtime.py  # to capture frames and produce student/professor images")
    print("Then run any build_embeddings script (if present) to create `models/embeddings.npz`,")
    print("and finally: python3 src/train_centroid.py")


if __name__ == '__main__':
    print("Bootstrap started:")
    print(f"Root: {ROOT}")

    ensure_dir(DATA_DIR)
    ensure_dir(MODELS_DIR)
    ensure_dir(REPORTS_DIR)

    # ensure minimal model files
    ensure_file(CENTROIDS, {"centroids": {}})
    ensure_file(CLASSES_META, DEFAULT_CLASSES_META)
    ensure_file(STUDENTS_META, DEFAULT_STUDENTS_META)

    # touch embeddings.npz only if user wants; do not create binary placeholder
    print("\nDone creating minimal files/folders.")
    inspect_and_recommend()
