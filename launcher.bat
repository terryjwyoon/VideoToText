@echo off
REM Project Root Launcher - Redirects to main launcher
REM This maintains compatibility while using the new structure

echo.
echo ============================================================
echo     MP4/M4A to Text Converter - Redirecting to Launcher
echo ============================================================
echo.

REM Check if the scripts directory exists
if not exist "scripts\launcher.bat" (
    echo [ERROR] Launcher not found in scripts directory!
    echo Please ensure you're running from the project root.
    pause
    exit /b 1
)

echo Launching main control system...
echo.

REM Change to scripts directory and run launcher
cd scripts
call launcher.bat

REM Return to original directory  
cd ..