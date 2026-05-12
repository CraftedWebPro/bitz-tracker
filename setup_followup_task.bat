@echo off
echo Setting up Windows Task Scheduler for Biz Tracker follow-up reminders...
echo.

set SCRIPT_PATH=%~dp0utils\followup_checker.py
set PYTHON_EXE=python.exe

%PYTHON_EXE% -c "import plyer" 2>nul
if errorlevel 1 (
    echo ERROR: plyer not installed. Run: pip install plyer
    pause
    exit /b 1
)

schtasks /query /tn "BizTracker_FollowUp_Checker" >nul 2>&1
if not errorlevel 1 (
    echo Task already exists. Deleting old task...
    schtasks /delete /tn "BizTracker_FollowUp_Checker" /f
)

schtasks /create /tn "BizTracker_FollowUp_Checker" ^
    /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --notify" ^
    /sc daily ^
    /st 09:00 ^
    /ru "%USERNAME%" ^
    /f

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create scheduled task.
    echo Try running this batch file as Administrator.
) else (
    echo.
    echo SUCCESS! Follow-up reminders will pop up daily at 9:00 AM.
    echo.
    echo To test notifications now, run:
    echo   python "%SCRIPT_PATH%" --notify
)

pause
