# Face Recognition Attendance System

A **portable, beginner-friendly** face recognition attendance system that saves all data to Excel (no database needed). Works on **Windows, macOS, and Linux**.

---

## 📋 What This Project Does

- Recognizes students by their face using a camera.
- Records attendance in clean, formatted Excel spreadsheets.
- One Excel file per class with columns: `name`, `student_id`, `date`, `no_of_present`, `no_of_absent`, `total_class`.
- **No SQL database** — works anywhere (share with professor easily!).
- **Prevents duplicate check-ins** on the same day.

---

## ⚙️ What You Need Before Starting

1. **Python 3.8 or newer** installed on your computer.
   - Download from [python.org](https://www.python.org/downloads/)
   - Check if you have it: Open terminal/command prompt and type `python3 --version`

2. **A camera** (for face recognition mode).

3. **This project folder** downloaded/cloned to your computer.

---

## 🔁 Clone the project (one-time)

Open a terminal or PowerShell and run:

```bash
git clone https://github.com/bala2207022/face.git
cd face_attendance
```

If you already have the project folder, `cd` to it instead.

---

## ✅ Quick start (all platforms)

1. Clone the repo (see above) or open project folder.
2. Create & activate virtual environment.

macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Upgrade pip and install dependencies:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

4. Initialize project folders and meta files:
```bash
python3 src/bootstrap.py   # or `python` on Windows
```

5. (Optional) If you have face embeddings and want recognition:
```bash
python3 src/train_centroid.py
```

## 🟣 Streamlit Camera-Only UI (recommended)

This repository now includes a Streamlit UI (`streamlit_app.py`) which enforces camera-only image capture for both professor and student registration. Uploading images from files is intentionally disabled to improve data integrity and reduce spoofing risk.

Key points:
- Registration requires 15–17 camera captures per person (configurable in the app).
- The app performs basic embedding consistency checks and will reject duplicate/identical or highly inconsistent captures.
- Start the Streamlit UI (recommended for easy use):

```bash
# from project root
. .venv/bin/activate        # macOS / Linux

streamlit run streamlit_app.py
```

Open the Streamlit URL shown in the terminal (usually http://localhost:8501).

If you prefer the older Flask dashboard the repo still contains `src/index.py`, but the Streamlit UI is recommended.

6. Start the web dashboard (easy UI):
```bash
python3 src/index.py
# open http://127.0.0.1:50135 in your browser
```

7. Or run camera mode (realtime):
```bash
python3 src/verify_realtime.py
```


## 🎯 One-line commands (recommended)

These one-liners are the simplest way for a non-technical user to get started. Pick the line for your OS and whether you want pip or conda.

- macOS / Linux (pip-based, interactive):
```bash
bash scripts/setup.sh && bash scripts/run_dashboard.sh
```

- macOS / Linux (conda-based — recommended when pip fails for insightface):
```bash
bash scripts/install_miniforge.sh && conda activate face_env && python src/bootstrap.py && bash scripts/run_dashboard.sh
```

- Windows (PowerShell):
```powershell
.\scripts\setup.bat
.venv\Scripts\Activate.ps1
python src\bootstrap.py
.\scripts\run_dashboard.bat
```

If you prefer camera mode, replace `run_dashboard` with `run_camera` in the commands above.
## 🚀 STEP-BY-STEP SETUP (Choose Your Platform)

### **WINDOWS**

#### Step 1: Open Command Prompt (PowerShell)
Press `Win + R`, type `powershell`, press Enter.

#### Step 2: Navigate to Project Folder
```powershell
cd C:\Users\YourUsername\Documents\face_attendance
```
(Replace `YourUsername` with your actual Windows username, and adjust the path if your project is elsewhere.)

#### Step 3: Create Virtual Environment
```powershell
python -m venv .venv
```

#### Step 4: Activate Virtual Environment
```powershell
.venv\Scripts\Activate.ps1
```
After this, you should see `(.venv)` at the start of your command line.

#### Step 5: Install All Required Libraries
```powershell
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
This downloads and installs all necessary packages (takes 2-5 minutes).

#### Step 6: Create Project Structure
```powershell
python src/bootstrap.py
```
This creates required folders and starter files.

---

### **macOS**

#### Step 1: Open Terminal
Press `Cmd + Space`, type `terminal`, press Enter.

#### Step 2: Navigate to Project Folder
```bash
cd ~/Documents/face_attendance
```
(Adjust path if your project is elsewhere.)

#### Step 3: Create Virtual Environment
```bash
python3 -m venv .venv
```

#### Step 4: Activate Virtual Environment
```bash
source .venv/bin/activate
```
After this, you should see `(.venv)` at the start of your terminal.

#### Step 5: Install All Required Libraries
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
This downloads and installs all necessary packages (takes 2-5 minutes).

#### Step 6: Create Project Structure
```bash
python3 src/bootstrap.py
```
This creates required folders and starter files.

---

### **Linux (Ubuntu/Debian)**

#### Step 1: Open Terminal
Press `Ctrl + Alt + T` (or open from application menu).

#### Step 2: Navigate to Project Folder
```bash
cd ~/Documents/face_attendance
```
(Adjust path if your project is elsewhere.)

#### Step 3: Create Virtual Environment
```bash
python3 -m venv .venv
```

#### Step 4: Activate Virtual Environment
```bash
source .venv/bin/activate
```
After this, you should see `(.venv)` at the start of your terminal.

#### Step 5: Install All Required Libraries
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
This downloads and installs all necessary packages (takes 2-5 minutes).

#### Step 6: Create Project Structure
```bash
python3 src/bootstrap.py
```
This creates required folders and starter files.

---

## ▶️ HOW TO RUN THE PROJECT

Once setup is complete (Steps 1-6 above), **always do this before running**:

### Windows
```powershell
.venv\Scripts\Activate.ps1
```

### macOS / Linux
```bash
source .venv/bin/activate
```

After activating (you should see `(.venv)` in your terminal), choose one of these:

---

### **Option A: Web Dashboard (Easy UI)**

Run this command:
- **Windows**: `python src/index.py`
- **macOS/Linux**: `python3 src/index.py`

Open your browser and go to: `http://127.0.0.1:50135`

**What you can do:**
- Create a new class
- Register students
- Mark attendance
- Download Excel report

---

### **Option B: Camera Mode (Real-time)**

Run this command:
- **Windows**: `python src/verify_realtime.py`
- **macOS/Linux**: `python3 src/verify_realtime.py`

**What happens:**
1. Camera opens.
2. First person recognized = Professor (starts class).
3. Other people recognized = Students (marked present).
4. Press `q` to end class (saves Excel file).

---

### **Option C: Train Face Recognition (Advanced)**

If you have face embeddings file (`embeddings.npz`):

- **Windows**: `python src/train_centroid.py`
- **macOS/Linux**: `python3 src/train_centroid.py`

This processes face data for faster recognition.

---

## 🔧 One-click setup scripts

To make setup easier, there are helper scripts in the `scripts/` folder:

- `scripts/setup.sh` — for Linux and macOS. Usage:

```bash
bash scripts/setup.sh        # runs interactively (recommended)
bash scripts/setup.sh --detach   # runs installs in background (useful if you want to close terminal)
```

The `--detach` mode will run the heavy `pip install` steps via `nohup` and write logs to `./setup-install.log` so you can close your terminal and check progress later.

- `scripts/setup.bat` — for Windows. Run it from the project root in Command Prompt. It creates the venv and shows activation & next-step commands.

### Automatic Miniforge installer (macOS / Linux)

If you don't have `conda` or `mamba` installed and `insightface` fails with pip, this helper downloads and installs Miniforge and installs the required packages into a `face_env` environment:

```bash
bash scripts/install_miniforge.sh
```

This script will:
- Download the correct Miniforge installer for your OS/architecture
- Install Miniforge to `~/miniforge3`
- Create a `face_env` conda environment and install `insightface` and other heavy packages from `conda-forge`

After it finishes, run:

```bash
conda activate face_env
python src/bootstrap.py
python src/index.py
```

### Quick smoke-test (no insightface required)

To verify that the project can create Excel reports on your machine even before face models are installed, run the smoke test (requires only `openpyxl`):

```bash
source .venv/bin/activate   # or activate your environment
python src/test_smoke.py
```

This writes `excel_reports/smoke_test_class.xlsx` and demonstrates the duplicate-check prevention logic.

### If `insightface` fails with pip

Some systems (esp. macOS M1/ARM or minimal Linux) fail to build `insightface` from pip because it needs compiled binaries.

- Easiest fix: install `miniforge` or `miniconda` and use the conda-forge packages. Example using `conda`:

```bash
# create env (you can name it anything)
conda create -n face_env python=3.10 -y
conda activate face_env
conda install -c conda-forge insightface onnxruntime onnx opencv numpy scipy pillow openpyxl flask python-docx -y
```

- Or use the helper in this repo which wraps conda installs:

```bash
bash scripts/setup.sh --use-conda
```

This will create a `face_env` conda environment and install the heavy packages from `conda-forge`, avoiding compilation failures.


---

## 📁 Where Your Data is Saved

After running, you'll see:

- **`excel_reports/`** — Contains Excel files (one per class)
  - File name: `class_1_Math.xlsx` (example)
  - Open with Excel or Google Sheets
  - Sheets inside: `meta`, `students`, `Attendance`, `Summary`

- **`models/`** — Face recognition data (created automatically)

- **`data/`** — Student photos and info (created automatically)

---

## ❓ Troubleshooting

### "Python not found" error
- **Windows**: Use `python` instead of `python3` (or reinstall Python, making sure to check "Add Python to PATH")
- **macOS/Linux**: Use `python3` (not `python`)

### Virtual environment won't activate
- Make sure you're in the project folder
- Try deleting `.venv` folder and creating it again (Steps 3-4)

### Camera doesn't work
- Check if your camera is connected
- Try unplugging/replugging the camera
- Or try a different USB port

### "Module not found" error
- Make sure virtual environment is activated (you should see `(.venv)` in terminal)
- Run `pip install -r requirements.txt` again

### Port 50135 already in use (Web Dashboard)
- Another program is using that port
- Close the program or wait, then try again

---

## 🎯 Complete Example Workflow

1. **Setup** (do once):
   ```
   Create venv → Activate → pip install → python bootstrap.py
   ```

2. **Use Web Dashboard**:
   ```
   Activate venv → python src/index.py → Open browser http://127.0.0.1:50135
   ```

3. **Check Excel file**:
   ```
   Open folder → excel_reports/ → class_1_Math.xlsx (example)
   ```

---

## 📊 Excel File Format

Your attendance report looks like this:

| name | id | date | no_of_present | no_of_absent | total_class |
|------|-------|---------|---------|---------|---------|
| John Doe | 123 | 2025-12-07 | 5 | 2 | 7 |
| Jane Smith | 456 | 2025-12-07 | 6 | 1 | 7 |

- **Bold blue header row** (easy to read)
- **Auto-fitted columns** (names don't get cut off)
- **Alternating row colors** (professional look)

---

## 🔒 No Database = Easy Sharing

All your data is in **Excel files inside `excel_reports/`** — no database needed!

**Share with your professor**: Just send the `.xlsx` file. They can open it in Excel, Google Sheets, or any spreadsheet app.

---

## 📝 Tips for Success

- **First time?** Start with the **Web Dashboard** (Option A) — easier to understand.
- **Have a camera?** Try **Camera Mode** (Option B) for fully automatic attendance.
- **Stuck?** Check the error message carefully — it usually tells you what's wrong.
- **Take screenshots** of error messages — helps with troubleshooting.

---

**Last updated:** December 7, 2025  
**Works on:** Windows 10+, macOS 10.14+, Ubuntu 18.04+
