@echo off
setlocal
echo Starting ResumeIQ — AI-Powered ATS Analyzer...
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment (venv) not found.
    echo Please run "python -m venv venv" and "pip install -r requirements.txt" first.
    goto :EOF
)

echo Activating virtual environment...
call "venv\Scripts\activate"

echo.
echo Checking dependencies...
python -m pip install -r requirements.txt --quiet

echo.
echo Starting FastAPI server with Uvicorn...
echo Access the UI by opening frontend/index.html in your browser.
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

:EOF
endlocal
pause
