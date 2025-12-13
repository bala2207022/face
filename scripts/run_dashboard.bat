@echo off
REM Try to activate conda env 'face_env' if present, otherwise activate .venv
where conda >nul 2>&1
if %errorlevel%==0 (
  for /f "tokens=*" %%e in ('conda env list ^| find "face_env"') do (
    if NOT "%%e"=="" (
      echo Activating conda environment face_env
      call conda activate face_env
      python src\index.py
      goto :EOF
    )
  )
)

if exist .venv\Scripts\activate.bat (
  echo Activating .venv
  call .venv\Scripts\activate.bat
  python src\index.py
  goto :EOF
)

echo No conda env 'face_env' and no .venv found. Run scripts\setup.bat first.
exit /b 2
