# train_centroid.py — build class centroids from saved embeddings

import os
import json
import numpy as np

# project-relative paths
ROOT       = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(ROOT, "models")
EMB_FILE   = os.path.join(MODELS_DIR, "embeddings.npz")
OUT_FILE   = os.path.join(MODELS_DIR, "centroids.json")


def main():
    # check embeddings file is present
    if not os.path.exists(EMB_FILE):
        print(f"Embeddings file not found: {EMB_FILE}")
        print("Run build_embeddings.py first to generate embeddings.")
        return

    data = np.load(EMB_FILE, allow_pickle=True)

    # basic key checks
    if "X" not in data or "y" not in data:
        print("Embeddings file is missing 'X' or 'y' arrays.")
        return

    X = data["X"]
    y = data["y"]

    if X.size == 0 or y.size == 0:
        print("No embeddings or labels found in file.")
        return

    labels = np.unique(y)
    if labels.size == 0:
        print("No labels found to build centroids.")
        return

    # compute mean embedding per label
    centroids = {}
    for lab in labels:
        mask = (y == lab)
        class_vectors = X[mask]
        if class_vectors.size == 0:
            continue
        centroids[str(lab)] = class_vectors.mean(axis=0).tolist()

    if not centroids:
        print("No centroids were computed. Check your embeddings file.")
        return

    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(OUT_FILE, "w") as f:
        json.dump({"centroids": centroids}, f)

    print(f"Saved centroids for {len(centroids)} class(es) to {OUT_FILE}")


if __name__ == "__main__":
    main()