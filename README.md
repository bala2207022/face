**Project Overview**

- **Purpose**: Face recognition attendance system that stores attendance in Excel workbooks (no SQL). Each class has a workbook in `excel_reports/` with sheets: `meta`, `students`, `Attendance`, and `Summary`.
- **Key features**: Portable (no DB), formatted Excel `Summary` (columns: `name`, `id`, `date`, `no_of_present`, `no_of_absent`, `total_class`), duplicate same-day check-ins prevented.

**Prerequisites**

- macOS with `python3` (3.8+) installed.
- Recommended: use a virtual environment.
- Camera available for realtime checks (for `verify_realtime.py`).

**Install dependencies**

1. Create and activate a virtual environment (zsh):

```
python3 -m venv .venv
source .venv/bin/activate
```

2. Install packages:

```
pip install -r requirements.txt
```

**Execution Order (recommended)**

1. `bootstrap` — create required directories and placeholder meta files.
2. `train_centroid` — (if you have embeddings) generate centroids used by the recognizer.
3. `dashboard` — start the Flask web dashboard (optional, for professor UI).
4. `verify_realtime` — run headless/CLI camera mode for professor + students attendance.

**Step-by-step Quick Start**

1. Run bootstrap to create folders and JSON placeholders:

```
python3 src/bootstrap.py
```

This creates `models/classes_meta.json`, `models/students_meta.json`, `models/centroids.json` and the directory `excel_reports/` if they don't exist.

2. (Optional) If you already have face embeddings (`embeddings.npz`) and want to compute centroids:

```
python3 src/train_centroid.py
```

After running this, `models/centroids.json` will contain centroids used by the recognition scripts.

3. Start the web dashboard (professor web UI):

```
python3 src/dashboard.py
```

- By default the dashboard runs on `http://127.0.0.1:50135` (check console output for exact URL).
- Use the dashboard endpoints to create classes, register students, open sessions, and view/generate summary Excel sheets.

4. Or run the CLI realtime verifier (camera-based):

```
python3 src/verify_realtime.py
```

- First recognized face is treated as the professor (to start the class). Then students can check in.
- When the session ends (press `q`), a `Summary` sheet is written to the class workbook inside `excel_reports/`.

**Where output is saved**

- Per-class workbooks: `excel_reports/class_<id>_<label>.xlsx` (each file contains `meta`, `students`, `Attendance`, `Summary`).
- `Summary` sheet columns: `name`, `id`, `date`, `no_of_present`, `no_of_absent`, `total_class`.
- The `Summary` sheet is formatted (bold headers, blue header row, alternating row colors) and column widths auto-adjusted to fit names and data.

**Duplicate check-in handling**

- The system prevents marking the same student present more than once on the same date. If a duplicate check-in occurs, the scripts will not add a second attendance entry and will return an "Already marked present today" type message.

**Troubleshooting & Notes**

- If camera access fails in `verify_realtime.py`, try editing the `open_cam()` function to change the camera index or backend.
- If you don't have `embeddings.npz`, you can still create classes and manually register students via the dashboard; face recognition will only work once centroids/embeddings are available.
- If the web dashboard port conflicts, check the console output after running `dashboard.py` for the actual host and port.

**Optional: Smoke Test (manual)**

1. Run `bootstrap`.
2. Start `dashboard.py` or call the API endpoints to:
   - Create a class
   - Register two students for that class
   - Open the class session
3. Use `verify_realtime.py` to check in the two students (or simulate via API if you prefer).
4. Inspect the generated workbook at `excel_reports/` and open the `Summary` sheet to verify formatting and counts.

**Development & Contribution**

- Source files are under `src/`.
- Model/meta files are under `models/`.
- Generated Excel reports are under `excel_reports/`.

If you'd like, I can also:
- Add a one-shot smoke-test script `src/test_smoke.py` to create a class, register sample students, perform a simulated check-in flow, and verify that the `Summary` sheet exists.
- Add a short `README` section showing example API calls for the dashboard endpoints.

---

Last updated: 2025-12-04
