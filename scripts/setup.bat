@echo off
REM Simple setup script for Windows (PowerShell recommended for activation)
SET ROOT_DIR=%~dp0\..
SET VENV_DIR=%ROOT_DIR%\.venv

echo Root: %ROOT_DIR%

where python >nul 2>&1 || (
  echo Python not found on PATH. Please install Python 3.8+ and try again.
  exit /b 2
)

python -m venv "%VENV_DIR%"
echo Created venv at %VENV_DIR%

echo Activate the venv manually with:
echo   %VENV_DIR%\Scripts\Activate.ps1   (PowerShell)
echo Then run:
echo   pip install --upgrade pip setuptools wheel
echo   pip install -r requirements.txt
echo   python src\bootstrap.py

exit /b 0
